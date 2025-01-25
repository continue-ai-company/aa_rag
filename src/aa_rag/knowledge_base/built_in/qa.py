from typing import List, Any

from langchain_core.documents import Document

from aa_rag import setting
from aa_rag.index.chunk import ChunkIndex
from aa_rag.knowledge_base.base import BaseKnowledge
from aa_rag.retrieve.hybrid import HybridRetrieve


class QAKnowledge(BaseKnowledge):
    _knowledge_name = "QA"

    def __init__(
        self,
        relation_db_path: str = setting.db.relation.uri,
        vector_db_path: str = setting.db.vector.uri,
        **kwargs,
    ):
        """
        QA Knowledge Base. Built-in Knowledge Base.
        Args:
            relation_db_path: The path of the relation database.
            vector_db_path: The path of the vector database.
            **kwargs: The keyword arguments.
        """
        super().__init__(**kwargs)

        # # create the directory and file if not exist
        # relation_db_path_obj = Path(relation_db_path)
        # if not relation_db_path_obj.exists():
        #     relation_db_path_obj.parent.mkdir(parents=True, exist_ok=True)
        #     relation_db_path_obj.touch()
        # # create the connection and create the table if not exist
        # self.relation_db_conn = sqlite3.connect(relation_db_path)
        # self.relation_table_name = self.knowledge_name.lower()
        # self.relation_db_conn.execute(f"""
        #     CREATE TABLE IF NOT EXISTS {self.relation_table_name} (
        #         qa_id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         guides TEXT NOT NULL,
        #         project_meta TEXT NOT NULL)""")
        # self.relation_db_conn.commit()

        self._indexer = ChunkIndex(
            knowledge_name=self.knowledge_name.lower(), vector_db_path=vector_db_path
        )

        self.vector_db_path = vector_db_path

    def index(
        self, error_desc: str, error_solution: str, tags: List[str], **kwargs
    ) -> List[str]:
        """
        Index the QA information.
        Args:
            error_desc: The error description.
            error_solution: The solution of the QA.
            tags: The tags of the QA.
            **kwargs:
        Returns:
            List[str]: List of document id what be inserted.
        """
        # check if the project is already indexed

        self._indexer.chunk_size = (
            len(error_desc) * 2
            if kwargs.get("chunk_size") is None
            else kwargs.get("chunk_size")
        )
        self._indexer.chunk_overlap = (
            0 if kwargs.get("chunk_overlap") is None else kwargs.get("chunk_overlap")
        )

        self._indexer.index(
            Document(
                page_content=error_desc,
                metadata={"solution": error_solution, "tags": tags},
            )
        )

        return self._indexer.store()

    def retrieve(self, error_desc: str, tags: List[str] = None) -> List[Any]:
        """
        Retrieve the QA information.
        Args:
            error_desc: The error description.
            tags: The tags of the QA.
        Returns:
            List[Any]: The QA information.
        """
        retriever = HybridRetrieve(
            knowledge_name=self.knowledge_name.lower(),
            index_type=self._indexer.index_type,
            vector_db_path=self.vector_db_path,
        )
        return retriever.retrieve(query=error_desc, top_k=1, only_page_content=False)
