from typing import Optional

from pydantic import BaseModel, Field

from aa_rag import setting


class BaseEngineItem(BaseModel):
    index_kwargs: Optional[dict] = Field(
        default=None,
        description="Indexing parameters for the engine.",
    )

    store_kwargs: Optional[dict] = Field(
        default=None,
        description="Storage parameters for the engine.",
    )


class SimpleChunkEngineItem(BaseEngineItem):
    knowledge_name: str = Field(default=..., examples=["fairy_tale"])
    identifier: Optional[str] = Field(
        default=None,
        examples=["12345678"],
        description="Identifies the index target table. You can use User ID as an identifier.",
    )

    embedding_model: str = Field(
        default=setting.embedding.model,
        description="Embedding model for the engine.",
    )
