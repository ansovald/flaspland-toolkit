# rendering visualizations
# from flatland.envs.rail_env import RailEnvActions
from flatland.utils.rendertools import RenderTool
import imageio.v2 as imageio
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import tempfile

from .visualization import get_train_data, Landscape, Animation, EnvData
from .defs import DIR_MAP, ACTION_MAP

import json

import logging
logger = logging.getLogger(__name__)

class Renderer():
    def __init__(self, env, env_name, *args, **kwargs):
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
        super().__init__(env, env_name)
        self.env_renderer = RenderTool(env, gl=gl)
        self.env_renderer.reset()
        self.images = []
        # temporary directory for the rendered frames
        self.frames = tempfile.TemporaryDirectory()
        self.font = font
        if self.font is None:
            self.font = Path(__file__).resolve().parent / "LiberationMono-Regular.ttf"

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

class HtmlRenderer(Renderer):
    def __init__(self, env, env_path, env_name, cell_size=25, milliseconds_per_step=400):
        logger.info("Initializing HtmlRenderer")
        super().__init__(env, env_name)
        
        self.milliseconds_per_step = milliseconds_per_step

        svg_path = Path(*("svg" if part == "pkl" else part for part in Path(env_path).parts))
        if svg_path.suffix == ".pkl":
            svg_path = svg_path.with_suffix(".svg")
        try:
            # Check if there is already an SVG version of the landscape corresponding to the environment path
            landscape = Landscape.from_svg(svg_path)
            self.landscape = landscape
        except Exception as e:
            logger.info(f"Failed to load landscape from {svg_path}: {e}")
            env_name = env_path.stem
            env_data = EnvData(env, env_name)
            landscape = Landscape.from_env_data(env_data=env_data, cell_size=cell_size)
            svg_path.parent.mkdir(parents=True, exist_ok=True)
            landscape.save_svg(svg_path)
            logger.info(f"Landscape created and saved to {svg_path}")
            self.landscape = landscape

        self.train_data = get_train_data(env)
        self.timeframe = 0

    def render_frame(self, timestep, actions):
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

        animation = Animation(landscape=self.landscape, train_data=self.train_data, timeframe=self.timeframe, env_name=self.env_name)
        animation.save_html(output_dir / "visualization.html", milliseconds_per_step=self.milliseconds_per_step)


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
