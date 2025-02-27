from typing import Any, List, cast

import pandas as pd
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_milvus import Milvus
from langchain_text_splitters import RecursiveCharacterTextSplitter

from aa_rag import setting, utils
from aa_rag.db.base import BaseDataBase, BaseVectorDataBase
from aa_rag.engine.base import BaseEngine
from aa_rag.gtypes.enums import EngineType, VectorDBType, DBMode, RetrieveType

cls_setting = setting.engine.simple_chunk


class SimpleChunk(BaseEngine):
    def __init__(
        self,
        knowledge_name: str,
        embedding_model: str = setting.embedding.model,
        identifier: str = None,
        index_kwargs: dict = None,
        store_kwargs: dict = None,
        **kwargs,
    ):
        """
        Initialize the SimpleChunk engine.

        Args:
            knowledge_name (str): The name of the knowledge base.
            embedding_model (str, optional): The embedding model to use. Defaults to setting.embedding.model.
            identifier (str, optional): An optional identifier for the engine instance.
            index_kwargs (dict, optional): Additional keyword arguments for indexing.
            store_kwargs (dict, optional): Additional keyword arguments for storing.
            **kwargs: Additional keyword arguments.
        """

        self.embeddings, self.dimension = utils.get_embedding_model(
            embedding_model, return_dim=True
        )

        # parameters that make up the table name
        self.knowledge_name = knowledge_name
        self.embedding_model = embedding_model
        self.identifier = identifier

        # additional keyword arguments
        self.kwargs = kwargs

        super().__init__(
            index_kwargs=index_kwargs,
            store_kwargs=store_kwargs,
        )

    @property
    def db_type(self) -> VectorDBType:
        return setting.db.vector

    @property
    def type(self):
        return EngineType.SIMPLE_CHUNK

    def _get_table(self, db_obj: BaseDataBase) -> str:
        """
        Get or create a table in the vector database.

        Args:
            db_obj (BaseDataBase): The database object.

        Returns:
            str: The name of the table.
        """
        assert isinstance(db_obj, BaseVectorDataBase), (
            f"db_obj must be an instance of BaseVectorDataBase, not {type(db_obj)}"
        )

        vector_db: BaseVectorDataBase = cast(BaseVectorDataBase, db_obj)

        # self.identifier can ensure that the table name is unique
        if self.identifier:
            table_name = f"{self.knowledge_name}_{self.type}_{self.embedding_model}_{self.identifier}"
        else:
            table_name = (
                f"{self.knowledge_name}_{self.type}_{self.embedding_model}_common"
            )

        table_name = table_name.replace("-", "_")

        if table_name not in db_obj.table_list():
            if self.kwargs.get("schema"):
                schema = self.kwargs["schema"]
            else:
                match vector_db.db_type:
                    case VectorDBType.LANCE:
                        import pyarrow as pa

                        schema = pa.schema(
                            [
                                pa.field("id", pa.utf8(), False),
                                pa.field(
                                    "vector",
                                    pa.list_(pa.float64(), self.dimension),
                                    False,
                                ),
                                pa.field("text", pa.utf8(), False),
                                pa.field(
                                    "metadata",
                                    pa.struct(
                                        [
                                            pa.field("source", pa.utf8(), False),
                                        ]
                                    ),
                                    False,
                                ),
                            ]
                        )
                    case VectorDBType.MILVUS:
                        from pymilvus import CollectionSchema, FieldSchema, DataType

                        id_field = FieldSchema(
                            name="id",
                            dtype=DataType.VARCHAR,
                            max_length=256,
                            is_primary=True,
                        )

                        vector_field = FieldSchema(
                            name="vector",
                            dtype=DataType.FLOAT_VECTOR,
                            dim=self.dimension,
                        )

                        text_field = FieldSchema(
                            name="text",
                            dtype=DataType.VARCHAR,
                            max_length=65535,
                        )

                        metadata_field = FieldSchema(
                            name="metadata",
                            dtype=DataType.JSON,
                        )

                        schema = CollectionSchema(
                            fields=[id_field, vector_field, text_field, metadata_field],
                        )
                    case _:
                        raise ValueError(
                            f"Unsupported vector database type: {vector_db.db_type}"
                        )
            vector_db.create_table(table_name, schema=schema)
        else:
            pass

        return table_name

    def _build_index(
        self,
        chunk_size: int = cls_setting.index.chunk_size,
        chunk_overlap: int = cls_setting.index.chunk_size,
    ) -> Any:
        """
        Build the index by splitting the source data into chunks.

        Args:
            chunk_size (int, optional): The size of each chunk. Defaults to 512.
            chunk_overlap (int, optional): The overlap between chunks. Defaults to 100.
        """
        if isinstance(self.source_data, Document):
            source_docs = [self.source_data]
        else:
            source_docs = self.source_data

        # split the document into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        self._indexed_data = splitter.split_documents(source_docs)

    def _build_store(self, mode: DBMode | str = setting.db.mode) -> Any:
        """
        Build the store by inserting or updating the indexed data in the vector database.

        Args:
            mode (DBMode): The mode of operation (INSERT, UPSERT, OVERWRITE).
        """
        if isinstance(mode, str):
            mode: DBMode = DBMode(mode)

        # detects whether the metadata has an id field. If not, it will be generated id based on page_content via md5 algorithm.
        id_s = [
            doc.metadata.get("id", utils.calculate_md5(doc.page_content))
            for doc in self.indexed_data
        ]

        text_vector_s = self.embeddings.embed_documents(
            [_.page_content for _ in self.indexed_data]
        )

        data = []

        for id_, vector, doc in zip(id_s, text_vector_s, self.indexed_data):
            data.append(
                {
                    "id": id_,
                    "vector": vector,
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                }
            )

        vector_db, table_name = self.db[self.db_type]
        assert isinstance(vector_db, BaseVectorDataBase), (
            f"db must be an instance of BaseVectorDataBase, not {type(vector_db)}"
        )

        with vector_db.using(table_name) as table:
            match mode:
                case DBMode.INSERT:
                    table.add(data)

                case DBMode.UPSERT:
                    table.upsert(data)

                case DBMode.OVERWRITE:
                    table.overwrite(data)
                case _:
                    raise ValueError(f"Invalid mode: {mode}")

    def retrieve(
        self,
        query: str,
        top_k: int = cls_setting.retrieve.k,
        retrieve_type: RetrieveType = RetrieveType.HYBRID,
        **kwargs,
    ):
        """
        Retrieve documents based on the provided query and retrieval method.

        Args:
            query (str): The query string to search for.
            top_k (int, optional): The number of top results to return. Defaults to setting.retrieve.k.
            retrieve_type (RetrieveType, optional): The retrieval method to use. Defaults to RetrieveType.HYBRID.
            **kwargs: Additional keyword arguments for the retrieval process.

        Returns:
            List[Document]: A list of retrieved documents.
        """
        match retrieve_type:
            case RetrieveType.DENSE:
                result = self._dense_retrieve(query, top_k, **kwargs)
            case RetrieveType.BM25:
                result = self._bm25_retrieve(query, top_k, **kwargs)
            case RetrieveType.HYBRID:
                result = self._hybrid_retrieve(query, top_k, **kwargs)
            case _:
                raise ValueError(f"Invalid retrieve method: {retrieve_type}")

        return [doc.model_dump(include={"metadata", "page_content"}) for doc in result]

    def _dense_retrieve(
        self,
        query: str,
        top_k: int = cls_setting.retrieve.k,
        only_return_retriever=False,
        **kwargs,
    ) -> BaseRetriever | List[Document]:
        """
        Perform a dense retrieval of documents based on the query.

        Args:
            query (str): The query string to search for.
            top_k (int, optional): The number of top results to return. Defaults to setting.retrieve.k.
            only_return_retriever (bool, optional): If True, only return the retriever object. Defaults to False.
            **kwargs: Additional keyword arguments for the similarity search.

        Returns:
            BaseRetriever | List[Document]: The retriever object if only_return_retriever is True, otherwise a list of retrieved documents.
        """
        vector_db, table_name = self.db[self.db_type]
        assert isinstance(vector_db, BaseVectorDataBase), (
            f"db must be an instance of BaseVectorDataBase, not {type(vector_db)}"
        )

        # Get the appropriate retriever based on the vector database type
        match self.db_type:
            case VectorDBType.LANCE:
                from langchain_community.vectorstores import LanceDB

                dense_retriever = LanceDB(
                    connection=vector_db.connection,
                    table_name=table_name,
                    embedding=self.embeddings,
                )
            case VectorDBType.MILVUS:
                dense_retriever = Milvus(
                    embedding_function=self.embeddings,
                    collection_name=table_name,
                    connection_args={
                        **setting.db.milvus.model_dump(
                            include={"uri", "user", "password"}
                        ),
                        "db_name": setting.db.milvus.database,
                    },
                    primary_field="id",
                    metadata_field="metadata",
                )
            case _:
                raise ValueError(f"Unsupported vector database type: {self.db_type}")

        if only_return_retriever:
            return dense_retriever.as_retriever()

        # Perform the similarity search and return the results
        result: List[Document] = dense_retriever.similarity_search(
            query, k=top_k, **kwargs
        )

        return result

    def _bm25_retrieve(
        self,
        query: str,
        top_k: int = cls_setting.retrieve.k,
        only_return_retriever=False,
        **kwargs,
    ) -> BaseRetriever | List[Document]:
        """
        Perform a BM25 retrieval of documents based on the query.

        Args:
            query (str): The query string to search for.
            top_k (int, optional): The number of top results to return. Defaults to setting.retrieve.k.
            only_return_retriever (bool, optional): If True, only return the retriever object. Defaults to False.
            **kwargs: Additional keyword arguments for the retrieval process.

        Returns:
            BaseRetriever | List[Document]: The retriever object if only_return_retriever is True, otherwise a list of retrieved documents.
        """
        vector_db, table_name = self.db[self.db_type]
        assert isinstance(vector_db, BaseVectorDataBase), (
            f"db must be an instance of BaseVectorDataBase, not {type(vector_db)}"
        )

        # get retriever
        with vector_db.using(table_name) as table:
            all_doc = table.query(
                "", limit=-1, output_fields=["id", "text", "metadata"]
            )  # get all documents
            all_doc_df = pd.DataFrame(all_doc)
            all_doc_s = (
                all_doc_df[["id", "text", "metadata"]]
                .apply(
                    lambda x: Document(
                        page_content=x["text"],
                        metadata={**x["metadata"], "id": x["id"]},
                    ),
                    axis=1,
                )
                .tolist()
            )
        sparse_retriever = BM25Retriever.from_documents(all_doc_s)
        sparse_retriever.k = top_k

        if only_return_retriever:
            return sparse_retriever

        # retrieve
        result: List[Document] = sparse_retriever.invoke(query, **kwargs)

        return result

    def _hybrid_retrieve(
        self,
        query: str,
        top_k: int = cls_setting.retrieve.k,
        dense_weight=cls_setting.retrieve.weight.dense,
        sparse_weight=cls_setting.retrieve.weight.sparse,
        **kwargs,
    ) -> List[Document]:
        """
        Perform a hybrid retrieval of documents based on the query.

        Args:
            query (str): The query string to search for.
            top_k (int, optional): The number of top results to return. Defaults to setting.retrieve.k.
            dense_weight (float, optional): The weight for dense retrieval. Defaults to setting.retrieve.weight.dense.
            sparse_weight (float, optional): The weight for sparse retrieval. Defaults to setting.retrieve.weight.sparse.
            **kwargs: Additional keyword arguments for the retrieval process.

        Returns:
            List[Document]: A list of retrieved documents.
        """
        dense_retriever = self._dense_retrieve(query, top_k, only_return_retriever=True)
        sparse_retriever = self._bm25_retrieve(query, top_k, only_return_retriever=True)

        # combine the all retrievers
        ensemble_retriever = EnsembleRetriever(
            retrievers=[dense_retriever, sparse_retriever],
            weights=[dense_weight, sparse_weight],
        )
        return ensemble_retriever.invoke(query, **kwargs)[:top_k]
