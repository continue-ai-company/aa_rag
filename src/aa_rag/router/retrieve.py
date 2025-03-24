from fastapi import APIRouter, HTTPException

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


@router.post("/")
async def root(item: RetrieveItem):
    match item.engine_type:
        case EngineType.SimpleChunk:
            chunk_item = SimpleChunkRetrieveItem(**item.model_dump())
            return await chunk_retrieve(chunk_item)
        case _:
            raise HTTPException(status_code=400, detail="RetrieveType not supported")


@router.post("/chunk", tags=["SimpleChunk"], response_model=RetrieveResponse)
async def chunk_retrieve(item: SimpleChunkRetrieveItem) -> RetrieveResponse:
    engine = SimpleChunk(SimpleChunkInitParams(**item.model_dump()))

    result = engine.retrieve(SimpleChunkRetrieveParams(**item.model_dump()))

    return RetrieveResponse(
        code=200,
        status="success",
        message=f"Retrieval completed via HybridRetrieve in {item.retrieve_mode}",
        data=RetrieveResponse.Data(documents=result),
    )


@router.post("/lightrag", tags=["LightRAG"], response_model=RetrieveResponse)
async def lightrag_retrieve(item: LightRAGRetrieveItem) -> RetrieveResponse:
    engine = LightRAGEngine(LightRAGInitParams(**item.model_dump()))

    result = await engine.retrieve(LightRAGRetrieveParams(**item.model_dump()))

    return RetrieveResponse(
        code=200,
        status="success",
        message=f"Retrieval completed via LightRAGRetrieve in {item.retrieve_mode}",
        data=RetrieveResponse.Data(documents=result),
    )
