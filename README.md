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

You can choose one of the following installation methods: **uv** (recommended) or **requirements.txt**.

#### Option 1: UV Installation (Recommended)

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

#### Option 2: Installation via requirements.txt

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/continue-ai-company/aa_rag.git
   cd aa_rag
   ```

2. **Environment Setup:**
    - You can use your existing Python environment or create a new one, based on your preference.

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
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
    >  You can set command-line arguments to change the server configuration if you use `aarag` to startup. `aarag -h` will show you the available options. 

    - If you installed the package from source code and are using the `requirements.txt` file, you can run the server using the following command:
      ```bash
        source ./.venv/bin/activate
        export PYTHONPATH=$(pwd)/src # Set the PYTHONPATH to the src directory
        python -m aa_rag.main
        ```

2. **Access the API Documentation:**
    - Open your browser and navigate to:
     ```
     http://localhost:222/docs
     ```
   - This page provides an interactive Swagger UI to explore and test all available APIs.

---

## Features

- Full support for OpenAI API integrations.
- Interactive API documentation using Swagger UI.
- Simplified RAG workflow for AI applications.

---

## GitHub

Find the source code and related projects on [GitHub](https://github.com/continue-ai-company/aa_rag)
and [AI2APPS](https://github.com/Avdpro/ai2apps).

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Support

For any issues or feature requests, please open a ticket in
the [GitHub Issues](https://github.com/continue-ai-company/aa_rag/issues).

---

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Submit a pull request.