import lancedb

from aa_rag import default as dfs
from aa_rag import utils
from aa_rag.gtypes import EmbeddingModel
from aa_rag.gtypes.enums import RetrieveType, IndexType


class BaseRetrieve:
    _retrieve_type: RetrieveType

    def __init__(
        self,
        knowledge_name: str,
        index_type: IndexType,
        db_path: str = dfs.VECTOR_DB_PATH,
        embedding_model: EmbeddingModel = dfs.EMBEDDING_MODEL,
        **kwargs,
    ):
        self._table_name = f"{knowledge_name}_{index_type}_{embedding_model}"
        self._db = lancedb.connect(db_path)

        assert self.table_name in self.db.table_names(), (
            f"Table not found: {self.table_name}"
        )

        self._embeddings = utils.get_embedding_model(embedding_model)

    @property
    def table_name(self):
        return self._table_name

    @property
    def db(self):
        return self._db

    @property
    def embeddings(self):
        return self._embeddings

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        only_page_content: bool = False,
        **kwargs,
    ):
        return NotImplementedError
