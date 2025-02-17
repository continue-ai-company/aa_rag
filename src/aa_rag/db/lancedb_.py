from typing import List

import lancedb
from lancedb import DBConnection
from lancedb.pydantic import LanceModel
from lancedb.table import Table
from pandas import DataFrame

from aa_rag import setting
from aa_rag.db.base import BaseVectorDataBase
from aa_rag.gtypes.enums import VectorDBType


class LanceDBDataBase(BaseVectorDataBase):
    _db_type = VectorDBType.LANCE

    def __init__(self, uri: str = setting.db.lancedb.uri, **kwargs):
        self.uri = uri
        self._conn_obj = self.connect()
        super().__init__(**kwargs)

    @property
    def connection(self) -> DBConnection:
        return self._conn_obj

    @property
    def table(self) -> Table:
        return self._table_obj

    def connect(self, **kwargs) -> DBConnection:
        return lancedb.connect(self.uri, **kwargs)

    def table_list(self, **kwargs) -> List[str]:
        table_name_s = self.connection.table_names(**kwargs)
        return list(table_name_s)

    def get_table(self, table_name, **kwargs):
        self._table_obj = self.connection.open_table(table_name, **kwargs)

        return self

    def create_table(self, table_name, schema: LanceModel, **kwargs):
        self.connection.create_table(name=table_name, schema=schema, **kwargs)

    def drop_table(self, table_name):
        return self.connection.drop_table(table_name)

    def select(self, where: str = None, **kwargs) -> DataFrame:
        assert self.table is not None, (
            "Table object is not defined, please use `with db.get_table()` to use select method"
        )

        return self.table.search().where(where).to_pandas()

    def insert(self, data: list[dict] | DataFrame, **kwargs):
        assert self.table is not None, (
            "Table object is not defined, please use `with db.get_table()` to use insert method"
        )

        self.table.add(data, **kwargs)

    def update(self, where: str, values: dict, **kwargs):
        assert self.table is not None, (
            "Table object is not defined, please use `with db.get_table()` to use update method"
        )

        self.table.update(where=where, values=values, **kwargs)

    def delete(self, where: str):
        assert self.table is not None, (
            "Table object is not defined, please use `with db.get_table()` to use delete method"
        )

        self.table.delete(where=where)

    def search(self, query_vector: List[float], top_k: int = 3, **kwargs):
        assert self.table is not None, (
            "Table object is not defined, please use `with db.get_table()` to use search method"
        )

        return self.table.search(query_vector).to_list()[:top_k]
