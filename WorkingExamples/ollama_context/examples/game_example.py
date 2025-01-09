# examples/game_example.py
from ollama_context import ContextEngine
from pydantic import BaseModel
from typing import List, Optional
import logging

class GameCharacter(BaseModel):
    name: str
    role: str
    level: int
    health: int
    abilities: list[str]
    inventory: list[str]
    status_effects: Optional[list[str]] = []

class GameLocation(BaseModel):
    name: str
    description: str
    available_actions: list[str]
    npcs_present: list[str]
    items_present: list[str]

class GameAction(BaseModel):
    action: str
    target: str
    result: str
    consequences: list[str]

def main():
    # Initialize engine with both RAG and CAG capabilities
    engine = ContextEngine(
        mode="combined",
        log_level=logging.INFO,
        database="examples/game_db"
    )
    
    # Game world lore and rules
    game_world = """
    The Realm of Mystara is a land of ancient magic and forgotten secrets.
    The world operates on these fundamental rules:
    1. Characters can interact with objects, NPCs, and the environment
    2. Actions have consequences that affect the game state
    3. Combat uses a turn-based system with initiative
    4. Magic requires mana and proper training
    5. Items can be collected, used, and combined
    
    Locations in the world:
    - The Whispering Woods: A mysterious forest with ancient secrets
    - Crystal Haven: The central city and trading hub
    - The Mage's Academy: Where magic is studied and taught
    - The Dark Caves: Dangerous dungeons filled with treasures
    
    Available character classes:
    - Warrior: Specializes in combat and protection
    - Mage: Masters of arcane magic
    - Rogue: Experts in stealth and subterfuge
    - Healer: Skilled in restoration magic
    """
    
    # Save world data
    with open("examples/game_world.txt", "w") as f:
        f.write(game_world)
    
    # Index game world data with different section metadata
    engine.load_and_index_documents(
        "examples/game_world.txt",
        metadatas=[
            {"section": "rules"},
            {"section": "locations"},
            {"section": "classes"}
        ]
    )
    
    # Register character templates
    player_template = """
    Name: {name}
    Class: {class_type}
    Level: {level}
    Background: {background}
    Personality: {personality}
    Current Quest: {current_quest}
    """
    
    npc_template = """
    Name: {name}
    Role: {role}
    Location: {location}
    Knowledge: {knowledge}
    Attitude: {attitude}
    Quests Available: {quests}
    """
    
    # Create player character
    player_vars = {
        "name": "Aether",
        "class_type": "Mage",
        "level": "5",
        "background": "Promising student at the Mage's Academy",
        "personality": "Curious and determined",
        "current_quest": "Investigate strange energies in the Whispering Woods"
    }
    
    # Create NPC
    mentor_vars = {
        "name": "Arch-Mage Thorn",
        "role": "Academy Mentor",
        "location": "Mage's Academy",
        "knowledge": "Expert in energy anomalies and ancient magic",
        "attitude": "Wise and concerned about recent events",
        "quests": "Investigate the Whispering Woods"
    }
    
    # Register contexts
    engine.register_context("player", player_template, player_vars)
    engine.register_context("mentor", npc_template, mentor_vars)
    
    try:
        # Example 1: Get character information
        print("\n=== Character Information ===")
        char_info = engine.query_structured(
            prompt="Tell me about the player character",
            response_model=GameCharacter,
            context_name="player"
        )
        print(f"Character: {char_info.name}")
        print(f"Role: {char_info.role}")
        print(f"Level: {char_info.level}")
        print(f"Abilities: {', '.join(char_info.abilities)}")
        
        # Example 2: Get location information using RAG
        print("\n=== Location Information ===")
        location_info = engine.query_structured(
            prompt="Describe the Whispering Woods",
            response_model=GameLocation,
            where={"section": "locations"}
        )
        print(f"Location: {location_info.name}")
        print(f"Description: {location_info.description}")
        print(f"Available Actions: {', '.join(location_info.available_actions)}")
        
        # Example 3: Character interaction using combined mode
        print("\n=== Character Interaction ===")
        dialogue = engine.query(
            prompt="Ask the mentor about the strange energies in the woods",
            context_name="mentor",
            where={"section": "locations"},
            mode="combined"
        )
        print(f"Mentor's Response: {dialogue['result']}")
        
        # Example 4: Process game action
        print("\n=== Game Action ===")
        action_result = engine.query_structured(
            prompt="Cast a detection spell to investigate the strange energies",
            response_model=GameAction,
            context_name="player",
            where={"section": "rules"},
            mode="combined"
        )
        print(f"Action: {action_result.action}")
        print(f"Result: {action_result.result}")
        print(f"Consequences: {', '.join(action_result.consequences)}")

    finally:
        # Ensure proper cleanup
        del engine

if __name__ == "__main__":
    main()