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

# 空间分区常量
GRID_SIZE = 100  # 网格大小
GRID_COLS = SCREEN_WIDTH // GRID_SIZE + 1
GRID_ROWS = SCREEN_HEIGHT // GRID_SIZE + 1

# Particle types
PLAYER = "player"
ENEMY = "enemy"
ENEMY_ELITE = "enemy_elite"  # New type for elite enemies
WEAPON = "weapon"
XP = "xp"
DAMAGE_TEXT = "damage_text"  # New particle type for damage numbers
BLOOD = "blood"  # 血液粒子类型

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
ENEMY_SPEED_MAX = 3
ELITE_SPEED_MULTIPLIER = 1.2  # Elite enemies move faster
ENEMY_SPEED_REDUCTION = 0.5  # 全局敌人速度减速系数
WEAPON_SPEED = 8
MAX_ENEMIES = 50  # 优化：减少最大敌人数
MAX_WEAPONS = 4   # 优化：减少最大武器数
MAX_DAMAGE_TEXTS = 20  # 限制同时存在的伤害数字
MAX_BLOOD_PARTICLES = 28  # 限制血液粒子数量
BLOOD_PARTICLE_COUNT = 8  # 每次生成的血液粒子数量
BLOOD_PARTICLE_SIZE = 5  # 血液粒子大小
BLOOD_PARTICLE_SPEED = 8  # 血液粒子初始速度
BLOOD_PARTICLE_LIFETIME = 20  # 血液粒子存活帧数
DESPAWN_DISTANCE = 1.5 * max(SCREEN_WIDTH, SCREEN_HEIGHT)  # Distance at which enemies despawn
FRAMES_PER_MINUTE = 60 * 60  # 60fps * 60 seconds
WAVE_INTERVAL = FRAMES_PER_MINUTE  # One wave per minute
SPAWN_DISTANCE = max(SCREEN_WIDTH, SCREEN_HEIGHT) * 1.1  # Distance from player to spawn enemies
KNOCKBACK_DISTANCE = 5  # Knockback distance in pixels
KNOCKBACK_DURATION = 10  # Duration of knockback in frames
DAMAGE_TEXT_DURATION = 30  # 伤害数字持续时间（1秒 = 60帧）
DAMAGE_TEXT_RISE = 50  # 伤害数字上升距离
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
        "shape": "rectangle",  # 十字架用矩形表示
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
        "duration": 4.0,  # 持续4秒
        "cooldown": 180,  # 3秒冷却
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
        "base_damage": 5,  # Level 1 damage
        "area": 1.0,  # Base area (100%)
        "speed": 0,  # No speed needed for aura
        "amount": 1,
        "pierce": -1,  # AOE damage
        "duration": 1.0,
        "cooldown": 78,  # 1.3s = 78 frames at 60fps
        "projectile_interval": 0,
        "hitbox_delay": 0,
        "knockback": 0,
        "pool_limit": -1,  # Unlimited targets (AOE)
        "chance": 0,
        "crit_multi": 1.0,
        "block_by_walls": False,
        "rarity": 1,
        "size": 70,  # Base size for aura
        "shape": "circle",
        "behavior": "aura",
        "upgrade_table": [
            {"damage": 2},  # Level 2: 5+2 = 7
            {"damage": 1, "cooldown": -6},  # Level 3: 7+1 = 8, cooldown -0.1s
            {"damage": 1, "area": 0.2},  # Level 4: 8+1 = 9, area +20%
            {"damage": 2, "cooldown": -6},  # Level 5: 9+2 = 11, cooldown -0.1s
            {"damage": 1, "area": 0.2},  # Level 6: 11+1 = 12, area +20%
            {"damage": 1, "cooldown": -6},  # Level 7: 12+1 = 13, cooldown -0.1s
            {"damage": 2}  # Level 8: 13+2 = 15
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
class Game(BaseGame):
    def __init__(self):
        """Initialize the game"""
        super().__init__(max_num_particles=1000)  # Initialize with max 1000 particles
        self.particles = []
        self.next_id = 0
        self.game_state = STATE_START_MENU
        self.show_debug_toolbar = True  # Initialize debug toolbar visibility flag
        
        # 初始化空间网格
        self.spatial_grid = {}
        
        # 移动和武器系统
        self.last_move_dir = (1, 0)  # 默认向右
        self.knife_projectile_timer = 0
        
        # 游戏状态变量
        self.available_upgrades = []
        self.selected_upgrade_index = 0
        self.frame_count = 0
        self.kill_count = 0
        self.elite_kill_count = 0
        self.last_spawn_time = 0
        self.last_elite_spawn_time = 0
        self.spawn_cooldown = 60
        self.elite_spawn_cooldown = 300
        self.wave_number = 0
        self.last_wave_time = 0
        self.wave_interval = 1800  # 30 seconds at 60fps
        
        # 分数系统
        self.score = 0
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = self.level * 50
        
        # 计时器
        self.last_reset = 0
        self.game_timer = 0
        self.wave_timer = 0
        self.current_wave = 0
        self.min_enemies_per_wave = MIN_ENEMIES_PER_WAVE
        self.next_spawn_timer = 0
        
        # 生命值动画系统
        self.hp_displayed = 100  # 平滑显示的HP
        self.hp_transition_timer = 0  # HP过渡动画计时器
        self.hp_blink_timer = 0  # HP闪烁效果计时器
        self.hp_section = 5  # HP阈值区间 (100/20 = 5)
        
        # 升级菜单
        self.upgrade_options = []
        
        # 鼠标处理
        self.mouse_pos = (0, 0)
        self.mouse_clicked = False
        
        # 特效计数器
        self.damage_text_count = 0
        self.blood_particle_count = 0
        
        # 初始化游戏
        self.initialize_game()
        self.set_system_prompt(
            "Vampire Survivors-like game. Survive as long as possible by collecting XP and leveling up. "
            "Enemies will spawn from the edges of the screen and chase you. "
            "Your weapons will automatically orbit around you and attack nearby enemies."
        )

    def update_spatial_grid(self):
        """更新空间网格"""
        self.spatial_grid.clear()
        for particle in self.particles:
            if particle.kind in [ENEMY, ENEMY_ELITE, WEAPON, PLAYER]:
                grid_x = int(particle.x // GRID_SIZE)
                grid_y = int(particle.y // GRID_SIZE)
                grid_key = (grid_x, grid_y)
                if grid_key not in self.spatial_grid:
                    self.spatial_grid[grid_key] = []
                self.spatial_grid[grid_key].append(particle)

    def get_nearby_particles(self, x, y, radius):
        """获取指定位置附近的粒子"""
        grid_x_start = int((x - radius) // GRID_SIZE)
        grid_x_end = int((x + radius) // GRID_SIZE)
        grid_y_start = int((y - radius) // GRID_SIZE)
        grid_y_end = int((y + radius) // GRID_SIZE)
        
        nearby = []
        for gx in range(grid_x_start, grid_x_end + 1):
            for gy in range(grid_y_start, grid_y_end + 1):
                if (gx, gy) in self.spatial_grid:
                    nearby.extend(self.spatial_grid[(gx, gy)])
        return nearby
        self.available_upgrades = []
        self.selected_upgrade_index = 0
        self.frame_count = 0
        self.kill_count = 0
        self.elite_kill_count = 0
        self.last_spawn_time = 0
        self.last_elite_spawn_time = 0
        self.spawn_cooldown = 60
        self.elite_spawn_cooldown = 300
        self.wave_number = 0
        self.last_wave_time = 0
        self.wave_interval = 1800  # 30 seconds at 60fps
        
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
        self.hp_section = 5  # HP threshold for each section of health bar
        
        # Upgrade menu variables
        self.upgrade_options = []
        
        # Mouse handling
        self.mouse_pos = (0, 0)
        self.mouse_clicked = False
        
        # 初始化空间网格
        self.spatial_grid = {}
        self.damage_text_count = 0
        self.blood_particle_count = 0
        
        self.initialize_game()
        self.set_system_prompt(
            "Vampire Survivors-like game. Survive as long as possible by collecting XP and leveling up. "
            "Enemies will spawn from the edges of the screen and chase you. "
            "Your weapons will automatically orbit around you and attack nearby enemies."
        )
        self.last_move_dir = (1, 0)  # 默认向右
        self.knife_projectile_timer = 0
    
    def get_frame(self):
        """Get the current frame of the game"""
        frame = Frame()
        
        # 1. Draw background
        frame.add_rectangle(Rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, "#000000"))
        
      
        # 3. Draw aura effects (except Garlic)
        garlic_weapons = []  # Store Garlic weapons for later rendering
        for weapon in self.get_particles(WEAPON):
            if weapon.attributes.get("is_aura"):
                weapon_name = weapon.attributes.get("weapon_name")
                if weapon_name == "Garlic":
                    garlic_weapons.append(weapon)  # Collect Garlic weapons
                    continue
                else:
                    radius = weapon.attributes["aura_radius"]
                    base_color = WEAPON_COLORS.get(weapon_name, "#FFFFFF")
                    
                    weapon_type = next((w for w in WEAPON_TYPES if w["name"] == weapon_name), None)
                    if weapon_type:
                        alpha = 0.3 + 0.1 * (1 - weapon.attributes["duration"] / weapon_type["cooldown"])
                        
                        if isinstance(base_color, dict):
                            base_color = base_color.get("main", "#FFFFFF")
                        
                        # Normal aura drawing for other weapons
                        frame.add_circle(Circle(
                            weapon.x, weapon.y, radius,
                            f"{base_color}{int(alpha * 255):02x}",
                            is_filled=True
                        ))
                        frame.add_circle(Circle(
                            weapon.x, weapon.y, radius,
                            f"{base_color}88",
                            is_filled=False
                        ))
        
        # Draw Garlic aura (only once per unique position)
        rendered_positions = set()  # Track rendered positions
        for weapon in garlic_weapons:
            pos = (weapon.x, weapon.y)
            if pos not in rendered_positions:
                rendered_positions.add(pos)
                radius = weapon.attributes.get("aura_radius")  # Use the radius we calculated in spawn_aura
                if radius is None:  # Fallback only if radius is not set
                    radius = WEAPON_SIZE * 2

                # Draw red border on top
                frame.add_circle(Circle(
                    weapon.x, weapon.y, radius,
                    self.get_garlic_border_color(weapon),  # 使用动态颜色
                    is_filled=False
                ))
        
        # 4. Draw XP particles
        for xp in self.get_particles(XP):
            frame.add_circle(Circle(xp.x, xp.y, XP_SIZE, XP_COLOR))
        
        # 5. Draw enemies
        for enemy_type in [ENEMY, ENEMY_ELITE]:
            for enemy in self.get_particles(enemy_type):
                if enemy.attributes.get("is_dying"):
                    size = enemy.attributes.get("death_anim_size", ENEMY_SIZE if enemy_type == ENEMY else ELITE_SIZE)
                    color = "#FFFFFF" if enemy.attributes.get("death_anim_white") else (ENEMY_COLOR if enemy_type == ENEMY else ELITE_COLOR)
                    frame.add_circle(Circle(enemy.x, enemy.y, max(1, size), color))
                else:
                    # 检查是否处于受伤变白状态
                    white_effect_timer = enemy.attributes.get("white_effect_timer", 0)
                    if white_effect_timer > 0:
                        enemy.attributes["white_effect_timer"] = white_effect_timer - 1
                        color = "#FFFFFF"  # 受伤时显示为白色
                    else:
                        color = ENEMY_COLOR if enemy_type == ENEMY else ELITE_COLOR
                    size = ENEMY_SIZE if enemy_type == ENEMY else ELITE_SIZE
                    frame.add_circle(Circle(enemy.x, enemy.y, size + 1, "#FFFFFF"))  # 白色边框
                    frame.add_circle(Circle(enemy.x, enemy.y, size, color))  # 主体颜色
        
        # 6. Draw weapons (except auras and Garlic)
        for weapon in self.get_particles(WEAPON):
            if not weapon.attributes.get("is_aura") and weapon.attributes.get("weapon_name") != "Garlic":
                weapon_name = weapon.attributes.get("weapon_name", "")
                weapon_type = next((w for w in WEAPON_TYPES if w["name"] == weapon_name), None)
                weapon_size = weapon_type["size"] if weapon_type else WEAPON_SIZE
                shape = weapon_type.get("shape", "circle") if weapon_type else "circle"
                angle = weapon.attributes.get("angle", 0)
                
                # Get weapon color
                if weapon_name == "Knife" and weapon.attributes.get("is_knife"):
                    main_color = weapon.attributes.get("main_color", "#FFFFFF")
                    border_color = weapon.attributes.get("border_color", "#8B4513")
                    shape_color = main_color
                else:
                    color_info = WEAPON_COLORS.get(weapon_name, "#FFFFFF")
                    shape_color = color_info.get("main", color_info) if isinstance(color_info, dict) else color_info
                
                # Draw weapon based on its shape
                if weapon_name == "MagicWand":
                    inner_color = "#3399FF"
                    outer_color = "#0055AA"
                    wand_size = weapon_size * 0.5
                    frame.add_circle(Circle(weapon.x, weapon.y, wand_size + 3, outer_color))
                    frame.add_circle(Circle(weapon.x, weapon.y, wand_size, inner_color))
                elif weapon_name == "KingBible" and shape == "rectangle":
                    current_size = weapon.attributes.get("current_size", weapon_size)
                    side = current_size * 1.4
                    frame.add_rectangle(Rectangle(weapon.x - side/2, weapon.y - side/2, side, side, shape_color, angle))
                elif weapon_name == "Cross" and shape == "rectangle":
                    # Calculate cross dimensions
                    long_side = weapon_size * 2.0  # Long edge
                    short_side = weapon_size * 0.4  # Short edge
                    
                    # Get self-rotation angle
                    self_rotation = weapon.attributes.get("self_rotation", 0)
                    
                    # Calculate positions for four rectangles (forming a cross)
                    segments = 4  # Each arm uses two rectangles
                    segment_length = long_side / 2  # Length of each rectangle
                    segment_width = short_side  # Width of rectangle
                    
                    for i in range(segments):
                        angle = self_rotation + (i * 90)  # Place a rectangle every 90 degrees
                        rad = math.radians(angle)
                        
                        # Calculate offset
                        offset = segment_length / 2  # Distance to offset from center
                        dx = math.cos(rad) * offset
                        dy = math.sin(rad) * offset
                        
                        # Draw rectangle
                        frame.add_rectangle(Rectangle(
                            weapon.x + dx - segment_width/2,  # Center x + offset - width/2
                            weapon.y + dy - segment_width/2,  # Center y + offset - width/2
                            segment_length,  # Length
                            segment_width,   # Width
                            shape_color,
                            angle  # Use current arm's angle
                        ))
                elif weapon_name == "Knife" and weapon.attributes.get("is_knife"):
                    frame.add_triangle(Triangle(weapon.x, weapon.y, weapon_size * 1.4, border_color, angle))
                    frame.add_triangle(Triangle(weapon.x, weapon.y, weapon_size * 1.2, main_color, angle))
                elif weapon_name == "Axe":
                    frame.add_circle(Circle(weapon.x, weapon.y, weapon_size * 0.9, "#FFA50044"))
                    frame.add_cross(Cross(weapon.x, weapon.y, weapon_size * 1.26, "#000000"))
                    frame.add_cross(Cross(weapon.x, weapon.y, weapon_size * 1.2, "#FFB700"))
                    frame.add_cross(Cross(weapon.x, weapon.y, weapon_size * 0.75, "#FFFFFF"))
                    frame.add_circle(Circle(weapon.x, weapon.y, weapon_size * 0.15, "#FFFFFF"))
                elif shape == "circle":
                    frame.add_circle(Circle(weapon.x, weapon.y, weapon_size, shape_color))
                elif shape == "triangle":
                    frame.add_triangle(Triangle(weapon.x, weapon.y, weapon_size * 1.2, shape_color, angle))
                elif shape == "cross":
                    frame.add_cross(Cross(weapon.x, weapon.y, weapon_size * 1.2, shape_color, angle))
                elif shape == "rectangle":
                    width = weapon_size * 3
                    height = weapon_size * 0.5
                    frame.add_rectangle(Rectangle(weapon.x - width/2, weapon.y - height/2, width, height, shape_color, angle))
        
        # 7. Draw player (top layer)
        for player in self.get_particles(PLAYER):
            if player.attributes.get("damage_effect_timer", 0) > 0:
                frame.add_circle(Circle(player.x, player.y, PLAYER_SIZE, "#FF0000"))
            else:
                frame.add_circle(Circle(player.x, player.y, PLAYER_SIZE, PLAYER_COLOR))
            
            if player.health_system:
                bar_width = 40
                bar_height = 6
                hp_percent = player.health_system.current_hp / player.health_system.max_hp
                bar_x = player.x - bar_width // 2
                bar_y = player.y - PLAYER_SIZE - 12
                frame.add_rectangle(Rectangle(bar_x, bar_y, bar_width, bar_height, "#444444"))
                frame.add_rectangle(Rectangle(bar_x, bar_y, int(bar_width * hp_percent), bar_height, 
                    "#FF4444" if hp_percent < 0.3 else ("#FFFF00" if hp_percent < 0.6 else "#00FF00")))
          # Draw blood particles 
        for blood in self.get_particles(BLOOD):
            alpha = format(blood.attributes.get("alpha", 255), '02x')
            color = f"#FF0000{alpha}"  # Red with transparency
            frame.add_circle(Circle(blood.x, blood.y, blood.attributes.get("size", BLOOD_PARTICLE_SIZE), color))
        
        # 8. Draw damage numbers (very top layer)
        for damage_text in self.get_particles(DAMAGE_TEXT):
            alpha = damage_text.attributes.get("alpha", 255)
            scale = damage_text.attributes.get("scale", 1.0)
            base_size = 24  # 基础字号
            current_size = int(base_size * scale)  # 应用缩放
            alpha_hex = format(alpha, '02x')
            text = damage_text.attributes["text"]
            x = damage_text.x
            y = damage_text.y
            # 黑色描边（上下左右各1像素）
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                frame.add_text(Text(x+dx, y+dy, text, f"#000000{alpha_hex}", current_size))
            # 正常白色文字
            frame.add_text(Text(x, y, text, f"#FFFFFF{alpha_hex}", current_size))
        
        # 9. Draw UI based on game state
        if self.game_state == STATE_UPGRADE_MENU:
            self.draw_upgrade_menu(frame)
        elif self.game_state == STATE_START_MENU:
            self.draw_start_menu(frame)
        elif self.game_state == STATE_GAME_OVER:
            self.draw_game_over(frame)
        elif self.game_state == STATE_PLAYING:
            self.draw_hud(frame)
            if self.show_debug_toolbar:
                self.draw_debug_toolbar(frame)
        
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
        if not self.show_debug_toolbar:
            return
            
        # Background for debug toolbar
        toolbar_y = SCREEN_HEIGHT - DEBUG_TOOLBAR_HEIGHT
        frame.add_rectangle(Rectangle(0, toolbar_y, SCREEN_WIDTH, DEBUG_TOOLBAR_HEIGHT, "#333333"))
        
        # Title for debug toolbar
        frame.add_text(Text(10, toolbar_y + 30, "Debug Toolbar:", "#FFFFFF", DEBUG_FONT_SIZE))
        
        # Get player weapon levels
        player = self.get_particle(PLAYER)
        if not player:
            print("[DEBUG] No player found in draw_debug_toolbar")
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
            
            # Draw - button with hover effect
            button_x_minus = button_x
            is_minus_hovered = self.is_point_in_rect(
                self.mouse_pos[0], self.mouse_pos[1],
                button_x_minus, toolbar_y + 20,
                DEBUG_BUTTON_WIDTH, DEBUG_BUTTON_HEIGHT
            )
            minus_color = "#CC0000" if is_minus_hovered else "#AA0000"
            frame.add_rectangle(Rectangle(button_x_minus, toolbar_y + 20, DEBUG_BUTTON_WIDTH, DEBUG_BUTTON_HEIGHT, minus_color))
            frame.add_text(Text(button_x_minus + DEBUG_BUTTON_WIDTH/2 - 5, toolbar_y + 40, "-", "#FFFFFF", DEBUG_FONT_SIZE))
            
            # Draw + button with hover effect
            button_x_plus = button_x_minus + DEBUG_BUTTON_WIDTH + 2
            is_plus_hovered = self.is_point_in_rect(
                self.mouse_pos[0], self.mouse_pos[1],
                button_x_plus, toolbar_y + 20,
                DEBUG_BUTTON_WIDTH, DEBUG_BUTTON_HEIGHT
            )
            plus_color = "#00CC00" if is_plus_hovered else "#00AA00"
            frame.add_rectangle(Rectangle(button_x_plus, toolbar_y + 20, DEBUG_BUTTON_WIDTH, DEBUG_BUTTON_HEIGHT, plus_color))
            frame.add_text(Text(button_x_plus + DEBUG_BUTTON_WIDTH/2 - 5, toolbar_y + 40, "+", "#FFFFFF", DEBUG_FONT_SIZE))
            

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
        player_x = SCREEN_WIDTH // 2
        player_y = SCREEN_HEIGHT // 2
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
        self.xp_to_next_level = 150
        self.game_timer = 0
        self.current_wave = 0
        self.min_enemies_per_wave = MIN_ENEMIES_PER_WAVE
        self.next_spawn_timer = 0
        self.wave_timer = WAVE_INTERVAL
        self.elite_spawned = False
        self.particles = []
        self.next_id = 0
        self.last_move_dir = [0, 0]
        self.available_upgrades = []
        self.selected_upgrade_index = 0
        self.frame_count = 0
        self.kill_count = 0
        self.elite_kill_count = 0
        self.last_spawn_time = 0
        self.last_elite_spawn_time = 0
        self.spawn_cooldown = 60
        self.elite_spawn_cooldown = 300
        self.wave_number = 0
        self.last_wave_time = 0
        self.wave_interval = 1800
        
        # Keep debug toolbar state
        debug_toolbar_state = self.show_debug_toolbar
        
        # Create player
        self.create_player()
        
        # Restore debug toolbar state
        self.show_debug_toolbar = debug_toolbar_state
        
        print(f"[DEBUG] Game reset. Debug toolbar state: {self.show_debug_toolbar}")
        
    def format_time(self, frames):
        """Convert frame count to time string (MM:SS)"""
        total_seconds = frames // 60  # 60 fps
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
        
    def handle_input(self, actions=None, mouse_pos=None, mouse_clicked=False):
        """Handle input for various game states"""
        if actions is None:
            actions = []
            
        # Toggle debug toolbar with q key
        if "q" in actions:
            self.toggle_debug_toolbar()
            
        self.mouse_pos = mouse_pos if mouse_pos else (0, 0)
        self.mouse_clicked = mouse_clicked
        
        # Print mouse info when clicked
       
        if self.game_state == STATE_START_MENU:
            # Handle start menu input
            if self.mouse_clicked:
                # Check if mouse is over start button
                button_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
                button_y = SCREEN_HEIGHT // 2 - 30
                if self.is_point_in_rect(
                    self.mouse_pos[0], self.mouse_pos[1],
                    button_x, button_y,
                    BUTTON_WIDTH, BUTTON_HEIGHT
                ):
                    self.reset_game()
                    self.game_state = STATE_PLAYING
        
        elif self.game_state == STATE_PLAYING:
            # Get player particle
            player = self.get_particle(PLAYER)
            if not player:
                print("[DEBUG] No player found!")
                return
            
            # Handle debug toolbar clicks if visible
            if self.show_debug_toolbar and self.mouse_clicked:
                toolbar_y = SCREEN_HEIGHT - DEBUG_TOOLBAR_HEIGHT
                weapons = player.attributes.get("weapons", {})
                
                print(f"[DEBUG] Current weapons: {weapons}")
                print(f"[DEBUG] Toolbar Y: {toolbar_y}")
                
                # Check each weapon's buttons
                for i, weapon_type in enumerate(WEAPON_TYPES):
                    weapon_name = weapon_type["name"]
                    level = weapons.get(weapon_name, 0)
                    button_x = 200 + i * (DEBUG_BUTTON_WIDTH * 2 + DEBUG_BUTTON_SPACING)
                    
                   # Check minus button
                    if self.is_point_in_rect(
                        self.mouse_pos[0], self.mouse_pos[1],
                        button_x, toolbar_y + 20,
                        DEBUG_BUTTON_WIDTH, DEBUG_BUTTON_HEIGHT
                    ):
                        print(f"[DEBUG] Minus button clicked for {weapon_name}")
                        if level > 0:
                            weapons[weapon_name] = max(0, level - 1)
                            player.attributes["weapons"] = weapons.copy()  # Make a copy to ensure update
                            print(f"[DEBUG] Decreased {weapon_name} level to {weapons[weapon_name]}")
                            print(f"[DEBUG] Updated weapons: {player.attributes['weapons']}")
                        return actions
                    
                    # Check plus button
                    button_x_plus = button_x + DEBUG_BUTTON_WIDTH + 2
                    if self.is_point_in_rect(
                        self.mouse_pos[0], self.mouse_pos[1],
                        button_x_plus, toolbar_y + 20,
                        DEBUG_BUTTON_WIDTH, DEBUG_BUTTON_HEIGHT
                    ):
                        print(f"[DEBUG] Plus button clicked for {weapon_name}")
                        max_level = next((w["max_level"] for w in WEAPON_TYPES if w["name"] == weapon_name), 8)
                        if level < max_level:
                            if weapon_name not in weapons:
                                weapons[weapon_name] = 1
                            else:
                                weapons[weapon_name] = min(max_level, level + 1)
                            player.attributes["weapons"] = weapons.copy()  # Make a copy to ensure update
                            print(f"[DEBUG] Increased {weapon_name} level to {weapons[weapon_name]}")
                            print(f"[DEBUG] Updated weapons: {player.attributes['weapons']}")
                        return actions
            
            # Handle movement
            dx = 0
            dy = 0
            speed = PLAYER_SPEED
            
            if "UP" in actions:
                dy -= speed
            if "DOWN" in actions:
                dy += speed
            if "LEFT" in actions:
                dx -= speed
            if "RIGHT" in actions:
                dx += speed
            
            # Store movement direction for weapon aiming
            if dx != 0 or dy != 0:
                self.last_move_dir = [dx, dy]
            
            # Apply movement
            player.x = int(max(PLAYER_SIZE // 2, min(SCREEN_WIDTH - PLAYER_SIZE // 2, player.x + dx)))
            player.y = int(max(PLAYER_SIZE // 2, min(SCREEN_HEIGHT - PLAYER_SIZE // 2, player.y + dy)))
        
        elif self.game_state == STATE_UPGRADE_MENU:
            # Handle upgrade menu input
            if self.upgrade_options:
                cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
                if self.mouse_clicked:
                    # Check if mouse is over any upgrade button
                    for i, upgrade in enumerate(self.upgrade_options):
                        button_y = cy - 50 + i * (BUTTON_HEIGHT + 20)
                        button_x = cx - BUTTON_WIDTH // 2
                        if self.is_point_in_rect(
                            self.mouse_pos[0], self.mouse_pos[1],
                            button_x, button_y,
                            BUTTON_WIDTH, BUTTON_HEIGHT
                        ):
                            print(f"Selected upgrade: {upgrade}")  # Debug print
                            self.apply_upgrade(upgrade)
                            self.game_state = STATE_PLAYING
                            break
                elif "UP" in actions:
                    self.selected_upgrade_index = (self.selected_upgrade_index - 1) % len(self.upgrade_options)
                elif "DOWN" in actions:
                    self.selected_upgrade_index = (self.selected_upgrade_index + 1) % len(self.upgrade_options)
                elif "SPACE" in actions:
                    # Apply selected upgrade
                    self.apply_upgrade(self.upgrade_options[self.selected_upgrade_index])
                    self.game_state = STATE_PLAYING
        
        elif self.game_state == STATE_GAME_OVER:
            # Handle game over input
            if "SPACE" in actions or self.mouse_clicked:
                self.reset_game()
                self.game_state = STATE_START_MENU
        
        return actions
    
    def is_point_in_rect(self, x, y, rect_x, rect_y, rect_width, rect_height):
        """Check if a point is inside a rectangle"""
        return (x >= rect_x and x <= rect_x + rect_width and
                y >= rect_y and y <= rect_y + rect_height)
    
    def check_collision(self, particle1, particle2, size1=None, size2=None):
        """Check if two particles are colliding"""
    
        # 优化：只检测屏幕内的粒子
        if getattr(particle1, 'attributes', {}).get('is_dying') or getattr(particle2, 'attributes', {}).get('is_dying'):
            return False
        if not (0 <= particle1.x <= SCREEN_WIDTH and 0 <= particle1.y <= SCREEN_HEIGHT):
            return False
        if not (0 <= particle2.x <= SCREEN_WIDTH and 0 <= particle2.y <= SCREEN_HEIGHT):
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
                elif weapon_name == "Cross":
                    size1 = weapon_type["size"] * 2.0  # 十字架使用2倍尺寸，与显示大小匹配
                elif weapon_name == "Garlic" and particle1.attributes.get("is_aura"):
                    # 对于大蒜光环，使用其实际的aura_radius
                    size1 = particle1.attributes.get("aura_radius", weapon_type["size"] * 2)
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
                elif weapon_name == "Cross":
                    size2 = weapon_type["size"] * 2.0  # 十字架使用2倍尺寸，与显示大小匹配
                elif weapon_name == "Garlic" and particle2.attributes.get("is_aura"):
                    # 对于大蒜光环，使用其实际的aura_radius
                    size2 = particle2.attributes.get("aura_radius", weapon_type["size"] * 2)
                else:
                    size2 = weapon_type["size"]
            
        # 基本圆形碰撞检测
        dx = particle1.x - particle2.x
        dy = particle1.y - particle2.y
        distance = math.sqrt(dx * dx + dy * dy)
        collision = distance < (size1 + size2) / 2
        
        return collision
    
    def show_upgrade_menu(self):
        """Show the upgrade menu with weapon options"""
        self.game_state = STATE_UPGRADE_MENU
        self.upgrade_anim_timer = 12  # 0.2秒动画
        self.selected_upgrade_index = 0  # Initialize selection index
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
                # Update weapon level
                weapons[name] = level + 1
                print("升级武器 {} 到等级 {}".format(name, level+1))
                
                # Remove existing weapon particles of this type
                weapons_to_remove = [w for w in self.get_particles(WEAPON) 
                                   if w.attributes.get("weapon_name") == name and 
                                   w.attributes.get("target_player_id") == player.attributes["id"]]
                for weapon in weapons_to_remove:
                    if weapon in self.particles:
                        self.remove_particle(weapon)
                
                # Reset cooldown for this weapon
                cooldown_key = f"{name}_cooldown"
                weapon_type = next((w for w in WEAPON_TYPES if w["name"] == name), None)
                if weapon_type:
                    player.attributes[cooldown_key] = 0  # Reset cooldown to trigger immediate respawn
                    
                    # For Garlic, immediately recreate with new stats
                    if name == "Garlic":
                        self.spawn_aura(player, name, level + 1)
                
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
        print("Resetting level")
        self.last_reset = 0
        self.clear_particles()
        self.next_id = 0
        player_x = SCREEN_WIDTH // 2
        player_y = SCREEN_HEIGHT // 2
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
                    "damage": 10,
                    "id": self.next_id,
                    "blink_timer": 0,
                    "wave": self.current_wave,
                    "xp_value": 30,
                    "white_effect_timer": 0  # 初始化受伤变白效果计时器
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
        enemy_speed = random.randint(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
        self.particles.append(
            Particle(
                ENEMY,
                spawn_x,
                spawn_y,
                attributes={
                    "speed": enemy_speed,
                    "base_hp": enemy_health,
                    "max_hp": enemy_health,
                    "damage": 5,
                    "id": self.next_id,
                    "blink_timer": 0,
                    "wave": self.current_wave,
                    "xp_value": 10,
                    "white_effect_timer": 0  # 初始化受伤变白效果计时器
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

    def spawn_boomerang(self, player, weapon_name, level, angle=None):
        # 如果没有指定角度，寻找最近的敌人
        if angle is None:
            nearest_enemy = None
            min_dist = float('inf')
            for enemy_type in [ENEMY, ENEMY_ELITE]:
                for enemy in self.get_particles(enemy_type):
                    dx = enemy.x - player.x
                    dy = enemy.y - player.y
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_enemy = enemy

            # 如果找到敌人，计算发射角度；否则默认向右
            if nearest_enemy:
                angle = math.degrees(math.atan2(nearest_enemy.y - player.y, nearest_enemy.x - player.x))
            else:
                angle = 0

        # 根据等级获取属性
        base_damage = 10
        if level >= 2:
            base_damage = 20
        if level >= 5:
            base_damage = 30
        if level >= 8:
            base_damage = 40

        # 计算速度倍率
        speed_multiplier = 1.0
        if level >= 3:
            speed_multiplier = 1.25
        if level >= 6:
            speed_multiplier = 1.5

        # 基础速度
        base_speed = 8 * speed_multiplier

        rad = math.radians(angle)
        
        # 创建武器粒子
        self.particles.append(
            Particle(
                WEAPON,
                player.x,
                player.y,
                attributes={
                    "damage": base_damage,
                    "speed": base_speed,
                    "angle": angle,
                    "id": self.next_id,
                    "weapon_name": weapon_name,
                    "level": level,
                    "vx": math.cos(rad) * base_speed,
                    "vy": math.sin(rad) * base_speed,
                    "initial_vx": math.cos(rad) * base_speed,  # 记录初始速度
                    "initial_vy": math.sin(rad) * base_speed,
                    "ax": 0,  # 初始加速度为0
                    "ay": 0,
                    "original_speed": base_speed,
                    "has_hit": False,  # 是否已击中敌人
                    "is_returning": False,  # 是否在返回
                    "pierce_count": 999,  # 无限穿透
                    "duration": 300,  # 5秒持续时间
                    "self_rotation": random.uniform(0, 360),  # 随机初始角度
                    "rotation_speed": 24  # 每帧旋转24度
                }
            )
        )
        print(f"生成十字架 ID:{self.next_id} 角度:{angle:.1f} 速度:{base_speed:.1f}")
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
                "duration": int(4.0 * 60),  # 4秒持续时间
                "total_duration": int(4.0 * 60),  # 保存总持续时间
                "original_size": weapon_type["size"],  # 保存原始尺寸
                "current_size": weapon_type["size"],  # 当前尺寸（用于淡出动画）
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
            
        # Get weapon configuration
        weapon_type = next((w for w in WEAPON_TYPES if w["name"] == weapon_name), None)
        if not weapon_type:
            return
            
        # Calculate base damage and area
        base_damage = weapon_type["base_damage"]
        base_size = weapon_type["size"]  # Base size for aura
        
        # Calculate level-based stats
        damage = base_damage
        area_multiplier = 1.0  # Start with base multiplier (100%)
        pool_limit = weapon_type["pool_limit"]
        
        # Apply upgrades based on level
        print(f"[DEBUG] Garlic Level {level} - Processing upgrades:")
        upgrades_to_process = min(level - 1, len(weapon_type["upgrade_table"]))  # Make sure we don't exceed the upgrade table
        for i in range(upgrades_to_process):
            upgrade = weapon_type["upgrade_table"][i]
            print(f"[DEBUG] Processing upgrade {i+1}: {upgrade}")
            if "damage" in upgrade:
                damage += upgrade["damage"]
            if "area" in upgrade:
                old_multiplier = area_multiplier
                area_multiplier += upgrade["area"]  # Add area upgrade multipliers (20% = 0.2)
                print(f"[DEBUG] Area multiplier updated: {old_multiplier} -> {area_multiplier}")
            if "pool_limit" in upgrade:
                if upgrade["pool_limit"] == -1:
                    pool_limit = -1  # Unlimited targets
                else:
                    pool_limit += upgrade["pool_limit"]
        
        # Calculate final aura radius with area multiplier
        aura_radius = base_size * area_multiplier
        print(f"[DEBUG] Final Garlic stats - Base Size: {base_size}, Area Multiplier: {area_multiplier}, Final Radius: {aura_radius}")
        
        # Remove existing Garlic auras for this player
        existing_garlic = [w for w in self.get_particles(WEAPON) 
                          if w.attributes.get("weapon_name") == "Garlic" and 
                          w.attributes.get("target_player_id") == player.attributes["id"]]
        for old_garlic in existing_garlic:
            self.remove_particle(old_garlic)
        
        # Create the aura particle
        self.particles.append(
            Particle(
                WEAPON,
                player.x,
                player.y,
                attributes={
                    "damage": damage,
                    "speed": 0,  # Aura doesn't move independently
                    "angle": 0,
                    "id": self.next_id,
                    "weapon_name": weapon_name,
                    "level": level,
                    "base_size": base_size,  # Store base size
                    "area_multiplier": area_multiplier,  # Store area multiplier
                    "aura_radius": aura_radius,  # Use the scaled radius
                    "pool_limit": pool_limit,
                    "hit_cooldown": {},  # Dictionary to track per-enemy hit cooldowns
                    "duration": weapon_type["cooldown"],  # Duration until next damage tick
                    "knockback": weapon_type["knockback"],
                    "affected_enemies": set(),  # Track currently affected enemies
                    "target_player_id": player.attributes["id"],  # Link to player
                    "shape": weapon_type["shape"],
                    "is_aura": True,  # Flag to identify as an aura effect
                    "cooldown": weapon_type["cooldown"],  # Store original cooldown value
                    "breath_timer": 0  # 添加呼吸效果计时器
                }
            )
        )
        print(f"[DEBUG] Created new Garlic aura with radius {aura_radius} at level {level}")
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
            
        # 更新空间网格
        self.update_spatial_grid()
        
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
            player.x = int(max(PLAYER_SIZE // 2, min(SCREEN_WIDTH - PLAYER_SIZE // 2, player.x + dx)))
            player.y = int(max(PLAYER_SIZE // 2, min(SCREEN_HEIGHT - PLAYER_SIZE // 2, player.y + dy)))
            # 记录移动方向
            if dx != 0 or dy != 0:
                norm = math.sqrt(dx*dx + dy*dy)
                self.last_move_dir = (dx/norm, dy/norm)

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
                        enemy.x = max(0, min(SCREEN_WIDTH, enemy.x))
                        enemy.y = max(0, min(SCREEN_HEIGHT, enemy.y))
        
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
                    
                    # Make it fade out by adjusting alpha
                    # 在最后0.3秒开始淡出
                    fade_start = 0.7  # 0.7秒后开始淡出
                    if progress > fade_start:
                        fade_progress = (progress - fade_start) / (1 - fade_start)
                        alpha = int(255 * (1 - fade_progress))
                    else:
                        alpha = 255
                    particle.attributes["alpha"] = alpha

                    # 处理尺寸动画
                    if particle.attributes["scale_phase"] == "grow":
                        # 在前0.2秒内从50%变到100%
                        grow_duration = DAMAGE_TEXT_DURATION / 5  # 0.2秒
                        grow_progress = min(1.0, (DAMAGE_TEXT_DURATION - particle.attributes["timer"]) / grow_duration)
                        particle.attributes["scale"] = 0.5 + (0.5 * grow_progress)
                        if grow_progress >= 1.0:
                            particle.attributes["scale_phase"] = "shrink"
                    else:  # shrink phase
                        # 在0.2秒后的0.5秒内从100%变回50%
                        shrink_start = DAMAGE_TEXT_DURATION / 5  # 0.2秒
                        shrink_duration = DAMAGE_TEXT_DURATION / 1  # 0.5秒
                        shrink_progress = ((DAMAGE_TEXT_DURATION - particle.attributes["timer"]) - shrink_start) / shrink_duration
                        shrink_progress = min(1.0, max(0.0, shrink_progress))
                        particle.attributes["scale"] = 1.0 - (0.5 * shrink_progress)

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
                        # 获取武器类型配置
                        weapon_type = next((w for w in WEAPON_TYPES if w["name"] == name), None)
                        if not weapon_type:
                            continue
                            
                        # 检查是否已经有圣经在场上
                        existing_bibles = [w for w in self.get_particles(WEAPON) 
                                         if w.attributes.get("weapon_name") == "KingBible" and 
                                         w.attributes.get("target_player_id") == player.attributes["id"]]
                        
                        # 如果没有圣经在场上，且冷却时间结束，则生成新的
                        if not existing_bibles and current_cooldown <= 0:
                            # 获取当前等级的属性
                            lvl = min(level, len(KING_BIBLE_LEVELS)) - 1
                            props = KING_BIBLE_LEVELS[lvl]
                            amount = max(1, props["amount"])
                            for i in range(amount):
                                self.spawn_orbiting_book(player, name, level, i, amount)
                            # 不在这里设置冷却时间，而是在粒子消失时设置
                            print("圣经粒子生成完成")
                    elif name == "FireWand":
                        # 获取当前等级的属性
                        amount = 1 + sum(u.get("count", 0) for u in w["upgrade_table"][:max(0,level-1)])
                        for i in range(amount):
                            self.spawn_fan_shot(player, name, level, i, amount)
                        player.attributes[cooldown_key] = w["cooldown"]
                    elif name == "Cross":
                        # 获取当前等级的属性
                        amount = 1
                        if level >= 4:
                            amount = 2
                        if level >= 7:
                            amount = 3
                            
                        # 发射序列状态
                        if "cross_shot_seq" not in player.attributes:
                            player.attributes["cross_shot_seq"] = None
                        seq = player.attributes["cross_shot_seq"]
                        
                        if current_cooldown <= 0 and seq is None:
                            # 冷却到0，初始化发射序列
                            player.attributes["cross_shot_seq"] = {
                                "amount": amount,
                                "interval": 6,  # 0.1秒间隔（6帧）
                                "next_shot": 0,
                                "shots_left": amount,
                                "base_angle": None  # 记录本轮齐射基准角度
                            }
                            player.attributes[cooldown_key] = w["cooldown"]  # 设置总冷却时间
                            continue
                            
                        # 处理发射序列
                        if seq is not None:
                            if seq["shots_left"] > 0:
                                if seq["next_shot"] <= 0:
                                    # 寻找最近的敌人，计算发射角度
                                    nearest_enemy = None
                                    min_dist = float('inf')
                                    for enemy_type in [ENEMY, ENEMY_ELITE]:
                                        for enemy in self.get_particles(enemy_type):
                                            dx = enemy.x - player.x
                                            dy = enemy.y - player.y
                                            dist = math.sqrt(dx * dx + dy * dy)
                                            if dist < min_dist:
                                                min_dist = dist
                                                nearest_enemy = enemy
                                    
                                    # 计算发射角度
                                    if nearest_enemy:
                                        angle = math.degrees(math.atan2(nearest_enemy.y - player.y, nearest_enemy.x - player.x))
                                    else:
                                        angle = random.uniform(0, 360)  # 如果没有敌人，随机方向
                                        
                                    # 发射单个十字架
                                    self.spawn_boomerang(player, name, level, angle)
                                    seq["shots_left"] -= 1
                                    seq["next_shot"] = seq["interval"]
                                else:
                                    seq["next_shot"] -= 1
                            if seq["shots_left"] <= 0:
                                player.attributes["cross_shot_seq"] = None
                            continue
                        # 冷却递减
                        if current_cooldown > 0:
                            player.attributes[cooldown_key] -= 1
                        continue
                    elif name == "Garlic":
                        # Check if we need to create or recreate the Garlic aura
                        existing_garlic = next((w for w in self.get_particles(WEAPON) 
                                              if w.attributes.get("weapon_name") == "Garlic" and 
                                              w.attributes.get("target_player_id") == player.attributes["id"]), None)
                        if not existing_garlic:
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
            
            # Handle Garlic aura damage
            if wname == "Garlic" and weapon.attributes.get("is_aura"):
                # Update weapon position to follow player
                target_player = next((p for p in self.get_particles(PLAYER) if p.attributes["id"] == weapon.attributes["target_player_id"]), None)
                if target_player:
                    weapon.x = target_player.x
                    weapon.y = target_player.y
                
                # Process duration and cooldown
                weapon.attributes["duration"] -= 1
                if weapon.attributes["duration"] <= 0:
                    # Reset duration using stored cooldown
                    weapon.attributes["duration"] = weapon.attributes.get("cooldown", 78)  # Default to 78 if not stored
                    # Clear hit cooldowns when the aura refreshes
                    weapon.attributes["hit_cooldown"] = {}
                    
                    # Check for enemies in range
                    radius = weapon.attributes.get("aura_radius")  # Use the radius we calculated in spawn_aura
                    print(f"[DEBUG] Garlic aura damage tick - Radius: {radius}, Level: {weapon.attributes.get('level')}")
                    
                    for enemy_type in [ENEMY, ENEMY_ELITE]:
                        for enemy in self.get_particles(enemy_type):
                            if enemy.attributes.get("is_dying"):
                                continue
                            
                            # Calculate distance to enemy
                            dx = enemy.x - weapon.x
                            dy = enemy.y - weapon.y
                            dist = math.sqrt(dx * dx + dy * dy)
                            
                            # If enemy is in range
                            if dist <= radius:
                                enemy_id = enemy.attributes.get("id", -1)
                                hit_cooldown = weapon.attributes.get("hit_cooldown", {})
                                
                                # Check if we can damage this enemy
                                if enemy_id not in hit_cooldown or hit_cooldown[enemy_id] <= 0:
                                    # Apply damage and knockback
                                    damage = weapon.attributes.get("damage", 5)
                                    self.apply_damage(weapon, enemy, damage)
                        
                                    # Apply knockback
                                    knockback = weapon.attributes.get("knockback", 0)
                                    if knockback > 0 and dist > 0:
                                        # Calculate knockback direction (away from aura center)
                                        kdx = dx / dist
                                        kdy = dy / dist
                                        enemy.attributes["knockback_dx"] = kdx
                                        enemy.attributes["knockback_dy"] = kdy
                                        enemy.attributes["knockback_timer"] = 5  # 5 frames of knockback
                                    
                                    # Set cooldown for this enemy (1.3s = 78 frames at 60fps)
                                    hit_cooldown[enemy_id] = 78
                                
                                # Update the hit cooldown dictionary
                                weapon.attributes["hit_cooldown"] = hit_cooldown
                continue
            
            # Handle other weapons
            if wname == "Knife" and "vx" in weapon.attributes and "vy" in weapon.attributes:
                # 保护武器颜色
                self.protect_weapon_colors(weapon)
                weapon.x += weapon.attributes["vx"]
                weapon.y += weapon.attributes["vy"]
                if (weapon.x < -WEAPON_SIZE or weapon.x > SCREEN_WIDTH + WEAPON_SIZE or
                    weapon.y < -WEAPON_SIZE or weapon.y > SCREEN_HEIGHT + WEAPON_SIZE):
                    weapons_to_remove.append(weapon)
                continue
            # 其余武器移动逻辑...（保持原有）

        # Remove expired weapons
        for weapon in weapons_to_remove:
            if weapon in self.particles:  # Check if weapon still exists
                self.remove_particle(weapon)
                
        # Move enemies towards player and check for despawning
        enemies_to_remove = []


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
                if (weapon.x < -WEAPON_SIZE or weapon.x > SCREEN_WIDTH + WEAPON_SIZE or
                    weapon.y < -WEAPON_SIZE or weapon.y > SCREEN_HEIGHT + WEAPON_SIZE):
                    weapons_to_remove.append(weapon)
                continue
            if wname == "MagicWand" and "target_id" not in weapon.attributes and "vx" in weapon.attributes and "vy" in weapon.attributes:
                vx = weapon.attributes.get("vx", 0)
                vy = weapon.attributes.get("vy", 0)
                weapon.x += vx
                weapon.y += vy
                weapon.attributes["last_vx"] = vx
                weapon.attributes["last_vy"] = vy
                if (weapon.x < -WEAPON_SIZE or weapon.x > SCREEN_WIDTH + WEAPON_SIZE or
                    weapon.y < -WEAPON_SIZE or weapon.y > SCREEN_HEIGHT + WEAPON_SIZE):
                    weapons_to_remove.append(weapon)
                continue
            # 十字架的移动逻辑
            if wname == "Cross":
                # 获取当前状态
                has_hit = weapon.attributes.get("has_hit", False)
                
                # 获取当前速度和加速度
                vx = weapon.attributes.get("vx", 0)
                vy = weapon.attributes.get("vy", 0)
                
                # 获取初始速度和方向
                initial_vx = weapon.attributes.get("initial_vx", 0)
                initial_vy = weapon.attributes.get("initial_vy", 0)
                initial_speed = math.sqrt(initial_vx * initial_vx + initial_vy * initial_vy)
                
                # 更新自转角度（使用配置的旋转速度）
                self_rotation = weapon.attributes.get("self_rotation", 0)
                rotation_speed = weapon.attributes.get("rotation_speed", 24)  # 使用配置的旋转速度，默认24
                self_rotation = (self_rotation + rotation_speed) % 360
                weapon.attributes["self_rotation"] = self_rotation
                
                if initial_speed > 0:
                    # 计算当前速度
                    current_speed = math.sqrt(vx * vx + vy * vy)
                    
                    # 计算加速度（始终与初始方向相反）
                    deceleration = 0.2  # 加速度大小
                    ax = -(initial_vx / initial_speed) * deceleration
                    ay = -(initial_vy / initial_speed) * deceleration
                    
                    # 应用加速度
                    vx += ax
                    vy += ay
                    
                    # 检查速度方向是否已经改变（点积小于0表示方向已改变）
                    direction_changed = (vx * initial_vx + vy * initial_vy) < 0
                    
                    if direction_changed:
                        # 如果方向已改变，增加返回加速度
                        return_acceleration = 0.3  # 返回时的加速度大小
                        vx += -initial_vx / initial_speed * return_acceleration
                        vy += -initial_vy / initial_speed * return_acceleration
                    
                    # 限制最大返回速度
                    max_return_speed = initial_speed * 1.5
                    current_speed = math.sqrt(vx * vx + vy * vy)
                    if current_speed > max_return_speed:
                        speed_scale = max_return_speed / current_speed
                        vx *= speed_scale
                        vy *= speed_scale
                
                # 更新位置和速度
                weapon.x += vx
                weapon.y += vy
                weapon.attributes["vx"] = vx
                weapon.attributes["vy"] = vy
                
                # 更新角度（基于当前速度方向）
                if math.sqrt(vx * vx + vy * vy) > 0:
                    weapon.attributes["angle"] = math.degrees(math.atan2(vy, vx))
                
                # 检查是否超出屏幕
                if (weapon.x < -WEAPON_SIZE or weapon.x > SCREEN_WIDTH + WEAPON_SIZE or
                    weapon.y < -WEAPON_SIZE or weapon.y > SCREEN_HEIGHT + WEAPON_SIZE):
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
                    orbit_angle = (orbit_angle + speed * 6) % 360  # 增加旋转速度系数到6
                    weapon.attributes["orbit_angle"] = orbit_angle
                    
                    # 计算新位置
                    rad = math.radians(orbit_angle)
                    # 获取当前持续时间进度
                    duration = weapon.attributes.get("duration", 0)
                    total_duration = weapon.attributes.get("total_duration", 240)  # 4秒 = 240帧
                    fade_duration = 30  # 淡出动画持续30帧 (0.5秒)
                    
                    if duration <= fade_duration:
                        # 在最后0.5秒进行淡出动画
                        fade_progress = duration / fade_duration
                        # 逐渐减小半径，使圣经向玩家靠拢
                        current_radius = orbit_radius * fade_progress
                        # 同时缩小尺寸
                        weapon.attributes["current_size"] = weapon.attributes.get("original_size", 14) * fade_progress
                    else:
                        current_radius = orbit_radius
                    
                    weapon.x = target_player.x + current_radius * math.cos(rad)
                    weapon.y = target_player.y + current_radius * math.sin(rad)
                    
                    # 更新武器角度（用于渲染）
                    weapon.attributes["angle"] = orbit_angle
                    
                    # 检查持续时间
                    if "duration" in weapon.attributes:
                        weapon.attributes["duration"] -= 1
                        if weapon.attributes["duration"] <= 0:
                            if weapon not in weapons_to_remove:  # 避免重复添加
                                weapons_to_remove.append(weapon)
                                # 如果是圣经粒子，在消失时设置冷却时间
                                if weapon.attributes.get("weapon_name") == "KingBible":
                                    # 找到对应的玩家
                                    for player in self.get_particles(PLAYER):
                                        if player.attributes.get("id") == weapon.attributes.get("target_player_id"):
                                            # 设置3秒冷却（180帧）
                                            player.attributes["KingBible_cooldown"] = 180
                                            break
                            continue  # 跳过后续处理
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
                if enemy.x > SCREEN_WIDTH - safe_margin:
                    enemy.x = SCREEN_WIDTH - safe_margin
                if enemy.y > SCREEN_HEIGHT - safe_margin:
                    enemy.y = SCREEN_HEIGHT - safe_margin
                    
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
                        
                        # 将闪烁效果改为变白效果
                        enemy.attributes["white_effect_timer"] = 6  # 0.1秒 = 6帧
                        
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
                            enemy.attributes["death_anim_white"] = True  # 改为True，使死亡时也显示闪白效果


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
                    self.xp_to_next_level = 100 + self.level * 50
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
                if (weapon.x < -WEAPON_SIZE or weapon.x > SCREEN_WIDTH + WEAPON_SIZE or
                    weapon.y < -WEAPON_SIZE or weapon.y > SCREEN_HEIGHT + WEAPON_SIZE):
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
                if (weapon.x < -WEAPON_SIZE or weapon.x > SCREEN_WIDTH + WEAPON_SIZE or
                    weapon.y < -WEAPON_SIZE or weapon.y > SCREEN_HEIGHT + WEAPON_SIZE):
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

        # Handle aura weapons (Garlic)
        for weapon in self.get_particles(WEAPON):
            if weapon.attributes.get("is_aura"):
                # Update aura position to follow player
                for player in self.get_particles(PLAYER):
                    if player.attributes["id"] == weapon.attributes["target_player_id"]:
                        weapon.x = player.x
                        weapon.y = player.y
                        break
                
                # Process duration
                weapon.attributes["duration"] -= 1
                if weapon.attributes["duration"] <= 0:
                    # Reset duration for next tick
                    weapon_type = next((w for w in WEAPON_TYPES if w["name"] == weapon.attributes["weapon_name"]), None)
                    if weapon_type:
                        weapon.attributes["duration"] = weapon_type["cooldown"]
                    
                    # Check for enemies in range
                    radius = weapon.attributes.get("aura_radius")  # Use the radius we calculated in spawn_aura
                    if radius is None:  # Fallback only if radius is not set
                        radius = WEAPON_SIZE * 2
                    
                    for enemy_type in [ENEMY, ENEMY_ELITE]:
                        for enemy in self.get_particles(enemy_type):
                            if enemy.attributes.get("is_dying"):
                                continue
                            
                            # Calculate distance to enemy
                            dx = enemy.x - weapon.x
                            dy = enemy.y - weapon.y
                            dist = math.sqrt(dx * dx + dy * dy)
                            
                            # If enemy is in range
                            if dist <= radius:
                                enemy_id = enemy.attributes.get("id", -1)
                                hit_cooldown = weapon.attributes.get("hit_cooldown", {})
                                
                                # Update cooldown for this enemy
                                if enemy_id in hit_cooldown:
                                    hit_cooldown[enemy_id] = max(0, hit_cooldown[enemy_id] - 1)
                                
                                # Check if we can damage this enemy
                                if enemy_id not in hit_cooldown or hit_cooldown[enemy_id] <= 0:
                                    # Apply damage and knockback
                                    damage = weapon.attributes.get("damage", 5)
                                    self.apply_damage(weapon, enemy, damage)
                                    
                                    # Apply knockback
                                    knockback = weapon.attributes.get("knockback", 0.5)
                                    if knockback > 0 and dist > 0:
                                        # Calculate knockback direction (away from aura center)
                                        kdx = dx / dist
                                        kdy = dy / dist
                                        enemy.attributes["knockback_dx"] = kdx
                                        enemy.attributes["knockback_dy"] = kdy
                                        enemy.attributes["knockback_timer"] = 5  # 5 frames of knockback
                                    
                                    # Set cooldown for this enemy (1.3s = 78 frames at 60fps)
                                    hit_cooldown[enemy_id] = 78
                                
                                # Update the hit cooldown dictionary
                                weapon.attributes["hit_cooldown"] = hit_cooldown
                continue
            
            # Handle other weapon types...

        # 优化：使用空间网格进行碰撞检测
        for weapon in self.get_particles(WEAPON):
            if weapon.attributes.get("is_aura"):
                continue
                
            weapon_size = weapon.attributes.get("size", WEAPON_SIZE)
            # 获取武器附近的粒子
            nearby_enemies = self.get_nearby_particles(weapon.x, weapon.y, weapon_size * 2)
            
            for enemy in nearby_enemies:
                if enemy.kind not in [ENEMY, ENEMY_ELITE] or enemy.attributes.get("is_dying"):
                    continue
                    
                enemy_size = ELITE_SIZE if enemy.kind == ENEMY_ELITE else ENEMY_SIZE
                if self.check_collision(weapon, enemy, weapon_size, enemy_size):
                    # 处理武器和敌人的碰撞
                    damage = weapon.attributes.get("damage", 1)
                    self.apply_damage(weapon, enemy, damage)
                    
                    # 处理击退效果
                    if not enemy.attributes.get("is_dying"):
                        knockback = weapon.attributes.get("knockback", 1.0)
                        if knockback > 0:
                            dx = enemy.x - weapon.x
                            dy = enemy.y - weapon.y
                            dist = math.sqrt(dx * dx + dy * dy)
                            if dist > 0:
                                enemy.attributes["knockback_timer"] = KNOCKBACK_DURATION
                                enemy.attributes["knockback_dx"] = dx / dist
                                enemy.attributes["knockback_dy"] = dy / dist

        # 优化：使用空间网格处理敌人之间的碰撞
        for enemy1 in self.get_particles(ENEMY) + self.get_particles(ENEMY_ELITE):
            if enemy1.attributes.get("is_dying"):
                continue
                
            enemy1_size = ELITE_SIZE if enemy1.kind == ENEMY_ELITE else ENEMY_SIZE
            nearby_enemies = self.get_nearby_particles(enemy1.x, enemy1.y, enemy1_size * 2)
            
            for enemy2 in nearby_enemies:
                if (enemy2.kind not in [ENEMY, ENEMY_ELITE] or 
                    enemy2.attributes.get("is_dying") or 
                    enemy2 is enemy1):
                    continue
                    
                enemy2_size = ELITE_SIZE if enemy2.kind == ENEMY_ELITE else ENEMY_SIZE
                is_colliding, dx, dy, dist = self.check_enemy_collision(enemy1, enemy2)
                
                if is_colliding and dist > 0:
                    # 应用排斥力
                    repulsion = 0.5  # 排斥力强度
                    enemy1.x -= (dx / dist) * repulsion
                    enemy1.y -= (dy / dist) * repulsion
                    enemy2.x += (dx / dist) * repulsion
                    enemy2.y += (dy / dist) * repulsion
                    
                    # 确保敌人不会移出屏幕
                    enemy1.x = max(0, min(SCREEN_WIDTH, enemy1.x))
                    enemy1.y = max(0, min(SCREEN_HEIGHT, enemy1.y))
                    enemy2.x = max(0, min(SCREEN_WIDTH, enemy2.x))
                    enemy2.y = max(0, min(SCREEN_HEIGHT, enemy2.y))

    def agent_action(self, last_action=None):
        """
        AI agent that mimics human player behavior in a Vampire Survivors-like game.
        Prioritizes survival while maintaining smooth movement and strategic XP collection.
        """
        # Handle menu states
        if self.game_state != STATE_PLAYING:
            return self._handle_menu_states()

        # Get player and health info
        player = self.get_particle(PLAYER)
        if not player:
            return [False, False, False, False, False]
            
        # Get current health percentage
        health_percentage = 1.0
        if player.health_system:
            health_percentage = player.health_system.current_hp / player.health_system.max_hp

        # Analyze game state
        game_state = self._analyze_game_state(player, health_percentage)
        
        # Calculate movement direction based on game state
        move_x, move_y = self._calculate_movement(player, game_state, last_action)
        
        # Convert movement to actions
        return self._movement_to_actions(move_x, move_y)

    def _handle_menu_states(self):
        """Handle different menu states with appropriate actions."""
        if self.game_state == STATE_START_MENU:
            button_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
            button_y = SCREEN_HEIGHT // 2 - 30
            self.handle_input(None, (button_x + BUTTON_WIDTH//2, button_y + BUTTON_HEIGHT//2), True)
            return [False, False, False, False, False]
        elif self.game_state == STATE_UPGRADE_MENU:
            if self.upgrade_options:
                upgrade_index = random.randint(0, len(self.upgrade_options) - 1)
                cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
                button_y = cy - 50 + upgrade_index * (BUTTON_HEIGHT + 20)
                button_x = cx - BUTTON_WIDTH // 2
                self.handle_input(None, (button_x + BUTTON_WIDTH//2, button_y + BUTTON_HEIGHT//2), True)
            return [False, False, False, False, False]
        elif self.game_state == STATE_GAME_OVER:
            button_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
            button_y = SCREEN_HEIGHT // 2 - 30
            self.handle_input(None, (button_x + BUTTON_WIDTH//2, button_y + BUTTON_HEIGHT//2), True)
            return [False, False, False, False, False]
        return [False, False, False, False, False]

    def _analyze_game_state(self, player, health_percentage):
        """Analyze the current game state."""
        # 获取所有敌人
        enemies = []
        nearest_enemy = None
        min_distance = float('inf')
        
        for enemy in self.get_particles(ENEMY):
            dx = player.x - enemy.x
            dy = player.y - enemy.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # 计算威胁等级
            threat_level = self._calculate_threat_level(enemy, distance, health_percentage)
            
            # 预测敌人位置
            pred_x, pred_y = self._predict_enemy_position(enemy, dx, dy, distance)
            
            enemy_info = {
                "enemy": enemy,
                "distance": distance,
                "threat_level": threat_level,
                "predicted_x": pred_x,
                "predicted_y": pred_y
            }
            enemies.append(enemy_info)
            
            # 更新最近敌人
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy_info
        
        # 检查是否被包围
        is_surrounded = self._check_surrounded(enemies)
        
        # 获取最近的经验值
        nearest_xp = self._find_nearest_xp(player)
        
        return {
            "enemies": enemies,
            "is_surrounded": is_surrounded,
            "nearest_xp": nearest_xp,
            "health_percentage": health_percentage,
            "player": player,
            "nearest_enemy": nearest_enemy
        }

    def _calculate_threat_level(self, enemy, distance, health_percentage):
        """Calculate threat level for an enemy based on various factors."""
        threat_level = 2.0 if enemy.kind == ENEMY_ELITE else 1.0
        
        # Adjust threat based on distance
        if distance < 100:
            threat_level *= 2.0
        elif distance < 200:
            threat_level *= 1.5
            
        # Adjust threat based on health
        if health_percentage < 0.3:
            threat_level *= 1.5
            
        return threat_level

    def _predict_enemy_position(self, enemy, dx, dy, distance):
        """Predict enemy's position after a short time."""
        if distance == 0:
            return (enemy.x, enemy.y)
            
        enemy_speed = enemy.attributes.get("speed", ENEMY_SPEED_MIN)
        prediction_frames = 10  # Predict 10 frames ahead
        
        predicted_x = enemy.x + (dx / distance) * enemy_speed * prediction_frames
        predicted_y = enemy.y + (dy / distance) * enemy_speed * prediction_frames
        
        return (predicted_x, predicted_y)

    def _check_surrounded(self, enemies):
        """Check if player is surrounded by enemies."""
        if not enemies:
            return False
            
        # 计算敌人分布
        angles = []
        for enemy_info in enemies:
            if enemy_info["distance"] > 300:  # 只考虑较近的敌人
                continue
                
            enemy = enemy_info["enemy"]
            dx = enemy.x - self.get_particle(PLAYER).x
            dy = enemy.y - self.get_particle(PLAYER).y
            angle = math.degrees(math.atan2(dy, dx))
            angles.append(angle)
        
        if len(angles) < 3:  # 至少需要3个敌人才能形成包围
            return False
            
        # 检查角度分布
        angles.sort()
        max_gap = 0
        for i in range(len(angles)):
            gap = (angles[(i + 1) % len(angles)] - angles[i]) % 360
            max_gap = max(max_gap, gap)
            
        # 如果最大间隙小于120度，认为被包围
        return max_gap < 120

    def _find_nearest_xp(self, player):
        """Find the nearest XP particle if it's safe to collect."""
        xp_particles = self.get_particles(XP)
        if not xp_particles:
            return None
            
        nearest_xp = min(xp_particles, key=lambda xp: 
            (player.x - xp.x) ** 2 + (player.y - xp.y) ** 2)
            
        xp_dx = nearest_xp.x - player.x
        xp_dy = nearest_xp.y - player.y
        xp_dist = math.sqrt(xp_dx * xp_dx + xp_dy * xp_dy)
        
        if xp_dist < 200:  # Only consider close XP
            return {
                "xp": nearest_xp,
                "dx": xp_dx,
                "dy": xp_dy,
                "distance": xp_dist
            }
        return None

    def _calculate_movement(self, player, game_state, last_action):
        """Calculate the movement direction for the agent."""
        # 感知系统：获取玩家和敌人位置
        player_pos = (player.x, player.y)
        enemy_positions = [(enemy_info["enemy"].x, enemy_info["enemy"].y) for enemy_info in game_state["enemies"]]
        
        # 威胁评估：创建敌人密度图
        threat_map = self._create_threat_map(player_pos, enemy_positions)
        
        # 检查是否被包围
        if game_state["is_surrounded"]:
            # 逃脱机制：寻找最弱围堵点
            escape_direction = self._find_escape_direction(player_pos, enemy_positions, threat_map)
            move_x, move_y = escape_direction
        else:
            # 在安全区域内，选择最近经验球所在方向
            nearest_xp = self._find_nearest_xp(player)
            if nearest_xp and self._is_safe_to_collect_xp(player, game_state):
                xp_dx = nearest_xp.x - player.x
                xp_dy = nearest_xp.y - player.y
                xp_dist = math.sqrt(xp_dx * xp_dx + xp_dy * xp_dy)
                if xp_dist > 0:
                    move_x = xp_dx / xp_dist
                    move_y = xp_dy / xp_dist
            else:
                # 选择威胁最小的方向
                move_x, move_y = self._find_safest_direction(player_pos, threat_map)
        
        # 移动平滑策略
        if last_action:
            move_x, move_y = self._smooth_movement(move_x, move_y, last_action)
        
        return move_x, move_y

    def _create_threat_map(self, player_pos, enemy_positions):
        """Create a threat map based on enemy positions."""
        threat_map = {}
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
                threat = 0
                for enemy_pos in enemy_positions:
                    dx = x - enemy_pos[0]
                    dy = y - enemy_pos[1]
                    distance = math.sqrt(dx * dx + dy * dy)
                    if distance > 0:
                        threat += 1 / (distance * distance + 1)
                threat_map[(x, y)] = threat
        return threat_map

    def _find_escape_direction(self, player_pos, enemy_positions, threat_map):
        """Find the direction with the least resistance to escape."""
        min_threat = float('inf')
        escape_direction = (0, 0)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            dir_x = math.cos(rad)
            dir_y = math.sin(rad)
            threat = self._calculate_direction_threat(player_pos, dir_x, dir_y, threat_map)
            if threat < min_threat:
                min_threat = threat
                escape_direction = (dir_x, dir_y)
        return escape_direction

    def _calculate_direction_threat(self, player_pos, dir_x, dir_y, threat_map):
        """Calculate the threat in a given direction."""
        threat = 0
        for x, y in threat_map:
            dx = x - player_pos[0]
            dy = y - player_pos[1]
            if dx * dir_x + dy * dir_y > 0:
                threat += threat_map[(x, y)]
        return threat

    def _calculate_escape_path(self, player, enemies):
        """Calculate the best escape path considering enemy movement prediction."""
        best_path = None
        max_safety = -float('inf')
        
        # 获取最近的几个敌人
        nearby_enemies = sorted(enemies, key=lambda x: x["distance"])[:3]
        if not nearby_enemies:
            return None
            
        # 预测敌人的未来位置
        predicted_positions = []
        for enemy_info in nearby_enemies:
            enemy = enemy_info["enemy"]
            # 计算敌人到玩家的方向
            dx = player.x - enemy.x
            dy = player.y - enemy.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                # 预测敌人未来位置（假设敌人会继续向玩家移动）
                pred_x = enemy.x + (dx / dist) * 100  # 预测100单位距离
                pred_y = enemy.y + (dy / dist) * 100
                predicted_positions.append({
                    "x": pred_x,
                    "y": pred_y,
                    "threat": enemy_info["threat_level"]
                })
        
        # 检查16个可能的方向
        for angle in range(0, 360, 23):
            rad = math.radians(angle)
            test_x = math.cos(rad)
            test_y = math.sin(rad)
            
            # 计算这个方向的安全性
            safety = self._calculate_predicted_path_safety(player, test_x, test_y, predicted_positions)
            
            if safety > max_safety:
                max_safety = safety
                best_path = (test_x, test_y)
        
        return best_path

    def _calculate_direction_density(self, player, dir_x, dir_y, enemies):
        """Calculate the density of enemies in a given direction."""
        density = 0
        for enemy_info in enemies:
            enemy = enemy_info["enemy"]
            dx = enemy.x - player.x
            dy = enemy.y - player.y
            if (dx * dir_x + dy * dir_y) > 0:
                density += 1
        return density / len(enemies)

    def _is_direction_safe(self, player, dir_x, dir_y, enemies):
        """Check if a direction is safe based on enemy density."""
        density = self._calculate_direction_density(player, dir_x, dir_y, enemies)
        return density < 0.5

    def _calculate_direction_danger(self, player, dir_x, dir_y, enemies):
        """Calculate the danger of a direction based on enemy density."""
        density = self._calculate_direction_density(player, dir_x, dir_y, enemies)
        return 1.0 - density

    def get_kingbible_damage(self, level):
        """Calculate the damage for the 'KingBible' weapon based on its level."""
        if level <= 3:
            return 10
        elif level <= 6:
            return 20
        else:
            return 30

    def check_enemy_collision(self, enemy1, enemy2):
        """Check for collisions between two enemy particles."""
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
        """Generate blood effects at the specified position."""
        # 限制同时存在的血液粒子数量
        blood_particles = [p for p in self.particles if p.kind == BLOOD]
        if len(blood_particles) >= MAX_BLOOD_PARTICLES:
            return
            
        # 计算可以生成的新粒子数量
        available_slots = MAX_BLOOD_PARTICLES - len(blood_particles)
        count = min(BLOOD_PARTICLE_COUNT, available_slots)
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(BLOOD_PARTICLE_SPEED * 0.5, BLOOD_PARTICLE_SPEED)
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
                        "alpha": 255
                    }
                )
            )
            self.next_id += 1

    def _find_safest_direction(self, player_pos, threat_map):
        """Find the safest direction for the agent to move based on the threat map."""
        min_threat = float('inf')
        safest_direction = (0, 0)
        for x, y in threat_map:
            dx = x - player_pos[0]
            dy = y - player_pos[1]
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 0:
                threat = threat_map[(x, y)]
                if threat < min_threat:
                    min_threat = threat
                    safest_direction = (dx / distance, dy / distance)
        return safest_direction

    def _movement_to_actions(self, move_x, move_y):
        """Convert movement vector to action inputs."""
        actions = [False, False, False, False, False]
        if move_x < -0.3:
            actions[0] = True  # Left
        elif move_x > 0.3:
            actions[1] = True  # Right
        if move_y < -0.3:
            actions[2] = True  # Up
        elif move_y > 0.3:
            actions[3] = True  # Down
        return actions

    def protect_weapon_colors(self, weapon):
        """Protect the colors of weapons to ensure they are not modified."""
        if weapon.attributes.get("weapon_name") == "Knife" and weapon.attributes.get("is_knife"):
            # 恢复飞刀的颜色
            weapon.attributes["main_color"] = "#FFFFFF"
            weapon.attributes["border_color"] = "#8B4513"
            weapon.attributes["shape_color"] = "#FFFFFF"
            weapon.attributes["color_locked"] = True
            weapon.attributes["is_knife"] = True
            weapon.attributes["original_main_color"] = "#FFFFFF"
            weapon.attributes["original_border_color"] = "#8B4513"

    def spawn_damage_text(self, x, y, damage_amount):
        """Generate damage text at the specified position."""
        if int(damage_amount) <= 0:
            return  # 伤害为0不显示跳字
            
        # 限制同时存在的伤害文本数量
        damage_texts = [p for p in self.particles if p.kind == DAMAGE_TEXT]
        if len(damage_texts) >= MAX_DAMAGE_TEXTS:
            # 找到最旧的伤害文本并移除
            oldest_text = min(damage_texts, key=lambda p: p.attributes.get("timer", 0))
            self.remove_particle(oldest_text)
            
        # 如果没有可合并的，创建新的伤害文本
        self.particles.append(
            Particle(
                DAMAGE_TEXT,
                x,
                y,
                attributes={
                    "text": str(int(damage_amount)),
                    "timer": DAMAGE_TEXT_DURATION,
                    "id": self.next_id,
                    "alpha": 255,
                    "scale": 0.5,
                    "scale_phase": "grow",
                    "color": "#FFFFFF"
                }
            )
        )
        self.next_id += 1

    def _is_safe_to_collect_xp(self, player, game_state):
        """Check if it's safe for the agent to collect experience points."""
        # 检查周围是否有敌人
        for enemy_info in game_state["enemies"]:
            if enemy_info["distance"] < 300:  # 增加安全距离
                return False
        
        # 检查是否被包围
        if game_state["is_surrounded"]:
            return False
            
        # 检查当前网格的安全性
        grid_width = SCREEN_WIDTH / 8
        grid_height = SCREEN_HEIGHT / 4
        current_grid_x = int(player.x / grid_width)
        current_grid_y = int(player.y / grid_height)
        
        # 计算当前网格中心点
        center_x = (current_grid_x + 0.5) * grid_width
        center_y = (current_grid_y + 0.5) * grid_height
        
        # 计算当前网格得分
        score = self._calculate_grid_score(player, center_x, center_y, game_state["enemies"], grid_width, grid_height)
        
        # 如果得分太高，认为不安全
        return score < 2.0

    def draw_start_menu(self, frame):
        """Draw the start menu screen."""
        # Background
        frame.add_rectangle(Rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, "#000000"))
        
        # Title
        title_x = SCREEN_WIDTH // 2 - 150
        title_y = SCREEN_HEIGHT // 2 - 100
        frame.add_text(Text(title_x, title_y, "Vampire Survivor", "#FFFFFF", 40))
        
        # Start button
        button_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
        button_y = SCREEN_HEIGHT // 2 - 30  # Match the click detection position
        
        # Button hover effect
        button_background = BUTTON_HOVER_COLOR if self.is_point_in_rect(
            self.mouse_pos[0], self.mouse_pos[1],
            button_x, button_y,
            BUTTON_WIDTH, BUTTON_HEIGHT
        ) else BUTTON_COLOR
        
        # Draw button
        frame.add_rectangle(Rectangle(
            button_x, button_y,
            BUTTON_WIDTH, BUTTON_HEIGHT,
            button_background
        ))
        
        # Button text
        text_x = button_x + BUTTON_WIDTH // 2 - 30
        text_y = button_y + BUTTON_HEIGHT // 2 + 5
        frame.add_text(Text(text_x, text_y, "Start", BUTTON_TEXT_COLOR, 20))
        
        # Instructions
        instruction_x = SCREEN_WIDTH // 2 - 140
        instruction_y = SCREEN_HEIGHT // 2 + 50
        frame.add_text(Text(instruction_x, instruction_y, 
            "WASD to move, survive as long as possible!", "#CCCCCC", 16))