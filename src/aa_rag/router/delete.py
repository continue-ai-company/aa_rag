from typing import List

from fastapi import APIRouter, status, Response

from aa_rag.engine.simple_chunk import SimpleChunk, SimpleChunkInitParams
from aa_rag.gtypes.models.delete import (
    SimpleChunkDeleteItem,
    SolutionDeleteItem,
)
from aa_rag.knowledge_base.built_in.qa import QAKnowledge
from aa_rag.knowledge_base.built_in.solution import SolutionKnowledge
from aa_rag.router.qa import router as qa_router
from aa_rag.router.solution import router as solution_router

router = APIRouter(
    prefix="/delete",
    tags=["Delete"],
    responses={404: {"description": "Not Found？？"}},
)


@qa_router.get("/delete", status_code=status.HTTP_204_NO_CONTENT)
@router.get("/qa", status_code=status.HTTP_204_NO_CONTENT)
def qa(id: str | None = None, ids: List[str] | None = None):
    assert id or ids, "id or ids must be provided"
    engine = QAKnowledge().engine

    if id:
        with engine.db.using(engine.table_name) as table:
            table.delete(f'id in ["{id}"]')
    if ids:
        cond = ",".join([f'"{i}"' for i in ids])
        cond = f"id in [{cond}]"
        with engine.db.using(engine.table_name) as table:
            table.delete(cond)


@router.post("/knowledge", status_code=status.HTTP_204_NO_CONTENT)
def knowledge(request: SimpleChunkDeleteItem):
    engine = SimpleChunk(params=SimpleChunkInitParams(**request.model_dump()))

    if request.id:
        with engine.db.using(engine.table_name) as table:
            table.delete(f'id in ["{request.id}"]')
    if request.ids:
        cond = ",".join([f'"{i}"' for i in request.ids])
        cond = f"id in [{cond}]"
        with engine.db.using(engine.table_name) as table:
            table.delete(cond)


@solution_router.post("/delete", status_code=status.HTTP_204_NO_CONTENT)
@router.post("/solution", status_code=status.HTTP_204_NO_CONTENT)
def solution(request: SolutionDeleteItem, response: Response):
    solution_obj = SolutionKnowledge()

    if request.id:
        with solution_obj.nosql_db.using(solution_obj.table_name) as table:
            hit_record = table.select({"project_id": request.id})

            try:
                guides = hit_record[0]["guides"]
            except Exception:
                response.status_code = status.HTTP_404_NOT_FOUND
                return

            new_guides = []
            for guide in guides:
                compatible_env = guide["compatible_env"]
                if compatible_env["platform"] != request.platform or compatible_env["arch"] != request.arch:
                    new_guides.append(guide)
                else:
                    pass

            table.update({"guides": new_guides}, {"project_id": request.id})
