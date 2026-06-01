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
import creature_database



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
        
        # 1. Standard generic boss positioning tracking
        self.boss_x = config.GRID_SIZE - 1
        self.boss_y = config.GRID_SIZE - 1
        
        # 2. Initialize the container dictionary cleanly
        self.active_creatures = {}
        
        # 3. Pull a randomized boss key from the dedicated BOSSES dictionary catalog
        available_bosses = list(creature_database.BOSSES.keys())
        random_boss = random.choice(available_bosses)
        
        # Seat the boss at the exit coordinates
        self.active_creatures[(self.boss_x, self.boss_y)] = random_boss
        
        # 4. FIXED: Clean extraction of minions directly from the separate database
        available_creatures = list(creature_database.CREATURES.keys())
        
        # 5. FIXED: Adjusted target threshold size to 5 (1 boss + 4 unique minions)
        while len(self.active_creatures) < 5:
            gx = random.randint(0, config.GRID_SIZE - 1)
            gy = random.randint(0, config.GRID_SIZE - 1)
            
            # FIXED: Updated the exclusion check to utilize self.boss_x / self.boss_y
            if self.dungeon_map[gy][gx] == config.FLOOR and (gx, gy) != (0,0) and (gx, gy) != (self.boss_x, self.boss_y):
                if (gx, gy) not in self.active_creatures:
                    # Randomly pick a creature type (e.g., "goblin" or "orc")
                    random_creature = random.choice(available_creatures)
                    self.active_creatures[(gx, gy)] = random_creature

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
        current_pos = (self.player_x, self.player_y)
        
        # 1. DYNAMIC CHECK: Is there any creature from the database sitting on this tile?
        if current_pos in self.active_creatures:
            self.current_enemy_coords = current_pos
            creature_type = self.active_creatures[current_pos]
            
            # Launch combat using the exact string key pulled from the map dictionary
            self.start_combat(creature_type)
            return
                
        # 2. Check Boss Collision
        if current_pos == (self.boss_x, self.boss_y):
            self.current_enemy_coords = None
            creature_type = self.active_creatures[current_pos]
            self.start_combat(creature_type)

    # -------------------------------------------------------------------------
    # TURN-BASED COMBAT WINDOW MANAGEMENT
    # -------------------------------------------------------------------------
    def start_combat(self, enemy_type):
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
    
    def check_level_up(self):
        """Checks if the player has passed the XP threshold and scales requirements dynamically."""
        leveled_up = False
        
        # A while loop handles multiple level ups if they get a massive XP drop!
        while self.player_xp >= self.player_xp_needed:
            self.player_xp -= self.player_xp_needed  # Deduct the spent XP
            self.player_level += 1
            leveled_up = True
            
            # --- THE FORMULA ---
            # Multiply the previous requirement by 1.2 (and turn it into an integer)
            self.player_xp_needed = int(self.player_xp_needed * 1.2)
            
            # Permanently boost core player base stats!
            self.player_max_hp += 15
            self.player_hp = self.player_max_hp  # Fully heal on level up
            self.player_str += 3
            self.player_def += 1
            
            messagebox.showinfo(
                "LEVEL UP! ✨", 
                f"Congratulations! You reached Level {self.player_level}!\n\n"
                f"Max HP increased to {self.player_max_hp}\n"
                f"Base Strength increased to {self.player_str}\n"
                f"Base Defense increased to {self.player_def}\n"
                f"Next Level requires: {self.player_xp_needed} XP"
            )
            
        # Refresh the main window interface if a level up occurred
        if leveled_up:
            self.render_game()

    def close_combat(self, victory):
        if victory:
            
            xp_gained = self.active_battle.xp_reward
            self.player_xp += xp_gained
            
            # --- FIXED: Check if the enemy type exists anywhere inside the BOSS database ---
            if self.active_battle.enemy_type in creature_database.BOSSES:
                # Grab the real display name of the boss for the message box
                boss_name = creature_database.BOSSES[self.active_battle.enemy_type]["name"]
                
                messagebox.showinfo(
                    "Floor Cleared!", 
                    f"You have vanquished the legendary {boss_name}!\n"
                    f"Gained {xp_gained} XP.\n\n"
                    f"Descending deeper into the cavern layout..."
                )
                self.dungeon_map = self.map_engine.next_level()
                self.spawn_entities()
            else:
                # Remove defeated minor monster from the map dictionary using its coordinates
                if self.current_enemy_coords in self.active_creatures:
                    self.active_creatures.pop(self.current_enemy_coords)
            
            if hasattr(self, 'check_level_up'):
                self.check_level_up()
                
        self.battle_win.destroy()
        self.render_game()
        
        # Re-bind movement controls
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

       # --- FIXED: DYNAMIC PROXIMITY CHECK / VISIBILITY RENDER ---
        # Loops through every monster currently active on the map dictionary
        for (mx, my), creature_type in self.active_creatures.items():
            # Calculate distance from player to this specific monster
            dist = max(abs(self.player_x - mx), abs(self.player_y - my))
            
            # Proximity fog-of-war check (only show if within 2 tiles)
            if dist <= 2:
                # Dynamically find the matching sprite (e.g., self.orc_sprite, self.troll_sprite)
                # Falls back to self.goblin_sprite if a specific asset isn't found
                sprite_attr_name = f"{creature_type}_sprite"
                creature_sprite = getattr(self, sprite_attr_name, self.goblin_sprite)
                
                # Render the creature onto the canvas
                self.canvas.create_image(mx * ts, my * ts, anchor="nw", image=creature_sprite)

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