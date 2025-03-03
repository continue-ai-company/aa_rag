from abc import abstractmethod, ABC
from typing import Any, List

from pandas import DataFrame

from aa_rag.gtypes.enums import VectorDBType, NoSQLDBType


def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


class BaseDataBase:
    _db_type: Any
    _conn_obj: Any

    def __init__(self, **kwargs):
        self._conn_obj = self.connect(**kwargs)

    @property
    def connection(self):
        return self._conn_obj

    @property
    def db_type(self):
        return self._db_type

    @abstractmethod
    def connect(self, **kwargs):
        return NotImplemented

    @abstractmethod
    def table_list(self) -> List[str]:
        return NotImplemented

    @abstractmethod
    def create_table(self, table_name, schema, **kwargs):
        return NotImplemented

    @abstractmethod
    def drop_table(self, table_name):
        return NotImplemented

    @abstractmethod
    def close(self):
        return NotImplemented

    @abstractmethod
    def using(self, *args, **kwargs):
        """
        Set the table or collection to use. This is useful for chaining methods.

        Returns:
            self

        """
        return self

    def __enter__(self):
        return self

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        return NotImplemented

    def __call__(self, *args, **kwargs):
        return self.using(*args, **kwargs)


class BaseVectorDataBase(BaseDataBase, ABC):
    _db_type: VectorDBType

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def insert(self, data: list[dict] | DataFrame, **kwargs):
        return NotImplemented

    @abstractmethod
    def delete(self, where: str):
        return NotImplemented

    @abstractmethod
    def upsert(self, data: list[dict], **kwargs):
        return NotImplemented

    @abstractmethod
    def overwrite(self, data: list[dict] | DataFrame, **kwargs):
        return NotImplemented

    @abstractmethod
    def query(self, expr: str, **kwargs):
        return NotImplemented


class BaseNoSQLDataBase(BaseDataBase, ABC):
    _db_type: NoSQLDBType

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def create_table(self, table_name, **kwargs):
        return NotImplemented

    @abstractmethod
    def select(self, query: dict = None):
        return NotImplemented
