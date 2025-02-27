from typing import List

from pydantic import BaseModel, Field, ConfigDict

from aa_rag import setting
from aa_rag.gtypes.enums import EngineType
from aa_rag.gtypes.models.base import BaseResponse
from aa_rag.gtypes.models.engine import SimpleChunkEngineItem
from aa_rag.gtypes.models.parse import ParserNeedItem


class BaseIndexItem(ParserNeedItem, BaseModel):
    pass


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
