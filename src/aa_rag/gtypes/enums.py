from enum import Enum


class IndexType(Enum):
    CHUNK: str = "chunk"

    def __str__(self):
        return f"{self.value}"


class OpenAIModel(Enum):
    TEXT_EMBEDDING_3_SMALL: str = "text-embedding-3-small"
    GPT_4O: str = "gpt-4o"
    GPT_4O_MINI: str = "gpt-4o-mini"

    def __str__(self):
        return f"{self.value}"


class EmbeddingModel(Enum):
    TEXT_EMBEDDING_3_SMALL: str = OpenAIModel.TEXT_EMBEDDING_3_SMALL.value

    def __str__(self):
        return f"{self.value}"


class LLModel(Enum):
    GPT_4O: str = OpenAIModel.GPT_4O.value
    GPT_4O_MINI: str = OpenAIModel.GPT_4O_MINI.value

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
