from typing import List, Union, Any

import lancedb
from langchain_core.documents import Document

from aa_rag import default as dfs
from aa_rag import utils
from aa_rag.gtypes import IndexType, EmbeddingModel


class BaseIndex:
    _index_type: IndexType
    _indexed_data: Any

    def __init__(
        self,
        knowledge_name: str,
        db_path: str = dfs.VECTOR_DB_PATH,
        embedding_model: EmbeddingModel = dfs.EMBEDDING_MODEL,
        **kwargs,
    ):
        self._table_name = f"{knowledge_name}_{self.index_type}_{embedding_model}"
        self._db = lancedb.connect(db_path)
        self._embeddings = utils.get_embedding_model(embedding_model)

    @property
    def indexed_data(self):
        return self._indexed_data

    @property
    def index_type(self):
        return self._index_type

    @property
    def table_name(self):
        return self._table_name

    @property
    def db(self):
        return self._db

    @property
    def embeddings(self):
        return self._embeddings

    def index(self, source_docs: Union[Document | List[Document]]):
        """
        Index documents. Assign the return value to self.indexed_data.

        Args:
            source_docs (Union[Document  |  List[Document]]): Document instance or more base on langchain.
        """
        return NotImplemented

    def store(self, **kwargs):
        """
        Write self.indexed_data to the database.

        Args:
            **kwargs:
        """
        return NotImplemented

    def __repr__(self):
        return f"{self.__class__.__name__}({self.table_name})"
