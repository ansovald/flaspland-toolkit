from pydreamplet import G, Vector, Path, Circle, Rect
import xml.etree.ElementTree as ET
from pathlib import Path as FilePath
import logging

logger = logging.getLogger(__name__)

SVG_DIR = FilePath(__file__).resolve().parent

# Used for scaling SVG elements consistently. The original SVG tiles all hav dim 240x240.
SVG_SCALE = 240

TRACK_FILES = []
track_dir = SVG_DIR / "tracks"
# track files consist only of numbers
for file in track_dir.iterdir():
    if file.name.endswith(".svg") and file.name.split(".")[0].isdigit():
        TRACK_FILES.append(file)

# def make_signal_group(signal_id, cell_size=25, scale=SVG_SCALE):
#     """
#     Create an SVG group representing a signal at a specific position.
#     The signal consists of a background path and two lights (red and green).
#     """
#     signal_group = G(id=f"signal_{signal_id}_group", class_name="train_signal")
#     primitives = G(id=f"signal_{signal_id}_primitives", class_name="signal_primitives")
#     background = Path(d="m 228,76.8 c 0,9.941 -8.059,18 -18,18 -9.941,-0 -18,-8.059 -18,-18 V 30 c 0,-9.941 8.059,-18 18,-18 9.941,0 18,8.059 18,18z", style="stroke: #000000; stroke-width: 14.4;")
#     primitives.append(background)
#     red_light = Circle(cx=210, cy=30, r=18, style="fill: #cc3232;", id=f"signal_{signal_id}_red_light", class_name="red_light")
#     primitives.append(red_light)
#     green_light = Circle(cx=210, cy=76.8, r=18, style="fill: #2dc937;", id=f"signal_{signal_id}_green_light", class_name="green_light")
#     primitives.append(green_light)
#     primitives.scale = Vector(cell_size/scale, cell_size/scale)
#     transform_group = G(id=f"signal_{signal_id}_transform_group", class_name="signal_transform")
#     transform_group.set_attr("transform", f"translate({cell_size/2}, {-cell_size/2})")
#     # transform_group.pos = Vector(-cell_size/2, -cell_size/2)
#     transform_group.append(primitives)
#     signal_group.append(transform_group)
#     return signal_group

def get_signal_svg(signal_id, rotation, cell_size=25, scale=SVG_SCALE):
    """
    Signal SVG is stored as a generic template and customized for each signal using its ID
    """
    svg_file = SVG_DIR / "generic_signal.xml"
    svg_string = svg_file.read_text()
    svg_string = svg_string.replace("{SIGNAL_ID}", str(signal_id))

    # customize the generic xml, and scale it to cell size
    scale_group = clean_svg_group(svg_string, f"signal_{signal_id}_scale", cell_size, scale)
    # move the midpoint of the scaled signal to the origin for clean rotation
    origin_group = G(id=f"signal_{signal_id}_origin")
    origin_group.set_attr("transform", f"translate({-cell_size/2}, {-cell_size/2})")
    origin_group.append(scale_group)
    # rotate the signal to the correct angle
    rotation_group = G(id=f"signal_{signal_id}_rotation")
    rotation_group.set_attr("transform", f"rotate({rotation})")
    rotation_group.append(origin_group)

    # wrap the rotated signal in a group for further positioning and handling
    signal_group = G(id=f"signal_{signal_id}", class_name="signal")
    signal_group.append(rotation_group)
    return signal_group

def get_train_svg(train_id, cell_size=25, scale=SVG_SCALE):
    """
    Train SVG is stored as a generic template and customized for each train using its ID
    """
    # Generic train svg file used as a template for all trains, with placeholders for train id and color
    svg_file = SVG_DIR / "generic_train.xml"
    svg_string = svg_file.read_text()
    svg_string = svg_string.replace("{TRAIN_ID}", str(train_id))
    train_group = clean_svg_group(svg_string, f"train_{train_id}_group", cell_size, scale, class_name="train")
    train_group.id = f"train_{train_id}_group"
    # train_group.append(make_signal_group(train_id))
    return train_group

def make_train_group(train_id, cell_size=25, scale=SVG_SCALE):
    """
    Create a train group containing the train itself and background, rotation, and animation groups.
    """
    train_group = G(id=f"train_{train_id}", 
                    class_name="train",
                    opacity="1")
    
    train_render_group = get_train_svg(train_id, cell_size, scale)
    train_rotation_group = G(id=f"train_{train_id}_rotation_group", class_name="train_rotation")

    background_rect = Rect(
        pos=Vector(0, 0),
        rx=cell_size/5, ry=cell_size/5,
        width=cell_size,
        height=cell_size,
        id=f"train_{train_id}_rect",
        class_name=f"train_background train_rect train_{train_id}_rect"
    )
    train_rotation_group.append(background_rect)
    train_rotation_group.append(train_render_group)
    train_rotation_group.pos = Vector(-cell_size/2, -cell_size/2)
    train_rotation_group.__setattr__("transform-origin", "center")
    train_rotation_group.angle = 90

    transformed_train_group = G(id=f"train_{train_id}_transformed_group", class_name="train_transformed")
    transformed_train_group.append(train_rotation_group)

    train_animation_group = G(id=f"train_{train_id}_animation_group", class_name="train_animation")
    path_animation = ET.Element("animateMotion", {
        "id": f"train_{train_id}_animate",
        "dur": "1s",    # to be set in JavaScript
        "path": "", # to be set in JavaScript
        "repeatCount": "1", # set to `indefinite` for debugging
        "fill": "freeze",
        "rotate": "auto",
        "keyPoints": "0;1",
        "keyTimes": "0;1",
        "calcMode": "linear"
    })
    train_animation_group.append(path_animation)
    train_animation_group.append(transformed_train_group)

    train_group.append(train_animation_group)

    return train_group


def clean_svg_group(svg_file, group_id, cell_size=25, scale=SVG_SCALE, class_name=None):
    """
    Loads an SVG file or string, cleans it by removing elements (definitions, title, style) 
    not necessary when visualizing the environment, and adds the remaining element to a new SVG group.
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
