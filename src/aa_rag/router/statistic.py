from typing import Dict, List

from fastapi import APIRouter, Response

from aa_rag.engine.simple_chunk import SimpleChunkInitParams, SimpleChunk
from aa_rag.gtypes.models.statistic import SimpleChunkStatisticItem
from aa_rag.knowledge_base.built_in.qa import QAKnowledge
from aa_rag.knowledge_base.built_in.solution import SolutionKnowledge
from aa_rag.router.qa import router as qa_router
from aa_rag.router.solution import router as solution_router

router = APIRouter(
    prefix="/statistic",
    tags=["Statistic"],
    responses={404: {"description": "Not Found"}},
)


@router.post("/knowledge")
def knowledge(request: SimpleChunkStatisticItem, response: Response):
    result: Dict[str, List] = {}
    engine = SimpleChunk(params=SimpleChunkInitParams(**request.model_dump()))

    if engine.table_name not in engine.db.table_list():
        response.status_code = 404
        return []
    else:
        with engine.db.using(engine.table_name) as table:
            hit_record_s = table.query(
                f'array_contains(identifier,"{request.identifier}")',
                output_fields=["*"],
            )

            for record in hit_record_s:
                record.pop("identifier") if "identifier" in record.keys() else None
                record.pop("vector") if "vector" in record.keys() else None

                source = record.get("metadata", {}).get("source")
                assert source is not None, "source is None"

                if source not in result.keys():
                    result[source] = []
                result[source].append(record)

        if result:
            return result
        else:
            response.status_code = 404
            return []


@qa_router.get("/statistic")
@router.get("/qa")
def qa(response: Response):
    result: List = []
    engine = QAKnowledge().engine

    with engine.db.using(engine.table_name) as table:
        hit_record_s = table.query(output_fields=["*"])
        for record in hit_record_s:
            record.pop("identifier") if "identifier" in record.keys() else None
            record.pop("vector") if "vector" in record.keys() else None
            result.append(record)

    if result:
        return result
    else:
        response.status_code = 404
        return []


@solution_router.get("/statistic")
@router.get("/solution")
def solution(response: Response):
    result: Dict[str, Dict] = {}
    solution_obj = SolutionKnowledge()

    with solution_obj.nosql_db.using(solution_obj.table_name) as table:
        all_docs_s = table.select()
        for record in all_docs_s:
            record.pop("_id") if "_id" in record.keys() else None

            project_name = record.get("name")
            if project_name not in result.keys():
                result[project_name] = {}
            result[project_name] = record

    if all_docs_s:
        pass
    else:
        response.status_code = 404
    return result
