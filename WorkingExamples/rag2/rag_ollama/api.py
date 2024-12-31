# game/rag_ollama/api.py
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from game.rag_ollama.rag_engine import RAGEngine, load_config  # Import from the correct location

app = FastAPI()
rag_engine = None

# --- Request Models ---
class InitRequest(BaseModel):
    embedding_model: str
    response_model: str

class IndexRequest(BaseModel):
    documents_path: str

class QueryRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    options: Optional[Dict[str, Any]] = {}  # For other Ollama parameters

@app.post("/init")
async def initialize_rag(request_body: InitRequest):
    """Initializes the RAG engine with the configuration."""
    global rag_engine
    try:
        config = load_config()
        if config:
            rag_engine = RAGEngine(config)
            # You can also pass the config directly if you prefer:
            # rag_engine = RAGEngine(request_body.dict())
            return {"message": "RAG engine initialized."}
        else:
            raise HTTPException(status_code=500, detail="Failed to load configuration.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing RAG engine: {str(e)}")

@app.post("/index")
async def index_documents(request_body: IndexRequest):
    """Loads and indexes documents from the specified path."""
    global rag_engine
    if not rag_engine:
        raise HTTPException(status_code=400, detail="RAG engine not initialized. Call /init first.")
    try:
        rag_engine.load_and_index_documents(request_body.documents_path)
        return {"message": f"Documents indexed from {request_body.documents_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing documents: {str(e)}")

@app.post("/query")
async def query_rag(request_body: QueryRequest):
    """Queries the RAG engine."""
    global rag_engine
    if not rag_engine:
        raise HTTPException(status_code=400, detail="RAG engine not initialized. Call /init first.")

    try:
        result = rag_engine.query(
            request_body.prompt,
            request_body.system_prompt,
            **request_body.options
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during query: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)