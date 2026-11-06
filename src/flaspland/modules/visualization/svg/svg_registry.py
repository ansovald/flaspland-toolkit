"""

Generate svg lists, built after `.../utils/graphics_pil.py` from flatlands-rl

"""

from pathlib import Path

SVG_DIR = Path(__file__).parent

BUILDING_FILES = [
    "Buildings-Bank.png",
    "Buildings-Bar.png",
    "Buildings-Wohnhaus.png",
    "Buildings-Hochhaus.png",
    "Buildings-Hotel.png",
    "Buildings-Office.png",
    "Buildings-Polizei.png",
    "Buildings-Post.png",
    "Buildings-Supermarkt.png",
    "Buildings-Tankstelle.png",
    "Buildings-Fabrik_A.png",
    "Buildings-Fabrik_B.png",
    "Buildings-Fabrik_C.png",
    "Buildings-Fabrik_D.png",
    "Buildings-Fabrik_E.png",
    "Buildings-Fabrik_F.png",
    "Buildings-Fabrik_G.png",
    "Buildings-Fabrik_H.png",
    "Buildings-Fabrik_I.png"
]

SCENERY_FILES = [
    "Scenery-Laubbaume_A.png",
    "Scenery-Laubbaume_B.png",
    "Scenery-Laubbaume_C.png",
    "Scenery-Nadelbaume_A.png",
    "Scenery-Nadelbaume_B.png",
    "Scenery-Bergwelt_B.png"
]

SCENERY_FILES_D2 = [
    "Scenery-Bergwelt_C_Teil_1_links.png",
    "Scenery-Bergwelt_C_Teil_2_rechts.png"
]

SCENERY_FILES_D3 = [
    "Scenery-Bergwelt_A_Teil_1_links.png",
    "Scenery-Bergwelt_A_Teil_2_mitte.png",
    "Scenery-Bergwelt_A_Teil_3_rechts.png"
]

SCENERY_FILES_WATER = [
    "Scenery_Water.png"
]

STATION_FILES = [
    # renamed, since the original files contain `#`, which can lead to reference problems in XML
    "Station.svg"
]

REGISTRY_STRUCTURE = {
    "buildings": ("buildings", BUILDING_FILES),
    "scenery": ("scenery", SCENERY_FILES),
    "scenery_d2": ("scenery", SCENERY_FILES_D2),
    "scenery_d3": ("scenery", SCENERY_FILES_D3),
    "scenery_water": ("scenery", SCENERY_FILES_WATER),
    "station": ("station", STATION_FILES)
}

def get_svg_registry(registry_structure=REGISTRY_STRUCTURE):
    registry = {}
    for type in registry_structure:
        registry[type] = []
        dir, files = registry_structure[type]
        for file in files:
            file = file.lower()
            file = file.replace(".png", ".svg")
            file = SVG_DIR / dir / file
            registry[type].append(file)
    return registry

TRACKS_FILES = {}
TRACKS_DIR = Path("tracks")
for track_file in (Path(__file__).parent / "tracks" ).glob("*.svg"):
    num = int(track_file.stem)
    TRACKS_FILES[num] = track_file

def get_track_file(num):
    return TRACKS_FILES.get(num)