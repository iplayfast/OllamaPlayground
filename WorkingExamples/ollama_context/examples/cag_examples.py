# examples/cag_example.py
from ollama_context import ContextEngine
from pydantic import BaseModel
from typing import List
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)

class Character(BaseModel):
    name: str
    role: str
    personality: str
    key_traits: List[str]

class DialogueResponse(BaseModel):
    speaker: str
    dialogue: str
    emotion: str
    actions: List[str]

def create_config():
    """Create a default config file if it doesn't exist."""
    config_dir = "ollama_context"
    config_path = os.path.join(config_dir, "config.json")
    
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    if not os.path.exists(config_path):
        config = {
            "response_model": "llama3.2:latest"
        }
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        logger.info(f"Created default config at {config_path}")
    
    return config_path

def test_character_generation(engine: ContextEngine):
    """Test character-based generation."""
    try:
        # Register a character context template
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
            "background": "Studied magic for 200 years in the Crystal Tower",
            "personality": "Wise, patient, but slightly eccentric",
            "speaking_style": "Formal and scholarly, often uses arcane terminology"
        }
        
        # Register the context
        logger.info("Registering wizard character context...")
        engine.register_context("wizard", character_template, wizard_variables)
        
        # Basic generation example
        logger.info("\n=== Basic Character Response ===")
        prompt = "What do you think about the recent surge in wild magic?"
        response = engine.query(
            prompt=prompt,
            context_name="wizard",
            system_prompt="You are a wise wizard responding to questions."
        )
        print(f"\nQuestion: {prompt}")
        print(f"Response: {response['result']}\n")
        
        # Update context variables
        logger.info("Updating wizard context...")
        engine.update_context_variables(
            "wizard",
            {
                "background": "Recently discovered ancient scrolls about wild magic",
                "personality": "More concerned and serious than usual"
            }
        )
        
        # Generate a structured character response
        logger.info("\n=== Structured Character Information ===")
        prompt = "Tell me about yourself"
        character_info = engine.query_structured(
            prompt=prompt,
            response_model=Character,
            context_name="wizard",
            system_prompt="Extract key character information in a structured format"
        )
        print("\nCharacter Information:")
        print(f"Name: {character_info.name}")
        print(f"Role: {character_info.role}")
        print(f"Personality: {character_info.personality}")
        print(f"Key Traits: {', '.join(character_info.key_traits)}\n")
        
    except Exception as e:
        logger.error(f"Error in character generation: {str(e)}")
        raise

def test_dialogue_generation(engine: ContextEngine):
    """Test dialogue-based generation."""
    try:
        # Register a dialogue context
        dialogue_template = (
            "Scene: {location}\n"
            "Time: {time}\n"
            "Atmosphere: {atmosphere}\n"
            "Present Characters: {characters}\n"
            "Previous Events: {previous_events}"
        )
        
        dialogue_variables = {
            "location": "Crystal Tower Library",
            "time": "Late evening",
            "atmosphere": "Tense and mysterious",
            "characters": "Eldric the Wise, apprentice Sarah",
            "previous_events": "Strange magical fluctuations have been detected"
        }
        
        logger.info("Registering dialogue scene context...")
        engine.register_context("dialogue_scene", dialogue_template, dialogue_variables)
        
        # Generate structured dialogue
        logger.info("\n=== Structured Dialogue ===")
        prompt = "How does Eldric respond to Sarah's question about the magical fluctuations?"
        dialogue = engine.query_structured(
            prompt=prompt,
            response_model=DialogueResponse,
            context_name="dialogue_scene",
            system_prompt="Generate dialogue and actions for the scene"
        )
        print("\nDialogue Generation:")
        print(f"Speaker: {dialogue.speaker}")
        print(f"Dialogue: {dialogue.dialogue}")
        print(f"Emotion: {dialogue.emotion}")
        print(f"Actions: {', '.join(dialogue.actions)}\n")
        
    except Exception as e:
        logger.error(f"Error in dialogue generation: {str(e)}")
        raise

def main():
    try:
        # Ensure config exists
        config_path = create_config()
        logger.info(f"Using config from: {config_path}")
        
        # Initialize the engine
        logger.info("Initializing engine...")
        engine = ContextEngine(
            mode="context",
            log_level=logging.CRITICAL,
            enable_http_logs=False
        )
        
        # Run the tests
        test_character_generation(engine)
        test_dialogue_generation(engine)
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()
