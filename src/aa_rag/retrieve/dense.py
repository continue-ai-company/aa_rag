from typing import List, Dict

from langchain_community.vectorstores import LanceDB
from langchain_core.documents import Document

from aa_rag import setting
from aa_rag.gtypes.enums import RetrieveType, IndexType
from aa_rag.retrieve.base import BaseRetrieve


class DenseRetrieve(BaseRetrieve):
    _retrieve_type = RetrieveType.DENSE

    def __init__(self, knowledge_name: str, index_type: IndexType, **kwargs):
        super().__init__(knowledge_name, index_type, **kwargs)

    def retrieve(
        self,
        query: str,
        top_k: int = setting.retrieve.k,
        only_page_content: bool = setting.retrieve.only_page_content,
        **kwargs,
    ) -> List[Dict | str]:
        """
        Retrieve documents by dense.

        Args:
            query (str): Query string.
            top_k (int, optional): Number of documents to retrieve. Defaults to 3.
            only_page_content (bool, optional): Return only page content. Defaults to False.

        Returns:
            List[Dict|str]: List of retrieved documents.
        """

        # dense retrieval
        dense_retriever = LanceDB(
            connection=self.vector_db,
            table_name=self.table_name,
            embedding=self.embeddings,
        )

        result: List[Document] = dense_retriever.similarity_search(query, k=top_k)

        if only_page_content:
            return [doc.page_content for doc in result]
        else:
            return [doc.model_dump(exclude={"id", "type"}) for doc in result]
