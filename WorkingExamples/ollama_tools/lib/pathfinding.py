from typing import List, Tuple, Optional
import heapq
from dataclasses import dataclass

class MapNode:
    def __init__(self, position: Tuple[int, int], cost: int):
        self.position = position
        self.cost = cost
        self.g = float('inf')
        self.h = 0
        self.f = float('inf')
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f

def manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(pos: Tuple[int, int], game_map: List[List[str]]) -> List[Tuple[int, int]]:
    neighbors = []
    y, x = pos
    for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        new_y, new_x = y + dy, x + dx
        if (0 <= new_y < len(game_map) and 
            0 <= new_x < len(game_map[0])):
            neighbors.append((new_y, new_x))
    return neighbors

def is_door(pos: Tuple[int, int], game_map: List[List[str]]) -> bool:
    y, x = pos
    if not (0 <= y < len(game_map) and 0 <= x < len(game_map[0])):
        return False
    return game_map[y][x] == 'd'

def get_terrain_cost(cell: str, pos: Tuple[int, int], game_map: List[List[str]]) -> int:
    if is_door(pos, game_map):
        return 3
    if cell.isupper():  # Building wall
        return 15
    elif cell.islower() and cell != 'd':  # Building interior
        return 7
    elif cell == 'd':  # Door
        return 3
    elif cell.isdigit():  # Terrain
        return int(cell)
    return 5

        
def find_path(game_map: List[List[str]], start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
    """Find complete path from start to goal using A* algorithm"""
    if not (0 <= start[0] < len(game_map) and 0 <= start[1] < len(game_map[0])):
        return None
    if not (0 <= goal[0] < len(game_map) and 0 <= goal[1] < len(game_map[0])):
        return None

    nodes = {}
    open_set = []
    closed_set = set()
    
    start_node = MapNode(start, get_terrain_cost(game_map[start[0]][start[1]], start, game_map))
    start_node.g = 0
    start_node.h = manhattan_distance(start, goal)
    start_node.f = start_node.g + start_node.h
    nodes[start] = start_node
    heapq.heappush(open_set, start_node)
    
    while open_set:
        current = heapq.heappop(open_set)
        
        if current.position == goal:
            path = []
            while current:
                path.append(current.position)
                current = current.parent
            return list(reversed(path))
        
        closed_set.add(current.position)
        
        for neighbor_pos in get_neighbors(current.position, game_map):
            if neighbor_pos in closed_set:
                continue
                
            neighbor_cost = get_terrain_cost(game_map[neighbor_pos[0]][neighbor_pos[1]], 
                                          neighbor_pos, game_map)
            if neighbor_pos not in nodes:
                nodes[neighbor_pos] = MapNode(neighbor_pos, neighbor_cost)
            
            neighbor = nodes[neighbor_pos]
            tentative_g = current.g + neighbor_cost
            
            if tentative_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = tentative_g
                neighbor.h = manhattan_distance(neighbor_pos, goal)
                neighbor.f = neighbor.g + neighbor.h
                
                if neighbor not in open_set:
                    heapq.heappush(open_set, neighbor)
    
    return None
