from fastapi import status
from fastapi.responses import JSONResponse

from aa_rag.gtypes.models.base import BaseResponse


async def handle_exception_error(request, exc):
    """
    Handle universal exception error
    Args:
        request:
        exc:

    Returns:

    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=BaseResponse(
            code=status.HTTP_400_BAD_REQUEST,
            status="failed",
            message=f"{type(exc).__name__} Error",
            data=str(exc),
        ).model_dump(),
    )
