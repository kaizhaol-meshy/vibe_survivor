#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib
import time
import random

def run_test():
    # 导入游戏模块
    module_name = "games.survivor"
    game_module = importlib.import_module(module_name)
    game_state = game_module.Game()
    game_state.reset_level()
    
    print("开始测试游戏逻辑...")
    
    # 设置游戏状态为正在游戏
    game_state.game_state = "playing"
    
    # 确保玩家有武器
    player = game_state.get_particle("player")
    if player:
        # 确保玩家有所有武器
        weapons = {w["name"]: 1 for w in game_module.WEAPON_TYPES}
        player.attributes["weapons"] = weapons
        print(f"玩家已装备武器: {weapons}")
    
    # 强制生成一些敌人
    for _ in range(5):
        game_state.spawn_enemy()
    
    # 强制生成所有武器
    if player:
        weapons = player.attributes.get("weapons", {})
        for w_type in game_module.WEAPON_TYPES:
            name = w_type["name"]
            if name in weapons and weapons[name] > 0:
                level = weapons[name]
                behavior = w_type["behavior"]
                
                if behavior == "orbit" and name == "KingBible":
                    lvl = min(level, len(game_module.KING_BIBLE_LEVELS)) - 1
                    props = game_module.KING_BIBLE_LEVELS[lvl]
                    amount = props["amount"]
                    for i in range(amount):
                        game_state.spawn_orbiting_book(player, name, level, i, amount)
                elif behavior == "horizontal_slash":
                    game_state.spawn_whip(player, name, level)
                elif behavior == "homing_missile":
                    game_state.spawn_homing_missile(player, name, level)
                elif behavior == "straight_shot":
                    game_state.spawn_straight_shot(player, name, level)
                elif behavior == "arc_throw":
                    game_state.spawn_arc_throw(player, name, level, 0, 1)
                elif behavior == "boomerang":
                    game_state.spawn_boomerang(player, name, level)
                elif behavior == "fan_shot":
                    game_state.spawn_fan_shot(player, name, level, 0, 1)
                elif behavior == "aura":
                    game_state.spawn_aura(player, name, level)
    
    # 运行游戏逻辑一段时间
    num_frames = 600  # 运行10秒
    actions = [False, False, False, False, False]
    
    for frame in range(num_frames):
        # 随机移动方向
        if frame % 30 == 0:  # 每半秒改变一次方向
            move_left = random.choice([True, False])
            move_right = random.choice([True, False])
            move_up = random.choice([True, False])
            move_down = random.choice([True, False])
            actions = [move_left, move_right, move_up, move_down, False]
        
        # 更新游戏逻辑
        game_state.step(actions)
        
        # 每隔一段时间输出状态
        if frame % 60 == 0:
            enemies = game_state.get_particles("enemy")
            weapons = game_state.get_particles("weapon")
            print(f"帧 {frame}: 敌人数量 = {len(enemies)}, 武器数量 = {len(weapons)}")
            
            # 检查敌人生命值
            for i, enemy in enumerate(enemies[:3]):  # 只显示前三个敌人
                if enemy.health_system:
                    hp = enemy.health_system.current_hp
                    print(f"  敌人 {i+1} HP: {hp}")
        
        time.sleep(1 / 60)  # 保持60帧的帧率
    
    print("测试完成！")

if __name__ == "__main__":
    run_test() 