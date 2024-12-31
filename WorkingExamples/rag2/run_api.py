# game/run_api.py
import uvicorn
from game.rag_ollama.api import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

