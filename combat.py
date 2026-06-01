import random
import item_database
import creature_database

class CombatSystem:
    # 1. FIXED: Pass player's base stats and gear directly into the battle tracker
    def __init__(self, player_hp, player_base_str, equipped_weapon_id, enemy_type):
        self.player_hp = player_hp
        self.player_base_str = player_base_str
        self.equipped_weapon_id = equipped_weapon_id
        self.enemy_type = enemy_type
        
        creature_data = creature_database.CREATURES.get(enemy_type, {})
        if not creature_data:
            creature_data = creature_database.BOSSES.get(enemy_type)
        
        if creature_data:
            self.enemy_hp = creature_data["hp"]
            self.enemy_attack = creature_data["attack"]
            self.xp_reward = creature_data["xp_reward"]
        else:
            self.enemy_hp = 10
            self.enemy_attack = 2
            self.xp_reward = 10
            
    # 2. Added 'self' so it is a proper class method
    def calculate_player_attack_damage(self):
        # Look up the item data from our database file
        weapon_data = item_database.WEAPONS.get(self.equipped_weapon_id)
    
        # Extract the numerical bonus (defaults to 0 if weapon isn't found)
        weapon_bonus = weapon_data.get("attack_bonus", 0) if weapon_data else 0
    
        # Total Damage = Player's level strength + weapon power + a tiny bit of random variance
        variance = random.randint(-2, 2) # Adds some excitement so every swing isn't identical
        return self.player_base_str + weapon_bonus + variance

    def player_attack(self):
        # 3. Call our dynamic calculator instead of using hardcoded numbers!
        damage = self.calculate_player_attack_damage()
        
        # Prevent dealing negative or zero damage
        if damage < 1: 
            damage = 1
            
        self.enemy_hp -= damage
        return f"You strike the {self.enemy_type} for {damage} damage!"

    def player_defend(self):
        return "You raise your shield and prepare for the impact!"

    def try_run(self):
        return random.random() > 0.5


