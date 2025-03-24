from fastapi import APIRouter, HTTPException, Response, status

from aa_rag import utils
from aa_rag.engine.lightrag import (
    LightRAGEngine,
    LightRAGInitParams,
    LightRAGIndexParams,
)
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
    LightRAGIndexItem,
)
from aa_rag.gtypes.models.parse import ParserNeedItem

router = APIRouter(
    prefix="/index", tags=["Index"], responses={404: {"description": "Not found"}}
)


@router.post(
    "/chunk",
    tags=["SimpleChunk"],
    response_model=IndexResponse,
    status_code=status.HTTP_201_CREATED,
)
async def chunk_index(item: SimpleChunkIndexItem, response: Response) -> IndexResponse:
    source_data = await utils.parse_content(params=ParserNeedItem(**item.model_dump()))

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
        response=response, message="Indexing completed via SimpleChunkIndex", data=[]
    )


@router.post(
    "/lightrag",
    tags=["LightRAG"],
    response_model=IndexResponse,
    status_code=status.HTTP_201_CREATED,
)
async def lightrag_index(item: LightRAGIndexItem, response: Response) -> IndexResponse:
    # parse content
    source_data = await utils.parse_content(params=ParserNeedItem(**item.model_dump()))

    # index content
    engine = LightRAGEngine(params=LightRAGInitParams(**item.model_dump()))

    await engine.index(
        params=LightRAGIndexParams(
            **{
                **item.model_dump(),
                "source_data": source_data,
            }
        )
    )

    return IndexResponse(
        response=response, message="Indexing completed via LightRAGIndex", data=[]
    )
