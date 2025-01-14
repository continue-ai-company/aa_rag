import json

from fastapi import status
from fastapi.responses import JSONResponse


async def handle_validation_error(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": "Validation Error", "detail": json.loads(exc.json())},
    )


async def handle_assertion_error(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": "Assertion Error", "detail": str(exc)},
    )
