from typing import List

from fastapi import status
from pydantic import BaseModel, Field, ConfigDict, FilePath

from aa_rag import default as dfs
from aa_rag.gtypes import IndexType
from aa_rag.gtypes.enums import DBMode


class IndexItem(BaseModel):
    knowledge_name: str = Field(default=..., examples=["fairy_tale"])
    index_type: IndexType = Field(default=dfs.INDEX_TYPE, examples=[dfs.INDEX_TYPE])
    embedding_model: str = Field(
        default=dfs.EMBEDDING_MODEL, examples=[dfs.EMBEDDING_MODEL]
    )

    model_config = ConfigDict(extra="allow")


class ChunkIndexItem(IndexItem):
    file_path: FilePath = Field(default=..., examples=["./data/fairy_tale.txt"])
    db_mode: DBMode = Field(
        default=dfs.DB_MODE,
        examples=[dfs.DB_MODE],
        description="Mode for inserting data to db",
    )
    chunk_size: int = Field(
        default=dfs.INDEX_CHUNK_SIZE, examples=[dfs.INDEX_CHUNK_SIZE]
    )
    chunk_overlap: int = Field(
        default=dfs.INDEX_OVERLAP_SIZE, examples=[dfs.INDEX_OVERLAP_SIZE]
    )
    index_type: IndexType = Field(default=dfs.INDEX_TYPE, examples=[dfs.INDEX_TYPE])

    model_config = ConfigDict(extra="forbid")


class IndexResponse(BaseModel):
    class Data(BaseModel):
        affect_row_id: List[str] = Field(default=..., examples=[[]])
        affect_row_num: int = Field(default=..., examples=[0])
        table_name: str = Field(..., examples=["fairy_tale_chunk_text_embedding_model"])

    code: int = Field(..., examples=[status.HTTP_200_OK])
    status: str = Field(default="success", examples=["success"])
    message: str = Field(
        default="Indexing completed via ChunkIndex",
        examples=["Indexing completed via ChunkIndex"],
    )
    data: Data = Field(default_factory=Data)
