import uvicorn
import argparse
import logging
import asyncio
import signal
import os
from typing import Any

def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run the Context API server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')
    return parser.parse_args()

async def run_server(host: str, port: int, reload: bool, workers: int):
    """Run the Uvicorn server."""
    config = uvicorn.Config(
        "ollama_context.api:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        loop="asyncio"
    )
    server = uvicorn.Server(config)
    await server.serve()

def force_exit(signal_name: str):
    """Forcefully exit the program."""
    logger = logging.getLogger(__name__)
    logger.warning(f"Forcefully exiting on signal: {signal_name}")
    os._exit(0)

def main():
    """Main entry point for running the API server."""
    setup_logging()
    args = parse_arguments()

    logger = logging.getLogger(__name__)
    logger.info(f"Starting server on {args.host}:{args.port}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Register signal handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: force_exit(signal.Signals(s).name))

    try:
        loop.run_until_complete(run_server(args.host, args.port, args.reload, args.workers))
    finally:
        logger.info("Cleaning up resources")
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        logger.info("Server shutdown complete")

if __name__ == "__main__":
    main()

