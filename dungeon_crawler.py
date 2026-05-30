import os
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Import your custom engine modules
import config
from map_generator import MapGenerator
from combat import CombatSystem

import item_database



class DungeonEngine:
    def __init__(self, root):
        self.root = root
        self.root.title("Modular Dungeon Crawler")
        
        # Initialize State Trackers
        self.map_engine = MapGenerator()
        self.dungeon_map = self.map_engine.generate_level()
        
        # player state and xp tracking
        self.player_level = 1
        self.player_xp = 0
        self.player_xp_needed = 100
        
        self.player_hp = 100
        self.player_max_hp = 100
        self.player_str = 8     # Base damage power without weapons
        self.player_def = 1     # Base natural defense reduction
        
        # The Knight's loadout tracking strings
        self.equipped_weapon = "iron_axe"
        self.equipped_armor = "leather_rags"

        self.inventory = ["minor_potion", "minor_potion", "spiked_mace"]
        
     
        
        # 2. Setup Primary Canvas Layout
        self.canvas = tk.Canvas(
            root, 
            width=config.WINDOW_WIDTH, 
            height=config.WINDOW_HEIGHT + 40, # Extra space at bottom for UI HUD
            bg="#111111"
        )
        self.canvas.pack()
        
        # 3. Load Assets & Spawn
        self.load_sprites()
        self.spawn_entities()
        self.render_game()
        
        # 4. Keyboard Input Binding
        self.root.bind("<Up>", lambda e: self.move_player(0, -1))
        self.root.bind("<Down>", lambda e: self.move_player(0, 1))
        self.root.bind("<Left>", lambda e: self.move_player(-1, 0))
        self.root.bind("<Right>", lambda e: self.move_player(1, 0))

    def load_sprites(self):
        assets_folder = "assets"
        ts = config.TILE_SIZE
        
        # Characters
        self.player_sprite = ImageTk.PhotoImage(Image.open(os.path.join(assets_folder, "knight.png")).resize((ts, ts)))
        self.ogre_sprite = ImageTk.PhotoImage(Image.open(os.path.join(assets_folder, "ogre.png")).resize((ts, ts)))
        self.goblin_sprite = ImageTk.PhotoImage(Image.open(os.path.join(assets_folder, "goblin.png")).resize((ts, ts)))
        
        #Environment Tiles
        self.wall_tile = ImageTk.PhotoImage(Image.open(os.path.join(assets_folder, "rock_tile.png")).resize((ts, ts)))
        self.floor_tile = ImageTk.PhotoImage(Image.open(os.path.join(assets_folder, "dirt_tile.png")).resize((ts, ts)))

    def spawn_entities(self):
        self.player_x = 0
        self.player_y = 0
        self.ogre_x = config.GRID_SIZE - 1
        self.ogre_y = config.GRID_SIZE - 1
        
        # Spawn 3 Goblins randomly on open floor tiles
        self.goblins = []
        while len(self.goblins) < 3:
            gx = random.randint(0, config.GRID_SIZE - 1)
            gy = random.randint(0, config.GRID_SIZE - 1)
            if self.dungeon_map[gy][gx] == config.FLOOR and (gx, gy) != (0,0) and (gx, gy) != (self.ogre_x, self.ogre_y):
                if (gx, gy) not in self.goblins:
                    self.goblins.append([gx, gy])

    def move_player(self, dx, dy):
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        
        if 0 <= new_x < config.GRID_SIZE and 0 <= new_y < config.GRID_SIZE:
            if self.dungeon_map[new_y][new_x] == config.FLOOR:
                self.player_x = new_x
                self.player_y = new_y
                self.check_game_events()

    def check_game_events(self):
        self.render_game()
        
        # Check Goblin Collision
        for i, goblin in enumerate(self.goblins):
            if [self.player_x, self.player_y] == goblin:
                self.start_combat("goblin", i)
                return
                
        # Check Ogre Boss Collision
        if self.player_x == self.ogre_x and self.player_y == self.ogre_y:
            self.start_combat("ogre", -1)

    # -------------------------------------------------------------------------
    # TURN-BASED COMBAT WINDOW MANAGEMENT
    # -------------------------------------------------------------------------
    def start_combat(self, enemy_type, enemy_index):
        # Unbind movement keys so player can't walk away mid-fight
        self.root.unbind("<Up>")
        self.root.unbind("<Down>")
        self.root.unbind("<Left>")
        self.root.unbind("<Right>")
        
        # Initialize combat module processing
        self.active_battle = CombatSystem(
            self.player_hp, 
            self.player_str, 
            self.equipped_weapon, 
            enemy_type
        )
        self.enemy_idx_to_remove = enemy_index
        
        # Create a popup overlay window
        self.battle_win = tk.Toplevel(self.root)
        self.battle_win.title(f"Battle - Vs {enemy_type.capitalize()}!")
        self.battle_win.geometry("400x300")
        self.battle_win.grab_set() # Locks focus strictly to combat window
        
        # Combat UI Text Fields
        self.status_lbl = tk.Label(self.battle_win, text=f"A wild {enemy_type} stands before you!", font=("Arial", 12, "bold"), pady=10)
        self.status_lbl.pack()
        
        self.hp_lbl = tk.Label(self.battle_win, text=f"Your HP: {self.active_battle.player_hp}  |  Enemy HP: {self.active_battle.enemy_hp}", font=("Arial", 11))
        self.hp_lbl.pack(pady=10)
        
        self.log_lbl = tk.Label(self.battle_win, text="What will you do?", font=("Arial", 10), fg="blue", wraplength=350)
        self.log_lbl.pack(pady=15)
        
        # Action Buttons Layout
        btn_frame = tk.Frame(self.battle_win)
        btn_frame.pack(side="bottom", pady=20)
        
        tk.Button(btn_frame, text="Attack ⚔️", width=10, command=self.exec_attack).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Defend 🛡️", width=10, command=self.exec_defend).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Run 🏃", width=10, command=self.exec_run).pack(side="left", padx=5)

    def exec_attack(self):
        log_msg = self.active_battle.player_attack()
        self.process_enemy_turn(log_msg, defending=False)

    def exec_defend(self):
        log_msg = self.active_battle.player_defend()
        self.process_enemy_turn(log_msg, defending=True)

    def exec_run(self):
        success = self.active_battle.try_run()
        if success:
            messagebox.showinfo("Escaped!", "You successfully scrambled backward to safety!")
            # Move player back slightly so they aren't on the enemy tile
            self.player_x = max(0, self.player_x - 1)
            self.close_combat(victory=False)
        else:
            log_msg = "You tried to run, but the path was blocked!"
            self.process_enemy_turn(log_msg, defending=False)

    def process_enemy_turn(self, initial_msg, defending):
        # Update HP display after player move
        self.hp_lbl.config(text=f"Your HP: {self.active_battle.player_hp}  |  Enemy HP: {self.active_battle.enemy_hp}")
        
        # Check Win Condition
        if self.active_battle.enemy_hp <= 0:
            messagebox.showinfo("Victory!", f"You defeated the {self.active_battle.enemy_type}!")
            self.close_combat(victory=True)
            return
        
        # lookup defense data from item database
        armor_data = item_database.ARMOR.get(self.equipped_armor)
        armor_bonus = armor_data.get("defense_bonus", 0) if armor_data else 0
        total_defense = self.player_def + armor_bonus
        
        # Enemy Turn calculation
        raw_damage = self.active_battle.enemy_attack
        # If player chose to defend, cut raw attack power in half first
        if defending:
            raw_damage = max(1, raw_damage // 2)
            
        # Subtract defense value from incoming damage (ensure they take at least 1 damage)
        actual_damage = max(1, raw_damage - total_defense)
        
        self.active_battle.player_hp -= actual_damage
        self.player_hp = self.active_battle.player_hp # Sync engine HP
        
        # Display turn outcome log
        enemy_msg = f"\nThe {self.active_battle.enemy_type} strikes back dealing {actual_damage} damage!"
        self.log_lbl.config(text=initial_msg + enemy_msg)
        self.hp_lbl.config(text=f"Your HP: {self.active_battle.player_hp}  |  Enemy HP: {self.active_battle.enemy_hp}")
        
        # Check Loss Condition
        if self.player_hp <= 0:
            messagebox.showerror("Defeat", "Your health dropped to 0. You fell in battle!")
            self.battle_win.destroy()
            self.game_over()

    def close_combat(self, victory):
        if victory:
            if self.enemy_idx_to_remove == -1: # Ogre Boss defeated
                # Advance map generator to next level floor layout
                messagebox.showinfo("Floor Cleared", "Descending deeper into the dungeon layout...")
                self.dungeon_map = self.map_engine.next_level()
                self.spawn_entities()
            else:
                # Remove defeated minor goblin from current map instance
                self.goblins.pop(self.enemy_idx_to_remove)
                
        self.battle_win.destroy()
        self.render_game()
        
        # Re-bind movement controls for main window navigation
        self.root.bind("<Up>", lambda e: self.move_player(0, -1))
        self.root.bind("<Down>", lambda e: self.move_player(0, 1))
        self.root.bind("<Left>", lambda e: self.move_player(-1, 0))
        self.root.bind("<Right>", lambda e: self.move_player(1, 0))

    def game_over(self):
        self.map_engine = MapGenerator() # Reset floor counter back to level 1
        self.dungeon_map = self.map_engine.generate_level()
        self.player_hp = 100
        self.spawn_entities()
        self.render_game()
        
        # Reset standard keys
        self.root.bind("<Up>", lambda e: self.move_player(0, -1))
        self.root.bind("<Down>", lambda e: self.move_player(0, 1))
        self.root.bind("<Left>", lambda e: self.move_player(-1, 0))
        self.root.bind("<Right>", lambda e: self.move_player(1, 0))

    # -------------------------------------------------------------------------
    # RENDERING ENGINE
    # -------------------------------------------------------------------------
    def render_game(self):
        self.canvas.delete("all")
        ts = config.TILE_SIZE
        
        # Render Environment Blocks
        for row in range(config.GRID_SIZE):
            for col in range(config.GRID_SIZE):
                x1, y1 = col * ts, row * ts
                x2, y2 = x1 + ts, y1 + ts
                
                # Check tile type and stamp down the correct graphic asset
                if self.dungeon_map[row][col] == config.WALL:
                    self.canvas.create_image(x1, y1, anchor="nw", image=self.wall_tile)
                else:
                    self.canvas.create_image(x1, y1, anchor="nw", image=self.floor_tile)

        # Proximity Check / Visibility Render
        ogre_dist = max(abs(self.player_x - self.ogre_x), abs(self.player_y - self.ogre_y))
        if ogre_dist <= 2:
            self.canvas.create_image(self.ogre_x * ts, self.ogre_y * ts, anchor="nw", image=self.ogre_sprite)
            
        for gx, gy in self.goblins:
            gob_dist = max(abs(self.player_x - gx), abs(self.player_y - gy))
            if gob_dist <= 2:
                self.canvas.create_image(gx * ts, gy * ts, anchor="nw", image=self.goblin_sprite)

        # Player Rendering
        self.canvas.create_image(self.player_x * ts, self.player_y * ts, anchor="nw", image=self.player_sprite)
        
        # HUD Information Bar at the bottom
        hud_y = (config.GRID_SIZE * ts) + 15
        self.canvas.create_text(
            15, hud_y, 
            text=f"Knight HP: {self.player_hp}/{self.player_max_hp}  |  Dungeon Floor: B{self.map_engine.current_level}   | XP: {self.player_xp}/{self.player_xp_needed}",  
            # Equipped: {item_database.WEAPONS[self.equipped_weapon]['name']} & {item_database.ARMOR[self.equipped_armor]['name']}", 
            fill="white", anchor="w", font=("Arial", 12, "bold")
        )

if __name__ == "__main__":
    window = tk.Tk()
    game = DungeonEngine(window)
    window.mainloop()