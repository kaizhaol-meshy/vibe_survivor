import re
from abc import ABC, abstractmethod
import copy
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 1024 // 16 * 9

SPATIAL_RESOLUTION = 1024
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

    def to_str(self):
        if len(self.attributes) > 0:
            assert "id" in self.attributes
            return f"{{id:{self.attributes['id']}, kind:{self.kind}, x:{self.x}, y:{self.y}, {', '.join([f'{k}:{v}' for k, v in self.attributes.items() if k != 'id'])}}}\n"
        else:
            return f"{{id:0, kind:{self.kind}, x:{self.x}, y:{self.y}}}\n"


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
            self.particles.append(Particle(kind, x, y, attributes))
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
        inputs[0] = "ArrowLeft" in keys
        inputs[1] = "ArrowRight" in keys
        inputs[2] = "ArrowUp" in keys
        inputs[3] = "ArrowDown" in keys
        inputs[4] = " " in keys
        print(inputs)
        return inputs

    def get_user_keys(self, actions):
        keys = []
        if actions[0]:
            keys.append("arrow left")
        if actions[1]:
            keys.append("arrow right")
        if actions[2]:
            keys.append("arrow up")
        if actions[3]:
            keys.append("arrow down")
        if actions[4]:
            keys.append("space")
        return keys
