from flatland.envs.rail_env import RailEnv
from ..defs import DIR_MAP
import numpy as np
import logging
from dataclasses import dataclass
from .svg import get_svg_registry, get_track_file

logger = logging.getLogger(__name__)

@dataclass
class Tile:
    file: str = ""
    station: str = ""

class EnvData:
    """
    Class to hold all relevant environment data for rendering purposes, including the grid layout, 
    train information, and station locations.
    Unfortunately, the Render classes of flatland-rl do not provide an easy way to just
    extract the relevant information without loading all images, so we have to rebuild it
    """
    def __init__(self, env: RailEnv, env_name: str):
        self.name = env_name
        self.grid = {}
        self.height = env.height
        self.width = env.width
        self.timeframe = 0
        self.train_count = env.get_num_agents()
        self.stations = []
        self.grid_bounds = {}
        self.background_grid = {}
        self.city_size = 1
        if len(env.agents):
            self.city_size = max(1, np.log(1 + len(env.agents)) / 2.5)
        logger.debug(f"City size calculated: {self.city_size}")
        self._populate_stations(env)
        self._populate_grid(env)

        logger.debug(f"Environment data populated: grid bounds={self.grid_bounds}, train_count={self.train_count}, stations={self.stations}, city size={self.city_size}")
        logger.debug(f"Background grid built:\n{self.background_grid}")

    def _populate_grid(self, env: RailEnv):
        """
        Populate the grid with the file paths of the SVG tiles that are to be displayed.
        Includes the logic for sampling background tiles based on distance to stations and other factors,
        which is modeled after `PILSVG.set_rail_at()`
        """
        if not self.background_grid:
            self._build_background_grid()
        svg_registry = get_svg_registry()
        self.grid = {}
        rail_grid = env.rail.grid
        for col in range(self.width):
            self.grid[col] = {}
            for row in range(self.height):
                tile = Tile()
                if not env.rail.grid[row, col] == 0:
                    tile.file = get_track_file(env.rail.grid[row, col])
                    for s in self.stations:
                        if row == s["y"] and col == s["x"]:
                            tile.station = svg_registry["station"][0]
                            break
                else:
                    distance = int(self.background_grid[col][row])
                    if distance <= 4 + np.ceil(((col * row + col) % 10) / self.city_size):
                        # if distance to next station is small, place a building or scenery file
                        distance = distance % len(svg_registry["buildings"])
                        if (col + row + col * row) % 13 > 11:
                            tile.file = svg_registry["scenery"][distance % len(svg_registry["scenery"])]
                        else:
                            if (col + row + col * row) % 3 == 0:
                                distance = (distance + (col + row + col * row)) % len(svg_registry["buildings"])
                            tile.file = svg_registry["buildings"][distance]
                    elif (
                        (distance > 5 + ((col * row + col) % 3) ) or
                        ((col ** 3 + row ** 2 + col * row) % 10 == 0)
                    ):
                        # if distance is larger, place scenery (possibly spanning three tiles) or water
                        distance = distance - 4
                        a2 = (distance + (col + row + col * row + col ** 3 + row ** 4))
                        if a2 % 64 > 11:
                            distance = a2
                        a_l = distance % len(svg_registry["scenery"])
                        if a2 % 50 == 49:
                            tile.file = svg_registry["scenery_water"][0]
                        else:
                            tile.file = svg_registry["scenery"][a_l]
                        if rail_grid is not None:
                            if a2 % 11 > 3:
                                if a_l == len(svg_registry["scenery"]) - 1:
                                    # 2-wide mountain
                                    if col > 1 and row % 7 == 1:
                                        if rail_grid[row, col - 1] == 0:
                                            self.grid[col - 1][row].type = "scenery"
                                            self.grid[col - 1][row].file = svg_registry["scenery_d2"][0]
                                            tile.file = svg_registry["scenery_d2"][1]
                            else:
                                if a_l == len(svg_registry["scenery"]) - 1:
                                    # 3-wide mountain
                                    if col > 2 and not (row % 7 == 1):
                                        if rail_grid[row, col - 1] == 0 and rail_grid[row, col - 2] == 0:
                                            self.grid[col - 2][row].type = "scenery"
                                            self.grid[col - 2][row].file = svg_registry["scenery_d3"][0]
                                            self.grid[col - 1][row].type = "scenery"
                                            self.grid[col - 1][row].file = svg_registry["scenery_d3"][1]
                                            tile.file = svg_registry["scenery_d3"][2]
                    # if none of the conditions are met, the tile remains empty
                self.grid[col][row] = tile
                logger.debug(f"Placed tile at col={col}, row={row}: {tile}")

        self._find_grid_bounds()

    def _find_grid_bounds(self):
        """
        Find the minimum and maximum x and y coordinates of non-empty tiles in the grid.
        Currently not used, but could be employed to clip the map or viewport to the relevant area
        """
        grid_bounds = {
            "min_x": float('inf'),
            "min_y": float('inf'),
            "max_x": float('-inf'),
            "max_y": float('-inf')
        }
        for row in self.grid:
            for col in self.grid[row]:
                if self.grid[row][col] != 0:
                    grid_bounds['min_x'] = min(grid_bounds['min_x'], col)
                    grid_bounds['min_y'] = min(grid_bounds['min_y'], row)
                    grid_bounds['max_x'] = max(grid_bounds['max_x'], col)
                    grid_bounds['max_y'] = max(grid_bounds['max_y'], row)
        self.grid_bounds = grid_bounds

    def _populate_stations(self, env: RailEnv):
        """
        Find all stations, based on the waypoints of the agents.
        """
        self.stations = []
        for agent_num, agent in enumerate(env.agents):
            for waypoints in agent.waypoints:
                for wp in waypoints:
                    pos = {
                        "x": wp.position[1],
                        "y": wp.position[0]
                    }
                    if pos not in self.stations:
                        self.stations.append(pos)

    def _build_background_grid(self):
        """
        Build a background grid where each cell contains the distance to the nearest station.
        Used later for sampling landscape tiles.
        Modeled after `PILSVG.build_background_map()`
        """
        self.background_grid = {}
        for col in range(self.width):
            self.background_grid[col] = {}
            for row in range(self.height):
                distance = int(np.ceil(np.sqrt(self.width ** 2.0 + self.height ** 2.0)))
                for target in self.stations:
                    d = int(np.floor(np.sqrt((col - target["x"]) ** 2 + (row - target["y"]) ** 2)) / 0.5)
                    distance = min(distance, d)
                self.background_grid[col][row] = distance


def get_train_data(env: RailEnv):
    """
    Base code for extracting train data from the environment.
    Returns a dictionary with train information, including start and end positions, directions, speed, and 
    an initialized path.
    """
    trains = {}
    for agent_num, agent in enumerate(env.agents):
        (init_y, init_x), init_dir = agent.initial_configuration
    
        # Toolkit has a set of targets with different directions. We don't need those, so we just pick the first one.
        (goal_y, goal_x) = list(agent.targets)[0] [0]
        min_start, max_end = agent.earliest_departure, agent.latest_arrival
        speed = int(1/agent.speed_counter.speed) # inverse, e.g. 1/2 --> 2, 1/4 --> 4 etc.
        direction = DIR_MAP[init_dir]
        trains[int(agent_num)] = {
            "start": {
                "position": {
                    "y": int(init_y),
                    "x": int(init_x)
                },
                "min_start": int(min_start),
                "direction": direction
            },
            "end": {
                "position": {
                    "y": int(goal_y),
                    "x": int(goal_x)
                },
                "max_end": int(max_end)
            },
            "speed": int(speed),
            "path": {}
        }
    return trains