from fastapi import APIRouter
from starlette.responses import JSONResponse

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


@router.post("/index", response_model=SolutionIndexResponse)
async def index(item: SolutionIndexItem):
    solution = SolutionKnowledge(**item.model_dump(include={"llm", "embedding_model"}))

    affect_row_num_s = solution.index(
        **item.model_dump(include={"env_info", "procedure", "project_meta"})
    )

    return SolutionIndexResponse(
        code=200,
        status="success",
        data=SolutionIndexResponse.Data(
            affect_row_num=affect_row_num_s, table_name="solution"
        ),
    )


@router.post("/retrieve", response_model=SolutionRetrieveResponse)
async def retrieve(item: SolutionRetrieveItem):
    solution = SolutionKnowledge(
        **item.model_dump(include={"llm", "embedding_model", "relation_db_path"})
    )

    guide: Guide | None = solution.retrieve(
        **item.model_dump(include={"env_info", "project_meta"})
    )
    if guide is None:
        return JSONResponse(
            status_code=404,
            content=SolutionRetrieveResponse(
                code=404,
                status="failed",
                message="Guide not found",
                data=SolutionRetrieveResponse.Data(guide=None),
            ).model_dump(),
        )
    else:
        return SolutionRetrieveResponse(
            code=200, status="success", data=SolutionRetrieveResponse.Data(guide=guide)
        )
