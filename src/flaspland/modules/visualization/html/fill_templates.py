from pathlib import Path
from ..load_templates import load_template

# Template files that should be in the `templates` directory relative from where flaspland is executed
HTML_TEMPLATE_FN = "template.html"
TRAIN_WIDGET_FN = "train_widget.html"
DYNAMIC_STYLE_FN = "dynamic_style.css"
TRAIN_STYLE_TEMPLATE_FN = "train_style_template.css"

# Static paths to template files that are stored in this module (not copied to the user's instance)
TRAIN_ANIMATION_TEMPLATE_PATH = Path(__file__).parent / "train_animation_template.js"
STOP_ANIMATION_TEMPLATE_PATH = Path(__file__).parent / "stop_animation_template.js"
SVG_PAN_ZOOM_PATH = Path(__file__).parent / "svg-pan-zoom.js"
TRAIN_DEF_TEMPLATE_PATH = Path(__file__).parent / "train_def_template.js"

SIGNAL_DEF_TEMPLATE_PATH = Path(__file__).parent / "signal_def_template.js"
SIGNAL_ANIMATION_TEMPLATE_PATH = Path(__file__).parent / "signal_animation_template.js"

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

def get_html(svg_pan_zoom_path=SVG_PAN_ZOOM_PATH, html_template_fn=HTML_TEMPLATE_FN):
    """
    Load the main HTML template and inject the SVG pan-zoom script.
    """
    html_template = load_template(html_template_fn)
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

def get_train_widgets(train_data: dict, train_widget_fn=TRAIN_WIDGET_FN):
    """
    Generate HTML ino widgets for each train to be displayed on the right side of the interface.
    """
    train_widget = load_template(train_widget_fn)
    train_widgets = ""
    for id, train_info in train_data.items():
        widget = train_widget.replace("TRAIN_ID", str(id))
        widget = widget.replace("SPEED", str(train_info["speed"]))
        train_widgets += widget
    return train_widgets

def get_train_rules(num_trains: int, cell_size: int, train_style_template_fn=TRAIN_STYLE_TEMPLATE_FN):
    """
    Generate CSS rules for each train based on the dynamic sizes and train ID.
    """
    sizes = get_dynamic_sizes(cell_size)
    train_style_template = load_template(train_style_template_fn)
    train_style_template = train_style_template.replace(
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

def get_signal_definitions(num_signals: int, signal_def_template_path=SIGNAL_DEF_TEMPLATE_PATH):
    """
    Generate JS code for signal definitions for each signal.
    """
    signal_def_template = signal_def_template_path.read_text()
    signal_def_code = ""
    for id in range(num_signals):
        signal_def_code += signal_def_template.replace("SIGNAL_ID", str(id))
    return signal_def_code

def get_signal_animations(num_signals: int, signal_animation_template_path=SIGNAL_ANIMATION_TEMPLATE_PATH):
    """
    Generate JS code for signal animations for each signal.
    """
    signal_animation_template = signal_animation_template_path.read_text()
    signal_animation_code = ""
    for id in range(num_signals):
        signal_animation_code += signal_animation_template.replace("SIGNAL_ID", str(id))
    return signal_animation_code

def get_dynamic_style(num_trains: int, cell_size: int, train_colors: list = None, dynamic_style_fn=DYNAMIC_STYLE_FN):
    """
    Generate the dynamic CSS style including train colors, sizes, and train-specific hover rules.
    """
    def get_train_color(id: int):
        try:
            if id > len(train_colors) - 1:
                id = id % len(train_colors)
            return train_colors[id]
        except:
            return "#FFFFFF"  # default color if train_colors is not provided or index is out of range
    train_color_vars = ""
    train_color_template = "  --train-TRAIN_ID-color: TRAIN_COLOR;"
    for id in range(num_trains):
        train_color_vars += train_color_template.replace(
                "TRAIN_ID", str(id)
            ).replace(
                "TRAIN_COLOR", get_train_color(id)
            )
    sizes = get_dynamic_sizes(cell_size)
    dynamic_style = load_template(dynamic_style_fn)
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
    