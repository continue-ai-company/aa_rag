from typing import List

from fastapi import Response
from langchain_core.documents import Document
from pydantic import BaseModel, Field, computed_field, ConfigDict, field_validator


class BaseResponse(BaseModel):
    default_response_code: int = Field(default=200, exclude=True)
    response: Response = Field(
        default=..., exclude=True, description="The response of the API"
    )

    message: str = Field(default=...)
    data: List[Document] = Field(
        default_factory=list, description="The data of the response"
    )

    @computed_field(return_type=int)
    @property
    def code(self):
        return self.response.status_code or self.default_response_code

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("data")
    def validate(cls, v):
        result = []
        for _ in v:
            doc_json = _.model_dump()
            if "id" in doc_json.keys() and doc_json["id"] is None:
                doc_json.pop("id")

            if "type" in doc_json.keys() and doc_json["type"] == "Document":
                doc_json.pop("type")

            result.append(doc_json)

        return result
