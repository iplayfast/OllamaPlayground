# ollama_context/engine.py
import json
import os
from typing import Any, Dict, List, Optional
import ollama
import chromadb
from fastapi import HTTPException
from pydantic import BaseModel
import asyncio
import nest_asyncio
from logging import getLogger
import logging
import re

nest_asyncio.apply()
logger = getLogger(__name__)

def configure_logging(level: int = logging.INFO, enable_http_logs: bool = True):
    """Configure logging for the engine."""
    logger.setLevel(level)
    if not enable_http_logs:
        httpx_logger = logging.getLogger("httpx")
        httpx_logger.setLevel(logging.WARNING)

def load_config(config_path=None):
    """Loads the configuration from the specified JSON file."""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "embedding_model": "nomic-embed-text:latest",
            "response_model": "llama3.2:latest"
        }

def split_into_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs by newlines."""
    cleaned_text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
    paragraphs = [p.strip() for p in cleaned_text.split('\n\n') if p.strip()]
    return paragraphs

def merge_short_paragraphs(paragraphs: List[str], min_size: int = 100, max_size: int = 300) -> List[str]:
    """Merge paragraphs into optimally sized chunks."""
    merged = []
    current_chunk = []
    current_size = 0
    
    for p in paragraphs:
        if current_size + len(p) > max_size and current_chunk:
            merged.append(' '.join(current_chunk))
            current_chunk = []
            current_size = 0
        
        if len(p) > max_size:
            sentences = [s.strip() + '.' for s in p.split('.') if s.strip()]
            for sentence in sentences:
                if len(sentence) > max_size:
                    words = sentence.split()
                    temp = []
                    temp_size = 0
                    for word in words:
                        if temp_size + len(word) > max_size:
                            merged.append(' '.join(temp))
                            temp = [word]
                            temp_size = len(word)
                        else:
                            temp.append(word)
                            temp_size += len(word) + 1
                    if temp:
                        merged.append(' '.join(temp))
                else:
                    merged.append(sentence)
        else:
            current_chunk.append(p)
            current_size += len(p)
            
            if current_size >= min_size and (p.endswith('.') or p.endswith('?') or p.endswith('!')):
                merged.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
    
    if current_chunk:
        merged.append(' '.join(current_chunk))
    
    return merged

class ContextTemplate:
    """Manages context templates and their variables."""
    
    def __init__(self, template: str, variables: Dict[str, str]):
        self.template = template
        self.variables = variables
        self._validate_template()
    
    def _validate_template(self):
        """Ensure all template variables are defined."""
        template_vars = set(re.findall(r'\{([^}]+)\}', self.template))
        missing_vars = template_vars - set(self.variables.keys())
        if missing_vars:
            raise ValueError(f"Missing template variables: {missing_vars}")
    
    def generate(self) -> str:
        """Generate context by filling in template variables."""
        return self.template.format(**self.variables)

class ContextEngineAsync:
    """A unified engine combining retrieval and context capabilities."""
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        mode: str = "auto",
        log_level: int = logging.INFO,
        enable_http_logs: bool = True,
        database: Optional[str] = None
    ):
        configure_logging(log_level, enable_http_logs)
        self.config = self._initialize_config(config)
        self.mode = mode
        self.ollamaAsyncClient = ollama.AsyncClient()
        
        # Initialize models
        self.embedding_model = self.config.get("embedding_model", "nomic-embed-text:latest")
        self.response_model = self.config.get("response_model", "llama3.2:latest")
        
        # Initialize stores
        if mode in ["retrieval", "combined", "auto"]:
            self._initialize_vector_store(database)
        if mode in ["context", "combined", "auto"]:
            self.contexts = {}
            
        self._validate_models()

    def _initialize_config(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Initialize configuration with provided config or load defaults."""
        if config:
            return self._validate_config(config)
        return self._validate_config(load_config())
    
    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration has all required fields."""
        required_fields = ["embedding_model", "response_model"]
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            raise ValueError(f"Configuration missing required fields: {missing_fields}")
        return config
    def register_context(self, name: str, template: str, variables: Dict[str, str]):
        """Register a new context template."""
        self.contexts[name] = ContextTemplate(template, variables)
        logger.info(f"Registered context: {name}")
        return self.contexts[name]

    def update_context_variables(self, name: str, variables: Dict[str, str]):
        """Update variables for an existing context template."""
        if name not in self.contexts:
            raise KeyError(f"Context '{name}' not found")
        
        self.contexts[name].variables.update(variables)
        self.contexts[name]._validate_template()
        logger.info(f"Updated context variables for: {name}")
    def _initialize_vector_store(self, database=None) -> None:
        """Initialize connection to ChromaDB."""
        try:
            if database is None:
                self.chroma_client = chromadb.Client()
            else:
                self.chroma_client = chromadb.PersistentClient(path=database)
            self.chroma_client.heartbeat()
            self.vectorstore = None
        except Exception as e:
            raise ConnectionError(f"Failed to initialize ChromaDB: {e}")


    async def query(self, prompt: str, system_prompt: Optional[str] = None,
                context_name: Optional[str] = None, where: Optional[Dict[str, Any]] = None,
                mode: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Query with mode-specific handling."""
        try:
            # Handle mode selection
            query_mode = mode if mode is not None else self.mode
            
            context_str = ""
            
            # Handle context if we're using CAG mode
            if context_name and query_mode in ["context", "combined", "auto"]:
                if context_name not in self.contexts:
                    raise KeyError(f"Context '{context_name}' not found")
                context_str = self.contexts[context_name].generate() + "\n\n"

            # Handle RAG if we have a where clause
            if where and query_mode in ["retrieval", "combined", "auto"]:
                if self.vectorstore is None:
                    raise ValueError("No documents indexed for retrieval")

                # Get embedding for query
                query_embedding = await self._get_embeddings(prompt)
                
                # Check if documents exist
                collection_data = self.vectorstore.get()
                if not collection_data['ids']:
                    return {"result": "No documents have been indexed yet."}
                
                # Query the vector store
                query_params = {
                    "query_embeddings": [query_embedding],
                    "n_results": min(4, len(collection_data['ids'])),
                    "include": ["documents"],
                    "where": where
                }
                
                results = self.vectorstore.query(**query_params)
                
                if not results or 'documents' not in results or not results['documents']:
                    return {"result": "No relevant documents found"}
                
                retrieved_context = "\n".join(results['documents'][0])
                
                if context_str:
                    # Combine CAG and RAG contexts
                    final_prompt = f"{context_str}Additional Context:\n{retrieved_context}\n\nInput: {prompt}"
                else:
                    # RAG-only
                    final_prompt = f"Context:\n{retrieved_context}\n\nInput: {prompt}"
            else:
                # CAG-only or direct prompt
                final_prompt = f"{context_str}Input: {prompt}" if context_str else prompt

            if system_prompt:
                final_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{final_prompt}<|im_end|>"

            # Remove mode from kwargs before passing to Ollama
            kwargs.pop('mode', None)
            
            try:
                response = await self.ollamaAsyncClient.generate(
                    model=self.response_model,
                    prompt=final_prompt,
                    **kwargs
                )
            except Exception:
                # Fallback to CPU if GPU fails
                response = await self.ollamaAsyncClient.generate(
                    model=self.response_model,
                    prompt=final_prompt,
                    options={"gpu_layers": 0},
                    **kwargs
                )

            return {"result": response.response if hasattr(response, 'response') else ''}
                
        except Exception as e:
            logger.error(f"Error during query: {str(e)}")
            raise

    async def query_structured(self, prompt: str, response_model: type[BaseModel],
                            context_name: Optional[str] = None,
                            system_prompt: Optional[str] = None,
                            where: Optional[Dict[str, Any]] = None,
                            mode: Optional[str] = None,
                            **kwargs: Any) -> BaseModel:
        """Generate a structured response with mode-specific handling."""
        try:
            # Handle mode selection
            query_mode = mode if mode is not None else self.mode
            
            context_str = ""
            
            # Handle context if we're using CAG
            if context_name and query_mode in ["context", "combined", "auto"]:
                if context_name not in self.contexts:
                    raise KeyError(f"Context '{context_name}' not found")
                context_str = self.contexts[context_name].generate() + "\n\n"

            # Handle RAG if we have a where clause
            if where and query_mode in ["retrieval", "combined", "auto"]:
                if self.vectorstore is None:
                    raise ValueError("No documents indexed for retrieval")

                # Get embedding for query
                query_embedding = await self._get_embeddings(prompt)
                
                # Query the vector store
                query_params = {
                    "query_embeddings": [query_embedding],
                    "n_results": 4,
                    "include": ["documents"],
                    "where": where
                }
                
                results = self.vectorstore.query(**query_params)
                
                if not results or 'documents' not in results or not results['documents']:
                    raise ValueError("No relevant documents found")
                
                retrieved_context = "\n".join(results['documents'][0])
                
                if context_str:
                    context_str += f"Additional Context:\n{retrieved_context}\n\n"
                else:
                    context_str = f"Context:\n{retrieved_context}\n\n"

            messages = [
                {
                    'role': 'system',
                    'content': system_prompt if system_prompt else 
                        'Return your response in the requested JSON format.'
                },
                {
                    'role': 'user',
                    'content': f"{context_str}Input: {prompt}"
                }
            ]

            # Remove mode from kwargs before passing to Ollama
            kwargs.pop('mode', None)

            response = await self.ollamaAsyncClient.chat(
                model=self.response_model,
                messages=messages,
                format=response_model.model_json_schema(),
                options={'temperature': 0.7, **kwargs}
            )

            return response_model.model_validate_json(response.message.content)
        except Exception as e:
            logger.error(f"Error during structured query: {str(e)}")
            raise
        
    def check_database_status(self):
        """Check database status."""
        try:
            collections = self.chroma_client.list_collections()
            
            if not collections:
                return {"status": "empty", "message": "No collections found"}
                
            if self.vectorstore is None:
                try:
                    self.vectorstore = self.chroma_client.get_collection("rag_collection")
                except:
                    return {"status": "empty", "message": "Collection not found"}
            
            collection_data = self.vectorstore.get()
            return {
                "status": "populated" if len(collection_data['ids']) > 0 else "empty",
                "num_documents": len(collection_data['ids']),
                "ids": collection_data['ids']
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _get_embeddings(self, text: str, use_cpu: bool = False) -> List[float]:
        """Generate embeddings for text."""
        options = {"gpu_layers": 0} if use_cpu else {}
        try:
            response = await self.ollamaAsyncClient.embeddings(
                model=self.embedding_model,
                prompt=text,
                options=options
            )
            if hasattr(response, 'embedding'):
                return [float(x) for x in response.embedding]
            raise ValueError("Invalid embedding format")
        except Exception as e:
            if not use_cpu:
                return await self._get_embeddings(text, use_cpu=True)
            raise
    async def index_documents(self, documents_path: str,
                        metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        """Index documents with optional metadata, skipping existing content."""
        # Read and process the document
        with open(documents_path, "r") as f:
            text = f.read()

        paragraphs = split_into_paragraphs(text)
        chunks = merge_short_paragraphs(paragraphs)
        
        # Initialize or get collection
        try:
            if self.vectorstore is None:
                try:
                    self.vectorstore = self.chroma_client.get_collection("rag_collection")
                    logger.info("Retrieved existing collection")
                except:
                    self.vectorstore = self.chroma_client.create_collection("rag_collection")
                    logger.info("Created new collection")

            # Get existing documents and their IDs
            existing_data = self.vectorstore.get()
            existing_docs = set(existing_data['documents'])
            next_id = max([int(id.split('_')[1]) for id in existing_data['ids']] + [-1]) + 1

            # Prepare new documents
            new_embeddings = []
            new_documents = []
            new_ids = []
            new_metadatas = []
            
            doc_id = next_id
            for i, chunk in enumerate(chunks):
                # Skip if document already exists
                if chunk in existing_docs:
                    continue
                    
                # Get embedding for new document
                embedding = await self._get_embeddings(chunk)
                
                if metadatas:
                    for metadata in metadatas:
                        new_embeddings.append(embedding)
                        new_documents.append(chunk)
                        new_ids.append(f"doc_{doc_id}")
                        new_metadatas.append(metadata)
                        doc_id += 1
                else:
                    new_embeddings.append(embedding)
                    new_documents.append(chunk)
                    new_ids.append(f"doc_{doc_id}")
                    doc_id += 1

            # Add only if we have new documents
            if new_documents:
                if metadatas:
                    self.vectorstore.add(
                        embeddings=new_embeddings,
                        documents=new_documents,
                        ids=new_ids,
                        metadatas=new_metadatas
                    )
                else:
                    self.vectorstore.add(
                        embeddings=new_embeddings,
                        documents=new_documents,
                        ids=new_ids
                    )
                logger.info(f"Added {len(new_documents)} new documents to collection")
            else:
                logger.info("No new documents to add - all content already exists")
                
        except Exception as e:
            logger.error(f"Error during document indexing: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error during indexing: {str(e)}")
        

    def _validate_models(self) -> None:
        """Verify model availability."""
        try:
            models_response = ollama.list()
            available_models = [model.model for model in models_response.models]
            
            for model_name in [self.embedding_model, self.response_model]:
                if model_name not in available_models:
                    logger.warning(f"Model '{model_name}' not found. Available: {available_models}")
        except Exception as e:
            logger.warning(f"Could not verify models: {e}")
            
    
class ContextEngine:
    """Synchronous wrapper for ContextEngineAsync."""    
    
    def __init__(self, **kwargs):
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        self.engine = ContextEngineAsync(**kwargs)
    
    def _run_async(self, coro):
        """Run coroutine in event loop."""
        try:
            if self._loop.is_running():
                # If we're in a running loop (like FastAPI), use asyncio.run_coroutine_threadsafe
                future = asyncio.run_coroutine_threadsafe(coro, self._loop)
                return future.result()
            else:
                # If no loop is running, run it directly
                return self._loop.run_until_complete(coro)
        except Exception as e:
            raise e
        
    def __del__(self):
        try:
            if hasattr(self, '_loop') and self._loop and not self._loop.is_closed():
                pending = asyncio.all_tasks(self._loop)
                if pending:
                    self._loop.run_until_complete(asyncio.gather(*pending))
                self._loop.close()
        except Exception:
            pass

    async def cleanup(self):
        """Cleanup async resources."""
        if hasattr(self, '_loop') and self._loop and not self._loop.is_closed():
            pending = asyncio.all_tasks(self._loop)
            if pending:
                await asyncio.gather(*pending, return_exceptions=True)

    def _run_async(self, coro):
        """Run coroutine in event loop."""
        try:
            return self._loop.run_until_complete(coro)
        except RuntimeError as e:
            if "Event loop is closed" in str(e):
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
                return self._loop.run_until_complete(coro)
            raise
                
    def check_database_status(self):
        """Check database status."""
        return self.engine.check_database_status()
    def register_context(self, name: str, template: str, variables: Dict[str, str]):
        """Register a new context template."""
        return self.engine.register_context(name, template, variables)

    def update_context_variables(self, name: str, variables: Dict[str, str]):
        """Update variables for an existing context template."""
        return self.engine.update_context_variables(name, variables)

    def load_and_index_documents(self, documents_path: str,
                               metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        """Index documents synchronously."""
        return self._run_async(
            self.engine.index_documents(documents_path, metadatas)
        )


    def query(self, prompt: str, system_prompt: Optional[str] = None,
            context_name: Optional[str] = None, where: Optional[Dict[str, Any]] = None,
            **kwargs: Any) -> Dict[str, Any]:
        """Query synchronously with all options."""
        return self._run_async(
            self.engine.query(
                prompt=prompt,
                system_prompt=system_prompt,
                context_name=context_name,
                where=where,
                **kwargs
            )
        )

    def query_structured(self, prompt: str, response_model: type[BaseModel],
                        context_name: Optional[str] = None,
                        system_prompt: Optional[str] = None,
                        where: Optional[Dict[str, Any]] = None,
                        **kwargs: Any) -> BaseModel:
        """Structured query synchronously with all options."""
        return self._run_async(
            self.engine.query_structured(
                prompt=prompt,
                response_model=response_model,
                context_name=context_name,
                system_prompt=system_prompt,
                where=where,
                **kwargs
            )
        )
        
