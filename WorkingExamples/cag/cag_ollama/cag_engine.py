# cag_ollama/cag_engine.py
import json
import os
from typing import Any, Dict, List, Optional
import ollama
from pydantic import BaseModel
import asyncio
import nest_asyncio
from logging import getLogger
import logging
import re

nest_asyncio.apply()
logger = getLogger(__name__)

def configure_logging(level: int = logging.INFO, enable_http_logs: bool = True):
    """Configure logging for the CAG engine."""
    # Configure main logger
    logger.setLevel(level)
    
    # Configure HTTP request logging
    if not enable_http_logs:
        httpx_logger = logging.getLogger("httpx")
        httpx_logger.setLevel(logging.WARNING)

def load_config(config_path=None):
    """Loads the configuration from the specified JSON file."""
    if config_path is None:
        config_path = os.path.join("cag_ollama", "config.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

class ContextTemplate:
    """Manages context templates and their variables."""
    
    def __init__(self, template: str, variables: Dict[str, str]):
        self.template = template
        self.variables = variables
        self._validate_template()
    
    def _validate_template(self):
        """Ensure all template variables are defined."""
        # Use regex to find all template variables
        template_vars = set(re.findall(r'\{([^}]+)\}', self.template))
        missing_vars = template_vars - set(self.variables.keys())
        if missing_vars:
            raise ValueError(f"Missing template variables: {missing_vars}")
    
    def generate(self) -> str:
        """Generate context by filling in template variables."""
        return self.template.format(**self.variables)

class CAGEngineAsync:
    """
    A Context-Augmented Generation engine that combines predefined contexts with LLM responses.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None, 
                 log_level: int = logging.INFO,
                 enable_http_logs: bool = True):
        """Initialize the CAG engine with given configuration."""
        configure_logging(log_level, enable_http_logs)
        self.config = self._initialize_config(config)
        self.model_name = self.config["model"]
        self.ollamaAsyncClient = ollama.AsyncClient()
        self.contexts = {}
        self._validate_models()
    
    def _initialize_config(self, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Initialize configuration with provided config or load defaults."""
        if config is not None:
            return self._validate_config(config)
        
        config = load_config()
        if config is None:
            raise ValueError("Could not load default configuration and no config provided")
        
        return self._validate_config(config)
    
    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the configuration has all required fields."""
        required_fields = ["model"]
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            raise ValueError(f"Configuration missing required fields: {missing_fields}")
        
        return config
    def _validate_models(self) -> None:
        """Verify availability of required model through Ollama."""
        try:
            models_response = ollama.list()
            available_models = [model.model for model in models_response.models]
            
            if self.model_name not in available_models:
                # List of preferred fallback models in order
                fallback_models = [
                    "llama3.2:latest",
                    "llama3.3:latest",
                    "mistral:latest",
                    "openhermes:latest"
                ]
                
                # Try to find a working fallback model
                for model in fallback_models:
                    if model in available_models:
                        logger.warning(
                            f"Model '{self.model_name}' not found. "
                            f"Falling back to '{model}'"
                        )
                        self.model_name = model
                        return
                
                # If no fallback models are available, log available models
                logger.warning(
                    f"Model '{self.model_name}' not found and no fallback models available. "
                    f"Available models: {', '.join(available_models)}"
                )
                raise ValueError(f"No suitable model found. Please install one of: {', '.join(fallback_models)}")
                
        except Exception as e:
            logger.warning(f"Could not verify model availability: {e}")

    def register_context(self, name: str, template: str, variables: Dict[str, str]):
        """Register a new context template."""
        self.contexts[name] = ContextTemplate(template, variables)
        return self.contexts[name]

    def update_context_variables(self, name: str, variables: Dict[str, str]):
        """Update variables for an existing context template."""
        if name not in self.contexts:
            raise KeyError(f"Context '{name}' not found")
        
        self.contexts[name].variables.update(variables)
        self.contexts[name]._validate_template()

    async def generate(self, prompt: str, context_name: str, 
                      system_prompt: Optional[str] = None,
                      **ollama_kwargs: Any) -> Dict[str, Any]:
        """Generate a response using the specified context."""
        if context_name not in self.contexts:
            raise KeyError(f"Context '{context_name}' not found")

        try:
            context = self.contexts[context_name].generate()
            
            final_prompt = (
                f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
                f"<|im_start|>user\nContext:\n{context}\n\n"
                f"Input: {prompt}<|im_end|>"
            ) if system_prompt else f"Context:\n{context}\n\nInput: {prompt}"

            try:
                response = await self.ollamaAsyncClient.generate(
                    model=self.model_name,
                    prompt=final_prompt,
                    **ollama_kwargs
                )
            except Exception as e:
                logger.warning(f"Error with default settings: {e}, trying CPU...")
                response = await self.ollamaAsyncClient.generate(
                    model=self.model_name,
                    prompt=final_prompt,
                    options={"gpu_layers": 0},
                    **ollama_kwargs
                )

            return {"result": response.response if hasattr(response, 'response') else ''}
            
        except Exception as e:
            raise Exception(f"Error during CAG generation: {str(e)}")

    async def generate_structured(self, prompt: str, context_name: str,
                                response_model: type[BaseModel],
                                system_prompt: Optional[str] = None,
                                **ollama_kwargs: Any) -> BaseModel:
        """Generate a structured response using the specified context."""
        if context_name not in self.contexts:
            raise KeyError(f"Context '{context_name}' not found")

        try:
            context = self.contexts[context_name].generate()

            response = await self.ollamaAsyncClient.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': system_prompt if system_prompt else 
                            'You are a helpful assistant. Return your response in the requested JSON format.'
                    },
                    {
                        'role': 'user',
                        'content': f"Context:\n{context}\n\nInput: {prompt}"
                    }
                ],
                format=response_model.model_json_schema(),
                options={'temperature': 0.7, **ollama_kwargs}
            )

            return response_model.model_validate_json(response.message.content)
            
        except Exception as e:
            raise Exception(f"Error during structured CAG generation: {str(e)}")

class CAGEngine:
    """Synchronous wrapper for the async CAG engine."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 log_level: int = logging.INFO,
                 enable_http_logs: bool = True):
        self.engine = CAGEngineAsync(config=config, 
                                   log_level=log_level,
                                   enable_http_logs=enable_http_logs)
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
    
    def __del__(self):
        if self._loop and not self._loop.is_closed():
            self._loop.close()

    def _run_async(self, coro):
        try:
            result = self._loop.run_until_complete(coro)
            return result
        except RuntimeError as e:
            if "Event loop is closed" in str(e):
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
                return self._loop.run_until_complete(coro)
            raise

    def register_context(self, name: str, template: str, variables: Dict[str, str]):
        """Register a new context template."""
        return self.engine.register_context(name, template, variables)

    def update_context_variables(self, name: str, variables: Dict[str, str]):
        """Update variables for an existing context template."""
        return self.engine.update_context_variables(name, variables)

    def generate(self, prompt: str, context_name: str,
                system_prompt: Optional[str] = None,
                **ollama_kwargs: Any) -> Dict[str, Any]:
        """Generate a response using the specified context."""
        return self._run_async(
            self.engine.generate(prompt, context_name,
                               system_prompt=system_prompt,
                               **ollama_kwargs)
        )

    def generate_structured(self, prompt: str, context_name: str,
                          response_model: type[BaseModel],
                          system_prompt: Optional[str] = None,
                          **ollama_kwargs: Any) -> BaseModel:
        """Generate a structured response using the specified context."""
        return self._run_async(
            self.engine.generate_structured(
                prompt, context_name, response_model,
                system_prompt=system_prompt,
                **ollama_kwargs
            )
        )
