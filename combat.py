import random

class CombatSystem:
    def __init__(self, player_hp, enemy_type):
        self.player_hp = player_hp
        self.enemy_type = enemy_type
        
        # Scale enemy HP based on what you ran into
        if enemy_type == "troll":
            self.enemy_hp = 50
            self.enemy_attack = 10
        else: # goblin
            self.enemy_hp = 15
            self.enemy_attack = 4

    def player_attack(self):
        damage = random.randint(5, 12)
        self.enemy_hp -= damage
        return f"You strike the {self.enemy_type} for {damage} damage!"

    def player_defend(self):
        # Temporarily cut incoming enemy damage in half for one turn
        return "You raise your shield and prepare for the impact!"

    def try_run(self):
        # 50% chance to successfully flee back to a safe tile
        return random.random() > 0.5