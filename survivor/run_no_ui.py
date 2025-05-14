#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import time
import importlib

def run(game_name, fps=60):
    """运行游戏的核心逻辑，但不显示UI"""
    # 导入游戏模块
    module_name = "games." + game_name
    game_module = importlib.import_module(module_name)
    game_state = game_module.Game()
    game_state.reset_level()
    
    # 设置游戏状态为正在游戏
    game_state.game_state = "playing"
    
    print("开始运行游戏 {}...".format(game_name))
    
    last_action = [False, False, False, False, False]
    frame_time = 1.0 / fps
    
    try:
        while True:
            start_time = time.time()
            
            # 更新游戏状态
            game_state.step(last_action)
            
            # 如果是代理控制，获取代理动作
            new_action = game_state.agent_action(last_action)
            last_action = new_action
            
            # 控制帧率
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_time - elapsed)
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        print("\n游戏已停止")
    
    print("游戏结束")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        game_name = sys.argv[1]
    else:
        game_name = "survivor"
    
    fps = 60
    if len(sys.argv) > 2:
        try:
            fps = int(sys.argv[2])
        except ValueError:
            pass
    
    run(game_name, fps) 