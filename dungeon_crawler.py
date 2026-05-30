import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# 1. Game Constants
GRID_SIZE = 10          # A 10x10 grid layout
TILE_SIZE = 50          # Each square grid tile is 50x50 pixels
WINDOW_WIDTH = GRID_SIZE * TILE_SIZE
WINDOW_HEIGHT = GRID_SIZE * TILE_SIZE

class DungeonGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Mega Man Dungeon Crawler")
        
        # 2. Player and Target Positions (Grid Coordinates: 0 to 9)
        self.player_x = 0
        self.player_y = 0
        
        self.target_x = 9
        self.target_y = 9
        
        # 3. Setup the Game Canvas
        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="#111111")
        self.canvas.pack()
        
        # 4. Load Sprites using Pillow
        self.load_sprites()
        
        # 5. Draw the initial game board
        self.render_game()
        
        # 6. Keyboard Binding: Listen for Arrow Key presses
        self.root.bind("<Up>", self.move_up)
        self.root.bind("<Down>", self.move_down)
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)

    def load_sprites(self):
        # Paths to your existing Mega Man assets
        assets_folder = os.path.join("assets", "fantasy")
        
        # Load and resize Player
        player_path = os.path.join(assets_folder, "megaman.png")
        pil_player = Image.open(player_path).resize((TILE_SIZE, TILE_SIZE))
        self.player_sprite = ImageTk.PhotoImage(pil_player)
        
        # Load and resize Target Boss
        target_path = os.path.join(assets_folder, "gemini.png")
        pil_target = Image.open(target_path).resize((TILE_SIZE, TILE_SIZE))
        self.target_sprite = ImageTk.PhotoImage(pil_target)

    def render_game(self):
        # Clear the whiteboard before redrawing
        self.canvas.delete("all")
        
        # Draw a subtle grid map background
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x1 = col * TILE_SIZE
                y1 = row * TILE_SIZE
                x2 = x1 + TILE_SIZE
                y2 = y1 + TILE_SIZE
                # Draw grid square outlines
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="#222222")
        
        # Draw Target Boss (Gemini Man) at its pixel location
        target_pixel_x = self.target_x * TILE_SIZE
        target_pixel_y = self.target_y * TILE_SIZE
        self.canvas.create_image(target_pixel_x, target_pixel_y, anchor="nw", image=self.target_sprite)
        
        # Draw Player (Mega Man) at his pixel location
        player_pixel_x = self.player_x * TILE_SIZE
        player_pixel_y = self.player_y * TILE_SIZE
        self.canvas.create_image(player_pixel_x, player_pixel_y, anchor="nw", image=self.player_sprite)

    # 7. Movement Controls & Boundary Guards
    def move_up(self, event):
        if self.player_y > 0:  # Prevents moving off the top edge
            self.player_y -= 1
            self.check_game_state()

    def move_down(self, event):
        if self.player_y < GRID_SIZE - 1:  # Prevents moving off the bottom edge
            self.player_y += 1
            self.check_game_state()

    def move_left(self, event):
        if self.player_x > 0:  # Prevents moving off the left edge
            self.player_x -= 1
            self.check_game_state()

    def move_right(self, event):
        if self.player_x < GRID_SIZE - 1:  # Prevents moving off the right edge
            self.player_x += 1
            self.check_game_state()

    # 8. Collision Detection Logic
    def check_game_state(self):
        # Redraw player at their new position
        self.render_game()
        
        # If player coordinates match the target coordinates, victory!
        if self.player_x == self.target_x and self.player_y == self.target_y:
            messagebox.showinfo("Victory!", "⚡ Boss Defeated! You navigated the dungeon safely!")
            # Reset player to start
            self.player_x = 0
            self.player_y = 0
            self.render_game()

# Main Application Loop
if __name__ == "__main__":
    window = tk.Tk()
    game = DungeonGame(window)
    window.mainloop()