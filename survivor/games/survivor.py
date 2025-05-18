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
BLOOD = "blood"  # 新增：血液粒子类型

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
ENEMY_SPEED_MIN = 3
ENEMY_SPEED_MAX = 4
ELITE_SPEED_MULTIPLIER = 1.5  # Elite enemies move faster
ENEMY_SPEED_REDUCTION = 0.2  # 全局敌人速度减速系数
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
        "size": 28,
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
    "Knife": {
        "main": "#FFFFFF",  # 主体为白色
        "border": "#8B4513"  # 褐色描边
    },
    "Axe": "#FF9900",
    "Cross": "#FFD700",
    "KingBible": "#0066FF",
    "FireWand": "#FF6600",
    "Garlic": "#FFFF99",
}

BLOOD_PARTICLE_COUNT = 8  # 每次受伤产生的血液粒子数量
BLOOD_PARTICLE_SIZE = 3   # 血液粒子大小
BLOOD_PARTICLE_SPEED = 6  # 血液粒子初始速度
BLOOD_PARTICLE_LIFETIME = 20  # 血液粒子存活帧数

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
        self.last_move_dir = (1, 0)  # 默认向右
        self.knife_projectile_timer = 0
    
    def get_frame(self):
        """Create and return a Frame object with the current game state"""
        frame = Frame()
        # 1. 先画黑色底
        frame.add_rectangle(Rectangle(0, 0, SPATIAL_RESOLUTION, SPATIAL_RESOLUTION, "#000000"))
        
        # 2. 画血液粒子（在最底层）
        for p in self.particles:
            if p.kind == BLOOD:
                # 计算alpha值的十六进制表示
                alpha = format(p.attributes.get("alpha", 255), '02x')
                color = f"#FF0000{alpha}"  # 红色加上透明度
                frame.add_circle(Circle(p.x, p.y, p.attributes.get("size", BLOOD_PARTICLE_SIZE), color))
        
        # 3. 画敌人（普通敌人和精英敌人）
        for p in self.particles:
            if p.kind in [ENEMY, ENEMY_ELITE]:
                if p.attributes.get("is_dying"):
                    size = p.attributes.get("death_anim_size", ENEMY_SIZE if p.kind == ENEMY else ELITE_SIZE)
                    color = "#FFFFFF" if p.attributes.get("death_anim_white") else (ENEMY_COLOR if p.kind == ENEMY else ELITE_COLOR)
                    frame.add_circle(Circle(p.x, p.y, max(1, size), color))
                else:
                    if "blink_timer" in p.attributes and p.attributes["blink_timer"] > 0 and p.attributes["blink_timer"] % 4 >= 2:
                        continue
                    size = ENEMY_SIZE if p.kind == ENEMY else ELITE_SIZE
                    frame.add_circle(Circle(p.x, p.y, size + 1, "#FFFFFF"))
                    frame.add_circle(Circle(p.x, p.y, size, ENEMY_COLOR if p.kind == ENEMY else ELITE_COLOR))
        
        # 4. 画经验球
        for p in self.particles:
            if p.kind == XP:
                frame.add_circle(Circle(p.x, p.y, XP_SIZE, XP_COLOR))
        
        # 5. 画武器
        for p in self.particles:
            if p.kind == WEAPON:
                weapon_name = p.attributes.get("weapon_name", "")
                weapon_type = next((w for w in WEAPON_TYPES if w["name"] == weapon_name), None)
                weapon_size = weapon_type["size"] if weapon_type else WEAPON_SIZE
                shape = weapon_type.get("shape", "circle") if weapon_type else "circle"
                angle = p.attributes.get("angle", 0)
                
                # 获取武器颜色
                if weapon_name == "Knife" and p.attributes.get("is_knife"):
                    main_color = p.attributes.get("main_color", "#FFFFFF")
                    border_color = p.attributes.get("border_color", "#8B4513")
                    shape_color = main_color
                else:
                    shape_color = WEAPON_COLORS.get(weapon_name, WEAPON_COLOR)
                
                # 特殊武器渲染
                if weapon_name == "MagicWand":
                    inner_color = "#FFFFFF"
                    outer_color = "#0055AA"
                    wand_size = weapon_size * 0.5
                    frame.add_circle(Circle(p.x, p.y, wand_size + 3, outer_color))
                    frame.add_circle(Circle(p.x, p.y, wand_size, inner_color))
                elif weapon_name == "KingBible" and shape == "rectangle":
                    side = weapon_size * 1.4
                    frame.add_rectangle(Rectangle(p.x - side/2, p.y - side/2, side, side, shape_color, angle))
                elif weapon_name == "Knife" and p.attributes.get("is_knife"):
                    frame.add_triangle(Triangle(p.x, p.y, weapon_size * 1.4, border_color, angle))
                    frame.add_triangle(Triangle(p.x, p.y, weapon_size * 1.2, main_color, angle))
                elif weapon_name == "Axe":
                    frame.add_circle(Circle(p.x, p.y, weapon_size * 0.9, "#FFA50044"))
                    frame.add_cross(Cross(p.x, p.y, weapon_size * 1.26, "#000000"))
                    frame.add_cross(Cross(p.x, p.y, weapon_size * 1.2, "#FFB700"))
                    frame.add_cross(Cross(p.x, p.y, weapon_size * 0.75, "#FFFFFF"))
                    frame.add_circle(Circle(p.x, p.y, weapon_size * 0.15, "#FFFFFF"))
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
        
        # 6. 画玩家（在最上层）
        for p in self.particles:
            if p.kind == PLAYER:
                if self.player_blink_timer > 0 and self.player_blink_timer % 4 >= 2:
                    continue
                # 检查是否有伤害效果
                if p.attributes.get("damage_effect_timer", 0) > 0:
                    frame.add_circle(Circle(p.x, p.y, PLAYER_SIZE, "#FF0000"))  # 受伤时显示红色
                else:
                    frame.add_circle(Circle(p.x, p.y, PLAYER_SIZE, PLAYER_COLOR))
                if p.health_system:
                    bar_width = 40
                    bar_height = 6
                    hp_percent = p.health_system.current_hp / p.health_system.max_hp
                    bar_x = p.x - bar_width // 2
                    bar_y = p.y - PLAYER_SIZE - 12
                    frame.add_rectangle(Rectangle(bar_x, bar_y, bar_width, bar_height, "#444444"))
                    frame.add_rectangle(Rectangle(bar_x, bar_y, int(bar_width * hp_percent), bar_height, "#FF4444" if hp_percent < 0.3 else ("#FFFF00" if hp_percent < 0.6 else "#00FF00")))
        
        # 7. 画伤害数字（最顶层）
        for p in self.particles:
            if p.kind == DAMAGE_TEXT:
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
        
        # 8. 根据游戏状态画UI
        if self.game_state == STATE_UPGRADE_MENU:
            self.draw_upgrade_menu(frame)
        elif self.game_state == STATE_PLAYING:
            self.draw_hud(frame)
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
        """Check if two particles are colliding"""
        # 调试信息：检查飞刀颜色
        if particle1.kind == WEAPON and particle1.attributes.get("weapon_name") == "Knife":
            print(f"[DEBUG] 碰撞检测前飞刀 ID:{particle1.attributes.get('id')} 颜色:{particle1.attributes.get('main_color')}")
        elif particle2.kind == WEAPON and particle2.attributes.get("weapon_name") == "Knife":
            print(f"[DEBUG] 碰撞检测前飞刀 ID:{particle2.attributes.get('id')} 颜色:{particle2.attributes.get('main_color')}")

        # 优化：只检测屏幕内的粒子
        if getattr(particle1, 'attributes', {}).get('is_dying') or getattr(particle2, 'attributes', {}).get('is_dying'):
            return False
        if not (0 <= particle1.x <= SPATIAL_RESOLUTION and 0 <= particle1.y <= SPATIAL_RESOLUTION):
            return False
        if not (0 <= particle2.x <= SPATIAL_RESOLUTION and 0 <= particle2.y <= SPATIAL_RESOLUTION):
            return False

        # 对于武器，获取其实际尺寸
        if particle1.kind == WEAPON:
            weapon_name = particle1.attributes.get("weapon_name", "")
            weapon_type = next((w for w in WEAPON_TYPES if w["name"] == weapon_name), None)
            if weapon_type:
                if weapon_name == "KingBible":
                    size1 = weapon_type["size"] * 3  # 圣经使用3倍尺寸
                elif weapon_name == "Knife":
                    size1 = weapon_type["size"] * 1.5  # 飞刀使用1.5倍尺寸
                elif weapon_name == "Axe":
                    size1 = weapon_type["size"] * 1.2  # 斧子使用1.2倍尺寸，与显示大小匹配
                else:
                    size1 = weapon_type["size"]

        if particle2.kind == WEAPON:
            weapon_name = particle2.attributes.get("weapon_name", "")
            weapon_type = next((w for w in WEAPON_TYPES if w["name"] == weapon_name), None)
            if weapon_type:
                if weapon_name == "KingBible":
                    size2 = weapon_type["size"] * 3
                elif weapon_name == "Knife":
                    size2 = weapon_type["size"] * 1.5
                elif weapon_name == "Axe":
                    size2 = weapon_type["size"] * 1.2  # 斧子使用1.2倍尺寸，与显示大小匹配
                else:
                    size2 = weapon_type["size"]

        # 对于光环类武器(Garlic)，使用属性中指定的范围
        if particle1.kind == WEAPON and particle1.attributes.get("weapon_name") == "Garlic":
            size1 = particle1.attributes.get("aura_radius", size1)
        if particle2.kind == WEAPON and particle2.attributes.get("weapon_name") == "Garlic":
            size2 = particle2.attributes.get("aura_radius", size2)
            
        # 基本圆形碰撞检测
        dx = particle1.x - particle2.x
        dy = particle1.y - particle2.y
        distance = math.sqrt(dx * dx + dy * dy)
        collision = distance < (size1 + size2) / 2
        
        # 打印碰撞信息用于调试
        if collision and (particle1.kind == WEAPON or particle2.kind == WEAPON):
            weapon = particle1 if particle1.kind == WEAPON else particle2
            weapon_name = weapon.attributes.get("weapon_name", "未知")
            if not weapon.attributes.get("is_knife", False):  # 只打印非飞刀的碰撞信息
                print(f"检测到碰撞: {weapon_name} 距离: {distance:.2f}, 碰撞阈值: {(size1 + size2) / 2:.2f}")
            
        return collision
    
    def show_upgrade_menu(self):
        """Show the upgrade menu with weapon options"""
        self.game_state = STATE_UPGRADE_MENU
        self.upgrade_anim_timer = 12  # 0.2秒动画
        # 生成烟花特效
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
        # 禁止用spawn_weapon发射Knife，强制用spawn_straight_shot
        if weapon_name == "Knife":
            print("[DEBUG] 禁止用spawn_weapon发射Knife，请用spawn_straight_shot")
            return
        w = next((w for w in WEAPON_TYPES if w["name"] == weapon_name), None)
        if not w or level <= 0:
            return
        damage = w["base_damage"] + sum(u.get("damage", 0) for u in w["upgrade_table"][:max(0,level-1)])
        if damage <= 0:
            damage = 1
        distance = 50
        x = int(player_x + distance * math.cos(math.radians(angle)))
        y = int(player_y + distance * math.sin(math.radians(angle)))
        shape = w.get("shape", "circle")
        size = w["size"]
        special_attrs = {}
        if shape == "rectangle":
            special_attrs["width"] = size * 3
            special_attrs["height"] = size
        # --- 修正：Knife带vx/vy ---
        attributes = {
            "damage": damage,
            "speed": WEAPON_SPEED,
            "angle": angle,
            "id": self.next_id,
            "weapon_name": weapon_name,
            "level": level,
            "shape": shape,
            **special_attrs
        }
        if weapon_name == "Knife":
            rad = math.radians(angle)
            attributes["vx"] = math.cos(rad) * WEAPON_SPEED
            attributes["vy"] = math.sin(rad) * WEAPON_SPEED
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

    def spawn_straight_shot(self, player, weapon_name, level, angle=None, amount=None):
        if level <= 0:
            return
        # 1. 计算伤害和穿透力
        knife_damage_table = [10, 10, 15, 15, 15, 15, 20, 20]
        knife_pierce_table = [0, 0, 0, 0, 1, 1, 1, 2]
        knife_amount_table = [1, 2, 3, 4, 4, 5, 6, 6]
        idx = min(level, 8) - 1
        damage = knife_damage_table[idx]
        pierce = knife_pierce_table[idx]
        # 如果没有指定amount，使用等级表中的值
        if amount is None:
            amount = knife_amount_table[idx]
        # 2. 计算发射角度
        if angle is None:
            if self.last_move_dir[0] == 0 and self.last_move_dir[1] == 0:
                angle = 0  # 默认向右
            else:
                angle = math.degrees(math.atan2(self.last_move_dir[1], self.last_move_dir[0]))
        print(f"[DEBUG] 飞刀发射角度: {angle}, last_move_dir: {self.last_move_dir}")
        # 3. 齐射角度错位
        spread = 10  # 总扩散角度
        if amount > 1:
            base_angle = angle - spread/2
            angle_step = spread / (amount-1) if amount > 1 else 0
        else:
            base_angle = angle
            angle_step = 0
        for i in range(amount):
            shot_angle = base_angle + i * angle_step
            rad = math.radians(shot_angle)
            vx = math.cos(rad) * 14
            vy = math.sin(rad) * 14
            # 创建粒子
            particle = Particle(
                WEAPON,
                player.x,
                player.y,
                attributes={
                    "damage": damage,
                    "speed": 14,
                    "angle": shot_angle,
                    "id": self.next_id,
                    "weapon_name": weapon_name,
                    "level": level,
                    "vx": vx,
                    "vy": vy,
                    "shape": "triangle",
                    "pierce_count": pierce,
                    "main_color": "#FFFFFF",  # 固定为白色主体
                    "border_color": "#8B4513",  # 固定为褐色描边
                    "is_knife": True,  # 标记为飞刀，防止其他逻辑修改颜色
                    "color_locked": True,  # 添加颜色锁定标记
                    "original_main_color": "#FFFFFF",  # 保存原始颜色
                    "original_border_color": "#8B4513",  # 保存原始颜色
                    "shape_color": "#FFFFFF"  # 设置shape_color为主体色
                }
            )
            print(f"[DEBUG] 创建飞刀粒子 ID:{self.next_id} 颜色:{particle.attributes.get('main_color')}")
            self.particles.append(particle)
            self.next_id += 1

    def spawn_arc_throw(self, player, weapon_name, level, i, count):
        if level <= 0:
            return
            
        # 根据玩家移动方向决定基础角度
        if self.last_move_dir[0] == 0 and self.last_move_dir[1] == 0:
            # 静止时默认向右上抛出
            if i == 0:
                base_angle = 45  # 第一个斧子右上
            else:
                base_angle = 135  # 第二个斧子左上
        else:
            # 根据移动方向计算基础角度
            move_angle = math.degrees(math.atan2(-self.last_move_dir[1], self.last_move_dir[0]))
            if move_angle < 0:
                move_angle += 360
            # 移动时斧子总是投向移动方向的上方
            if move_angle <= 90:  # 向右上移动
                base_angle = 45
            else:  # 向左上移动
                base_angle = 135
                
        # 计算发射角度（在基础角度附近扇形分布）
        angle = base_angle - 15 + (30 // max(1, count-1)) * i if count > 1 else base_angle
        
        # 基础速度和伤害（参考附件数值）
        base_speed = 8  # 基础速度
        damage = 20 if level == 1 else (40 if level <= 4 else (60 if level <= 7 else 80))
            
        # 转换角度为弧度
        rad = math.radians(angle)
        # 计算初始速度分量（添加向上的初速度）
        vx = base_speed * math.cos(rad)
        vy = -8  # 固定向上的初速度
        
        # 获取武器类型和形状
        weapon_type = next((w for w in WEAPON_TYPES if w["name"] == weapon_name), None)
        shape = weapon_type.get("shape", "cross") if weapon_type else "cross"
        size = weapon_type["size"] if weapon_type else WEAPON_SIZE
        
        print(f"[DEBUG] Spawning Axe at ({player.x}, {player.y}) with vx={vx:.1f}, vy={vy:.1f}, angle={angle}")
        
        # 创建武器粒子
        particle = Particle(
            WEAPON,
            player.x,
            player.y,
            attributes={
                "damage": damage,
                "speed": base_speed,
                "angle": angle,
                "id": self.next_id,
                "weapon_name": weapon_name,
                "level": level,
                "vx": vx,
                "vy": vy,
                "gravity": 0.4,  # 增加重力加速度使抛物线更明显
                "shape": shape,
                "size": size,
                "lifetime": 120,  # 生命周期限制（2秒）
                "initial_y": player.y  # 记录初始Y坐标
            }
        )
        print(f"[DEBUG] Created Axe particle with ID {self.next_id}")
        self.particles.append(particle)
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
                dx *= 0.7071
                dy *= 0.7071
            player.x = int(max(PLAYER_SIZE // 2, min(SPATIAL_RESOLUTION - PLAYER_SIZE // 2, player.x + dx)))
            player.y = int(max(PLAYER_SIZE // 2, min(SPATIAL_RESOLUTION - PLAYER_SIZE // 2, player.y + dy)))
            # 记录移动方向
            if dx != 0 or dy != 0:
                norm = math.sqrt(dx*dx + dy*dy)
                self.last_move_dir = (dx/norm, dy/norm)
            print("[DEBUG] 玩家移动dx,dy:", dx, dy, "last_move_dir:", self.last_move_dir)

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
            
        # Update player invincible timer
        if player.attributes.get("is_invincible", False):
            invincible_timer = player.attributes.get("invincible_timer", 0)
            if invincible_timer > 0:
                player.attributes["invincible_timer"] = invincible_timer - 1
            else:
                player.attributes["is_invincible"] = False
            
        # Update damage effect timer
        if player.attributes.get("damage_effect_timer", 0) > 0:
            player.attributes["damage_effect_timer"] -= 1
            
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
            if level > 0:
                cooldown_key = f"{name}_cooldown"
                current_cooldown = player.attributes.get(cooldown_key, 0)
                # 飞刀特殊处理
                if name == "Knife":
                    # 飞刀等级表
                    knife_amount_table = [1, 2, 3, 4, 4, 5, 6, 6]
                    knife_interval_table = [6, 6, 6, 5, 5, 4, 3, 2]  # 间隔帧数（0.1s~0.04s）
                    idx = min(level, 8) - 1
                    amount = knife_amount_table[idx]
                    interval = knife_interval_table[idx]
                    # 发射序列状态
                    if "knife_shot_seq" not in player.attributes:
                        player.attributes["knife_shot_seq"] = None
                    seq = player.attributes["knife_shot_seq"]
                    if current_cooldown <= 0 and seq is None:
                        # 冷却到0，初始化发射序列
                        player.attributes["knife_shot_seq"] = {
                            "amount": amount,
                            "interval": interval,
                            "next_shot": 0,
                            "shots_left": amount,
                            "base_angle": None  # 记录本轮齐射基准角度
                        }
                        player.attributes[cooldown_key] = 60  # 1秒冷却
                        continue
                    # 处理发射序列
                    if seq is not None:
                        if seq["shots_left"] > 0:
                            if seq["next_shot"] <= 0:
                                # 计算本轮齐射基准角度
                                if seq["base_angle"] is None:
                                    if self.last_move_dir[0] == 0 and self.last_move_dir[1] == 0:
                                        base_angle = 0
                                    else:
                                        base_angle = math.degrees(math.atan2(self.last_move_dir[1], self.last_move_dir[0]))
                                    seq["base_angle"] = base_angle
                                else:
                                    base_angle = seq["base_angle"]
                                # 计算当前发射的角度
                                shot_idx = amount - seq["shots_left"]
                                spread = 10  # 总扩散角度
                                if amount > 1:
                                    angle_step = spread / (amount - 1)
                                    shot_angle = base_angle - spread/2 + shot_idx * angle_step
                                else:
                                    shot_angle = base_angle
                                # 加入随机扰动
                                shot_angle += random.uniform(-2, 2)
                                # 发射单个飞刀
                                self.spawn_straight_shot(player, name, level, angle=shot_angle, amount=1)
                                seq["shots_left"] -= 1
                                seq["next_shot"] = seq["interval"]
                            else:
                                seq["next_shot"] -= 1
                        if seq["shots_left"] <= 0:
                            player.attributes["knife_shot_seq"] = None
                        continue
                    # 冷却递减
                    if current_cooldown > 0:
                        player.attributes[cooldown_key] -= 1
                    continue
                # 其它武器生成逻辑
                if current_cooldown <= 0:
                    # 根据武器类型调用不同的生成函数
                    if name == "MagicWand":
                        self.spawn_homing_missile(player, name, level)
                        player.attributes[cooldown_key] = w["cooldown"]
                    elif name == "KingBible":
                        # 获取当前等级的属性
                        lvl = min(level, len(KING_BIBLE_LEVELS)) - 1
                        props = KING_BIBLE_LEVELS[lvl]
                        amount = max(1, props["amount"])
                        for i in range(amount):
                            self.spawn_orbiting_book(player, name, level, i, amount)
                        player.attributes[cooldown_key] = w["cooldown"]
                    elif name == "FireWand":
                        # 获取当前等级的属性
                        amount = 1 + sum(u.get("count", 0) for u in w["upgrade_table"][:max(0,level-1)])
                        for i in range(amount):
                            self.spawn_fan_shot(player, name, level, i, amount)
                        player.attributes[cooldown_key] = w["cooldown"]
                    elif name == "Cross":
                        self.spawn_boomerang(player, name, level)
                        player.attributes[cooldown_key] = w["cooldown"]
                    elif name == "Garlic":
                        self.spawn_aura(player, name, level)
                        player.attributes[cooldown_key] = w["cooldown"]
                    elif name == "Whip":
                        self.spawn_whip(player, name, level)
                        player.attributes[cooldown_key] = w["cooldown"]
                    elif name == "Axe":
                        amount = 1 + sum(u.get("count", 0) for u in w["upgrade_table"][:max(0,level-1)])
                        for i in range(amount):
                            self.spawn_arc_throw(player, name, level, i, amount)
                        player.attributes[cooldown_key] = w["cooldown"]
                # 冷却递减
                if current_cooldown > 0:
                    player.attributes[cooldown_key] -= 1
                continue
        # ... existing code ...

        # Move and update weapons
        weapons_to_remove = []
        for weapon in self.get_particles(WEAPON):
            wname = weapon.attributes.get("weapon_name", "")
            # Knife粒子只做直线运动，彻底避免被其他逻辑影响
            if wname == "Knife" and "vx" in weapon.attributes and "vy" in weapon.attributes:
                # 保护武器颜色
                self.protect_weapon_colors(weapon)
                weapon.x += weapon.attributes["vx"]
                weapon.y += weapon.attributes["vy"]
                if (weapon.x < -WEAPON_SIZE or weapon.x > SPATIAL_RESOLUTION + WEAPON_SIZE or
                    weapon.y < -WEAPON_SIZE or weapon.y > SPATIAL_RESOLUTION + WEAPON_SIZE):
                    weapons_to_remove.append(weapon)
                continue
            # 其余武器移动逻辑...（保持原有）

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
                    
                # 处理敌人之间的碰撞
                total_repulsion_x = 0
                total_repulsion_y = 0
                collision_count = 0
                
                # 检查与其他敌人的碰撞
                for other_type in [ENEMY, ENEMY_ELITE]:
                    for other in self.get_particles(other_type):
                        if other == enemy or other.attributes.get("is_dying"):
                            continue
                            
                        # 检查碰撞
                        is_colliding, cdx, cdy, cdist = self.check_enemy_collision(enemy, other)
                        if is_colliding:
                            collision_count += 1
                            # 计算排斥力（越近排斥力越大）
                            if cdist > 0:
                                # 使用非线性排斥力，让近距离排斥更强
                                repulsion = 10 * (1.0 - cdist / ((ENEMY_SIZE + ENEMY_SIZE) * 1.5)) ** 2
                                # 归一化方向向量
                                total_repulsion_x -= (cdx / cdist) * repulsion
                                total_repulsion_y -= (cdy / cdist) * repulsion
                
                # 如果发生碰撞，应用排斥力
                if collision_count > 0:
                    # 归一化总排斥力
                    repulsion_magnitude = math.sqrt(total_repulsion_x**2 + total_repulsion_y**2)
                    if repulsion_magnitude > 0:
                        total_repulsion_x /= repulsion_magnitude
                        total_repulsion_y /= repulsion_magnitude
                        
                        # 增加排斥力的影响权重
                        dx = dx/dist * 0.3 + total_repulsion_x * 0.7
                        dy = dy/dist * 0.3 + total_repulsion_y * 0.7
                        
                        # 重新归一化最终方向
                        final_magnitude = math.sqrt(dx**2 + dy**2)
                        if final_magnitude > 0:
                            dx /= final_magnitude
                            dy /= final_magnitude
                else:
                    # 没有碰撞时正常归一化方向
                    dx /= dist
                    dy /= dist
                
                # Apply movement
                speed = enemy.attributes.get("speed", 1) * ENEMY_SPEED_REDUCTION
                if enemy.kind == ENEMY_ELITE:
                    speed *= ELITE_SPEED_MULTIPLIER
                
                # 处理击退效果
                knockback_timer = enemy.attributes.get("knockback_timer", 0)
                if knockback_timer > 0:
                    knockback_dx = enemy.attributes.get("knockback_dx", 0)
                    knockback_dy = enemy.attributes.get("knockback_dy", 0)
                    enemy.x += knockback_dx * KNOCKBACK_DISTANCE
                    enemy.y += knockback_dy * KNOCKBACK_DISTANCE
                    enemy.attributes["knockback_timer"] = knockback_timer - 1
                else:
                    # 正常移动（考虑碰撞后的方向）
                    enemy.x += dx * speed
                    enemy.y += dy * speed

                # Check for collisions with player
                if not player.attributes.get("is_invincible", False):
                    # 根据敌人类型确定碰撞尺寸
                    enemy_size = ELITE_SIZE if enemy.kind == ENEMY_ELITE else ENEMY_SIZE
                    if self.check_collision(player, enemy, PLAYER_SIZE, enemy_size):
                        # Apply damage to player
                        damage = enemy.attributes.get("damage", 1)
                        if enemy.kind == ENEMY_ELITE:
                            damage *= 2  # Elite enemies deal double damage
                        is_alive = self.apply_damage(enemy, player, damage)
                        if not is_alive:
                            self.game_state = STATE_GAME_OVER
                            return
                        # 添加流血效果
                        self.spawn_blood_effect(player.x, player.y)
                        # Make player invincible briefly
                        player.attributes["is_invincible"] = True
                        player.attributes["invincible_timer"] = 10  # 1 second at 60fps
                        # Start player blinking effect
                        self.player_blink_timer = PLAYER_BLINK_DURATION
                        # Set player damage effect
                        player.attributes["damage_effect_timer"] = 10  # 2 frames of red flash
                        # Move enemy away slightly to prevent continuous damage
                        enemy.x = enemy.x - dx * 10
                        enemy.y = enemy.y - dy * 10

                # Check for collisions with weapons
                for weapon in self.get_particles(WEAPON):
                    # 根据敌人类型确定碰撞尺寸
                    enemy_size = ELITE_SIZE if enemy.kind == ENEMY_ELITE else ENEMY_SIZE
                    if self.check_collision(weapon, enemy, WEAPON_SIZE, enemy_size):
                        # 保护武器颜色
                        self.protect_weapon_colors(weapon)
                        
                        # Apply damage to enemy using health system
                        weapon_damage = weapon.attributes["damage"]
                        
                        # Store old HP value for damage calculation
                        old_hp = enemy.health_system.current_hp if enemy.health_system else 0
                        
                        # Start enemy blinking effect
                        enemy.attributes["blink_timer"] = PLAYER_BLINK_DURATION  # Use same duration as player
                        
                        # Apply damage using health system
                        is_alive = self.apply_damage(weapon, enemy, weapon_damage)
                        
                        # 再次保护武器颜色
                        self.protect_weapon_colors(weapon)
                        
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
                            if enemy.kind == ENEMY_ELITE or random.random() < XP_DROP_CHANCE:
                                self.spawn_xp(enemy.x, enemy.y)
                            # 开始死亡动画
                            enemy.attributes["is_dying"] = True
                            enemy.attributes["death_anim_timer"] = 30
                            enemy.attributes["death_anim_size"] = enemy_size
                            enemy.attributes["death_anim_white"] = False
                        else:
                            # 如果敌人还活着，确保飞刀颜色不变
                            if weapon.attributes.get("weapon_name") == "Knife":
                                self.protect_weapon_colors(weapon)

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
            # 圣经的旋转移动
            if wname == "KingBible":
                # 获取目标玩家
                target_player = None
                for p in self.get_particles(PLAYER):
                    if p.attributes.get("id") == weapon.attributes.get("target_player_id"):
                        target_player = p
                        break
                if target_player:
                    # 更新旋转角度
                    orbit_angle = weapon.attributes.get("orbit_angle", 0)
                    orbit_radius = weapon.attributes.get("orbit_radius", 60)
                    speed = weapon.attributes.get("speed", 1.0)
                    
                    # 更新角度
                    orbit_angle = (orbit_angle + speed * 3) % 360  # 3是旋转速度系数
                    weapon.attributes["orbit_angle"] = orbit_angle
                    
                    # 计算新位置
                    rad = math.radians(orbit_angle)
                    weapon.x = target_player.x + orbit_radius * math.cos(rad)
                    weapon.y = target_player.y + orbit_radius * math.sin(rad)
                    
                    # 更新武器角度（用于渲染）
                    weapon.attributes["angle"] = orbit_angle
                    
                    # 检查持续时间
                    if "duration" in weapon.attributes:
                        weapon.attributes["duration"] -= 1
                        if weapon.attributes["duration"] <= 0:
                            weapons_to_remove.append(weapon)
                else:
                    weapons_to_remove.append(weapon)
                continue
        # 魔杖粒子碰撞穿透处理，击中第一个敌人后移除target_id
        for weapon in self.get_particles(WEAPON):
            if weapon.attributes.get("weapon_name") == "MagicWand":
                for enemy_type in [ENEMY, ENEMY_ELITE]:
                    for enemy in self.get_particles(enemy_type):
                        # 根据敌人类型确定碰撞尺寸
                        enemy_size = ELITE_SIZE if enemy.kind == ENEMY_ELITE else ENEMY_SIZE
                        if self.check_collision(weapon, enemy, WEAPON_SIZE, enemy_size):
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
                    
                # 处理敌人之间的碰撞
                total_repulsion_x = 0
                total_repulsion_y = 0
                collision_count = 0
                
                # 检查与其他敌人的碰撞
                for other_type in [ENEMY, ENEMY_ELITE]:
                    for other in self.get_particles(other_type):
                        if other == enemy or other.attributes.get("is_dying"):
                            continue
                            
                        # 检查碰撞
                        is_colliding, cdx, cdy, cdist = self.check_enemy_collision(enemy, other)
                        if is_colliding:
                            collision_count += 1
                            # 计算排斥力（越近排斥力越大）
                            if cdist > 0:
                                # 使用非线性排斥力，让近距离排斥更强
                                repulsion = 10 * (1.0 - cdist / ((ENEMY_SIZE + ENEMY_SIZE) * 1.2)) ** 2
                                # 归一化方向向量
                                total_repulsion_x -= (cdx / cdist) * repulsion
                                total_repulsion_y -= (cdy / cdist) * repulsion
                
                # 如果发生碰撞，应用排斥力
                if collision_count > 0:
                    # 归一化总排斥力
                    repulsion_magnitude = math.sqrt(total_repulsion_x**2 + total_repulsion_y**2)
                    if repulsion_magnitude > 0:
                        total_repulsion_x /= repulsion_magnitude
                        total_repulsion_y /= repulsion_magnitude
                        
                        # 增加排斥力的影响权重
                        dx = dx/dist * 0.3 + total_repulsion_x * 0.7
                        dy = dy/dist * 0.3 + total_repulsion_y * 0.7
                        
                        # 重新归一化最终方向
                        final_magnitude = math.sqrt(dx**2 + dy**2)
                        if final_magnitude > 0:
                            dx /= final_magnitude
                            dy /= final_magnitude
                else:
                    # 没有碰撞时正常归一化方向
                    dx /= dist
                    dy /= dist
                
                # Apply movement
                speed = enemy.attributes.get("speed", 1) * ENEMY_SPEED_REDUCTION
                if enemy.kind == ENEMY_ELITE:
                    speed *= ELITE_SPEED_MULTIPLIER
                
                # 处理击退效果
                knockback_timer = enemy.attributes.get("knockback_timer", 0)
                if knockback_timer > 0:
                    knockback_dx = enemy.attributes.get("knockback_dx", 0)
                    knockback_dy = enemy.attributes.get("knockback_dy", 0)
                    enemy.x += knockback_dx * KNOCKBACK_DISTANCE
                    enemy.y += knockback_dy * KNOCKBACK_DISTANCE
                    enemy.attributes["knockback_timer"] = knockback_timer - 1
                else:
                    # 正常移动（考虑碰撞后的方向）
                    enemy.x += dx * speed
                    enemy.y += dy * speed

                # Check for collisions with player
                if not player.attributes.get("is_invincible", False):
                    # 根据敌人类型确定碰撞尺寸
                    enemy_size = ELITE_SIZE if enemy.kind == ENEMY_ELITE else ENEMY_SIZE
                    if self.check_collision(player, enemy, PLAYER_SIZE, enemy_size):
                        # Apply damage to player
                        damage = enemy.attributes.get("damage", 1)
                        if enemy.kind == ENEMY_ELITE:
                            damage *= 2  # Elite enemies deal double damage
                        is_alive = self.apply_damage(enemy, player, damage)
                        if not is_alive:
                            self.game_state = STATE_GAME_OVER
                            return
                        # 添加流血效果
                        self.spawn_blood_effect(player.x, player.y)
                        # Make player invincible briefly
                        player.attributes["is_invincible"] = True
                        player.attributes["invincible_timer"] = 10  # 1 second at 60fps
                        # Start player blinking effect
                        self.player_blink_timer = PLAYER_BLINK_DURATION
                        # Set player damage effect
                        player.attributes["damage_effect_timer"] = 10  # 2 frames of red flash
                        # Move enemy away slightly to prevent continuous damage
                        enemy.x = enemy.x - dx * 10
                        enemy.y = enemy.y - dy * 10

                # Check for collisions with weapons
                for weapon in self.get_particles(WEAPON):
                    # 根据敌人类型确定碰撞尺寸
                    enemy_size = ELITE_SIZE if enemy.kind == ENEMY_ELITE else ENEMY_SIZE
                    if self.check_collision(weapon, enemy, WEAPON_SIZE, enemy_size):
                        # 保护武器颜色
                        self.protect_weapon_colors(weapon)
                        
                        # Apply damage to enemy using health system
                        weapon_damage = weapon.attributes["damage"]
                        
                        # Store old HP value for damage calculation
                        old_hp = enemy.health_system.current_hp if enemy.health_system else 0
                        
                        # Start enemy blinking effect
                        enemy.attributes["blink_timer"] = PLAYER_BLINK_DURATION  # Use same duration as player
                        
                        # Apply damage using health system
                        is_alive = self.apply_damage(weapon, enemy, weapon_damage)
                        
                        # 再次保护武器颜色
                        self.protect_weapon_colors(weapon)
                        
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
                            if enemy.kind == ENEMY_ELITE or random.random() < XP_DROP_CHANCE:
                                self.spawn_xp(enemy.x, enemy.y)
                            # 开始死亡动画
                            enemy.attributes["is_dying"] = True
                            enemy.attributes["death_anim_timer"] = 30
                            enemy.attributes["death_anim_size"] = enemy_size
                            enemy.attributes["death_anim_white"] = False
                        else:
                            # 如果敌人还活着，确保飞刀颜色不变
                            if weapon.attributes.get("weapon_name") == "Knife":
                                self.protect_weapon_colors(weapon)

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
            # Knife粒子只做直线运动，彻底避免被其他逻辑影响
            if wname == "Knife" and "vx" in weapon.attributes and "vy" in weapon.attributes:
                # 保护武器颜色
                self.protect_weapon_colors(weapon)
                weapon.x += weapon.attributes["vx"]
                weapon.y += weapon.attributes["vy"]
                if (weapon.x < -WEAPON_SIZE or weapon.x > SPATIAL_RESOLUTION + WEAPON_SIZE or
                    weapon.y < -WEAPON_SIZE or weapon.y > SPATIAL_RESOLUTION + WEAPON_SIZE):
                    weapons_to_remove.append(weapon)
                continue
            # 斧子的抛物线移动
            if wname == "Axe" and "vx" in weapon.attributes and "vy" in weapon.attributes:
                # 更新速度（重力影响）
                weapon.attributes["vy"] += weapon.attributes["gravity"]
                
                # 更新位置
                weapon.x += weapon.attributes["vx"]
                weapon.y += weapon.attributes["vy"]
                
                # 更新旋转角度（根据移动方向）
                current_angle = math.degrees(math.atan2(weapon.attributes["vy"], weapon.attributes["vx"]))
                weapon.attributes["angle"] = current_angle
                
                # 检查生命周期
                if "lifetime" in weapon.attributes:
                    weapon.attributes["lifetime"] -= 1
                    if weapon.attributes["lifetime"] <= 0:
                        weapons_to_remove.append(weapon)
                        continue
                
                # 检查是否超出屏幕边界
                if (weapon.x < -WEAPON_SIZE or weapon.x > SPATIAL_RESOLUTION + WEAPON_SIZE or
                    weapon.y < -WEAPON_SIZE or weapon.y > SPATIAL_RESOLUTION + WEAPON_SIZE):
                    weapons_to_remove.append(weapon)
                continue
            # 其他武器的移动逻辑...

        # 更新血液粒子
        blood_to_remove = []
        for blood in self.get_particles(BLOOD):
            # 更新位置
            blood.x += blood.attributes["vx"]
            blood.y += blood.attributes["vy"]
            
            # 减少生命周期
            blood.attributes["lifetime"] -= 1
            if blood.attributes["lifetime"] <= 0:
                blood_to_remove.append(blood)
            else:
                # 逐渐降低不透明度
                progress = 1 - blood.attributes["lifetime"] / BLOOD_PARTICLE_LIFETIME
                blood.attributes["alpha"] = int(255 * (1 - progress))
                # 减小速度（模拟阻力）
                blood.attributes["vx"] *= 0.9
                blood.attributes["vy"] *= 0.9
                # 添加一点重力效果
                blood.attributes["vy"] += 0.2
        
        # 移除过期的血液粒子
        for blood in blood_to_remove:
            if blood in self.particles:
                self.remove_particle(blood)

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
        # 调试信息：检查飞刀颜色
        if attacker.kind == WEAPON and attacker.attributes.get("weapon_name") == "Knife":
            print(f"[DEBUG] 伤害前飞刀 ID:{attacker.attributes.get('id')} 颜色:{attacker.attributes.get('main_color')}")

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

        # 调试信息：再次检查飞刀颜色
        if attacker.kind == WEAPON and attacker.attributes.get("weapon_name") == "Knife":
            print(f"[DEBUG] 伤害后飞刀 ID:{attacker.attributes.get('id')} 颜色:{attacker.attributes.get('main_color')}")

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

    def protect_weapon_colors(self, weapon):
        """保护武器的颜色属性不被修改"""
        if weapon.attributes.get("weapon_name") == "Knife" and weapon.attributes.get("is_knife"):
            # 恢复飞刀的颜色
            weapon.attributes["main_color"] = "#FFFFFF"
            weapon.attributes["border_color"] = "#8B4513"
            weapon.attributes["shape_color"] = "#FFFFFF"
            weapon.attributes["color_locked"] = True
            weapon.attributes["is_knife"] = True
            weapon.attributes["original_main_color"] = "#FFFFFF"
            weapon.attributes["original_border_color"] = "#8B4513"

    def check_enemy_collision(self, enemy1, enemy2):
        """检查两个敌人之间的距离，返回是否在排斥范围内以及相关向量"""
        # 获取敌人尺寸
        size1 = ELITE_SIZE if enemy1.kind == ENEMY_ELITE else ENEMY_SIZE
        size2 = ELITE_SIZE if enemy2.kind == ENEMY_ELITE else ENEMY_SIZE
        
        # 计算两个敌人之间的距离
        dx = enemy2.x - enemy1.x
        dy = enemy2.y - enemy1.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # 计算排斥范围（1.5倍敌人尺寸）
        repulsion_range = (size1 + size2) * 1.2
        
        # 如果距离小于排斥范围，返回排斥信息
        return distance < repulsion_range, dx, dy, distance

    def spawn_blood_effect(self, x, y):
        """在指定位置产生流血效果"""
        for _ in range(BLOOD_PARTICLE_COUNT):
            # 随机角度
            angle = random.uniform(0, 2 * math.pi)
            # 随机速度
            speed = random.uniform(BLOOD_PARTICLE_SPEED * 0.5, BLOOD_PARTICLE_SPEED)
            # 计算速度分量
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            self.particles.append(
                Particle(
                    BLOOD,
                    x,
                    y,
                    attributes={
                        "id": self.next_id,
                        "vx": vx,
                        "vy": vy,
                        "lifetime": BLOOD_PARTICLE_LIFETIME,
                        "size": BLOOD_PARTICLE_SIZE,
                        "alpha": 255  # 初始不透明度
                    }
                )
            )
            self.next_id += 1