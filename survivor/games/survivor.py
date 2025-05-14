import random
import math
from base_game import (
    BaseGame,
    Particle,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SPATIAL_RESOLUTION,
)
from graphics import Frame, Rectangle, Text

# Particle types
PLAYER = "player"
ENEMY = "enemy"
WEAPON = "weapon"
XP = "xp"

# Game constants
PLAYER_SIZE = 30
ENEMY_SIZE = 25
WEAPON_SIZE = 15
XP_SIZE = 10
PLAYER_SPEED = 5
ENEMY_SPEED_MIN = 1
ENEMY_SPEED_MAX = 3
WEAPON_SPEED = 8
WEAPON_COOLDOWN = 30
ENEMY_SPAWN_RATE = 60
MAX_ENEMIES = 20
XP_SPAWN_RATE = 120
MAX_WEAPONS = 5

class Game(BaseGame):
    def __init__(self):
        super().__init__(max_num_particles=MAX_ENEMIES + MAX_WEAPONS + 2)  # +2 for player and XP
        self.score = 0
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        self.last_reset = 0
        self.next_id = 0  # Track next available ID
        self.reset_level()
        self.set_system_prompt(
            "Vampire Survivors-like game. Survive as long as possible by collecting XP and leveling up. "
            "Enemies will spawn from the edges of the screen and chase you. "
            "Your weapons will automatically orbit around you and attack nearby enemies."
        )

    def reset_level(self):
        print(f"Resetting level after {self.num_steps - self.last_reset} steps")
        self.last_reset = self.num_steps
        self.clear_particles()
        self.next_id = 0
        # Add player particle
        player_x = SPATIAL_RESOLUTION // 2
        player_y = SPATIAL_RESOLUTION // 2
        self.particles.append(
            Particle(
                PLAYER,
                player_x,
                player_y,
                attributes={
                    "weapon_cooldown": 0,
                    "level": self.level,
                    "xp": self.xp,
                    "id": self.next_id
                }
            )
        )
        self.next_id += 1

        # Add initial enemies
        for _ in range(5):
            self.spawn_enemy()

    def spawn_enemy(self):
        if len(self.get_particles(ENEMY)) >= MAX_ENEMIES:
            return

        # Spawn enemies at the edges of the screen
        side = random.randint(0, 3)  # 0: top, 1: right, 2: bottom, 3: left
        if side == 0:  # top
            x = random.randint(0, SPATIAL_RESOLUTION)
            y = 0
        elif side == 1:  # right
            x = SPATIAL_RESOLUTION
            y = random.randint(0, SPATIAL_RESOLUTION)
        elif side == 2:  # bottom
            x = random.randint(0, SPATIAL_RESOLUTION)
            y = SPATIAL_RESOLUTION
        else:  # left
            x = 0
            y = random.randint(0, SPATIAL_RESOLUTION)

        self.particles.append(
            Particle(
                ENEMY,
                x,
                y,
                attributes={
                    "speed": random.randint(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX),
                    "health": 2 + self.level // 2,
                    "damage": 1,
                    "id": self.next_id
                }
            )
        )
        self.next_id += 1

    def spawn_weapon(self, player_x, player_y):
        if len(self.get_particles(WEAPON)) >= MAX_WEAPONS:
            return

        # Create a weapon that rotates around the player
        angle = random.randint(0, 359)  # Random angle in degrees
        distance = 50  # Distance from player
        x = int(player_x + distance * math.cos(math.radians(angle)))
        y = int(player_y + distance * math.sin(math.radians(angle)))
        
        self.particles.append(
            Particle(
                WEAPON,
                x,
                y,
                attributes={
                    "damage": 1 + self.level // 2,
                    "speed": WEAPON_SPEED,
                    "angle": angle,  # Store angle in degrees
                    "id": self.next_id
                }
            )
        )
        self.next_id += 1

    def spawn_xp(self, x, y):
        self.particles.append(
            Particle(
                XP,
                int(x),
                int(y),
                attributes={"id": self.next_id}
            )
        )
        self.next_id += 1

    def step(self, actions=None):
        player = self.get_particle(PLAYER)
        if player is None:
            self.reset_level()
            return

        # Process player movement
        if actions:
            dx = 0
            dy = 0
            if actions[0]:  # Left
                dx -= PLAYER_SPEED
            if actions[1]:  # Right
                dx += PLAYER_SPEED
            if actions[2]:  # Up
                dy -= PLAYER_SPEED
            if actions[3]:  # Down
                dy += PLAYER_SPEED

            # Normalize diagonal movement
            if dx != 0 and dy != 0:
                dx *= 0.7071  # 1/sqrt(2)
                dy *= 0.7071

            player.x = int(max(PLAYER_SIZE // 2, min(SPATIAL_RESOLUTION - PLAYER_SIZE // 2, player.x + dx)))
            player.y = int(max(PLAYER_SIZE // 2, min(SPATIAL_RESOLUTION - PLAYER_SIZE // 2, player.y + dy)))

        # Automatic weapon spawning with cooldown
        if player.attributes["weapon_cooldown"] <= 0:
            self.spawn_weapon(player.x, player.y)
            player.attributes["weapon_cooldown"] = WEAPON_COOLDOWN
        else:
            player.attributes["weapon_cooldown"] -= 1

        # Move and update weapons
        for weapon in self.get_particles(WEAPON):
            # Rotate around player
            weapon.attributes["angle"] = (weapon.attributes["angle"] + 6) % 360  # Increase angle by 6 degrees
            angle = weapon.attributes["angle"]
            distance = 50  # Distance from player
            weapon.x = int(player.x + distance * math.cos(math.radians(angle)))
            weapon.y = int(player.y + distance * math.sin(math.radians(angle)))

        # Move enemies towards player
        for enemy in self.get_particles(ENEMY):
            # Calculate direction to player
            dx = player.x - enemy.x
            dy = player.y - enemy.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                dx /= dist
                dy /= dist
                enemy.x = int(enemy.x + dx * enemy.attributes["speed"])
                enemy.y = int(enemy.y + dy * enemy.attributes["speed"])

            # Check for collisions with player
            if self.check_collision(player, enemy, PLAYER_SIZE, ENEMY_SIZE):
                self.reset_level()
                return

            # Check for collisions with weapons
            for weapon in self.get_particles(WEAPON):
                if self.check_collision(weapon, enemy, WEAPON_SIZE, ENEMY_SIZE):
                    enemy.attributes["health"] -= weapon.attributes["damage"]  # Reduce enemy health
                    if enemy.attributes["health"] <= 0:
                        self.score += 10
                        self.xp += 5
                        # Spawn XP orb
                        self.spawn_xp(enemy.x, enemy.y)
                        self.remove_particle(enemy)
                    break

        # Check for XP collection
        for xp in self.get_particles(XP):
            if self.check_collision(player, xp, PLAYER_SIZE, XP_SIZE):
                self.xp += 10
                self.remove_particle(xp)
                # Level up if enough XP
                if self.xp >= self.xp_to_next_level:
                    self.level += 1
                    self.xp -= self.xp_to_next_level
                    self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
                    player.attributes["level"] = self.level

        # Spawn new enemies
        if random.random() < 0.05:
            self.spawn_enemy()

        super().step()

    def check_collision(self, object1, object2, size1, size2):
        # Simple circle collision
        dx = object1.x - object2.x
        dy = object1.y - object2.y
        distance = (dx * dx + dy * dy) ** 0.5
        return distance < (size1 + size2) // 2

    def get_frame(self):
        # Create a Frame object
        frame = Frame()

        # Add dark background
        frame.add_rectangle(Rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, "#1a1a1a"))

        # Draw player
        player = self.get_particle(PLAYER)
        if player:
            frame.add_rectangle(
                Rectangle(
                    player.x * SCREEN_WIDTH / SPATIAL_RESOLUTION - PLAYER_SIZE // 2,
                    player.y * SCREEN_HEIGHT / SPATIAL_RESOLUTION - PLAYER_SIZE // 2,
                    PLAYER_SIZE,
                    PLAYER_SIZE,
                    "#00FFFF",  # Cyan for player
                )
            )

        # Draw enemies
        for enemy in self.get_particles(ENEMY):
            frame.add_rectangle(
                Rectangle(
                    enemy.x * SCREEN_WIDTH / SPATIAL_RESOLUTION - ENEMY_SIZE // 2,
                    enemy.y * SCREEN_HEIGHT / SPATIAL_RESOLUTION - ENEMY_SIZE // 2,
                    ENEMY_SIZE,
                    ENEMY_SIZE,
                    "#FF0000",  # Red for enemies
                )
            )

        # Draw weapons
        for weapon in self.get_particles(WEAPON):
            frame.add_rectangle(
                Rectangle(
                    weapon.x * SCREEN_WIDTH / SPATIAL_RESOLUTION - WEAPON_SIZE // 2,
                    weapon.y * SCREEN_HEIGHT / SPATIAL_RESOLUTION - WEAPON_SIZE // 2,
                    WEAPON_SIZE,
                    WEAPON_SIZE,
                    "#FFFF00",  # Yellow for weapons
                )
            )

        # Draw XP orbs
        for xp in self.get_particles(XP):
            frame.add_rectangle(
                Rectangle(
                    xp.x * SCREEN_WIDTH / SPATIAL_RESOLUTION - XP_SIZE // 2,
                    xp.y * SCREEN_HEIGHT / SPATIAL_RESOLUTION - XP_SIZE // 2,
                    XP_SIZE,
                    XP_SIZE,
                    "#00FF00",  # Green for XP
                )
            )

        # Draw HUD
        frame.add_text(Text(10, 30, f"Score: {self.score}", "#FFFFFF", 20))
        frame.add_text(Text(10, 60, f"Level: {self.level}", "#FFFFFF", 20))
        frame.add_text(Text(10, 90, f"XP: {self.xp}/{self.xp_to_next_level}", "#FFFFFF", 20))
        frame.add_text(Text(10, 120, "WASD to move", "#FFFFFF", 20))

        return frame

    def agent_action(self, last_action=None):
        """
        AI agent that tries to avoid enemies and collect XP
        """
        player = self.get_particle(PLAYER)
        if not player:
            return [False, False, False, False]

        # Get nearest enemy and XP
        nearest_enemy = None
        nearest_enemy_dist = float('inf')
        nearest_xp = None
        nearest_xp_dist = float('inf')

        for enemy in self.get_particles(ENEMY):
            dx = player.x - enemy.x
            dy = player.y - enemy.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < nearest_enemy_dist:
                nearest_enemy_dist = dist
                nearest_enemy = enemy

        for xp in self.get_particles(XP):
            dx = player.x - xp.x
            dy = player.y - xp.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < nearest_xp_dist:
                nearest_xp_dist = dist
                nearest_xp = xp

        # Default to random movement
        move_left = False
        move_right = False
        move_up = False
        move_down = False

        if random.random() < 0.1:
            # Random movement
            direction = random.randint(0, 3)
            if direction == 0:
                move_left = True
            elif direction == 1:
                move_right = True
            elif direction == 2:
                move_up = True
            else:
                move_down = True
        else:
            # Smart movement
            if nearest_enemy and nearest_enemy_dist < 100:
                # Move away from nearest enemy
                if nearest_enemy.x > player.x:
                    move_left = True
                else:
                    move_right = True
                if nearest_enemy.y > player.y:
                    move_up = True
                else:
                    move_down = True
            elif nearest_xp:
                # Move towards nearest XP
                if nearest_xp.x < player.x:
                    move_left = True
                else:
                    move_right = True
                if nearest_xp.y < player.y:
                    move_up = True
                else:
                    move_down = True

        return [move_left, move_right, move_up, move_down, False]