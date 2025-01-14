from enum import Enum


class IndexType(Enum):
    CHUNK: str = "chunk"

    def __str__(self):
        return f"{self.value}"


class OpenAIModel(Enum):
    TEXT_EMBEDDING_3_SMALL: str = "text-embedding-3-small"

    def __str__(self):
        return f"{self.value}"


class EmbeddingModel(Enum):
    TEXT_EMBEDDING_3_SMALL: str = OpenAIModel.TEXT_EMBEDDING_3_SMALL

    def __str__(self):
        return f"{self.value}"


class RetrieveType(Enum):
    HYBRID: str = "hybrid"
    DENSE: str = "dense"
    BM25: str = "bm25"

    def __str__(self):
        return f"{self.value}"


class DBMode(Enum):
    INSERT = "insert"
    DEINSERT = "deinsert"
    OVERWRITE = "overwrite"
    UPSERT = "upsert"

    def __str__(self):
        return f"{self.value}"
