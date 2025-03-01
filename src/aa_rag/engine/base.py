from abc import abstractmethod
from typing import TypeVar, Generic

from pydantic import BaseModel

# 定义泛型参数
IndexT = TypeVar("IndexT", bound=BaseModel)
RetrieveT = TypeVar("RetrieveT", bound=BaseModel)
GenerateT = TypeVar("GenerateT", bound=BaseModel)


class BaseEngine(Generic[IndexT, RetrieveT, GenerateT]):
    @property
    @abstractmethod
    def type(self):
        """
        Return the type of the engine.
        """
        ...

    @abstractmethod
    def index(self, params: IndexT):
        """
        Build index from source data and store to database.
        """
        ...

    @abstractmethod
    def retrieve(self, params: RetrieveT):
        """
        Retrieve data.
        """
        ...

    @abstractmethod
    def generate(self, params: GenerateT):
        """
        Generate data.
        """
        ...
