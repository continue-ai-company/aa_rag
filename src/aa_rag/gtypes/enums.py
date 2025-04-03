from enum import Enum


class IndexType(Enum):
    CHUNK = "chunk"

    def __str__(self):
        return f"{self.value}"


class RetrieveType(Enum):
    HYBRID = "hybrid"
    DENSE = "dense"
    BM25 = "bm25"

    def __str__(self):
        return f"{self.value}"


class DBMode(Enum):
    INSERT = "insert"
    OVERWRITE = "overwrite"
    UPSERT = "upsert"

    def __str__(self):
        return f"{self.value}"


class VectorDBType(Enum):
    LANCE = "lance"
    MILVUS = "milvus"

    def __str__(self):
        return f"{self.value}"


class NoSQLDBType(Enum):
    TINYDB = "tinydb"
    MONGODB = "mongodb"

    def __str__(self):
        return f"{self.value}"


class EngineType(Enum):
    SimpleChunk = "chunk"
    LightRAG = "lightrag"

    def __str__(self):
        return f"{self.value}"


class ParsingType(Enum):
    MARKITDOWN = "markitdown"

    def __str__(self):
        return f"{self.value}"


class LightRAGVectorStorageType(Enum):
    MILVUS = "MilvusVectorDBStorage"

    def __str__(self):
        return f"{self.value}"


class LightRAGGraphStorageType(Enum):
    NEO4J = "Neo4JStorage"
    NETWORKX = "NetworkXStorage"

    def __str__(self):
        return f"{self.value}"
