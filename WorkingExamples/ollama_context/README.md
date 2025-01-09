# Ollama Context Engine

A unified context-enhanced generation engine that combines Retrieval-Augmented Generation (RAG) and Context-Augmented Generation (CAG) capabilities using Ollama. This project enables both document-based retrieval and template-based context generation for rich, contextually-aware responses.

## Overview

The Context Engine combines three powerful approaches to LLM-based generation:

### RAG (Retrieval-Augmented Generation)
- Finds and uses relevant information from document collections
- Enables semantic search and document retrieval
- Perfect for knowledge-based queries
- Ideal for handling factual information and domain-specific knowledge

### CAG (Context-Augmented Generation)
- Dynamically injects structured, templated context into prompts
- Maintains consistent character personas or response formats
- Excellent for formatted outputs and consistent voice
- Specialized in template-based, structured responses

### Combined Context-Enhanced Generation
- Merges both RAG and CAG capabilities
- Can retrieve relevant documents AND maintain consistent context
- Perfect for complex scenarios requiring both knowledge and structure
- Automatically chooses the best approach based on the query

## Key Use Cases

### RAG Scenarios
- Question answering from documentation
- Knowledge base queries
- Research assistance
- Technical support
- Educational content delivery

### CAG Scenarios
- Character-based interactions
- Consistent persona maintenance
- Template-based responses
- Structured data extraction
- Format-specific generation

### Combined Scenarios
- Interactive storytelling with factual backgrounds
- Technical documentation with consistent voice
- Customer service with knowledge base integration
- Educational systems with adaptive content
- Games with rich lore and consistent characters

## Features

- Flexible operation modes:
  - `retrieval`: Traditional RAG with document search
  - `context`: Template-based CAG
  - `combined`: Unified RAG+CAG
  - `auto`: Intelligently selects the appropriate mode
- Document processing:
  - Semantic search using ChromaDB
  - Automatic chunking and indexing
  - Metadata filtering
- Context management:
  - Dynamic template system
  - Variable substitution
  - Context updating
- Response generation:
  - Free-form responses
  - Structured outputs using Pydantic models
  - Combined context-aware responses
- Technical features:
  - FastAPI-based REST API
  - Async/sync support
  - Automatic model fallback
  - GPU/CPU flexibility
  - Configurable logging

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

3. Install the package:
```bash
pip install -e .
```

## Configuration

The default configuration is stored in `ollama_context/config.json`:

```json
{
  "embedding_model": "nomic-embed-text:latest",
  "response_model": "llama3.2:latest"
}
```

## Usage Examples

### Basic Usage

```python
from ollama_context import ContextEngine

# Initialize the engine
engine = ContextEngine(mode="auto", database="local_db")

# Index some documents
engine.load_and_index_documents(
    "documents.txt",
    metadatas=[{"section": "lore"}]
)

# Register a context template
character_template = """
Character Name: {name}
Role: {role}
Background: {background}
"""

variables = {
    "name": "Eldric",
    "role": "Wizard",
    "background": "200 years of study"
}

engine.register_context("wizard", character_template, variables)

# Make different types of queries
# RAG query
lore_response = engine.query(
    prompt="Tell me about the kingdom's history",
    where={"section": "lore"}
)

# CAG query
character_response = engine.query(
    prompt="What do you think about magic?",
    context_name="wizard"
)

# Combined query
combined_response = engine.query(
    prompt="What do you know about the ancient wars?",
    context_name="wizard",
    where={"section": "lore"},
    mode="combined"
)
```

### Structured Output

```python
from pydantic import BaseModel
from typing import List

class Character(BaseModel):
    name: str
    role: str
    personality: str
    key_traits: List[str]

character_info = engine.query_structured(
    prompt="Tell me about yourself",
    response_model=Character,
    context_name="wizard"
)
```

### Using the API

1. Start the API server:
```bash
python run_api.py
```

2. Initialize the engine:
```python
import requests

response = requests.post(
    "http://localhost:8000/init",
    json={
        "mode": "auto",
        "database": "api_db"
    }
)
```

3. Index documents:
```python
response = requests.post(
    "http://localhost:8000/index",
    json={
        "documents_path": "documents.txt",
        "metadatas": [{"section": "lore"}]
    }
)
```

4. Register a context:
```python
response = requests.post(
    "http://localhost:8000/context/register",
    json={
        "name": "wizard",
        "template": "Name: {name}\nRole: {role}",
        "variables": {
            "name": "Eldric",
            "role": "Wizard"
        }
    }
)
```

5. Make queries:
```python
# RAG query
response = requests.post(
    "http://localhost:8000/query",
    json={
        "prompt": "Tell me about the history",
        "where": {"section": "lore"}
    }
)

# CAG query
response = requests.post(
    "http://localhost:8000/query",
    json={
        "prompt": "What do you think?",
        "context_name": "wizard"
    }
)

# Combined query
response = requests.post(
    "http://localhost:8000/query",
    json={
        "prompt": "What do you know about this?",
        "context_name": "wizard",
        "where": {"section": "lore"},
        "mode": "combined"
    }
)
```

## API Endpoints

- POST `/init`: Initialize the engine
- GET `/status`: Check engine status
- POST `/index`: Index documents
- POST `/context/register`: Register a context template
- POST `/context/update`: Update context variables
- POST `/query`: Generate responses
- POST `/query/structured`: Generate structured responses

## Project Structure

```
ollama_context/
├── examples/
│   ├── basic_usage_example.py
│   ├── api_usage_example.py
│   └── structured_query_example.py
├── ollama_context/
│   ├── __init__.py
│   ├── api.py
│   ├── config.json
│   └── engine.py
├── tests/
│   └── test_engine.py
├── README.md
├── requirements.txt
├── run_api.py
└── setup.py
```

## Advanced Usage

### Metadata Filtering
```python
# Filter by section
response = engine.query(
    prompt="Query",
    where={"section": "specific_section"}
)

# Complex filters
response = engine.query(
    prompt="Query",
    where={"$and": [
        {"section": "lore"},
        {"type": "history"}
    ]}
)
```

### Custom System Prompts
```python
response = engine.query(
    prompt="Query",
    context_name="wizard",
    system_prompt="Respond as a wise and ancient being"
)
```

### Model Options
```python
response = engine.query(
    prompt="Query",
    context_name="wizard",
    options={
        "temperature": 0.7,
        "top_p": 0.9
    }
)
```

## Running Tests

Execute the test suite:
```bash
./runtests.sh
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details
