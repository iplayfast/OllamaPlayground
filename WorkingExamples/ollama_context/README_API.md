# ollama_context API Demo Guide

## Prerequisites
- Python installed on your system
- `venv` module available (typically included with Python)

## Setup

### 1. Create a Virtual Environment
```bash
python -m venv ollama_context_env
```

### 2. Activate the Virtual Environment
#### On Windows:
```bash
ollama_context_env\Scripts\activate
```

#### On macOS and Linux:
```bash
source ollama_context_env/bin/activate
```

### 3. Install Dependencies
With the virtual environment activated, install the required packages:
```bash
pip install -r requirements.txt
```

## Demo Procedure

### Terminal 1: Start API Server
1. Activate the virtual environment
2. Run the API server:
```bash
python examples/run_api.py
```

### Terminal 2: Run API Usage Example
1. Open a new terminal
2. Activate the same virtual environment
3. Run the usage example:
```bash
python examples/api_usage_example.py
```

## Troubleshooting
- Ensure the virtual environment is activated in both terminals
- Verify all dependencies are installed
- Check that no other processes are using the same network port

## Deactivating the Virtual Environment
When you're done, you can deactivate the virtual environment:
```bash
deactivate
```

## Additional Notes
- Both scripts require the virtual environment to be activated
- Dependencies should be installed within the virtual environment

## Contact
For issues or questions, please refer to the project's issue tracker or contact the maintainer.
