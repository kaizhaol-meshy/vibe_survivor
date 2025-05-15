# -*- coding: utf-8 -*-
import random
import math
from base_game import (
    BaseGame,
    Particle,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SPATIAL_RESOLUTION,
)
from graphics import Frame, Rectangle, Text, Circle, Triangle, Cross

# Particle types
PLAYER = "player"
ENEMY = "enemy"
ENEMY_ELITE = "enemy_elite"  # New type for elite enemies
WEAPON = "weapon"
XP = "xp"
DAMAGE_TEXT = "damage_text"  # New particle type for damage numbers

# Game states
STATE_START_MENU = "start_menu"
STATE_PLAYING = "playing"
STATE_UPGRADE_MENU = "upgrade_menu"
STATE_GAME_OVER = "game_over"

# Game constants
PLAYER_SIZE = int(30 * 0.4 * 1.5)
ENEMY_SIZE = int(25 * 0.4)
ELITE_SIZE = int(40 * 0.4)
WEAPON_SIZE = int(15 * 0.4)
XP_SIZE = int(10 * 0.4)
PLAYER_SPEED = 5
ENEMY_SPEED_MIN = 2
ENEMY_SPEED_MAX = 2
ELITE_SPEED_MULTIPLIER = 1.5  # Elite enemies move faster
WEAPON_SPEED = 8
WEAPON_COOLDOWN = 30
MAX_ENEMIES = 60  # 优化：减少最大敌人数
MAX_WEAPONS = 4   # 优化：减少最大武器数
DESPAWN_DISTANCE = 1.5 * SPATIAL_RESOLUTION  # Distance at which enemies despawn
FRAMES_PER_MINUTE = 60 * 60  # 60fps * 60 seconds
WAVE_INTERVAL = FRAMES_PER_MINUTE  # One wave per minute
SPAWN_DISTANCE = SPATIAL_RESOLUTION * 1.1  # Distance from player to spawn enemies
KNOCKBACK_DISTANCE = 5  # Knockback distance in pixels
KNOCKBACK_DURATION = 10  # Duration of knockback in frames
DAMAGE_TEXT_DURATION = 60  # How long damage text stays visible in frames
DAMAGE_TEXT_RISE = 30  # How far damage text rises before disappearing
MIN_ENEMIES_PER_WAVE = 30  # 提高最小敌人数
XP_DROP_CHANCE = 0.5  # 50% chance to drop XP when enemy dies
ELITE_HEALTH_MULTIPLIER = 5  # Elite enemies have 5x normal health
XP_MAGNET_RANGE = 80  # Range at which XP starts moving toward player
XP_MAGNET_SPEED_MIN = int(2 * 0.7)
XP_MAGNET_SPEED_MAX = int(15 * 0.7)
XP_ACCELERATION = 0.2  # How quickly XP accelerates toward player

# Health system animation constants
HP_TRANSITION_DURATION = 20  # Steps for hp animation
HP_BLINK_DURATION = 10  # Steps for hp blinking effect
PLAYER_BLINK_DURATION = 12  # Steps for player blinking effect
HP_THRESHOLD = 20  # HP threshold for each section of health bar

# Colors
PLAYER_COLOR = "#00AAFF"
ENEMY_COLOR = "#FF4444"
ELITE_COLOR = "#FF00FF"
WEAPON_COLOR = "#FFFFFF"
XP_COLOR = "#00FF00"
BUTTON_COLOR = "#444488"
BUTTON_HOVER_COLOR = "#6666BB"
BUTTON_TEXT_COLOR = "#FFFFFF"

# Button constants
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 40

# Debug toolbar constants
DEBUG_BUTTON_WIDTH = 40  # 减小按钮宽度
DEBUG_BUTTON_HEIGHT = 30
DEBUG_BUTTON_SPACING = 5  # 减小按钮间距
DEBUG_FONT_SIZE = 16
DEBUG_TOOLBAR_HEIGHT = 50

# Weapon types
WEAPON_TYPES = [
    {
        "name": "Whip",
        "display": "鞭子",
        "max_level": 8,
        "base_damage": 10,
        "area": 1.0,
        "speed": 1.0,
        "amount": 1,
        "pierce": 1,
        "duration": 1.0,
        "cooldown": 90,
        "projectile_interval": 0,
        "hitbox_delay": 0,
        "knockback": 1.0,
        "pool_limit": 0,
        "chance": 0,
        "crit_multi": 1.0,
        "block_by_walls": False,
        "rarity": 1,
        "size": 12,
        "shape": "rectangle",  # 鞭子用矩形表示
        "behavior": "horizontal_slash",
        "upgrade_table": [
            {"damage": 5}, {"count": 1}, {"area": 0.25}, {"damage": 5},
            {"count": 1}, {"area": 0.25}, {"cooldown": -10}, {"damage": 10}
        ]
    },
    {
        "name": "MagicWand",
        "display": "魔法杖",
        "max_level": 8,
        "base_damage": 10,
        "area": 1.0,
        "speed": 1.0,
        "amount": 1,
        "pierce": 0,
        "duration": 1.0,
        "cooldown": 72,  # 1.2s (60fps*1.2)
        "projectile_interval": 6,  # 0.1s
        "hitbox_delay": 0,
        "knockback": 1.0,
        "pool_limit": 0,
        "chance": 0,
        "crit_multi": 1.0,
        "block_by_walls": False,
        "rarity": 1,
        "size": 10,
        "shape": "triangle",
        "behavior": "homing_missile",
        "upgrade_table": [
            {"amount": 1},  # Lv2: +1投掷物
            {"cooldown": -12},  # Lv3: 冷却-0.2s
            {"amount": 1},  # Lv4: +1投掷物
            {"damage": 10},  # Lv5: 伤害+10
            {"amount": 1},  # Lv6: +1投掷物
            {"pierce": 1},  # Lv7: 穿透+1
            {"damage": 10},  # Lv8: 伤害+10
        ]
    },
    {
        "name": "Knife",
        "display": "飞刀",
        "max_level": 8,
        "base_damage": 7,
        "area": 1.0,
        "speed": 1.0,
        "amount": 1,
        "pierce": 1,
        "duration": 1.0,
        "cooldown": 30,
        "projectile_interval": 0,
        "hitbox_delay": 0,
        "knockback": 1.0,
        "pool_limit": 0,
        "chance": 0,
        "crit_multi": 1.0,
        "block_by_walls": False,
        "rarity": 1,
        "size": 8,
        "shape": "triangle",  # 飞刀用三角形表示
        "behavior": "straight_shot",
        "upgrade_table": [
            {"damage": 2}, {"count": 1}, {"cooldown": -4}, {"damage": 2},
            {"count": 1}, {"cooldown": -4}, {"damage": 3}, {"count": 1}
        ]
    },
    {
        "name": "Axe",
        "display": "斧子",
        "max_level": 8,
        "base_damage": 12,
        "area": 1.0,
        "speed": 1.0,
        "amount": 1,
        "pierce": 1,
        "duration": 1.0,
        "cooldown": 70,
        "projectile_interval": 0,
        "hitbox_delay": 0,
        "knockback": 1.0,
        "pool_limit": 0,
        "chance": 0,
        "crit_multi": 1.0,
        "block_by_walls": False,
        "rarity": 1,
        "size": 14,
        "shape": "cross",  # 斧子用十字形表示
        "behavior": "arc_throw",
        "upgrade_table": [
            {"damage": 4}, {"count": 1}, {"area": 0.2}, {"damage": 4},
            {"count": 1}, {"area": 0.2}, {"cooldown": -8}, {"damage": 8}
        ]
    },
    {
        "name": "Cross",
        "display": "十字架",
        "max_level": 8,
        "base_damage": 10,
        "area": 1.0,
        "speed": 1.0,
        "amount": 1,
        "pierce": 1,
        "duration": 1.0,
        "cooldown": 80,
        "projectile_interval": 0,
        "hitbox_delay": 0,
        "knockback": 1.0,
        "pool_limit": 0,
        "chance": 0,
        "crit_multi": 1.0,
        "block_by_walls": False,
        "rarity": 1,
        "size": 14,
        "shape": "cross",  # 十字架用十字形表示
        "behavior": "boomerang",
        "upgrade_table": [
            {"damage": 3}, {"count": 1}, {"area": 0.2}, {"damage": 3},
            {"count": 1}, {"area": 0.2}, {"cooldown": -8}, {"damage": 6}
        ]
    },
    {
        "name": "KingBible",
        "display": "圣经",
        "max_level": 8,
        "base_damage": 8,
        "area": 1.0,
        "speed": 1.0,
        "amount": 1,
        "pierce": 1,
        "duration": 3.0,
        "cooldown": 180,
        "projectile_interval": 0,
        "hitbox_delay": 0,
        "knockback": 1.0,
        "pool_limit": 0,
        "chance": 0,
        "crit_multi": 1.0,
        "block_by_walls": False,
        "rarity": 1,
        "size": int(10 * 1.4),  # 尺寸增加40%
        "shape": "rectangle",  # 改为正方形
        "behavior": "orbit",
        "upgrade_table": [
            {"damage": 2}, {"count": 1}, {"speed": 0.2}, {"area": 0.2},
            {"damage": 2}, {"count": 1}, {"cooldown": -10}, {"damage": 6}
        ]
    },
    {
        "name": "FireWand",
        "display": "火焰之杖",
        "max_level": 8,
        "base_damage": 15,
        "area": 1.0,
        "speed": 1.0,
        "amount": 1,
        "pierce": 1,
        "duration": 1.0,
        "cooldown": 100,
        "projectile_interval": 0,
        "hitbox_delay": 0,
        "knockback": 1.0,
        "pool_limit": 0,
        "chance": 0,
        "crit_multi": 1.0,
        "block_by_walls": False,
        "rarity": 1,
        "size": 14,
        "behavior": "fan_shot",
        "upgrade_table": [
            {"damage": 5}, {"count": 1}, {"area": 0.2}, {"damage": 5},
            {"count": 1}, {"area": 0.2}, {"cooldown": -10}, {"damage": 10}
        ]
    },
    {
        "name": "Garlic",
        "display": "大蒜",
        "max_level": 8,
        "base_damage": 5,
        "area": 1.0,
        "speed": 1.0,
        "amount": 1,
        "pierce": 1,
        "duration": 1.0,
        "cooldown": 30,
        "projectile_interval": 0,
        "hitbox_delay": 0,
        "knockback": 1.0,
        "pool_limit": 0,
        "chance": 0,
        "crit_multi": 1.0,
        "block_by_walls": False,
        "rarity": 1,
        "size": 16,
        "behavior": "aura",
        "upgrade_table": [
            {"damage": 2}, {"area": 0.2}, {"damage": 2}, {"area": 0.2},
            {"damage": 2}, {"area": 0.2}, {"cooldown": -5}, {"damage": 4}
        ]
    },
]

# King Bible每级属性表
KING_BIBLE_LEVELS = [
    {"damage": 10, "amount": 1, "area": 1.0, "speed": 1.0, "duration": 3.0},
    {"damage": 10, "amount": 2, "area": 1.0, "speed": 1.0, "duration": 3.0},
    {"damage": 10, "amount": 2, "area": 1.25, "speed": 1.3, "duration": 3.0},
    {"damage": 20, "amount": 2, "area": 1.25, "speed": 1.3, "duration": 3.0},
    {"damage": 20, "amount": 3, "area": 1.25, "speed": 1.3, "duration": 3.0},
    {"damage": 20, "amount": 3, "area": 1.5, "speed": 1.6, "duration": 3.0},
    {"damage": 30, "amount": 3, "area": 1.5, "speed": 1.6, "duration": 3.0},
    {"damage": 30, "amount": 4, "area": 1.5, "speed": 1.6, "duration": 3.0},
]

# 武器颜色表
WEAPON_COLORS = {
    "Whip": "#FF3333",
    "MagicWand": "#3399FF",  # 统一为蓝色
    "Knife": "#CCCCCC",
    "Axe": "#FF9900",
    "Cross": "#FFD700",
    "KingBible": "#0066FF",
    "FireWand": "#FF6600",
    "Garlic": "#FFFF99",
}

class Game(BaseGame):
    def __init__(self):
        super().__init__(1000)  # Max 1000 particles
        
        # Game state constants
        self.game_state = STATE_START_MENU
        
        # Score variables
        self.score = 0
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = self.level * 50
        
        # Timer variables
        self.last_reset = 0
        self.game_timer = 0
        self.wave_timer = 0
        self.current_wave = 0
        self.min_enemies_per_wave = MIN_ENEMIES_PER_WAVE
        self.next_spawn_timer = 0
        
        # Health animation system
        self.hp_displayed = 100  # The smoothly displayed HP (for animation)
        self.hp_transition_timer = 0  # Timer for HP transition animation
        self.hp_blink_timer = 0  # Timer for HP blinking effect
        self.player_blink_timer = 0  # Timer for player blinking effect
        self.hp_section = 5  # HP threshold sections (100/20 = 5 sections)
        
        # Upgrade menu variables
        self.upgrade_options = []
        
        # ID generator for entities
        self.next_id = 0  
        
        # Mouse handling
        self.mouse_pos = (0, 0)
        self.mouse_clicked = False
        
        self.initialize_game()
        self.set_system_prompt(
            "Vampire Survivors-like game. Survive as long as possible by collecting XP and leveling up. "
            "Enemies will spawn from the edges of the screen and chase you. "
            "Your weapons will automatically orbit around you and attack nearby enemies."
        )
    
    def get_frame(self):
        """Create and return a Frame object with the current game state"""
        from graphics import Frame, Circle, Rectangle, Triangle, Cross, Text
        frame = Frame()
        # 1. 先画黑色底
        frame.add_rectangle(Rectangle(0, 0, SPATIAL_RESOLUTION, SPATIAL_RESOLUTION, "#000000"))
        # 2. 升级界面时，先画所有粒子，再画界面
        if self.game_state == STATE_UPGRADE_MENU:
            for p in self.particles:
                if p.kind == PLAYER:
                    if self.player_blink_timer > 0 and self.player_blink_timer % 4 >= 2:
                        continue
                    frame.add_circle(Circle(p.x, p.y, PLAYER_SIZE, PLAYER_COLOR))
                    if p.health_system:
                        bar_width = 40
                        bar_height = 6
                        hp_percent = p.health_system.current_hp / p.health_system.max_hp
                        bar_x = p.x - bar_width // 2
                        bar_y = p.y - PLAYER_SIZE - 12
                        frame.add_rectangle(Rectangle(bar_x, bar_y, bar_width, bar_height, "#444444"))
                        frame.add_rectangle(Rectangle(bar_x, bar_y, int(bar_width * hp_percent), bar_height, "#FF4444" if hp_percent < 0.3 else ("#FFFF00" if hp_percent < 0.6 else "#00FF00")))
                elif p.kind == ENEMY:
                    if p.attributes.get("is_dying"):
                        size = p.attributes.get("death_anim_size", ENEMY_SIZE)
                        color = "#FFFFFF" if p.attributes.get("death_anim_white") else ENEMY_COLOR
                        frame.add_circle(Circle(p.x, p.y, max(1, size), color))
                    else:
                        if "blink_timer" in p.attributes and p.attributes["blink_timer"] > 0 and p.attributes["blink_timer"] % 4 >= 2:
                            continue
                        frame.add_circle(Circle(p.x, p.y, ENEMY_SIZE, ENEMY_COLOR))
                elif p.kind == ENEMY_ELITE:
                    if p.attributes.get("is_dying"):
                        size = p.attributes.get("death_anim_size", ELITE_SIZE)
                        color = "#FFFFFF" if p.attributes.get("death_anim_white") else ELITE_COLOR
                        frame.add_circle(Circle(p.x, p.y, max(1, size), color))
                    else:
                        if "blink_timer" in p.attributes and p.attributes["blink_timer"] > 0 and p.attributes["blink_timer"] % 4 >= 2:
                            continue
                        frame.add_circle(Circle(p.x, p.y, ELITE_SIZE, ELITE_COLOR))
                elif p.kind == WEAPON:
                    weapon_name = p.attributes.get("weapon_name", "")
                    weapon_type = next((w for w in WEAPON_TYPES if w["name"] == weapon_name), None)
                    weapon_size = weapon_type["size"] if weapon_type else WEAPON_SIZE
                    shape = weapon_type.get("shape", "circle") if weapon_type else "circle"
                    angle = p.attributes.get("angle", 0)
                    if weapon_name == "MagicWand":
                        inner_color = "#FFFFFF"
                        outer_color = "#0055AA"
                        wand_size = weapon_size * 0.5
                        frame.add_circle(Circle(p.x, p.y, wand_size + 3, outer_color))
                        frame.add_circle(Circle(p.x, p.y, wand_size, inner_color))
                    elif weapon_name == "KingBible" and shape == "rectangle":
                        side = weapon_size * 1.4
                        shape_color = WEAPON_COLORS.get(weapon_name, WEAPON_COLOR)
                        frame.add_rectangle(Rectangle(p.x - side/2, p.y - side/2, side, side, shape_color, angle))
                    elif shape == "circle":
                        frame.add_circle(Circle(p.x, p.y, weapon_size, shape_color))
                    elif shape == "triangle":
                        frame.add_triangle(Triangle(p.x, p.y, weapon_size * 1.2, shape_color, angle))
                    elif shape == "cross":
                        frame.add_cross(Cross(p.x, p.y, weapon_size * 1.2, shape_color, angle))
                    elif shape == "rectangle":
                        width = weapon_size * 3
                        height = weapon_size * 0.5
                        frame.add_rectangle(Rectangle(p.x - width/2, p.y - height/2, width, height, shape_color, angle))
                elif p.kind == XP:
                    frame.add_circle(Circle(p.x, p.y, XP_SIZE, XP_COLOR))
                elif p.kind == DAMAGE_TEXT:
                    alpha = p.attributes.get("alpha", 255)
                    alpha_hex = format(int(alpha), '02x')
                    text = p.attributes.get("text", "")
                    size = p.attributes.get("size", 32)
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx != 0 or dy != 0:
                                frame.add_text(Text(
                                    p.x + dx, p.y + dy, text, f"#000000{alpha_hex}", size
                                ))
                    damage_color = f"{p.attributes.get('color', '#FFFFFF')}{alpha_hex}"
                    frame.add_text(Text(
                        p.x, 
                        p.y, 
                        text, 
                        damage_color, 
                        size
                    ))
                elif p.kind == WEAPON and p.attributes.get("weapon_name") == "KingBible":
                    frame.add_circle(Circle(p.x, p.y, int(WEAPON_SIZE*6.0), shape_color))
                    continue
            self.draw_upgrade_menu(frame)
            return frame
        elif self.game_state == STATE_PLAYING:
            self.draw_hud(frame)
            for p in self.particles:
                if p.kind == PLAYER:
                    # Skip drawing player if blinking and on blink frame
                    if self.player_blink_timer > 0 and self.player_blink_timer % 4 >= 2:
                        continue
                    frame.add_circle(Circle(p.x, p.y, PLAYER_SIZE, PLAYER_COLOR))
                    # Draw health bar above player
                    if p.health_system:
                        bar_width = 40
                        bar_height = 6
                        hp_percent = p.health_system.current_hp / p.health_system.max_hp
                        bar_x = p.x - bar_width // 2
                        bar_y = p.y - PLAYER_SIZE - 12
                        frame.add_rectangle(Rectangle(bar_x, bar_y, bar_width, bar_height, "#444444"))
                        frame.add_rectangle(Rectangle(bar_x, bar_y, int(bar_width * hp_percent), bar_height, "#FF4444" if hp_percent < 0.3 else ("#FFFF00" if hp_percent < 0.6 else "#00FF00")))
                elif p.kind == ENEMY:
                    # 死亡动画：闪白+缩小
                    if p.attributes.get("is_dying"):
                        size = p.attributes.get("death_anim_size", ENEMY_SIZE)
                        color = "#FFFFFF" if p.attributes.get("death_anim_white") else ENEMY_COLOR
                        frame.add_circle(Circle(p.x, p.y, max(1, size), color))
                    else:
                        if "blink_timer" in p.attributes and p.attributes["blink_timer"] > 0 and p.attributes["blink_timer"] % 4 >= 2:
                            continue
                        frame.add_circle(Circle(p.x, p.y, ENEMY_SIZE, ENEMY_COLOR))
                elif p.kind == ENEMY_ELITE:
                    if p.attributes.get("is_dying"):
                        size = p.attributes.get("death_anim_size", ELITE_SIZE)
                        color = "#FFFFFF" if p.attributes.get("death_anim_white") else ELITE_COLOR
                        frame.add_circle(Circle(p.x, p.y, max(1, size), color))
                    else:
                        if "blink_timer" in p.attributes and p.attributes["blink_timer"] > 0 and p.attributes["blink_timer"] % 4 >= 2:
                            continue
                        frame.add_circle(Circle(p.x, p.y, ELITE_SIZE, ELITE_COLOR))
                elif p.kind == WEAPON:
                    weapon_name = p.attributes.get("weapon_name", "")
                    weapon_type = next((w for w in WEAPON_TYPES if w["name"] == weapon_name), None)
                    weapon_size = weapon_type["size"] if weapon_type else WEAPON_SIZE
                    shape = weapon_type.get("shape", "circle") if weapon_type else "circle"
                    angle = p.attributes.get("angle", 0)
                    # 魔杖粒子特殊渲染：浅蓝圆+深蓝外圈
                    if weapon_name == "MagicWand":
                        inner_color = "#FFFFFF"  # 浅蓝
                        outer_color = "#0055AA"  # 深蓝
                        wand_size = weapon_size * 0.5
                        frame.add_circle(Circle(p.x, p.y, wand_size + 3, outer_color))
                        frame.add_circle(Circle(p.x, p.y, wand_size, inner_color))
                    elif weapon_name == "KingBible" and shape == "rectangle":
                        side = weapon_size * 1.4
                        shape_color = WEAPON_COLORS.get(weapon_name, WEAPON_COLOR)
                        frame.add_rectangle(Rectangle(p.x - side/2, p.y - side/2, side, side, shape_color, angle))
                    elif shape == "circle":
                        frame.add_circle(Circle(p.x, p.y, weapon_size, shape_color))
                    elif shape == "triangle":
                        frame.add_triangle(Triangle(p.x, p.y, weapon_size * 1.2, shape_color, angle))
                    elif shape == "cross":
                        frame.add_cross(Cross(p.x, p.y, weapon_size * 1.2, shape_color, angle))
                    elif shape == "rectangle":
                        width = weapon_size * 3
                        height = weapon_size * 0.5
                        frame.add_rectangle(Rectangle(p.x - width/2, p.y - height/2, width, height, shape_color, angle))
                elif p.kind == XP:
                    frame.add_circle(Circle(p.x, p.y, XP_SIZE, XP_COLOR))
                elif p.kind == DAMAGE_TEXT:
                    alpha = p.attributes.get("alpha", 255)
                    alpha_hex = format(int(alpha), '02x')
                    text = p.attributes.get("text", "")
                    size = p.attributes.get("size", 32)
                    # 黑色描边
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx != 0 or dy != 0:
                                frame.add_text(Text(
                                    p.x + dx, p.y + dy, text, f"#000000{alpha_hex}", size
                                ))
                    # 白色正字
                    damage_color = f"{p.attributes.get('color', '#FFFFFF')}{alpha_hex}"
                    frame.add_text(Text(
                        p.x, 
                        p.y, 
                        text, 
                        damage_color, 
                        size
                    ))
                elif p.kind == WEAPON and p.attributes.get("weapon_name") == "KingBible":
                    frame.add_circle(Circle(p.x, p.y, int(WEAPON_SIZE*6.0), shape_color))
                    continue
        
        elif self.game_state == STATE_START_MENU:
            self.draw_start_menu(frame)
        elif self.game_state == STATE_GAME_OVER:
            self.draw_game_over(frame)
        return frame
        
    def draw_hud(self, frame):
        """Draw HUD elements (health, score, time, etc.)"""
        player = self.get_particle(PLAYER)
        
        # Score and timer
        frame.add_text(Text(10, 50, f"Score: {self.score}", "#FFFFFF", 16))
        time_str = self.format_time(self.game_timer)
        frame.add_text(Text(10, 70, f"Time: {time_str}", "#FFFFFF", 16))
        
        # Level and XP
        level_text = f"Level: {self.level}"
        xp_text = f"XP: {self.xp}/{self.xp_to_next_level}"
        frame.add_text(Text(10, 90, level_text, "#FFFFFF", 16))
        frame.add_text(Text(10, 110, xp_text, "#FFFFFF", 16))
        
        # Wave info
        wave_text = f"Wave: {self.current_wave}"
        enemies_text = f"Enemies: {len(self.get_particles(ENEMY)) + len(self.get_particles(ENEMY_ELITE))}"
        frame.add_text(Text(10, 130, wave_text, "#FFFFFF", 16))
        frame.add_text(Text(10, 150, enemies_text, "#FFFFFF", 16))
        
        # Debug toolbar at the bottom of the screen
        self.draw_debug_toolbar(frame)
    
    def draw_debug_toolbar(self, frame):
        """Draw the debug toolbar at the bottom of the screen"""
        # Background for debug toolbar
        toolbar_y = SCREEN_HEIGHT - DEBUG_TOOLBAR_HEIGHT
        frame.add_rectangle(Rectangle(0, toolbar_y, SCREEN_WIDTH, DEBUG_TOOLBAR_HEIGHT, "#333333"))
        
        # Title for debug toolbar
        frame.add_text(Text(10, toolbar_y + 30, "Debug Toolbar:", "#FFFFFF", DEBUG_FONT_SIZE))
        
        # Get player weapon levels
        player = self.get_particle(PLAYER)
        if not player:
            return
            
        weapons = player.attributes.get("weapons", {})
        
        # Draw weapon level controls
        for i, weapon_type in enumerate(WEAPON_TYPES):
            weapon_name = weapon_type["name"]
            display_name = weapon_type["display"]
            level = weapons.get(weapon_name, 0)
            
            # Position for this weapon's controls
            button_x = 200 + i * (DEBUG_BUTTON_WIDTH * 2 + DEBUG_BUTTON_SPACING)
            
            # Display weapon name and current level
            weapon_text = f"{display_name}: {level}"
            frame.add_text(Text(button_x, toolbar_y + 15, weapon_text, "#FFFFFF", DEBUG_FONT_SIZE - 2))
            
            # Draw - button
            button_x_minus = button_x
            frame.add_rectangle(Rectangle(button_x_minus, toolbar_y + 20, DEBUG_BUTTON_WIDTH, DEBUG_BUTTON_HEIGHT, "#AA0000"))
            frame.add_text(Text(button_x_minus + 15, toolbar_y + 40, "-", "#FFFFFF", DEBUG_FONT_SIZE))
            
            # Draw + button
            button_x_plus = button_x_minus + DEBUG_BUTTON_WIDTH + 2
            frame.add_rectangle(Rectangle(button_x_plus, toolbar_y + 20, DEBUG_BUTTON_WIDTH, DEBUG_BUTTON_HEIGHT, "#00AA00"))
            frame.add_text(Text(button_x_plus + 15, toolbar_y + 40, "+", "#FFFFFF", DEBUG_FONT_SIZE))

    def initialize_game(self):
        """Initialize game state without resetting score, etc."""
        self.clear_particles()
        self.next_id = 0
        self.game_timer = 0
        
        # Only add player if we're in playing state
        if self.game_state == STATE_PLAYING:
            self.create_player()
            
            # Reset visual effect states
            self.hp_displayed = 100
            self.hp_transition_timer = 0
            self.hp_blink_timer = 0
            self.player_blink_timer = 0
            self.hp_section = 5
            
            # Reset wave system
            self.current_wave = 1
            self.wave_timer = WAVE_INTERVAL  # Start first wave immediately
            self.next_spawn_timer = 0
            self.min_enemies_per_wave = MIN_ENEMIES_PER_WAVE
            self.elite_spawned = False

            # Add initial enemies for first wave
            self.spawn_enemy_wave()
            
        print(f"游戏初始化完成，当前游戏状态: {self.game_state}")
        
    def create_player(self):
        """Create the player particle"""
        player_x = SPATIAL_RESOLUTION // 2
        player_y = SPATIAL_RESOLUTION // 2
        # 初始武器为1级圣经（KingBible），其他武器为0级
        weapons = {"KingBible": 1}
        
        # 确保其他武器也在初始武器列表中，但等级为0
        for weapon_type in WEAPON_TYPES:
            weapon_name = weapon_type["name"]
            if weapon_name != "KingBible":
                weapons[weapon_name] = 0
        
        self.particles.append(
            Particle(
                PLAYER,
                player_x,
                player_y,
                attributes={
                    "level": self.level,
                    "xp": self.xp,
                    "id": self.next_id,
                    "base_hp": 100,
                    "max_hp": 100,
                    "weapons": weapons,  # 使用包含所有武器的字典
                    "KingBible_cooldown": 0  # 确保可以立即使用武器
                }
            )
        )
        self.next_id += 1
        
    def reset_game(self):
        """Completely reset the game for a new playthrough"""
        self.score = 0
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = self.level * 50
        self.last_reset = 0
        self.game_state = STATE_PLAYING
        self.game_timer = 0
        self.initialize_game()
        
    def format_time(self, frames):
        """Convert frame count to time string (MM:SS)"""
        total_seconds = frames // 60  # 60 fps
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
        
    def handle_input(self, actions=None, mouse_pos=None, mouse_clicked=False):
        """Handle input for various game states"""
        self.mouse_pos = mouse_pos if mouse_pos else (0, 0)
        self.mouse_clicked = mouse_clicked
        
        if self.game_state == STATE_START_MENU:
            # Check if start button was clicked
            if self.mouse_clicked and self.is_point_in_rect(
                self.mouse_pos[0], self.mouse_pos[1],
                SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 50,
                BUTTON_WIDTH, BUTTON_HEIGHT
            ):
                self.game_state = STATE_PLAYING
                self.reset_game()
                
        elif self.game_state == STATE_UPGRADE_MENU:
            # Check if any upgrade option was clicked
            for i, option in enumerate(self.upgrade_options):
                button_y = SCREEN_HEIGHT // 2 - 50 + i * (BUTTON_HEIGHT + 20)
                if self.mouse_clicked and self.is_point_in_rect(
                    self.mouse_pos[0], self.mouse_pos[1],
                    SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
                    button_y,
                    BUTTON_WIDTH, BUTTON_HEIGHT
                ):
                    self.selected_upgrade = option
                    self.game_state = STATE_PLAYING
                    # Apply the upgrade
                    self.apply_upgrade(option)
                    break
                    
        elif self.game_state == STATE_GAME_OVER:
            # Check if restart button was clicked
            if self.mouse_clicked and self.is_point_in_rect(
                self.mouse_pos[0], self.mouse_pos[1],
                SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 80,
                BUTTON_WIDTH, BUTTON_HEIGHT
            ):
                self.game_state = STATE_PLAYING
                self.reset_game()
                return
        
        elif self.game_state == STATE_PLAYING:
            # Handle debug toolbar button clicks
            if self.mouse_clicked:
                player = self.get_particle(PLAYER)
                if player:
                    weapons = player.attributes.get("weapons", {})
                    
                    # Calculate toolbar starting position
                    toolbar_y = SCREEN_HEIGHT - DEBUG_TOOLBAR_HEIGHT
                    
                    for i, weapon_type in enumerate(WEAPON_TYPES):
                        weapon_name = weapon_type["name"]
                        # Each weapon has two buttons (-/+), starting after title (x=200)
                        button_x_minus = 200 + i * (DEBUG_BUTTON_WIDTH * 2 + DEBUG_BUTTON_SPACING)
                        button_x_plus = button_x_minus + DEBUG_BUTTON_WIDTH + 2
                        
                        # Check if decrease level button was clicked
                        if self.is_point_in_rect(
                            self.mouse_pos[0], self.mouse_pos[1],
                            button_x_minus, toolbar_y + 20,
                            DEBUG_BUTTON_WIDTH, DEBUG_BUTTON_HEIGHT
                        ):
                            # Decrease weapon level
                            current_level = weapons.get(weapon_name, 0)
                            if current_level > 0:
                                if current_level == 1:
                                    weapons.pop(weapon_name, None)  # Remove weapon if level is 1
                                else:
                                    weapons[weapon_name] = current_level - 1
                                print(f"Decreased {weapon_name} level to {weapons.get(weapon_name, 0)}")
                                
                        # Check if increase level button was clicked
                        elif self.is_point_in_rect(
                            self.mouse_pos[0], self.mouse_pos[1],
                            button_x_plus, toolbar_y + 20,
                            DEBUG_BUTTON_WIDTH, DEBUG_BUTTON_HEIGHT
                        ):
                            # Increase weapon level
                            current_level = weapons.get(weapon_name, 0)
                            max_level = weapon_type["max_level"]
                            if current_level < max_level:
                                if current_level == 0:
                                    weapons[weapon_name] = 1  # Add weapon at level 1 if it doesn't exist
                                else:
                                    weapons[weapon_name] = current_level + 1
                                print(f"Increased {weapon_name} level to {weapons[weapon_name]}")
                    
                    # Update player weapons attribute
                    player.attributes["weapons"] = weapons
        
        return actions
    
    def is_point_in_rect(self, x, y, rect_x, rect_y, rect_width, rect_height):
        """Check if a point is inside a rectangle"""
        return (x >= rect_x and x <= rect_x + rect_width and
                y >= rect_y and y <= rect_y + rect_height)
    
    def check_collision(self, particle1, particle2, size1, size2):
        # 优化：只检测屏幕内的粒子
        if getattr(particle1, 'attributes', {}).get('is_dying') or getattr(particle2, 'attributes', {}).get('is_dying'):
            return False
        if not (0 <= particle1.x <= SPATIAL_RESOLUTION and 0 <= particle1.y <= SPATIAL_RESOLUTION):
            return False
        if not (0 <= particle2.x <= SPATIAL_RESOLUTION and 0 <= particle2.y <= SPATIAL_RESOLUTION):
            return False
        # 对于KingBible，使用更大的碰撞范围
        if particle1.kind == WEAPON and particle1.attributes.get("weapon_name") == "KingBible":
            size1 = size1 * 3  # 增大圣经的碰撞范围（原来2倍，现3倍）
        
        # 对于光环类武器(Garlic)，使用属性中指定的范围
        if particle1.kind == WEAPON and particle1.attributes.get("weapon_name") == "Garlic":
            size1 = particle1.attributes.get("aura_radius", size1)
            
        # 基本圆形碰撞检测
        dx = particle1.x - particle2.x
        dy = particle1.y - particle2.y
        distance = math.sqrt(dx * dx + dy * dy)
        collision = distance < (size1 + size2) / 2
        
        # 打印碰撞信息用于调试
        if collision and (particle1.kind == WEAPON or particle2.kind == WEAPON):
            weapon = particle1 if particle1.kind == WEAPON else particle2
            weapon_name = weapon.attributes.get("weapon_name", "未知")
            print(f"检测到碰撞: {weapon_name} 距离: {distance:.2f}, 碰撞阈值: {(size1 + size2) / 2:.2f}")
            
        return collision
    
    def show_upgrade_menu(self):
        """Show the upgrade menu with weapon options"""
        self.game_state = STATE_UPGRADE_MENU
        self.upgrade_anim_timer = 12  # 0.2秒动画
        # 生成烟花特效
        import random
        self.upgrade_fireworks = []
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        for _ in range(14):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(4, 8)
            color = random.choice(["#FFD700", "#00FFFF", "#FF66FF", "#FFFFFF"])
            self.upgrade_fireworks.append([cx, cy, 8, color, angle, speed, 0])
        player = self.get_particle(PLAYER)
        if not player:
            return
        weapons = player.attributes.get("weapons", {})
        options = []
        # 1. 可升级的已有武器
        for w in WEAPON_TYPES:
            level = weapons.get(w["name"], 0)
            if 0 < level < w["max_level"]:
                options.append({
                    "type": "upgrade_weapon",
                    "display": w["display"],
                    "name": w["name"],
                    "level": level
                })
        # 2. 未拥有的新武器
        if len(weapons) < 6:
            for w in WEAPON_TYPES:
                if w["name"] not in weapons:
                    options.append({
                        "type": "new_weapon",
                        "display": w["display"],
                        "name": w["name"]
                    })
        # 3. 其他通用升级
        options.append({
            "type": "stat_upgrade",
            "display": "Damage +1"
        })
        options.append({
            "type": "stat_upgrade", 
            "display": "Attack Speed +10%"
        })
        import random
        self.upgrade_options = random.sample(options, min(3, len(options)))
        print("生成升级选项: {}".format(self.upgrade_options))
        
    def apply_upgrade(self, upgrade):
        """Apply the selected upgrade to the player"""
        player = self.get_particle(PLAYER)
        if not player:
            return
        
        weapons = player.attributes.setdefault("weapons", {})
        
        if upgrade["type"] == "upgrade_weapon":
            # 武器升级
            name = upgrade["name"]
            level = weapons.get(name, 1)
            if level < next((w["max_level"] for w in WEAPON_TYPES if w["name"] == name), 8):
                weapons[name] = level + 1
                print("升级武器 {} 到等级 {}".format(name, level+1))
                
        elif upgrade["type"] == "new_weapon":
            # 新武器
            name = upgrade["name"]
            if len(weapons) < 6 and name not in weapons:
                weapons[name] = 1
                print("获得新武器 {}".format(name))
                
        elif upgrade["type"] == "stat_upgrade":
            # 通用升级
            if upgrade["display"] == "Damage +1":
                for weapon in self.get_particles(WEAPON):
                    weapon.attributes["damage"] += 1
                print("所有武器伤害+1")
            elif upgrade["display"] == "Attack Speed +10%":
                for name in weapons:
                    cooldown_key = "{}_cooldown".format(name)
                    if cooldown_key in player.attributes:
                        player.attributes[cooldown_key] = max(5, player.attributes[cooldown_key] * 0.9)
                print("攻击速度提升10%")
        
    def show_game_over(self):
        """Show the game over screen"""
        self.game_state = STATE_GAME_OVER

    def reset_level(self):
        print(f"Resetting level after {self.num_steps - self.last_reset} steps")
        self.last_reset = self.num_steps
        self.clear_particles()
        self.next_id = 0
        player_x = SPATIAL_RESOLUTION // 2
        player_y = SPATIAL_RESOLUTION // 2
        # 只在新游戏时加1级圣经，调试工具可自由设为0
        if not hasattr(self, 'player_initialized') or not self.player_initialized:
            weapons = {"KingBible": 1}
            self.player_initialized = True
        else:
            weapons = {w["name"]: 0 for w in WEAPON_TYPES}
        self.particles.append(
            Particle(
                PLAYER,
                player_x,
                player_y,
                attributes={
                    "level": self.level,
                    "xp": self.xp,
                    "id": self.next_id,
                    "base_hp": 100,
                    "max_hp": 100,
                    "weapons": weapons,
                    "KingBible_cooldown": 0
                }
            )
        )
        self.next_id += 1

        # Reset visual effect states
        self.hp_displayed = 100
        self.hp_transition_timer = 0
        self.hp_blink_timer = 0
        self.player_blink_timer = 0
        self.hp_section = 5
        
        # Reset wave system
        self.current_wave = 1
        self.wave_timer = WAVE_INTERVAL  # Start first wave immediately
        self.next_spawn_timer = 0
        self.min_enemies_per_wave = MIN_ENEMIES_PER_WAVE
        self.elite_spawned = False

        # Add initial enemies for first wave
        self.spawn_enemy_wave()

    def spawn_enemy_wave(self):
        """Spawn a wave of enemies"""
        
        min_enemies = min(self.min_enemies_per_wave, MAX_ENEMIES)
        current_enemies = len(self.get_particles(ENEMY)) + len(self.get_particles(ENEMY_ELITE))
        
        # Don't spawn if we already have maximum enemies
        if current_enemies >= MAX_ENEMIES:
            return
            
        # Calculate how many enemies to spawn to reach minimum
        enemies_to_spawn = max(0, min_enemies - current_enemies)
        
        # If we already have enough enemies, just spawn one of each type
        # For now, we only have one type, so spawn just one
        if enemies_to_spawn == 0:
            enemies_to_spawn = 1
            
        print(f"Wave {self.current_wave}: Spawning {enemies_to_spawn} enemies")
        
        # Spawn the calculated number of enemies
        for _ in range(enemies_to_spawn):
            self.spawn_enemy()
        
        # Spawn one elite enemy per wave
        if not self.elite_spawned:
            self.spawn_elite_enemy()
            self.elite_spawned = True
            
        # Increase minimum enemies for next wave
        self.min_enemies_per_wave = min(MIN_ENEMIES_PER_WAVE + self.current_wave, MAX_ENEMIES)
        
        # Reset wave timer
        self.wave_timer = 0
        
        # Increment wave counter
        self.current_wave += 1
        
        # Reset elite spawn flag for next wave
        self.elite_spawned = False

    def spawn_elite_enemy(self):
        """Spawn an elite enemy with higher stats"""
        player = self.get_particle(PLAYER)
        if not player:
            return
        angle = random.uniform(0, 2 * math.pi)
        spawn_x = player.x + math.cos(angle) * SPAWN_DISTANCE
        spawn_y = player.y + math.sin(angle) * SPAWN_DISTANCE
        spawn_x = max(-ELITE_SIZE, min(SCREEN_WIDTH + ELITE_SIZE, spawn_x))
        spawn_y = max(-ELITE_SIZE, min(SCREEN_HEIGHT + ELITE_SIZE, spawn_y))
        elite_health = 30
        elite_speed = random.randint(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX) * ELITE_SPEED_MULTIPLIER
        self.particles.append(
            Particle(
                ENEMY_ELITE,
                spawn_x,
                spawn_y,
                attributes={
                    "speed": elite_speed,
                    "base_hp": elite_health,
                    "max_hp": elite_health,
                    "damage": 2,
                    "id": self.next_id,
                    "blink_timer": 0,
                    "wave": self.current_wave,
                    "xp_value": 30
                }
            )
        )
        self.next_id += 1
        print(f"Spawned elite enemy for wave {self.current_wave} with {elite_health} HP")
        
    def spawn_enemy(self):
        if len(self.get_particles(ENEMY)) + len(self.get_particles(ENEMY_ELITE)) >= MAX_ENEMIES:
            return
        player = self.get_particle(PLAYER)
        if not player:
            return
        angle = random.uniform(0, 2 * math.pi)
        spawn_x = player.x + math.cos(angle) * SPAWN_DISTANCE
        spawn_y = player.y + math.sin(angle) * SPAWN_DISTANCE
        spawn_x = max(-ENEMY_SIZE, min(SCREEN_WIDTH + ENEMY_SIZE, spawn_x))
        spawn_y = max(-ENEMY_SIZE, min(SCREEN_HEIGHT + ENEMY_SIZE, spawn_y))
        enemy_health = 10
        self.particles.append(
            Particle(
                ENEMY,
                spawn_x,
                spawn_y,
                attributes={
                    "speed": random.randint(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX),
                    "base_hp": enemy_health,
                    "max_hp": enemy_health,
                    "damage": 1,
                    "id": self.next_id,
                    "blink_timer": 0,
                    "wave": self.current_wave,
                    "xp_value": 10
                }
            )
        )
        self.next_id += 1

    def spawn_weapon(self, player_x, player_y, weapon_name, level, angle):
        w = next((w for w in WEAPON_TYPES if w["name"] == weapon_name), None)
        if not w or level <= 0:
            return
        damage = w["base_damage"] + sum(u.get("damage", 0) for u in w["upgrade_table"][:max(0,level-1)])
        if damage <= 0:
            damage = 1
        distance = 50
        x = int(player_x + distance * math.cos(math.radians(angle)))
        y = int(player_y + distance * math.sin(math.radians(angle)))
        
        # 获取武器的形状属性
        shape = w.get("shape", "circle")  # 默认为圆形
        size = w["size"]
        
        # 根据武器类型调整特殊属性
        special_attrs = {}
        if shape == "rectangle":
            special_attrs["width"] = size * 3  # 矩形武器（如鞭子）更长
            special_attrs["height"] = size
        
        # 合并所有属性
        attributes = {
            "damage": damage,
            "speed": WEAPON_SPEED,
            "angle": angle,
            "id": self.next_id,
            "weapon_name": weapon_name,
            "level": level,
            "shape": shape,  # 添加形状属性
            **special_attrs  # 添加特殊属性
        }
        
        self.particles.append(
            Particle(
                WEAPON,
                x,
                y,
                attributes=attributes
            )
        )
        self.next_id += 1

    def spawn_xp(self, x, y):
        self.particles.append(
            Particle(
                XP,
                int(x),
                int(y),
                attributes={
                    "id": self.next_id,
                    "speed": 0,  # Initial speed is 0
                    "moving_to_player": False  # Flag to track if XP is moving to player
                }
            )
        )
        self.next_id += 1

    def spawn_homing_missile(self, player, weapon_name, level):
        enemies = self.get_particles(ENEMY) + self.get_particles(ENEMY_ELITE)
        if not enemies:
            return
        weapon_type = next((w for w in WEAPON_TYPES if w["name"] == weapon_name), None)
        base_amount = weapon_type["amount"] if weapon_type else 1
        amount = base_amount + sum(u.get("amount", 0) for u in weapon_type["upgrade_table"][:max(0,level-1)])
        if amount < 1:
            amount = 1
        base_pierce = weapon_type["pierce"] if weapon_type else 0
        pierce = base_pierce + sum(u.get("pierce", 0) for u in weapon_type["upgrade_table"][:max(0,level-1)])
        pierce_count = pierce + 1
        base_speed = 10 * 0.6
        used_targets = set()
        for i in range(amount):
            available_enemies = [e for e in enemies if e.attributes["id"] not in used_targets]
            if available_enemies:
                nearest = min(available_enemies, key=lambda e: (player.x-e.x)**2 + (player.y-e.y)**2)
                used_targets.add(nearest.attributes["id"])
                angle = math.degrees(math.atan2(nearest.y - player.y, nearest.x - player.x))
            else:
                angle = random.uniform(0, 360)
            rad = math.radians(angle)
            vx = math.cos(rad) * base_speed
            vy = math.sin(rad) * base_speed
            self.particles.append(
                Particle(
                    WEAPON,
                    player.x,
                    player.y,
                    attributes={
                        "damage": 8 + 2 * (level-1),
                        "speed": base_speed,
                        "angle": angle,
                        "id": self.next_id,
                        "weapon_name": weapon_name,
                        "level": level,
                        "pierce_count": pierce_count,
                        "vx": vx,
                        "vy": vy
                    }
                )
            )
            self.next_id += 1

    def spawn_straight_shot(self, player, weapon_name, level):
        if level <= 0:
            return
        angle = 0
        damage = 7 + 2 * (level-1)
        if damage <= 0:
            damage = 1
            
        # 获取武器类型和形状
        weapon_type = next((w for w in WEAPON_TYPES if w["name"] == weapon_name), None)
        shape = weapon_type.get("shape", "circle") if weapon_type else "circle"
        
        self.particles.append(
            Particle(
                WEAPON,
                player.x,
                player.y,
                attributes={
                    "damage": damage,
                    "speed": 14,
                    "angle": angle,
                    "id": self.next_id,
                    "weapon_name": weapon_name,
                    "level": level,
                    "vx": math.cos(math.radians(angle)),
                    "vy": math.sin(math.radians(angle)),
                    "duration": 60,
                    "shape": shape
                }
            )
        )
        self.next_id += 1

    def spawn_arc_throw(self, player, weapon_name, level, i, count):
        if level <= 0:
            return
        angle = -60 + (120 // max(1, count-1)) * i if count > 1 else 0
        speed = 10
        damage = 12 + 3 * (level-1)
        if damage <= 0:
            damage = 1
        self.particles.append(
            Particle(
                WEAPON,
                player.x,
                player.y,
                attributes={
                    "damage": damage,
                    "speed": speed,
                    "angle": angle,
                    "id": self.next_id,
                    "weapon_name": weapon_name,
                    "level": level,
                    "vx": speed * math.cos(math.radians(angle)),
                    "vy": speed * math.sin(math.radians(angle)),
                    "gravity": 0.5
                }
            )
        )
        self.next_id += 1

    def spawn_boomerang(self, player, weapon_name, level):
        # 十字架：直线飞行后回旋
        angle = 0
        
        # 增加打印输出
        print(f"生成回旋武器 {weapon_name} (level {level})")
        
        # 创建武器粒子
        self.particles.append(
            Particle(
                WEAPON,
                player.x,
                player.y,
                attributes={
                    "damage": 10 + 2 * (level-1),
                    "speed": 12,
                    "angle": angle,
                    "id": self.next_id,
                    "weapon_name": weapon_name,
                    "level": level,
                    "vx": math.cos(math.radians(angle)),
                    "vy": math.sin(math.radians(angle)),
                    "boomerang_timer": 30,  # 30帧后回旋
                    "duration": 90  # 添加持续时间，确保武器粒子不会太快被移除
                }
            )
        )
        self.next_id += 1

    def spawn_orbiting_book(self, player, weapon_name, level, i, count):
        if level <= 0:
            return
        lvl = min(level, len(KING_BIBLE_LEVELS)) - 1
        props = KING_BIBLE_LEVELS[lvl]
        damage = self.get_kingbible_damage(level)
        base_radius = 60
        radius = base_radius * props["area"]
        amount = max(1, props["amount"])
        if i == 0:
            weapons_to_remove = []
            for weapon in self.get_particles(WEAPON):
                if (weapon.attributes.get("weapon_name") == "KingBible" and 
                    weapon.attributes.get("target_player_id") == player.attributes.get("id")):
                    weapons_to_remove.append(weapon)
            for weapon in weapons_to_remove:
                if weapon in self.particles:
                    self.remove_particle(weapon)
        angle = (360 // amount) * i if amount > 1 else 0
        pos_x = player.x + radius * math.cos(math.radians(angle))
        pos_y = player.y + radius * math.sin(math.radians(angle))
        
        # 获取武器类型和形状
        weapon_type = next((w for w in WEAPON_TYPES if w["name"] == weapon_name), None)
        shape = weapon_type.get("shape", "circle") if weapon_type else "circle"
        
        weapon = Particle(
            WEAPON,
            pos_x,
            pos_y,
            attributes={
                "damage": damage,
                "speed": props["speed"],
                "angle": angle,
                "id": self.next_id,
                "weapon_name": weapon_name,
                "level": level,
                "orbit_radius": radius,
                "orbit_angle": angle,
                "duration": int(3.0 * 60),
                "target_player_id": player.attributes["id"],
                "hit_cooldown": {},
                "shape": shape
            }
        )
        self.particles.append(weapon)
        self.next_id += 1
        return weapon

    def spawn_fan_shot(self, player, weapon_name, level, i, count):
        if level <= 0:
            return
        spread = 60
        base_angle = -spread//2 + (spread//max(1, count-1))*i if count > 1 else 0
        print(f"生成扇形武器 {weapon_name} (level {level}, 角度 {base_angle})")
        damage = 15 + 3 * (level-1)
        if damage <= 0:
            damage = 1
        self.particles.append(
            Particle(
                WEAPON,
                player.x,
                player.y,
                attributes={
                    "damage": damage,
                    "speed": 11,
                    "angle": base_angle,
                    "id": self.next_id,
                    "weapon_name": weapon_name,
                    "level": level,
                    "vx": math.cos(math.radians(base_angle)),
                    "vy": math.sin(math.radians(base_angle)),
                    "duration": 60
                }
            )
        )
        self.next_id += 1

    def spawn_aura(self, player, weapon_name, level):
        if level <= 0:
            return
        damage = 5 + 2 * (level-1)
        if damage <= 0:
            damage = 1
        self.particles.append(
            Particle(
                WEAPON,
                player.x,
                player.y,
                attributes={
                    "damage": damage,
                    "speed": 0,
                    "angle": 0,
                    "id": self.next_id,
                    "weapon_name": weapon_name,
                    "level": level,
                    "aura_radius": 60 + 10 * (level-1),
                    "duration": 60
                }
            )
        )
        self.next_id += 1

    def spawn_whip(self, player, weapon_name, level):
        if level <= 0:
            return
        angle = 0
        damage = 10 + 3 * (level-1)
        if damage <= 0:
            damage = 1
        self.particles.append(
            Particle(
                WEAPON,
                player.x,
                player.y,
                attributes={
                    "damage": damage,
                    "speed": 0,
                    "angle": angle,
                    "id": self.next_id,
                    "weapon_name": weapon_name,
                    "level": level,
                    "whip_timer": 5
                }
            )
        )
        self.next_id += 1

    def step(self, actions=None):
        # Process input first
        # Note: This is now handled in run.py, so we don't process input here
        # actions = self.handle_input(actions)
        
        # If we're not in playing state, don't update game logic
        if self.game_state != STATE_PLAYING:
            return
            
        # Increment game timer
        self.game_timer += 1
        
        player = self.get_particle(PLAYER)
        if player is None:
            self.show_game_over()
            return
        
        # 每900帧（15秒）输出一次游戏状态（进一步减少日志）
        if self.game_timer % 900 == 0:
            weapons = player.attributes.get("weapons", {})
            weapon_count = len(self.get_particles(WEAPON))
            enemy_count = len(self.get_particles(ENEMY)) + len(self.get_particles(ENEMY_ELITE))
            print(f"游戏状态 - 时间: {self.format_time(self.game_timer)}, 敌人数: {enemy_count}, 武器数: {weapon_count}")
            
        # Update wave timer
        self.wave_timer += 1
        if self.wave_timer >= WAVE_INTERVAL:
            print(f"生成新一波敌人 - 波次: {self.current_wave + 1}")
            self.spawn_enemy_wave()
            
        # Handle enemy spawning within wave if below minimum
        current_enemies = len(self.get_particles(ENEMY)) + len(self.get_particles(ENEMY_ELITE))
        if current_enemies < self.min_enemies_per_wave and current_enemies < MAX_ENEMIES:
            # 快速补充到最小敌人数
            for _ in range(self.min_enemies_per_wave - current_enemies):
                if len(self.get_particles(ENEMY)) + len(self.get_particles(ENEMY_ELITE)) < MAX_ENEMIES:
                    self.spawn_enemy()
            if self.next_spawn_timer <= 0:
                self.spawn_enemy()
                # Set timer for next spawn (faster spawn rate: 0.5-1 second)
                self.next_spawn_timer = random.randint(30, 60)
            else:
                self.next_spawn_timer -= 1

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

        # Update animation timers
        if self.hp_transition_timer > 0:
            self.hp_transition_timer -= 1
            # Update displayed HP smoothly
            if player.health_system:
                target_hp = player.health_system.current_hp
                remaining_percentage = self.hp_transition_timer / HP_TRANSITION_DURATION
                self.hp_displayed = target_hp + (self.hp_displayed - target_hp) * remaining_percentage
        
        if self.hp_blink_timer > 0:
            self.hp_blink_timer -= 1
            
        if self.player_blink_timer > 0:
            self.player_blink_timer -= 1
            
        # Update enemy blink timers and knockback effects
        for enemy_type in [ENEMY, ENEMY_ELITE]:
            for enemy in self.get_particles(enemy_type):
                if enemy.attributes.get("is_dying"):
                    continue  # 死亡动画期间不移动不受击退
                if "blink_timer" in enemy.attributes and enemy.attributes["blink_timer"] > 0:
                    enemy.attributes["blink_timer"] -= 1
                # Process knockback effect
                if "knockback_timer" in enemy.attributes and enemy.attributes["knockback_timer"] > 0:
                    enemy.attributes["knockback_timer"] -= 1
                    if enemy.attributes["knockback_timer"] > 0 and "knockback_dx" in enemy.attributes and "knockback_dy" in enemy.attributes:
                        knockback_remaining = enemy.attributes["knockback_timer"] / KNOCKBACK_DURATION
                        knockback_force = knockback_remaining * knockback_remaining
                        enemy.x += enemy.attributes["knockback_dx"] * knockback_force * KNOCKBACK_DISTANCE
                        enemy.y += enemy.attributes["knockback_dy"] * knockback_force * KNOCKBACK_DISTANCE
                        enemy.x = max(0, min(SPATIAL_RESOLUTION, enemy.x))
                        enemy.y = max(0, min(SPATIAL_RESOLUTION, enemy.y))
        
        # Update and process damage text particles
        damage_texts_to_remove = []
        for particle in self.get_particles(DAMAGE_TEXT):
            if "timer" in particle.attributes:
                particle.attributes["timer"] -= 1
                if particle.attributes["timer"] <= 0:
                    damage_texts_to_remove.append(particle)
                else:
                    # Move the text upward as it fades
                    progress = 1 - (particle.attributes["timer"] / DAMAGE_TEXT_DURATION)
                    particle.y -= DAMAGE_TEXT_RISE / DAMAGE_TEXT_DURATION
                    
                    # Make it fade out by adjusting alpha in the color attribute
                    alpha = int(255 * (1 - progress))
                    particle.attributes["alpha"] = alpha
        
        # Remove expired damage texts
        for text in damage_texts_to_remove:
            self.remove_particle(text)

        # Automatic weapon spawning with cooldown
        weapons = player.attributes.get("weapons", {})
        for w in WEAPON_TYPES:
            name = w["name"]
            level = weapons.get(name, 0)
            if level > 0:  # 只有等级大于0的武器才会生成粒子
                cooldown_key = "{}_cooldown".format(name)
                current_cooldown = player.attributes.get(cooldown_key, 0)
                # 输出当前武器冷却情况
                if self.game_timer % 60 == 0 and current_cooldown > 0:
                    print(f"武器 {name} 当前冷却: {current_cooldown}")
                if current_cooldown <= 0:
                    print(f"生成武器 {name} (level {level})")
                    if name == "KingBible":
                        # 对于圣经武器，确保清理先前的粒子再生成新的
                        lvl = min(level, len(KING_BIBLE_LEVELS)) - 1
                        props = KING_BIBLE_LEVELS[lvl]
                        amount = props["amount"]
                        for i in range(amount):
                            self.spawn_orbiting_book(player, name, level, i, amount)
                        # 使用KING_BIBLE_LEVELS中的冷却时间，而不是固定值
                        # 转换为帧数 (秒 * 60)
                        cooldown_seconds = 3.0  # 圣经冷却3秒
                        player.attributes[cooldown_key] = int(cooldown_seconds * 60)
                    else:
                        count = 1 + sum(u.get("count", 0) for u in w["upgrade_table"][:level-1])
                        for i in range(count):
                            if w["behavior"] == "horizontal_slash":
                                angle = 0 if i % 2 == 0 else 180
                                self.spawn_weapon(player.x, player.y, name, level, angle)
                            elif w["behavior"] == "homing_missile":
                                self.spawn_homing_missile(player, name, level)
                            elif w["behavior"] == "straight_shot":
                                self.spawn_straight_shot(player, name, level)
                            elif w["behavior"] == "arc_throw":
                                self.spawn_arc_throw(player, name, level, i, count)
                            elif w["behavior"] == "boomerang":
                                self.spawn_boomerang(player, name, level)
                            elif w["behavior"] == "orbit":
                                self.spawn_orbiting_book(player, name, level, i, count)
                            elif w["behavior"] == "fan_shot":
                                self.spawn_fan_shot(player, name, level, i, count)
                            elif w["behavior"] == "aura":
                                self.spawn_aura(player, name, level)
                            elif w["behavior"] == "whip":
                                self.spawn_whip(player, name, level)
                    base_cd = w["cooldown"]
                    cd_bonus = sum(u.get("cooldown", 0) for u in w["upgrade_table"][:level-1])
                    player.attributes[cooldown_key] = max(5, base_cd + cd_bonus)
                else:
                    player.attributes[cooldown_key] -= 1

        # Move and update weapons
        player = self.get_particle(PLAYER)
        
        # 修改强制生成武器的部分，添加对圣经武器的特殊处理
        # 每15秒手动强制生成一次所有武器，用于调试武器可见性
        if self.game_timer % 900 == 1:
            print("手动强制生成所有武器类型")
            player = self.get_particle(PLAYER)
            if player:
                # 获取玩家武器
                weapons = player.attributes.get("weapons", {})
                
                # 创建一个标志变量，记录是否已经生成过圣经
                bible_generated = False
                
                # 强制生成所有等级大于0的武器
                for w_type in WEAPON_TYPES:
                    name = w_type["name"]
                    level = weapons.get(name, 0)
                    if level <= 0:  # 跳过等级为0的武器
                        continue
                        
                    behavior = w_type["behavior"]
                    
                    # 对圣经武器做特殊处理，只生成一次
                    if behavior == "orbit" and name == "KingBible":  # KingBible
                        if not bible_generated:
                            lvl = min(level, len(KING_BIBLE_LEVELS)) - 1
                            props = KING_BIBLE_LEVELS[lvl]
                            amount = props["amount"]
                            for i in range(amount):
                                self.spawn_orbiting_book(player, name, level, i, amount)
                            bible_generated = True
                    elif behavior == "horizontal_slash":  # Whip
                        self.spawn_whip(player, name, level)
                    elif behavior == "homing_missile":  # MagicWand
                        self.spawn_homing_missile(player, name, level)
                    elif behavior == "straight_shot":  # Knife
                        self.spawn_straight_shot(player, name, level)
                    elif behavior == "arc_throw":  # Axe
                        self.spawn_arc_throw(player, name, level, 0, 1)
                    elif behavior == "boomerang":  # Cross
                        self.spawn_boomerang(player, name, level)
                    elif behavior == "fan_shot":  # FireWand
                        self.spawn_fan_shot(player, name, level, 0, 1)
                    elif behavior == "aura":  # Garlic
                        self.spawn_aura(player, name, level)
                print("已生成所有等级大于0的武器类型的粒子")
                
        # 每10秒手动强制生成一次圣经，用于调试
        if self.game_timer % 600 == 1:
            print("手动强制生成圣经武器")
            player = self.get_particle(PLAYER)
            if player:
                # 确保玩家有圣经武器
                weapons = player.attributes.get("weapons", {})
                if "KingBible" not in weapons or weapons["KingBible"] <= 0:
                    weapons["KingBible"] = 1
                    player.attributes["weapons"] = weapons
                    print("给玩家添加了圣经武器")
                
                # 强制生成圣经
                level = weapons.get("KingBible", 1)
                if level > 0:  # 确保等级大于0
                    lvl = min(level, len(KING_BIBLE_LEVELS)) - 1
                    props = KING_BIBLE_LEVELS[lvl]
                    amount = props["amount"]
                    for i in range(amount):
                        self.spawn_orbiting_book(player, "KingBible", level, i, amount)
        
        # Process weapon timers and remove expired weapons
        weapons_to_remove = []
        for weapon in self.get_particles(WEAPON):
            wname = weapon.attributes.get("weapon_name", "")
            
            # 基本移动逻辑 - 对于普通武器（不是orbit或特殊武器）
            if "orbit_radius" not in weapon.attributes and "whip_timer" not in weapon.attributes and "duration" not in weapon.attributes:
                # 如果没有vx和vy，使用角度和速度更新位置
                if "vx" not in weapon.attributes and "vy" not in weapon.attributes:
                    angle_rad = math.radians(weapon.attributes.get("angle", 0))
                    speed = weapon.attributes.get("speed", WEAPON_SPEED)
                    weapon.x += math.cos(angle_rad) * speed
                    weapon.y += math.sin(angle_rad) * speed

            # Process whip timer (for Whip weapon)
            if "whip_timer" in weapon.attributes:
                weapon.attributes["whip_timer"] -= 1
                if weapon.attributes["whip_timer"] <= 0:
                    weapons_to_remove.append(weapon)
            
            # Process duration timer (for KingBible, Garlic, etc.)
            if "duration" in weapon.attributes:
                weapon.attributes["duration"] -= 1
                if weapon.attributes["duration"] <= 0:
                    weapons_to_remove.append(weapon)
            
            # Process boomerang timer
            if "boomerang_timer" in weapon.attributes:
                weapon.attributes["boomerang_timer"] -= 1
                # When timer reaches zero, reverse direction to return to player
                if weapon.attributes["boomerang_timer"] == 0:
                    if "vx" in weapon.attributes and "vy" in weapon.attributes:
                        weapon.attributes["vx"] *= -1
                        weapon.attributes["vy"] *= -1
            
            # Update orbit positions (for KingBible)
            if "orbit_radius" in weapon.attributes and "orbit_angle" in weapon.attributes:
                # 更新KingBible武器的目标冷却时间
                if weapon.attributes.get("weapon_name") == "KingBible" and "hit_cooldown" in weapon.attributes:
                    # 遍历所有敌人冷却，减少计时器
                    cooldowns = weapon.attributes["hit_cooldown"]
                    for eid in list(cooldowns.keys()):
                        if cooldowns[eid] > 0:
                            cooldowns[eid] -= 1
                        else:
                            del cooldowns[eid]  # 移除已过期的冷却
                
                # 找到正确的玩家
                target_player = None
                if player and player.attributes.get("id") == weapon.attributes.get("target_player_id", -1):
                    target_player = player
                else:
                    # 如果当前玩家不是目标，尝试查找目标玩家
                    for p in self.get_particles(PLAYER):
                        if p.attributes.get("id") == weapon.attributes.get("target_player_id", -1):
                            target_player = p
                            break
                
                # 如果找到玩家，更新轨道位置
                if target_player:
                    # 更新轨道角度
                    speed_factor = weapon.attributes.get("speed", 1.0)
                    weapon.attributes["orbit_angle"] += 6 * speed_factor  # 旋转速度加倍
                    
                    # 计算新位置
                    angle_rad = math.radians(weapon.attributes["orbit_angle"])
                    radius = weapon.attributes["orbit_radius"]
                    weapon.x = target_player.x + radius * math.cos(angle_rad)
                    weapon.y = target_player.y + radius * math.sin(angle_rad)
                else:
                    # 如果找不到玩家，将武器标记为过期
                    weapons_to_remove.append(weapon)
            
            # Update homing projectiles
            if "target_id" in weapon.attributes or weapon.attributes.get("weapon_name") == "MagicWand":
                # Find target enemy
                target = None
                for enemy_type in [ENEMY, ENEMY_ELITE]:
                    for enemy in self.get_particles(enemy_type):
                        if "target_id" in weapon.attributes and enemy.attributes.get("id") == weapon.attributes["target_id"]:
                            target = enemy
                            break
                # If target exists, home in on it
                if target:
                    dx = target.x - weapon.x
                    dy = target.y - weapon.y
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist > 0:
                        dx = dx / dist * weapon.attributes.get("speed", WEAPON_SPEED)
                        dy = dy / dist * weapon.attributes.get("speed", WEAPON_SPEED)
                        weapon.x += dx
                        weapon.y += dy
                        weapon.attributes["angle"] = math.degrees(math.atan2(dy, dx))
                        weapon.attributes["vx"] = dx
                        weapon.attributes["vy"] = dy
                        weapon.attributes["last_vx"] = dx
                        weapon.attributes["last_vy"] = dy
                else:
                    # 目标消失则按原方向继续运动
                    vx = weapon.attributes.get("vx", 0)
                    vy = weapon.attributes.get("vy", 0)
                    weapon.x += vx
                    weapon.y += vy
                    weapon.attributes["last_vx"] = vx
                    weapon.attributes["last_vy"] = vy
                # 超出边界移除
                if (weapon.x < -WEAPON_SIZE or weapon.x > SPATIAL_RESOLUTION + WEAPON_SIZE or
                    weapon.y < -WEAPON_SIZE or weapon.y > SPATIAL_RESOLUTION + WEAPON_SIZE):
                    weapons_to_remove.append(weapon)
                continue
            # 魔杖粒子无target_id时直线运动
            if wname == "MagicWand" and "target_id" not in weapon.attributes and "vx" in weapon.attributes and "vy" in weapon.attributes:
                vx = weapon.attributes.get("vx", 0)
                vy = weapon.attributes.get("vy", 0)
                weapon.x += vx
                weapon.y += vy
                weapon.attributes["last_vx"] = vx
                weapon.attributes["last_vy"] = vy
                if (weapon.x < -WEAPON_SIZE or weapon.x > SPATIAL_RESOLUTION + WEAPON_SIZE or
                    weapon.y < -WEAPON_SIZE or weapon.y > SPATIAL_RESOLUTION + WEAPON_SIZE):
                    weapons_to_remove.append(weapon)
                continue
        # 魔杖粒子碰撞穿透处理，击中第一个敌人后移除target_id
        for weapon in self.get_particles(WEAPON):
            if weapon.attributes.get("weapon_name") == "MagicWand":
                for enemy_type in [ENEMY, ENEMY_ELITE]:
                    for enemy in self.get_particles(enemy_type):
                        if self.check_collision(weapon, enemy, WEAPON_SIZE, ENEMY_SIZE if enemy_type == ENEMY else ELITE_SIZE):
                            # 先造成伤害
                            self.apply_damage(weapon, enemy, weapon.attributes.get("damage", 1))
                            # 只在首次穿透时移除target_id并设置vx/vy
                            if "target_id" in weapon.attributes and not weapon.attributes.get("has_pierced"):
                                weapon.attributes["has_pierced"] = True
                                weapon.attributes.pop("target_id")
                                weapon.attributes["vx"] = weapon.attributes.get("last_vx", 0)
                                weapon.attributes["vy"] = weapon.attributes.get("last_vy", 0)
                            # 穿透计数
                            if "pierce_count" in weapon.attributes:
                                weapon.attributes["pierce_count"] -= 1
                                if weapon.attributes["pierce_count"] <= 0:
                                    weapons_to_remove.append(weapon)
                            else:
                                weapons_to_remove.append(weapon)
                            break

        # Remove expired weapons
        for weapon in weapons_to_remove:
            if weapon in self.particles:  # Check if weapon still exists
                self.remove_particle(weapon)
                
        # Move enemies towards player and check for despawning
        enemies_to_remove = []
        
        # Process all types of enemies (regular and elite)
        for enemy_type in [ENEMY, ENEMY_ELITE]:
            for enemy in self.get_particles(enemy_type):
                if enemy.attributes.get("is_dying"):
                    continue  # 死亡动画期间不移动
                # 边界强制反弹修正
                safe_margin = 10
                center_x = SPATIAL_RESOLUTION / 2
                center_y = SPATIAL_RESOLUTION / 2
                if enemy.x < safe_margin:
                    enemy.x = safe_margin
                if enemy.y < safe_margin:
                    enemy.y = safe_margin
                if enemy.x > SPATIAL_RESOLUTION - safe_margin:
                    enemy.x = SPATIAL_RESOLUTION - safe_margin
                if enemy.y > SPATIAL_RESOLUTION - safe_margin:
                    enemy.y = SPATIAL_RESOLUTION - safe_margin
                # Calculate direction to player
                dx = player.x - enemy.x
                dy = player.y - enemy.y
                dist = math.sqrt(dx * dx + dy * dy)
                # 如果方向为0，直接赋值为(1,1)
                if dx == 0 and dy == 0:
                    dx, dy = 1, 1
                    dist = math.sqrt(2)
                # Check if enemy should despawn due to distance
                if dist > DESPAWN_DISTANCE:
                    enemies_to_remove.append(enemy)
                    continue
                # Check if enemy is stuck (near corners or edges)
                enemy_size = ELITE_SIZE if enemy.kind == ENEMY_ELITE else ENEMY_SIZE
                is_stuck = False
                margin = 5
                if ((enemy.x < margin and enemy.y < margin) or  # top-left corner
                   (enemy.x < margin and enemy.y > SPATIAL_RESOLUTION - margin) or  # bottom-left corner
                   (enemy.x > SPATIAL_RESOLUTION - margin and enemy.y < margin) or  # top-right corner
                   (enemy.x > SPATIAL_RESOLUTION - margin and enemy.y > SPATIAL_RESOLUTION - margin) or  # bottom-right corner
                   (enemy.x < margin) or  # left edge
                   (enemy.x > SPATIAL_RESOLUTION - margin) or  # right edge
                   (enemy.y < margin) or  # top edge
                   (enemy.y > SPATIAL_RESOLUTION - margin)):  # bottom edge
                    is_stuck = True
                # Make sure the direction vector is normalized
                if dist < 1:
                    dx = center_x - enemy.x
                    dy = center_y - enemy.y
                    norm = math.sqrt(dx * dx + dy * dy)
                    if norm > 0:
                        dx /= norm
                        dy /= norm
                else:
                    dx /= dist
                    dy /= dist
                # 边界修正：如果靠近左上角等边界，强制向中心加大扰动
                if (enemy.x < margin and enemy.y < margin) or (enemy.x < margin) or (enemy.y < margin):
                    center_x = SPATIAL_RESOLUTION / 2
                    center_y = SPATIAL_RESOLUTION / 2
                    dx = (center_x - enemy.x) / SPATIAL_RESOLUTION + random.uniform(-0.3, 0.3)
                    dy = (center_y - enemy.y) / SPATIAL_RESOLUTION + random.uniform(-0.3, 0.3)
                    norm = math.sqrt(dx*dx + dy*dy)
                    if norm > 0:
                        dx /= norm
                        dy /= norm
                
                # Only move enemy if not in knockback
                if "knockback_timer" not in enemy.attributes or enemy.attributes["knockback_timer"] <= 0:
                    # If stuck, apply special movement to help unstick
                    if is_stuck:
                        # Move toward center of screen if stuck at edge
                        center_x = SPATIAL_RESOLUTION / 2
                        center_y = SPATIAL_RESOLUTION / 2
                        
                        # Vector from enemy to center
                        to_center_x = center_x - enemy.x
                        to_center_y = center_y - enemy.y
                        
                        # Normalize
                        to_center_dist = math.sqrt(to_center_x * to_center_x + to_center_y * to_center_y)
                        if to_center_dist > 0:
                            to_center_x /= to_center_dist
                            to_center_y /= to_center_dist
                        
                        # Blend movement: 70% toward center, 30% toward player when stuck
                        blended_dx = 0.7 * to_center_x + 0.3 * dx
                        blended_dy = 0.7 * to_center_y + 0.3 * dy
                        
                        # Normalize blended direction
                        blended_dist = math.sqrt(blended_dx * blended_dx + blended_dy * blended_dy)
                        if blended_dist > 0:
                            blended_dx /= blended_dist
                            blended_dy /= blended_dist
                        
                        # Move with increased speed to escape edge
                        next_x = enemy.x + blended_dx * enemy.attributes["speed"] * 1.5
                        next_y = enemy.y + blended_dy * enemy.attributes["speed"] * 1.5
                    else:
                        # Normal movement toward player
                        next_x = enemy.x + dx * enemy.attributes["speed"]
                        next_y = enemy.y + dy * enemy.attributes["speed"]
                    
                    # Additional checks to prevent sticking at exact boundaries
                    if (next_x <= 0 and dx < 0) or (next_x >= SPATIAL_RESOLUTION and dx > 0):
                        # If moving toward edge, adjust position to prevent sticking
                        next_x = max(enemy_size/2, min(SPATIAL_RESOLUTION - enemy_size/2, next_x))
                        # Add slight random movement in y direction to help unstick
                        next_y += random.uniform(-2, 2)
                    
                    if (next_y <= 0 and dy < 0) or (next_y >= SPATIAL_RESOLUTION and dy > 0):
                        # If moving toward edge, adjust position to prevent sticking
                        next_y = max(enemy_size/2, min(SPATIAL_RESOLUTION - enemy_size/2, next_y))
                        # Add slight random movement in x direction to help unstick
                        next_x += random.uniform(-2, 2)
                    
                    # Ensure enemy always stays within valid bounds (with small buffer)
                    buffer = enemy_size / 4
                    next_x = max(buffer, min(SPATIAL_RESOLUTION - buffer, next_x))
                    next_y = max(buffer, min(SPATIAL_RESOLUTION - buffer, next_y))
                    
                    # Update enemy position
                    enemy.x = next_x
                    enemy.y = next_y

                # Check for collisions with player
                if self.check_collision(player, enemy, PLAYER_SIZE, enemy_size):
                    # Instead of instant reset, apply damage to player
                    damage = enemy.attributes["damage"]
                    
                    # Store old HP value for section detection
                    old_hp = player.health_system.current_hp if player.health_system else 0
                    
                    # Apply damage
                    is_alive = self.apply_damage(enemy, player, damage)
                    
                    # Trigger damage effects
                    if player.health_system:
                        # Start HP animation transition
                        self.hp_transition_timer = HP_TRANSITION_DURATION
                        
                        # Start player blink effect
                        self.player_blink_timer = PLAYER_BLINK_DURATION
                        
                        # Check for HP section change
                        new_section = int(player.health_system.current_hp / HP_THRESHOLD)
                        if new_section < self.hp_section:
                            # HP dropped to a new section, trigger blinking
                            self.hp_blink_timer = HP_BLINK_DURATION
                            self.hp_section = new_section
                            # TODO: Play sound effect here once sound system is implemented
                            print("HP section changed! Playing sound effect...")
                    
                    # Show game over if player dies
                    if not is_alive:
                        self.show_game_over()
                        return
                    
                    # Move enemy away slightly to prevent continuous damage
                    enemy.x = enemy.x - dx * 10
                    enemy.y = enemy.y - dy * 10

                # Check for collisions with weapons
                for weapon in self.get_particles(WEAPON):
                    if self.check_collision(weapon, enemy, WEAPON_SIZE, enemy_size):
                        # Apply damage to enemy using health system
                        weapon_damage = weapon.attributes["damage"]
                        
                        # Store old HP value for damage calculation
                        old_hp = enemy.health_system.current_hp if enemy.health_system else 0
                        
                        # Start enemy blinking effect
                        enemy.attributes["blink_timer"] = PLAYER_BLINK_DURATION  # Use same duration as player
                        
                        # Apply damage using health system
                        is_alive = self.apply_damage(weapon, enemy, weapon_damage)
                        
                        # Calculate actual damage dealt
                        if enemy.health_system:
                            actual_damage = old_hp - enemy.health_system.current_hp
                        else:
                            actual_damage = weapon_damage
                        
                        # Apply knockback effect
                        knockback_dx = enemy.x - player.x
                        knockback_dy = enemy.y - player.y
                        
                        # Normalize direction vector
                        knockback_dist = math.sqrt(knockback_dx * knockback_dx + knockback_dy * knockback_dy)
                        if knockback_dist > 0:
                            knockback_dx /= knockback_dist
                            knockback_dy /= knockback_dist
                        else:
                            knockback_dx = random.uniform(-1, 1)
                            knockback_dy = random.uniform(-1, 1)
                        
                        # Set knockback attributes
                        enemy.attributes["knockback_timer"] = KNOCKBACK_DURATION
                        enemy.attributes["knockback_dx"] = knockback_dx
                        enemy.attributes["knockback_dy"] = knockback_dy
                        
                        # Create damage text particle
                        self.spawn_damage_text(enemy.x, enemy.y, actual_damage)
                        
                        # If enemy died, handle it
                        if not is_alive:
                            self.score += 10
                            
                            # 50% chance to drop XP (or always drop for elites)
            # frame.add_text(Text(10, 180, "WASD to move", "#FFFFFF", 20))
            
        # Note: Debug toolbar should only be drawn in draw_debug_toolbar method, not in step

        # 经验拾取判定
        xp_to_remove = []
        for xp in self.get_particles(XP):
            if self.check_collision(player, xp, PLAYER_SIZE, XP_SIZE):
                xp_value = 10  # 默认经验值
                self.xp += xp_value
                player.attributes["xp"] = self.xp
                if self.xp >= self.xp_to_next_level:
                    self.level += 1
                    self.xp -= self.xp_to_next_level
                    self.xp_to_next_level = self.level * 50
                    print("玩家升级! 新等级: {}".format(self.level))
                    self.show_upgrade_menu()
                xp_to_remove.append(xp)
        for xp in xp_to_remove:
            self.remove_particle(xp)

        # XP吸附效果
        for xp in self.get_particles(XP):
            dx = player.x - xp.x
            dy = player.y - xp.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < XP_MAGNET_RANGE:
                # 吸附标记
                xp.attributes["moving_to_player"] = True
                # 计算吸附速度
                speed = xp.attributes.get("speed", XP_MAGNET_SPEED_MIN)
                speed = min(speed + XP_ACCELERATION, XP_MAGNET_SPEED_MAX)
                xp.attributes["speed"] = speed
                # 单位向量
                if dist > 0:
                    dx /= dist
                    dy /= dist
                # 更新位置
                xp.x += dx * speed
                xp.y += dy * speed
            else:
                # 未吸附时速度归零
                xp.attributes["speed"] = XP_MAGNET_SPEED_MIN
                xp.attributes["moving_to_player"] = False

        # 死亡动画处理
        dying_enemies = [e for e in self.particles if e.kind in [ENEMY, ENEMY_ELITE] and e.attributes.get("is_dying")]
        for enemy in dying_enemies:
            timer = enemy.attributes.get("death_anim_timer", 0)
            if timer > 0:
                enemy.attributes["death_anim_timer"] -= 1
                progress = 1 - enemy.attributes["death_anim_timer"] / 30
                # 尺寸缩小
                if enemy.kind == ENEMY:
                    enemy.attributes["death_anim_size"] = ENEMY_SIZE * (1 - progress)
                else:
                    enemy.attributes["death_anim_size"] = ELITE_SIZE * (1 - progress)
                # 颜色闪白
                enemy.attributes["death_anim_white"] = True
            else:
                if enemy in self.particles:
                    self.remove_particle(enemy)

        for weapon in self.get_particles(WEAPON):
            wname = weapon.attributes.get("weapon_name", "")
            # 魔杖粒子跟踪目标，击中第一个敌人后转为直线运动
            if wname == "MagicWand" and "target_id" in weapon.attributes:
                # 查找目标
                target = None
                for enemy_type in [ENEMY, ENEMY_ELITE]:
                    for enemy in self.get_particles(enemy_type):
                        if enemy.attributes.get("id") == weapon.attributes["target_id"]:
                            target = enemy
                            break
                if target:
                    dx = target.x - weapon.x
                    dy = target.y - weapon.y
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist > 0:
                        dx = dx / dist * weapon.attributes.get("speed", WEAPON_SPEED)
                        dy = dy / dist * weapon.attributes.get("speed", WEAPON_SPEED)
                        weapon.x += dx
                        weapon.y += dy
                        weapon.attributes["angle"] = math.degrees(math.atan2(dy, dx))
                        weapon.attributes["vx"] = dx
                        weapon.attributes["vy"] = dy
                        weapon.attributes["last_vx"] = dx
                        weapon.attributes["last_vy"] = dy
                else:
                    vx = weapon.attributes.get("vx", 0)
                    vy = weapon.attributes.get("vy", 0)
                    weapon.x += vx
                    weapon.y += vy
                    weapon.attributes["last_vx"] = vx
                    weapon.attributes["last_vy"] = vy
                if (weapon.x < -WEAPON_SIZE or weapon.x > SPATIAL_RESOLUTION + WEAPON_SIZE or
                    weapon.y < -WEAPON_SIZE or weapon.y > SPATIAL_RESOLUTION + WEAPON_SIZE):
                    weapons_to_remove.append(weapon)
                continue
            if wname == "MagicWand" and "target_id" not in weapon.attributes and "vx" in weapon.attributes and "vy" in weapon.attributes:
                vx = weapon.attributes.get("vx", 0)
                vy = weapon.attributes.get("vy", 0)
                weapon.x += vx
                weapon.y += vy
                weapon.attributes["last_vx"] = vx
                weapon.attributes["last_vy"] = vy
                if (weapon.x < -WEAPON_SIZE or weapon.x > SPATIAL_RESOLUTION + WEAPON_SIZE or
                    weapon.y < -WEAPON_SIZE or weapon.y > SPATIAL_RESOLUTION + WEAPON_SIZE):
                    weapons_to_remove.append(weapon)
                continue
        # 魔杖粒子碰撞穿透处理，击中第一个敌人后移除target_id
        for weapon in self.get_particles(WEAPON):
            if weapon.attributes.get("weapon_name") == "MagicWand":
                for enemy_type in [ENEMY, ENEMY_ELITE]:
                    for enemy in self.get_particles(enemy_type):
                        if self.check_collision(weapon, enemy, WEAPON_SIZE, ENEMY_SIZE if enemy_type == ENEMY else ELITE_SIZE):
                            # 先造成伤害
                            self.apply_damage(weapon, enemy, weapon.attributes.get("damage", 1))
                            # 只在首次穿透时移除target_id并设置vx/vy
                            if "target_id" in weapon.attributes and not weapon.attributes.get("has_pierced"):
                                weapon.attributes["has_pierced"] = True
                                weapon.attributes.pop("target_id")
                                weapon.attributes["vx"] = weapon.attributes.get("last_vx", 0)
                                weapon.attributes["vy"] = weapon.attributes.get("last_vy", 0)
                            # 穿透计数
                            if "pierce_count" in weapon.attributes:
                                weapon.attributes["pierce_count"] -= 1
                                if weapon.attributes["pierce_count"] <= 0:
                                    weapons_to_remove.append(weapon)
                            else:
                                weapons_to_remove.append(weapon)
                            break

    def agent_action(self, last_action=None):
        """
        AI agent that tries to avoid enemies and collect XP
        """
        # In non-playing states, we need to simulate mouse/click actions
        if self.game_state != STATE_PLAYING:
            # Simulate clicks in different menu states
            if self.game_state == STATE_START_MENU:
                # Click the start button
                mouse_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)
                self.handle_input(None, mouse_pos, True)
                return [False, False, False, False, False]
            
            elif self.game_state == STATE_UPGRADE_MENU:
                # Select a random upgrade option
                if self.upgrade_options:
                    option_index = random.randint(0, len(self.upgrade_options) - 1)
                    button_y = SCREEN_HEIGHT // 2 - 50 + option_index * (BUTTON_HEIGHT + 20)
                    mouse_pos = (SCREEN_WIDTH // 2, button_y + BUTTON_HEIGHT // 2)
                    self.handle_input(None, mouse_pos, True)
                return [False, False, False, False, False]
                
            elif self.game_state == STATE_GAME_OVER:
                # Click the restart button
                mouse_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)
                self.handle_input(None, mouse_pos, True)
                return [False, False, False, False, False]
        
        # Normal playing state AI
        player = self.get_particle(PLAYER)
        if not player:
            return [False, False, False, False]

        # Get nearest enemy and XP
        nearest_enemy = None
        nearest_enemy_dist = float('inf')
        nearest_xp = None
        nearest_xp_dist = float('inf')

        for enemy_type in [ENEMY, ENEMY_ELITE]:
            for enemy in self.get_particles(enemy_type):
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

    def draw_start_menu(self, frame):
        """Draw the start menu screen"""
        # Background
        frame.add_rectangle(Rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, "#000000"))
        
        # Title
        frame.add_text(Text(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, "Vampire Survivor", "#FFFFFF", 40))
        
        # Start button
        button_background = BUTTON_HOVER_COLOR if self.is_point_in_rect(
            self.mouse_pos[0], self.mouse_pos[1],
            SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 50,
            BUTTON_WIDTH, BUTTON_HEIGHT
        ) else BUTTON_COLOR
        
        frame.add_rectangle(Rectangle(
            SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 50,
            BUTTON_WIDTH, BUTTON_HEIGHT,
            button_background
        ))
        
        frame.add_text(Text(
            SCREEN_WIDTH // 2 - 30,
            SCREEN_HEIGHT // 2 + 80,
            "Start",
            BUTTON_TEXT_COLOR,
            20
        ))
        
        # Instructions
        frame.add_text(Text(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 150, "WASD to move, survive as long as possible!", "#CCCCCC", 16))

    def draw_upgrade_menu(self, frame):
        """Draw the upgrade menu screen，严格层级：背景-按钮-文本-烟花"""
        # 1. 半透明界面背景（遮住粒子但不完全不透明）
        frame.add_rectangle(Rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, "#222244CC"))
        # 2. 动画缩放
        scale = 1.0
        if hasattr(self, 'upgrade_anim_timer') and self.upgrade_anim_timer > 0:
            scale = 0.7 + 0.3 * (1 - self.upgrade_anim_timer / 12)
            self.upgrade_anim_timer -= 1
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        def sx(x): return int((x - cx) * scale + cx)
        def sy(y): return int((y - cy) * scale + cy)
        # 3. 按钮（背景之上）
        for i, upgrade in enumerate(self.upgrade_options):
            button_y = cy - 50 + i * (BUTTON_HEIGHT + 20)
            btn_x = sx(cx - BUTTON_WIDTH // 2)
            btn_y = sy(button_y)
            btn_w = max(60, int(BUTTON_WIDTH * scale))
            btn_h = max(20, int(BUTTON_HEIGHT * scale))
            frame.add_rectangle(Rectangle(
                btn_x,
                btn_y,
                btn_w,
                btn_h,
                BUTTON_COLOR
            ))
        # 4. 文本（按钮之上）
        levelup_text = "Level Up!"
        font_size = max(10, int(40 * scale))
        text_width = len(levelup_text) * font_size * 0.5
        frame.add_text(Text(sx(cx - text_width // 2), sy(cy - 150), levelup_text, "#FFFFFF", font_size))
        for i, upgrade in enumerate(self.upgrade_options):
            button_y = cy - 50 + i * (BUTTON_HEIGHT + 20)
            btn_x = sx(cx - BUTTON_WIDTH // 2)
            btn_y = sy(button_y)
            btn_w = max(60, int(BUTTON_WIDTH * scale))
            btn_h = max(20, int(BUTTON_HEIGHT * scale))
            upgrade_text = ""
            if upgrade["type"] == "new_weapon":
                upgrade_text = "New: {}".format(upgrade["display"])
            elif upgrade["type"] == "upgrade_weapon":
                upgrade_text = "Upgrade: {} Lv.{}".format(upgrade["display"], upgrade["level"])
            else:
                upgrade_text = "{}".format(upgrade["display"])
            text_x = btn_x + btn_w // 2 - len(upgrade_text) * 5
            text_y = btn_y + btn_h // 2 + 5
            frame.add_text(Text(
                text_x,
                text_y,
                upgrade_text,
                BUTTON_TEXT_COLOR,
                max(10, int(18 * scale))
            ))
        # 5. 烟花特效（最上层）
        if hasattr(self, 'upgrade_fireworks'):
            for fw in self.upgrade_fireworks:
                fw[0] += math.cos(fw[4]) * fw[5]
                fw[1] += math.sin(fw[4]) * fw[5]
                fw[2] = max(1, fw[2] - 0.2)
                fw[6] += 1
                frame.add_circle(Circle(fw[0], fw[1], fw[2], fw[3]))
            self.upgrade_fireworks = [fw for fw in self.upgrade_fireworks if fw[6] < 30]

    def draw_game_over(self, frame):
        """Draw the game over screen"""
        # Darkened background
        frame.add_rectangle(Rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, "#00000088"))
        
        # Game over text
        frame.add_text(Text(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 - 100, "Game Over", "#FF0000", 50))
        
        # Score
        frame.add_text(Text(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 30, f"Score: {self.score}", "#FFFFFF", 30))
        
        # Time survived
        time_str = self.format_time(self.game_timer)
        frame.add_text(Text(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 10, f"Time Survived: {time_str}", "#FFFFFF", 30))
        
        # Restart button
        button_background = BUTTON_HOVER_COLOR if self.is_point_in_rect(
            self.mouse_pos[0], self.mouse_pos[1],
            SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 80,
            BUTTON_WIDTH, BUTTON_HEIGHT
        ) else BUTTON_COLOR
        
        frame.add_rectangle(Rectangle(
            SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 80,
            BUTTON_WIDTH, BUTTON_HEIGHT,
            button_background
        ))
        
        frame.add_text(Text(
            SCREEN_WIDTH // 2 - 40,
            SCREEN_HEIGHT // 2 + 110,
            "Restart",
            BUTTON_TEXT_COLOR,
            20
        ))

    def spawn_damage_text(self, x, y, damage_amount):
        """Spawn a damage text particle at the given position"""
        # Format damage as int
        if int(damage_amount) <= 0:
            return  # 伤害为0不显示跳字
        damage_text = str(int(damage_amount))
        # Create damage text particle
        self.particles.append(
            Particle(
                DAMAGE_TEXT,
                x,
                y,
                attributes={
                    "id": self.next_id,
                    "text": damage_text,
                    "timer": DAMAGE_TEXT_DURATION,
                    "color": "#FFFFFF",  # 白色
                    "size": 24,  # 字号加倍（原来是16）
                    "alpha": 255
                }
            )
        )
        self.next_id += 1

    def apply_damage(self, attacker, defender, damage):
        """
        应用伤害从攻击者到防御者
        """
        # 圣经冷却处理，未真正造成伤害时直接return True，不显示跳字
        if attacker.attributes.get("weapon_name") == "KingBible":
            cooldowns = attacker.attributes.setdefault("hit_cooldown", {})
            eid = int(defender.attributes["id"])
            if cooldowns.get(eid, 0) > 0:
                return True  # 冷却中直接返回，不显示跳字
            cooldowns[eid] = 30
            level = attacker.attributes.get("level", 1)
            custom_damage = self.get_kingbible_damage(level)
            if custom_damage:
                damage = custom_damage
        if damage <= 0:
            damage = 1
        if defender.health_system:
            old_hp = defender.health_system.current_hp
            is_alive = defender.take_damage(damage)
            # 只有敌人被玩家或武器攻击时才显示伤害跳字，且实际伤害大于0才显示
            if defender.kind in ["enemy", "enemy_elite"] and attacker.kind not in ["enemy", "enemy_elite"]:
                actual_damage = old_hp - defender.health_system.current_hp if defender.health_system else damage
                if actual_damage > 0:
                    self.spawn_damage_text(defender.x, defender.y, actual_damage)
            if not is_alive and defender.kind in ["enemy", "enemy_elite"]:
                self.on_particle_death(defender, attacker, show_death_anim=True)
            return is_alive
        else:
            return True

    def get_kingbible_damage(self, level):
        if level <= 3:
            return 10
        elif level <= 6:
            return 20
        else:
            return 30
    
    def on_particle_death(self, dead_particle, killer_particle=None, show_death_anim=False):
        """
        处理粒子死亡的事件
        """
        if dead_particle.kind in ["enemy", "enemy_elite"]:
            self.score += 10 if dead_particle.kind == "enemy" else 30
            should_drop_xp = (dead_particle.kind == "enemy_elite") or (random.random() < XP_DROP_CHANCE)
            if should_drop_xp:
                xp_value = dead_particle.attributes.get("xp_value", 10)
                self.spawn_xp(dead_particle.x, dead_particle.y)
            # 死亡动画：闪白+缩小
            if show_death_anim:
                dead_particle.attributes["death_anim_timer"] = 30  # 30帧=500ms
                dead_particle.attributes["death_anim_progress"] = 0
                dead_particle.attributes["is_dying"] = True
            else:
                if dead_particle in self.particles:
                    self.remove_particle(dead_particle)
        else:
            if dead_particle in self.particles:
                self.remove_particle(dead_particle)