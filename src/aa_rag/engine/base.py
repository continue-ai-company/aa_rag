from abc import abstractmethod
from typing import TypeVar, Generic

from pydantic import BaseModel, Field

from aa_rag.db.multimodal import StoreImageParams

# 定义泛型参数
IndexT = TypeVar("IndexT", bound=BaseModel)
RetrieveT = TypeVar("RetrieveT", bound=BaseModel)
GenerateT = TypeVar("GenerateT", bound=BaseModel)


class BaseIndexParams(BaseModel):
    metadata: dict = Field(
        default_factory=dict,
        examples=[{"url": "https://www.google.com"}],
        description="The metadata of the index item, the meatadata will be updated to the index item",
    )


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
