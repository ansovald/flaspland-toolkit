"""
The `flaspland` command: dispatches to `flaspland init`, `flaspland build` and `flaspland solve`.
"""

import shutil
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path

from . import __version__

import logging

LOGGING_CONFIG_FN = "logging_config.toml"
LOGGING_CONFIG = Path(LOGGING_CONFIG_FN)
# Load logging configuration from the TOML file if it exists
if not LOGGING_CONFIG.is_file():
    # copy the default logging configuration from the template
    shutil.copyfile(Path(__file__).resolve().parent / LOGGING_CONFIG_FN, LOGGING_CONFIG)
import tomllib
try:
    with LOGGING_CONFIG.open("rb") as f:
        config = tomllib.load(f)
        LOG_LEVEL = getattr(logging, config.get("log_level", "INFO").upper(), logging.INFO)
        LOG_DIR = Path(config.get("log_directory", "logs"))
        LOG_DIR.mkdir(exist_ok=True)
        LOG_FILE = LOG_DIR / config.get("log_file", "flaspland.log")
        HANDLERS = config.get("handlers", ["console", "file"])
        FILEMODE = config.get("filemode", "w")
        FORMAT = config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
except Exception as e:
    print(f"Failed to load logging configuration from {LOGGING_CONFIG}, using default valus:\n{e}")
    LOG_LEVEL = logging.INFO
    LOG_DIR = Path("logs")
    LOG_DIR.mkdir(exist_ok=True)
    LOG_FILE = LOG_DIR / "flaspland.log"
    FILEMODE = "w"
    HANDLERS = ["console", "file"]
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

handlers = []
if "console" in HANDLERS:
    handlers.append(logging.StreamHandler())
if "file" in HANDLERS:
    handlers.append(logging.FileHandler(LOG_FILE, encoding="utf-8", mode=FILEMODE))

logging.basicConfig(
    level=LOG_LEVEL,
    format=FORMAT,
    handlers=handlers
)
logger = logging.getLogger(__name__)

COMMANDS = {
    "init": "create cconfig and template files with 'flaspland build'",
    "build": "generate Flatland environments into envs/",
    "solve": "solve an environment with your encodings and simulate the plan",
}

BUILD_CONFIG_FN = "build_config.toml"
SOLVE_CONFIG_FN = "solve_config.toml"

BUILD_CONFIG_TEMPLATE = Path(__file__).resolve().parent / BUILD_CONFIG_FN

SOLVE_CONFIG_TEMPLATE = Path(__file__).resolve().parent / SOLVE_CONFIG_FN
VIS_TEMPLATES_DIRECTORY = Path(__file__).resolve().parent / "modules" / "visualization" / "templates"


def init(argv) -> int:
    """ 
    copy the default build_config.toml, visualization.toml, 
    and visualization templates into the current folder
    """
    parser = ArgumentParser(prog="flaspland init", description=COMMANDS["init"].capitalize() + ".")
    parser.add_argument("--force", action="store_true", help="overwrite existing config and template files")
    args = parser.parse_args(argv)

    targets = [
        Path(BUILD_CONFIG_FN),
        Path(SOLVE_CONFIG_FN),
        Path(LOGGING_CONFIG_FN),
        Path("templates")
    ]
    for target in targets:
        if target.exists() and not args.force:
            logger.warning(f"{target} already exists; use --force to overwrite it")

    shutil.copyfile(BUILD_CONFIG_TEMPLATE, Path(BUILD_CONFIG_FN))
    shutil.copyfile(SOLVE_CONFIG_TEMPLATE, Path(SOLVE_CONFIG_FN))
    shutil.copyfile(LOGGING_CONFIG, Path(LOGGING_CONFIG_FN))
    if not Path("templates").exists():
        shutil.copytree(VIS_TEMPLATES_DIRECTORY, Path("templates"))
    logger.info("Initialized project folder. Edit `build_config.toml` and run build. `solve_config.toml` and `templates` control solving & visualization, 'logging_config.toml' controls logging.")
    return 0


def main(argv=None) -> int:
    """ run the flaspland command line interface """
    argv = sys.argv[1:] if argv is None else list(argv)

    # the commands are imported only when used, as loading Flatland takes a moment
    if argv and argv[0] == "init":
        return init(argv[1:])
    if argv and argv[0] == "build":
        from . import build  # pylint: disable=import-outside-toplevel
        return build.main(argv[1:])
    if argv and argv[0] == "solve":
        from . import solve  # pylint: disable=import-outside-toplevel
        return solve.main(argv[1:])

    commands = "\n".join(f"  {name:8}{text}" for name, text in COMMANDS.items())
    parser = ArgumentParser(
        prog="flaspland",
        description="Generate Flatland environments and solve them with clingo.",
        epilog=f"commands:\n{commands}\n\nRun 'flaspland <command> -h' for the options of a command.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("command", choices=COMMANDS, metavar="command", help="one of: " + ", ".join(COMMANDS))
    if not argv:
        parser.print_help()
        return 1
    parser.parse_args(argv)  # prints the help, the version or an error and exits
    return 1
