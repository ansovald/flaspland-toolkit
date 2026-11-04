from pydreamplet import G, Vector, Path, Circle
import xml.etree.ElementTree as ET
import random
from pathlib import Path as FilePath

SVG_DIR = FilePath(__file__).resolve().parent

train_colors = ["#d50000", "#2979ff", "#ff6f00", "#fdd835", "#00c853", "#aa00ff", "#00bfa5", "#c51162", "#64dd17", "#304ffe", "#ffd600", "#00b8d4", "#9e9e9e", "#ff1744", "#00e676", "#6200ea", "#2962ff", "#aeea00", "#f50057", "#00b0ff"]

def get_train_color(train_id):
    return train_colors[int(train_id) % len(train_colors)]

TRACK_FILES = []
track_dir = SVG_DIR / "tracks"
# track files consist only of numbers
for file in track_dir.iterdir():
    if file.name.endswith(".svg") and file.name.split(".")[0].isdigit():
        TRACK_FILES.append(file)

def make_signal_group(train_id):
    # Signal group for the train, directly constructed from SVG elements
    signal_group = G(id=f"train_{train_id}_signal_group", class_name="train_signal")
    background = Path(d="m 228,76.8 c 0,9.941 -8.059,18 -18,18 -9.941,-0 -18,-8.059 -18,-18 V 30 c 0,-9.941 8.059,-18 18,-18 9.941,0 18,8.059 18,18z", style="stroke: #000000; stroke-width: 14.4;")
    signal_group.append(background)
    red_light = Circle(cx=210, cy=30, r=18, style="fill: #cc3232;", id=f"train_{train_id}_red_light", class_name="red_light")
    signal_group.append(red_light)
    green_light = Circle(cx=210, cy=76.8, r=18, style="fill: #2dc937;", id=f"train_{train_id}_green_light", class_name="green_light")
    signal_group.append(green_light)
    return signal_group

def get_train_svg(train_id, cell_size=25, scale=240):
    # Generic train svg file used as a template for all trains, with placeholders for train id and color
    svg_file = SVG_DIR / "train-generic.xml"
    svg_string = svg_file.read_text()
    # replace color placeholder with actual color
    svg_string = svg_string.replace("{TRAIN_ID}", str(train_id))
    train_group = clean_svg_group(svg_string, f"train_{train_id}_group", cell_size, scale, class_name="train")
    train_group.id = f"train_{train_id}_group"
    train_group.append(make_signal_group(train_id))
    return train_group

def clean_svg_group(svg_file, group_id, cell_size=25, scale=240, class_name=None):
    """
    Loads an SVG file or string, cleans it by removing elements (mostly style definitions) not necessary 
    when used in the environment visualization, and returns a cleaned SVG group.
    """
    if isinstance(svg_file, FilePath):
        elem = ET.parse(svg_file).getroot()
    elif not svg_file.endswith(".svg"):
        # assume it's a string
        try:
            elem = ET.fromstring(svg_file)
        except ET.ParseError as e:
            raise ValueError(f"passed svg_file doesn't end with .svg, and appears not to be a valid XML string: {e}")
    else:
        elem = ET.parse(SVG_DIR / svg_file).getroot()
    for child in elem.iter():
        if child.tag.endswith("defs") or child.tag.endswith("title") or child.tag.endswith("style"):
            try:
                elem.remove(child)
            except ValueError:
                pass
    group = G(id=group_id)
    for child in elem:
        group.append(child)
    group.scale = Vector(cell_size / scale, cell_size / scale)
    if class_name:
        group.class_name = class_name
    return group