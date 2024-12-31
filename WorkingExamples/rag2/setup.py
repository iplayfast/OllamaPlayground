from setuptools import setup, find_packages

setup(
    name="game",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'ollama',
        'chromadb',
        'pydantic'
    ],
)
