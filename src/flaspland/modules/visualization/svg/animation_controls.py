from pydreamplet import SVG, Rect, Path, Vector, G, Circle, Text
import xml.etree.ElementTree as ET

play_button = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" class="fill-button">
  <rect x="2" y="2" rx="2" ry="2" width="20" height="20"/>
  <path fill-rule="evenodd" d="M8.6 5.2A1 1 0 0 0 7 6v12a1 1 0 0 0 1.6.8l8-6a1 1 0 0 0 0-1.6l-8-6Z" clip-rule="evenodd"/>
</svg>"""

pause_button = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" class="fill-button">
  <rect x="2" y="2" rx="2" ry="2" width="20" height="20"/>
  <path fill-rule="evenodd" d="M8 5a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2H8Zm7 0a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-1Z" clip-rule="evenodd"/>
</svg>"""
forward_button = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" class="fill-button">
  <rect x="2" y="2" rx="2" ry="2" width="20" height="20"/>
  <path fill-rule="evenodd" d="M17 6a1 1 0 1 0-2 0v4L8.6 5.2A1 1 0 0 0 7 6v12a1 1 0 0 0 1.6.8L15 14v4a1 1 0 1 0 2 0V6Z" clip-rule="evenodd"/>
</svg>"""
backward_button = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24" class="fill-button">
  <rect x="2" y="2" rx="2" ry="2" width="20" height="20"/>
  <path fill-rule="evenodd" d="M7 6a1 1 0 0 1 2 0v4l6.4-4.8A1 1 0 0 1 17 6v12a1 1 0 0 1-1.6.8L9 14v4a1 1 0 1 1-2 0V6Z" clip-rule="evenodd"/>
</svg>"""
first_button = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" class="stroke-button">
  <rect x="2" y="2" rx="2" ry="2" width="20" height="20"/>
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m17 16-4-4 4-4m-6 8-4-4 4-4"/>
</svg>"""
last_button = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" class="stroke-button">
  <rect x="2" y="2" rx="2" ry="2" width="20" height="20"/>
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m7 16 4-4-4-4m6 8 4-4-4-4"/>
</svg>"""

def build_button(svg_string: str, transform: Vector, id: str, class_name: str) -> G:
    button_svg = ET.fromstring(svg_string)
    button_group = G(id=id, class_name=class_name)
    button_group.append(button_svg)
    button_group.scale = transform
    return button_group

def build_buttons(cell_size: int = 24) -> G:
    control_group = G(id="control_buttons", class_name="control buttons")
    transform_vector = Vector(cell_size / 24, cell_size / 24)
    for button in ["first_button", "backward_button", "pause_button", "play_button", "forward_button", "last_button"]:
        svg_string = globals()[button]
        button_id = button
        class_name = button.replace("_", " ")
        button_group = build_button(svg_string, transform_vector, button_id, class_name)
        index = ["first_button", "backward_button", "pause_button", "play_button", "forward_button", "last_button"].index(button)
        button_group.pos = Vector(cell_size * index, 0)
        control_group.append(button_group)
    return control_group

def build_animation_controls(control_cell_size, control_width=1000):
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