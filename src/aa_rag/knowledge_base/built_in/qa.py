from typing import List, Any

from langchain_core.documents import Document

from aa_rag.gtypes.enums import VectorDBType
from aa_rag.index.chunk import ChunkIndex
from aa_rag.knowledge_base.base import BaseKnowledge
from aa_rag.retrieve.hybrid import HybridRetrieve


class QAKnowledge(BaseKnowledge):
    _knowledge_name = "QA"

    def __init__(
        self,
        vector_db: VectorDBType = VectorDBType.LANCE,
        **kwargs,
    ):
        """
        QA Knowledge Base. Built-in Knowledge Base.
        """
        super().__init__(**kwargs)

        # define table schema
        import pyarrow as pa

        schema = pa.schema(
            [
                pa.field("id", pa.utf8(), False),
                pa.field("vector", pa.list_(pa.float64(), self.dimensions), False),
                pa.field("text", pa.utf8(), False),
                pa.field(
                    "metadata",
                    pa.struct(
                        [
                            pa.field("solution", pa.utf8(), False),
                            pa.field("tags", pa.list_(pa.utf8()), False),
                        ]
                    ),
                    False,
                ),
            ]
        )

        self._indexer = ChunkIndex(
            knowledge_name=self.knowledge_name.lower(),
            vector_db=vector_db,
            schema=schema,
        )
        self.db = vector_db

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
            vector_db=self.db,
        )
        return retriever.retrieve(query=error_desc, top_k=1, only_page_content=False)
