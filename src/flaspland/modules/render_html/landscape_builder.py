from __future__ import annotations
import xml.etree.ElementTree as ET
from pydreamplet import SVG, G, Vector, Rect, Text, Path, Circle, SvgElement
from pydreamplet.markers import Marker, ARROW_SIMPLE
import os
from .svg_files.control_buttons import build_buttons
from .svg_files.get_svg import clean_svg_group, sample_scenery_id, get_train_svg, get_train_color
from .train_paths import TrainPath
from .env_data import EnvData
from pathlib import Path as PathlibPath
import json

import logging
logger = logging.getLogger(__name__)

RESOURCE_DIR = PathlibPath(__file__).resolve().parent

SVG_STYLES = RESOURCE_DIR / "svg_files" / "svg_styles.css"
DYNAMIC_STYLE = RESOURCE_DIR / "standard_style_dynamic.css"
TRAIN_HOVER_TEMPLATE = RESOURCE_DIR / "train_hover_template.css"

HTML_TEMPLATE_FILE = RESOURCE_DIR / "html_template.html"
TRAIN_WIDGET_FILE = RESOURCE_DIR / "train_widget.html"
PAN_ZOOM_SCRIPT = RESOURCE_DIR / "svg-pan-zoom.js"

class LandscapeBuilder:
    def __init__(self, base_dir: PathlibPath, env_data: EnvData, time_frame: int=None, cell_size=25, style_files=[SVG_STYLES, DYNAMIC_STYLE], hover_template=TRAIN_HOVER_TEMPLATE, save=False):
        self.base_dir = base_dir
        self.env_data = env_data
        self.time_frame = time_frame
        self.cell_size = cell_size        
        self.prepare_dynamic_styles(
            styles=style_files,
            train_hover_style_path=hover_template
            )
        self.height = self.env_data.height + 2
        self.width = self.env_data.width + 2
        self.use_groups = []
        self.canvas = self.build_landscape()
        self.control_canvas = self.build_controls(control_cell_size=self.cell_size)
        self.train_paths = self.prepare_train_paths()
        self.display_states = {}
        self.place_trains()
        if save:
            self.save_svg()

    def prepare_dynamic_styles(self, styles, train_hover_style_path):
        # pre-computes all elements that depend on cell size
        self.font_size = self.cell_size / 2
        self.font_size_hover = f"{1.2 * self.font_size}px"
        self.train_path_width = self.cell_size / 30
        self.train_path_width_hover = f"{4 * self.train_path_width}px"

        style_content = ""
        for style_path in styles:
            with open(style_path, "r") as f:
                style_content += f.read()

        style_content = style_content.replace("{{HOVER_FONT_SIZE}}", f"{self.font_size_hover}")

        # generate train fill colors
        train_fill_colors = ""
        train_info_style = ""
        train_fill_template = ".train-fill-TRAIN_ID{fill: TRAIN_COLOR;}"
        train_info_template = ".train_TRAIN_ID_background { background-color: TRAIN_COLOR; }"
        for train_id in self.env_data.trains.keys():
            train_color = get_train_color(train_id)
            train_fill_colors += train_fill_template.replace("TRAIN_ID", str(train_id)).replace("TRAIN_COLOR", train_color) + "\n"
            train_info_style += train_info_template.replace("TRAIN_ID", str(train_id)).replace("TRAIN_COLOR", train_color) + "\n"
        style_content = style_content.replace("{{TRAIN_INFO_STYLE}}", train_info_style)
        style_content = style_content.replace("{{TRAIN_FILL_COLORS}}", train_fill_colors)

        self.standard_style = style_content

        # prepare train hover styles
        with open(train_hover_style_path, "r") as f:
            train_hover_template = f.read()
        train_hover_style = ""
        for train_id in self.env_data.trains.keys():
            train_hover_style += train_hover_template.replace("TRAIN_ID", str(train_id)).replace("HOVER_WIDTH", f"{self.train_path_width_hover}") + "\n"
        self.standard_style = self.standard_style.replace("{{TRAIN_HOVER_STYLE}}", train_hover_style)

    def save_svg(self, output_filename=None):
        if not output_filename:
            output_filename = os.path.join(self.base_dir, "landscape.svg")
        static_svg = self.full_svg.to_string()
        static_svg = ET.ElementTree(ET.fromstring(static_svg))
        # add style element
        style_element = ET.Element("style")
        style_element.text = self.standard_style
        static_svg.getroot().insert(0, style_element)
        with open(output_filename, "w") as f:
            f.write(ET.tostring(static_svg.getroot(), encoding='unicode'))
    
    def svg_string(self):
        return self.full_svg.to_string()
    
    def canvas_string(self):
        return self.canvas.to_string()
    
    def control_svg_string(self):
        return self.control_canvas.to_string()

    def get_abs_coord(self, coord, grid_offset=True):
        offset = 1 if grid_offset else 0
        # convert coordinates to absolute svg coordinates. If grid_offset, add margin for grid labels
        return (coord + offset) * self.cell_size
        
    def get_abs_vector(self, x, y, grid_offset=True):
        # convert coordinates to absolute svg coordinates. If grid=True, add margin for grid labels
        offset = 1 if grid_offset else 0
        # convert grid coords to absolute svg coords, allowing for 1 cell margin
        abs_x = (x + offset) * self.cell_size
        abs_y = (y + offset) * self.cell_size
        return Vector(abs_x, abs_y)
    
    def cell_label(self, x, y, text):
        label = Text(text)
        label.font_family = "monospace"
        label.font_size = self.font_size * 0.8
        label.fill = "#000000"
        label.font_weight = 700
        label.stroke_width = self.cell_size * .02
        label.pos = self.get_abs_vector(x + .5, y +.5)
        label.text_anchor = "middle"
        label.dominant_baseline = "central"
        return label

    def get_use_id(self, file_path, scale=240):
        file_name = file_path.stem
        if file_name in self.use_groups:
            return file_name
        cell_group = clean_svg_group(file_path, file_name, self.cell_size, scale=scale)
        cell_group.pos = Vector(0,0)
        self.defs.append(cell_group)
        self.use_groups.append(file_name)
        return file_name

    def build_landscape(self):
        self.full_svg = SVG(self.width * self.cell_size, self.height * self.cell_size, id="svg_canvas")
        self.canvas = G(class_name="svg-pan-zoom-viewport")
        self.defs = SvgElement("defs")
        self.full_svg.append(self.canvas)
        # self.prepare_use_groups()
        self.canvas.append(self.defs)
        # set background color
        self.canvas.append(Rect(pos=self.get_abs_vector(0,0), width=self.env_data.width * self.cell_size, height=self.env_data.height * self.cell_size, class_name="background"))

        landscape = G(id="landscape", class_name="landscape")
        self.canvas.append(landscape)

        # label rows and columns
        for y in range(self.env_data.height):
            label_group = G(id=f"row_label_{y}", class_name="row_label")
            # add a rect covering the whole row as first child for easier selection
            label_background = Rect(
                pos=self.get_abs_vector(-1, y, grid_offset=True),
                width=(self.env_data.width + 2) * self.cell_size,
                height=self.cell_size,
                fill="#000000",
                fill_opacity=0.0,
                id=f"row_label_{y}_background"
            )
            label_group.append(label_background)
            label_left = self.cell_label(-1, y, str(y))
            label_group.append(label_left)
            label_right = self.cell_label(self.env_data.width, y, str(y))
            label_group.append(label_right)
            landscape.append(label_group)
        for x in range(self.env_data.width):
            label_group = G(id=f"col_label_{x}", class_name="col_label")
            # add a rect covering the whole column as first child for easier selection
            label_background = Rect(
                pos=self.get_abs_vector(x, -1, grid_offset=True),
                width=self.cell_size,
                height=(self.env_data.height + 2) * self.cell_size,
                fill="#000000",
                fill_opacity=0.0,
                id=f"col_label_{x}_background"
            )
            label_group.append(label_background)
            top_label = self.cell_label(x, -1, str(x))
            label_group.append(top_label)
            bottom_label = self.cell_label(x, self.env_data.height, str(x))
            label_group.append(bottom_label)
            landscape.append(label_group)

        for y in self.env_data.grid:
            for x in self.env_data.grid[y]:
                tile = self.env_data.grid[x][y]
                station_id = None
                if tile.file:
                    use_id = self.get_use_id(tile.file)
                    if tile.station:
                        station_id = self.get_use_id(tile.station)
                else:
                    use_id = "0"


                group_id = f"cell_{x}_{y}_t{use_id}"
                cell_group = G(id=group_id, class_name="cell")
                cell_image = SvgElement("use")
                cell_image.href = f"#{use_id}"
                cell_pos = self.get_abs_vector(x, y, grid_offset=True)
                cell_image.transform = f"translate({cell_pos.x}, {cell_pos.y})"
                cell_group.append(cell_image)

                if station_id:
                    station_image = SvgElement("use")
                    station_image.href = f"#{station_id}"
                    station_image.transform = f"translate({cell_pos.x}, {cell_pos.y})"
                    cell_group.append(station_image)
                # add invisible rect to capture hover events with stroke to show grid
                hover_rect = Rect(
                    pos=cell_pos,
                    width=self.cell_size,
                    height=self.cell_size,
                    stroke="#000000",
                    stroke_width=1,
                    stroke_opacity=0.05,
                    fill="#000000",
                    fill_opacity=0.0,
                    id=f"cell_{x}_{y}_hover_rect"
                )
                cell_group.append(hover_rect)

                coord_label = self.cell_label(x, y, f"{x},{y}")
                coord_label.opacity = 0.0
                cell_group.append(coord_label)
                landscape.append(cell_group)
        return self.canvas
    
    def prepare_train_paths(self):
        """
        Generates a default path element for each train to be populated later.
        Added to self.train_path_group so that it appears behind trains.
        """
        self.train_path_group = G(id="train_paths", class_name="train_paths")
        self.canvas.append(self.train_path_group)
        train_paths = {}
        for train_id in self.env_data.trains.keys():
            path_element = Path(
                d="",
                stroke=get_train_color(train_id),
                stroke_width=self.train_path_width,
                stroke_dasharray=f"{self.cell_size * 0.2},{self.cell_size * 0.2}",
                stroke_linecap="round",
                fill="none",
                id=f"train_{train_id}_path",
                class_name=f"train_{train_id}_path",
                opacity=1.0
                )
            self.train_path_group.append(path_element)
            train_paths[train_id] = path_element
        return train_paths

    def place_trains(self):
        """
        Calls TrainPath to build paths for each train and prepares their respective SVG elements.
        """
        for train_id in self.env_data.trains:
            logger.debug(f"Placing train {train_id}")
            train_color = get_train_color(train_id)
            # container to hold all elements of the train for easy highlighting
            train_group = G(id=f"train_{train_id}_main", class_name="train")
            train_info = self.env_data.trains[train_id]
            # build train path
            logger.debug(f"Initializing TrainPath for train {train_id} with time frame {self.time_frame}")
            train_path_builder = TrainPath(train_id, train_info, self.time_frame, self.cell_size)
            path_string = train_path_builder.path_string
            self.display_states[train_id] = train_path_builder.get_display_states()
            self.train_paths[train_id].d = path_string

            # Prepare train SVG
            train_render_group = get_train_svg(train_id, self.cell_size, scale=240)
            logger.debug(f"Train render group for train {train_id} prepared")

            # Train rotation group normalizes position so that mid point is at (0,0) for easier rotation (set in JavaScript)
            # rotation needs to be set to 90 degrees initially to align with the motion path direction
            train_rotation_group = G(id=f"train_{train_id}_rotation_group", class_name="train_rotation")

            # add a rect behind the train as first child for easier selection
            background_rect = Rect(
                pos=Vector(0, 0),
                rx=self.cell_size/5, ry=self.cell_size/5,
                width=self.cell_size,
                height=self.cell_size,
                stroke=train_color,
                stroke_width=self.cell_size / 15,
                stroke_opacity=0.0,
                fill=train_color,
                fill_opacity=0.0,
                id=f"train_{train_id}_background",
                class_name="train_background"
            )
            train_rotation_group.append(background_rect)

            train_rotation_group.append(train_render_group)
            train_rotation_group.pos = Vector(-self.cell_size/2, -self.cell_size/2)
            train_rotation_group.__setattr__("transform-origin", "center")
            train_rotation_group.angle = 90

            transformed_train_group = G(id=f"train_{train_id}_transformed_group", class_name="train_transformed")
            transformed_train_group.append(train_rotation_group)
            # Make animation group, takes care of positioning and rotation during animation
            train_animation_group = G(id=f"train_{train_id}_animation_group", class_name="train_animation")

            path_animation = ET.Element("animateMotion", {
                "id": f"train_{train_id}_animate",
                "dur": "1s",    # to be set in JavaScript
                "path": "", # to be set in JavaScript
                "repeatCount": "1",
                # "repeatCount": "indefinite", # for debugging
                "fill": "freeze",
                "rotate": "auto",
                "path": "",
                "keyPoints": "0;1",
                "keyTimes": "0;1",
                "calcMode": "linear"
            })
            train_animation_group.append(path_animation)
            train_animation_group.append(transformed_train_group)

            opacity_animation = ET.Element("animate", {
                "id": f"train_{train_id}_opacity_animation",
                "attributeName": "opacity",
                "dur": "1s",    # to be set in JavaScript
                "repeatCount": "1",
                # "repeatCount": "indefinite", # for debugging
                "fill": "freeze",
                "from": "1",
                "to": "1",
                "begin": "0s"
            })
            train_animation_group.append(opacity_animation)

            train_group.append(train_animation_group)

            self.canvas.append(train_group)
    
    def build_controls(self, control_cell_size):
        control_cell_size = control_cell_size
        control_width = 1000
        control_height = 2 * control_cell_size
        control_canvas = SVG(control_width, control_height)

        buttons_x = control_width - 7 * control_cell_size
        buttons_y = control_cell_size
        controls_group = build_buttons(control_cell_size)
        controls_group.pos = Vector(
            buttons_x,
            buttons_y
        )
        control_canvas.append(controls_group)
        
        slider_group = G(id="slider_group", class_name="slider")
        control_canvas.append(slider_group)

        slider_x = control_cell_size
        slider_y = buttons_y
        slider_width = buttons_x - 2 * control_cell_size
        # make invisible rect behind slider for calculating time steps
        slider_background = Rect(
            pos=Vector(slider_x, slider_y),
            width=slider_width,
            height=control_cell_size,
            fill="#000000",
            fill_opacity=0.0,
            id="slider_background",
            class_name="slider_background"
        )
        slider_group.append(slider_background)
        # make a path from .5 to self.buttons_x - 1 on height control_y + .5 for time step slider
        slider_path = Path(
            class_name="slider-path",
            d=f"M {slider_x},{slider_y + .5 * control_cell_size} L {slider_x + slider_width},{slider_y + .5 * control_cell_size}",
            stroke_width=control_cell_size * 0.5,
            stroke_linecap="round",
            fill="none",
            id="time_step_slider_path"
        )
        slider_group.append(slider_path)

        slider_handle = Circle(
            cx=slider_x + 0.5 * control_cell_size, 
            cy=slider_y + .5 * control_cell_size, r=control_cell_size*.4, 
            stroke_width=control_cell_size * 0.1, 
            id="slider_handle", 
            class_name="slider-handle")
        slider_group.append(slider_handle)

        step_group = G(id="step_legend", class_name="step_legend")
        step_group.pos = Vector(
            slider_x + slider_width / 2,
            slider_y - 0.5 * control_cell_size
        )
        step_label = Text(
            initial_text="Time Step: 0",
            class_name="footer-svg-foreground",
            font_family="monospace",
            font_size=control_cell_size * 0.7,
            font_weight=700,
            dominant_baseline="central",
            text_anchor="middle",
            id="step_label"
            )
        step_group.append(step_label)
        slider_group.append(step_group)
        return control_canvas

    def build_html(self, milliseconds_per_step=400, html_template_file=HTML_TEMPLATE_FILE, train_widget_file=TRAIN_WIDGET_FILE, pan_zoom_script=PAN_ZOOM_SCRIPT):
        svg_output = self.canvas_string()
        control_svg_output = self.control_svg_string()

        with open(html_template_file, "r") as f:
            html_template = f.read()
        with open(pan_zoom_script, "r") as f:
                pan_zoom_script_content = f.read()
        
        html_output = html_template.replace("{{HEADING}}", f"Flaspland SVG Animation: {self.env_data.name}")
        html_output = html_output.replace("{{STANDARD_CSS}}", self.standard_style)
        html_output = html_output.replace("{{INLINE_SVG}}", svg_output)
        html_output = html_output.replace("{{CONTROL_SVG}}", control_svg_output)
        html_output = html_output.replace("{{PAN_ZOOM_SCRIPT}}", pan_zoom_script_content)

        train_widgets = self.build_train_widgets()
        html_output = html_output.replace("{{TRAIN_WIDGETS}}", train_widgets)
        html_output = html_output.replace("{{TRAIN_DATA}}", json.dumps(self.display_states, indent=4))

        train_defs = ""
        path_defs = ""
        for train_id in self.env_data.trains.keys():
            train_defs += f"const train_{train_id}_rotation = document.getElementById('train_{train_id}_rotation_group');\n"
            train_defs += f"const train_{train_id}_animate = document.getElementById('train_{train_id}_animate');\n"
            train_defs += f"const train_{train_id}_opacity_animation = document.getElementById('train_{train_id}_opacity_animation');\n"
            path_defs  += f"const path_{train_id} = data[\"{train_id}\"];\n"
            train_defs += f"const train_{train_id}_status = document.getElementById('train_{train_id}_status');\n"
            train_defs += f"const train_{train_id}_action = document.getElementById('train_{train_id}_action');\n"
            train_defs += f"const train_{train_id}_pos = document.getElementById('train_{train_id}_pos');\n"
            # train_defs += f"const train_{train_id}_action_label = document.getElementById('train_{train_id}_action_label');\n"
            # train_defs += f"const train_{train_id}_position_label = document.getElementById('train_{train_id}_position_label');\n"
            # train_defs += f"const train_{train_id}_signal_group = document.getElementById('train_{train_id}_signal_group');\n"
            
        html_output = html_output.replace("{{TRAIN_DEFS}}", train_defs)
        html_output = html_output.replace("{{PATH_DEFS}}", path_defs)
    
        html_output = html_output.replace("{{MAX_STEP}}", str(self.time_frame))
    
        html_output = html_output.replace("{{MILLISECONDS_PER_STEP}}", str(milliseconds_per_step))

        path_step_code = ""
        for train_id in self.env_data.trains.keys():
            path_step_code += f"  const state_{train_id} = path_{train_id}[step];\n"
            path_step_code += f"  train_{train_id}_animate.setAttribute('dur', `${{ms_per_step}}ms`);\n"
            path_step_code += f"  train_{train_id}_animate.setAttribute('keyPoints', `${{state_{train_id}.keyPoints}}`);\n"
            path_step_code += f"  train_{train_id}_animate.setAttribute('path', `${{state_{train_id}.motionPath}}`);\n"
            path_step_code += f"  train_{train_id}_animate.beginElement();\n"
            # # debugging:
            # path_step_code += f"  train_{train_id}_rotation.setAttribute('opacity', '1');\n"
            # path_step_code += f"  train_{train_id}_opacity_animation.setAttribute('dur', '{milliseconds_per_step}ms');\n"
            # set 'ms_per_step' to match the animation duration
            path_step_code += f"  train_{train_id}_opacity_animation.setAttribute('dur', `${{ms_per_step}}ms`);\n"
            # path_step_code += f"  train_{train_id}_opacity_animation.setAttribute('values', `${{state_{train_id}.opacity}}`);\n"
            path_step_code += f"  train_{train_id}_opacity_animation.setAttribute('from', state_{train_id}.opacity[0]);\n"
            path_step_code += f"  train_{train_id}_opacity_animation.setAttribute('to', state_{train_id}.opacity[1]);\n"
            path_step_code += f"  train_{train_id}_status.textContent = `Status: ${{state_{train_id}.status}}`;\n"
            path_step_code += f"  train_{train_id}_action.textContent = ` Action: ${{state_{train_id}.action}}`;\n"
            path_step_code += f"  train_{train_id}_pos.textContent = ` Position: [${{state_{train_id}.position}}]`;\n"
            # path_step_code += f"  train_{train_id}_action_label.textContent = `${{state_{train_id}.action}}`;\n"
            # path_step_code += f"  train_{train_id}_position_label.textContent = `${{state_{train_id}.position}}`;\n"
            # add signal logic: if "", add class "hide"; if "red" add class "red"; if "green" add class "green"
            path_step_code += f"  train_{train_id}_signal_group.classList.remove('hide', 'red', 'green');\n"
            path_step_code += f"  if (state_{train_id}.signal === 'red') {{\n"
            path_step_code += f"    train_{train_id}_signal_group.classList.add('red');\n"
            path_step_code += f"  }} else if (state_{train_id}.signal === 'green') {{\n"
            path_step_code += f"    train_{train_id}_signal_group.classList.add('green');\n"
            path_step_code += f"  }} else {{\n"
            path_step_code += f"    train_{train_id}_signal_group.classList.add('hide');\n"
            path_step_code += f"  }}\n"
    
        html_output = html_output.replace("{{PATH_STEP}}", path_step_code)

        stop_animation_code = ""
        for train_id in self.env_data.trains.keys():
            stop_animation_code += f"  train_{train_id}_animate.endElement();\n"
        html_output = html_output.replace("{{STOP_ANIMATION}}", stop_animation_code)
    
        slider_offset = self.get_abs_coord(1.5, grid_offset=False)
        html_output = html_output.replace("{{SLIDER_OFFSET}}", str(slider_offset))
    
        return html_output

    def build_train_widgets(self, train_widget_file=TRAIN_WIDGET_FILE):
        with open(train_widget_file, "r") as f:
            train_widget_template = f.read()
        train_widgets = ""
        for train_id in self.env_data.trains.keys():
            widget = train_widget_template.replace("{{TRAIN_ID}}", str(train_id))
            widget = widget.replace("{{SPEED}}", str(self.env_data.trains[train_id]['speed']))
            train_widgets += widget
        return train_widgets

    def save_html(self, filename="visualization.html"):
        html_content = self.build_html()
        filename = self.base_dir / filename
        with open(filename, "w") as f:
            f.write(html_content)
        logger.info(f"Visualization saved to {filename}")