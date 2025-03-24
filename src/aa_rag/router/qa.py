from fastapi import APIRouter

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


@router.post("/index", response_model=QAIndexResponse)
async def index(item: QAIndexItem):
    qa = QAKnowledge()

    result = qa.index(
        **item.model_dump(include={"error_desc", "error_solution", "tags"})
    )

    return QAIndexResponse(
        code=200,
        status="success",
        message="Indexing completed in QA Knowledge Base",
        data=QAIndexResponse.Data(affect_row_ids=result),
    )


@router.post("/retrieve", response_model=QARetrieveResponse)
async def retrieve(item: QARetrieveItem):
    qa = QAKnowledge()

    result = qa.retrieve(**item.model_dump(include={"error_desc", "tags"}))
    return QARetrieveResponse(
        code=200,
        status="success",
        message="Retrieving completed in QA Knowledge Base",
        data=QARetrieveResponse.Data(qa=result),
    )
