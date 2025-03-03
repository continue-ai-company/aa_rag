from typing import List
from pandas import DataFrame
from aa_rag import setting
from aa_rag.db.base import BaseVectorDataBase


class LanceDBDataBase(BaseVectorDataBase):
    def __init__(self, uri: str = setting.storage.lancedb.uri, **kwargs):
        self.uri = uri
        self._conn_obj = self.connect()
        super().__init__(**kwargs)

    @property
    def connection(self):
        if not hasattr(self, "_conn_obj"):
            self._conn_obj = self.connect()
        return self._conn_obj

    @property
    def table(self):
        if not hasattr(self, "_table_obj"):
            raise AttributeError(
                "Table object is not defined, please use `get_table()` method."
            )
        return self._table_obj

    def connect(self, **kwargs):
        try:
            import lancedb
        except ImportError:
            raise ImportError(
                "LanceDB can only be enabled on the online service, please execute `pip install aa-rag[online]`."
            )
        return lancedb.connect(self.uri, **kwargs)

    def table_list(self, **kwargs) -> List[str]:
        return list(self.connection.table_names(**kwargs))

    def get_table(self, table_name, **kwargs):
        self._table_obj = self.connection.open_table(table_name, **kwargs)
        return self

    def create_table(self, table_name, schema, **kwargs):
        from lancedb.pydantic import LanceModel

        if not isinstance(schema, LanceModel):
            raise ValueError("Schema must be an instance of LanceModel.")

        self.connection.create_table(name=table_name, schema=schema, **kwargs)

    def drop_table(self, table_name):
        return self.connection.drop_table(table_name)

    def select(self, where: str = None, **kwargs) -> DataFrame:
        return self.table.search().where(where).to_pandas()

    def insert(self, data: list[dict] | DataFrame, **kwargs):
        self.table.add(data, **kwargs)

    def update(self, where: str, values: dict, **kwargs):
        self.table.update(where=where, values=values, **kwargs)

    def delete(self, where: str):
        self.table.delete(where=where)

    def search(self, query_vector: List[float], top_k: int = 3, **kwargs):
        return self.table.search(query_vector).to_list()[:top_k]
