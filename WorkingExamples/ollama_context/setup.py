from setuptools import setup, find_packages

setup(
    name="ollama_context",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "ollama",
        "chromadb",
        "pydantic",
        "nest_asyncio"
    ],
)
