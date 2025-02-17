from aa_rag import utils, setting
from aa_rag.db.base import BaseVectorDataBase
from aa_rag.gtypes.enums import RetrieveType, IndexType, VectorDBType


class BaseRetrieve:
    _retrieve_type: RetrieveType

    def __init__(
        self,
        knowledge_name: str,
        index_type: IndexType,
        vector_db: VectorDBType = setting.db.vector,
        embedding_model: str = setting.embedding.model,
        **kwargs,
    ):
        self._table_name = f"{knowledge_name}_{index_type}_{embedding_model}".replace(
            "-", "_"
        )
        self._vector_db = utils.get_vector_db(vector_db)
        self._embeddings = utils.get_embedding_model(embedding_model, return_dim=False)

        assert self.table_name in self.vector_db.table_list(), (
            f"Table {self.table_name} not found in {self.vector_db}"
        )

    @property
    def table_name(self):
        return self._table_name

    @property
    def vector_db(self) -> BaseVectorDataBase:
        return self._vector_db

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
