
# examples/context_usage_example.py
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
    # Initialize in auto mode
    engine = ContextEngine(
        mode="auto",
        log_level=logging.ERROR,
        database="examples/context_db"
    )
    
    # Set up RAG with some documents
    engine.load_and_index_documents(
        "game_lore.txt",
        metadatas=[{"section": "lore"}]
    )
    
    # Set up CAG with character template
    character_template = (
        "Character Name: {name}\n"
        "Role: {role}\n"
        "Background: {background}\n"
        "Personality: {personality}\n"
        "Speaking Style: {speaking_style}"
    ).strip()
    
    wizard_variables = {
        "name": "Eldric the Wise",
        "role": "Ancient Court Wizard",
        "background": "Studied magic for 200 years",
        "personality": "Wise and eccentric",
        "speaking_style": "Formal and scholarly"
    }
    
    engine.register_context("wizard", character_template, wizard_variables)
    
    # Example 1: RAG-only query about lore
    print("\n=== RAG Query ===")
    lore_query = "What happened in the Great War of the Crystal?"
    rag_response = engine.query(
        prompt=lore_query,
        where={"section": "lore"}
    )
    print(f"Question: {lore_query}")
    print(f"Answer: {rag_response['result']}\n")
    
    # Example 2: CAG-only query for character response
    print("\n=== CAG Query ===")
    character_query = "What do you think about wild magic?"
    cag_response = engine.query(
        prompt=character_query,
        context_name="wizard"
    )
    print(f"Question: {character_query}")
    print(f"Answer: {cag_response['result']}\n")
    
    # Example 3: Combined query using both RAG and CAG
    print("\n=== Combined Query ===")
    combined_query = "What do you know about the Crystal Guard and their training?"
    combined_response = engine.query(
        prompt=combined_query,
        context_name="wizard",
        where={"section": "lore"},
        mode="combined"
    )
    print(f"Question: {combined_query}")
    print(f"Answer: {combined_response['result']}\n")
    
    # Example 4: Structured combined query
    print("\n=== Structured Combined Query ===")
    structured_query = "Tell me about yourself and your knowledge of the Crystal Guard"
    char_info = engine.query_structured(
        prompt=structured_query,
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