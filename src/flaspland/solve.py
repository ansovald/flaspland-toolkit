"""
Solve a Flatland environment with ASP encodings and simulate the plan.

Run as `flaspland solve ENV ENCODING [ENCODING ...]`; see `flaspland solve -h`.
"""

# standard packages
import sys
import time
import pickle
import logging
import tomllib

# import tempfile
from argparse import ArgumentParser, Namespace
from pathlib import Path
from tqdm import tqdm

# custom modules
from .modules.api import FlatlandPlan
from .modules.convert import convert_malfunctions_to_clingo, convert_formers_to_clingo, convert_futures_to_clingo
from .modules.render import GifRenderer, HtmlRenderer
from .modules.defs import DIR_MAP, ACTION_MAP, STATE_MAP

# clingo
from clingo.application import clingo_main

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_FILE = Path("solve_config.toml")

DEFAULT_CONFIG = {
    "save_model": True,
    "save_stats": True,
    "save_encodings": True,
    "encodings": None,
    "renderers": ["html"],
    "ms_per_step": 300,
    "cell_size": 25,
    "log_train_states": False,
    "train_colors": ["#d50000", "#2979ff", "#ff6f00", "#fdd835", "#00c853", "#aa00ff", "#00bfa5", "#c51162", "#64dd17", "#304ffe", "#ffd600", "#00b8d4", "#9e9e9e", "#ff1744", "#00e676", "#6200ea", "#2962ff", "#aeea00", "#f50057", "#00b0ff"]
}

class MalfunctionManager():
    def __init__(self, num_agents):
        self.num_agents = num_agents
        self.malfunctions = []

    def get(self) -> list:
        """ get the list of malfunctions """
        return(self.malfunctions)

    def deduct(self) -> None:
        """ decrease the duration of each malfunction by one and delete expired malfunctions """
        malfunctions_to_remove = []
        for i, malf in enumerate(self.malfunctions):
            self.malfunctions[i] = (self.malfunctions[i][0], self.malfunctions[i][1] - 1)
            if self.malfunctions[i][1] == 0:
                malfunctions_to_remove.append(i)
        
        # delete expired malfunctions
        for i in sorted(malfunctions_to_remove, reverse=True):
            del self.malfunctions[i]

    def check(self, info) -> set:
        """ check current state of the env for new malfunctions """
        malfunctioning_info = info['malfunction']
        malfunctioning_trains = {train for train, duration in malfunctioning_info.items() if duration > 0}
        existing = {malf[0] for malf in self.malfunctions}
        new = malfunctioning_trains.difference(existing)

        # add new ones to malfunctions
        for train in new:
            self.malfunctions.append((train, malfunctioning_info[train]))

        return(new)


def check_plan(action_list, when) -> list:
    """ stop with a clear message if clingo did not produce a plan """
    if action_list is None:
        raise SystemExit(f"No plan found {when}: see the clingo output above (e.g. UNSATISFIABLE, or an error in an encoding).")
    return(action_list)


class SimulationManager():
    def __init__(self, env, env_name, encodings, clingo_args=()):
        self.env = env
        self.encodings = encodings
        self.clingo_args = list(clingo_args)
        self.stats = {
            "env_name": env_name,
            "num_agents": self.env.get_num_agents(),
            "encodings": self.encodings
        }

    def build_actions(self) -> list:
        """ create initial list of actions """
        # pass env, encodings
        app = FlatlandPlan(self.env, None)
        clingo_main(app, self.encodings + self.clingo_args)
        self.stats.update(app.stats)
        self.model = app.model
        return(check_plan(app.action_list, "for the initial plan"))

    def provide_context(self, actions, timestep, malfunctions) -> str:
        """ provide additional facts when updating list """
        # actions that have already been executed
        # wait actions that are enforced because of malfunctions
        # future actions that were previously planned
        past = convert_formers_to_clingo(actions[:timestep])
        present = convert_malfunctions_to_clingo(malfunctions, timestep)
        future = convert_futures_to_clingo(actions[timestep:])
        return(past + present + future)

    def update_actions(self, context) -> list:
        """ update list of actions following malfunction """
        # pass env, encodings, context
        app = FlatlandPlan(self.env, context)
        clingo_main(app, self.encodings + self.clingo_args)
        self.stats.update(app.stats)
        self.model = app.model
        return(check_plan(app.action_list, "while replanning after a malfunction"))

    def save_model(self, output_dir) -> None:
        """ save the model to the local drive """
        with (Path(output_dir) / "model.lp").open("w") as f:
            for symbol in self.model:
                f.write(str(symbol) + "\n")
        logger.info(f"Model saved to {Path(output_dir) / 'model.lp'}")

    def save_stats(self, output_dir) -> None:
        """ save the stats to the local drive """
        import json
        with (Path(output_dir) / "clingo_stats.json").open("w") as f:
            json.dump(self.stats, f, indent=4)
        logger.info(f"Clingo stats saved to {Path(output_dir) / 'stats.json'}")

    def save_encodings(self, output_dir) -> None:
        """
        copy the encodings used to the output directory.
        Useful when you want to track performance of different versions of your encodings.
        """
        from shutil import copy
        for encoding in self.encodings:
            copy(encoding, Path(output_dir) / Path(encoding).name)
        logger.info(f"Encodings saved to {Path(output_dir)}")


class OutputLogManager():
    def __init__(self) -> None:
        self.logs = []

    def add(self,info) -> None:
        """ add info from a timestep to the log """
        self.logs.append(info)

    def save(self, directory: str | Path) -> None:
        """ save output log to local drive """
        with (Path(directory) / "paths.csv").open("w") as f:
            f.write("agent;timestep;position;direction;status;given_command\n")
            for log in self.logs:
                f.write(log)
        logger.info(f"Paths saved to {Path(directory) / 'paths.csv'}")


def get_position_and_direction(agent) -> tuple:
    """ get an agent's position and direction; position is None while the agent is off the map """
    if agent.current_configuration is not None:
        return(agent.current_configuration)
    # off the map: use the arrival direction if done, otherwise the starting direction
    if agent.target_configuration is not None:
        return(None, agent.target_configuration[1])
    return(None, agent.initial_configuration[1])

def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog='flaspland solve',
        description='Solve a Flatland environment with your encodings and simulate the plan. '
                    'Results are saved to output/<date>_<time>/ in the current folder.',
        epilog="Options after '--' are passed on to clingo, e.g. 'flaspland solve env.pkl main.lp -- -t 4'.")
    parser.add_argument('env', type=str, help='the Flatland environment, a .pkl file created by flaspland build')
    parser.add_argument("-c", "--config", type=str, help="TOML file with solve & visualization configuration (overriden by flags); default: solve_config.toml in the current folder")
    parser.add_argument('-e', '--encodings', type=str, nargs='+', help='one or more encodings (.lp) to load into clingo')
    parser.add_argument('-t', '--time-limit', type=int, metavar='SECONDS', help='stop each clingo call after SECONDS and use the best plan found so far')
    parser.add_argument('-m', '--save-model', action='store_true', help='save the model after solving')
    parser.add_argument('-s', '--save-stats', action='store_true', help='save clingo statistics')
    parser.add_argument('--save-encodings', action='store_true', help='save the encodings used. Useful for tracking the effects of changes to the encodings, or reproducing results.'
                                                                      'Note: #include statements are NOT resolved when saving encodings.')
    vis = parser.add_argument_group('Visualization options')
    vis.add_argument('--renderers', type=str, nargs='+', help='list of renderers to use, e.g. "html" or "gif"')
    vis.add_argument('--cell-size', type=int, help='size of each cell in the HTML visualization, in SVG user units')
    vis.add_argument('--log-train-states', action='store_true', help='log the train states used for calculating the displayed path')
    vis.add_argument('--train-colors', type=str, nargs='+', help='list of colors for individual trains')
    parser.set_defaults(**DEFAULT_CONFIG)
    return parser

def load_config(parser: ArgumentParser, config_file: Path) -> dict:
    """Load solve & visualization configuration from a TOML file and return as a dictionary suitable for parser.set_defaults"""
    try:
        with open(config_file, 'rb') as f:
            config = tomllib.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {config_file}")
    except Exception as e:
        raise ValueError(f"Invalid config file: {config_file}") from e

    return config

def parse_args(argv: list[str] | None = None) -> Namespace:
    parser = build_parser()
    argv = sys.argv[1:] if argv is None else list(argv)
    clingo_args = []
    if '--' in argv:
        split = argv.index('--')
        argv, clingo_args = argv[:split], argv[split+1:]

    pre, _ = parser.parse_known_args(argv)
    solve_config = pre.config
    if solve_config is None and DEFAULT_CONFIG_FILE.is_file():
        solve_config = DEFAULT_CONFIG_FILE
    if solve_config is None:
        logger.info("No solve_config file specified; using default.")
    try:
        solve_config = Path(solve_config)
        parser.set_defaults(**load_config(parser, solve_config))
    except Exception as e:
        logger.error(f"Config file not found or invalid: {solve_config}")
    
    args = parser.parse_args(argv)
    if args.time_limit is not None:
        clingo_args.append(f'--time-limit={args.time_limit}')
    args.clingo_args = clingo_args

    if args.renderers:
        # if passed from command line, separate into individual renderers (separated by +)
        renderers = []
        for r in args.renderers:
            for rp in r.split('+'):
                renderers.append(rp)
        args.renderers = renderers

    return args


def create_output_dir() -> Path:
    """ create a new folder output/<date>_<time> in the current folder """
    stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    path = Path("output") / stamp
    number = 1
    while path.exists():
        number += 1
        path = Path("output") / f"{stamp}_{number}"

    path.mkdir(parents=True, exist_ok=True)
    return(path)


def main(argv=None) -> int:
    args = parse_args(argv)
    env_path = Path(args.env)
    if not env_path.is_file():
        raise SystemExit(f"Environment not found: {args.env}")
    with env_path.open("rb") as f:
        try:
            env = pickle.load(f)
        except (ModuleNotFoundError, AttributeError) as e:
            raise SystemExit(f"Could not load '{args.env}' ({e}). It was probably created with a different version of flatland; regenerate it with 'flaspland build'.")
        
    env_renderers = []
    env_name = Path(args.env).stem
    for r in args.renderers:
        if r == 'gif':
            try:
                env_renderers.append(GifRenderer(env=env, env_name=env_name))
            except Exception as e:
                logger.error(f"Failed to initialize GIF renderer: {e} (but continuing with other renderers)")
        elif r == 'html':
            try:
                env_renderers.append(HtmlRenderer(env=env, env_path=env_path, env_name=env_name, config=args.__dict__))
            except Exception as e:
                logger.error(f"Failed to initialize HTML renderer: {e} (but continuing with other renderers)")
        else:
            logger.warning(f"Unknown renderer specified: {r}")
    
    # create manager objects
    mal = MalfunctionManager(env.get_num_agents())
    sim = SimulationManager(env, env_name, args.encodings, args.clingo_args)
    log = OutputLogManager()

    actions = sim.build_actions()

    logger.info(f"Starting simulation with environment {args.env} and encoding(s) {args.encodings}")

    for timestep in tqdm(range(len(actions)), desc="Simulating timesteps"):
        # add to the log
        for a in actions[timestep]:
            position, direction = get_position_and_direction(env.agents[a])
            log.add(f'{a};{timestep};{position};{DIR_MAP[direction]};{STATE_MAP[env.agents[a].state]};{ACTION_MAP[actions[timestep][a]]}\n')

        if env_renderers:
            for renderer in env_renderers:
                renderer.process_actions(timestep=timestep, actions=actions)

        _, _, done, info = env.step(actions[timestep])

        # end if simulation is finished
        if done['__all__'] and timestep < len(actions)-1:
            logger.warning('Simulation has reached its end before actions list has been exhausted.')
            break

        # check for new malfunctions
        new_malfs = mal.check(info)

        if len(new_malfs) > 0:
            context = sim.provide_context(actions, timestep, mal.get())
            actions = sim.update_actions(context)

        mal.deduct() #??? where in the loop should this go - before context?

        timestep = timestep + 1

    # create a new folder for the gif and output log
    output_dir = create_output_dir()

    for renderer in env_renderers:
        renderer.save(output_dir=output_dir, loop=0, duration=240)

    # save output log
    log.save(output_dir)

    if args.save_model:
        sim.save_model(output_dir=output_dir)
    if args.save_stats:
        sim.save_stats(output_dir=output_dir)
    if args.save_encodings:
        sim.save_encodings(output_dir=output_dir)

    return(0)


if __name__ == "__main__":
    sys.exit(main())
