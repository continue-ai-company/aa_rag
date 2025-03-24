from pydantic import Field, ConfigDict

from aa_rag import setting
from aa_rag.engine.lightrag import LightRAGInitParams, LightRAGIndexParams
from aa_rag.engine.simple_chunk import SimpleChunkIndexParams, SimpleChunkInitParams
from aa_rag.gtypes.enums import EngineType
from aa_rag.gtypes.models.base import BaseResponse
from aa_rag.gtypes.models.parse import ParserNeedItem


class BaseIndexItem(ParserNeedItem):
    pass


class IndexItem(BaseIndexItem):
    engine_type: EngineType = Field(
        default=setting.engine.type, examples=[setting.engine.type]
    )

    model_config = ConfigDict(extra="allow")


class SimpleChunkIndexItem(
    SimpleChunkInitParams, SimpleChunkIndexParams, BaseIndexItem
):
    source_data: None = Field(
        None, exclude=True, validate_default=False, deprecated=True
    )


class LightRAGIndexItem(LightRAGInitParams, LightRAGIndexParams, BaseIndexItem):
    source_data: None = Field(
        None, exclude=True, validate_default=False, deprecated=True
    )


class IndexResponse(BaseResponse):
    default_response_code: int = Field(default=201, exclude=True)
    message: str = Field(
        default="Indexing completed via SimpleChunkIndex",
        examples=["Indexing completed via SimpleChunkIndex"],
    )
