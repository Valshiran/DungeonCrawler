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
            
        # 2. Run the 2 smoothing passes to get organic cave curves
        for _ in range(2):
            dungeon_map = self.smooth_map(dungeon_map)

        # ---------------------------------------------------------------------
        # FIXED: Carve out guaranteed open pathways AFTER the map is smoothed
        # ---------------------------------------------------------------------
        # Top-Left Starting Area (3x3 open runway for the Knight)
        for r in range(3):
            for c in range(3):
                dungeon_map[r][c] = FLOOR
                
        # Bottom-Right Boss Area (3x3 open runway for the Troll)
        for r in range(1, 4):
            for c in range(1, 4):
                dungeon_map[GRID_SIZE - r][GRID_SIZE - c] = FLOOR
                
        return dungeon_map

    def smooth_map(self, old_map):
        """Looks at surrounding tiles to group walls together like natural caves."""
        new_map = [[FLOOR for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                wall_count = 0
                for r_offset in [-1, 0, 1]:
                    for c_offset in [-1, 0, 1]:
                        neighbor_r = row + r_offset
                        neighbor_c = col + c_offset
                        
                        if not (0 <= neighbor_r < GRID_SIZE and 0 <= neighbor_c < GRID_SIZE):
                            wall_count += 1
                        elif old_map[neighbor_r][neighbor_c] == WALL:
                            wall_count += 1
                
                if wall_count >= 5:
                    new_map[row][col] = WALL
                else:
                    new_map[row][col] = FLOOR
                    
        return new_map

    def next_level(self):
        self.current_level += 1
        return self.generate_level()