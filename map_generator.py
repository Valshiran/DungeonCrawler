import random
from config import GRID_SIZE, WALL, FLOOR

class MapGenerator:
    def __init__(self):
        self.current_level = 1

    def generate_level(self):
        """Returns a brand new 2D array layout."""
        # Increase difficulty (more walls) on higher levels
        wall_chance = 0.20 + (self.current_level * 0.02) 
        
        dungeon_map = []
        for row in range(GRID_SIZE):
            map_row = [WALL if random.random() < wall_chance else FLOOR for _ in range(GRID_SIZE)]
            dungeon_map.append(map_row)
            
        # Ensure start and end tiles are open
        dungeon_map[0][0] = FLOOR
        dungeon_map[GRID_SIZE-1][GRID_SIZE-1] = FLOOR
        return dungeon_map
        
    def next_level(self):
        self.current_level += 1
        return self.generate_level()