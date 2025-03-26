import time
from abc import abstractmethod
from typing import TypeVar, Generic

from pydantic import BaseModel, Field, field_validator

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

    @field_validator("metadata", mode="after")
    def validate_metadata(cls, v):
        # add timestamp to metadata
        if "index_time" not in v:
            v["index_time"] = [str(int(time.time()))]
        else:
            if isinstance(v["index_time"], list):
                return v
            elif isinstance(v["index_time"], str):
                v["index_time"] = [v["index_time"]]
        return v


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
