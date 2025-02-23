from fastapi import APIRouter, HTTPException

from aa_rag.engine.simple_chunk import SimpleChunk
from aa_rag.gtypes.enums import EngineType
from aa_rag.gtypes.models.engine import SimpleChunkEngineItem
from aa_rag.gtypes.models.retrieve import (
    RetrieveItem,
    RetrieveResponse,
    SimpleChunkRetrieveItem,
)

router = APIRouter(
    prefix="/retrieve", tags=["Retrieve"], responses={404: {"description": "Not found"}}
)


@router.post("/")
async def root(item: RetrieveItem):
    match item.engine_type:
        case EngineType.SIMPLE_CHUNK:
            chunk_item = SimpleChunkRetrieveItem(**item.model_dump())
            return await chunk_retrieve(chunk_item)
        case _:
            raise HTTPException(status_code=400, detail="RetrieveType not supported")


@router.post("/chunk", tags=["SimpleChunk"])
async def chunk_retrieve(item: SimpleChunkRetrieveItem) -> RetrieveResponse:
    engine_fields = SimpleChunkEngineItem.model_fields
    assert isinstance(engine_fields, dict), "engine_fields must be a dict"

    engine = SimpleChunk(**item.model_dump(include=set(engine_fields.keys())))

    result = engine.retrieve(**item.model_dump(exclude=set(engine_fields.keys())))

    return RetrieveResponse(
        code=200,
        status="success",
        message="Retrieval completed via HybridRetrieve",
        data=RetrieveResponse.Data(documents=result),
    )
