from fastapi import APIRouter, status, Response

from aa_rag import utils
from aa_rag.gtypes.models.knowlege_base.solution import (
    SolutionIndexItem,
    SolutionIndexResponse,
    SolutionRetrieveItem,
    Guide,
    SolutionRetrieveResponse,
)
from aa_rag.knowledge_base.built_in.solution import SolutionKnowledge

router = APIRouter(
    prefix="/solution",
    tags=["Solution"],
    responses={404: {"description": "Not Found"}},
)


@router.get("/")
async def root():
    return {
        "built_in": True,
        "description": "项目部署方案库",
    }


@router.post(
    "/index",
    response_model=SolutionIndexResponse,
    status_code=status.HTTP_201_CREATED,
)
async def index(item: SolutionIndexItem, response: Response):
    """
    Handles the indexing of a solution in the knowledge base.

    This endpoint accepts a `SolutionIndexItem` object, processes it to create a `SolutionKnowledge` instance, and indexes the solution using the provided data. The response includes a `SolutionIndexResponse` object.

    Args:
        item (SolutionIndexItem): The input data required for indexing, including
            details like LLM, embedding model, environment info, procedure, and
            project metadata.
        response (Response): The FastAPI response object used to set the status code.

    Examples:
        Example 1: Indexing a solution with basic environment info and project metadata
        {
            "env_info": {
                "platform": "darwin",
                "arch": "arm64"
            },
            "project_meta": {
                "name": "PaddleOCR6666",
                "url": "github.com/test/run??"
            },
            "procedure": "春天花儿开，小鸟依然33333333自在，奶奶的哦哦哦哦！！！",
            "llm": "gpt-4o-mini"
        }

        Example 2: Indexing a solution with additional metadata
        {
            "env_info": {
                "platform": "linux",
                "arch": "x86_64"
            },
            "project_meta": {
                "name": "ExampleProject",
                "id": "12345",
                "description": "An example project for testing",
                "url": "github.com/example/project"
            },
            "procedure": "This is a detailed deployment procedure for the solution.",
            "llm": "gpt-3.5",
            "embedding_model": "embedding-v2"
        }

    Returns:
        SolutionIndexResponse: The response model indicating the result of the indexing
        operation, including a success message and status code.
    """
    solution = SolutionKnowledge(**item.model_dump(include={"llm", "embedding_model"}))

    solution.index(**item.model_dump(include={"env_info", "procedure", "project_meta"}))

    return SolutionIndexResponse(response=response)


@router.post("/retrieve", response_model=SolutionRetrieveResponse)
async def retrieve(item: SolutionRetrieveItem, response: Response):
    solution = SolutionKnowledge(**item.model_dump(include={"llm", "embedding_model", "relation_db_path"}))

    guide: Guide | None = solution.retrieve(**item.model_dump(include={"env_info", "project_meta"}))
    if guide is None:
        response.status_code = 404
        return SolutionRetrieveResponse(
            response=response,
            message="Guide not found",
        )
    else:
        return SolutionRetrieveResponse(response=response, data=[utils.guide2document(guide)])
