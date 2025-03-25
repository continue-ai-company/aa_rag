from pydantic import BaseModel, Field, field_validator


class StatisticKnowledgeItem(BaseModel):
    knowledge_name: str = Field(
        ..., description="knowledge name", examples=["user_manual"]
    )
    identifier: str = Field(
        default="common", description="The identifier of the knowledge"
    )

    @field_validator("knowledge_name")
    def check(cls, v):
        if "-" in v:
            v.replace("-", "_")
        return v
