"""

Functionality to unify the style elements of the flatland-rl SVG files.
Not used during runtime, only for preprocessing SVG files to unify their styles.

"""


from pathlib import Path
import re
import json
import xml.etree.ElementTree as ET

CSS_PATH = Path(__file__).parent / "svg_styles.css"

ORIG_SVG_PATH = Path("~/repositories/flatland/pr-venv/lib/python3.12/site-packages/flatland/svg").expanduser()

SVG_TYPES = {
    "Buildings": "Buildings*.svg",
    "Scenery": "Scenery*.svg",
    "Station": "Bahnhof*.svg"
}

REPLACEMENTS = {
    "display:none": "fill:none",
    "display:inline": ""
}

def parse_css_file(css_path=CSS_PATH):
    css_content = css_path.read_text().replace("\n", "").replace(" ", "")

    # remove comments from the CSS content
    css_content = re.sub(r"/\*.*?\*/", "", css_content)

    # remove placeholders from the CSS content
    placeholder_pattern = re.compile(r"\{\{(.*?)\}\}")
    css_content = placeholder_pattern.sub("", css_content)

    styles = css_content.split("}")

    style_dict = {}
    prop_dict = {}

    for style in styles:
        if "{" in style:
            selector, properties = style.split("{", 1)
            selector = selector.lstrip(".")
            style_dict[selector] = properties
            prop_dict[properties] = selector

    return style_dict, prop_dict

def find_svgs(pattern, svg_path=ORIG_SVG_PATH):
    return list(svg_path.glob(pattern))

def map_styles(svg_dict: dict, style_dict: dict, rule_dict: dict):
    # new_styles = {}
    # new_rule_dict = {}
    new_css = ""
    for type, svg_files in svg_dict.items():
        style_counter = 0
        type_dir = Path(__file__).parent / type.lower()
        type_dir.mkdir(parents=True, exist_ok=True)
        print(f"Processing SVG type: {type}, output directory: {type_dir}")
        for svg_file in svg_files:
            style_mapping = {}
            name = svg_file.name.lower()
            print()
            print(name)
            print("=" * len(name))
            tree = ET.parse(svg_file)
            root = tree.getroot()
            custom_css = ""
            for elem in root.iter():
                if elem.tag.endswith("style"):
                    elem_styles = elem.text.strip().replace("\n", "").replace(" ", "").split("}")
                    for elem_style in elem_styles:
                        if not elem_style:
                            continue
                        style_name = elem_style.split("{", 1)[0].strip().lstrip(".")
                        style_value = elem_style.split("{", 1)[1].lower() if "{" in elem_style else ""
                        for replace_from, replace_to in REPLACEMENTS.items():
                            style_value = style_value.replace(replace_from, replace_to).lstrip(';')
                        if style_value in rule_dict:
                            standard_style = rule_dict[style_value]
                            style_mapping[style_name] = standard_style
                            custom_css += f".{standard_style}{{{style_value}}}"
                            # print(f"Mapping style {style_name} to {standard_style}")
                        else:
                            new_style_name = f"{type.lower()}-{style_counter}"
                            style_counter += 1
                            style_dict[new_style_name] = style_value
                            rule_dict[style_value] = new_style_name
                            style_mapping[style_name] = new_style_name
                            css_snippet = f".{new_style_name}{{{style_value}}}"
                            new_css += css_snippet + "\n"
                            custom_css += css_snippet
                            # print(f"Creating new style {new_style_name} for value {style_value}")
                        if style_mapping:
                            elem.text = custom_css

            for elem in root.iter():
                if 'class' in elem.attrib:
                    class_name = elem.attrib['class']
                    if class_name in style_mapping:
                        elem.attrib['class'] = style_mapping[class_name]
                    else:
                        print(f"Class {class_name} not found in style mapping")
            output_path = type_dir / svg_file.name.lower()
            tree.write(output_path)
            print(f"Written updated SVG to {output_path}")
    return new_css


if __name__ == "__main__":
    style_dict, rule_dict = parse_css_file()

    svg_collection = {}

    for svg_type, pattern in SVG_TYPES.items():
        svg_files = find_svgs(pattern=pattern)
        svg_collection[svg_type] = svg_files

    new_css = map_styles(svg_collection, style_dict, rule_dict)

    if new_css:
        with open(CSS_PATH, "a") as f:
            f.write(new_css)
