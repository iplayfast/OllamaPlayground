from io import StringIO
import sys
from typing import Dict, Any
from ollama_tools.tools_engine import TOOLSEngine
import subprocess
import ast
import requests

def check_available_models():
    """
    Check which Ollama models are available locally.
    
    Returns:
        List of available model names
    """
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            models = response.json()
            return [model['name'] for model in models['models']]
        return []
    except Exception as e:
        print(f"Error checking available models: {e}")
        return []

def create_code(description: str) -> Dict[str, Any]:
    """
    Request the creation of Python code based on a description.
    
    Args:
        description: Description of what the code should do
        
    Returns:
        Dict containing:
            - code: The generated code (str)
            - description: Original request (str)
    """
    return {
        "code": "",  # This will be filled by the LLM
        "description": description
    }

def validate_code(code: str) -> Dict[str, Any]:
    """
    Validate Python code without executing it.
    
    Args:
        code: Python code to validate
        
    Returns:
        Dict containing:
            - valid: Whether code is syntactically valid (bool)
            - errors: List of syntax errors found (List[str])
            - warnings: List of potential issues (List[str])
    """
    results = {
        "valid": False,
        "errors": [],
        "warnings": []
    }
    
    try:
        # Parse the code to check syntax
        ast.parse(code)
        results["valid"] = True
        
        # Basic code checks
        tree = ast.parse(code)
        for node in ast.walk(tree):
            # Check for potential infinite recursion
            if isinstance(node, ast.FunctionDef):
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Call) and hasattr(subnode.func, 'id') and subnode.func.id == node.name:
                        if not any(isinstance(n, ast.If) for n in ast.walk(node)):
                            results["warnings"].append(f"Function {node.name} may have infinite recursion - no base case found")
            
            # Check for bare except clauses
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                results["warnings"].append("Bare except clause used - consider catching specific exceptions")
                
    except SyntaxError as e:
        results["errors"].append(f"Syntax error: {str(e)}")
    except Exception as e:
        results["errors"].append(f"Validation error: {str(e)}")
    
    return results

def execute_code(code: str) -> Dict[str, Any]:
    """
    Execute Python code in a controlled environment.
    
    Args:
        code: Python code to execute
        
    Returns:
        Dict containing:
            - success: Whether execution was successful (bool)
            - output: Output from the code execution (str)
            - error: Error message if execution failed (str)
    """
    # Capture original stdout/stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    
    # Create string buffers for output capture
    stdout_buffer = StringIO()
    stderr_buffer = StringIO()
    
    # Results dictionary
    results = {
        "success": False,
        "output": "",
        "error": ""
    }
    
    try:
        # Redirect output
        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer
        
        # Create namespace for execution
        namespace = {'__name__': '__main__'}
        
        # Add builtins to namespace
        namespace.update({
            name: getattr(__builtins__, name)
            for name in ['abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 
                       'dir', 'divmod', 'enumerate', 'filter', 'float', 'format',
                       'frozenset', 'hash', 'hex', 'int', 'isinstance', 'issubclass',
                       'iter', 'len', 'list', 'map', 'max', 'min', 'next', 'oct',
                       'ord', 'pow', 'print', 'range', 'repr', 'reversed', 'round',
                       'set', 'slice', 'sorted', 'str', 'sum', 'tuple', 'type', 'zip']
        })
        
        # Execute the code in a single namespace
        exec(code, namespace)
        
        # Capture output
        results["output"] = stdout_buffer.getvalue()
        results["success"] = True
        
    except Exception as e:
        results["error"] = f"{type(e).__name__}: {str(e)}"
        results["success"] = False
        
    finally:
        # Restore original stdout/stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
    return results

if __name__ == "__main__":
    # The specific model we want to use
    REQUIRED_MODEL = "llama3.2"
    
    # Check available models
    #available_models = check_available_models()
    
    #print("\nChecking for required model:", REQUIRED_MODEL)
    
    #if REQUIRED_MODEL not in available_models:
    #    print(f"\nRequired model {REQUIRED_MODEL} not found.")
    #    print(f"Please install it using:")
    #    print(f"ollama pull {REQUIRED_MODEL}")
    #    sys.exit(1)
    
    try:
        # Initialize engine with our specific model
        engine = TOOLSEngine(REQUIRED_MODEL)
        
        # Register all three tools
        engine.add_tool(create_code)
        engine.add_tool(validate_code)
        engine.add_tool(execute_code)
        
        # Test the tools through the engine
        print("\nTesting code creation, validation, and execution pipeline...\n")
        
        # Step 1: Create the code
        response, tool_calls = engine.chat(
            "Using the create_code tool, write a Python function to calculate factorial of 5. "
            "The code should include a proper base case to avoid infinite recursion."
        )
        
        if tool_calls and tool_calls[0].response.get("code"):
            generated_code = tool_calls[0].response["code"]
            print("\nGenerated Code:")
            print(generated_code)
            
            # Step 2: Validate the code
            print("\nValidating code...")
            response, validate_calls = engine.chat(
                f"Using the validate_code tool, check this code for issues:\n{generated_code}"
            )
            
            if validate_calls and validate_calls[0].response.get("valid"):
                print("Code is valid!")
                if validate_calls[0].response.get("warnings"):
                    print("Warnings:", validate_calls[0].response["warnings"])
                
                # Step 3: Execute the code
                print("\nExecuting code...")
                response, execute_calls = engine.chat(
                    f"Using the execute_code tool, run this code:\n{generated_code}"
                )
                
                if execute_calls and execute_calls[0].response.get("success"):
                    print("Output:", execute_calls[0].response["output"])
                else:
                    print("Execution failed:", execute_calls[0].response.get("error"))
            else:
                print("Validation failed:", validate_calls[0].response.get("errors"))
                
    except Exception as e:
        print(f"\nError: {e}")
        if "does not support tools" in str(e):
            print(f"\nThe model {REQUIRED_MODEL} is required for this example as it supports function calling.")
            print(f"Please ensure you have it installed: ollama pull {REQUIRED_MODEL}")
        else:
            print("\nPlease ensure Ollama is running:")
            print("ollama serve")
