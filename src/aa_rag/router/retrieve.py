from fastapi import APIRouter, HTTPException, Response

from aa_rag.engine.lightrag import (
    LightRAGEngine,
    LightRAGInitParams,
    LightRAGRetrieveParams,
)
from aa_rag.engine.simple_chunk import (
    SimpleChunk,
    SimpleChunkRetrieveParams,
    SimpleChunkInitParams,
)
from aa_rag.gtypes.enums import EngineType
from aa_rag.gtypes.models.retrieve import (
    RetrieveItem,
    RetrieveResponse,
    SimpleChunkRetrieveItem,
    LightRAGRetrieveItem,
)

router = APIRouter(
    prefix="/retrieve", tags=["Retrieve"], responses={404: {"description": "Not found"}}
)


@router.post("/chunk", tags=["SimpleChunk"], response_model=RetrieveResponse)
async def chunk_retrieve(
    item: SimpleChunkRetrieveItem, response: Response
) -> RetrieveResponse:
    engine = SimpleChunk(SimpleChunkInitParams(**item.model_dump()))

    result = engine.retrieve(SimpleChunkRetrieveParams(**item.model_dump()))

    return RetrieveResponse(
        response=response,
        message=f"Retrieval completed via HybridRetrieve in {item.retrieve_mode}",
        data=result,
    )


@router.post("/lightrag", tags=["LightRAG"], response_model=RetrieveResponse)
async def lightrag_retrieve(
    item: LightRAGRetrieveItem, response: Response
) -> RetrieveResponse:
    engine = LightRAGEngine(LightRAGInitParams(**item.model_dump()))

    result = await engine.retrieve(LightRAGRetrieveParams(**item.model_dump()))

    return RetrieveResponse(
        response=response,
        message=f"Retrieval completed via LightRAGRetrieve in {item.retrieve_mode}",
        data=result,
    )
