from typing import List, Dict

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

from aa_rag import setting
from aa_rag.gtypes.enums import RetrieveType, IndexType
from aa_rag.retrieve.base import BaseRetrieve


class BM25Retrieve(BaseRetrieve):
    _retrieve_type = RetrieveType.BM25

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
        Retrieve documents by BM25.

        Args:
            query (str): Query string.
            top_k (int, optional): Number of documents to retrieve. Defaults to 3.
            only_page_content (bool, optional): Return only page content. Defaults to False.

        Returns:
            List[Dict|str]: List of retrieved documents.
        """

        # sparse retriever
        all_docs = (
            self.vector_db.open_table(self.table_name)
            .search()
            .to_pandas()[["text", "metadata"]]
            .apply(
                lambda x: Document(page_content=x["text"], metadata=x["metadata"]),
                axis=1,
            )
            .tolist()
        )
        sparse_retriever = BM25Retriever.from_documents(all_docs)
        sparse_retriever.k = top_k

        result: List[Document] = sparse_retriever.invoke(query)

        if only_page_content:
            return [doc.page_content for doc in result]
        else:
            return [doc.model_dump(exclude={"id", "type"}) for doc in result]
