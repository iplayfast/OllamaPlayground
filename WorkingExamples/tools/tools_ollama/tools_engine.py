from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union
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
        sig = inspect.signature(func)
        self.type_map = {
            "number": (int, float),
            "boolean": bool,
            "string": str,
            "array": list,
            "object": dict
        }
        self.parameters = self._get_parameters(sig)
    
    def _get_parameters(self, sig: inspect.Signature) -> Dict:
        params = {
            "type": "object",
            "required": [],
            "properties": {}
        }
        for name, param in sig.parameters.items():
            param_type = param.annotation
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
        for key, value in self.type_map.items():
            if typ in value if isinstance(value, tuple) else typ == value:
                return key
        return "string"
    
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
        dprint.set_level('DEBUG')  # Using string
        dprint.info("\n=== Starting chat function ===")
        dprint.info(f"Received message: {message}")
        
        all_tool_calls = []  # Track all tool calls across chains
        current_message = message
        
        while True:  # Allow for multiple rounds of tool processing
            self.messages.append({"role": "user", "content": current_message})
            dprint.info(f"\nProcessing message: {current_message}")
            
            tool_list = [t.to_dict() if isinstance(t, Tool) else t for t in self.tools.values()]
            
            response: ChatResponse = chat(
                self.model,
                messages=self.messages,
                tools=tool_list
            )
            
            if not response.message.tool_calls:
                dprint.info("\nNo tool calls in response")
                return response.message.content, all_tool_calls
                
            next_prompt = None
            
            for tool_call in response.message.tool_calls:
                tool_name = tool_call.function.name
                
                if tool := self.tools.get(tool_name):
                    try:
                        args = (tool_call.function.arguments 
                            if isinstance(tool_call.function.arguments, dict)
                            else json.loads(tool_call.function.arguments))
                        
                        # Process arguments to convert string tuples to actual tuples
                        processed_args = {}
                        for key, value in args.items():
                            if isinstance(value, str) and value.startswith('(') and value.endswith(')'):
                                # Convert string tuple to actual tuple
                                try:
                                    # Extract numbers from the string tuple
                                    numbers = [int(x.strip()) for x in value.strip('()').split(',')]
                                    processed_args[key] = tuple(numbers)
                                except (ValueError, SyntaxError):
                                    # If conversion fails, keep original value
                                    processed_args[key] = value
                            else:
                                processed_args[key] = value
                                
                        dprint.info(f"Original args: {args}")
                        dprint.info(f"Processed args: {processed_args}")
                        
                        if isinstance(tool, Tool):
                            result = tool.func(**processed_args)
                        else:
                            func_name = tool["function"]["name"]
                            result = globals()[func_name](**processed_args)
                        
                        all_tool_calls.append(ToolCall(tool_name, processed_args, result))
                        
                        # Check if the result includes a prompt for the next round
                        if isinstance(result, dict) and "promptMessage" in result:
                            next_prompt = result["promptMessage"]
                            dprint.info(f"\nTool returned new prompt: {next_prompt}")
                            break  # Exit tool processing to handle new prompt
                            
                    except Exception as e:
                        dprint.info(f"Error during tool execution: {str(e)}")
                        raise
            
            if next_prompt:
                current_message = next_prompt  # Continue loop with new prompt
                continue
            else:
                return response.message.content, all_tool_calls  # End if no new prompt
        
    
            

    def chatold(self, message: str) -> tuple[str, list[ToolCall]]:
        self.messages.append({"role": "user", "content": message})
        
        tool_list = [t.to_dict() if isinstance(t, Tool) else t for t in self.tools.values()]
        
        response: ChatResponse = chat(
            self.model,
            messages=self.messages,
            tools=tool_list
        )
        
        if response.message.tool_calls:
            tool_calls = []
            for tool_call in response.message.tool_calls:
                tool_name = tool_call.function.name
                if tool := self.tools.get(tool_name):
                    # Convert arguments string to dictionary
                    if isinstance(tool_call.function.arguments, dict):
                        args = tool_call.function.arguments
                    else:
                        args = json.loads(tool_call.function.arguments)
                        
                    if isinstance(tool, Tool):
                        result = tool.func(**args)
                    else:
                        func_name = tool["function"]["name"]
                        result = globals()[func_name](**args)
                    
                    tool_calls.append(ToolCall(tool_name, args, result))
                    
                    self.messages.append(response.message)
                    self.messages.append({
                        "role": "tool",
                        "content": str(result),
                        "name": tool_name
                    })
            
            final_response = chat(self.model, messages=self.messages)
            return final_response.message.content, tool_calls
        
        return response.message.content, []
