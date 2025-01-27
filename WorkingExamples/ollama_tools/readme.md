# TOOLS Library

A Python library for integrating function calling capabilities with Ollama LLMs. This is a subproject within the OllamaPlayground repository.

## Installation

### Prerequisites
- Python 3.8 or higher
- Ollama installed and running on your system ([Ollama installation guide](https://ollama.ai/download))

### Clone and Setup

```bash
# Clone the full OllamaPlayground repository
git clone git@github.com:iplayfast/OllamaPlayground.git

# Navigate to the ollama_tools directory
cd OllamaPlayground/WorkingExamples/ollama_tools

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install the package in editable mode
pip install -e .
```

## Model Configuration

The library determines which Ollama model to use in the following order of precedence:

1. Local `config.json` file in the current directory
2. `config.json` file in the parent directory
3. `OLLAMA_MODEL` environment variable
4. Defaults to 'llama3.2'

### Using config.json

Create a `config.json` file in your working directory:
```json
{
    "model": "granite3.1-moe"
}
```

### Using Environment Variable
```bash
export OLLAMA_MODEL=granite3.1-moe
```

### Recommended Models
The following models are known to work well with function calling:
- granite3.1-moe (recommended)
- llama3.2
- llama2

## Project Structure
```
WorkingExamples/ollama_tools/
├── doc/                   # Documentation
│   └── tools_explanation.md
├── examples/             # Example implementations
│   ├── code_executor/    # Code execution examples
│   │   ├── code_executor_example.py
│   │   └── code_management_examples.py
│   ├── pathfinding/      # Pathfinding implementation
│   │   ├── landmarks.py
│   │   ├── map.txt
│   │   └── pathfinding_example.py
│   └── tools_examples.py # General usage examples
├── lib/                  # Core library utilities
└── ollama_tools/         # Main package
```

## Running Examples

### Basic Tools Usage
```bash
cd OllamaPlayground/WorkingExamples/ollama_tools/examples
# Ensure config.json is present or set OLLAMA_MODEL
python tools_examples.py
```

### Basic Example

```python
from ollama_tools import TOOLSEngine
from pathlib import Path
import json
import os

def get_model_name():
    """Get configured model name"""
    config_file = Path.cwd() / 'config.json'
    if config_file.exists():
        with open(config_file) as f:
            return json.load(f)['model']
    return os.environ.get('OLLAMA_MODEL', 'llama3.2')

def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

# Initialize engine with configured model
engine = TOOLSEngine(get_model_name())
engine.add_tool(add_numbers)
response, tool_calls = engine.chat("What is 5 plus 3?")
print(response)
```

## Examples

The `examples` directory contains several implementations:
- `tools_examples.py`: Various function calling examples including:
  - Compound interest calculations
  - Password validation
  - Temperature conversion
  - Text analysis
  - Mortgage calculations
- `pathfinding_example.py`: A* pathfinding implementation
- Code execution examples in the `code_executor` directory

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
