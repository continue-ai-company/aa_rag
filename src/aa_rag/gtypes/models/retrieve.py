from typing import List

from langchain_core.documents import Document
from pydantic import BaseModel, Field, ConfigDict, field_validator

from aa_rag import setting
from aa_rag.engine.lightrag import LightRAGInitParams, LightRAGRetrieveParams
from aa_rag.engine.simple_chunk import SimpleChunkRetrieveParams, SimpleChunkInitParams
from aa_rag.gtypes.enums import EngineType
from aa_rag.gtypes.models.base import BaseResponse


class BaseRetrieveItem(BaseModel):
    pass


class RetrieveItem(BaseModel):
    engine_type: EngineType = Field(
        default=setting.engine.type, examples=[setting.engine.type]
    )

    model_config = ConfigDict(extra="allow")


class SimpleChunkRetrieveItem(
    SimpleChunkInitParams, SimpleChunkRetrieveParams, BaseRetrieveItem
):
    pass


class LightRAGRetrieveItem(
    LightRAGInitParams, LightRAGRetrieveParams, BaseRetrieveItem
):
    pass


class RetrieveResponse(BaseResponse):
    class Data(BaseModel):
        documents: List[Document] = Field(
            default=...,
            examples=[{"metadata": {"source": "oss://..."}, "page_content": "....."}],
        )

        @field_validator("documents")
        def validate_documents(cls, v):
            doc_s = [doc.model_dump(include={"metadata", "page_content"}) for doc in v]

            for doc in v:
                if "metadata" in doc:
                    if "identifier" in doc["metadata"]:
                        doc.pop("identifier")

            return doc_s

    message: str = Field(
        default="Retrieval completed via BaseRetrieve", examples=["Retrieval completed"]
    )
    data: Data = Field(default_factory=Data)
