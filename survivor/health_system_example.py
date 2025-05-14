from base_game import BaseGame, Particle

class HealthExample(BaseGame):
    def __init__(self):
        super().__init__(max_num_particles=100)
        
        # Create a player with health
        self.player = self.create_particle(
            kind="player",
            x=100,
            y=100,
            attributes={
                "id": 1,
                "base_hp": 100,
                "max_hp": 100
            }
        )
        
        # Create an enemy with health
        self.enemy = self.create_particle(
            kind="enemy",
            x=300,
            y=300,
            attributes={
                "id": 2,
                "base_hp": 150,
                "max_hp": 150,
                "damage": 10
            }
        )
        
        # Create a healing item
        self.healing_item = self.create_particle(
            kind="healingItem",
            x=200,
            y=200,
            attributes={
                "id": 3,
                "heal_amount": 20
            }
        )
    
    def get_frame(self):
        # Example frame renderer - not implemented for this example
        return None
    
    def agent_action(self, last_action=None):
        # Example agent action - not implemented for this example
        return None
    
    def on_particle_death(self, dead_particle, killer_particle=None):
        """Override base method to handle particle death"""
        print(f"Particle {dead_particle.kind} (ID: {dead_particle.attributes['id']}) has died!")
        
        if killer_particle:
            print(f"  Killed by: {killer_particle.kind} (ID: {killer_particle.attributes['id']})")
        
        # Optional: remove the dead particle
        # self.remove_particle(dead_particle)


# Example usage
if __name__ == "__main__":
    game = HealthExample()
    
    # Display initial health
    print(f"Player initial HP: {game.player.health_system.current_hp}")
    print(f"Enemy initial HP: {game.enemy.health_system.current_hp}")
    
    # Player attacks enemy
    player_damage = 30
    print(f"\nPlayer attacks enemy for {player_damage} damage!")
    is_alive = game.apply_damage(game.player, game.enemy, player_damage)
    print(f"Enemy HP after attack: {game.enemy.health_system.current_hp}")
    
    # Enemy attacks player
    enemy_damage = game.enemy.attributes["damage"]
    print(f"\nEnemy attacks player for {enemy_damage} damage!")
    is_alive = game.apply_damage(game.enemy, game.player, enemy_damage)
    print(f"Player HP after attack: {game.player.health_system.current_hp}")
    
    # Player uses healing item
    heal_amount = game.healing_item.attributes["heal_amount"]
    print(f"\nPlayer uses healing item to recover {heal_amount} HP!")
    actual_heal = game.heal_particle(game.player, heal_amount)
    print(f"Player HP after healing: {game.player.health_system.current_hp} (Healed: {actual_heal})")
    
    # Kill enemy with excessive damage
    print(f"\nPlayer attacks enemy with massive damage!")
    is_alive = game.apply_damage(game.player, game.enemy, 1000)
    print(f"Enemy HP after massive damage: {game.enemy.health_system.current_hp}")
    print(f"Enemy is alive: {is_alive}")
    
    # Try to heal dead enemy
    print(f"\nAttempting to heal dead enemy...")
    actual_heal = game.heal_particle(game.enemy, 50)
    print(f"Enemy HP after attempted healing: {game.enemy.health_system.current_hp} (Healed: {actual_heal})")
    
    # Serialize and deserialize game state
    print("\nSerializing and deserializing game state...")
    game_state = game.encode()
    print(f"Game state: {game_state}")
    
    new_game = HealthExample()
    new_game.decode(game_state)
    
    print(f"\nAfter deserialization:")
    print(f"Player HP: {new_game.player.health_system.current_hp}")
    print(f"Enemy HP: {new_game.enemy.health_system.current_hp}")
    print(f"Enemy is alive: {new_game.enemy.health_system.is_alive}") 