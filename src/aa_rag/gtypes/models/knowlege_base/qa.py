from typing import List, Optional

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
    class Data(BaseModel):
        affect_row_ids: Optional[List[str]] = Field(
            None, examples=["1"], description="The id of the inserted row"
        )

    data: Data = Field(..., description="The data of the response")


class QARetrieveItem(BaseModel):
    error_desc: str = Field(
        ..., examples=["error_desc"], description="The error description"
    )
    tags: list[str] | None = Field(
        None, examples=[["tags"]], description="The tags of the QA"
    )


class QARetrieveResponse(BaseResponse):
    class Data(BaseModel):
        qa: List[dict] = Field(
            ...,
            examples=[
                {
                    "error_desc": "error_desc",
                    "error_solution": "error_solution",
                    "tags": ["tags"],
                }
            ],
        )

    data: Data = Field(..., description="The data of the response")
