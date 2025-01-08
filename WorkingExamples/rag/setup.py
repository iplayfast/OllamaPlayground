from setuptools import setup, find_packages

setup(
    name="rag_ollama",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'uvicorn',
        'ollama',
        'chromadb',
        'pydantic',
        'requests',
        'nest_asyncio'
    ],
)
