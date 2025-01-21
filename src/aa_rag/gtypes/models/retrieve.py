from pydantic import BaseModel, Field, ConfigDict

from aa_rag import setting
from aa_rag.gtypes import IndexType, EmbeddingModel
from aa_rag.gtypes.enums import RetrieveType
from aa_rag.gtypes.models.base import BaseResponse


class RetrieveItem(BaseModel):
    knowledge_name: str = Field(default=..., examples=["fairy_tale"])
    index_type: IndexType = Field(
        default=setting.index.type, examples=[setting.index.type]
    )
    retrieve_type: RetrieveType = Field(
        default=setting.retrieve.type, examples=[setting.retrieve.type]
    )
    embedding_model: EmbeddingModel = Field(
        default=setting.embedding.model, examples=[setting.embedding.model]
    )

    top_k: int = Field(default=setting.retrieve.type, examples=[setting.retrieve.type])
    only_page_content: bool = Field(
        default=setting.retrieve.only_page_content,
        examples=[setting.retrieve.only_page_content],
    )

    model_config = ConfigDict(extra="allow")


class HybridRetrieveItem(RetrieveItem):
    query: str = Field(default=..., examples=["What is the story of Cinderella?"])
    weight_dense: float = Field(
        default=setting.retrieve.weight.dense,
        examples=[setting.retrieve.weight.dense],
    )
    weight_sparse: float = Field(
        default=setting.retrieve.weight.sparse,
        examples=[setting.retrieve.weight.sparse],
    )

    model_config = ConfigDict(extra="forbid")


class DenseRetrieveItem(RetrieveItem):
    query: str = Field(default=..., examples=["What is the story of Cinderella?"])

    model_config = ConfigDict(extra="forbid")


class BM25RetrieveItem(RetrieveItem):
    query: str = Field(default=..., examples=["What is the story of Cinderella?"])

    model_config = ConfigDict(extra="forbid")


class RetrieveResponse(BaseResponse):
    class Data(BaseModel):
        documents: list = Field(default=..., examples=[[]])

    message: str = Field(
        default="Retrieval completed via BaseRetrieve", examples=["Retrieval completed"]
    )
    data: Data = Field(default_factory=Data)
