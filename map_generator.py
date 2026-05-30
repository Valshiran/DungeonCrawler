import random
from config import GRID_SIZE, WALL, FLOOR

class MapGenerator:
    def __init__(self):
        self.current_level = 1

    def generate_level(self):
        # 1. Start with a standard random distribution
        dungeon_map = []
        for row in range(GRID_SIZE):
            map_row = [WALL if random.random() < 0.45 else FLOOR for _ in range(GRID_SIZE)]
            dungeon_map.append(map_row)
            
        # 2. Run 2 "Smoothing Passes" to simulate natural cave formation
        for _ in range(2):
            dungeon_map = self.smooth_map(dungeon_map)

        # 3. Open up safe paths at the start and finish points
        for r in range(2):
            for c in range(2):
                dungeon_map[r][c] = FLOOR
                dungeon_map[GRID_SIZE-1-r][GRID_SIZE-1-c] = FLOOR
                
        return dungeon_map

    def smooth_map(self, old_map):
        """Looks at surrounding tiles to group walls together like natural caves."""
        new_map = [[FLOOR for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                # Count how many of the 8 surrounding tiles are solid walls
                wall_count = 0
                for r_offset in [-1, 0, 1]:
                    for c_offset in [-1, 0, 1]:
                        neighbor_r = row + r_offset
                        neighbor_c = col + c_offset
                        
                        # Treat map borders as solid walls
                        if not (0 <= neighbor_r < GRID_SIZE and 0 <= neighbor_c < GRID_SIZE):
                            wall_count += 1
                        elif old_map[neighbor_r][neighbor_c] == WALL:
                            wall_count += 1
                
                # Cave Rule: If surrounded by 5 or more walls, it becomes a solid cave wall
                if wall_count >= 5:
                    new_map[row][col] = WALL
                else:
                    new_map[row][col] = FLOOR
                    
        return new_map

    def next_level(self):
        self.current_level += 1
        return self.generate_level()