from pydantic import BaseModel, Field

from aa_rag import setting
from aa_rag.gtypes import EmbeddingModel
from aa_rag.gtypes.enums import LLModel


class BaseKnowledgeItem(BaseModel):
    llm: LLModel = Field(
        default=setting.llm.model,
        description="The language model used for the knowledge base",
    )
    embedding_model: EmbeddingModel = Field(
        default=setting.embedding.model,
        description="The embedding model used for the knowledge base",
    )
