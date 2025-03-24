from fastapi import status, Response
from langchain_core.documents import Document
from starlette.responses import JSONResponse

from aa_rag.gtypes.models.base import BaseResponse


async def handle_exception_error(request, exc):
    """
    Handle universal exception error
    Args:
        request:
        exc:

    Returns:

    """
    response = Response()
    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return JSONResponse(
        status_code=response.status_code,
        content=BaseResponse(
            response=response,
            message=f"{type(exc).__name__} Error {exc}",
        ).model_dump(),
    )


async def handel_file_not_found_error(request, exc):
    """
    Handle FileNotFoundError
    Args:
        request:
        exc:

    Returns:

    """
    response = Response()
    response.status_code = status.HTTP_404_NOT_FOUND

    return JSONResponse(
        status_code=response.status_code,
        content=BaseResponse(
            response=response,
            message=f"FileNotFoundError {exc}",
        ).model_dump(),
    )
