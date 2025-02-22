import ast
import importlib
import os
from pathlib import Path
from typing import Optional

import dotenv
from pydantic import BaseModel, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from aa_rag.gtypes.enums import (
    IndexType,
    DBMode,
    RetrieveType,
    VectorDBType,
    NoSQLDBType,
)

dotenv.load_dotenv(Path(".env").absolute())


def load_env(key: str, default=None):
    """
    Load environment variable from .env file. Convert to python object if possible.
    Args:
        key: Environment variable key.
        default: Default value if key not found.
    Returns:
        Python object.
    """

    value = os.getenv(key, default)
    try:
        return ast.literal_eval(value)
    except Exception:
        return value


class Server(BaseModel):
    host: str = Field(default="0.0.0.0", description="The host address for the server.")
    port: int = Field(
        default=222, description="The port number on which the server listens."
    )


class OpenAI(BaseModel):
    api_key: SecretStr = Field(
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

    @field_validator("api_key")
    def check_api_key(cls, v):
        assert v.get_secret_value(), "API key is required."
        return v


class DB(BaseModel):
    class LanceDB(BaseModel):
        uri: str = Field(
            default="./db/lancedb", description="URI for lanceDB database location."
        )

    class Milvus(BaseModel):
        uri: str = Field(
            default="./db/milvus.db",
            description="URI for the Milvus server location.",
        )
        user: str = Field(default="", description="Username for the Milvus server.")
        password: SecretStr = Field(
            default="",
            description="Password for the Milvus server.",
            validate_default=True,
        )
        database: str = Field(
            default="aarag", description="Database name for the Milvus server."
        )

    class TinyDB(BaseModel):
        uri: str = Field(
            default="./db/db.json",
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
        database: str = Field(
            default="aarag", description="Database name for the MongoDB server."
        )

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

    mode: DBMode = Field(
        default=DBMode.UPSERT, description="Mode of operation for the database."
    )
    vector: VectorDBType = Field(
        default=VectorDBType.MILVUS, description="Type of vector database used."
    )
    nosql: NoSQLDBType = Field(
        default=NoSQLDBType.TINYDB, description="Type of NoSQL database used."
    )

    @field_validator("vector")
    def check_vector_db(cls, v):
        if v == VectorDBType.LANCE:
            # check whether install lancedb package
            if importlib.util.find_spec("lancedb") is None:
                raise ImportError(
                    "LanceDB can only be enabled on the online service, please execute `pip install aa-rag[online]`."
                )
        return v

    @field_validator("nosql")
    def check_nosql_db(cls, v):
        if v == NoSQLDBType.MONGODB:
            # check whether install pymongo package
            if importlib.util.find_spec("pymongo") is None:
                raise ImportError(
                    "MongoDB can only be enabled on the online service, please execute `pip install aa-rag[online]`."
                )
        return v


class Embedding(BaseModel):
    model: str = Field(
        default="text-embedding-3-small",
        description="Model used for generating text embeddings.",
    )


class LLM(BaseModel):
    model: str = Field(
        default="gpt-4o",
        description="Model used for generating text embeddings.",
    )


class Index(BaseModel):
    type: IndexType = Field(
        default=IndexType.CHUNK, description="Type of index used for data retrieval."
    )
    chunk_size: int = Field(
        default=load_env("INDEX_CHUNK_SIZE", 512),
        description="Size of each chunk in the index.",
    )
    overlap_size: int = Field(
        default=load_env("INDEX_OVERLAP_SIZE", 100),
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

    type: RetrieveType = Field(
        default=RetrieveType.HYBRID, description="Type of retrieval strategy used."
    )
    k: int = Field(default=3, description="Number of top results to retrieve.")
    weight: Weight = Field(
        default_factory=Weight, description="Weights for different retrieval methods."
    )
    only_page_content: bool = Field(
        default=load_env("ONLY_PAGE_CONTENT", False),
        alias="ONLY_PAGE_CONTENT",
        description="Flag to retrieve only page content.",
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

    @field_validator("access_key")
    def check_access_key(cls, v):
        if v:
            if importlib.util.find_spec("boto3") is None:
                raise ImportError(
                    "OSS can only be enabled on the online service, please execute `pip install aa-rag[online]`."
                )
        return v


class Settings(BaseSettings):
    server: Server = Field(
        default_factory=Server, description="Server configuration settings."
    )
    openai: OpenAI = Field(
        default_factory=OpenAI, description="OpenAI API configuration settings."
    )

    db: DB = Field(default_factory=DB, description="Database configuration settings.")
    embedding: Embedding = Field(
        default_factory=Embedding, description="Embedding model configuration settings."
    )
    index: Index = Field(
        default_factory=Index, description="Index configuration settings."
    )
    retrieve: Retrieve = Field(
        default_factory=Retrieve,
        description="Retrieval strategy configuration settings.",
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
