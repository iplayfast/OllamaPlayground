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
│   ├── debugprint.py
│   ├── display_utils.py
│   ├── __init__.py
│   └── pathfinding.py
└── ollama_tools/         # Main package
    ├── code_executor.py
    ├── __init__.py
    └── tools_engine.py
```

## Running Examples

### Basic Tools Usage
```bash
cd OllamaPlayground/WorkingExamples/ollama_tools/examples
python tools_examples.py
```
This demonstrates:
- Compound interest calculations
- Password validation
- Temperature conversion
- Text analysis
- Mortgage calculations

### Pathfinding Implementation
```bash
cd OllamaPlayground/WorkingExamples/ollama_tools/examples/pathfinding
python pathfinding_example.py
```
Demonstrates:
- A* pathfinding algorithm
- Interactive map navigation
- Landmark-based routing

### Code Execution
```bash
cd OllamaPlayground/WorkingExamples/ollama_tools/examples/code_executor
python code_executor_example.py
```
Demonstrates:
- Secure code execution
- Code validation
- Integration testing

### Basic Usage Example

```python
from ollama_tools import TOOLSEngine

def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

# Initialize engine
engine = TOOLSEngine("llama3.2")
engine.add_tool(add_numbers)
response, tool_calls = engine.chat("What is 5 plus 3?")
print(response)
```

## Documentation

For detailed explanations of the tools system, see `doc/tools_explanation.md`.

## License

MIT License

Copyright (c) 2025
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
