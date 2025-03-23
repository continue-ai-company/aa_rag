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
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=BaseResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            status="failed",
            message=f"{type(exc).__name__} Error",
            data=str(exc),
        ).model_dump(),
    )


async def handel_FileNotFoundError(request, exc):
    """
    Handle FileNotFoundError
    Args:
        request:
        exc:

    Returns:

    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=BaseResponse(
            code=status.HTTP_404_NOT_FOUND,
            status="failed",
            message=f"{type(exc).__name__} Error",
            data=str(exc),
        ).model_dump(),
    )
