# examples/documentation_example.py
from ollama_context import ContextEngine
from pydantic import BaseModel
from typing import List, Dict
import logging

class APIEndpoint(BaseModel):
    path: str
    method: str
    description: str
    parameters: List[Dict[str, str]]
    response: Dict[str, str]
    examples: List[Dict[str, str]]

class DocumentationSection(BaseModel):
    title: str
    content: str
    code_examples: List[str]
    see_also: List[str]

def main():
    # Initialize engine
    engine = ContextEngine(
        mode="auto",
        log_level=logging.INFO,
        database="examples/docs_db"
    )
    
    # Technical documentation content
    api_docs = """
    REST API Documentation
    
    Authentication:
    All requests must include an API key in the header:
    X-API-Key: your_api_key_here
    
    Endpoints:
    
    POST /api/v1/analyze
    Analyzes text content using machine learning models.
    Parameters:
    - text (required): The content to analyze
    - model (optional): Specific model to use
    - language (optional): Content language
    
    GET /api/v1/models
    Lists available machine learning models.
    Parameters:
    - type (optional): Filter by model type
    - status (optional): Filter by model status
    
    Error Handling:
    - 400: Bad Request
    - 401: Unauthorized
    - 403: Forbidden
    - 404: Not Found
    - 500: Internal Server Error
    """
    
    # Save documentation
    with open("examples/api_docs.txt", "w") as f:
        f.write(api_docs)
    
    # Index documentation with metadata
    engine.load_and_index_documents(
        "examples/api_docs.txt",
        metadatas=[
            {"section": "authentication"},
            {"section": "endpoints"},
            {"section": "errors"}
        ]
    )
    
    # Register documentation style templates
    endpoint_template = """
    Endpoint Template:
    Path: {path}
    Method: {method}
    Description: {description}
    Auth Required: {auth_required}
    Response Format: {response_format}
    Style Guide:
    - Use clear, concise descriptions
    - Include request/response examples
    - List all parameters
    - Document error cases
    """
    
    guide_template = """
    Documentation Style:
    Tone: {tone}
    Target Audience: {audience}
    Technical Level: {tech_level}
    Include:
    - Clear explanations
    - Code examples
    - Common use cases
    - Troubleshooting tips
    """
    
    # Register contexts with variables
    endpoint_vars = {
        "path": "/api/v1/analyze",
        "method": "POST",
        "description": "Text analysis endpoint",
        "auth_required": "Yes",
        "response_format": "JSON"
    }
    
    guide_vars = {
        "tone": "Professional and clear",
        "audience": "Software developers",
        "tech_level": "Intermediate to advanced"
    }
    
    engine.register_context("endpoint", endpoint_template, endpoint_vars)
    engine.register_context("guide", guide_template, guide_vars)
    
    # Example 1: Generate endpoint documentation
    print("\n=== Endpoint Documentation ===")
    endpoint_doc = engine.query_structured(
        prompt="Document the text analysis endpoint",
        response_model=APIEndpoint,
        context_name="endpoint",
        where={"section": "endpoints"},
        mode="combined"
    )
    print(f"Endpoint: {endpoint_doc.path}")
    print(f"Description: {endpoint_doc.description}")
    print("Parameters:")
    for param in endpoint_doc.parameters:
        print(f"- {param['name']}: {param['description']}")
    
    # Example 2: Generate documentation section
    print("\n=== Documentation Section ===")
    auth_doc = engine.query_structured(
        prompt="Explain the authentication process",
        response_model=DocumentationSection,
        context_name="guide",
        where={"section": "authentication"},
        mode="combined"
    )
    print(f"Title: {auth_doc.title}")
    print(f"Content: {auth_doc.content}")
    print("Code Examples:")
    for example in auth_doc.code_examples:
        print(f"\n{example}")
    
    # Example 3: Generate error handling documentation
    print("\n=== Error Handling ===")
    error_doc = engine.query(
        prompt="Document error responses",
        context_name="guide",
        where={"section": "errors"}
    )
    print(error_doc['result'])

if __name__ == "__main__":
    main()
