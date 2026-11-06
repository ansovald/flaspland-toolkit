from pathlib import Path
from ..svg import get_train_color

HTML_TEMPLATE_PATH = Path(__file__).parent / "template.html"

TRAIN_WIDGET_PATH = Path(__file__).parent / "train_widget.html"

DYNAMIC_STYLE_PATH = Path(__file__).parent / "dynamic_style.css"

TRAIN_STYLE_TEMPLATE_PATH = Path(__file__).parent / "train_style_template.css"

TRAIN_ANIMATION_TEMPLATE_PATH = Path(__file__).parent / "train_animation_template.js"
STOP_ANIMATION_TEMPLATE_PATH = Path(__file__).parent / "stop_animation_template.js"

SVG_PAN_ZOOM_PATH = Path(__file__).parent / "svg-pan-zoom.js"

TRAIN_DEF_TEMPLATE_PATH = Path(__file__).parent / "train_def_template.js"

def get_dynamic_sizes(cell_size: int):
    """
    Calculate sizes for different style elements based on the cell size.
    """
    train_path_width = cell_size / 30
    hover_width = 4 * train_path_width
    rect_stroke_width = train_path_width * 2
    train_path_dash = cell_size * 0.2
    return {
        # make strings with max. 2 decimal places
        "train_path_width": f"{train_path_width:.2f}px",
        "hover_width": f"{hover_width:.2f}px",
        "rect_stroke_width": f"{rect_stroke_width:.2f}px",
        "train_path_dasharray": f"{train_path_dash:.2f}px,{train_path_dash:.2f}px"
    }

def get_html(html_template_path=HTML_TEMPLATE_PATH, svg_pan_zoom_path=SVG_PAN_ZOOM_PATH):
    """
    Load the main HTML template and inject the SVG pan-zoom script.
    """
    html_template = html_template_path.read_text()
    svg_pan_zoom = svg_pan_zoom_path.read_text()
    html_template = html_template.replace("PAN_ZOOM_SCRIPT", svg_pan_zoom)
    return html_template

def get_train_definitions(num_trains: int, train_def_template_path=TRAIN_DEF_TEMPLATE_PATH):
    """
    Create a JS snippet containing all relevant variable definitions for each train.
    """
    train_def_template = train_def_template_path.read_text()
    train_defs = ""
    for id in range(num_trains):
        train_def = train_def_template.replace("TRAIN_ID", str(id))
        train_defs += train_def
    return train_defs

def get_train_widgets(train_data: dict, train_widget_path=TRAIN_WIDGET_PATH):
    """
    Generate HTML ino widgets for each train to be displayed on the right side of the interface.
    """
    train_widget = train_widget_path.read_text()
    train_widgets = ""
    for id, train_info in train_data.items():
        widget = train_widget.replace("TRAIN_ID", str(id))
        widget = widget.replace("SPEED", str(train_info["speed"]))
        train_widgets += widget
    return train_widgets

def get_train_rules(num_trains: int, cell_size: int, train_style_template_path=TRAIN_STYLE_TEMPLATE_PATH):
    """
    Generate CSS rules for each train based on the dynamic sizes and train ID.
    """
    sizes = get_dynamic_sizes(cell_size)
    train_style_template = train_style_template_path.read_text().replace(
            "HOVER_WIDTH", sizes["hover_width"]
        ).replace(
            "RECT_STROKE_WIDTH", sizes["rect_stroke_width"]
        )
    train_rules = ""
    for id in range(num_trains):
        train_rules += train_style_template.replace("TRAIN_ID", str(id))
    return train_rules

def get_train_animations(num_trains: int, train_animation_template_path=TRAIN_ANIMATION_TEMPLATE_PATH, stop_animation_template_path=STOP_ANIMATION_TEMPLATE_PATH):
    """
    Generate JS code for train animations and stop animations for each train.
    """
    train_animation_template = train_animation_template_path.read_text()
    train_animation_code = ""
    stop_animation_template = stop_animation_template_path.read_text()
    stop_animation_code = ""
    for id in range(num_trains):
        train_animation_code += train_animation_template.replace("TRAIN_ID", str(id))
        stop_animation_code += stop_animation_template.replace("TRAIN_ID", str(id))

    return train_animation_code, stop_animation_code

def get_dynamic_style(num_trains: int, cell_size: int, dynamic_style_path=DYNAMIC_STYLE_PATH):
    """
    Generate the dynamic CSS style including train colors, sizes, and train-specific hover rules.
    """
    train_color_vars = ""
    train_color_template = "  --train-TRAIN_ID-color: TRAIN_COLOR;"
    for id in range(num_trains):
        train_color_vars += train_color_template.replace(
                "TRAIN_ID", str(id)
            ).replace(
                "TRAIN_COLOR", get_train_color(id)
            )
    sizes = get_dynamic_sizes(cell_size)
    dynamic_style = dynamic_style_path.read_text()
    replacements = {
        "RECT_STROKE_WIDTH": sizes["rect_stroke_width"],
        "TRAIN_PATH_WIDTH": sizes["train_path_width"],
        "TRAIN_PATH_DASHARRAY": sizes["train_path_dasharray"],
        "/* TRAIN_COLORS */": train_color_vars,
        "/* TRAIN_STYLES */": get_train_rules(num_trains=num_trains, cell_size=cell_size)
    }
    for key, value in replacements.items():
        dynamic_style = dynamic_style.replace(key, value)
    return dynamic_style
    