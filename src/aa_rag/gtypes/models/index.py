from os import PathLike
from typing import List

from pydantic import BaseModel, Field, ConfigDict

from aa_rag import setting
from aa_rag.gtypes.enums import EngineType
from aa_rag.gtypes.models.base import BaseResponse
from aa_rag.gtypes.models.engine import SimpleChunkEngineItem


class BaseIndexItem(BaseModel):
    file_path: PathLike = Field(
        default=...,
        examples=[
            "user_manual/call_llm.md",
        ],
        description="Path to the file to be indexed.",
    )

    use_cache: bool = Field(
        default=True, examples=[True], description="Whether to use OSS cache."
    )


class IndexItem(BaseIndexItem):
    engine_type: EngineType = Field(
        default=setting.engine.type, examples=[setting.engine.type]
    )

    model_config = ConfigDict(extra="allow")


class SimpleChunkIndexItem(SimpleChunkEngineItem, BaseIndexItem):
    pass

    model_config = ConfigDict(extra="forbid")


class IndexResponse(BaseResponse):
    class Data(BaseModel):
        table_name: str | List[str] = Field(
            ..., examples=["fairy_tale_chunk_text_embedding_model"]
        )

    message: str = Field(
        default="Indexing completed via ChunkIndex",
        examples=["Indexing completed via ChunkIndex"],
    )
    data: Data = Field(default_factory=Data)
