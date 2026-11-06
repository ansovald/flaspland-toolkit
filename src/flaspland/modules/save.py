# functions for saving a Flatland environment as various file types

from flatland.utils.rendertools import RenderTool
import pickle
import json
from .visualization import Landscape, EnvData
from pathlib import Path

def save_lp(env, file_name, file_location):
    """ 
    save the clingo representation as an .lp file to be loaded later 
    """
    with open(f"{file_location}lp/{file_name}.lp", "w") as f:
        f.write(env)


def save_png(env, file_name, file_location):
    """ 
    visually render a given environment and save image to file
    """
    DO_RENDERING = True    
    env_renderer = RenderTool(env, gl="PILSVG")
    env_renderer.reset()

    if env_renderer is not None:
        env_renderer.render_env(show=True, show_observations=False, show_predictions=False)
        env_renderer.gl.save_image(f"{file_location}png/{file_name}.png")
        env_renderer.reset()


def save_pkl(env, file_name, file_location):
    """ 
    save a given rail environment metadata as a pickle file to be loaded later 
    """
    pickle.dump(env, open(f"{file_location}pkl/{file_name}.pkl", "wb"))

def save_svg(env, file_name: str, file_location: Path | str):
    env_data = EnvData(env, env_name=file_name)
    landscape = Landscape.from_env_data(env_data=env_data, cell_size=25)
    landscape.save_svg(Path(file_location) / "svg" / f"{file_name}.svg")