from abc import abstractmethod
from typing import Any, List, Dict, Tuple

from langchain_core.documents import Document

from aa_rag import utils
from aa_rag.db.base import BaseDataBase
from aa_rag.gtypes.enums import VectorDBType, NoSQLDBType


class BaseEngine:
    _source_data: Any
    _indexed_data: Any

    _db: Dict[VectorDBType | NoSQLDBType, Tuple[BaseDataBase, str]] = {}

    def __init__(
        self,
        index_kwargs: dict = None,
        store_kwargs: dict = None,
    ):
        # check the db to ensure that target table exists
        if self.db_type:
            db_s = (
                [self.db_type] if not isinstance(self.db_type, list) else self.db_type
            )
            for db_type in db_s:
                db_obj = utils.get_db(db_type)
                table_name = self._get_table(db_obj)
                self._db[db_type] = (db_obj, table_name)
        else:
            self._db = {}

        self.index_kwargs = index_kwargs or {}
        self.store_kwargs = store_kwargs or {}

    @property
    def source_data(self):
        """
        To be handled data source
        """
        return self._source_data

    @property
    def indexed_data(self):
        """
        Handled data from source data
        """
        return self._indexed_data

    @property
    def db(self):
        """
        Database object
        """
        return self._db

    @property
    def db_type(self):
        return NotImplemented

    @property
    def type(self):
        """
        Return the type of the engine.
        """
        return NotImplemented

    @abstractmethod
    def _get_table(self, db_obj: BaseDataBase) -> str:
        """
        Return a table name after checking the existence of the table in the database. If the table does not exist, create it.
        """
        return NotImplemented

    @abstractmethod
    def _build_index(self, **kwargs) -> Any:
        """
        Build index from source data and assign to self._indexed_data.
        """
        return NotImplemented

    @abstractmethod
    def _build_store(self, **kwargs) -> Any:
        """
        Store indexed data to database.
        """
        return NotImplemented

    def index(self, source_data: Document | List[Document], **kwargs):
        """
        Build index from source data and store to database.
        """
        self._source_data = source_data

        # build index
        index_kwargs = kwargs.get("index_kwargs", self.index_kwargs)
        self._build_index(**index_kwargs)
        assert self.indexed_data, "Can not store because indexed data is empty."
        # store index
        store_kwargs = kwargs.get("store_kwargs", self.store_kwargs)
        self._build_store(**store_kwargs)

    @abstractmethod
    def retrieve(self, **kwargs):
        """
        Retrieve data.
        """
        return NotImplemented
