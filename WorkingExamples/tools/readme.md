# TOOLS Library

A Python library for integrating function calling capabilities with Ollama LLMs.

## Installation

### Set up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Install development version from source
git clone https://github.com/yourusername/tools-ollama.git
cd tools-ollama
pip install -e .
```

Note: Ensure you have Ollama installed and running on your system. See [Ollama installation guide](https://ollama.ai/download).

## Usage

### Basic Example

```python
from tools_ollama import TOOLSEngine

def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

# Initialize engine
engine = TOOLSEngine("llama3.2")
engine.add_tool(add_numbers)
response, tool_calls = engine.chat("What is 5 plus 3?")
print(response)
```

## Examples

Check the `examples` directory for more sample code:
- `tools_examples.py`: Various function calling examples
- `pathfinding_example.py`: A* pathfinding implementation

## License

MIT License

Copyright (c) 2024

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
