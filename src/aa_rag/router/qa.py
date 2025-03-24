from fastapi import APIRouter, status, Response

from aa_rag.gtypes.models.knowlege_base.qa import (
    QAIndexItem,
    QAIndexResponse,
    QARetrieveItem,
    QARetrieveResponse,
)
from aa_rag.knowledge_base.built_in.qa import QAKnowledge

router = APIRouter(
    prefix="/qa", tags=["qa"], responses={404: {"description": "Not Found"}}
)


@router.get("/")
async def root():
    return {
        "built_in": True,
        "description": "问题/解决方案库",
    }


@router.post(
    "/index", response_model=QAIndexResponse, status_code=status.HTTP_201_CREATED
)
async def index(item: QAIndexItem, response: Response):
    qa = QAKnowledge()

    qa.index(**item.model_dump(include={"error_desc", "error_solution", "tags"}))

    return QAIndexResponse(
        response=response,
        message="Indexing completed in QA Knowledge Base",
        data=[],
    )


@router.post("/retrieve", response_model=QARetrieveResponse)
async def retrieve(item: QARetrieveItem, response: Response):
    qa = QAKnowledge()

    result = qa.retrieve(**item.model_dump(include={"error_desc", "tags"}))
    return QARetrieveResponse(
        response=response,
        message="Retrieving completed in QA Knowledge Base",
        data=result,
    )
