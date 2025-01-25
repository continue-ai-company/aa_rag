import json

from fastapi import status
from fastapi.responses import JSONResponse

from aa_rag.gtypes.models.base import BaseResponse


async def handle_validation_error(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=BaseResponse(
            code=status.HTTP_400_BAD_REQUEST,
            status="failed",
            message="Validation Error",
            data=json.loads(exc.json),
        ).model_dump(),
    )


async def handle_assertion_error(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=BaseResponse(
            code=status.HTTP_400_BAD_REQUEST,
            status="failed",
            message="Assertion Error",
            data=str(exc),
        ).model_dump(),
    )
