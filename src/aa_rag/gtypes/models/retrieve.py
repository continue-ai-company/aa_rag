from pydantic import BaseModel, Field, ConfigDict

from aa_rag import default as dfs
from aa_rag.gtypes import IndexType, EmbeddingModel
from aa_rag.gtypes.enums import RetrieveType


class RetrieveItem(BaseModel):
    knowledge_name: str = Field(default=..., examples=["fairy_tale"])
    index_type: IndexType = Field(default=dfs.INDEX_TYPE, examples=[dfs.INDEX_TYPE])
    retrieve_type: RetrieveType = Field(
        default=RetrieveType.HYBRID, examples=[dfs.RETRIEVE_TYPE]
    )
    embedding_model: EmbeddingModel = Field(
        default=dfs.EMBEDDING_MODEL, examples=[dfs.EMBEDDING_MODEL]
    )

    top_k: int = Field(default=dfs.RETRIEVE_TOP_K, examples=[dfs.RETRIEVE_TOP_K])
    only_page_content: bool = Field(
        default=dfs.RETRIEVE_ONLY_PAGE_CONTENT,
        examples=[dfs.RETRIEVE_ONLY_PAGE_CONTENT],
    )

    model_config = ConfigDict(extra="allow")


class HybridRetrieveItem(RetrieveItem):
    query: str = Field(default=..., examples=["What is the story of Cinderella?"])
    weight_dense: float = Field(
        default=dfs.RETRIEVE_HYBRID_DENSE_WEIGHT,
        examples=[dfs.RETRIEVE_HYBRID_DENSE_WEIGHT],
    )
    weight_sparse: float = Field(
        default=dfs.RETRIEVE_HYBRID_SPARSE_WEIGHT,
        examples=[dfs.RETRIEVE_HYBRID_SPARSE_WEIGHT],
    )

    model_config = ConfigDict(extra="forbid")


class DenseRetrieveItem(RetrieveItem):
    query: str = Field(default=..., examples=["What is the story of Cinderella?"])

    model_config = ConfigDict(extra="forbid")


class BM25RetrieveItem(RetrieveItem):
    query: str = Field(default=..., examples=["What is the story of Cinderella?"])

    model_config = ConfigDict(extra="forbid")


class RetrieveResponse(BaseModel):
    class Data(BaseModel):
        documents: list = Field(default=..., examples=[[]])

    code: int = Field(..., examples=[200])
    status: str = Field(default="success", examples=["success"])
    message: str = Field(
        default="Retrieval completed via BaseRetrieve", examples=["Retrieval completed"]
    )
    data: Data = Field(default_factory=Data)
