from pydantic import BaseModel, Field, ConfigDict, field_validator

from aa_rag import setting
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


class RetrieveResponse(BaseResponse):
    class Data(BaseModel):
        documents: list = Field(default=..., examples=[[]])

        @field_validator("documents")
        def validate_documents(cls, v):
            """
            Remove identifier from metadata
            """
            for _ in v:
                if (
                    isinstance(_, dict)
                    and "metadata" in _
                    and "identifier" in _["metadata"]
                ):
                    _.pop("identifier")
            return v

    message: str = Field(
        default="Retrieval completed via BaseRetrieve", examples=["Retrieval completed"]
    )
    data: Data = Field(default_factory=Data)
