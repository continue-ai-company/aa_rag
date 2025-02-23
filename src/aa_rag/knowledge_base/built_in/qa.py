from typing import List, Any

from langchain_core.documents import Document

from aa_rag import setting
from aa_rag.engine.simple_chunk import SimpleChunk
from aa_rag.gtypes.enums import VectorDBType
from aa_rag.knowledge_base.base import BaseKnowledge


class QAKnowledge(BaseKnowledge):
    _knowledge_name = "QA"

    def __init__(
        self,
        vector_db: VectorDBType = setting.db.vector,
        **kwargs,
    ):
        """
        QA Knowledge Base. Built-in Knowledge Base.
        """
        super().__init__(**kwargs)

        # define table schema
        if vector_db == VectorDBType.LANCE:
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
        else:
            schema = None

        self.engine = SimpleChunk(
            knowledge_name=self.knowledge_name.lower(),
            vector_db=vector_db,
            schema=schema,
        )
        self.db = vector_db

    def index(self, error_desc: str, error_solution: str, tags: List[str], **kwargs):
        """
        Index the QA information.
        Args:
            error_desc: The error description.
            error_solution: The solution of the QA.
            tags: The tags of the QA.
            **kwargs:
        # check if the project is already indexed
        """

        chunk_size = (
            len(error_desc) * 2
            if kwargs.get("chunk_size") is None
            else kwargs.get("chunk_size")
        )  # ensure the chunk size is large enough to cover the whole text. do not split the text.
        chunk_overlap = (
            0 if kwargs.get("chunk_overlap") is None else kwargs.get("chunk_overlap")
        )

        self.engine.index(
            Document(
                page_content=error_desc,
                metadata={"solution": error_solution, "tags": tags},
            ),
            index_kwargs={
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
            },
        )

    def retrieve(self, error_desc: str, tags: List[str] = None) -> List[Any]:
        """
        Retrieve the QA information.
        Args:
            error_desc: The error description.
            tags: The tags of the QA.
        Returns:
            List[Any]: The QA information.
        """
        return self.engine.retrieve(query=error_desc, top_k=1)
