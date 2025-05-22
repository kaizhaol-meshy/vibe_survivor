import re
from abc import ABC, abstractmethod
import copy
from health_system import HealthSystem

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 576

SPATIAL_RESOLUTION = 576
NUM_INPUTS = 4

import random

class Particle:
    def __init__(self, kind, x, y, attributes=None):
        self.kind = kind
        self.x = x
        self.y = y
        if attributes is None:
            attributes = {}
        self.attributes = attributes
        
        # Initialize health system if health attributes are provided
        if 'base_hp' in attributes:
            max_hp = attributes.get('max_hp', attributes['base_hp'])
            self.health_system = HealthSystem(attributes['base_hp'], max_hp)
        else:
            self.health_system = None

    def to_str(self):
        attr_str = []
        for k, v in self.attributes.items():
            if k != 'id':
                attr_str.append(f'{k}:{v}')
        
        # Add health info to attributes if health system exists
        if self.health_system:
            attr_str.append(f'current_hp:{self.health_system.current_hp}')
            attr_str.append(f'is_alive:{int(self.health_system.is_alive)}')
            
        if len(self.attributes) > 0:
            assert "id" in self.attributes
            return f"{{id:{self.attributes['id']}, kind:{self.kind}, x:{self.x}, y:{self.y}, {', '.join(attr_str)}}}\n"
        else:
            return f"{{id:0, kind:{self.kind}, x:{self.x}, y:{self.y}}}\n"
            
    def take_damage(self, damage_amount):
        """Apply damage to this particle if it has a health system"""
        if self.health_system:
            return self.health_system.take_damage(damage_amount)
        return True
        
    def heal(self, heal_amount):
        """Heal this particle if it has a health system"""
        if self.health_system:
            return self.health_system.heal(heal_amount)
        return 0
        
    def is_alive(self):
        """Check if this particle is alive"""
        if self.health_system:
            return self.health_system.is_alive
        return True  # Particles without health systems are always considered "alive"

class BaseGame(ABC):
    def __init__(self, max_num_particles):
        self.particles = []
        self.max_num_particles = max_num_particles
        self.num_steps = 0
        self.num_inputs = NUM_INPUTS
        self.fps = 60
        self.system_prompt = ""

    def set_system_prompt(self, system_prompt):
        self.system_prompt = system_prompt

    def get_system_prompt(self):
        return self.system_prompt

    def clear_particles(self):
        self.particles = []

    def create_particle(self, kind, x, y, attributes={}):
        assert len(self.particles) < self.max_num_particles
        particle = Particle(kind, x, y, attributes)
        self.particles.append(particle)
        return particle

    def remove_particle(self, particle):
        assert particle in self.particles
        self.particles.remove(particle)

    def step(self):
        self.num_steps += 1

    @abstractmethod
    def get_frame(self):
        pass

    def encode(self):
        game_state = ""
        for p in self.particles:
            game_state += p.to_str()
        return game_state

    def shuffle_encode(self):
        game_state = ""
        particles = copy.deepcopy(self.particles)
        random.shuffle(particles)
        for p in particles:
            game_state += p.to_str()
        return game_state

    def decode(self, game_state: str):
        particle_blocks = re.findall(r'\{(.*?)\}', game_state)
        self.particles.clear()
        for block in particle_blocks:
            pairs = dict(re.findall(r'(\w+):([^\s,<>]+)', block))
            kind = pairs['kind']
            x = float(pairs['x'])
            y = float(pairs['y'])
            attributes = {}
            for k, v in pairs.items():
                if k not in ['kind', 'x', 'y']:
                    try:
                        attributes[k] = float(v)
                    except:
                        attributes[k] = v
            
            # Create the particle
            particle = Particle(kind, x, y, attributes)
            
            # If the particle has health-related attributes, set them correctly
            if particle.health_system and 'current_hp' in pairs:
                particle.health_system.current_hp = float(pairs['current_hp'])
                if 'is_alive' in pairs:
                    particle.health_system.is_alive = bool(int(pairs['is_alive']))
            
            self.particles.append(particle)
        
        self.particles = sorted(self.particles, key=lambda p: p.attributes['id'])
        return self.encode()

    def get_particle(self, kind):
        return next((p for p in self.particles if p.kind == kind), None)

    def get_particles(self, kind):
        return [p for p in self.particles if p.kind == kind]

    @abstractmethod
    def agent_action(self, last_action=None):
        pass

    def get_user_inputs(self, keys):
        print(keys)
        inputs = [0, 0, 0, 0, 0]
        inputs[0] = "a" in keys  # Left
        inputs[1] = "d" in keys  # Right
        inputs[2] = "w" in keys  # Up
        inputs[3] = "s" in keys  # Down
        inputs[4] = " " in keys  # Space
        print(inputs)
        return inputs

    def get_user_keys(self, actions):
        keys = []
        if actions[0]:
            keys.append("a")
        if actions[1]:
            keys.append("d")
        if actions[2]:
            keys.append("w")
        if actions[3]:
            keys.append("s")
        if actions[4]:
            keys.append("space")
        return keys

    def apply_damage(self, source_particle, target_particle, damage_amount):
        """
        Apply damage from one particle to another
        
        Args:
            source_particle (Particle): The particle causing the damage
            target_particle (Particle): The particle receiving the damage
            damage_amount (int): The amount of damage to apply
            
        Returns:
            bool: True if the target is still alive, False if it died
        """
        is_alive = target_particle.take_damage(damage_amount)
        if not is_alive:
            self.on_particle_death(target_particle, source_particle)
        return is_alive
    
    def heal_particle(self, target_particle, heal_amount):
        """
        Heal a particle
        
        Args:
            target_particle (Particle): The particle to heal
            heal_amount (int): The amount of health to restore
            
        Returns:
            int: The actual amount healed
        """
        return target_particle.heal(heal_amount)
    
    def on_particle_death(self, dead_particle, killer_particle=None):
        """
        Handle a particle's death. Override this in subclasses to add custom behavior.
        
        Args:
            dead_particle (Particle): The particle that died
            killer_particle (Particle, optional): The particle that caused the death, if any
        """
        pass
