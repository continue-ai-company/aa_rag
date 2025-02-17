from typing import List, Dict

import pandas as pd
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import LanceDB
from langchain_core.documents import Document
from langchain_milvus import Milvus

from aa_rag import setting
from aa_rag.gtypes.enums import RetrieveType, IndexType, VectorDBType
from aa_rag.retrieve.base import BaseRetrieve


class HybridRetrieve(BaseRetrieve):
    _retrieve_type = RetrieveType.HYBRID

    def __init__(self, knowledge_name: str, index_type: IndexType, **kwargs):
        super().__init__(knowledge_name, index_type, **kwargs)

    def retrieve(
        self,
        query: str,
        top_k: int = setting.retrieve.k,
        only_page_content: bool = setting.retrieve.only_page_content,
        dense_weight: float = setting.retrieve.weight.dense,
        sparse_weight: float = setting.retrieve.weight.sparse,
        **kwargs,
    ) -> List[Dict | str]:
        """
        Retrieve documents using a hybrid approach.

        Args:
            query (str): Query string.
            top_k (int, optional): Number of documents to retrieve. Defaults to 3.
            only_page_content (bool, optional): Return only page content. Defaults to False.
            dense_weight (float, optional): Weight for dense retrieval. Defaults to 0.5.
            sparse_weight (float, optional): Weight for sparse retrieval. Defaults to 0.5.

        Returns:
            List[Dict|str]: List of retrieved documents.
        """

        # dense retrieval
        match self.vector_db.db_type:
            case VectorDBType.LANCE:
                dense_retriever = LanceDB(
                    connection=self.vector_db.connection,
                    table_name=self.table_name,
                    embedding=self.embeddings,
                ).as_retriever()
            case VectorDBType.MILVUS:
                dense_retriever = Milvus(
                    embedding_function=self.embeddings,
                    collection_name=self.table_name,
                    connection_args={
                        **setting.db.milvus.model_dump(
                            include={"uri", "user", "password"}
                        ),
                        "db_name": setting.db.milvus.database,
                    },
                    index_params={
                        "metric_type": "L2",
                        "index_type": "AUTOINDEX",
                        "params": {},
                    },
                ).as_retriever()
            case _:
                raise ValueError(
                    f"Unsupported vector database type: {self.vector_db.db_type}"
                )

        # sparse retrieval
        with self.vector_db.using(self.table_name) as table:
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
        sparse_retrieval = BM25Retriever.from_documents(all_doc_s)

        # combine the results
        ensemble_retriever = EnsembleRetriever(
            retrievers=[dense_retriever, sparse_retrieval],
            weights=[dense_weight, sparse_weight],
            id_key="id",
        )
        result: List[Document] = ensemble_retriever.invoke(query, id_key="id")[:top_k]

        if only_page_content:
            return [doc.page_content for doc in result]
        else:
            return [doc.model_dump(exclude={"id", "type"}) for doc in result]
