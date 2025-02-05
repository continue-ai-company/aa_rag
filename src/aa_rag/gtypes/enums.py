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
