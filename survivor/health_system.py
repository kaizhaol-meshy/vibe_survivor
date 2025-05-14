class HealthSystem:
    def __init__(self, base_hp=100, max_hp=None):
        """
        Initialize the health system for a character.
        
        Args:
            base_hp (int): The base health points for the character, default is 100.
            max_hp (int): The maximum health points, defaults to base_hp if not specified.
        """
        self.base_hp = base_hp
        self.max_hp = max_hp if max_hp is not None else base_hp
        self.current_hp = self.max_hp
        self.is_alive = True
    
    def take_damage(self, damage_amount):
        """
        Apply damage to the character.
        
        Args:
            damage_amount (int): The amount of damage to apply.
            
        Returns:
            bool: True if the character is still alive after taking damage, False otherwise.
        """
        self.current_hp = max(0, self.current_hp - damage_amount)
        
        if self.current_hp <= 0:
            self.is_alive = False
            
        return self.is_alive
    
    def heal(self, heal_amount):
        """
        Heal the character.
        
        Args:
            heal_amount (int): The amount of health to restore.
            
        Returns:
            int: The actual amount healed.
        """
        if not self.is_alive:
            return 0
            
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + heal_amount)
        
        return self.current_hp - old_hp
    
    def revive(self, hp_percentage=1.0):
        """
        Revive the character if they are dead.
        
        Args:
            hp_percentage (float): The percentage of max_hp to restore upon revival, default is 100%.
            
        Returns:
            bool: True if the character was revived, False if they were already alive.
        """
        if self.is_alive:
            return False
            
        self.current_hp = int(self.max_hp * hp_percentage)
        self.is_alive = True
        
        return True
    
    def get_hp_percentage(self):
        """
        Get the current health as a percentage of max health.
        
        Returns:
            float: The percentage of health remaining (0.0 to 1.0).
        """
        return self.current_hp / self.max_hp
    
    def reset(self):
        """
        Reset health to maximum.
        """
        self.current_hp = self.max_hp
        self.is_alive = True 