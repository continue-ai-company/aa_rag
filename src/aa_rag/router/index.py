from fastapi import APIRouter, HTTPException

from aa_rag import utils
from aa_rag.engine.simple_chunk import SimpleChunk
from aa_rag.gtypes.enums import EngineType
from aa_rag.gtypes.models.engine import SimpleChunkEngineItem
from aa_rag.gtypes.models.index import IndexItem, SimpleChunkIndexItem, IndexResponse

router = APIRouter(
    prefix="/index", tags=["Index"], responses={404: {"description": "Not found"}}
)


@router.post("/")
async def root(item: IndexItem):
    match item.engine_type:
        case EngineType.SIMPLE_CHUNK:
            chunk_item = SimpleChunkIndexItem(**item.model_dump())
            return await chunk_index(chunk_item)
        case _:
            raise HTTPException(status_code=400, detail="IndexType not supported")


@router.post("/chunk", tags=["SimpleChunk"])
async def chunk_index(item: SimpleChunkIndexItem) -> IndexResponse:
    # parse content
    source_data = utils.parse_file(str(item.file_path), use_cache=item.use_cache)

    engine_fields = SimpleChunkEngineItem.model_fields
    assert isinstance(engine_fields, dict), "engine_fields must be a dict"

    engine = SimpleChunk(**item.model_dump(include=set(engine_fields.keys())))

    engine.index(source_data=source_data)

    return IndexResponse(
        code=200,
        status="success",
        message="Indexing completed via SimpleChunkIndex",
        data=IndexResponse.Data(
            table_name=[obj_name[1] for _, obj_name in engine.db.items()],
        ),
    )
