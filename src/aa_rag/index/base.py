from typing import List, Union, Any

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from aa_rag import setting
from aa_rag import utils
from aa_rag.gtypes import IndexType
from aa_rag.gtypes.enums import VectorDBType


class BaseIndex:
    _index_type: IndexType
    _indexed_data: Any

    def __init__(
        self,
        knowledge_name: str,
        vector_db: VectorDBType = VectorDBType.LANCE,
        embedding_model: str = setting.embedding.model,
        **kwargs,
    ):
        self._table_name = f"{knowledge_name}_{self.index_type}_{embedding_model}"

        self._vector_db = utils.get_vector_db(vector_db)
        self._embeddings, dimensions = utils.get_embedding_model(
            embedding_model, return_dim=True
        )

        if self.table_name not in self.vector_db.table_list():
            # create table if not exist
            if kwargs.get("schema"):
                self._vector_db.create_table(
                    self.table_name, schema=kwargs.get("schema")
                )
            else:
                import pyarrow as pa

                schema = pa.schema(
                    [
                        pa.field("id", pa.utf8(), False),
                        pa.field("vector", pa.list_(pa.float64(), dimensions), False),
                        pa.field("text", pa.utf8(), False),
                        pa.field(
                            "metadata",
                            pa.struct(
                                [
                                    pa.field("source", pa.utf8(), False),
                                ]
                            ),
                            False,
                        ),
                    ]
                )

                self._vector_db.create_table(self.table_name, schema=schema)
        else:
            pass

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
    def vector_db(self):
        return self._vector_db

    @property
    def embeddings(self) -> Embeddings:
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
