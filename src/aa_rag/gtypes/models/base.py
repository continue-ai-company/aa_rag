from typing import Any

from fastapi import status
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    code: int = Field(..., examples=[status.HTTP_200_OK])
    status: str = Field(default=..., examples=["success"])
    message: str = Field(default=...)
    data: Any = Field(default=...)
