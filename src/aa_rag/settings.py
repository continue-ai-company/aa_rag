import ast
import importlib
from pathlib import Path
from typing import Optional, Any, Literal

from dotenv.main import DotEnv
from pydantic import BaseModel, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from aa_rag.gtypes.enums import (
    DBMode,
    RetrieveType,
    VectorDBType,
    NoSQLDBType,
    EngineType,
    LightRAGVectorStorageType,
    LightRAGGraphStorageType,
)


def load_env(key: str, default: Any = None):
    """
    Load environment variable from .env file. Convert to python object if possible.

    Args:
        key (str): Environment variable key.
        default (Any, optional): Default value if key not found. Defaults to None.If default is a tuple,
         it will be treated as a pair of values for development and production environments.

    Returns:
        Any: Python object representing the environment variable value or the default value.
    """
    env = DotEnv(Path(".env").absolute(), verbose=False, encoding="utf-8")

    if isinstance(default, tuple):
        env_mode = env.get("ENVIRONMENT")
        env_mode = env_mode.lower() if env_mode else "development"
        dev_dft, prod_dft = default
        match env_mode.lower():
            case "development" | "dev":
                default = dev_dft
            case "production" | "prod":
                default = prod_dft
            case _:
                default = dev_dft
    else:
        default = default

    value = env.get(key)

    if value is None:
        return default
    else:
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value


class Server(BaseModel):
    host: str = Field(default="0.0.0.0", description="The host address for the server.")
    port: int = Field(
        default=222, description="The port number on which the server listens."
    )
    environment: Literal["Development", "Production"] = Field(
        default=load_env("ENVIRONMENT", ("Development", "Production")),
        description="The environment in which the server is running.",
    )


class OpenAI(BaseModel):
    api_key: Optional[SecretStr] = Field(
        default=load_env("OPENAI_API_KEY"),
        alias="OPENAI_API_KEY",
        description="API key for accessing OpenAI services.",
        validate_default=True,
    )
    base_url: str = Field(
        default=load_env("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        alias="OPENAI_BASE_URL",
        description="Base URL for OpenAI API requests.",
    )

    @model_validator(mode="after")
    def check_api_key(self):
        assert self.api_key, "API key is required."
        assert self.api_key.get_secret_value(), "API key is required."
        return self


class Storage(BaseModel):
    class LanceDB(BaseModel):
        uri: str = Field(
            default="./storage/lancedb",
            description="URI for lanceDB database location.",
        )

    class Milvus(BaseModel):
        uri: str = Field(
            default=load_env(
                "STORAGE_MILVUS_URI", ("./storage/milvus.db", "http://localhost:19530")
            ),
            description="URI for the Milvus server location.",
        )
        user: str = Field(default="", description="Username for the Milvus server.")
        password: SecretStr = Field(
            default="",
            description="Password for the Milvus server.",
            validate_default=True,
        )
        db_name: str = Field(
            default="aarag", description="Database name for the Milvus server."
        )

    class TinyDB(BaseModel):
        uri: str = Field(
            default="./storage/tinydb.json",
            description="URI for the relational database location.",
        )

    class MongoDB(BaseModel):
        uri: str = Field(
            default="mongodb://localhost:27017",
            description="URI for the MongoDB server location.",
        )
        user: str = Field(default="", description="Username for the MongoDB server.")
        password: SecretStr = Field(
            default="",
            description="Password for the MongoDB server.",
            validate_default=True,
        )
        db_name: str = Field(
            default="aarag", description="Database name for the MongoDB server."
        )

    class Neo4j(BaseModel):
        uri: str = Field(
            default=load_env("STORAGE_NEO4J_URI", (None, "bolt://localhost:7687")),
            description="URI for the Neo4j server location.",
        )
        user: str = Field(default=None, description="Username for the Neo4j server.")
        password: SecretStr = Field(
            default=None, description="Password for the Neo4j server."
        )

        @model_validator(mode="after")
        def check(self):
            if self.uri:
                if importlib.util.find_spec("neo4j") is None:
                    raise ImportError(
                        "Neo4j can only be enabled on the online service, please execute `pip install aa-rag[online]`."
                    )
            return self

    lancedb: LanceDB = Field(
        default_factory=LanceDB, description="LanceDB database configuration settings."
    )
    milvus: Milvus = Field(
        default_factory=Milvus, description="Milvus database configuration settings."
    )
    tinydb: TinyDB = Field(
        default_factory=TinyDB, description="TinyDB database configuration settings."
    )
    mongodb: MongoDB = Field(
        default_factory=MongoDB, description="MongoDB database configuration settings."
    )

    neo4j: Neo4j = Field(
        default_factory=Neo4j, description="Neo4j configuration settings."
    )

    mode: DBMode = Field(
        default=DBMode.UPSERT, description="Mode of operation for the database."
    )
    vector: VectorDBType = Field(
        default=VectorDBType.MILVUS, description="Type of vector database used."
    )
    nosql: NoSQLDBType = Field(
        default=load_env("DB_NOSQL", (NoSQLDBType.TINYDB, NoSQLDBType.MONGODB)),
        description="Type of NoSQL database used.",
    )

    @model_validator(mode="after")
    def check(self):
        if self.vector == VectorDBType.MILVUS:
            if importlib.util.find_spec("pymilvus") is None:
                raise ImportError(
                    "Milvus can only be enabled on the online service, please execute `pip install aa-rag[online]`."
                )
        if self.nosql == NoSQLDBType.TINYDB:
            if importlib.util.find_spec("tinydb") is None:
                raise ImportError(
                    "TinyDB can only be enabled on the online service, please execute `pip install aa-rag[online]`."
                )

        return self


class Embedding(BaseModel):
    model: str = Field(
        default="text-embedding-3-small",
        description="Model used for generating text embeddings.",
    )


class LLM(BaseModel):
    model: str = Field(
        default="gpt-4o",
        description="Model used for understanding text.",
    )
    multimodal_model: str = Field(
        default="gpt-4o",
        description="Model used for understanding the image.",
    )


class Engine(BaseModel):
    class SimpleChunk(BaseModel):
        class Index(BaseModel):
            chunk_size: int = Field(
                default=load_env("ENGINE_SIMPLECHUNK_INDEX_CHUNK_SIZE", 1000),
                description="Size of each chunk in the index.",
            )
            overlap_size: int = Field(
                default=load_env("ENGINE_SIMPLECHUNK_INDEX_OVERLAP_SIZE", 100),
                description="Overlap size between chunks in the index.",
            )

        class Retrieve(BaseModel):
            class Weight(BaseModel):
                dense: float = Field(
                    default=0.5, description="Weight for dense retrieval methods."
                )
                sparse: float = Field(
                    default=0.5, description="Weight for sparse retrieval methods."
                )

            k: int = Field(default=3, description="Number of top results to retrieve.")
            weight: Weight = Field(
                default_factory=Weight,
                description="Weights for different retrieval methods.",
            )
            type: RetrieveType = Field(
                default=RetrieveType.HYBRID,
                description="Type of retrieval strategy used.",
            )

        index: Index = Field(
            default_factory=Index, description="Index configuration settings."
        )
        retrieve: Retrieve = Field(
            default_factory=Retrieve, description="Retrieve configuration settings."
        )

    class LightRAG(BaseModel):
        dir: str = Field(
            default="./storage/lightrag",
            description="Directory for LightRAG database location.",
        )
        vector_storage: LightRAGVectorStorageType = Field(
            default=LightRAGVectorStorageType.MILVUS,
            description="Type of vector storage used for LightRAG.",
        )
        graph_storage: LightRAGGraphStorageType = Field(
            default=load_env(
                "LIGHTRAG_GRAPH_STORAGE",
                (LightRAGGraphStorageType.NETWORKX, LightRAGGraphStorageType.NEO4J),
            ),
            description="Type of graph storage used for LightRAG.",
        )
        llm: str = Field(
            default="gpt-4o-mini", description="Model used for understanding text."
        )
        embedding: str = Field(
            default_factory=Embedding,
            description="Model used for generating text embeddings.",
        )
        cosine_threshold: float = Field(
            default=load_env("LIGHTRAG_COSINE_THRESHOLD", 0.3),
            description="Cosine similarity threshold for LightRAG.",
        )

        k: int = Field(
            default=60,
            description="Number of top items to retrieve. Represents entities in 'local' mode and relationships in 'global' mode.",
        )

        @model_validator(mode="after")
        def check(self):
            if self.graph_storage == LightRAGGraphStorageType.NEO4J:
                if importlib.util.find_spec("neo4j") is None:
                    raise ImportError(
                        "Neo4j can only be enabled on the online service, please execute `pip install aa-rag[online]`."
                    )
            return self

    type: EngineType = Field(
        default=EngineType.SimpleChunk,
        description="Type of index used for data retrieval.",
    )

    simple_chunk: SimpleChunk = Field(
        default_factory=SimpleChunk,
        description="Simple chunk index configuration settings.",
    )

    lightrag: LightRAG = Field(
        default_factory=LightRAG,
        description="LightRAG index configuration settings.",
    )


class Retrieve(BaseModel):
    class Weight(BaseModel):
        dense: float = Field(
            default=0.5, description="Weight for dense retrieval methods."
        )
        sparse: float = Field(
            default=0.5, description="Weight for sparse retrieval methods."
        )

    type: RetrieveType = Field(
        default=RetrieveType.HYBRID, description="Type of retrieval strategy used."
    )
    k: int = Field(default=3, description="Number of top results to retrieve.")
    weight: Weight = Field(
        default_factory=Weight, description="Weights for different retrieval methods."
    )


class OSS(BaseModel):
    access_key: Optional[str] = Field(
        default=load_env("OSS_ACCESS_KEY"),
        alias="OSS_ACCESS_KEY",
        description="Access key for accessing OSS services.",
    )

    endpoint: str = Field(
        default="https://s3.amazonaws.com",
        description="Endpoint for OSS API requests.",
    )
    secret_key: Optional[SecretStr] = Field(
        default=load_env("OSS_SECRET_KEY"),
        alias="OSS_SECRET_KEY",
        description="Secret key for accessing OSS services.",
        validate_default=True,
    )

    bucket: str = Field(default="aarag", description="Bucket name for storing data.")
    cache_bucket: str = Field(
        default=load_env("OSS_CACHE_BUCKET", "aarag-cache"),
        description="Bucket name for storing cache data.",
    )

    @model_validator(mode="after")
    def check(self):
        if self.access_key:
            if importlib.util.find_spec("boto3") is None:
                raise ImportError(
                    "OSS can only be enabled on the online service, please execute `pip install aa-rag[online]`."
                )
        return self


class Settings(BaseSettings):
    server: Server = Field(
        default_factory=Server, description="Server configuration settings."
    )
    openai: OpenAI = Field(
        default_factory=OpenAI, description="OpenAI API configuration settings."
    )

    storage: Storage = Field(
        default_factory=Storage, description="Database configuration settings."
    )
    embedding: Embedding = Field(
        default_factory=Embedding, description="Embedding model configuration settings."
    )
    engine: Engine = Field(
        default_factory=Engine, description="Indexing engine configuration settings."
    )
    llm: LLM = Field(
        default_factory=LLM,
        description="Language model configuration settings.",
    )

    oss: OSS = Field(default_factory=OSS, description="Minio configuration settings.")

    # 这里禁用了自动的 CLI 解析
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="_",
        extra="ignore",
    )


setting = Settings()
