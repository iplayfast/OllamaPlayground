# ollama_context/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from .engine import ContextEngine, load_config
import logging
import json

# Models for request/response
class InitRequest(BaseModel):
    embedding_model: Optional[str] = None
    response_model: Optional[str] = None
    mode: str = "auto"
    database: Optional[str] = None
    log_level: int = logging.INFO

class ContextRequest(BaseModel):
    name: str
    template: str
    variables: Dict[str, str]

class UpdateContextRequest(BaseModel):
    name: str
    variables: Dict[str, str]

class QueryRequest(BaseModel):
    prompt: str
    context_name: Optional[str] = None
    system_prompt: Optional[str] = None
    where: Optional[Dict[str, Any]] = None
    mode: Optional[str] = None
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)

class StructuredQueryRequest(BaseModel):
    prompt: str
    model_schema: Dict[str, Any]
    context_name: Optional[str] = None
    system_prompt: Optional[str] = None
    where: Optional[Dict[str, Any]] = None
    mode: Optional[str] = None
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)

class IndexRequest(BaseModel):
    documents_path: str
    metadatas: Optional[List[Dict[str, Any]]] = None

# Global engine instance
engine: Optional[ContextEngine] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the API lifecycle."""
    yield
    if engine:
        await engine.cleanup()

# Create FastAPI app with lifespan management
app = FastAPI(lifespan=lifespan)

@app.post("/init")
async def initialize_engine(request: InitRequest):
    """Initialize the context engine with specified configuration."""
    global engine
    
    config = load_config()
    if request.embedding_model:
        config["embedding_model"] = request.embedding_model
    if request.response_model:
        config["response_model"] = request.response_model
        
    try:
        engine = ContextEngine(
            config=config,
            mode=request.mode,
            log_level=request.log_level,
            database=request.database
        )
        return {"status": "initialized", "config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")

@app.post("/index")
async def index_documents(request: IndexRequest):
    """Index documents with optional metadata."""
    if not engine:
        raise HTTPException(status_code=400, detail="Engine not initialized")
    
    try:
        await engine.engine.index_documents(
            request.documents_path,
            metadatas=request.metadatas
        )
        return {"status": "success", "message": "Documents indexed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

@app.post("/context/register")
async def register_context(request: ContextRequest):
    """Register a new context template."""
    if not engine:
        raise HTTPException(status_code=400, detail="Engine not initialized")
    
    try:
        engine.register_context(
            request.name,
            request.template,
            request.variables
        )
        return {"status": "success", "message": f"Context '{request.name}' registered"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context registration failed: {str(e)}")

@app.post("/context/update")
async def update_context(request: UpdateContextRequest):
    """Update variables for an existing context."""
    if not engine:
        raise HTTPException(status_code=400, detail="Engine not initialized")
    
    try:
        engine.update_context_variables(
            request.name,
            request.variables
        )
        return {"status": "success", "message": f"Context '{request.name}' updated"}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Context '{request.name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context update failed: {str(e)}")

@app.post("/query")
async def query(request: QueryRequest):
    """Generate a response using the context engine."""
    if not engine:
        raise HTTPException(status_code=400, detail="Engine not initialized")
    
    try:
        response = await engine.engine.query(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            context_name=request.context_name,
            where=request.where,
            mode=request.mode,
            **request.options
        )
        return response
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.post("/query/structured")
async def query_structured(request: StructuredQueryRequest):
    """Generate a structured response using the context engine."""
    if not engine:
        raise HTTPException(status_code=400, detail="Engine not initialized")
    
    try:
        # Create a base Pydantic model class with the schema
        class DynamicResponseModel(BaseModel):
            model_config = {
                "extra": "allow",
                "json_schema_extra": request.model_schema
            }
            
            @classmethod
            def model_json_schema(cls):
                return request.model_schema
        
        response = await engine.engine.query_structured(
            prompt=request.prompt,
            response_model=DynamicResponseModel,
            context_name=request.context_name,
            system_prompt=request.system_prompt,
            where=request.where,
            mode=request.mode,
            **request.options
        )
        
        # Convert to dict and return
        return json.loads(response.model_dump_json())
        
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Structured query failed: {str(e)}")

@app.get("/status")
async def get_status():
    """Get the current status of the engine."""
    if not engine:
        return {"status": "uninitialized"}
    
    try:
        db_status = engine.check_database_status()
        contexts = list(engine.engine.contexts.keys()) if hasattr(engine.engine, 'contexts') else []
        
        return {
            "status": "running",
            "mode": engine.engine.mode,
            "database": db_status,
            "registered_contexts": contexts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
