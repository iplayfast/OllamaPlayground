# Ollama Tools System Documentation

## Overview
The Ollama Tools system provides a framework for extending Ollama language models with custom Python functions. This system enables seamless integration between natural language processing and executable code, allowing models to invoke Python functions as needed during conversations.

## Core Components

### 1. TOOLSEngine Class
The central orchestrator that manages:
- Communication with Ollama models
- Tool registration and execution
- Conversation context and history
- Message routing and response handling

```python
engine = TOOLSEngine("llama3.2")  # Initialize with model name
```

### 2. Tool Class
Converts Python functions into model-compatible formats by:
- Extracting function signatures and type hints
- Converting docstrings into descriptions
- Creating standardized JSON schemas
- Managing parameter validation

## Basic Usage

### Defining Tools
Tools are regular Python functions with type hints and docstrings:

```python
def calculate_sum(a: int, b: int) -> int:
    """Add two numbers together
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of the two numbers
    """
    return a + b
```

### Registering Tools
```python
engine = TOOLSEngine("llama3.2")
engine.add_tool(calculate_sum)
```

### Using Tools in Conversations
```python
response, tool_calls = engine.chat("What is 5 plus 3?")
```

## How It Works

### 1. Message Flow
1. User sends a message
2. Engine forwards message + available tools to Ollama model
3. Model decides if tools are needed
4. If tools are needed:
   - Engine executes tool calls
   - Captures results
   - Returns results to model
   - Gets final response
5. Response returned to user

### 2. Tool Execution Process
```python
# When model decides to use a tool:
tool_calls = response.message.tool_calls
for tool in tool_calls:
    if function_to_call := available_functions.get(tool.function.name):
        output = function_to_call(**tool.function.arguments)
        # Result sent back to model
```

### 3. Type Safety and Validation
- Python type hints ensure parameter type safety
- Automatic validation of required vs optional parameters
- Error handling for invalid inputs
- Conversion between Python and JSON types

## Advanced Features

### 1. Complex Return Types
Tools can return complex data structures:
```python
def analyze_data(numbers: List[float]) -> Dict[str, Any]:
    return {
        "mean": statistics.mean(numbers),
        "median": statistics.median(numbers),
        "std_dev": statistics.stdev(numbers)
    }
```

### 2. Error Handling
```python
def validate_input(value: str) -> Dict[str, bool]:
    if not value:
        raise ValueError("Input cannot be empty")
    return {"valid": True, "length": len(value)}
```

### 3. Tool Chaining
Models can use multiple tools in sequence to solve complex problems:
```python
engine.add_tool(convert_temperature)
engine.add_tool(analyze_weather)
engine.add_tool(generate_forecast)

# Model can chain these tools together in a single response
response = engine.chat("What will the weather be like tomorrow if it's 25°C today?")
```

## Best Practices

### 1. Function Design
- Use clear, descriptive function names
- Provide comprehensive docstrings
- Use appropriate type hints
- Handle edge cases gracefully
- Return structured data when possible

### 2. Tool Registration
- Register related tools together
- Avoid duplicate functionality
- Ensure tool names are unique
- Provide clear descriptions

### 3. Error Handling
- Validate inputs thoroughly
- Raise descriptive exceptions
- Handle expected error cases
- Provide meaningful error messages

## Real-World Examples

### 1. Financial Calculations
```python
def calculate_mortgage(
    principal: float,
    rate: float,
    years: int
) -> Dict[str, float]:
    """Calculate mortgage payment details"""
    monthly_rate = rate / 1200  # Convert APR to monthly
    payments = years * 12
    payment = principal * (monthly_rate * (1 + monthly_rate)**payments) / ((1 + monthly_rate)**payments - 1)
    
    return {
        "monthly_payment": round(payment, 2),
        "total_payment": round(payment * payments, 2),
        "total_interest": round((payment * payments) - principal, 2)
    }
```

### 2. Text Analysis
```python
def analyze_text(text: str) -> Dict[str, Any]:
    """Analyze text and return statistics"""
    words = text.split()
    return {
        "word_count": len(words),
        "char_count": len(text),
        "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
        "sentence_count": text.count('.') + text.count('!') + text.count('?')
    }
```

## Limitations and Considerations

1. Model Dependency
   - Tool effectiveness depends on model understanding
   - Different models may handle tools differently
   - Response quality varies by model capability

2. Performance
   - Complex tools may impact response time
   - Consider async operations for long-running tasks
   - Monitor resource usage for heavy computations

3. Security
   - Validate all inputs thoroughly
   - Consider access control for sensitive operations
   - Be cautious with system operations

## Conclusion
The Ollama Tools system provides a powerful way to extend language models with custom Python functionality. By following best practices and understanding the system's components, developers can create robust and flexible applications that combine natural language processing with custom code execution.
