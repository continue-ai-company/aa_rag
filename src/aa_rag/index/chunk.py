from typing import List, Union

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from aa_rag import setting
from aa_rag import utils
from aa_rag.gtypes import IndexType
from aa_rag.gtypes.enums import DBMode
from aa_rag.index.base import BaseIndex


class ChunkIndex(BaseIndex):
    _index_type = IndexType.CHUNK

    def __init__(
        self,
        knowledge_name: str,
        chunk_size=setting.index.chunk_size,
        chunk_overlap=setting.index.overlap_size,
        **kwargs,
    ):
        super().__init__(knowledge_name, **kwargs)

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def index(
        self,
        source_docs: Union[Document | List[Document]],
    ):
        if isinstance(source_docs, Document):
            source_docs = [source_docs]

        # split the document into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )
        self._indexed_data = splitter.split_documents(source_docs)

    def store(self, mode: DBMode = setting.db.mode):
        """
        Insert documents to vector db.

        Args:
            mode: The mode to store the data.
        """
        assert self.indexed_data, "Can not store because indexed data is empty."
        # assert self.db, "Can not store because db is empty."

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

        match mode:
            case DBMode.INSERT:
                with self.vector_db.using(self.table_name) as table:
                    table.add(data)
                return id_s

            case DBMode.UPSERT:
                with self.vector_db.using(self.table_name) as table:
                    table.upsert(data)

            case DBMode.OVERWRITE:
                with self.vector_db.using(self.table_name) as table:
                    table.overwrite(data)

            case _:
                raise ValueError(f"Invalid mode: {mode}")
