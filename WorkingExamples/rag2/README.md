# Ollama RAG Engine

A Retrieval-Augmented Generation (RAG) engine that combines document retrieval with Large Language Model responses using Ollama and ChromaDB. This project enables efficient querying of documents using semantic search and generates context-aware responses using local LLMs.

## Features

- Document indexing and semantic search using ChromaDB
- Local LLM integration through Ollama
- FastAPI-based REST API for easy integration
- Configurable embedding and response models
- Automatic fallback to CPU when GPU is unavailable

## Prerequisites

- Python 3.12 or higher
- [Ollama](https://ollama.ai/) installed and running locally
- Required models pulled in Ollama:
  - An embedding model (default: nomic-embed-text:latest)
  - A response model (default: llama3.2:latest)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the package and its dependencies:
```bash
pip install -e .
```

## Configuration

The default configuration is stored in `rag_ollama/config.json`. You can modify this file to use different models:

```json
{
  "embedding_model": "nomic-embed-text:latest",
  "response_model": "llama3.2:latest"
}
```

## Usage

### As a Python Package

```python
from rag_ollama import RAGEngine

# Initialize the RAG engine
rag = RAGEngine()

# Index your documents
rag.load_and_index_documents("path/to/your/documents.txt")

# Query the system
response = rag.query("Your question here")
print(response['result'])
```

### Using the API

1. Start the API server:
```bash
python run_api.py
```

2. The API will be available at `http://localhost:8000` with the following endpoints:

- POST `/init`: Initialize the RAG engine
- POST `/index`: Index documents
- POST `/query`: Query the system

Example API usage:

```bash
# Initialize the engine
curl -X POST http://localhost:8000/init -H "Content-Type: application/json" -d '{
    "embedding_model": "nomic-embed-text:latest",
    "response_model": "llama3.2:latest"
}'

# Index documents
curl -X POST http://localhost:8000/index -H "Content-Type: application/json" -d '{
    "documents_path": "path/to/your/documents.txt"
}'

# Query the system
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{
    "prompt": "Your question here",
    "system_prompt": "Optional system prompt"
}'
```

## Running Tests

Execute the test suite using:
```bash
./runtests.sh
```

## Project Structure

```
.
├── game_lore.txt               # Example document for testing
├── rag_ollama/                # Main package directory
│   ├── api.py                 # FastAPI implementation
│   ├── config.json            # Configuration file
│   ├── rag_engine.py         # Core RAG implementation
│   └── __init__.py           # Package initialization
├── tests/                     # Test directory
│   └── test_rag_engine.py    # Test cases
├── run_api.py                # API runner script
├── rag_usage_example.py      # Usage example script
└── setup.py                  # Package setup file
```

## License

[Add your license information here]

## Contributing

[Add contribution guidelines if applicable]
