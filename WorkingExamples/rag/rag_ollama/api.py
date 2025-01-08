import asyncio


from typing import Any, Dict, Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, create_model

from .rag_engine import RAGEngine, load_config

# Request Models
class InitRequest(BaseModel):
    embedding_model: Optional[str] = None
    response_model: Optional[str] = None
    database: Optional[str] = None

class DatabaseStatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
    num_documents: Optional[int] = None
    ids: Optional[List[str]] = None

class QueryRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    where: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = {}
    model_schema: Optional[Dict[str, Any]] = None

class IndexRequest(BaseModel):
    documents_path: str
    metadatas: Optional[List[Dict[str, Any]]] = None

app = FastAPI(title="RAG API", description="API for RAG using Ollama")
rag_engine = None

@app.post("/init")
async def initialize_rag(request_body: InitRequest):
    global rag_engine
    try:
        config = load_config()
        if request_body.embedding_model:
            config["embedding_model"] = request_body.embedding_model
        if request_body.response_model:
            config["response_model"] = request_body.response_model
            
        rag_engine = RAGEngine(config=config, database=request_body.database)
        return {"status": "success", "message": "RAG engine initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status", response_model=DatabaseStatusResponse)
async def check_status():
    if not rag_engine:
        raise HTTPException(status_code=400, detail="RAG engine not initialized")
    return rag_engine.check_database_status()

@app.post("/index")
async def index_documents(request_body: IndexRequest):
    if not rag_engine:
        raise HTTPException(status_code=400, detail="RAG engine not initialized")
    try:
        rag_engine.load_and_index_documents(request_body.documents_path, request_body.metadatas)
        return {"status": "success", "message": "Documents indexed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# rag_ollama/api.py
@app.post("/query")
async def query(request_body: QueryRequest):    
    if not rag_engine:
        raise HTTPException(status_code=400, detail="RAG engine not initialized")
    try:
        status = rag_engine.check_database_status()
        loop = asyncio.get_running_loop()
        result = await rag_engine.engine.query(
            prompt=request_body.prompt,
            system_prompt=request_body.system_prompt,
            where=request_body.where,
            **request_body.options
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/structured")
async def query_structured(request_body: QueryRequest):
    if not request_body.model_schema:
        raise HTTPException(status_code=400, detail="model_schema is required")
    if not rag_engine:
        raise HTTPException(status_code=400, detail="RAG engine not initialized")
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
        loop = asyncio.get_running_loop()
        result = await rag_engine.engine.query_structured_async(
            prompt=request_body.prompt,
            response_model=DynamicModel,
            system_prompt=request_body.system_prompt,
            where=request_body.where,
            **request_body.options
        )
        return result.model_dump()
    except Exception as e:
        print(f"Structured query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
