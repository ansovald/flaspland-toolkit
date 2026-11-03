from flatland.envs.rail_env import RailEnv
from flatland.envs.agent_utils import Agent
import pickle
import json
import logging
logger = logging.getLogger(__name__)

def grid_dict(env: RailEnv) -> dict:
    """
    Convert Flatland environment to a grid dictionary
    """
    rail_map = env.rail.grid
    height, width = env.height, env.width
    grid_dict = {}

    for row in range(height):
        grid_dict[row] = {}
        for col in range(width):
            grid_dict[row][col] = str(rail_map[row][col])

    return grid_dict

def train_info(env: RailEnv) -> dict:
    """
    Extract train information from Flatland environment
    """
    dir_map = {0:"n", 1:"e", 2:"s", 3:"w"}
    train_dict = {}

    for agent_num, agent in enumerate(env.agents):
        (init_y, init_x), init_dir = agent.initial_configuration

        # Toolkit has a set of targets with different directions. We don't need those, so we just pick the first one.
        (goal_y, goal_x) = list(agent.targets)[0] [0]
        min_start, max_end = agent.earliest_departure, agent.latest_arrival
        speed = int(1/agent.speed_counter.speed) # inverse, e.g. 1/2 --> 2, 1/4 --> 4 etc.
        direction = dir_map[init_dir]

        train_dict[agent_num] = {
            "start": {
                "position": {
                    "x": int(init_x),
                    "y": int(init_y)
                }, 
                "min_start": int(min_start), 
                "direction": direction
                },
            "end": {
                "position": {
                    "x": int(goal_x),
                    "y": int(goal_y)
                },
                "max_end": int(max_end)
                },
            "speed": int(speed),
            "path": {}
        }

    return train_dict
