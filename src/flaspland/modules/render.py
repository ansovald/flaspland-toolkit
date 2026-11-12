from flatland.utils.rendertools import RenderTool
import imageio.v2 as imageio
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import tempfile

from .visualization import get_train_data, Landscape, Animation, EnvData
from .defs import DIR_MAP, ACTION_MAP

import json

from abc import abstractmethod

import logging
logger = logging.getLogger(__name__)

class Renderer():
    """
    Wrapper class for rendering visualizations of Flatland environments.
    """
    def __init__(self, env, env_name, *args, **kwargs):
        self.env = env
        self.env_name = env_name

    @abstractmethod
    def process_actions(self, timestep, *args, **kwargs):
        pass

    @abstractmethod
    def save(self, output_dir, *args, **kwargs):
        pass

class GifRenderer(Renderer):
    """
    Renderer class for creating GIF animations using the default rendering tool.
    """
    def __init__(self, env, env_name, gl="PILSVG", font=None):
        logger.info(f"Initializing GifRenderer for environment {env_name}")
        super().__init__(env, env_name)
        self.env_renderer = RenderTool(env, gl=gl)
        self.env_renderer.reset()
        self.images = []
        # temporary directory for the rendered frames
        self.frames = tempfile.TemporaryDirectory()
        self.font = font
        if self.font is None:
            self.font = Path(__file__).resolve().parent / "LiberationMono-Regular.ttf"

    def process_actions(self, timestep, *args, **kwargs):
        """
        Renders the frame for the given timestep using the current environment state.
        """
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

class HtmlRenderer(Renderer):
    """
    HTML renderer for visualizing controllable, animated Flatland environments.
    """
    def __init__(self, env, env_path, env_name, config):
        logger.info(f"Initializing HtmlRenderer for environment {env_name}")
        super().__init__(env, env_name)
        logger.debug(f"HtmlRenderer config:\n{config}")
        self.milliseconds_per_step = config.get("ms_per_step", 300)
        cell_size = config.get("cell_size", 25)
        self.log_train_states = config.get("log_train_states", False)
        self.train_colors = config.get("train_colors", ["#d50000", "#2979ff", "#ff6f00", "#fdd835", "#00c853", "#aa00ff", "#00bfa5", "#c51162", "#64dd17", "#304ffe", "#ffd600", "#00b8d4", "#9e9e9e", "#ff1744", "#00e676", "#6200ea", "#2962ff", "#aeea00", "#f50057", "#00b0ff"])

        svg_path = Path(*("svg" if part == "pkl" else part for part in Path(env_path).parts))
        if svg_path.suffix == ".pkl":
            svg_path = svg_path.with_suffix(".svg")
        try:
            # Check if there is already an SVG version of the landscape corresponding to the environment path
            landscape = Landscape.from_svg(svg_path)
            self.landscape = landscape
        except Exception as e:
            logger.info(f"Failed to load landscape from {svg_path}: {e}, attempting to create from environment data.")
            env_name = env_path.stem
            env_data = EnvData(env, env_name)
            landscape = Landscape.from_env_data(env_data=env_data, cell_size=cell_size)
            svg_path.parent.mkdir(parents=True, exist_ok=True)
            landscape.save_svg(svg_path)
            logger.info(f"Landscape created and saved to {svg_path}")
            self.landscape = landscape

        self.train_data = get_train_data(env)
        self.timeframe = 0

    def process_actions(self, timestep, actions):
        """
        Builds a record of train positions, directions, statuses, and actions for the given timestep.
        Later used to calculate the train paths for visualization.
        """
        for a in actions[timestep]:
            (x, y), direction = get_position_and_direction(self.env.agents[a])
            self.train_data[a]["path"][timestep] = {
                "position": {"x": x, "y": y},
                "direction": direction,
                "status": self.env.agents[a].state.name,
                "action": ACTION_MAP[actions[timestep][a]]
            }
        self.timeframe = timestep

    def save(self, output_dir, *args, **kwargs):
        output_file = output_dir / "train_info.json"
        with open(output_file, "w") as f:
            json.dump(self.train_data, f, indent=4)
        logger.info(f"Train info saved to {output_file}")

        try:
            animation = Animation(landscape=self.landscape, train_data=self.train_data, timeframe=self.timeframe + 1, env_name=self.env_name, train_colors=self.train_colors, log_train_states=self.log_train_states)
            animation.save_html(output_dir / "visualization.html", milliseconds_per_step=self.milliseconds_per_step)
        except Exception as e:
            # logger.error(f"Failed to save HTML visualization: {e}")
            raise e


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
