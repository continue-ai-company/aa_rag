# Configuration Parameters for aa-rag

This document explains in detail how to configure the aa-rag project using environment variables and a `.env` file. The project uses [pydantic-settings](https://docs.pydantic.dev/latest/api/pydantic_settings/) with CLI parsing enabled (via `cli_parse_args=True`) and a nested delimiter of `_` to manage its configuration.

## How Settings Are Loaded

- **Environment & .env File:**  
  The settings are loaded from a `.env` file (located in the project root) and from system environment variables. The settings class is configured with:
  - `env_file=".env"` — the dotenv file name.
  - `env_nested_delimiter="_"` — nested model fields are combined with underscores.
  
  If the same key is defined as a system environment variable and in the `.env` file, the system variable takes precedence.

- **Helper Function `load_env`:**  
  Some default values are set using a helper function `load_env(key, default)` that uses `ast.literal_eval` to convert string values (such as numbers or booleans) into their proper Python types.

## Settings Structure

The configuration is organized into several nested models:

### 1. Server

- **host**:  
  - *Type*: `str`  
  - *Default*: `"0.0.0.0"`  
  - *Description*: The host address for the server.
  
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
  - *Default*: Loaded from `OPENAI_BASE_URL` with a fallback to `"https://api.openai.com/v1"`  
  - *Description*: Base URL for OpenAI API requests.

*Environment variables*:  
`OPENAI_API_KEY`, `OPENAI_BASE_URL`

---

### 3. DB

This model contains two sub-models:

#### a. Vector

- **uri**:  
  - *Type*: `str`  
  - *Default*: `"./db/lancedb"`  
  - *Description*: URI for the vector database location.
  
- **mode**:  
  - *Type*: `DBMode` (an enum)  
  - *Default*: `DBMode.UPSERT`  
  - *Description*: Mode of operation for the database.

*Environment variables*:  
`DB_VECTOR_URI`, `DB_VECTOR_MODE`

#### b. NoSQL

- **uri**:  
  - *Type*: `str`  
  - *Default*: `"./db/db.json"`  
  - *Description*: URI for the document (NoSQL) database location.
  
- **mode**:  
  - *Type*: `DBMode`  
  - *Default*: `DBMode.UPSERT`  
  - *Description*: Mode of operation for the database.

*Environment variables*:  
`DB_NOSQL_URI`, `DB_NOSQL_MODE`

*Top-level key*: `db`

---

### 4. Embedding

- **model**:  
  - *Type*: `EmbeddingModel` (an enum)  
  - *Default*: `EmbeddingModel.TEXT_EMBEDDING_3_SMALL`  
  - *Description*: Model used for generating text embeddings.

*Environment variable*:  
`EMBEDDING_MODEL`

---

### 5. Index

- **type**:  
  - *Type*: `IndexType` (an enum)  
  - *Default*: `IndexType.CHUNK`  
  - *Description*: Type of index used for data retrieval.
  
- **chunk_size**:  
  - *Type*: `int`  
  - *Default*: Loaded from `INDEX_CHUNK_SIZE` (default value: `512`)
  - *Description*: Size of each chunk in the index.
  
- **overlap_size**:  
  - *Type*: `int`  
  - *Default*: Loaded from `INDEX_OVERLAP_SIZE` (default value: `100`)
  - *Description*: Overlap size between chunks in the index.

*Environment variables*:  
`INDEX_TYPE`, `INDEX_CHUNK_SIZE`, `INDEX_OVERLAP_SIZE`

---

### 6. Retrieve

Contains a nested **Weight** model:

#### a. Weight

- **dense**:  
  - *Type*: `float`  
  - *Default*: `0.5`  
  - *Description*: Weight for dense retrieval methods.
  
- **sparse**:  
  - *Type*: `float`  
  - *Default*: `0.5`  
  - *Description*: Weight for sparse retrieval methods.

#### b. Retrieve (top level)

- **type**:  
  - *Type*: `RetrieveType` (an enum)  
  - *Default*: `RetrieveType.HYBRID`  
  - *Description*: Type of retrieval strategy used.
  
- **k**:  
  - *Type*: `int`  
  - *Default*: `3`  
  - *Description*: Number of top results to retrieve.
  
- **only_page_content**:  
  - *Type*: `bool`  
  - *Default*: Loaded from `ONLY_PAGE_CONTENT` (default: `False`)
  - *Description*: Flag to retrieve only page content.

*Environment variables*:  
`RETRIEVE_TYPE`, `RETRIEVE_K`, `RETRIEVE_ONLY_PAGE_CONTENT`  
For weights: `RETRIEVE_WEIGHT_DENSE`, `RETRIEVE_WEIGHT_SPARSE`

---

### 7. Language Model (llm)

- **model**:  
  - *Type*: `LLModel` (an enum)  
  - *Default*: `LLModel.GPT_4O`  
  - *Description*: Language model configuration used for generating text.

*Environment variable*:  
`LLM_MODEL`

---

## Sample .env File

Below is an example of how your `.env` file might be structured. Environment variable names are uppercase and nested keys use underscores:

```dotenv
# Required: OpenAI configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# Server configuration (optional; defaults shown)
SERVER_HOST=127.0.0.1
SERVER_PORT=222

# Database configuration
DB_VECTOR_URI=./db/lancedb
DB_VECTOR_MODE="UPSERT"
DB_NOSQL_URI=./db/db.json
DB_NOSQL_MODE="UPSERT"

# Embedding model configuration
EMBEDDING_MODEL="TEXT_EMBEDDING_3_SMALL"

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
LLM_MODEL="GPT_4O"
