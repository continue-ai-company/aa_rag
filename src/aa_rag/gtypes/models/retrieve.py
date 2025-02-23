from pydantic import BaseModel, Field, ConfigDict

from aa_rag import setting
from aa_rag.gtypes.enums import RetrieveType, EngineType
from aa_rag.gtypes.models.base import BaseResponse
from aa_rag.gtypes.models.engine import SimpleChunkEngineItem


class BaseRetrieveItem(BaseModel):
    query: str = Field(default=..., examples=["What is the story of Cinderella?"])


class RetrieveItem(BaseModel):
    engine_type: EngineType = Field(
        default=setting.engine.type, examples=[setting.engine.type]
    )

    model_config = ConfigDict(extra="allow")


class SimpleChunkRetrieveItem(SimpleChunkEngineItem, BaseRetrieveItem):
    top_k: int = Field(
        default=setting.engine.simple_chunk.retrieve.k,
        examples=[setting.engine.simple_chunk.retrieve.k],
        description="Number of top results to retrieve.",
    )
    retrieve_type: RetrieveType = Field(
        default=setting.engine.simple_chunk.retrieve.type,
        examples=[setting.engine.simple_chunk.retrieve.type],
        description="Type of retrieval strategy used.",
    )

    dense_weight: float = Field(
        default=setting.engine.simple_chunk.retrieve.weight.dense,
        examples=[setting.engine.simple_chunk.retrieve.weight.dense],
        description="Weight for dense retrieval methods. Only used for hybrid retrieve type.",
    )

    sparse_weight: float = Field(
        default=setting.engine.simple_chunk.retrieve.weight.sparse,
        examples=[setting.engine.simple_chunk.retrieve.weight.sparse],
        description="Weight for sparse retrieval methods. Only used for hybrid retrieve type.",
    )


class RetrieveResponse(BaseResponse):
    class Data(BaseModel):
        documents: list = Field(default=..., examples=[[]])

    message: str = Field(
        default="Retrieval completed via BaseRetrieve", examples=["Retrieval completed"]
    )
    data: Data = Field(default_factory=Data)
