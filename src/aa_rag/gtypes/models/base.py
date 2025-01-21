from fastapi import status
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    code: int = Field(..., examples=[status.HTTP_200_OK])
    status: str = Field(default="success", examples=["success"])
