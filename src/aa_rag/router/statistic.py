from fastapi import APIRouter, Response

from aa_rag import utils, setting
from aa_rag.db.base import BaseVectorDataBase, BaseNoSQLDataBase
from aa_rag.gtypes.models.statistic import StatisticKnowledgeItem
from aa_rag.router.qa import router as qa_router
from aa_rag.router.solution import router as solution_router

router = APIRouter(
    prefix="/statistic",
    tags=["Statistic"],
    responses={404: {"description": "Not Found"}},
)


@router.get("/knowledge")
def knowledge(request: StatisticKnowledgeItem, response: Response):
    vector_db: BaseVectorDataBase = utils.get_vector_db(setting.storage.vector)
    table_list = vector_db.table_list()

    hit_table_s = list(
        filter(lambda x: x.split("__", 1)[0] == request.knowledge_name, table_list)
    )

    result = []
    for table_name in hit_table_s:
        with vector_db.using(table_name) as table:
            hit_record_s = table.query(
                f'array_contains(identifier,"{request.identifier}")',
                output_fields=["metadata", "identifier"],
            )
            metadata_s = [_.get("metadata", {}) for _ in hit_record_s]
            all_source = [_.get("source") for _ in metadata_s]
            result.extend(all_source)

    result = list(set(result))
    if None in result:
        result.remove(None)

    if result:
        return result
    else:
        response.status_code = 404
        return []


@qa_router.get("/statistic")
@router.get("/qa")
def qa(response: Response):
    vector_db: BaseVectorDataBase = utils.get_vector_db(setting.storage.vector)
    table_list = vector_db.table_list()

    hit_table_s = list(filter(lambda x: x.split("__", 1)[0] == "qa", table_list))

    result = []
    for table_name in hit_table_s:
        with vector_db.using(table_name) as table:
            hit_record_s = table.query(output_fields=["text"])
            text_s = [_.get("text") for _ in hit_record_s]
            result.extend(text_s)

    result = list(set(result))

    if result:
        return result
    else:
        response.status_code = 404
        return []


@solution_router.get("/statistic")
@router.get("/solution")
def solution(response: Response):
    nosql_db: BaseNoSQLDataBase = utils.get_nosql_db(setting.storage.nosql)
    with nosql_db.using("solution") as table:
        all_docs_s = table.select()
        for _ in all_docs_s:
            _.pop("project_id")
            _.pop("project_meta")

    if all_docs_s:
        return all_docs_s
    else:
        response.status_code = 404
        return []
