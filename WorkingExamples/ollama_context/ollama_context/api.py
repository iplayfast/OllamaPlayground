# ollama_context/api.py
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, create_model

from .engine import ContextEngine, load_config

# Request Models
class InitRequest(BaseModel):
    embedding_model: Optional[str] = None
    response_model: Optional[str] = None
    mode: Optional[str] = "auto"
    database: Optional[str] = None
    log_level: Optional[int] = None
    enable_http_logs: Optional[bool] = None

class DatabaseStatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
    num_documents: Optional[int] = None
    contexts: Optional[List[str]] = None

class ContextTemplate(BaseModel):
    template: str
    variables: Dict[str, str]

class RegisterContextRequest(BaseModel):
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
    options: Optional[Dict[str, Any]] = {}
    mode: Optional[str] = None
    model_schema: Optional[Dict[str, Any]] = None

class IndexRequest(BaseModel):
    documents_path: str
    metadatas: Optional[List[Dict[str, Any]]] = None

app = FastAPI(title="Context API", description="API for Context-Enhanced Generation using Ollama")
context_engine = None

@app.post("/init")
async def initialize_engine(request_body: InitRequest):
    """Initialize the context engine with specified configuration."""
    global context_engine
    try:
        config = load_config()
        if request_body.embedding_model:
            config["embedding_model"] = request_body.embedding_model
        if request_body.response_model:
            config["response_model"] = request_body.response_model
            
        context_engine = ContextEngine(
            config=config,
            mode=request_body.mode,
            log_level=request_body.log_level,
            enable_http_logs=request_body.enable_http_logs,
            database=request_body.database
        )
        return {"status": "success", "message": "Context engine initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status", response_model=DatabaseStatusResponse)
async def check_status():
    """Check status of the engine, including documents and contexts."""
    if not context_engine:
        raise HTTPException(status_code=400, detail="Context engine not initialized")
    
    try:
        # Get vectorstore status if available
        if hasattr(context_engine.engine, 'vectorstore'):
            collection_data = context_engine.engine.vectorstore.get() if context_engine.engine.vectorstore else None
            num_documents = len(collection_data['ids']) if collection_data else 0
        else:
            num_documents = 0
            
        # Get registered contexts if available
        contexts = list(context_engine.engine.contexts.keys()) if hasattr(context_engine.engine, 'contexts') else []
        
        return {
            "status": "active",
            "num_documents": num_documents,
            "contexts": contexts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/index")
async def index_documents(request_body: IndexRequest):
    """Index documents for retrieval."""
    if not context_engine:
        raise HTTPException(status_code=400, detail="Context engine not initialized")
    
    try:
        context_engine.load_and_index_documents(
            request_body.documents_path,
            request_body.metadatas
        )
        return {"status": "success", "message": "Documents indexed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/context/register")
async def register_context(request_body: RegisterContextRequest):
    """Register a new context template."""
    if not context_engine:
        raise HTTPException(status_code=400, detail="Context engine not initialized")
    
    try:
        context_engine.register_context(
            request_body.name,
            request_body.template,
            request_body.variables
        )
        return {
            "status": "success",
            "message": f"Context '{request_body.name}' registered successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/context/update")
async def update_context(request_body: UpdateContextRequest):
    """Update variables for an existing context."""
    if not context_engine:
        raise HTTPException(status_code=400, detail="Context engine not initialized")
    
    try:
        context_engine.update_context_variables(
            request_body.name,
            request_body.variables
        )
        return {
            "status": "success",
            "message": f"Context '{request_body.name}' updated successfully"
        }
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Context '{request_body.name}' not found"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query(request_body: QueryRequest):
    """Generate a response using the specified context and/or retrieved documents."""
    if not context_engine:
        raise HTTPException(status_code=400, detail="Context engine not initialized")
    
    try:
        # Use the engine's async methods directly
        result = await context_engine.engine.query(
            prompt=request_body.prompt,
            context_name=request_body.context_name,
            system_prompt=request_body.system_prompt,
            where=request_body.where,
            mode=request_body.mode,
            **request_body.options
        )
        return result
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/structured")
async def query_structured(request_body: QueryRequest):
    """Generate a structured response using the specified context and/or retrieved documents."""
    if not request_body.model_schema:
        raise HTTPException(status_code=400, detail="model_schema is required")
    
    if not context_engine:
        raise HTTPException(status_code=400, detail="Context engine not initialized")
    
    try:
        schema = request_body.model_schema
        properties = schema.get('properties', {})
        
        type_mapping = {
            'string': str,
            'array': List[str] if schema.get('items', {}).get('type') == 'string' else List
        }
        
        model_fields = {
            field: (type_mapping[props['type']], ...) 
            for field, props in properties.items()
        }
        
        DynamicModel = create_model('DynamicModel', **model_fields)
        
        # Use the engine's async methods directly
        result = await context_engine.engine.query_structured_async(
            prompt=request_body.prompt,
            response_model=DynamicModel,
            context_name=request_body.context_name,
            system_prompt=request_body.system_prompt,
            where=request_body.where,
            mode=request_body.mode,
            **request_body.options
        )
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/index")
async def index_documents(request_body: IndexRequest):
    """Index documents for retrieval."""
    if not context_engine:
        raise HTTPException(status_code=400, detail="Context engine not initialized")
    
    try:
        # Use the engine's async methods directly
        await context_engine.engine.index_documents(
            request_body.documents_path,
            request_body.metadatas
        )
        return {"status": "success", "message": "Documents indexed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
