from fastapi import APIRouter, HTTPException

from aa_rag import utils
from aa_rag.gtypes import IndexType
from aa_rag.gtypes.models.index import IndexItem, ChunkIndexItem, IndexResponse
from aa_rag.index.chunk import ChunkIndex

router = APIRouter(
    prefix="/index", tags=["Index"], responses={404: {"description": "Not found"}}
)


@router.post("/")
async def root(item: IndexItem):
    match item.index_type:
        case IndexType.CHUNK:
            chunk_item = ChunkIndexItem(**item.model_dump())
            return await chunk_index(chunk_item)
        case _:
            raise HTTPException(status_code=400, detail="IndexType not supported")


@router.post("/chunk")
async def chunk_index(item: ChunkIndexItem) -> IndexResponse:
    indexer = ChunkIndex(**item.model_dump(exclude={"file_path", "mode"}))
    source_docs = utils.parse_file(item.file_path)

    indexer.index(source_docs)
    affected_row_id_s = indexer.store(mode=item.db_mode)

    return IndexResponse(
        code=200,
        status="success",
        message="Indexing completed via ChunkIndex",
        data=IndexResponse.Data(
            affect_row_id=affected_row_id_s,
            affect_row_num=len(affected_row_id_s),
            table_name=indexer.table_name,
        ),
    )
