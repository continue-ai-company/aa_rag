from pydantic import BaseModel, Field

from aa_rag.gtypes.models.base import BaseResponse


class QAIndexItem(BaseModel):
    error_desc: str = Field(
        ..., examples=["error_desc"], description="The error description"
    )
    error_solution: str = Field(
        ..., examples=["error_solution"], description="The error solution"
    )
    tags: list[str] = Field(
        default_factory=list, examples=[["tags"]], description="The tags of the QA"
    )


class QAIndexResponse(BaseResponse):
    default_response_code: int = Field(default=201, exclude=True)


class QARetrieveItem(BaseModel):
    error_desc: str = Field(
        ..., examples=["error_desc"], description="The error description"
    )
    tags: list[str] | None = Field(
        None, examples=[["tags"]], description="The tags of the QA"
    )


class QARetrieveResponse(BaseResponse):
    pass
