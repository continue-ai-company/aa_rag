# Configuration Parameters for aa-rag

This document explains in detail how to configure the aa-rag project using environment variables and a `.env` file.
The project is configured with [pydantic-settings](https://docs.pydantic.dev/latest/api/pydantic_settings/), using the nested delimiter `_` to handle nested configurations.

## How Settings Are Loaded

- **Environment & .env File:**  
  Settings are loaded from a `.env` file located in the project root as well as from system environment variables. The
  loading rules are as follows:
  - The system environment variable takes precedence if the same key is defined both in the `.env` file and in the
    environment.
  - The configuration class specifies:
    - `env_file=".env"` — the name of the dotenv file.
    - `env_nested_delimiter="_"` — nested model fields are joined using underscores.

- **Helper Function `load_env`:**  
  Some default values are set using the helper function `load_env(key, default)`, which uses `ast.literal_eval` to
  convert string values (such as numbers or booleans) into their proper Python types.

## Configuration Structure

The configuration is organized into several nested models as detailed below:

### 1. Server

- **host**:  
  - *Type*: `str`  
  - *Default*: `"0.0.0.0"`  
  - *Description*: The host address on which the server listens.
  
- **port**:  
  - *Type*: `int`  
  - *Default*: `222`  
  - *Description*: The port number on which the server listens.

*Environment variables*:  
`SERVER_HOST`, `SERVER_PORT`

---

### 2. OpenAI

- **api_key**:  
  - *Type*: `str`  
  - *Default*: Loaded from `OPENAI_API_KEY` (via `load_env("OPENAI_API_KEY")`)  
  - *Description*: API key for accessing OpenAI services.
  - **Required**.

- **base_url**:  
  - *Type*: `str`  
  - *Default*: Loaded from `OPENAI_BASE_URL`, or defaults to `"https://api.openai.com/v1"` if not provided
  - *Description*: The base URL for OpenAI API requests.

*Environment variables*:  
`OPENAI_API_KEY`, `OPENAI_BASE_URL`

---

### 3. DB

This module contains two sub-models:

#### a. Vector

- **uri**:  
  - *Type*: `str`  
  - *Default*: `"./db/lancedb"`  
  - *Description*: The URI for the vector database.
  
- **mode**:  
  - *Type*: `DBMode` (an enum with options: `INSERT`, `OVERWRITE`, or `UPSERT`)
  - *Default*: `DBMode.UPSERT`  
  - *Description*: The operational mode for the database.

*Environment variables*:  
`DB_VECTOR_URI`, `DB_VECTOR_MODE`

#### b. NoSQL

- **uri**:  
  - *Type*: `str`  
  - *Default*: `"./db/db.json"`  
  - *Description*: The URI for the document (NoSQL) database.
  
- **mode**:  
  - *Type*: `DBMode` (an enum with options: `INSERT`, `OVERWRITE`, or `UPSERT`)
  - *Default*: `DBMode.UPSERT`  
  - *Description*: The operational mode for the database.

*Environment variables*:  
`DB_NOSQL_URI`, `DB_NOSQL_MODE`

*Top-level key*: `db`

*Additional Option*:  
To specify the type of NoSQL database, you can use `NoSQLDBType` with options `TINYDB` (represented as `"tinydb"`) and
`MONGODB` (represented as `"mongodb"`). Check the project documentation for further details.

---

### 4. Embedding

- **model**:  
  - *Type*: `str`
  - *Default*: `"text-embedding-3-small"`
  - *Description*: The model used for generating text embeddings.

*Environment variable*:  
`EMBEDDING_MODEL`

---

### 5. Index

- **type**:  
  - *Type*: `IndexType` (an enum with the option: `CHUNK`, represented as `"chunk"`)
  - *Default*: `IndexType.CHUNK`  
  - *Description*: The type of index used for data retrieval.
  
- **chunk_size**:  
  - *Type*: `int`  
  - *Default*: Loaded via `load_env("INDEX_CHUNK_SIZE", 512)` (default: `512`)
  - *Description*: The size of each chunk in the index.
  
- **overlap_size**:  
  - *Type*: `int`  
  - *Default*: Loaded via `load_env("INDEX_OVERLAP_SIZE", 100)` (default: `100`)
  - *Description*: The overlap size between chunks in the index.

*Environment variables*:  
`INDEX_TYPE`, `INDEX_CHUNK_SIZE`, `INDEX_OVERLAP_SIZE`

---

### 6. Retrieve

This module contains a nested **Weight** model:

#### a. Weight

- **dense**:  
  - *Type*: `float`  
  - *Default*: `0.5`  
  - *Description*: Weight for dense retrieval methods.
  
- **sparse**:  
  - *Type*: `float`  
  - *Default*: `0.5`  
  - *Description*: Weight for sparse retrieval methods.

#### b. Retrieve (top-level)

- **type**:  
  - *Type*: `RetrieveType` (an enum with options: `HYBRID` (represented as `"hybrid"`), `DENSE` (represented as
    `"dense"`), and `BM25` (represented as `"bm25"`))
  - *Default*: `RetrieveType.HYBRID`  
  - *Description*: The retrieval strategy type.
  
- **k**:  
  - *Type*: `int`  
  - *Default*: `3`  
  - *Description*: The number of top results to retrieve.
  
- **only_page_content**:  
  - *Type*: `bool`  
  - *Default*: Loaded via `load_env("RETRIEVE_ONLY_PAGE_CONTENT", False)` (default: `False`)
  - *Description*: Whether to retrieve only the page content.

*Environment variables*:  
`RETRIEVE_TYPE`, `RETRIEVE_K`, `RETRIEVE_ONLY_PAGE_CONTENT`  
For weights: `RETRIEVE_WEIGHT_DENSE`, `RETRIEVE_WEIGHT_SPARSE`

---

### 7. Language Model (llm)

- **model**:  
  - *Type*: `str`
  - *Default*: `"gpt-4o"`
  - *Description*: The language model configuration for generating text.

*Environment variable*:  
`LLM_MODEL`

---

## Sample .env File

Below is an example of how your `.env` file might be structured. Environment variable names are uppercase, and nested
configuration keys are separated by underscores:

```dotenv
# Required: OpenAI configuration
OPENAI_API_KEY=<your_openai_api_key_here>
OPENAI_BASE_URL=https://api.openai.com/v1

# Server configuration (optional; defaults are shown)
SERVER_HOST=127.0.0.1
SERVER_PORT=222

# Database configuration
DB_VECTOR_URI=./db/lancedb
DB_VECTOR_MODE="UPSERT"
DB_NOSQL_URI=./db/db.json
DB_NOSQL_MODE="UPSERT"

# Embedding model configuration
EMBEDDING_MODEL="text-embedding-3-small"

# Index configuration
INDEX_TYPE="CHUNK"
INDEX_CHUNK_SIZE=512
INDEX_OVERLAP_SIZE=100

# Retrieval configuration
RETRIEVE_TYPE="HYBRID"
RETRIEVE_K=3
RETRIEVE_WEIGHT_DENSE=0.5
RETRIEVE_WEIGHT_SPARSE=0.5
RETRIEVE_ONLY_PAGE_CONTENT=False

# Language model configuration
LLM_MODEL="gpt-4o"
```