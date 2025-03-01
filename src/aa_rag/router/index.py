from fastapi import APIRouter, HTTPException

from aa_rag.engine.simple_chunk import (
    SimpleChunk,
    SimpleChunkInitParams,
    SimpleChunkIndexParams,
)
from aa_rag.gtypes.enums import EngineType
from aa_rag.gtypes.models.index import (
    IndexItem,
    SimpleChunkIndexItem,
    IndexResponse,
)
from aa_rag.gtypes.models.parse import ParserNeedItem
from aa_rag.parse.markitdown import MarkitDownParser

router = APIRouter(
    prefix="/index", tags=["Index"], responses={404: {"description": "Not found"}}
)


@router.post("/")
async def root(item: IndexItem):
    match item.engine_type:
        case EngineType.SimpleChunk:
            chunk_item = SimpleChunkIndexItem(**item.model_dump())
            return await chunk_index(chunk_item)
        case _:
            raise HTTPException(status_code=400, detail="IndexType not supported")


@router.post("/chunk", tags=["SimpleChunk"])
async def chunk_index(item: SimpleChunkIndexItem) -> IndexResponse:
    # parse content

    parser = MarkitDownParser()
    source_data = await parser.aparse(
        **ParserNeedItem(**item.model_dump()).model_dump()
    )

    # index content

    engine = SimpleChunk(params=SimpleChunkInitParams(**item.model_dump()))

    engine.index(
        params=SimpleChunkIndexParams(
            **{
                **item.model_dump(),
                "source_data": source_data,
            }
        )
    )

    return IndexResponse(
        code=200,
        status="success",
        message="Indexing completed via SimpleChunkIndex",
        data=IndexResponse.Data(),
    )
