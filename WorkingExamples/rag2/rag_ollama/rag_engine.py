# game/rag_ollama/rag_engine.py
import json
import os
from typing import Any, Dict, List, Optional
import ollama
import chromadb
from fastapi import HTTPException

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

class RAGEngine:
    """
    A Retrieval-Augmented Generation engine that combines document retrieval with LLM responses.
    
    This engine uses ChromaDB for vector storage and Ollama for model inference.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the RAG engine with the given configuration or load defaults.
        
        Args:
            config: Optional configuration dictionary with settings for models and retrieval
                   If None, loads from default configuration file
        
        Raises:
            ValueError: If neither provided config nor default config is valid
            ConnectionError: If cannot connect to required services
        """
        self.config = self._initialize_config(config)
        self.embedding_model_name = self.config["embedding_model"]
        self.response_model_name = self.config["response_model"]
        
        # Initialize and validate core services
        self._initialize_vector_store()
        self._validate_models()
    
    def _initialize_config(self, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Load and validate configuration settings."""
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
    
    def _initialize_vector_store(self) -> None:
        """Initialize connection to ChromaDB."""
        try:
            self.chroma_client = chromadb.Client()
            # Test connection by performing a simple operation
            self.chroma_client.heartbeat()
            self.vectorstore = None  # Initialize actual collection when needed
        except Exception as e:
            raise ConnectionError(f"Failed to initialize ChromaDB: {e}")
    
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

    
    def load_and_index_documents(self, documents_path: str):
        """Loads documents from the given path, splits them, and indexes them."""
        with open(documents_path, "r") as f:
            text = f.read()

        # Simple text splitting (you might want more sophisticated methods)
        chunk_size = 1000
        chunk_overlap = 100
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size - chunk_overlap)]

        # Get embeddings for each chunk individually and combine them
        embeddings = []
        for chunk in chunks:
            embedding = self.get_embedding(chunk)
            embeddings.append(embedding)

        # Combine embeddings (you might want to use a more sophisticated method)
        combined_embedding = [sum(x) for x in zip(*embeddings)]

        # Index the document
        self.index_document(combined_embedding, text)

    def get_embedding(self, text: str) -> List[float]:
        """Gets the embedding for the given text using the configured embedding model."""
        # Implement this method using the Ollama API
        raise NotImplementedError

    
    def load_and_index_documents(self, documents_path: str):
        """Loads documents from the given path, splits them, and indexes them."""
        with open(documents_path, "r") as f:
            text = f.read()

        # Simple text splitting (you might want more sophisticated methods)
        chunk_size = 1000
        chunk_overlap = 100
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size - chunk_overlap)]

        # Get embeddings for each chunk individually and combine them
        embeddings = []
        for chunk in chunks:
            try:
                chunk_embedding = self._get_embeddings(chunk)
                embeddings.append(chunk_embedding)
            except Exception as e:
                print(f"Warning: Error embedding chunk: {e}")
                try:
                    # Try again with CPU only
                    chunk_embedding = self._get_embeddings(chunk, use_cpu=True)
                    embeddings.append(chunk_embedding)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to embed chunk: {str(e)}")

        if self.vectorstore is None:
            self.vectorstore = self.chroma_client.create_collection(name="rag_collection")

        self.vectorstore.add(
            embeddings=embeddings,
            documents=chunks,
            ids=[f"doc_{i}" for i in range(len(chunks))]
        )

    def query(self, prompt: str, system_prompt: Optional[str] = None, **ollama_kwargs: Any) -> Dict[str, Any]:
        """Queries the RAG engine with the given prompt."""
        if self.vectorstore is None:
            raise HTTPException(status_code=400, detail="No documents indexed yet. Call /index first.")

        try:
            # Get embeddings for the query
            query_embedding = self._get_embeddings(prompt)
            
            # Get number of available documents
            collection_data = self.vectorstore.get()
            available_docs = len(collection_data['ids'])
            n_results = min(4, available_docs)
            
            # Query the vector store
            results = self.vectorstore.query(
                query_embeddings=query_embedding,  # ChromaDB expects the raw embedding array
                n_results=n_results,
                include=['documents']  # Specify what to include in results
            )

            # Check if we got any results
            if not results or 'documents' not in results or not results['documents']:
                return {"result": "No relevant documents found to answer the query."}

            # Combine context from retrieved documents
            context = "\n".join(results['documents'][0])  # First list contains the actual documents

            # Construct the final prompt
            final_prompt = f"""<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\nContext:\n{context}\n\nQuestion: {prompt}<|im_end|>""" if system_prompt else f"Context:\n{context}\n\nQuestion: {prompt}"

            try:
                # First try with default settings
                response = ollama.generate(
                    model=self.response_model_name,
                    prompt=final_prompt,
                    **ollama_kwargs
                )
            except Exception as e:
                print(f"Warning: Error with default settings: {e}")
                try:
                    # Try again with CPU only
                    response = ollama.generate(
                        model=self.response_model_name,
                        prompt=final_prompt,
                        options={"gpu_layers": 0},  # Force CPU only
                        **ollama_kwargs
                    )
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")

            return {"result": response.get('response', '')}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during RAG query: {str(e)}")

    def _get_embeddings(self, text: str, use_cpu: bool = False) -> List[float]:
        """Gets embeddings for the given text using the configured embedding model.
        
        Args:
            text: The text to generate embeddings for
            use_cpu: If True, forces CPU-only execution
            
        Returns:
            List[float]: The embedding vector
            
        Raises:
            Exception: If embedding generation fails on both GPU and CPU
        """
        options = {"gpu_layers": 0} if use_cpu else {}
        try:
            embeddings_response = ollama.embed(
                model=self.embedding_model_name,
                input=text,
                options=options
            )
            #print(type(embeddings_response))
            # Access the embedding attribute of the EmbedResponse object
            return embeddings_response.embeddings[0]
        except Exception as e:
            if not use_cpu:
                print(f"Warning: Error getting embeddings: {e}, trying CPU...")
                return self._get_embeddings(text, use_cpu=True)
            raise e
        