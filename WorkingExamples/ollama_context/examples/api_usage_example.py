# examples/api_usage_example.py
import requests
import json
from typing import List, Dict, Any

BASE_URL = "http://localhost:8000"

def call_api(endpoint: str, method: str = 'get', data: Dict = None) -> Dict:
    """Make API calls and handle responses."""
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.post(url, json=data) if method == 'post' else requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {endpoint} - {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return None

def main():
    # Initialize the engine
    print("\n=== Initializing Engine ===")
    init_request = {
        "embedding_model": "nomic-embed-text:latest",
        "response_model": "llama3.2:latest",
        "mode": "auto",
        "database": "combined_db",
        "log_level": 50  # CRITICAL - minimal logging
    }
    print(call_api("init", "post", init_request))

    # Index some documents
    print("\n=== Indexing Documents ===")
    game_lore = """
    The Kingdom of Eldara is a realm of ancient magic and mystery.
    The Crystal Guard protects its borders, trained in both martial and magical arts.
    Ancient artifacts of power are scattered throughout the land, each with its own history.
    
    The Great War of the Crystal happened 1000 years ago, when the Dark Sorcerer Malakai 
    attempted to steal the Sacred Crystal. The Crystal's power was said to grant immortality, 
    but its true purpose was to maintain the balance between realms.
    
    Today, Queen Aria rules from the Crystal Throne, guided by ancient wisdom.
    The Academy of Light and Shadow trains new guardians in both martial and magical arts.
    """
    
    with open("game_lore.txt", "w") as f:
        f.write(game_lore)

    index_request = {
        "documents_path": "game_lore.txt",
        "metadatas": [
            {"section": "lore", "topic": "world"},
            {"section": "lore", "topic": "characters"}
        ]
    }
    print(call_api("index", "post", index_request))

    # Register character context
    print("\n=== Registering Character Context ===")
    character_context = {
        "name": "wizard",
        "template": (
            "Character Name: {name}\n"
            "Role: {role}\n"
            "Background: {background}\n"
            "Personality: {personality}\n"
            "Speaking Style: {speaking_style}"
        ),
        "variables": {
            "name": "Eldric the Wise",
            "role": "Senior Crystal Guard",
            "background": "Former battle-mage, now instructor",
            "personality": "Wise and patient, but strict",
            "speaking_style": "Formal and precise"
        }
    }
    print(call_api("context/register", "post", character_context))

    # Check status
    print("\n=== Checking Engine Status ===")
    print(call_api("status"))

    # Example 1: RAG-based query
    print("\n=== RAG Query ===")
    rag_request = {
        "prompt": "Tell me about the Crystal Guard",
        "where": {"section": "lore"},
        "mode": "retrieval"
    }
    rag_response = call_api("query", "post", rag_request)
    if rag_response:
        print(f"Response: {rag_response['result']}\n")

    # Example 2: CAG-based character response
    print("\n=== CAG Query ===")
    cag_request = {
        "prompt": "What do you think about training new guards?",
        "context_name": "wizard",
        "mode": "context"
    }
    cag_response = call_api("query", "post", cag_request)
    if cag_response:
        print(f"Response: {cag_response['result']}\n")

    # Example 3: Update character context
    print("\n=== Updating Context ===")
    update_request = {
        "name": "wizard",
        "variables": {
            "background": "Recently discovered ancient texts about guard training",
            "personality": "More excited about new discoveries"
        }
    }
    print(call_api("context/update", "post", update_request))

    # Example 4: Combined mode query
    print("\n=== Combined Query ===")
    combined_request = {
        "prompt": "Share your knowledge about the history of the Crystal Guard",
        "context_name": "wizard",
        "where": {"section": "lore"},
        "mode": "combined"
    }
    combined_response = call_api("query", "post", combined_request)
    if combined_response:
        print(f"Response: {combined_response['result']}\n")

    # Example 5: Structured artifact query
    print("\n=== Structured Artifact Query ===")
    artifact_schema = {
        "title": "Artifact",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "description": {"type": "string"},
            "current_owner": {"type": "string"},
            "powers": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["name", "description", "current_owner", "powers"]
    }
    
    artifact_request = {
        "prompt": "Tell me about the Sacred Crystal",
        "model_schema": artifact_schema,
        "where": {"topic": "world"},
        "mode": "retrieval",
        "system_prompt": "Extract information about this magical artifact in a structured format"
    }
    artifact_info = call_api("query/structured", "post", artifact_request)
    if artifact_info:
        print("\nArtifact Information:")
        print(f"Name: {artifact_info['name']}")
        print(f"Description: {artifact_info['description']}")
        print(f"Current Owner: {artifact_info['current_owner']}")
        print(f"Powers: {', '.join(artifact_info['powers'])}")

    # Example 6: Structured character query
    print("\n=== Structured Character Query ===")
    character_schema = {
        "title": "Character",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "role": {"type": "string"},
            "personality": {"type": "string"},
            "key_traits": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["name", "role", "personality", "key_traits"]
    }
    
    character_request = {
        "prompt": "Tell me about yourself and your role as a Crystal Guard",
        "model_schema": character_schema,
        "context_name": "wizard",
        "mode": "context",
        "system_prompt": "Extract character information in a structured format"
    }
    character_info = call_api("query/structured", "post", character_request)
    if character_info:
        print("\nCharacter Information:")
        print(f"Name: {character_info['name']}")
        print(f"Role: {character_info['role']}")
        print(f"Personality: {character_info['personality']}")
        print(f"Key Traits: {', '.join(character_info['key_traits'])}")

    # Example 7: Structured query with combined mode
    print("\n=== Structured Combined Query ===")
    dialogue_schema = {
        "title": "DialogueResponse",
        "type": "object",
        "properties": {
            "speaker": {"type": "string"},
            "dialogue": {"type": "string"},
            "emotion": {"type": "string"},
            "actions": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["speaker", "dialogue", "emotion", "actions"]
    }
    
    dialogue_request = {
        "prompt": "How do you respond to a student asking about the Great War of the Crystal?",
        "model_schema": dialogue_schema,
        "context_name": "wizard",
        "where": {"section": "lore"},
        "mode": "combined",
        "system_prompt": "Generate a dialogue response with actions and emotion"
    }
    dialogue = call_api("query/structured", "post", dialogue_request)
    if dialogue:
        print("\nDialogue Response:")
        print(f"Speaker: {dialogue['speaker']}")
        print(f"Dialogue: {dialogue['dialogue']}")
        print(f"Emotion: {dialogue['emotion']}")
        print(f"Actions: {', '.join(dialogue['actions'])}")

    # Example 8: Query about specific character
    print("\n=== Character History Query ===")
    character_query = {
        "prompt": "Tell me about Queen Aria and her connection to the kingdom",
        "where": {"topic": "characters"},
        "mode": "retrieval"
    }
    character_response = call_api("query", "post", character_query)
    if character_response:
        print(f"Response: {character_response['result']}\n")

if __name__ == "__main__":
    main()
