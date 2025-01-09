# examples/basic_usage_example.py
from ollama_context import ContextEngine
from pydantic import BaseModel
from typing import List
import logging

# Define models for structured output
class Character(BaseModel):
    name: str
    role: str
    personality: str
    key_traits: List[str]
    background_knowledge: List[str]

def main():
    # Initialize engine in auto mode
    engine = ContextEngine(
        mode="auto",
        log_level=logging.INFO,
        database="examples/example_db"
    )
    
    # Example game lore for RAG
    game_lore = """
    The Kingdom of Eldara is a realm of ancient magic and mystery. At its heart stands 
    the Crystal Haven, a city built upon ruins of an ancient civilization.

    The Great War of the Crystal occurred 1000 years ago when the Dark Sorcerer Malakai 
    attempted to steal the Sacred Crystal. The Crystal Guard, an elite group of warriors
    and mages, defended the kingdom and sealed away the dark magic.

    Today, Queen Aria rules from the Crystal Throne, guided by ancient wisdom and
    protected by the Crystal Guard. The Academy of Light and Shadow trains new 
    guardians in both martial and magical arts.
    """
    
    # Save lore to file
    with open("game_lore.txt", "w") as f:
        f.write(game_lore)
    
    # Index documents with metadata
    engine.load_and_index_documents(
        "game_lore.txt",
        metadatas=[{"section": "lore"}]
    )
    
    # Register character context
    character_template = """
    Character Name: {name}
    Role: {role}
    Background: {background}
    Personality: {personality}
    Speaking Style: {speaking_style}
    """
    
    wizard_variables = {
        "name": "Eldric the Wise",
        "role": "Senior Crystal Guard Instructor",
        "background": "Former battle-mage during the Border Wars",
        "personality": "Wise and patient, but strict with students",
        "speaking_style": "Formal and precise, often uses magical terminology"
    }
    
    engine.register_context("wizard", character_template, wizard_variables)
    
    # Example 1: Pure RAG query
    print("\n=== RAG Query ===")
    lore_query = "Tell me about the Crystal Guard and their training."
    response = engine.query(
        prompt=lore_query,
        where={"section": "lore"}
    )
    print(f"Question: {lore_query}")
    print(f"Answer: {response['result']}\n")
    
    # Example 2: Pure CAG query
    print("\n=== CAG Query ===")
    character_query = "What do you think about modern training methods?"
    response = engine.query(
        prompt=character_query,
        context_name="wizard"
    )
    print(f"Question: {character_query}")
    print(f"Answer: {response['result']}\n")
    
    # Example 3: Combined query using both RAG and CAG
    print("\n=== Combined Query ===")
    combined_query = "As an instructor, what can you tell me about the history and importance of the Crystal Guard?"
    response = engine.query(
        prompt=combined_query,
        context_name="wizard",
        where={"section": "lore"},
        mode="combined"
    )
    print(f"Question: {combined_query}")
    print(f"Answer: {response['result']}\n")
    
    # Example 4: Structured query
    print("\n=== Structured Query ===")
    struct_query = "Tell me about yourself and your knowledge of the Crystal Guard's history"
    char_info = engine.query_structured(
        prompt=struct_query,
        response_model=Character,
        context_name="wizard",
        where={"section": "lore"},
        mode="combined"
    )
    print("\nStructured Character Information:")
    print(f"Name: {char_info.name}")
    print(f"Role: {char_info.role}")
    print(f"Personality: {char_info.personality}")
    print(f"Key Traits: {', '.join(char_info.key_traits)}")
    print(f"Background Knowledge: {', '.join(char_info.background_knowledge)}")

if __name__ == "__main__":
    main()
