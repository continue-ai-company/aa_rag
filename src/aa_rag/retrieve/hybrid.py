from typing import List, Dict

from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import LanceDB
from langchain_core.documents import Document

from aa_rag import default as dfs
from aa_rag.gtypes.enums import RetrieveType, IndexType
from aa_rag.retrieve.base import BaseRetrieve


class HybridRetrieve(BaseRetrieve):
    _retrieve_type = RetrieveType.HYBRID

    def __init__(self, knowledge_name: str, index_type: IndexType, **kwargs):
        super().__init__(knowledge_name, index_type, **kwargs)

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        only_page_content: bool = False,
        dense_weight: float = dfs.RETRIEVE_HYBRID_DENSE_WEIGHT,
        sparse_weight: float = dfs.RETRIEVE_HYBRID_SPARSE_WEIGHT,
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
        dense_retriever = LanceDB(
            connection=self.db, table_name=self.table_name, embedding=self.embeddings
        ).as_retriever()

        # sparse retrieval
        all_docs = (
            self.db.open_table(self.table_name)
            .search()
            .to_pandas()[["text", "metadata"]]
            .apply(
                lambda x: Document(page_content=x["text"], metadata=x["metadata"]),
                axis=1,
            )
            .tolist()
        )
        sparse_retrieval = BM25Retriever.from_documents(all_docs)

        # combine the results
        ensemble_retriever = EnsembleRetriever(
            retrievers=[dense_retriever, sparse_retrieval],
            weights=[dense_weight, sparse_weight],
        )
        result: List[Document] = ensemble_retriever.invoke(query, id_key="id")[:top_k]

        if only_page_content:
            return [doc.page_content for doc in result]
        else:
            return [doc.model_dump(exclude={"id", "type"}) for doc in result]
