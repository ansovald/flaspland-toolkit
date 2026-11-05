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
    html_template = html_template_path.read_text()
    svg_pan_zoom = svg_pan_zoom_path.read_text()
    html_template = html_template.replace("PAN_ZOOM_SCRIPT", svg_pan_zoom)
    return html_template

def get_train_definitions(num_trains: int, train_def_template_path=TRAIN_DEF_TEMPLATE_PATH):
    train_def_template = train_def_template_path.read_text()
    train_defs = ""
    for id in range(num_trains):
        train_def = train_def_template.replace("TRAIN_ID", str(id))
        train_defs += train_def
    return train_defs

def get_train_widgets(num_trains: int, train_widget_path=TRAIN_WIDGET_PATH):
    train_widget = train_widget_path.read_text()
    train_widgets = ""
    for id in range(num_trains):
        widget = train_widget.replace("TRAIN_ID", str(id))
        widget = widget.replace("SPEED", "0")
        train_widgets += widget
    return train_widgets

def get_train_rules(num_trains: int, cell_size: int, train_style_template_path=TRAIN_STYLE_TEMPLATE_PATH):
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
    train_animation_template = train_animation_template_path.read_text()
    train_animation_code = ""
    stop_animation_template = stop_animation_template_path.read_text()
    stop_animation_code = ""
    for id in range(num_trains):
        train_animation_code += train_animation_template.replace("TRAIN_ID", str(id))
        stop_animation_code += stop_animation_template.replace("TRAIN_ID", str(id))

    return train_animation_code, stop_animation_code

def get_dynamic_style(num_trains: int, cell_size: int, dynamic_style_path=DYNAMIC_STYLE_PATH):
    # Prepare train color variables for CSS
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
    dynamic_style = dynamic_style = dynamic_style.replace(
            "RECT_STROKE_WIDTH", sizes["rect_stroke_width"]
        ).replace(
            "TRAIN_PATH_WIDTH", sizes["train_path_width"]
        ).replace(
            "TRAIN_PATH_DASHARRAY", sizes["train_path_dasharray"]
        ).replace(
            "/* TRAIN_COLORS */", train_color_vars
        ).replace(
            "/* TRAIN_STYLES */", get_train_rules(num_trains=num_trains, cell_size=cell_size)
        )
    return dynamic_style
    