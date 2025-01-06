import os
from typing import List, Tuple, Dict

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_terrain_char(cell: str) -> str:
    """Convert map cell to display character"""
    terrain_chars = {
        ' ': ' ',  # Normal terrain
        '6': '∙',  # Different terrain types
        '7': '∘',
        '8': '○',
        '9': '●',
        'S': '█',  # Building walls
        'H': '█',
        'd': '▢',  # Doors
        's': '▫',  # Building interior
        'h': '▫'
    }
    return terrain_chars.get(cell, cell)

def display_char(buffer: List[List[str]], row: int, col: int, char: str, color: str = '') -> None:
    """Add a character to the display buffer at specified position with optional color"""
    if 0 <= row < len(buffer) and 0 <= col < len(buffer[0]):
        if color:
            buffer[row][col] = f"{color}{char}\033[0m"
        else:
            buffer[row][col] = char

def display_str(buffer: List[List[str]], row: int, col: int, text: str, color: str = '') -> None:
    """Add a string to the display buffer starting at specified position"""
    for i, char in enumerate(text):
        if col + i < len(buffer[0]):
            display_char(buffer, row, col + i, char, color)

def draw_terrain(buffer: List[List[str]], game_map: List[List[str]]) -> None:
    """Draw the base terrain layer"""
    for y in range(len(game_map)):
        for x in range(len(game_map[0])):
            terrain_char = get_terrain_char(game_map[y][x])
            display_char(buffer, y, x, terrain_char)

def draw_path(buffer: List[List[str]], path: List[Tuple[int, int]]) -> None:
    """Draw the path on the buffer"""
    if path:
        for y, x in path:
            display_char(buffer, y, x, '*', '\033[93m')  # Yellow

def draw_landmarks(buffer: List[List[str]], landmarks: Dict) -> None:
    """Draw landmark names on the buffer"""
    for name, info in landmarks.items():
        pos_y, pos_x = info['position']
        h, w = info['size']
        display_name = info['display_name']
        
        # Calculate center position
        center_y = pos_y + (h // 2)
        text_length = len(display_name)
        
        # Calculate starting x position
        if text_length >= w:
            start_x = pos_x
        else:
            start_x = pos_x + (w - text_length) // 2
        
        display_str(buffer, center_y, start_x, display_name, '\033[96m')

def render_buffer(buffer: List[List[str]]) -> None:
    """Render the buffer to the screen"""
    for row in buffer:
        print(''.join(row))

def display_map(game_map: List[List[str]], current_pos: Tuple[int, int], landmarks: Dict, 
                path: List[Tuple[int, int]] = None, text_buffer: List[str] = None) -> None:
    """
    Display the map with landmarks, current position, path, and buffered text.
    
    Args:
        game_map: 2D list representing the map
        current_pos: Current position as (y, x) tuple
        landmarks: Dictionary of landmarks
        path: Optional list of path coordinates
        text_buffer: Optional list of text lines to display after the map
    """
    clear_screen()
    print("\n=== Interactive Pathfinding Map ===")
    
    # Create the display buffer
    height = len(game_map)
    width = len(game_map[0]) if height > 0 else 0
    display_buffer = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Draw layers in order
    draw_terrain(display_buffer, game_map)
    if path:
        draw_path(display_buffer, path)
    draw_landmarks(display_buffer, landmarks)
    display_char(display_buffer, current_pos[0], current_pos[1], '@', '\033[92m')
    
    # Render the final buffer
    render_buffer(display_buffer)
    
    # Add a legend at the bottom
    print("\nLegend:")
    print("\033[92m@\033[0m Player   ", end='')
    print("\033[93m*\033[0m Path   ", end='')
    print("\033[96mText\033[0m Landmark Name   ", end='')
    print("▢ Door   ", end='')
    print("█ Wall   ", end='')
    print("▫ Interior")
    
    # Display buffered text if provided
    if text_buffer:
        print("\nOutput:")
        for line in text_buffer:
            print(line)
