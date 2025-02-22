# Configuration Guide

This document describes all the available configuration options for the project. The settings are loaded from an environment file (.env) using pydantic-settings. For nested configuration sections, the keys follow the pattern:

section_fieldname

For example, to override the server host, use the key `SERVER_HOST`.

Some fields load their default values from environment variables directly using the custom `load_env` function. When not set, those defaults are applied.

Below is a detailed description of each configuration section and its available options.

---

## 1. Server Configuration

Settings for running the server.

- **host**  
  *Key:* `SERVER_HOST`  
  *Description:* The host address for the server.  
  *Default:* `"0.0.0.0"`

- **port**  
  *Key:* `SERVER_PORT`  
  *Description:* The port number on which the server listens.  
  *Default:* `222`

---

## 2. OpenAI Configuration

Settings for accessing OpenAI services. The API key and base URL can be set via environment variables.

- **api_key**  
  *Key:* `OPENAI_API_KEY`  
  *Description:* API key for accessing OpenAI services.  
  *Type:* Secret String (masked when printed)

- **base_url**  
  *Key:* `OPENAI_BASE_URL`  
  *Description:* Base URL for the OpenAI API requests.  
  *Default:* `"https://api.openai.com/v1"`

---

## 3. Database (DB) Configuration

The DB configuration contains settings for multiple database types. For nested settings, use the format `DB_<SUBSECTION>_<FIELD>`.

### 3.1. LanceDB Settings

- **uri**  
  *Key:* `DB_LANCEDB_URI`  
  *Description:* URI for the LanceDB database location.  
  *Default:* `"./db/lancedb"`

### 3.2. Milvus Settings

- **uri**  
  *Key:* `DB_MILVUS_URI`  
  *Description:* URI for the Milvus server location.  
  *Default:* `"./db/milvus.db"`

- **user**  
  *Key:* `DB_MILVUS_USER`  
  *Description:* Username for the Milvus server.  
  *Default:* `""` (empty string)

- **password**  
  *Key:* `DB_MILVUS_PASSWORD`  
  *Description:* Password for the Milvus server.  
  *Type:* Secret String

- **database**  
  *Key:* `DB_MILVUS_DATABASE`  
  *Description:* Database name for the Milvus server.  
  *Default:* `"aarag"`

### 3.3. TinyDB Settings

- **uri**  
  *Key:* `DB_TINYDB_URI`  
  *Description:* URI for the relational database location (TinyDB).  
  *Default:* `"./db/db.json"`

### 3.4. MongoDB Settings

- **uri**  
  *Key:* `DB_MONGODB_URI`  
  *Description:* URI for the MongoDB server location.  
  *Default:* `"mongodb://localhost:27017"`

- **user**  
  *Key:* `DB_MONGODB_USER`  
  *Description:* Username for the MongoDB server.  
  *Default:* `""` (empty string)

- **password**  
  *Key:* `DB_MONGODB_PASSWORD`  
  *Description:* Password for the MongoDB server.  
  *Type:* Secret String

- **database**  
  *Key:* `DB_MONGODB_DATABASE`  
  *Description:* Database name for the MongoDB server.  
  *Default:* `"aarag"`

### 3.5. General DB Options

- **mode**  
  *Key:* `DB_MODE`  
  *Description:* Mode of operation for the database. Expected values come from the DBMode enum (for example `UPSERT`).  
  *Default:* `UPSERT`

- **vector**  
  *Key:* `DB_VECTOR`  
  *Description:* Type of vector database used. Use one of the allowed enum values (e.g., `MILVUS`, `LANCE`).  
  *Default:* `MILVUS`  
  *Note:* If set to `LANCE`, the system checks if the `lancedb` package is installed.

- **nosql**  
  *Key:* `DB_NOSQL`  
  *Description:* Type of NoSQL database used. Use one of the allowed enum values (e.g., `TINYDB`, `MONGODB`).  
  *Default:* `TINYDB`  
  *Note:* If set to `MONGODB`, the system checks if the `pymongo` package is installed.

---

## 4. Embedding Configuration

Settings for the embedding model.

- **model**  
  *Key:* `EMBEDDING_MODEL`  
  *Description:* Model used for generating text embeddings.  
  *Default:* `"text-embedding-3-small"`

> Note: In the nested structure, the variable key becomes `EMBEDDING_MODEL`.

---

## 5. LLM Configuration

Settings for the language model used in the system.

- **model**  
  *Key:* `LLM_MODEL`  
  *Description:* Language model used for generating responses/embeddings.  
  *Default:* `"gpt-4o"`

---

## 6. Index Configuration

Settings for index creation and configuration.

- **type**  
  *Key:* `INDEX_TYPE`  
  *Description:* Type of index used for data retrieval. Use one of the values from the IndexType enum (for example, `CHUNK`).  
  *Default:* `CHUNK`

- **chunk_size**  
  *Key:* `INDEX_CHUNK_SIZE`  
  *Description:* Size of each chunk in the index.  
  *Default:* `512`

- **overlap_size**  
  *Key:* `INDEX_OVERLAP_SIZE`  
  *Description:* Overlap size between chunks in the index.  
  *Default:* `100`

> Note: The `chunk_size` and `overlap_size` are directly loaded via the custom `load_env` function; they may accept Python literal values.

---

## 7. Retrieve Configuration

Settings for the retrieval strategy of the system.

- **type**  
  *Key:* `RETRIEVE_TYPE`  
  *Description:* Type of retrieval strategy used. Use one of the values from the RetrieveType enum (e.g., `HYBRID`).  
  *Default:* `HYBRID`

- **k**  
  *Key:* `RETRIEVE_K`  
  *Description:* Number of top results to retrieve.  
  *Default:* `3`

### Weights for Retrieval Methods

The retrieval configuration includes a nested weight setting.

- **dense**  
  *Key:* `RETRIEVE_WEIGHT_DENSE`  
  *Description:* Weight for dense retrieval methods.  
  *Default:* `0.5`

- **sparse**  
  *Key:* `RETRIEVE_WEIGHT_SPARSE`  
  *Description:* Weight for sparse retrieval methods.  
  *Default:* `0.5`

- **only_page_content**  
  *Key:* `ONLY_PAGE_CONTENT`  
  *Description:* Flag to retrieve only page content; useful when you need just the text content without metadata.  
  *Default:* `False`  
  *Note:* This value is loaded using the `load_env` function.

---

## 8. OSS (Object Storage Service) Configuration

Settings for accessing object storage (e.g., Minio or AWS S3).

- **access_key**  
  *Key:* `OSS_ACCESS_KEY`  
  *Description:* Access key for accessing OSS services.  
  *Type:* Plain string (but consider this sensitive information)  
  *Note:* If provided, the system will check whether the `boto3` package is installed.

- **endpoint**  
  *Key:* `OSS_ENDPOINT`  
  *Description:* Endpoint for OSS API requests.  
  *Default:* `"https://s3.amazonaws.com"`

- **secret_key**  
  *Key:* `OSS_SECRET_KEY`  
  *Description:* Secret key for accessing OSS services.  
  *Type:* Secret String  
  *Note:* This key will be masked when printing configuration.

- **bucket**  
  *Key:* `OSS_BUCKET`  
  *Description:* Bucket name for storing data.  
  *Default:* `"aarag"`

- **cache_bucket**  
  *Key:* `OSS_CACHE_BUCKET`  
  *Description:* Bucket name for storing cache data.  
  *Default:* `"aarag-cache"`

---

## Complete .env Example

Below is a complete example of a .env file that shows how to set these configuration options:

```.dotenv
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=222

# OpenAI Configuration
OPENAI_API_KEY="your_openai_api_key_here"
OPENAI_BASE_URL="https://api.openai.com/v1"

# LanceDB Settings
DB_LANCEDB_URI=./db/lancedb

# Milvus Settings
DB_MILVUS_URI=./db/milvus.db
DB_MILVUS_USER="milvus_user"
DB_MILVUS_PASSWORD="milvus_password"
DB_MILVUS_DATABASE=aarag

# TinyDB Settings
DB_TINYDB_URI=./db/db.json

# MongoDB Settings
DB_MONGODB_URI="mongodb://localhost:27017"
DB_MONGODB_USER="mongodb_user"
DB_MONGODB_PASSWORD="mongodb_password"
DB_MONGODB_DATABASE=aarag

# General DB Options
DB_MODE=UPSERT
DB_VECTOR=MILVUS       # Options: MILVUS, LANCE, etc.
DB_NOSQL=TINYDB        # Options: TINYDB, MONGODB, etc.

# Embedding Configuration
EMBEDDING_MODEL=text-embedding-3-small

# LLM Configuration
LLM_MODEL=gpt-4o

# Index Configuration
INDEX_TYPE=CHUNK       # Use value from the IndexType enum
INDEX_CHUNK_SIZE=512
INDEX_OVERLAP_SIZE=100

# Retrieve Configuration
RETRIEVE_TYPE=HYBRID    # Use value from the RetrieveType enum
RETRIEVE_K=3
RETRIEVE_WEIGHT_DENSE=0.5
RETRIEVE_WEIGHT_SPARSE=0.5
ONLY_PAGE_CONTENT=False

# OSS (Object Storage) Configuration
OSS_ACCESS_KEY="your_oss_access_key"
OSS_ENDPOINT=https://s3.amazonaws.com
OSS_SECRET_KEY="your_oss_secret_key"
OSS_BUCKET=aarag
OSS_CACHE_BUCKET=aarag-cache
```