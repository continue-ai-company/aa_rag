from enum import Enum


class IndexType(Enum):
    CHUNK: str = "chunk"

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
    OVERWRITE = "overwrite"
    UPSERT = "upsert"

    def __str__(self):
        return f"{self.value}"


class VectorDBType(Enum):
    LANCE: str = "lance"
    MILVUS: str = "milvus"

    def __str__(self):
        return f"{self.value}"


class NoSQLDBType(Enum):
    TINYDB: str = "tinydb"
    MONGODB: str = "mongodb"

    def __str__(self):
        return f"{self.value}"


class EngineType(Enum):
    SimpleChunk: str = "chunk"
    LightRAG: str = "lightrag"

    def __str__(self):
        return f"{self.value}"


class ParsingType(Enum):
    MARKITDOWN: str = "markitdown"

    def __str__(self):
        return f"{self.value}"


class LightRAGVectorStorageType(Enum):
    MILVUS: str = "MilvusVectorDBStorage"

    def __str__(self):
        return f"{self.value}"


class LightRAGGraphStorageType(Enum):
    NEO4J: str = "Neo4JStorage"
    NETWORKX: str = "NetworkXStorage"

    def __str__(self):
        return f"{self.value}"
