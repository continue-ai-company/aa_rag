from pydantic import field_validator

from aa_rag.engine.simple_chunk import SimpleChunkInitParams


class SimpleChunkStatisticItem(SimpleChunkInitParams):
    @field_validator("knowledge_name")
    def check(cls, v):
        if "-" in v:
            v.replace("-", "_")
        return v
