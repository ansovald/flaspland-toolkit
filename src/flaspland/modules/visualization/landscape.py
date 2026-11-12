from __future__ import annotations
import xml.etree.ElementTree as ET
from pydreamplet import SVG, G, Vector, Rect, Text, Path, SvgElement
from .load_templates import load_template
from .svg import SVG_SCALE, clean_svg_group, make_train_group, build_animation_controls, get_signal_svg
from .html import (get_train_definitions, get_train_widgets, get_train_animations,
                   get_signal_definitions, get_signal_animations,
                   get_html, get_dynamic_style)
from .train_paths import TrainPath, SignalList
from .env_data import EnvData, Tile
from pathlib import Path as PathlibPath
import json

import logging
logger = logging.getLogger(__name__)

SVG_STYLE_FN = "svg_styles.css"

class Landscape:
    """
    Class representing the static landscape for the Flatland visualization, either created from an
    EnvData element, or an existing SVG. Handles the creation or parsing of the SVG canvas, 
    scaling, and placement of landscape elements.
    """
    def __init__(self, cell_size=25, landscape_width=None, landscape_height=None, width=None, height=None):
        self.cell_size = cell_size
        self.landscape_width = landscape_width
        self.landscape_height = landscape_height
        self.width = width
        self.height = height

    @classmethod
    def from_env_data(cls, env_data: EnvData, cell_size=25, style=None):
        if style is None:
            style = load_template(SVG_STYLE_FN)
        landscape = cls()
        landscape.sizes_from_env(env_data, cell_size=cell_size)
        landscape.prepare_style(style=style)

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

    def prepare_style(self, style):
        self.style = style
        style_replacements = {
            "LABEL_FONT_SIZE": f"{self.font_size * .8:.2f}px",
            "LABEL_FONT_STROKE": f"{self.cell_size * .02:.2f}px",
            "HOVER_RECT_STROKE_WIDTH": f"{self.cell_size / 20:.2f}px",
            "SIGNAL_STROKE_WIDTH": f"{self.cell_size * .06:.2f}px"
        }
        for key, value in style_replacements.items():
            self.style = self.style.replace(key, value)

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
        """
        Calculate relevant sizes for the visualization based on the cell size and the dimensions of the landscape.
        Other sizes used in the final HTML visualization are calculated based on cell_size in `get_dynamic_sizes()`
        in `..html.load_templates` module.
        """
        self.cell_size = cell_size
        # The size of the landscape grid in term of cells
        self.landscape_width = landscape_width
        self.landscape_height = landscape_height
        # The size of the SVG canvas including margins for displaying coordinates
        self.height = landscape_height + 2
        self.width = landscape_width + 2
        # Font size used for cell labels and other text elements in the SVG
        self.font_size = self.cell_size / 2

    def get_abs_coord(self, coord, grid_offset=True):
        """
        Get the absolute coordinate in the SVG canvas for a given grid coordinate.
        If grid_offset is True, add a margin for grid labels.
        """
        offset = 1 if grid_offset else 0
        return (coord + offset) * self.cell_size
        
    def get_abs_vector(self, x, y, grid_offset=True):
        """
        Get the absolute vector in the SVG canvas for given grid coordinates (x, y).
        If grid_offset is True, add a margin for grid labels.
        """
        offset = 1 if grid_offset else 0
        abs_x = (x + offset) * self.cell_size
        abs_y = (y + offset) * self.cell_size
        return Vector(abs_x, abs_y)

    def get_use_id(self, file_path: PathlibPath, scale=SVG_SCALE) -> str:
        """
        To keep file size small, reuse SVG elements by their IDs instead of duplicating them.
        If the SVG element for the given file path already exists, return its ID.
        Otherwise, create a new group for the element, add it to the defs, and return its ID.
        """
        svg_id = file_path.stem
        if svg_id in self.use_groups:
            return svg_id
        cell_group = clean_svg_group(file_path, svg_id, self.cell_size, scale=scale)
        cell_group.pos = Vector(0,0)
        self.defs.append(cell_group)
        self.use_groups.append(svg_id)
        return svg_id

    def make_tile(self, x, y, tile: Tile):
        use_id = None
        station_id = None
        if tile.file:
            use_id = self.get_use_id(tile.file)
            if tile.station:
                station_id = self.get_use_id(tile.station)

        group_id = f"cell_{x}_{y}_{use_id}"
        cell_group = G(id=group_id, class_name="tile")
        cell_pos = self.get_abs_vector(x, y, grid_offset=True)

        if use_id is not None:
            cell_image = SvgElement("use")
            cell_image.href = f"#{use_id}"
            cell_image.transform = f"translate({cell_pos.x}, {cell_pos.y})"
            cell_group.append(cell_image)
        if station_id:
            station_image = SvgElement("use")
            station_image.href = f"#{station_id}"
            y_offset = 0
            if use_id == "1025":
                # Offset station with horizontal tracks so the building aligns correctly
                y_offset = - self.cell_size / 2
            station_image.transform = f"translate({cell_pos.x}, {cell_pos.y + y_offset})"
            cell_group.append(station_image)

        return cell_group

    def cell_label(self, x, y, text):
        """
        Create a Text object for a cell at grid coordinates (x, y) with the given text.
        """
        label = Text(text, class_name="cell_label_text")
        label.pos = self.get_abs_vector(x + .5, y +.5)
        return label

    def make_cell_label(self, x, y):
        """
        Create a group containing the cell label and an hover rectangle for selection.
        It captures hover events for the cell and has a visible outline.
        """
        label_group = G(id=f"cell_label_{x}_{y}", class_name="cell_label")
        cell_pos = self.get_abs_vector(x, y, grid_offset=True)
        # add invisible rect to capture hover events with stroke to show grid
        hover_rect = Rect(
            pos=cell_pos,
            width=self.cell_size,
            height=self.cell_size,
            id=f"cell_{x}_{y}_hover_rect",
            class_name="hover-rect label-selector"
        )
        label_group.append(hover_rect)
        coord_label = self.cell_label(x, y, f"{x},{y}")
        coord_label.opacity = 0.0
        label_group.append(coord_label)
        return label_group

    def build_landscape(self, env_data: EnvData):
        """
        Build the basic landscape with background and row/column labels.
        """

        # Add background rectangle for the entire landscape
        self.canvas.append(Rect(pos=self.get_abs_vector(0,0), width=self.landscape_width * self.cell_size, height=self.landscape_height * self.cell_size, class_name="background"))

        landscape = G(id="landscape", class_name="landscape")
        self.canvas.append(landscape)
        tile_group = G(id="tiles", class_name="tiles")
        landscape.append(tile_group)
        label_group = G(id="labels", class_name="labels")
        landscape.append(label_group)

        # Iterate over the grid and create SVG elements for each cell. Sampling of tiles already done in `env_data.grid`
        for y in env_data.grid:
            for x in env_data.grid[y]:
                tile_group.append(self.make_tile(x, y, env_data.grid[x][y]))

        # label rows and columns
        row_label_group = G(id="row_labels", class_name="row_labels")
        label_group.append(row_label_group)
        for y in range(self.landscape_height):
            row_group = G(id=f"row_label_{y}", class_name="row_label")
            # add a rect covering the whole row as first child for easier selection
            label_background = Rect(
                pos=self.get_abs_vector(-1, y, grid_offset=True),
                width=(self.landscape_width + 2) * self.cell_size,
                height=self.cell_size,
                id=f"row_label_{y}_background",
                class_name=f"label-selector"
            )
            row_group.append(label_background)
            label_left = self.cell_label(-1, y, str(y))
            row_group.append(label_left)
            label_right = self.cell_label(self.landscape_width, y, str(y))
            row_group.append(label_right)
            row_label_group.append(row_group)

        column_label_group = G(id="column_labels", class_name="column_labels")
        label_group.append(column_label_group)
        for x in range(self.landscape_width):
            column_group = G(id=f"col_label_{x}", class_name="col_label")
            # add a rect covering the whole column as first child for easier selection
            label_background = Rect(
                pos=self.get_abs_vector(x, -1, grid_offset=True),
                width=self.cell_size,
                height=(self.landscape_height + 2) * self.cell_size,
                id=f"col_label_{x}_background",
                class_name="label-selector"
            )
            column_group.append(label_background)
            top_label = self.cell_label(x, -1, str(x))
            column_group.append(top_label)
            bottom_label = self.cell_label(x, self.landscape_height, str(x))
            column_group.append(bottom_label)
            column_label_group.append(column_group)

        # lastly, add cell labels on top of the landscape
        cell_label_group = G(id="cell_labels", class_name="cell_labels")
        label_group.append(cell_label_group)
        for x in range(self.landscape_width):
            for y in range(self.landscape_height):
                cell_label_group.append(self.make_cell_label(x, y))

    def get_canvas_string(self):
        if isinstance(self.canvas, SVG) or isinstance(self.canvas, G):
            return self.canvas.to_string()
        return ET.tostring(self.canvas, encoding='unicode')

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
    """
    Handles the animation and HTML generation, based on a Landscape object and a train data dictionary
    containing all relevant information for visualizing the train trajectories
    """
    def __init__(self, landscape: Landscape, train_data: dict, timeframe: int = 0, 
                 env_name: str = "", log_train_states: bool = False,
                 train_colors: list = None):
        self.landscape = landscape
        self.train_data = train_data
        self.timeframe = timeframe
        self.env_name = env_name
        # generate a css style for the animation, with dynamic styles based on the number of trains and cell size
        self.dynamic_style = get_dynamic_style(num_trains=len(self.train_data), cell_size=self.landscape.cell_size, train_colors=train_colors)
        self.control_canvas = build_animation_controls(control_cell_size=self.landscape.cell_size)
        self.display_states = {}
        self.place_trains(log_states=log_train_states)

    def prepare_train_paths(self):
        """
        Generates a default path element for each train to be populated later.
        Returns a dictionary mapping train IDs to their respective path elements.
        """
        train_path_group = G(id="train_paths", class_name="train_paths")
        self.landscape.canvas.append(train_path_group)
        train_paths = {}
        for train_id in self.train_data.keys():
            path_element = Path(
                d="",
                id=f"train_{train_id}_path",
                class_name=f"train_{train_id}_path train_path",
                )
            train_path_group.append(path_element)
            train_paths[train_id] = path_element
        return train_paths

    def place_trains(self, log_states: bool = False):
        """
        Calls TrainPath to build paths for each train and prepares their respective SVG elements.
        """
        train_group = G(id="trains", class_name="trains")
        self.landscape.canvas.append(train_group)
        train_path_group = G(id="train_paths", class_name="train_paths")
        train_group.append(train_path_group)
        signal_list = SignalList()
        train_paths = []
        for train_id, train_info in self.train_data.items():
            train_path_builder = TrainPath(train_id, train_info, self.timeframe, self.landscape.cell_size, log_states=log_states)
            
            path_element = Path(
                d=train_path_builder.get_path_string(),
                id=f"train_{train_id}_path",
                class_name=f"train_{train_id}_path train_path",
            )
            train_path_group.append(path_element)

            self.display_states[train_id] = train_path_builder.get_display_states()

            train_group.append(make_train_group(train_id, self.landscape.cell_size, scale=SVG_SCALE))

            train_signal_list = train_path_builder.get_signal_list()
            signal_list.extend(train_signal_list)
            train_paths.append(train_path_builder)
        signal_list.update_states(train_paths)
        self.signal_states = signal_list.get_display_states(timeframe=self.timeframe)
        self.signal_list = signal_list
        self.place_signals()

    def place_signals(self, signal_list: SignalList = None):
        """
        Places the signals on the landscape based on the provided signal list.
        """
        if signal_list is None:
            signal_list = self.signal_list
        signal_group = G(id="signals", class_name="signals")
        self.landscape.canvas.append(signal_group)
        for i, signal in enumerate(signal_list):
            signal_inst = get_signal_svg(i, signal.display_rotation)
            # adjust the signal position to the center of the cell
            x = self.landscape.get_abs_coord(signal.coords.x + .5 + signal.offset.x)
            y = self.landscape.get_abs_coord(signal.coords.y + .5 + signal.offset.y)
            signal_inst.set_attr("transform", f"translate({x},{y})")

            signal_group.append(signal_inst)

    def get_style_string(self):
        return self.dynamic_style + "\n" + self.landscape.style

    def get_canvas_string(self):
        return self.landscape.get_canvas_string()

    def get_control_svg_string(self):
        return self.control_canvas.to_string()

    def build_html(self, milliseconds_per_step=400):
        """
        Builds the complete HTML for the visualization, including the SVG canvas, control elements, 
        and train animations.
        """
        html_output = get_html()
        html_output = html_output.replace("TIMEFRAME", str(self.timeframe))
        html_output = html_output.replace("HEADING", f"Flaspland SVG Animation: {self.env_name}")
        html_output = html_output.replace("STANDARD_STYLE", self.get_style_string())
        html_output = html_output.replace("INLINE_SVG", self.get_canvas_string())
        html_output = html_output.replace("CONTROL_SVG", self.get_control_svg_string())

        html_output = html_output.replace("TRAIN_WIDGETS", get_train_widgets(self.train_data))
        html_output = html_output.replace("TRAIN_DATA", json.dumps(self.display_states, indent=4))
        html_output = html_output.replace("SIGNAL_DATA", json.dumps(self.signal_states, indent=4))
            
        html_output = html_output.replace("TRAIN_DEFS", get_train_definitions(len(self.train_data)))
        html_output = html_output.replace("SIGNAL_DEFS", get_signal_definitions(len(self.signal_list)))
    
        html_output = html_output.replace("MAX_STEP_PLACEHOLDER", str(self.timeframe))
    
        html_output = html_output.replace("MILLISECONDS_PER_STEP", str(milliseconds_per_step))

        path_step_code, stop_animation_code = get_train_animations(len(self.train_data))
        path_step_code += get_signal_animations(len(self.signal_list))
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
