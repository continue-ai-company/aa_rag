from typing import List

from pydantic import BaseModel, Field, ConfigDict, FilePath

from aa_rag import setting
from aa_rag.gtypes import IndexType, EmbeddingModel
from aa_rag.gtypes.enums import DBMode
from aa_rag.gtypes.models.base import BaseResponse


class IndexItem(BaseModel):
    knowledge_name: str = Field(default=..., examples=["fairy_tale"])
    index_type: IndexType = Field(
        default=setting.index.type, examples=[setting.index.type]
    )
    embedding_model: EmbeddingModel = Field(
        default=setting.embedding.model, examples=[setting.embedding.model]
    )

    model_config = ConfigDict(extra="allow")


class ChunkIndexItem(IndexItem):
    file_path: FilePath = Field(default=..., examples=["./data/fairy_tale.txt"])
    db_mode: DBMode = Field(
        default=setting.db.vector.mode,
        examples=[setting.db.vector.mode],
        description="Mode for inserting data to db",
    )
    chunk_size: int = Field(
        default=setting.index.chunk_size, examples=[setting.index.chunk_size]
    )
    chunk_overlap: int = Field(
        default=setting.index.overlap_size, examples=[setting.index.overlap_size]
    )
    index_type: IndexType = Field(
        default=setting.index.type, examples=[setting.index.type]
    )

    model_config = ConfigDict(extra="forbid")


class IndexResponse(BaseResponse):
    class Data(BaseModel):
        affect_row_id: List[str] = Field(default=..., examples=[[]])
        affect_row_num: int = Field(default=..., examples=[0])
        table_name: str = Field(..., examples=["fairy_tale_chunk_text_embedding_model"])

    message: str = Field(
        default="Indexing completed via ChunkIndex",
        examples=["Indexing completed via ChunkIndex"],
    )
    data: Data = Field(default_factory=Data)
