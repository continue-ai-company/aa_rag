# aa-rag

## Description

RAG Server for [AI2APPS](https://github.com/Avdpro/ai2apps). This server provides a Retrieval-Augmented Generation (RAG)
API to support advanced AI applications.

---

## Requirements

1. **OpenAI API Key:**
    - The service supports only the OpenAI interface style.
   - Ensure your `.env` file includes the following line:
     ```
     OPENAI_API_KEY=<your_openai_api_key>
     ```

2. **Environment Setup:**
   - Make sure your environment is properly configured to load environment variables from a `.env` file.
   - For complete details on how to configure the application using environment variables and a `.env` file, please see
     the [Configuration Parameters](CONFIGURATION.md) document.

---

## Installation

### Installation via PyPI

Install the package from PyPI:

```bash
pip install aa-rag
```


### Installation via Source Code

The project build via the `uv` tool. To install the project from source code, follow these steps:

1. **Install uv:**
    - On macOS, it is recommended to use Homebrew:
      ```bash
      brew install uv
      ```
    - For other operating systems, please refer to
      the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/#pypi).

2. **Clone the Repository:**
   ```bash
   git clone https://github.com/continue-ai-company/aa_rag.git
   cd aa_rag
   ```

3. **Synchronize Dependencies:**
    - Install dependencies as specified in the `uv.lock` file:
      ```bash
      uv sync
      ```
    - This command will create the virtual environment in the current project directory and install all necessary
      dependencies.


### Optional
If you want to install the package with the `online` extra, you can use the following command:
```bash
pip install "aa-rag[online]" # install package with pip
uv sync --extras online # install package with uv
```

---

## Usage

1. **Start the Web Server:**
    - If you installed the package via PyPI, you can run the server using the following command:
      ```bash
      aarag
      ``` 
    - If you installed the package from source code and are using the `uv` tool, you can run the server using the following command:
      ```bash
      uv run aarag
      ```
      
2. **Access the API Documentation:**
    - Open your browser and navigate to:
     ```
     http://localhost:222/docs
     ```
   - This page provides an interactive Swagger UI to explore and test all available APIs.

---