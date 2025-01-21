from typing import List, Union

from lancedb.table import Table
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import LanceDB
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

    def store(self, mode=setting.db.vector.mode) -> List[str]:
        """
        Insert documents to vector db.

        Args:
            mode (str, optional): Insert method. Defaults to 'deinsert'.

                - `insert`: Insert new documents to db directly without removing duplicate.
                - `deinsert`: Remove duplicate documents by id then insert new documents to db.
                - `overwrite`: Remove all documents in db then insert new documents to db.
                - `upsert`: Insert new documents to db, if document existed, update it.

        Returns:
            List[str]: List of document id what be inserted.
        """
        assert self.indexed_data, "Can not store because indexed data is empty."
        # assert self.db, "Can not store because db is empty."

        # detects whether the metadata has an id field. If not, it will be generated id based on page_content via md5 algorithm.
        id_s = [
            doc.metadata.get("id", utils.calculate_md5(doc.page_content))
            for doc in self.indexed_data
        ]
        # bind id to metadata.
        [doc.metadata.update({"id": id_}) for doc, id_ in zip(self.indexed_data, id_s)]
        # forced modify mode to `insert` if table not exist. insert data directly.
        if self.table_name not in self.vector_db.table_names():
            mode = DBMode.INSERT

        match mode:
            case DBMode.INSERT:
                vector_store = LanceDB(
                    connection=self.vector_db,
                    embedding=self.embeddings,
                    table_name=self.table_name,
                    mode="append",
                )
                return vector_store.add_documents(self.indexed_data, ids=id_s)
            case DBMode.DEINSERT:
                assert self.table_name in self.vector_db.table_names(), (
                    f"Table not found: {self.table_name}"
                )
                vector_store = LanceDB(
                    connection=self.vector_db,
                    embedding=self.embeddings,
                    table_name=self.table_name,
                    mode="append",
                )
                table: Table = vector_store.get_table()
                # find the old data by id field and de-weight it.
                ids_str = ", ".join(map(lambda x: f"'{x}'", id_s))
                query_str = f"id IN ({ids_str})"
                hit_id_s = table.search().where(query_str).to_pandas()["id"].to_list()
                remain_id_s = list(set(id_s) - set(hit_id_s))
                remain_docs = [
                    doc
                    for doc in self.indexed_data
                    if doc.metadata["id"] in remain_id_s
                ]
                if not remain_docs:
                    return []
                return vector_store.add_documents(
                    remain_docs, ids=[doc.metadata["id"] for doc in remain_docs]
                )
            case DBMode.OVERWRITE:
                vector_store = LanceDB(
                    connection=self.vector_db,
                    embedding=self.embeddings,
                    table_name=self.table_name,
                    mode="overwrite",
                )
                return vector_store.add_documents(self.indexed_data, ids=id_s)
            case DBMode.UPSERT:
                assert self.table_name in self.vector_db.table_names(), (
                    f"Table not found: {self.table_name}"
                )
                vector_store = LanceDB(
                    connection=self.vector_db,
                    embedding=self.embeddings,
                    table_name=self.table_name,
                    mode="append",
                )
                table = vector_store.get_table()

                ids_str = ", ".join(map(lambda x: f"'{x}'", id_s))
                query_str = f"id IN ({ids_str})"
                table.delete(where=query_str)
                return vector_store.add_documents(self.indexed_data, ids=id_s)
            case _:
                raise ValueError(f"Invalid mode: {mode}")
