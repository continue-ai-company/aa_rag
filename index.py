from typing import List, Union
import lancedb
from langchain_core.documents import Document
from langchain_community.vectorstores import LanceDB
import utils
from lancedb.table import Table
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
os.chdir(os.path.dirname(__file__))

class IndexKnowledge:
    def __init__(
        self,
        knowledge_name: str,
        index_type: str = "dpr",
        db_path: str = "./lancedb",
        embedding_model: str = "text-embedding-3-small",
    ):
        self.table_name = f"{knowledge_name}_{index_type}_{embedding_model}"
        self.db = lancedb.connect(db_path)
        self.embeddings = utils.get_embedding_model(embedding_model)
        self.index_type = index_type

    def index(self, source_docs: Union[Document | List[Document]], **kwargs) -> List[str]:
        if self.index_type == "dpr":
            return self._index_dpr(source_docs, **kwargs)
        else:
            raise ValueError(f"Invalid index type: {self.index_type}")

    def _index_dpr(
        self, source_docs: Union[Document | List[Document]], chunk_size=256, chunk_overlap=100
    ) -> List[str]:
        """
        Index documents using DPR.

        Args:
            source_docs (Union[Document  |  List[Document]]): Document instance or more base on langchain core.
            chunk_size (int, optional): each text chunk max length. Defaults to 256.
            chunk_overlap (int, optional): the length of the overlap between two chunks. Defaults to 100.

        Returns:
            List[str]: List of document id what be inserted.
        """
        if isinstance(source_docs, Document):
            source_docs = [source_docs]

        # split the document into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        docs = splitter.split_documents(source_docs)

        # insert the chunks into the db
        return self._doc2db(docs, mode="deinsert")

    def _doc2db(self, docs: Union[Document | List[Document]], mode="deinsert") -> List[str]:
        """
        Insert documents to vector db.

        Args:
            docs (Union[Document | List[Document]]):  Document instance or more base on langchain core.
            mode (str, optional): : `insert`, `deinsert`,`overwrite` or `upsert`. Defaults to `deinsert`.
            - `insert`: Insert new documents to db directly without removing duplicate.
            - `deinsert`: Remove duplicate documents by id then insert new documents to db.
            - `overwrite`: Remove all documents in db then insert new documents to db.
            - `upsert`: Insert new documents to db, if document existed, update it.

        Returns:
            List[str]: List of document id what be inserted.
        """

        if isinstance(docs, Document):
            docs = [docs]

        # detects whether the metadata has an id field. If not, it will be generate id based on page_content via md5 algorithm.
        id_s = [doc.metadata.get("id", utils.calculate_md5(doc.page_content)) for doc in docs]
        # bind id to metadata.
        [doc.metadata.update({"id": id_}) for doc, id_ in zip(docs, id_s)]
        # forced modify mode to `insert` if table not exist. insert data directly.
        if self.table_name not in self.db.table_names():
            mode = "insert"

        if mode == "insert":
            vector_store = LanceDB(
                connection=self.db,
                embedding=self.embeddings,
                table_name=self.table_name,
                mode="append",
            )
            return vector_store.add_documents(docs, ids=id_s)
        elif mode == "deinsert":
            assert self.table_name in self.db.table_names(), f"Table not found: {self.table_name}"
            vector_store = LanceDB(
                connection=self.db,
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
            remain_docs = [doc for doc in docs if doc.metadata["id"] in remain_id_s]
            return vector_store.add_documents(
                remain_docs, ids=[doc.metadata["id"] for doc in remain_docs]
            )
        elif mode == "overwrite":
            vector_store = LanceDB(
                connection=self.db,
                embedding=self.embeddings,
                table_name=self.table_name,
                mode="overwrite",
            )
            return vector_store.add_documents(docs, ids=id_s)
        elif mode == "upsert":
            assert self.table_name in self.db.table_names(), f"Table not found: {self.table_name}"
            vector_store = LanceDB(
                connection=self.db,
                embedding=self.embeddings,
                table_name=self.table_name,
                mode="append",
            )
            ids_str = ", ".join(map(lambda x: f"'{x}'", id_s))
            query_str = f"id IN ({ids_str})"
            hit_id_s = table.search().where(query_str).delete()
            return vector_store.add_documents(remain_docs, ids=id_s)
        else:
            raise ValueError(f"Invalid mode: {mode}")


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv(dotenv.find_dotenv())

    IndexKnowledge("fairy_tale").index(utils.parse_file("resources/小红帽与大灰狼.txt"))
