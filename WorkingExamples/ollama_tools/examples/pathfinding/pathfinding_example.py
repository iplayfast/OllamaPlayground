from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict, Any
from ollama import chat, ChatResponse
import time
import os
from landmarks import LANDMARKS, get_landmark_at_position
from lib.display_utils import display_map
from lib.pathfinding import find_path
from ollama_tools.tools_engine import TOOLSEngine

# Global game map
GAME_MAP: List[List[str]] = []

def read_map(filename: str) -> List[List[str]]:
    """Read and return the game map"""
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to map.txt
    map_path = os.path.join(script_dir, filename)
    
    with open(map_path, 'r') as f:
        lines = [line.rstrip('\n') for line in f]
        max_width = max(len(line) for line in lines)
        return [list(line.ljust(max_width)) for line in lines]

""" example of chaining tool
def process_order(order_id: str) -> dict:
    Process an order and optionally trigger shipping
    # Do order processing
    result = process_order_details(order_id)
    
    if result["needs_shipping"]:
        # Return a prompt to trigger shipping processing
        return {
            "promptMessage": f"Arrange shipping for processed order {order_id}"
        }
    else:
        return {
            "status": "completed",
            "order_id": order_id
        }
"""
def get_landmark_coordinates(landmark_name: str) -> Optional[Tuple[int, int]]:
    """
    Get coordinates for a landmark's entrance.
    
    Args:
        landmark_name: Name of the landmark (e.g., 'house3', 'store1')
    
    Returns:
        Tuple of (y, x) coordinates for the landmark's entrance, or None if not found
    """
    if landmark_name in LANDMARKS:
        coords = LANDMARKS[landmark_name]['doors'][0]
        print(f"\nFound {LANDMARKS[landmark_name]['display_name']} at: {coords}")
        return coords
    print("\nCouldn't find that location!")
    return None

def get_path_description(start_pos: Tuple[int, int], landmark_name: str) -> str:
    """
    Get a description of the path between two points.
    
    Args:
        start_pos: Starting position as (y, x) tuple
        landmark_name: Name of the target landmark
    
    Returns:
        String describing the path and its length
    """
    target_pos = get_landmark_coordinates(landmark_name)
    if not target_pos:
        return "No valid path found - landmark not found."
        
    path = find_path(GAME_MAP, start_pos, target_pos)
    if not path:
        return "No valid path found."
    
    display_map(GAME_MAP, start_pos, LANDMARKS, path)
    description = f"Path found! Length: {len(path)-1} steps. Route: {' -> '.join(str(pos) for pos in path)}"
    print(f"\n{description}")
    return description

def move_to_landmark(current_pos: Tuple[int, int], landmark_name: str) -> List[Tuple[int, int]] | None:
    """
    Calculate and return path to target position.
    
    Args:
        current_pos: Current position as (y, x) tuple
        landmark_name: Name of the target landmark
    
    Returns:
        List of positions forming the path, or None if no path found
    """

    target_pos = get_landmark_coordinates(landmark_name)
    if not target_pos:
        return None
        
    path = find_path(GAME_MAP, current_pos, target_pos)
    if path:
        # Show initial map with path
        display_map(GAME_MAP, current_pos, LANDMARKS, path)
        print(f"\nPath length: {len(path)-1} steps")
        input("\nPress Enter to start movement...")
        
        # Animate movement
        for pos in path:
            display_map(GAME_MAP, pos, LANDMARKS, path)
            time.sleep(0.2)
        
        # Final display
        print("\nDestination reached!")
        return path
    
    print("\nNo valid path found!")
    return None

class SimplifiedPathfindingGame:
    def __init__(self):
        global GAME_MAP
        GAME_MAP = read_map("map.txt")
        self.current_pos = (5, 5)
        self.engine = TOOLSEngine("llama3.2:latest")
        
        # Register tool functions
        self.engine.add_tool(get_landmark_coordinates)
        self.engine.add_tool(get_path_description)
        self.engine.add_tool(move_to_landmark)
        
    def process_command(self, command: str) -> None:
        """Process user command using tools"""
        prompt = f"""
        Use the available tools to help with this command: "{command}"
        
        Use these exact sequences for different commands:

        For movement commands (e.g. "go to X", "take me to X"):
        1. Call move_to_landmark with current_pos {self.current_pos} and the landmark name
        
        For location queries (e.g. "where is X", "find X"):
        1. Call get_landmark_coordinates with the landmark name
        
        For path queries (e.g. "how do I get to X", "show me the way to X"):
        1. Call get_path_description with current_pos {self.current_pos} and the landmark name
        
        Always determine the type of command first, then follow the exact sequence for that type.
        If you don't understand the command or it doesn't match these patterns, say "INVALID".
        """
        
        response, tool_calls = self.engine.chat(prompt)
        
        if response == "INVALID":
            print("I couldn't understand that command. Please try again.")
            return
            
        # Update current position if it was a movement command
        for call in tool_calls:
            if call.name == "move_to_landmark" and call.response:
                self.current_pos = call.response[-1]  # Last position in the path
        
        input("\nPress Enter to continue...")
        
from typing import Optional, Tuple, Dict

def normalize_landmark_name(name: str) -> str:
    """
    Normalize landmark names by removing extra spaces and converting to lowercase.
    
    Args:
        name: The landmark name to normalize
    
    Returns:
        Normalized landmark name
    """
    return ' '.join(name.lower().split())

def get_landmark_coordinates(landmark_name: str) -> Optional[Tuple[int, int]]:
    """
    Get coordinates for a landmark's entrance, supporting both internal keys and display names.
    
    Args:
        landmark_name: Name of the landmark (e.g., 'House 4', 'house4', 'Store 1', 'store1')
    
    Returns:
        Tuple of (y, x) coordinates for the landmark's entrance, or None if not found
    """
    normalized_input = normalize_landmark_name(landmark_name)
    
    # First try direct key lookup (for backward compatibility)
    if landmark_name in LANDMARKS:
        coords = LANDMARKS[landmark_name]['doors'][0]
        print(f"\nFound {LANDMARKS[landmark_name]['display_name']} at: {coords}")
        return coords
    
    # Then try matching against display names
    for key, landmark in LANDMARKS.items():
        if normalize_landmark_name(landmark['display_name']) == normalized_input:
            coords = landmark['doors'][0]
            print(f"\nFound {landmark['display_name']} at: {coords}")
            return coords
            
    print(f"\nCouldn't find a location matching '{landmark_name}'!")
    return None
def get_path_description(start_pos: Tuple[int, int], landmark_name: str) -> str:
    """
    Get a description of the path between two points.
    
    Args:
        start_pos: Starting position as (y, x) tuple
        landmark_name: Name of the target landmark
    
    Returns:
        String describing the path and its length
    """
    target_pos = get_landmark_coordinates(landmark_name)
    if not target_pos:
        return "No valid path found - landmark not found."
        
    path = find_path(GAME_MAP, start_pos, target_pos)
    if not path:
        return "No valid path found."
    
    display_map(GAME_MAP, start_pos, LANDMARKS, path)
    description = f"Path found! Length: {len(path)-1} steps. Route: {' -> '.join(str(pos) for pos in path)}"
    print(f"\n{description}")
    return description

def move_to_landmark(current_pos: Tuple[int, int], landmark_name: str) -> List[Tuple[int, int]] | None:
    """
    Calculate and return path to target position.
    
    Args:
        current_pos: Current position as (y, x) tuple
        landmark_name: Name of the target landmark
    
    Returns:
        List of positions forming the path, or None if no path found
    """
    target_pos = get_landmark_coordinates(landmark_name)
    if not target_pos:
        return None
        
    path = find_path(GAME_MAP, current_pos, target_pos)
    if path:
        # Show initial map with path
        display_map(GAME_MAP, current_pos, LANDMARKS, path)
        print(f"\nPath length: {len(path)-1} steps")
        input("\nPress Enter to start movement...")
        
        # Animate movement
        for pos in path:
            display_map(GAME_MAP, pos, LANDMARKS, path)
            time.sleep(0.2)
        
        # Final display
        print("\nDestination reached!")
        return path
    
    print("\nNo valid path found!")
    return None

class SimplifiedPathfindingGame:
    def __init__(self):
        global GAME_MAP
        GAME_MAP = read_map("map.txt")
        self.current_pos = (5, 5)
        self.engine = TOOLSEngine("llama3.2:latest")
        
        # Register tool functions
        self.engine.add_tool(get_landmark_coordinates)
        self.engine.add_tool(get_path_description)
        self.engine.add_tool(move_to_landmark)
        
    def process_command(self, command: str) -> None:
        """Process user command using tools"""
        prompt = f"""
        The user command is: "{command}"
        
        First, extract the landmark name from the command and store it for use.
        Then, determine the command type and execute the appropriate sequence:

        For movement commands (e.g. "go to X", "take me to X"):
        1. Extract the landmark name after "go to" or "take me to"
        2. Call move_to_landmark with current_pos {self.current_pos} and the extracted landmark name
        
        For location queries (e.g. "where is X", "find X"):
        1. Extract the landmark name after "where is" or "find"
        2. Call get_landmark_coordinates with the extracted landmark name
        
        For path queries (e.g. "how do I get to X", "show me the way to X"):
        1. Extract the landmark name from the end of the query
        2. Call get_path_description with current_pos {self.current_pos} and the extracted landmark name
        
        Always extract the landmark name first, then determine the type of command.
        Be sure to pass the exact extracted landmark name to the appropriate function.
        If you can't understand the command or extract a landmark name, say "INVALID".
        
        Example:
        If command is "where is house 4", you should extract "house 4" and use that exact string.
        If command is "go to store 1", you should extract "store 1" and use that exact string.
        """        
        response, tool_calls = self.engine.chat(prompt)
        
        if response == "INVALID":
            print("I couldn't understand that command. Please try again.")
            return
            
        # Update current position if it was a movement command
        for call in tool_calls:
            if call.name == "move_to_landmark" and call.response:
                self.current_pos = call.response[-1]  # Last position in the path
        
        input("\nPress Enter to continue...")        
    def run(self):
        print("\nWelcome to the Simplified Pathfinding Game!")
        print("\nYou can:")
        print("- Move to locations (e.g., 'go to house 3', 'take me to the store')")
        print("- Get coordinates (e.g., 'where is house 4', 'find store 1')")
        print("- Get directions (e.g., 'how do I get to house 2', 'show me the way to the store')")
        input("\nPress Enter to begin...")
        
        while True:
            display_map(GAME_MAP, self.current_pos, LANDMARKS)
            
            landmark = get_landmark_at_position(self.current_pos)
            print(f"\nCurrent position: {self.current_pos}")
            if landmark:
                print(f"You are in: {LANDMARKS[landmark]['display_name']}")
            
            print("\nEnter a command (or 'quit' to exit):")
            command = input("> ").strip()
            
            if command.lower() == 'quit' or command.lower() == 'exit' or command.lower() == '':
                print("\nGoodbye!")
                break
                
            self.process_command(command)

def main():
    try:
        game = SimplifiedPathfindingGame()
        game.run()
    except FileNotFoundError:
        print("Error: map.txt not found!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
