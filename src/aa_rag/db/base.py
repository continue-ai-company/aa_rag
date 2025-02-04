from typing import Any, List

from pandas import DataFrame


class BaseDataBase:
    _db_type: str
    _conn_obj: Any
    _table_obj: Any

    def __init__(self, **kwargs):
        pass

    @property
    def connection(self):
        return self._conn_obj

    @property
    def table(self):
        return self._table_obj

    def connect(self):
        return NotImplemented

    def get_table(self, table_name, **kwargs):
        return NotImplemented

    def table_list(self) -> List[str]:
        return NotImplemented

    def create_table(self, table_name, schema, **kwargs):
        return NotImplemented

    def drop_table(self, table_name):
        return NotImplemented

    def insert(self, **kwargs):
        return NotImplemented

    def select(self, **kwargs):
        return NotImplemented

    def update(self, **kwargs):
        return NotImplemented

    def delete(self, **kwargs):
        return NotImplemented

    def close(self):
        return NotImplemented

    def __enter__(self):
        assert self.table is not None, (
            "Table object is not defined, please use get_table() method to define it"
        )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._table_obj = None  # Reset the table object

        return False


class BaseVectorDataBase(BaseDataBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def insert(self, data: list[dict] | DataFrame, **kwargs):
        return NotImplemented

    def update(self, where: str, values: dict, **kwargs):
        return NotImplemented

    def delete(self, where: str):
        return NotImplemented

    def upsert(self, data: list[dict] | DataFrame, duplicate_where, **kwargs):
        assert self.table is not None, (
            "Table object is not defined, please use `with db.get_table()` to use insert method"
        )

        self.delete(duplicate_where)
        self.insert(data, **kwargs)

    def overwrite(self, data: list[dict] | DataFrame, **kwargs):
        assert self.table is not None, (
            "Table object is not defined, please use `with db.get_table()` to use overwrite method"
        )

        self.delete(where="1=1")
        self.insert(data, **kwargs)

    def search(self, query_vector: List[float], top_k: int = 3, **kwargs):
        return NotImplemented


class BaseNoSQLDataBase(BaseDataBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_table(self, table_name, **kwargs):
        return NotImplemented
