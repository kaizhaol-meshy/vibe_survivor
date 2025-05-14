# -*- coding: utf-8 -*-
import os
import argparse
import random
import numpy as np
import time
from server import Server
from datasets import Dataset
# import cv2
import importlib


def run(game_name, agent=False, gen_frames=0, port=0, save_name=None):
    file_name = game_name
    # Import the file
    import importlib

    module_name = "games." + file_name
    game_module = importlib.import_module(module_name)
    game_state = game_module.Game()
    game_state.reset_level()
    server = Server(port)
    server.start()

    num_inputs = game_state.num_inputs
    last_action = [0] * num_inputs

    print("max_num_particles: {}".format(game_state.max_num_particles))
    print("num_inputs: {}".format(num_inputs))

    states_all = []
    frame_count = 0
    force_restart_interval = 250
    shuffled_copies = 5

    show_every = 1 if gen_frames == 0 else 1000
    prev_encoded = ""
    while True:
        # Update and render
        game_state.step(last_action)
        
        # Get either agent or player actions
        if agent:
            new_action = game_state.agent_action(None)
            keys = game_state.get_user_keys(new_action)
            if frame_count % force_restart_interval == 0 and frame_count > 0:
                game_state.reset_level()
        else:
            keys = server.get_key_pressed()
            new_action = game_state.get_user_inputs(keys)
            # Get mouse information and pass it to the game
            mouse_pos, mouse_clicked = server.get_mouse_info()
            game_state.handle_input(new_action, mouse_pos, mouse_clicked)

        # 每100帧输出一次粒子信息
        if frame_count % 100 == 0:
            try:
                particles_info = {p_type: len(game_state.get_particles(p_type)) for p_type in ["player", "enemy", "weapon", "xp"]}
                print("帧 {}: 粒子数量 = {}".format(frame_count, particles_info))
            except Exception as e:
                print("调试输出错误: {}".format(e))

        # Store state if generating data
        if gen_frames > 0:
            encoded = game_state.encode()
            for _ in range(shuffled_copies):
                shuffle_encoded = game_state.shuffle_encode()
                states_all.append({
                    "prev_game_state": prev_encoded,
                    "cur_game_state": shuffle_encoded,
                    "user_input": ", ".join(keys)
                })
                states_all.append({
                    "prev_game_state": prev_encoded,
                    "cur_game_state": "{" + "id:{}".format(game_state.next_id + random.randint(0, 10)) + "}",
                    "user_input": ", ".join(keys)
                })
            frame_count += 1
            prev_encoded = encoded
            if frame_count >= gen_frames:
                Dataset.from_list(states_all).save_to_disk(save_name)
                print("Saved {} frames".format(gen_frames))
                return

            if frame_count % show_every == 0:
                print("Step {} of {}".format(frame_count, gen_frames))

        if gen_frames == 0 or frame_count % show_every == 0:
            server.update_frame(game_state.get_frame())
            frame_count += 1  # 确保计数器增加
            if gen_frames == 0:
                time.sleep(1 / game_state.fps)

        last_action = new_action


parser = argparse.ArgumentParser()
# The 1st parameter is the game name
parser.add_argument(
    "game_name", type=str, help="The name of the game to run, e.g., 'mario'"
)
parser.add_argument(
    "-s", "--save_name", type=str, help="The name of the file to save the states to"
)

parser.add_argument(
    "-a", "--agent", action="store_true", help="Use AI agent instead of player input"
)
parser.add_argument(
    "-g", "--generate", type=int, default=0, help="Generate n frames of training data"
)
parser.add_argument(
    "-p", "--port", type=int, default=8080, help="Port to run the server on"
)

args = parser.parse_args()

if __name__ == "__main__":
    if args.generate > 0:
        args.agent = True
    run(args.game_name, agent=args.agent, gen_frames=args.generate, port=args.port, save_name=args.save_name)
