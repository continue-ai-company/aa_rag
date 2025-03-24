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
    prefix="/solution", tags=["solution"], responses={404: {"description": "Not Found"}}
)


@router.get("/")
async def root():
    return {
        "built_in": True,
        "description": "项目部署方案库",
    }


@router.post(
    "/index", response_model=SolutionIndexResponse, status_code=status.HTTP_201_CREATED
)
async def index(item: SolutionIndexItem, response: Response):
    solution = SolutionKnowledge(**item.model_dump(include={"llm", "embedding_model"}))

    solution.index(**item.model_dump(include={"env_info", "procedure", "project_meta"}))

    return SolutionIndexResponse(response=response)


@router.post("/retrieve", response_model=SolutionRetrieveResponse)
async def retrieve(item: SolutionRetrieveItem, response: Response):
    solution = SolutionKnowledge(
        **item.model_dump(include={"llm", "embedding_model", "relation_db_path"})
    )

    guide: Guide | None = solution.retrieve(
        **item.model_dump(include={"env_info", "project_meta"})
    )
    if guide is None:
        response.status_code = 404
        return SolutionRetrieveResponse(
            response=response,
            message="Guide not found",
        )
    else:
        return SolutionRetrieveResponse(
            response=response, data=[utils.guide2document(guide)]
        )
