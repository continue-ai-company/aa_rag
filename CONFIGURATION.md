# aa-rag Configuration Manual

This project uses [pydantic-settings](https://docs.pydantic.dev/latest/api/pydantic_settings/) for configuration management, supporting both `.env` files and environment variables.

## Configuration Loading Rules
- Uses `.env` file at project root and environment variables
- Environment variables take precedence over `.env` file
- Nested configuration keys use `_` separator (e.g., `DB_MILVUS_URI`)

## Configuration Structure

### 1. Server Configuration
- **host**  
  - Type: `str`  
  - Default: `"0.0.0.0"`  
  - Env Var: `SERVER_HOST`  
  - Description: Service binding address

- **port**  
  - Type: `int`  
  - Default: `222`  
  - Env Var: `SERVER_PORT`  
  - Description: Service listening port

### 2. OpenAI Configuration
- **api_key**  
  - Type: `str`  
  - Required  
  - Env Var: `OPENAI_API_KEY`  
  - Description: OpenAI API key

### 3. Database Configuration (DB)
#### Vector Databases
- **LanceDB**
  - uri: `str` (Default: `./db/lancedb`, Env Var: `DB_LANCEDB_URI`)
- **Milvus**  
  - uri: `str` (Default: `./db/milvus.db`, Env Var: `DB_MILVUS_URI`)
  - user: `str` (Default: "")
  - password: `SecretStr` (Default: "")
  - database: `str` (Default: "default")

#### NoSQL Databases
- **TinyDB**
  - uri: `str` (Default: `./db/db.json`, Env Var: `DB_TINYDB_URI`)
- **MongoDB**  
  - uri: `str` (Default: `mongodb://localhost:27017`, Env Var: `DB_MONGODB_URI`)
  - database: `str` (Default: "aarag")

### 4. Retrieval Configuration
- **type**: `RetrieveType` (HYBRID/DENSE/BM25)
- **k**: `int` (Default: 3)
- **weights**:
  - dense: `float` (Default: 0.5)
  - sparse: `float` (Default: 0.5)
- **only_page_content**: `bool` (Default: False)

Env Vars:  
`RETRIEVE_TYPE`, `RETRIEVE_K`,  
`RETRIEVE_WEIGHT_DENSE`, `RETRIEVE_WEIGHT_SPARSE`,  
`RETRIEVE_ONLY_PAGE_CONTENT`

### 5. Language Model (LLM)
- **model**  
  - Type: `str`  
  - Default: `"gpt-4o"`  
  - Env Var: `LLM_MODEL`

---

## Sample .env File
```dotenv
# Required
OPENAI_API_KEY=your_api_key_here

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=222

# Databases
DB_LANCEDB_URI=./db/lancedb
DB_MILVUS_URI=./db/milvus.db
DB_MONGODB_URI=mongodb://localhost:27017

# Retrieval
RETRIEVE_TYPE=HYBRID
RETRIEVE_K=3
RETRIEVE_WEIGHT_DENSE=0.5
RETRIEVE_WEIGHT_SPARSE=0.5

# Models
LLM_MODEL=gpt-4o
```