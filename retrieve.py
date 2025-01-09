import lancedb
import utils
from langchain_core.documents import Document
from typing import List
from langchain_community.vectorstores import LanceDB
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
import os
os.chdir(os.path.dirname(__file__))


class RetrieveKnowledge:
    def __init__(
        self,
        knowledge_name: str,
        retrieve_type: str = "hybrid",
        index_type: str = "dpr",
        db_path: str = "./lancedb",
        embedding_model: str = "text-embedding-3-small",
    ):
        self.table_name = f"{knowledge_name}_{index_type}_{embedding_model}"
        self.db = lancedb.connect(db_path)

        assert self.table_name in self.db.table_names(), f"Table not found: {self.table_name}"

        self.embeddings = utils.get_embedding_model(embedding_model)
        self.retrieve_type = retrieve_type

    def retrieve(self, query: str, top_k: int = 3, to_json: bool = True,only_page_content:bool=True, **kwargs):
        if self.retrieve_type == "hybrid":
            result = self._retrieve_hybrid(query, top_k, **kwargs)
        elif self.retrieve_type == "dense":
            result = self._retrieve_dense(query, top_k)
        elif self.retrieve_type == "bm25":
            result = self._retrieve_bm25(query, top_k)
        else:
            raise ValueError(f"Invalid retrieve type: {self.retrieve_type}")

        if only_page_content:
            return [doc.page_content for doc in result]
        else:
            return [doc.to_json()['kwargs'] for doc in result]

    def _retrieve_dense(self, query: str, top_k: int = 3) -> List[Document]:
        """
        Retrieve documents using dense retrieval.

        Args:
            query (str): Query string.
            top_k (int, optional): Number of documents to retrieve. Defaults to 3.

        Returns:
            List[str]: List of document instance.
        """
        return self._retrieve_hybrid(query, top_k, dense_weight=1.0, sparse_weight=0.0)

    def _retrieve_bm25(self, query: str, top_k: int = 3) -> List[Document]:
        """
        Retrieve documents using BM25.

        Args:
            query (str): Query string.
            top_k (int, optional): Number of documents to retrieve. Defaults to 3.

        Returns:
            List[str]: List of document instance.
        """
        return self._retrieve_hybrid(query, top_k, dense_weight=0.0, sparse_weight=1.0)

    def _retrieve_hybrid(
        self, query: str, top_k: int = 3, dense_weight=0.5, sparse_weight=0.5
    ) -> List[Document]:
        """
        Retrieve documents using a hybrid approach.

        Args:
            query (str): Query string.
            top_k (int, optional): Number of documents to retrieve. Defaults to 3.
            dense_weight (float, optional): Weight of dense retrieval. Defaults to 0.5.
            sparse_weight (float, optional): Weight of sparse retrieval. Defaults to 0.5.

        Returns:
            List[str]: List of document instance.
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
            .apply(lambda x: Document(page_content=x["text"], metadata=x["metadata"]), axis=1)
            .tolist()
        )
        sparse_retrieval = BM25Retriever.from_documents(all_docs)

        # combine the results
        ensemble_retriever = EnsembleRetriever(
            retrievers=[dense_retriever, sparse_retrieval],
            weights=[dense_weight, sparse_weight],
            k=top_k,
        )
        return ensemble_retriever.invoke(query, id_key="id")[:top_k]


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv(dotenv.find_dotenv())
    rk = RetrieveKnowledge("fairy_tale")

    print(rk.retrieve("杨梅?", top_k=3))
