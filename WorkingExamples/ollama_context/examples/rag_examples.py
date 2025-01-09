# rag_example.py
from ollama_context import ContextEngine
from pydantic import BaseModel
from typing import List
import logging

# Define Pydantic models for structured responses
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

def main():
    # Initialize the engine with correct settings
    engine = ContextEngine(
        mode="retrieval",
        database="examples/chromadb",
        log_level=logging.ERROR
    )
    
    # Check database status
    status = engine.check_database_status()
    
    if status['status'] != 'populated':   
        # Create and load game lore
        game_lore = """
        The Kingdom of Eldara is a vast realm filled with ancient magic and mysterious creatures. 
        The capital city, Crystal Haven, is built upon the ruins of an ancient civilization.
        
        The Great War of the Crystal happened 1000 years ago, when the Dark Sorcerer Malakai 
        attempted to steal the Sacred Crystal from the Temple of Light. The Crystal's power was 
        said to grant immortality, but its true purpose was to maintain the balance between the 
        realms of light and shadow.
        
        The current ruler, Queen Aria, is a descendant of the legendary hero Thorian who defeated 
        Malakai. She possesses the Crown of Wisdom, one of the five Ancient Artifacts. The other 
        artifacts are: the Shield of Dawn, the Sword of Twilight, the Staff of Seasons, and the 
        Amulet of Dreams.
        
        The kingdom is protected by an elite group of warriors known as the Crystal Guard. Each 
        member of the Guard undergoes rigorous training in both combat and magical arts at the 
        Academy of Light and Shadow.

        Recently, Queen Aria discovered ancient scrolls in the Temple of Light library.
        While studying these scrolls, she encountered Peter, a young Crystal Guard scholar.
        Together, they uncovered evidence that the Crown of Wisdom and Shield of Dawn were created as a pair.
        Their research was interrupted by shadowy creatures, but Peter defended them using light magic.
        """
        
        # Save the stories to a file
        with open("game_lore.txt", "w") as f:
            f.write(game_lore)
            
        # Create metadata for the chunks
        metadatas = [
            {
                "section": "character",
                "topics": "world;history;artifacts"
            },
            {
                "section": "lore",
                "topics": "world;history;artifacts"
            },
            {
                "section": "events",
                "topics": "recent_events"
            }
        ]
    
        # Index the documents with metadata
        engine.load_and_index_documents("game_lore.txt", metadatas=metadatas)
    
    try:
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
            response = engine.query(query, where={"section": "lore"})
            print(f"Answer: {response['result']}")
            print("-" * 80)

        print("\n=== Character Queries ===")
        character_queries = [
            "Who is Queen Aria and what is her role?",
            "Who is Malakai and what did they do?",
            "Who is Thorian and what is their significance?",
            "What did Peter discover recently?"
        ]

        for query in character_queries:
            print(f"\nQuestion: {query}")
            response = engine.query(query, where={"section": "character"})
            print(f"Answer: {response['result']}")
            print("-" * 80)

        # Structured queries for world information
        print("\n=== World Information ===")
        
        # Get information about an artifact
        crown = engine.query_structured(
            prompt="Tell me about the Crown of Wisdom",
            response_model=Artifact,
            system_prompt="Extract information about this artifact in a structured format",
            where={"topics": {"$eq": "world;history;artifacts"}}
        )
        print("\nArtifact Information:")
        print(f"Name: {crown.name}")
        print(f"Description: {crown.description}")
        print(f"Current Owner: {crown.current_owner}")
        print(f"Powers: {', '.join(crown.powers)}")
        print("-" * 80)

        # Get character information with recent events
        queen = engine.query_structured(
            prompt="Tell me about Queen Aria and her recent activities",
            response_model=Character,
            system_prompt="Extract information about this character in a structured format",
            where={"characters": "Queen Aria;Peter"}
        )
        print("\nCharacter Information:")
        print(f"Name: {queen.name}")
        print(f"Title: {queen.title}")
        print(f"Affiliations: {', '.join(queen.affiliations)}")
        print(f"Key Achievements: {', '.join(queen.key_achievements)}")
        print("-" * 80)

        # Get location information
        capital = engine.query_structured(
            prompt="Describe Crystal Haven",
            response_model=Location,
            system_prompt="Extract information about this location in a structured format",
            where={"locations": "Crystal Haven"}
        )
        print("\nLocation Information:")
        print(f"Name: {capital.name}")
        print(f"Type: {capital.type}")
        print(f"Significance: {capital.significance}")
        print(f"Key Features: {', '.join(capital.key_features)}")
        print("-" * 80)

        # Query recent character events
        print("\n=== Recent Events ===")
        event = engine.query_structured(
            prompt="What happened when Aria and Peter met in the Temple?",
            response_model=CharacterEvent,
            where={"characters": "Peter"}
        )
        print("\nRecent Event:")
        print(f"Location: {event.location}")
        print(f"Action: {event.action}")
        print(f"Outcome: {event.outcome}")
        print(f"Characters Involved: {', '.join(event.other_characters)}")

    finally:
        # Ensure proper cleanup
        del engine

if __name__ == "__main__":
    main()
