# game/rag_ollama/rag_engine.py
import json
import os
from typing import Any, Dict, List, Optional
import ollama
import chromadb
from fastapi import HTTPException

from pydantic import BaseModel
from typing import List, Optional, Any, Dict
import asyncio
from ollama import AsyncClient

"""
RAG (Retrieval-Augmented Generation) Engine using Ollama and ChromaDB
====================================================

This engine combines document retrieval with LLM responses by:
1. Storing document embeddings in a vector database (ChromaDB)
2. Finding relevant document chunks for queries
3. Using those chunks as context for LLM responses (via Ollama)

Usage Examples:
See rag_usage_example.py for complete usage examples
"""
""" some utility functions"""
def split_into_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs by newlines."""
    # First clean up any excessive newlines
    cleaned_text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
    # Split on double newlines
    paragraphs = [p.strip() for p in cleaned_text.split('\n\n') if p.strip()]
    return paragraphs

def merge_short_paragraphs(paragraphs: List[str], min_size: int = 100, max_size: int = 300) -> List[str]:
    """
    Merge paragraphs into smaller, more focused chunks.
    
    Args:
        paragraphs: List of paragraph strings
        min_size: Minimum desired chunk size in characters (default: 100)
        max_size: Maximum desired chunk size in characters (default: 300)
    """
    merged = []
    current_chunk = []
    current_size = 0
    
    for p in paragraphs:
        # If this paragraph would make chunk too large, save current and start new
        if current_size + len(p) > max_size and current_chunk:
            merged.append(' '.join(current_chunk))
            current_chunk = []
            current_size = 0
        
        # If this single paragraph is longer than max_size, split it
        if len(p) > max_size:
            sentences = [s.strip() + '.' for s in p.split('.') if s.strip()]
            for sentence in sentences:
                if len(sentence) > max_size:
                    # If even a sentence is too long, force-split it
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
            
            # If we've reached minimum size and hit a natural break, save chunk
            if current_size >= min_size and (
                p.endswith('.') or 
                p.endswith('?') or 
                p.endswith('!')
            ):
                merged.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
    
    # Don't forget any remaining content
    if current_chunk:
        merged.append(' '.join(current_chunk))
    
    # Add debug output
    print("\nCreated chunks with sizes:")
    for i, chunk in enumerate(merged):
        print(f"\nChunk {i} ({len(chunk)} chars):")
        print("-" * 40)
        print(chunk)
        print("-" * 40)
    
    return merged
def load_config(config_path=None):
    """Loads the configuration from the specified JSON file."""
    if config_path is None:
        config_path = os.path.join("rag_ollama", "config.json")
        print(f"Trying to use configuration file {config_path}")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {config_path}")
        return None

from typing import Dict, Any, Optional, List
import chromadb
import ollama
from logging import getLogger

logger = getLogger(__name__)

class RAGEngineAsync:
    """
    A Retrieval-Augmented Generation engine that combines document retrieval with LLM responses.
    """    
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, database = None):
        """Initialize the RAG engine with the given configuration or load defaults."""
        self.config = self._initialize_config(config)
        self.embedding_model_name = self.config["embedding_model"]
        self.response_model_name = self.config["response_model"]
        self.ollamaAsyncClient = ollama.AsyncClient()
        self._initialize_vector_store(database)
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
        required_fields = ["embedding_model", "response_model"]
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            raise ValueError(f"Configuration missing required fields: {missing_fields}")
            
        return config
    
    def _initialize_vector_store(self, database=None) -> None:
        """Initialize connection to ChromaDB."""
        try:
            if database is None:
                self.chroma_client = chromadb.Client()
            else:                
                self.chroma_client = chromadb.PersistentClient(path=database)
            self.chroma_client.heartbeat()
            self.vectorstore = None  # Initialize actual collection when needed
        except Exception as e:
            raise ConnectionError(f"Failed to initialize ChromaDB: {e}")

    def check_database_status(self):
        """Check if the database has been initialized and contains indexed documents."""
        try:
            collections = self.chroma_client.list_collections()
            
            if not collections:
                return {"status": "empty", "message": "No collections found in database"}
                
            if self.vectorstore is None:
                try:
                    self.vectorstore = self.chroma_client.get_collection("rag_collection")
                except:
                    return {"status": "empty", "message": "Collection 'rag_collection' not found"}
            
            collection_data = self.vectorstore.get()
            num_documents = len(collection_data['ids'])
            
            return {
                "status": "populated" if num_documents > 0 else "empty",
                "num_documents": num_documents,
                "ids": collection_data['ids']
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Error checking database: {str(e)}"}
        
    def _validate_models(self) -> None:
        """Verify availability of required models through Ollama."""
        try:
            models_response = ollama.list()
            available_models = [model.model for model in models_response.models]
            
            self._check_model_availability(self.response_model_name, "response", available_models)
            self._check_model_availability(self.embedding_model_name, "embedding", available_models)
            
        except Exception as e:
            logger.warning(f"Could not verify model availability: {e}")
    
    def _check_model_availability(self, model_name: str, model_type: str, available_models: List[str]) -> None:
        """Check if a specific model is available and log appropriate warnings."""
        if model_name not in available_models:
            logger.warning(
                f"{model_type.capitalize()} model '{model_name}' not found in available models. "
                f"Available models: {', '.join(available_models)}"
            )

    async def _get_embeddings(self, text: str, use_cpu: bool = False) -> List[float]:
        """Generate embeddings for the given text using the Ollama embedding model."""
        options = {"gpu_layers": 0} if use_cpu else {}
        try:
            embeddings_response = await self.ollamaAsyncClient.embeddings(
                model=self.embedding_model_name,
                prompt=text,
                options=options
            )
            
            if embeddings_response and hasattr(embeddings_response, 'embedding'):
                embedding = embeddings_response.embedding
                if isinstance(embedding, list):
                    return [float(x) for x in embedding]
                
            raise ValueError("Invalid embedding format returned from Ollama")
                
        except Exception as e:
            if not use_cpu:
                print(f"Warning: Error getting embeddings: {e}, trying CPU...")
                return await self._get_embeddings(text, use_cpu=True)
            raise e
        
    async def load_and_index_documents(self, documents_path: str,
        metadatas: Optional[List[Dict[str, Any]]] = None):
        """Load documents from file, split into chunks, and index them with metadata."""
        with open(documents_path, "r") as f:
            text = f.read()

        # Split into paragraphs first
        paragraphs = split_into_paragraphs(text)
        
        # Merge short paragraphs to get reasonable chunk sizes
        chunks = merge_short_paragraphs(paragraphs)
        
        print(f"\nCreated {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks):
            print(f"\nChunk {i}:")
            print("-" * 40)
            print(chunk[:100] + "...")  # Print first 100 chars of each chunk
            print("-" * 40)

        if metadatas is not None:
            print(f"\nMetadata provided: {len(metadatas)}")
            print("Metadata contents:")
            for i, meta in enumerate(metadatas):
                print(f"Metadata {i}: {meta}")

        # Generate embeddings for each chunk (do this only once per chunk)
        chunk_embeddings = []
        for chunk in chunks:
            try:
                chunk_embedding = await self._get_embeddings(chunk)
                chunk_embeddings.append(chunk_embedding)
            except Exception as e:
                print(f"Warning: Error embedding chunk: {e}")
                try:
                    chunk_embedding = await self._get_embeddings(chunk, use_cpu=True)
                    chunk_embeddings.append(chunk_embedding)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to embed chunk: {str(e)}")

        if self.vectorstore is None:
            self.vectorstore = self.chroma_client.create_collection(name="rag_collection")

        # If no metadata provided, just store chunks once with empty metadata
        if metadatas is None or not metadatas:
            self.vectorstore.add(
                embeddings=chunk_embeddings,
                documents=chunks,
                ids=[f"doc_{i}" for i in range(len(chunks))]
            )
            return

        # For each chunk, store it multiple times - once for each metadata entry
        all_embeddings = []
        all_documents = []
        all_ids = []
        all_metadatas = []
        
        doc_id = 0
        for i, chunk in enumerate(chunks):
            for j, metadata in enumerate(metadatas):
                all_embeddings.append(chunk_embeddings[i])
                all_documents.append(chunk)
                all_ids.append(f"doc_{doc_id}")
                all_metadatas.append(metadata)
                doc_id += 1

        print(f"\nStoring {len(all_documents)} total entries in database")
        print(f"(Each chunk stored {len(metadatas)} times with different metadata)")

        # Store everything in one batch
        self.vectorstore.add(
            embeddings=all_embeddings,
            documents=all_documents,
            ids=all_ids,
            metadatas=all_metadatas
        )
    
    async def query(self, prompt: str, system_prompt: Optional[str] = None, 
            where: Optional[Dict[str, Any]] = None, **ollama_kwargs: Any) -> Dict[str, Any]:
        """Query the RAG engine with optional metadata filtering."""
        if self.vectorstore is None:
            raise HTTPException(status_code=400, detail="No documents indexed yet. Call /index first.")

        try:
            query_embedding = await self._get_embeddings(prompt)
            
            collection_data = self.vectorstore.get()
            available_docs = len(collection_data['ids'])
            n_results = min(4, available_docs)
            
            query_kwargs = {
                "query_embeddings": query_embedding,
                "n_results": n_results,
                "include": ['documents']
            }
            if where is not None:
                query_kwargs["where"] = where
                
            results = self.vectorstore.query(**query_kwargs)

            if not results or 'documents' not in results or not results['documents']:
                return {"result": "No relevant documents found to answer the query."}

            context = "\n".join(results['documents'][0])

            final_prompt = f"""<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\nContext:\n{context}\n\nQuestion: {prompt}<|im_end|>""" if system_prompt else f"Context:\n{context}\n\nQuestion: {prompt}"

            try:
                response = await self.ollamaAsyncClient.generate(
                    model=self.response_model_name,
                    prompt=final_prompt,
                    **ollama_kwargs
                )
            except Exception as e:
                print(f"Warning: Error with default settings: {e}")
                try:
                    response = await self.ollamaAsyncClient.generate(
                        model=self.response_model_name,
                        prompt=final_prompt,
                        options={"gpu_layers": 0},
                        **ollama_kwargs
                    )
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")

            return {"result": response.get('response', '')}
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during RAG query: {str(e)}")

# In the RAGEngineAsync class, modify the query_structured_async method:

    async def query_structured_async(
        self,
        prompt: str,
        response_model: type[BaseModel],
        system_prompt: Optional[str] = None,
        where: Optional[Dict[str, Any]] = None,
        **ollama_kwargs: Any
    ) -> BaseModel:
        """Queries the RAG engine asynchronously and returns a structured response matching the Pydantic model."""
        if self.vectorstore is None:
            raise HTTPException(status_code=400, detail="No documents indexed yet. Call /index first.")

        try:
            query_embedding = await self._get_embeddings(prompt)
            
            collection_data = self.vectorstore.get()
            available_docs = len(collection_data['ids'])
            n_results = min(4, available_docs)
            
            query_kwargs = {
                "query_embeddings": query_embedding,
                "n_results": n_results,
                "include": ['documents']
            }
            
            if where is not None:
                # Directly use the where clause without additional processing
                query_kwargs["where"] = where

            results = self.vectorstore.query(**query_kwargs)

            if not results or 'documents' not in results or not results['documents']:
                raise HTTPException(status_code=404, detail="No relevant documents found")

            context = "\n".join(results['documents'][0])

            response = await self.ollamaAsyncClient.chat(
                model=self.response_model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': system_prompt if system_prompt else 'You are a helpful assistant. Return your response in the requested JSON format.'
                    },
                    {
                        'role': 'user',
                        'content': f"Context:\n{context}\n\nQuestion: {prompt}"
                    }
                ],
                format=response_model.model_json_schema(),
                options={'temperature': 0.7, **ollama_kwargs}
            )

            structured_response = response_model.model_validate_json(
                response.message.content
            )
            
            return structured_response
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during structured RAG query: {str(e)}")
class RAGEngine:
    def __init__(self, config: Optional[Dict[str, Any]] = None, database = None):
        self.engine = RAGEngineAsync(config=config, database=database)
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
    
    def __del__(self):
        if self._loop and not self._loop.is_closed():
            self._loop.close()

    def _run_async(self, coro):
        """Helper method to run async operations with our managed event loop"""
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

    def load_and_index_documents(self, documents_path: str,
        metadatas: Optional[List[Dict[str, Any]]] = None):
        """Load and index documents synchronously."""
        return self._run_async(self.engine.load_and_index_documents(documents_path, metadatas=metadatas))

    def query(self, prompt: str, system_prompt: Optional[str] = None,
             where: Optional[Dict[str, Any]] = None, **ollama_kwargs: Any) -> Dict[str, Any]:
        """Query synchronously."""
        return self._run_async(self.engine.query(prompt, system_prompt=system_prompt, 
                                               where=where, **ollama_kwargs))

    def query_structured(self, prompt: str, response_model: type[BaseModel], 
                        system_prompt: Optional[str] = None, 
                        where: Optional[Dict[str, Any]] = None,
                        **ollama_kwargs: Any) -> BaseModel:
        """Performs a structured query synchronously."""
        return self._run_async(            
            self.engine.query_structured_async(
                prompt, 
                response_model, 
                system_prompt=system_prompt,
                where=where,
                **ollama_kwargs
            )
        )