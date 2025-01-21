# aa-rag

## Description
RAG Server for [AI2APPS](https://github.com/Avdpro/ai2apps). This server provides a Retrieval-Augmented Generation (RAG) API to support advanced AI applications. It leverages OpenAI's API for its core functionality.

---

## Requirements

**The current service supports only the OpenAI interface style**
1. **OpenAI API Key**:
   - Ensure your `.env` file includes the following line:
     ```
     OPENAI_API_KEY=<your_openai_api_key>
     ```

2. **Environment Setup**:
   - Make sure your environment is properly configured to load environment variables from a `.env` file.

---

## Installation

1. Install the package from PyPI:
   ```bash
   pip install aa-rag
   ```

2. Set up the `.env` file:
   - Create a `.env` file in the root directory of your project.
   - Add your OpenAI API key as described in the Requirements section.

---

## Usage

1. **Start the Web Server**:
   - Run the following command:
     ```bash
     aarag
     ```
   - if you want to change the port or host, you can use like this:
     ```bash
     aarag -server.host 127.0.0.1 --server.port 8788
     ```
   You can also run `aarag -h` to see the available options.
2. 

2. **Access the API Documentation**:
   - Once the server starts, open your browser and navigate to:
     ```
     http://localhost:222/docs
     ```
   - This page provides an interactive Swagger UI to explore and test all available APIs.
   - You can navigate to the `/default` endpoint to watch the default parameters and the available models.
---

## Features

- Fully supports OpenAI API integrations.
- Interactive API documentation using Swagger UI.
- Simplified RAG workflow for AI applications.

---

## GitHub

Find the source code and related projects on [GitHub](https://github.com/jarlor/aa_rag) and [AI2APPS](https://github.com/Avdpro/ai2apps).

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Support

For any issues or feature requests, please open a ticket in the [GitHub Issues](https://github.com/jarlor/aa_rag/issues).

---

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Submit a pull request.

---

