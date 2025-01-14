from fastapi import APIRouter, HTTPException

from aa_rag.gtypes.enums import RetrieveType
from aa_rag.gtypes.models.retrieve import (
    RetrieveItem,
    HybridRetrieveItem,
    DenseRetrieveItem,
    BM25RetrieveItem,
    RetrieveResponse,
)
from aa_rag.retrieve.bm25 import BM25Retrieve
from aa_rag.retrieve.dense import DenseRetrieve
from aa_rag.retrieve.hybrid import HybridRetrieve

router = APIRouter(
    prefix="/retrieve", tags=["Retrieve"], responses={404: {"description": "Not found"}}
)


@router.post("/")
async def root(item: RetrieveItem):
    match item.retrieve_type:
        case RetrieveType.HYBRID:
            hybrid_item = HybridRetrieveItem(**item.model_dump())
            return await hybrid_retrieve(hybrid_item)
        case RetrieveType.DENSE:
            dense_item = DenseRetrieveItem(**item.model_dump())
            return await dense_retrieve(dense_item)
        case RetrieveType.BM25:
            bm25_item = BM25RetrieveItem(**item.model_dump())
            return await bm25_retrieve(bm25_item)
        case _:
            raise HTTPException(status_code=400, detail="RetrieveType not supported")


@router.post("/hybrid")
async def hybrid_retrieve(item: HybridRetrieveItem) -> RetrieveResponse:
    retriever = HybridRetrieve(**item.model_dump())

    result = retriever.retrieve(
        query=item.query,
        top_k=item.top_k,
        only_page_content=item.only_page_content,
        dense_weight=item.weight_dense,
        sparse_weight=item.weight_sparse,
    )

    return RetrieveResponse(
        code=200,
        status="success",
        message="Retrieval completed via HybridRetrieve",
        data=RetrieveResponse.Data(documents=result),
    )


@router.post("/dense")
async def dense_retrieve(item: DenseRetrieveItem) -> RetrieveResponse:
    retriever = DenseRetrieve(**item.model_dump())

    result = retriever.retrieve(
        query=item.query, top_k=item.top_k, only_page_content=item.only_page_content
    )

    return RetrieveResponse(
        code=200,
        status="success",
        message="Retrieval completed via DenseRetrieve",
        data=RetrieveResponse.Data(documents=result),
    )


@router.post("/bm25")
async def bm25_retrieve(item: BM25RetrieveItem) -> RetrieveResponse:
    retriever = BM25Retrieve(**item.model_dump())

    result = retriever.retrieve(
        query=item.query, top_k=item.top_k, only_page_content=item.only_page_content
    )

    return RetrieveResponse(
        code=200,
        status="success",
        message="Retrieval completed via BM25Retrieve",
        data=RetrieveResponse.Data(documents=result),
    )
