import requests
import json
from pydantic import BaseModel
from typing import List, Dict, Any

BASE_URL = "http://localhost:8000"

def get_model_schema(model: type[BaseModel]) -> Dict:
    schema = {}
    for field_name, field in model.model_fields.items():
        field_type = str(field.annotation).replace("typing.", "")
        schema[field_name] = {"type": field_type}
    return schema
    
class Artifact(BaseModel):
    name: str
    description: str
    current_owner: str
    powers: List[str]

class Character(BaseModel):
    name: str
    title: str
    affiliations: List[str]
    key_achievements: List[str]

class Location(BaseModel):
    name: str
    type: str
    significance: str
    key_features: List[str]

class CharacterEvent(BaseModel):
    location: str
    action: str
    outcome: str
    other_characters: List[str]

def call_api(endpoint: str, method: str = 'get', data: Dict = None) -> Dict:
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.post(url, json=data) if method == 'post' else requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {endpoint} - {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        return None

# Initialize
print("\n=== Initializing RAG Engine ===")
init_request = {
    "embedding_model": "nomic-embed-text:latest",
    "response_model": "llama3.2:latest",
    "database": "chromadb"
}
print(call_api("init", "post", init_request))

# Basic lore queries
print("\n=== Basic Lore Queries ===")
queries = [
    "What are the five Ancient Artifacts?",
    "What artifacts exist?",
    "Tell me about the Crystal Guard",
    "What happened in the Great War of the Crystal?",
    "Who is the current ruler and what is their connection to the kingdom's history?"
]

for query in queries:
    print(f"\nQuestion: {query}")
    response = call_api("query", "post", {
        "prompt": query,
        "where": {"section": "lore"},
        "options": {}
    })
    print(f"Answer: {response}")


print("\n=== Character Queries ===")
character_queries = [
    "Who is Queen Aria and what is her role?",
    "Who is Malakai and what did they do?",
    "Who is Thorian and what is their significance?",
    "What did Peter discover recently?"
]

for query in character_queries:
    print(f"\nQuestion: {query}")
    response = call_api("query", "post", {
        "prompt": query,
        "where": {"section": "character"}
    })
    print(f"Answer: {response}")


print("\n=== Structured Queries ===")
crown_query = {
    "prompt": "Tell me about the Crown of Wisdom",
    "model_schema": Artifact.model_json_schema(),
    "where": {"topics": {"$eq": "world;history;artifacts"}},
    "system_prompt": "Extract information about this artifact in a structured format"
}

print("\nArtifact Query:")
print(call_api("query/structured", "post", crown_query))

queen_query = {
    "prompt": "Tell me about Queen Aria and her recent activities",
    "model_schema": Character.model_json_schema(),
    "where": {"characters": "Queen Aria;Peter"}
}
print("\nCharacter Query:")
print(call_api("query/structured", "post", queen_query))

capital_query = {
    "prompt": "Describe Crystal Haven",
    "model_schema": Location.model_json_schema(),
    "where": {"locations": "Crystal Haven"}
}
print("\nLocation Query:")
print(call_api("query/structured", "post", capital_query))

event_query = {
    "prompt": "What happened when Aria and Peter met in the Temple?",
    "model_schema": CharacterEvent.model_json_schema(),
    "where": {"characters": "Peter"}
}
print("\nEvent Query:")
print(call_api("query/structured", "post", event_query))
