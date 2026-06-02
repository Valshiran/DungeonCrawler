import tkinter as tk
from tkinter import messagebox
import item_database
import os
from PIL import Image, ImageTk

class InventoryWindow:
    def __init__(self, root, game_engine):
        """
        Creates the pop-up inventory interface.
        :param root: The main Tkinter root window
        :param game_engine: A reference to your main DungeonEngine instance
        """
        self.root = root
        self.game = game_engine  # This gives us access to self.game.inventory, self.game.player_hp, etc.
        
        # Create the popup window
        self.inv_win = tk.Toplevel(self.root)
        self.inv_win.title("Character Inventory & Equipment")
        self.inv_win.geometry("550x420")
        self.inv_win.grab_set()  # Freeze movement on the map behind it
        
        # Build the layout structure
        self.setup_layout()

    def get_item_data(self, item_id):
        """Searches across all four split dictionaries to find the item data."""
        # Check WEAPONS
        if item_id in item_database.WEAPONS:
            return item_database.WEAPONS[item_id]
        # Check SHIELDS
        elif item_id in item_database.SHIELDS:
            return item_database.SHIELDS[item_id]
        # Check ARMOR
        elif item_id in item_database.ARMOR:
            return item_database.ARMOR[item_id]
        # Check CONSUMABLES
        elif item_id in item_database.CONSUMABLES:
            return item_database.CONSUMABLES[item_id]
            
        # Default fallback if the item isn't found anywhere or is "none"
        return {"name": "Empty Slot", "stat_bonus": 0, "type": "none"}
    
    def setup_layout(self):
        # Left Panel: Equipment Slots
        left_frame = tk.LabelFrame(self.inv_win, text=" Equipped Gear ", font=("Arial", 10, "bold"), padx=10, pady=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Right Panel: Backpack Contents
        right_frame = tk.LabelFrame(self.inv_win, text=" Backpack ", font=("Arial", 10, "bold"), padx=10, pady=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # 1. Render Equipped Items
        for slot, item_id in self.game.equipped.items():
            item_data = self.get_item_data(item_id)
            
            slot_label = tk.Label(
                left_frame, 
                text=f"{slot.upper()}\n{item_data['name']} (+{item_data.get('stat_bonus', 0)})",
                font=("Arial", 9),
                bd=1, 
                relief="groove", 
                pady=8,
                width=22,
                bg="#f0f0f0"
            )
            slot_label.pack(pady=8)
            
        # 2. Render Backpack List
        self.inv_listbox = tk.Listbox(right_frame, selectmode="single", font=("Arial", 10), bd=2)
        self.inv_listbox.pack(fill="both", expand=True, pady=5)
        
        for item_id in self.game.inventory:
            item_data = self.get_item_data(item_id)
            
            display_name = item_data.get("name", item_id)
            self.inv_listbox.insert("end", display_name)
            
        # Equip/Use Button
        action_btn = tk.Button(
            right_frame, 
            text="⚔️ Equip / Use Item", 
            font=("Arial", 10, "bold"),
            command=self.use_selected_item, 
            bg="#4CAF50", 
            fg="white",
            pady=5
        )
        action_btn.pack(fill="x", pady=5)

    def use_selected_item(self):
        selected_index = self.inv_listbox.curselection()
        if not selected_index:
            return
            
        item_index = selected_index[0]
        new_item_id = self.game.inventory[item_index]
        item_data = item_database.ITEMS.get(new_item_id)
        
        if not item_data:
            return
            
        item_type = item_data.get("type")
        
        # equipment logic
        if item_type in ["weapon", "armor", "shield"]:
            # 1. Grab whatever is currently equipped in that slot
            old_item_id = self.game.equipped.get(item_type, "none")
            
            # 2. Put the new item into the equipment slot
            self.game.equipped[item_type] = new_item_id
            
            # 3. Remove the new item from the backpack list
            self.game.inventory.pop(item_index)
            
            # 4. If the old slot wasn't empty, put the old item back into the backpack
            if old_item_id != "none":
                self.game.inventory.append(old_item_id)
                messagebox.showinfo("Equipment Swapped", f"Equipped {item_data['name']} and unequipped your previous gear!")
            else:
                messagebox.showinfo("Equipment Equipped", f"You equipped the {item_data['name']}!")
        
        # consumable logic    
        elif item_type == "consumable":
            heal_amount = item_data.get("heal_amount", 0)
            self.game.player_hp = min(self.game.player_max_hp, self.game.player_hp + heal_amount)
            self.game.inventory.pop(item_index)
            messagebox.showinfo("Healed!", f"Used {item_data['name']}. Restored {heal_amount} HP!")
            
        # Redraw the window panels cleanly to show updates
        self.inv_win.destroy()
        InventoryWindow(self.root, self.game)
        
    def draw_paper_doll(self):
        """Draws the knight's asset image on the canvas with equipment squares surrounding it."""
        # Main visual canvas workspace (adjusted size to fit a nice character portrait)
        self.doll_canvas = tk.Canvas(self.left_frame, width=260, height=360, bg="#dcdde1", highlightthickness=1, relief="sunken")
        self.doll_canvas.pack(pady=15, padx=15)
        
        # --- 1. LOAD AND DRAW THE KNIGHT ASSET IMAGE ---
        try:
            # Look inside your assets folder for knight.png
            image_path = os.path.join("assets", "knight.png")
            raw_img = Image.open(image_path)
            
            # Resize it to fill the center of our inventory canvas nicely
            # (120x160 keeps it large but leaves room for buttons on the sides and bottom)
            resized_img = raw_img.resize((120, 160))
            
            # Convert to a Tkinter-compatible photo image
            # IMPORTANT: We attach it to 'self' so Python's garbage collector doesn't erase it from memory!
            self.knight_photo = ImageTk.PhotoImage(resized_img)
            
            # Draw the image right in the upper-center of the canvas
            self.doll_canvas.create_image(130, 110, anchor="center", image=self.knight_photo)
            
        except Exception as e:
            # Fallback: If the image file is missing, draw a placeholder box so the game doesn't crash
            self.doll_canvas.create_rectangle(70, 30, 190, 190, fill="#7f8c8d", width=2)
            self.doll_canvas.create_text(130, 110, text="[Knight Sprite]", fill="white")
            print(f"Warning: Could not load inventory knight sprite. Error: {e}")

        # --- 2. CONFIGURATION FOR YOUR 3 SPECIFIC SQUARES ---
        # Adjusted coordinates to frames perfectly around the 120x160 image space
        slots_config = {
            "weapon": {"x": 15,  "y": 90,  "label": "WEAPON"},
            "shield": {"x": 195, "y": 90,  "label": "SHIELD"},
            "armor":  {"x": 105, "y": 215, "label": "ARMOR"}
        }
        
        # --- 3. GENERATE INTERACTIVE EQUIPMENT BUTTONS ---
        for slot_type, pos in slots_config.items():
            current_item_id = self.game.equipped.get(slot_type, "none")
            item_data = item_database.ITEMS.get(current_item_id, {"name": "Empty"})
            
            # Label identifier text directly above each item slot square
            self.doll_canvas.create_text(
                pos["x"] + 25, 
                pos["y"] - 10, 
                text=pos["label"], 
                font=("Arial", 8, "bold"), 
                fill="#2f3640"
            )
            
            # Interactive equipment action button square
            slot_btn = tk.Button(
                self.left_frame,
                text=item_data["name"].replace(" ", "\n"),
                font=("Arial", 8, "bold"),
                bg="#ffffff" if current_item_id != "none" else "#b2bec3",
                fg="#2f3640" if current_item_id != "none" else "#636e72",
                relief="raised",
                bd=2,
                command=lambda s=slot_type: self.drop_item_in_slot(s)
            )
            
            # Embed the Tkinter button directly into the canvas coordinates
            self.doll_canvas.create_window(pos["x"], pos["y"], anchor="nw", window=slot_btn, width=50, height=50)