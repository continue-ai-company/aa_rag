from pydantic import BaseModel, Field

from aa_rag import setting


class BaseKnowledgeItem(BaseModel):
    llm: str = Field(
        default=setting.llm.model,
        description="The language model used for the knowledge base",
    )
    embedding_model: str = Field(
        default=setting.embedding.model,
        description="The embedding model used for the knowledge base",
    )
