from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union, get_type_hints
import inspect
import json
from ollama import chat, ChatResponse
from lib.debugprint import dprint, DebugLevel

@dataclass
class ToolCall:
    name: str
    arguments: Dict[str, Any]
    response: Any = None

class Tool:
    def __init__(self, func: Callable, description: Optional[str] = None):
        self.func = func
        self.name = func.__name__
        self.description = description or func.__doc__ or "No description provided"
        self.type_hints = get_type_hints(func)
        self.sig = inspect.signature(func)
        self.type_map = {
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "string": str,
            "array": list,
            "object": dict
        }
        self.parameters = self._get_parameters(self.sig)
    
    def _get_parameters(self, sig: inspect.Signature) -> Dict:
        params = {
            "type": "object",
            "required": [],
            "properties": {}
        }
        for name, param in sig.parameters.items():
            param_type = self.type_hints.get(name, Any)
            if param_type == inspect.Parameter.empty:
                param_type = Any
            params["properties"][name] = {
                "type": self._get_json_type(param_type),
                "description": f"Parameter {name}"
            }
            if param.default == inspect.Parameter.empty:
                params["required"].append(name)
        return params
    
    def _get_json_type(self, typ: type) -> str:
        if typ in (int, float):
            return "number"
        for key, value in self.type_map.items():
            if typ in value if isinstance(value, tuple) else typ == value:
                return key
        return "string"
    
    def convert_argument(self, name: str, value: Any) -> Any:
        """Convert argument to the correct type based on type hints"""
        target_type = self.type_hints.get(name, Any)
        
        # Handle tuple conversion first
        if isinstance(value, str) and value.startswith('(') and value.endswith(')'):
            try:
                # Extract numbers from the string tuple
                numbers = [int(x.strip()) for x in value.strip('()').split(',')]
                return tuple(numbers)
            except (ValueError, SyntaxError):
                pass  # Fall through to other conversions if tuple conversion fails
        
        # Handle special cases
        if target_type == bool:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'y')
            return bool(value)
        elif target_type in (int, float):
            if isinstance(value, str):
                # Remove any currency symbols or other non-numeric characters
                cleaned_value = ''.join(c for c in value if c.isdigit() or c in '.-')
                return target_type(cleaned_value)
            return target_type(value)
        
        # Default case: try direct conversion
        try:
            return target_type(value)
        except (TypeError, ValueError):
            return value
    
    def to_dict(self) -> Dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

class TOOLSEngine:
    def __init__(self, model: str):
        self.model = model
        self.tools: Dict[str, Tool] = {}
        self.messages: List[Dict[str, str]] = []
    
    def add_tool(self, func: Union[Callable, Dict]) -> None:
        if isinstance(func, dict):
            name = func["function"]["name"]
            self.tools[name] = func
        else:
            tool = Tool(func)
            self.tools[tool.name] = tool

    def chat(self, message: str) -> tuple[str, list[ToolCall]]:
        dprint.set_level('DEBUG')
        dprint.verbose("\n=== Starting chat function ===")
        dprint.verbose(f"Received message: {message}")
        
        all_tool_calls = []
        current_message = message
        
        while True:  # Allow for multiple rounds of tool processing
            self.messages.append({"role": "user", "content": current_message})
            dprint.verbose(f"\nProcessing message: {current_message}")
            
            tool_list = [t.to_dict() if isinstance(t, Tool) else t for t in self.tools.values()]
            
            response: ChatResponse = chat(
                self.model,
                messages=self.messages,
                tools=tool_list
            )
            
            if not response.message.tool_calls:
                dprint.verbose("\nNo tool calls in response")
                return response.message.content, all_tool_calls
                
            next_prompt = None
            
            for tool_call in response.message.tool_calls:
                tool_name = tool_call.function.name
                
                if tool := self.tools.get(tool_name):
                    try:
                        args = (tool_call.function.arguments 
                            if isinstance(tool_call.function.arguments, dict)
                            else json.loads(tool_call.function.arguments))
                        
                        dprint.verbose(f"Original args: {args}")
                        
                        # Process arguments with type conversion
                        processed_args = {}
                        if isinstance(tool, Tool):
                            for key, value in args.items():
                                processed_args[key] = tool.convert_argument(key, value)
                        else:
                            processed_args = args
                                
                        dprint.verbose(f"Processed args: {processed_args}")
                        
                        if isinstance(tool, Tool):
                            result = tool.func(**processed_args)
                        else:
                            func_name = tool["function"]["name"]
                            result = globals()[func_name](**processed_args)
                        
                        all_tool_calls.append(ToolCall(tool_name, processed_args, result))
                        
                        # Check if the result includes a prompt for the next round
                        if isinstance(result, dict) and "promptMessage" in result:
                            next_prompt = result["promptMessage"]
                            dprint.verbose(f"\nTool returned new prompt: {next_prompt}")
                            break
                            
                        self.messages.append(response.message)
                        self.messages.append({
                            "role": "tool",
                            "content": str(result),
                            "name": tool_name
                        })
                            
                    except Exception as e:
                        dprint.verbose(f"Error during tool execution: {str(e)}")
                        raise
            
            if next_prompt:
                current_message = next_prompt
                continue
            else:
                if response.message.tool_calls:
                    final_response = chat(self.model, messages=self.messages)
                    return final_response.message.content, all_tool_calls
                return response.message.content, all_tool_calls
