"""
Generate Flatland environments and export them for clingo (.lp), as an image
(.png) and as a pickle (.pkl), into envs/ in the current folder.

Parameters are read from config.toml in the current folder if there is one
(`flaspland init` creates it). Point --config at another file, or override any
single value with a command-line flag. Precedence: flag > config file > built-in.

Examples
--------
    flaspland build                        # 1 env, settings from build_config.toml
    flaspland build 10 --agents 5 --cities 3 --seed 42
    flaspland build 5 --config configs/hard.toml --malfunction-rate 0.01
"""

from __future__ import annotations

import argparse
import itertools
import math
import sys
import tomllib
import warnings
from pathlib import Path

# custom modules
from .modules.dirs import create_dirs, find_start
from .modules.save import save_lp, save_png, save_pkl, save_svg
from .modules.convert import convert_to_clingo

# Flatland modules
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import sparse_rail_generator
from flatland.envs.line_generators import sparse_line_generator
from flatland.envs.observations import GlobalObsForRailEnv
from flatland.envs.malfunction_generators import MalfunctionParameters, ParamMalfunctionGen

import logging
logger = logging.getLogger(__name__)


# used when --config is not given and the file exists in the current folder
DEFAULT_CONFIG = Path("build_config.toml")

DEFAULTS = {
    "width": 30,
    "height": 30,
    "number_of_agents": 2,
    "max_num_cities": 2,
    "line_length": None,  # None = don't pass it; use Flatland's own default
    "seed": None,  # None = fresh random environments every run
    "grid_mode": False,
    "max_rails_between_cities": 2,
    "max_rail_pairs_in_city": 2,
    "remove_agents_at_target": True,
    "speed_ratio_map": {1.0: 1.0},
    "malfunction_rate": 0.0,
    "min_duration": 20,
    "max_duration": 50,
}


# ---------------------------------------------------------------------------
# argument types
# ---------------------------------------------------------------------------

def positive_int(text: str) -> int:
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError(f"must be >= 1, got {value}")
    return value


def non_negative_int(text: str) -> int:
    value = int(text)
    if value < 0:
        raise argparse.ArgumentTypeError(f"must be >= 0, got {value}")
    return value


def probability(text: str) -> float:
    value = float(text)
    if not 0.0 <= value <= 1.0:
        raise argparse.ArgumentTypeError(f"must be between 0 and 1, got {value}")
    return value


def speed_ratio_map(text: str) -> dict[float, float]:
    """Parse 'speed:ratio,speed:ratio', e.g. '1.0:0.5,0.5:0.5'."""
    result: dict[float, float] = {}
    try:
        for pair in text.split(","):
            speed, ratio = pair.split(":")
            result[float(speed)] = float(ratio)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"expected 'speed:ratio,speed:ratio' (e.g. '1.0:0.5,0.5:0.5'), got {text!r}"
        )
    return result


# ---------------------------------------------------------------------------
# config file + CLI
# ---------------------------------------------------------------------------

CONFIG_TYPES = {
    "width": int, "height": int, "number_of_agents": int, "max_num_cities": int,
    "line_length": int, "seed": int, "grid_mode": bool, "max_rails_between_cities": int,
    "max_rail_pairs_in_city": int, "remove_agents_at_target": bool,
    "speed_ratio_map": dict, "malfunction_rate": float,
    "min_duration": int, "max_duration": int,
}


def load_config(parser: argparse.ArgumentParser, path: Path) -> dict:
    """Read a TOML config file, check its types and normalise it."""
    try:
        with path.open("rb") as f:
            config = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        parser.error(f"{path} is not valid TOML: {exc}")

    unknown = set(config) - set(CONFIG_TYPES)
    if unknown:
        parser.error(f"unknown key(s) in {path}: {', '.join(sorted(unknown))}")

    for key, value in config.items():
        expected = CONFIG_TYPES[key]
        ok = isinstance(value, expected) and not (expected is int and isinstance(value, bool))
        if expected is float and isinstance(value, int) and not isinstance(value, bool):
            ok, config[key] = True, float(value)  # allow `malfunction_rate = 0`
        if not ok:
            parser.error(f"{path}: '{key}' should be {expected.__name__}, "
                         f"got {type(value).__name__} ({value!r})")

    # TOML keys are always strings, so convert {"1.0" = 0.5} -> {1.0: 0.5}
    if "speed_ratio_map" in config:
        try:
            config["speed_ratio_map"] = {float(k): float(v) for k, v in config["speed_ratio_map"].items()}
        except (TypeError, ValueError):
            parser.error(f"{path}: speed_ratio_map entries must look like \"1.0\" = 0.5")

    return config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flaspland build",
        description="Generate Flatland environments and export them for clingo. "
                    "They are saved to envs/ in the current folder.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("num_envs", type=positive_int, nargs="?", default=1,
                        help="number of environments to create")
    parser.add_argument("-c", "--config", type=Path, metavar="FILE", default=None,
                        help="TOML file with the generation parameters (flags override it); "
                             "default: build_config.toml in the current folder, if it exists")

    grid = parser.add_argument_group("grid")
    grid.add_argument("--width", type=positive_int, metavar="N", help="grid width in cells")
    grid.add_argument("--height", type=positive_int, metavar="N", help="grid height in cells")
    grid.add_argument("--cities", dest="max_num_cities", type=positive_int, metavar="N",
                      help="maximum number of cities")
    grid.add_argument("--grid-mode", action=argparse.BooleanOptionalAction,
                      help="place cities on a regular grid instead of randomly")
    grid.add_argument("--rails-between-cities", dest="max_rails_between_cities", type=positive_int,
                      metavar="N", help="maximum rails connecting two cities")
    grid.add_argument("--rail-pairs-in-city", dest="max_rail_pairs_in_city", type=positive_int,
                      metavar="N", help="maximum parallel track pairs inside a city")

    trains = parser.add_argument_group("trains")
    trains.add_argument("-a", "--agents", dest="number_of_agents", type=positive_int, metavar="N",
                        help="number of trains")
    trains.add_argument("-l", "--line-length", type=positive_int, metavar="N",
                        help="cities each train visits, counting start and end "
                             "(2 = start/end only, 3 = one intermediate stop). "
                             "Omit to use Flatland's default")
    trains.add_argument("--speed-ratio-map", type=speed_ratio_map, metavar="MAP",
                        help="speed:ratio pairs, e.g. '1.0:0.5,0.5:0.5' (ratios must sum to 1)")
    trains.add_argument("--remove-agents-at-target", action=argparse.BooleanOptionalAction,
                        help="remove trains from the grid once they arrive")

    malf = parser.add_argument_group("malfunctions")
    malf.add_argument("--malfunction-rate", type=probability, metavar="P",
                      help="malfunction rate per train and step (0 disables malfunctions)")
    malf.add_argument("--min-duration", type=non_negative_int, metavar="N",
                      help="shortest malfunction in steps")
    malf.add_argument("--max-duration", type=non_negative_int, metavar="N",
                      help="longest malfunction in steps")

    parser.add_argument("-s", "--seed", type=int, metavar="N",
                        help="first seed; every attempt (including retries) uses the next one, "
                             "so a run is fully reproducible. Omit for random environments")

    parser.set_defaults(**DEFAULTS)
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = build_parser()

    # First pass only looks for --config, so its values can become the defaults
    # before the real parse. Explicit flags still win.
    pre, _ = parser.parse_known_args(argv)
    config = pre.config
    if config is None and DEFAULT_CONFIG.is_file():
        config = DEFAULT_CONFIG
    if config is None:
        logger.info("no build_config.toml in this folder, using built-in defaults")
    elif config.is_file():
        logger.info(f"note: using settings from {config}")
        parser.set_defaults(**load_config(parser, config))
    else:
        parser.error(f"config file not found: {config}")

    args = parser.parse_args(argv)
    validate(parser, args)
    return args


def validate(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    """Range checks (values from the config file skip argparse's type checks)
    and checks that involve more than one parameter."""
    for name in ("width", "height", "number_of_agents",
                 "max_rails_between_cities", "max_rail_pairs_in_city"):
        if getattr(args, name) < 1:
            parser.error(f"{name} must be at least 1, got {getattr(args, name)}")
    for name in ("min_duration", "max_duration"):
        if getattr(args, name) < 0:
            parser.error(f"{name} must not be negative, got {getattr(args, name)}")
    if args.line_length is not None:
        if args.line_length < 2:
            parser.error(f"line_length counts start and end, so it must be at least 2, "
                         f"got {args.line_length}")
        if args.line_length > args.max_num_cities:
            parser.error(f"line_length ({args.line_length}) needs at least that many cities, "
                         f"but --cities is {args.max_num_cities}")
    if not 0.0 <= args.malfunction_rate <= 1.0:
        parser.error(f"malfunction_rate must be between 0 and 1, got {args.malfunction_rate}")
    if args.max_num_cities < 2:
        parser.error("--cities must be at least 2 (trains need somewhere to go)")
    if args.min_duration > args.max_duration:
        parser.error(f"--min-duration ({args.min_duration}) is greater than "
                     f"--max-duration ({args.max_duration})")
    if not math.isclose(sum(args.speed_ratio_map.values()), 1.0):
        parser.error(f"speed ratios must sum to 1, got {sum(args.speed_ratio_map.values())}")


# ---------------------------------------------------------------------------
# environment generation
# ---------------------------------------------------------------------------

def make_env(args: argparse.Namespace) -> RailEnv:
    rail_generator = sparse_rail_generator(
        max_num_cities=args.max_num_cities,
        grid_mode=args.grid_mode,
        max_rails_between_cities=args.max_rails_between_cities,
        max_rail_pairs_in_city=args.max_rail_pairs_in_city,
    )
    # Only pass line_length when it's set, so leaving it out behaves exactly
    # as before (and still works on Flatland versions without the parameter).
    line_kwargs = {} if args.line_length is None else {"line_length": args.line_length}

    malfunctions = MalfunctionParameters(
        malfunction_rate=args.malfunction_rate,
        min_duration=args.min_duration,
        max_duration=args.max_duration,
    )
    return RailEnv(
        width=args.width,
        height=args.height,
        rail_generator=rail_generator,
        line_generator=sparse_line_generator(args.speed_ratio_map, **line_kwargs),
        number_of_agents=args.number_of_agents,
        obs_builder_object=GlobalObsForRailEnv(),
        malfunction_generator=ParamMalfunctionGen(malfunctions),
        remove_agents_at_target=args.remove_agents_at_target,
    )


MAX_ATTEMPTS = 10


def generate_valid_env(args: argparse.Namespace, seeds) -> tuple[RailEnv, int | None]:
    """Build environments until every train has the full number of waypoints.

    When Flatland can't find a path through all `line_length` cities for a
    train, it silently cuts that train's line short. Flatland's timetable
    generator then takes the number of stops from train 0 alone and applies it
    to every train, so the timetables come out wrong: too short for the trains
    that kept all their stops, or an IndexError if train 0 is the full one.
    Neither is usable, so such environments are thrown away and regenerated.
    """
    expected = args.line_length or 2
    problem = ""
    for _ in range(MAX_ATTEMPTS):
        seed = next(seeds)
        try:
            env = make_env(args)
            with warnings.catch_warnings():
                # reported below in a clearer form
                warnings.filterwarnings("ignore", message="Could not find path connecting")
                env.reset(random_seed=seed)
        except Exception as exc:
            problem = f"{type(exc).__name__}: {exc}"
        else:
            short = [a.handle for a in env.agents if len(a.waypoints) != expected]
            if not short:
                return env, seed
            problem = f"no path through all {expected} cities for train(s) {short}"
        logger.info(f"seed={seed}: {problem}; retrying")
    raise RuntimeError(f"no valid environment after {MAX_ATTEMPTS} attempts (last: {problem})")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    path = create_dirs()
    start_index = find_start(path)
    failures = 0
    seeds = itertools.repeat(None) if args.seed is None else itertools.count(args.seed)

    for i in range(start_index, start_index + args.num_envs):
        file_name = f"env_{i:03d}--{args.number_of_agents}_{args.max_num_cities}"
        seed = None

        try:
            env, seed = generate_valid_env(args, seeds)

            save_lp(convert_to_clingo(env), file_name, path)
            save_png(env, file_name, path)
            save_pkl(env, file_name, path)
            save_svg(env, file_name, path)
        except Exception as exc:  # keep going so one bad env doesn't kill a batch
            failures += 1
            logger.error(f"[{file_name}] failed (seed={seed}): {exc}")
            continue

        logger.info(f"[{file_name}] saved (seed={seed})")

    if failures:
        logger.info(f"{failures} of {args.num_envs} environment(s) failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())