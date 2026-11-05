from __future__ import annotations
import xml.etree.ElementTree as ET
from pydreamplet import SVG, G, Vector, Rect, Text, Path, SvgElement
from .svg import clean_svg_group, SVG_STYLE, make_train_group, build_animation_controls
from .html import (get_train_definitions, get_train_widgets, get_train_animations,
                   get_html, get_dynamic_style)
from .train_paths import TrainPath
from .env_data import EnvData
from pathlib import Path as PathlibPath
import json

import logging
logger = logging.getLogger(__name__)

class Landscape:
    def __init__(self, cell_size=25, landscape_width=None, landscape_height=None, width=None, height=None):
        self.cell_size = cell_size
        self.landscape_width = landscape_width
        self.landscape_height = landscape_height
        self.width = width
        self.height = height

    @classmethod
    def from_env_data(cls, env_data: EnvData, cell_size=25, style=SVG_STYLE):
        landscape = cls()
        landscape.sizes_from_env(env_data, cell_size=cell_size)
        landscape.style = style

        # list to hold svg snippets that are used repeatedly (mostly landscape tiles)
        landscape.use_groups = []

        landscape.full_svg = SVG(landscape.width * landscape.cell_size, landscape.height * landscape.cell_size, id="svg_canvas")
        landscape.canvas = G(class_name="svg-pan-zoom-viewport")
        landscape.full_svg.append(landscape.canvas)
        landscape.defs = SvgElement("defs")
        landscape.canvas.append(landscape.defs)

        information = SvgElement("information", 
                                 cell_size=landscape.cell_size,
                                 width=landscape.landscape_width, height=landscape.landscape_height)
        landscape.defs.append(information)

        landscape.build_landscape(env_data=env_data)
        return landscape

    @classmethod
    def from_svg(cls, svg_file: PathlibPath):
        landscape = cls()
        tree = ET.parse(svg_file)
        landscape.full_svg = tree.getroot()
        namespace = {"svg": "http://www.w3.org/2000/svg"}

        landscape.sizes_from_svg(landscape.full_svg, namespace=namespace)

        canvas = landscape.full_svg.find(".//svg:g[@class='svg-pan-zoom-viewport']", namespace)
        landscape.canvas = SVG.from_element(canvas)

        landscape.style = None
        style_el = landscape.full_svg.find(".//svg:style", namespace)
        if style_el is not None:
            landscape.style = style_el.text
            landscape.full_svg.remove(style_el)
        return landscape
        
    def sizes_from_env(self, env_data: EnvData, cell_size: int):
        self.calculate_sizes(cell_size=cell_size, landscape_width=env_data.width, landscape_height=env_data.height)

    def sizes_from_svg(self, svg_data: ET.Element, namespace: dict={"svg": "http://www.w3.org/2000/svg"}):
        background_rect = svg_data.find(".//svg:rect[@class='background']", namespace)
        width = int(background_rect.attrib["width"])
        height = int(background_rect.attrib["height"])
        cell_size = int(float(background_rect.attrib.get("x", 0)))
        width = width / self.cell_size
        height = height / self.cell_size
        self.calculate_sizes(cell_size=cell_size, landscape_width=width, landscape_height=height)

    def calculate_sizes(self, cell_size, landscape_width, landscape_height):
        self.cell_size = cell_size
        self.landscape_width = landscape_width
        self.landscape_height = landscape_height
        self.height = landscape_height + 2
        self.width = landscape_width + 2
        self.font_size = self.cell_size / 2

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

    def get_use_id(self, file_path: PathlibPath, scale=240):
        file_name = file_path.stem
        if file_name in self.use_groups:
            return file_name
        cell_group = clean_svg_group(file_path, file_name, self.cell_size, scale=scale)
        cell_group.pos = Vector(0,0)
        self.defs.append(cell_group)
        self.use_groups.append(file_name)
        return file_name

    def build_landscape(self, env_data: EnvData):
        # set background color
        self.canvas.append(Rect(pos=self.get_abs_vector(0,0), width=self.landscape_width * self.cell_size, height=self.landscape_height * self.cell_size, class_name="background"))

        landscape = G(id="landscape", class_name="landscape")
        self.canvas.append(landscape)

        # label rows and columns
        for y in range(self.landscape_height):
            label_group = G(id=f"row_label_{y}", class_name="row_label")
            # add a rect covering the whole row as first child for easier selection
            label_background = Rect(
                pos=self.get_abs_vector(-1, y, grid_offset=True),
                width=(self.landscape_width + 2) * self.cell_size,
                height=self.cell_size,
                fill="#000000",
                fill_opacity=0.0,
                id=f"row_label_{y}_background"
            )
            label_group.append(label_background)
            label_left = self.cell_label(-1, y, str(y))
            label_group.append(label_left)
            label_right = self.cell_label(self.landscape_width, y, str(y))
            label_group.append(label_right)
            landscape.append(label_group)
        for x in range(self.landscape_width):
            label_group = G(id=f"col_label_{x}", class_name="col_label")
            # add a rect covering the whole column as first child for easier selection
            label_background = Rect(
                pos=self.get_abs_vector(x, -1, grid_offset=True),
                width=self.cell_size,
                height=(self.landscape_height + 2) * self.cell_size,
                fill="#000000",
                fill_opacity=0.0,
                id=f"col_label_{x}_background"
            )
            label_group.append(label_background)
            top_label = self.cell_label(x, -1, str(x))
            label_group.append(top_label)
            bottom_label = self.cell_label(x, self.landscape_height, str(x))
            label_group.append(bottom_label)
            landscape.append(label_group)

        for y in env_data.grid:
            for x in env_data.grid[y]:
                tile = env_data.grid[x][y]
                station_id = None
                if tile.file:
                    use_id = self.get_use_id(tile.file)
                    if tile.station:
                        station_id = self.get_use_id(tile.station)
                else:
                    use_id = "0"


                group_id = f"cell_{x}_{y}_{use_id}"
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

    def save_svg(self, output_filename):
        if isinstance(self.full_svg, SVG):
            static_svg = self.full_svg.to_string()
            static_svg = ET.ElementTree(ET.fromstring(static_svg))
        else:
            static_svg = ET.ElementTree(self.full_svg)
        # add style element
        style_element = ET.Element("style")
        style_element.text = self.style
        static_svg.getroot().insert(0, style_element)
        with open(output_filename, "w") as f:
            f.write(ET.tostring(static_svg.getroot(), encoding='unicode'))

class Animation:
    def __init__(self, landscape: Landscape, train_data: dict, timeframe: int = 0, 
                 env_name: str = ""):
        self.landscape = landscape
        self.train_data = train_data
        self.timeframe = timeframe
        self.env_name = env_name
        self.dynamic_style = get_dynamic_style(num_trains=len(self.train_data), cell_size=self.landscape.cell_size)
        self.control_canvas = build_animation_controls(control_cell_size=self.landscape.cell_size)
        self.train_paths = self.prepare_train_paths()
        self.display_states = {}
        self.place_trains()

    def prepare_train_paths(self):
        """
        Generates a default path element for each train to be populated later.
        Added to self.train_path_group so that it appears behind trains.
        """
        self.train_path_group = G(id="train_paths", class_name="train_paths")
        self.landscape.canvas.append(self.train_path_group)
        train_paths = {}
        for train_id in self.train_data.keys():
            path_element = Path(
                d="",
                id=f"train_{train_id}_path",
                class_name=f"train_{train_id}_path train_path",
                )
            self.train_path_group.append(path_element)
            train_paths[train_id] = path_element
        return train_paths

    def place_trains(self):
        """
        Calls TrainPath to build paths for each train and prepares their respective SVG elements.
        """
        for train_id in self.train_data:
            # build train path
            train_info = self.train_data[train_id]
            train_path_builder = TrainPath(train_id, train_info, self.timeframe, self.landscape.cell_size)
            path_string = train_path_builder.path_string
            self.display_states[train_id] = train_path_builder.get_display_states()
            self.train_paths[train_id].d = path_string

            train_group = make_train_group(train_id, self.landscape.cell_size, scale=240)
            self.landscape.canvas.append(train_group)

    def get_complete_style(self):
        return self.dynamic_style + "\n" + self.landscape.style

    def canvas_string(self):
        return self.landscape.canvas.to_string()

    def control_svg_string(self):
        return self.control_canvas.to_string()

    def build_html(self, milliseconds_per_step=400):
        html_output = get_html()
        html_output = html_output.replace("HEADING", f"Flaspland SVG Animation: {self.env_name}")
        html_output = html_output.replace("STANDARD_STYLE", self.get_complete_style())
        html_output = html_output.replace("INLINE_SVG", self.canvas_string())
        html_output = html_output.replace("CONTROL_SVG", self.control_svg_string())

        html_output = html_output.replace("TRAIN_WIDGETS", get_train_widgets(len(self.train_data)))
        html_output = html_output.replace("TRAIN_DATA", json.dumps(self.display_states, indent=4))
            
        html_output = html_output.replace("TRAIN_DEFS", get_train_definitions(len(self.train_data)))
    
        html_output = html_output.replace("MAX_STEP_PLACEHOLDER", str(self.timeframe))
    
        html_output = html_output.replace("MILLISECONDS_PER_STEP", str(milliseconds_per_step))

        path_step_code, stop_animation_code = get_train_animations(len(self.train_data))
        html_output = html_output.replace("PATH_STEP", path_step_code)
        html_output = html_output.replace("STOP_ANIMATION", stop_animation_code)
    
        slider_offset = self.landscape.get_abs_coord(1.5, grid_offset=False)
        html_output = html_output.replace("SLIDER_OFFSET", str(slider_offset))
    
        return html_output

    def save_svg(self, file_path):
        self.landscape.save_svg(file_path)

    def save_html(self, file_path, milliseconds_per_step=400):
        with open(file_path, "w") as f:
            f.write(self.build_html(milliseconds_per_step=milliseconds_per_step))
        logger.info(f"HTML visualization saved to {file_path}")
