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

        # Carve out guaranteed open pathways AFTER the map is smoothed
        # Top-Left Starting Area (3x3 open runway for the Knight)
        for r in range(3):
            for c in range(3):
                dungeon_map[r][c] = FLOOR
                
        # Bottom-Right Boss Area (3x3 open runway for the Troll)
        for r in range(1, 4):
            for c in range(1, 4):
                dungeon_map[GRID_SIZE - r][GRID_SIZE - c] = FLOOR
        
        # verify path exists between start and end, if not drill a tunnel through the walls
        if not self.is_path_clear(dungeon_map):
            dungeon_map = self.drill_emergency_tunnel(dungeon_map)
                
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
    
    def is_path_clear(self, test_map):
        
        start = (0, 0)
        target = (GRID_SIZE - 1, GRID_SIZE - 1)
        
        # track tiles already checked
        visited = set()
        queue = [start]
        visited.add(start)
        
        while queue:
            current_col, current_row = queue.pop(0)
            
            if (current_col, current_row) == target:
                return True
            
            for dc, dr in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                next_col = current_col + dc
                next_row = current_row + dr
                
                if (0 <= next_col < GRID_SIZE and 0 <= next_row < GRID_SIZE):
                    if test_map[next_row][next_col] == FLOOR and (next_col, next_row) not in visited:
                        visited.add((next_col, next_row))
                        queue.append((next_col, next_row))
        return False
    
    def drill_emergency_tunnel (self, broken_map):
        
        cx, cy = 0, 0
        target = GRID_SIZE - 1
        
        # carve a tunnel step-by-step, destroying walls
        while cx < target or cy < target:
            
            # randomly choose to step right or down on the way to exit (the pathing)
            if cx < target and cy < target:
                if random.random() < 0.5:
                    cx += 1
                else:
                    cy += 1
            elif cx < target:
                cx += 1
            else:
                cy += 1
            
            # removes the stone and puts a floor tile    
            broken_map[cy][cx] = FLOOR
            
        return broken_map

    def next_level(self):
        self.current_level += 1
        return self.generate_level()