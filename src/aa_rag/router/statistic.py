from typing import Dict, List

import pandas as pd
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
    result: List = []
    engine = SimpleChunk(params=SimpleChunkInitParams(**request.model_dump()))

    if engine.table_name not in engine.db.table_list():
        response.status_code = 404
        return []
    else:
        with engine.db.using(engine.table_name) as table:
            hit_record_s = table.query(
                f'array_contains(identifier,"{request.identifier}")',
                output_fields=["id", "metadata", "text"],
            )
        if hit_record_s:
            df = pd.DataFrame(hit_record_s)
            df["index_time"] = df["metadata"].apply(lambda x: x.get("index_time"))
            df["source"] = df["metadata"].apply(lambda x: x.get("source"))
            df_explode = df.explode("index_time")
            g_df_by_source = df_explode.groupby(["source"])

            for (source,), crt_df_source in g_df_by_source:
                crt_knowledge = dict()
                crt_knowledge["source"] = source
                crt_knowledge["version"] = dict()
                g_df_by_version = crt_df_source.groupby(["index_time"])

                for (index_time,), crt_df_index_time in g_df_by_version:
                    crt_knowledge["version"][index_time] = crt_df_index_time.to_dict(orient="records")

                result.append(crt_knowledge)

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
def solution(response: Response, project_name: str | None = None):
    """
    Retrieves statistical information about solutions stored in the knowledge base.

    This function queries the `SolutionKnowledge` database to fetch records based on
    the provided project name. If no project name is specified, it retrieves all records.
    The results are returned as a dictionary where the keys are project names and the
    values are the corresponding project data.

    Args:
        response (Response): The FastAPI response object used to set the status code.
        project_name (str | None, optional): The name of the project to filter the results.
            If not provided, all projects are retrieved.

    Returns:
        Dict[str, Dict]: A dictionary containing project names as keys and their
        corresponding data as values. If no records are found, the response status
        code is set to 404.
    """
    result: Dict[str, Dict] = {}
    solution_obj = SolutionKnowledge()

    with solution_obj.nosql_db.using(solution_obj.table_name) as table:
        if project_name:
            hit_docs_s = table.select({"name": project_name})
        else:
            hit_docs_s = table.select()
        for record in hit_docs_s:
            record.pop("_id") if "_id" in record.keys() else None

            crt_project_name: str = record["name"]
            if crt_project_name not in result.keys():
                result[crt_project_name] = {}
            result[crt_project_name] = record

    if hit_docs_s:
        pass
    else:
        response.status_code = 404
    return result
