from typing import List, cast, Union, Tuple

import pandas as pd
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import LanceDB
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_milvus import Milvus
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from rank_bm25 import BM25Okapi

from aa_rag import setting, utils
from aa_rag.db.base import BaseDataBase, BaseVectorDataBase
from aa_rag.db.multimodal import StoreImageParams
from aa_rag.engine.base import BaseEngine, BaseIndexParams
from aa_rag.gtypes.enums import EngineType, VectorDBType, DBMode, RetrieveType
from aa_rag.oss import OSSStore, OSSStoreInitParams

dfs_setting = setting.engine.simple_chunk


# 公共字段
class SimpleChunkInitParams(BaseModel):
    knowledge_name: str = Field(..., description="The name of the knowledge base.")
    identifier: str = Field(
        default="common",
        description="An optional identifier for the engine instance.",
    )


# SimpleChunk 参数模型
class SimpleChunkIndexParams(BaseIndexParams, StoreImageParams):
    source_data: Union[Document, List[Document]] = Field(..., description="The source data to index.")

    retrieve_mode: DBMode = Field(
        default=setting.storage.mode,
        description="The mode of the index operation.",
    )


class SimpleChunkRetrieveParams(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(
        default=dfs_setting.retrieve.k,
        description="The number of top results to return.",
    )
    retrieve_mode: RetrieveType = Field(default=dfs_setting.retrieve.type, description="The retrieval method.")
    dense_weight: float = Field(
        default=dfs_setting.retrieve.weight.dense,
        description="The weight for dense retrieval.",
    )
    sparse_weight: float = Field(
        default=dfs_setting.retrieve.weight.sparse,
        description="The weight for sparse retrieval.",
    )


class SimpleChunkGenerateParams(BaseModel):
    pass


class SimpleChunk(
    BaseEngine[
        SimpleChunkIndexParams,
        SimpleChunkRetrieveParams,
        SimpleChunkGenerateParams,
    ]
):
    @property
    def type(self):
        return EngineType.SimpleChunk

    def __init__(
        self,
        params: SimpleChunkInitParams,
        embedding_model: str = setting.embedding.model,
        db_type: VectorDBType = setting.storage.vector,
        **kwargs,
    ):
        """
        Initialize the SimpleChunk engine.

        Args:
            params (SimpleChunkInitParams): The initialization parameters.
            embedding_model (str, optional): The name of the embedding model to use. Defaults to setting.embedding.model.
            db_type (VectorDBType, optional): The type of vector database to use. Defaults to setting.storage.vector.
            **kwargs: Additional keyword arguments for the engine initialization.
        """
        # kwargs
        self.kwargs = kwargs

        self.embeddings, self.dimension = utils.get_embedding_model(embedding_model, return_dim=True)

        # parameters that make up the table name
        self.knowledge_name = params.knowledge_name
        self.embedding_model = embedding_model
        self.identifier = params.identifier

        # db
        self.db = utils.get_db(db_type)
        self.table_name = self._get_table(self.db)

    def retrieve(
        self,
        params: SimpleChunkRetrieveParams,
    ):
        """
        Retrieve documents based on the provided query and retrieval method.

        Args:
            params (SimpleChunkRetrieveParams): The retrieval parameters.
        Returns:
            List[Document]: A list of retrieved documents.
        """
        assert self.table_exist, f"Table {self.table_name} does not exist."

        query, top_k, retrieve_type = (
            params.query,
            params.top_k,
            params.retrieve_mode,
        )

        result: BaseRetriever | List[Document] | None
        match retrieve_type:
            case RetrieveType.DENSE:
                result = self._dense_retrieve(query, top_k)
            case RetrieveType.BM25:
                result = self._bm25_retrieve(query, top_k)
            case RetrieveType.HYBRID:
                result = self._hybrid_retrieve(
                    query,
                    top_k,
                    dense_weight=params.dense_weight,
                    sparse_weight=params.sparse_weight,
                )
            case _:
                raise ValueError(f"Invalid retrieve method: {retrieve_type}")
        assert isinstance(result, List | None), f"Result must be a list, not {type(result)}"

        return [doc.model_dump(include={"metadata", "page_content"}) for doc in result] if result else []

    # def calculate_score(self, retrieve_type: RetrieveType, query: str, docs: List[Document]):
    #     match retrieve_type:
    #         case RetrieveType.DENSE:
    #
    #     sparse_retriever = BM25Retriever.from_documents(docs, preprocess_func=utils.split_multilingual)
    #     sparse_retriever.k = len(docs)
    #
    #     score_s: list = sparse_retriever.vectorizer.get_scores(sparse_retriever.preprocess_func(query))
    #
    #     for order, doc in enumerate(docs):
    #         doc.metadata.update({"score": score_s[order]})
    #
    #     return docs

    def _get_table(self, db_obj: BaseDataBase) -> str:
        """
        Get table name in the vector database.

        Args:
            db_obj (BaseDataBase): The database object.

        Returns:
            str: The name of the table.
        """
        assert isinstance(db_obj, BaseVectorDataBase), (
            f"db_obj must be an instance of BaseVectorDataBase, not {type(db_obj)}"
        )

        table_name = f"{self.knowledge_name}__{self.type}__{self.embedding_model}"

        table_name = table_name.replace("-", "_")

        if table_name not in db_obj.table_list():
            self.table_exist = False
        else:
            self.table_exist = True

        return table_name

    def _create_table(self):
        vector_db: BaseVectorDataBase = cast(BaseVectorDataBase, self.db)

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

                    identifier_field = FieldSchema(
                        name="identifier",
                        dtype=DataType.ARRAY,
                        element_type=DataType.VARCHAR,
                        max_length=65535,
                        max_capacity=4096,
                    )

                    schema = CollectionSchema(
                        fields=[
                            id_field,
                            vector_field,
                            text_field,
                            metadata_field,
                            identifier_field,
                        ],
                    )
                case _:
                    raise ValueError(f"Unsupported vector database type: {vector_db.db_type}")
        vector_db.create_table(self.table_name, schema=schema)

    def _dense_retrieve(
        self,
        query: str,
        top_k: int = dfs_setting.retrieve.k,
        only_return_retriever=False,
    ) -> VectorStoreRetriever | List[Document]:
        """
        Perform a dense retrieval of documents based on the query.

        Args:
            query (str): The query string to search for.
            top_k (int, optional): The number of top results to return. Defaults to setting.retrieve.k.
            only_return_retriever (bool, optional): If True, only return the retriever object. Defaults to False.

        Returns:
            VectorStoreRetriever | List[Document]: The retriever object if only_return_retriever is True, otherwise a list of retrieved documents.
        """
        vector_db, table_name = self.db, self.table_name
        assert isinstance(vector_db, BaseVectorDataBase), (
            f"db must be an instance of BaseVectorDataBase, not {type(vector_db)}"
        )

        # Get the appropriate retriever based on the vector database type
        dense_vectorstore: Milvus | LanceDB
        match self.db.db_type:
            case VectorDBType.LANCE:

                dense_vectorstore = LanceDB(
                    connection=vector_db.connection,
                    table_name=table_name,
                    embedding=self.embeddings,
                )
            case VectorDBType.MILVUS:
                dense_vectorstore = Milvus(
                    embedding_function=self.embeddings,
                    collection_name=table_name,
                    connection_args={
                        **setting.storage.milvus.model_dump(include={"uri", "user", "password"}),
                        "db_name": setting.storage.milvus.db_name,
                    },
                    primary_field="id",
                    metadata_field="metadata",
                )
            case _:
                raise ValueError(f"Unsupported vector database type: {self.db.db_type}")

        if only_return_retriever:
            dense_retriever = dense_vectorstore.as_retriever()
            dense_retriever.search_kwargs = {"expr": f'array_contains(identifier, "{self.identifier}")'}
            return dense_retriever

        # Perform the similarity search and return the results
        result: List[Tuple[Document, float]] = dense_vectorstore.similarity_search_with_relevance_scores(
            query,
            k=top_k,
            expr=f'array_contains(identifier, "{self.identifier}")',
        )

        for doc, score in result:
            doc.metadata["dense_score"] = score

        return [doc for doc, _ in result]

    def _bm25_retrieve(
        self,
        query: str,
        top_k: int = dfs_setting.retrieve.k,
        only_return_retriever=False,
    ) -> BM25Retriever | List[Document] | None:
        """
        Perform a BM25 retrieval of documents based on the query.

        Args:
            query (str): The query string to search for.
            top_k (int, optional): The number of top results to return. Defaults to setting.retrieve.k.
            only_return_retriever (bool, optional): If True, only return the retriever object. Defaults to False.

        Returns:
            BM25Retriever | List[Document|None: The retriever object if only_return_retriever is True, otherwise a list of retrieved documents. If build BM25 retriever failed, return None.
        """
        vector_db, table_name = self.db, self.table_name
        assert isinstance(vector_db, BaseVectorDataBase), (
            f"db must be an instance of BaseVectorDataBase, not {type(vector_db)}"
        )

        # get retriever
        with vector_db.using(table_name) as table:
            all_doc = table.query(
                f"array_contains(identifier,'{self.identifier}')",
                limit=-1,
                output_fields=["id", "text", "metadata"],
            )  # get all documents
            if not all_doc:
                return None

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

        sparse_retriever = BM25Retriever.from_documents(all_doc_s, preprocess_func=utils.split_multilingual)
        sparse_retriever.k = top_k

        if only_return_retriever:
            return sparse_retriever

        # retrieve
        result: List[Document] = sparse_retriever.invoke(query, expr=f'array_contains(identifier, "{self.identifier}")')

        # calculate sparse retrieval score
        corpus = list(map(lambda x: utils.split_multilingual(x.page_content), result))
        vectorizer = BM25Okapi(corpus)
        sparse_score_s = vectorizer.get_scores(utils.split_multilingual(query))
        for score, doc in zip(sparse_score_s, result):
            doc.metadata["sparse_score"] = score

        return result

    def _hybrid_retrieve(
        self,
        query: str,
        top_k: int = dfs_setting.retrieve.k,
        dense_weight=dfs_setting.retrieve.weight.dense,
        sparse_weight=dfs_setting.retrieve.weight.sparse,
    ) -> List[Document]:
        """
        Perform a hybrid retrieval of documents based on the query.

        Args:
            query (str): The query string to search for.
            top_k (int, optional): The number of top results to return. Defaults to setting.retrieve.k.
            dense_weight (float, optional): The weight for dense retrieval. Defaults to setting.retrieve.weight.dense.
            sparse_weight (float, optional): The weight for sparse retrieval. Defaults to setting.retrieve.weight.sparse.

        Returns:
            List[Document]: A list of retrieved documents.
        """
        dense_retriever = self._dense_retrieve(query, top_k, only_return_retriever=True)
        sparse_retriever = self._bm25_retrieve(query, top_k, only_return_retriever=True)

        dense_retriever = cast(VectorStoreRetriever, dense_retriever)


        if sparse_retriever is None:
            return []

        # combine the all retrievers
        ensemble_retriever = EnsembleRetriever(
            retrievers=[dense_retriever, sparse_retriever],  # type: ignore
            weights=[dense_weight, sparse_weight],
        )

        ensemble_result: List[Document] = ensemble_retriever.invoke(
            query, expr=f'array_contains(identifier, "{self.identifier}")'
        )[:top_k]

        # calculate dense retrieval score
        dense_score_result: List[Tuple[Document, float]] = (
            dense_retriever.vectorstore.similarity_search_with_relevance_scores(query)
        )
        dense_score_mapping = {}
        for doc, score in dense_score_result:
            dense_score_mapping[doc.page_content] = score
        for doc in ensemble_result:
            doc.metadata["dense_score"] = dense_score_mapping.get(doc.page_content, 0)

        # calculate sparse retrieval score
        corpus = list(map(lambda x: utils.split_multilingual(x.page_content), ensemble_result))
        vectorizer = BM25Okapi(corpus)
        sparse_score_s = vectorizer.get_scores(utils.split_multilingual(query))
        for score, doc in zip(sparse_score_s, ensemble_result):
            doc.metadata["sparse_score"] = score

        return ensemble_result

    def index(
        self,
        params: SimpleChunkIndexParams,
        chunk_size: int = dfs_setting.index.chunk_size,
        chunk_overlap: int = dfs_setting.index.overlap_size,
    ):
        """
        Build index from source data and store to database.

        Args:
            params (SimpleChunkIndexParams): The index parameters.
            chunk_size (int, optional): The size of each chunk. Defaults to setting.index.chunk_size.
            chunk_overlap (int, optional): The overlap size between chunks. Defaults to setting.index.overlap_size.
        """
        if not self.table_exist:
            self._create_table()

        source_data, mode = params.source_data, params.retrieve_mode

        if isinstance(source_data, Document):
            source_docs = [source_data]
        else:
            source_docs = source_data

        # split the document into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        indexed_data = splitter.split_documents(source_docs)

        # handle image
        img_params: StoreImageParams = StoreImageParams(**params.model_dump())
        if img_params.image and img_params.img_desc:
            oss_store_params = OSSStoreInitParams(**img_params.model_dump())
            img_doc: Document = OSSStore(params=oss_store_params).store_image(img_params)
            indexed_data.append(img_doc)  # add image description to indexed_data

        # store index

        # detects whether the metadata has an id field. If not, it will be generated id based on page_content via md5 algorithm.
        id_s = [doc.metadata.get("id", utils.calculate_md5(doc.page_content)) for doc in indexed_data]

        text_vector_s = self.embeddings.embed_documents([_.page_content for _ in indexed_data])

        data = []

        for id_, vector, doc in zip(id_s, text_vector_s, indexed_data):
            doc.metadata.update(params.metadata)  # update metadata with params.metadata
            data.append(
                {
                    "id": id_,
                    "vector": vector,
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "identifier": [self.identifier],
                }
            )

        vector_db, table_name = self.db, self.table_name
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

    def generate(self, params: SimpleChunkGenerateParams):
        return NotImplemented
