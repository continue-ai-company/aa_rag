from typing import List

from pydantic import field_validator, Field, model_validator, BaseModel

from aa_rag.engine.simple_chunk import SimpleChunkInitParams
from aa_rag.gtypes.models.knowlege_base.solution import CompatibleEnv


class BaseDeleteItem(BaseModel):
    id: str | None = Field(
        default=None,
        examples=["12"],
        description="The id of the item to be deleted",
    )
    ids: List[str] | None = Field(
        default=None,
        examples=[["12", "23"]],
        description="The ids of the items to be deleted",
    )

    @model_validator(mode="after")
    def check_id(self):
        assert self.id or self.ids, "id or ids must be provided"
        return self


class SimpleChunkDeleteItem(SimpleChunkInitParams, BaseDeleteItem):
    @field_validator("knowledge_name")
    def check(cls, v):
        if "-" in v:
            v.replace("-", "_")
        return v


class SolutionDeleteItem(CompatibleEnv):
    id: str = Field(
        default=...,
        examples=["12"],
        description="The id of the project to be deleted",
    )
