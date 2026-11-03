# rendering visualizations
# from flatland.envs.rail_env import RailEnvActions
from flatland.utils.rendertools import RenderTool
from flatland.envs.rail_env import RailEnv
import imageio.v2 as imageio
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import tempfile

from .render_html import train_info, grid_dict, LandscapeBuilder, generate_html
from .defs import DIR_MAP, ACTION_MAP

import json

import logging
logger = logging.getLogger(__name__)

DIR_MAP = {0:'n', 1:'e', 2:'s', 3:'w'}

class Renderer():
    def __init__(self, env, env_name):
        self.env = env
        self.env_name = env_name
        logger.info(f"Initializing Renderer for environment {env_name}")

    def render_frame(self, timestep):
        pass

    def save(self, output_dir, *args, **kwargs):
        pass

class GifRenderer(Renderer):
    def __init__(self, env, env_name, gl="PILSVG", font=None):
        logger.info("Initializing GifRenderer")
        super().__init__(env)
        self.env_renderer = RenderTool(env, gl=gl)
        self.env_renderer.reset()
        self.images = []
        # temporary directory for the rendered frames
        self.frames = tempfile.TemporaryDirectory()
        self.font = font
        if self.font is None:
            self.font = Path(__file__).resolve().parent / "LiberationMono-Regular.ttf"

    def __del__(self):
        self.frames.cleanup()

    def render_frame(self, timestep, *args, **kwargs):
        filename = Path(self.frames.name) / f'flatland_frame_{timestep:04d}.png'
        self.env_renderer.render_env(show=True, show_observations=False, show_predictions=False)
        self.env_renderer.gl.save_image(str(filename))
        self.env_renderer.reset()

        # add red numbers in the corner
        with Image.open(filename) as img:
            draw = ImageDraw.Draw(img)
            padding = 10
            font_size = int(min(img.width, img.height) * 0.10)
            try:
                font = ImageFont.truetype(str(self.font), font_size)
            except IOError:
                font = ImageFont.load_default()

            text = f"{timestep}"
            size = font.getbbox(text)
            text_width = size[2]-size[0]
            text_position = (img.width - text_width - padding, padding)

            x, y = text_position
            border_color = "black"
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                draw.text((x + dx, y + dy), text, fill=border_color, font=font)

            draw.text(text_position, text, fill="red", font=font)
            img.save(filename)

        self.images.append(imageio.imread(filename))

    def save(self, output_dir, loop=0, duration=240):
        self.make_gif(output_dir=output_dir, loop=loop, duration=duration)

    def make_gif(self, output_dir, loop=0, duration=240):
        output_file = Path(output_dir) / "animation.gif"
        imageio.mimsave(output_file, self.images, format='GIF', loop=loop, duration=duration)
        logger.info(f"GIF saved to {output_file}")


def get_position_and_direction(agent):
    """ get an agent's position and direction; position is None while the agent is off the map """
    if agent.current_configuration is not None:
        return (agent.current_configuration)
    # off the map: use the arrival direction if done, otherwise the starting direction
    if agent.target_configuration is not None:
        return (None, agent.target_configuration[1])
    return (None, agent.initial_configuration[1])

class HtmlRenderer(Renderer):
    def __init__(self, env, env_name, cell_size=25, milliseconds_per_step=500):
        logger.info("Initializing HtmlRenderer")
        super().__init__(env, env_name)
        self.train_info = train_info(env)
        self.time_frame = 0
        self.cell_size = cell_size
        self.milliseconds_per_step = milliseconds_per_step
        self.grid = grid_dict(env)

    def render_frame(self, timestep, actions):
        for a in actions[timestep]:
            (x, y), direction = get_position_and_direction(self.env.agents[a])
            self.train_info[a]["path"][timestep] = {
                "position": {"x": x, "y": y},
                "direction": direction,
                "status": self.env.agents[a].state.name,
                "action": ACTION_MAP[actions[timestep][a]]
            }
        self.time_frame = timestep

    def save(self, output_dir, *args, **kwargs):
        output_file = Path(output_dir) / "train_info.json"
        with open(output_file, "w") as f:
            json.dump(self.train_info, f, indent=4)
        logger.info(f"Train info saved to {output_file}")

        landscape = LandscapeBuilder(output_dir, self.grid, time_frame=self.time_frame, train_info=self.train_info, cell_size=self.cell_size)
        html_rendering = generate_html(self.env_name, landscape, milliseconds_per_step=self.milliseconds_per_step)
        with open(Path(output_dir) / "visualization.html", "w") as f:
            f.write(html_rendering)
        logger.info(f"Visualization saved to {Path(output_dir) / 'visualization.html'}")


def get_position_and_direction(agent):
    if agent.current_configuration is not None:
        (y, x), direction = agent.current_configuration
        y = int(y)
        x = int(x)
    elif agent.target_configuration is not None:
        y, x = None, None
        direction = agent.target_configuration[1]
    else:
        y, x = None, None
        direction = agent.initial_configuration[1]
    direction = DIR_MAP[direction]
    return (x, y), direction

def grid_to_dict(env: RailEnv) -> dict:
    """
    Convert the grid of a RailEnv into a dictionary representation.
    """

    rail_map = env.rail.grid
    height, width = env.height, env.width
    grid_dict = {}
    for row in range(height):
        grid_dict[row] = {}
        for col in range(width):
            grid_dict[row][col] = str(rail_map[row][col])
    return grid_dict