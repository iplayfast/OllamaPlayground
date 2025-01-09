# game/run_api.py
import uvicorn
import argparse
import logging
from ollama_context.api import app

def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run the RAG API server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')
    return parser.parse_args()

def main():
    """Main entry point for running the API server."""
    setup_logging()
    args = parse_arguments()
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting server on {args.host}:{args.port}")
    
    try:
 
        uvicorn.run(
            "ollama_context.api:app",  # Changed from rag_ollama.api:app
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers,
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == "__main__":
    main()
