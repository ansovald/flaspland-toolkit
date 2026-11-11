from clingo.application import Application
from .. import __version__
from .convert import convert_to_clingo
from .actionlist import build_action_list

class FlatlandPlan(Application):
    """ takes an environment and a set of primary encodings """
    program_name = "flaspland"
    version = __version__

    def __init__(self, env, actions):
        self.env = env
        self.actions = actions
        self.action_list = None
        self.stats = None
        self.model = None

    def main(self, ctl, files):
        # add encodings
        for f in files:
            ctl.load(f)
        if not files:
            raise Exception('No file loaded into clingo.')

        # add env
        ctl.add(convert_to_clingo(self.env))

        # only print the plan (and whatever the encodings #show) instead of every atom
        ctl.add("#show action/3.")

        # add actions
        if self.actions is not None:
            ctl.add('base', [], ' '.join(self.actions))

        # ground the program
        ctl.ground([("base", [])], context=self)

        # solve and keep the last model: with clingo's default settings this is the first
        # model, or the best one found for encodings with optimization statements
        last, cost, count, result = None, [], 0, None
        try:
            with ctl.solve(yield_=True) as handle:
                for model in handle:
                    last, cost, count = model.symbols(atoms=True), model.cost, count + 1
                result = handle.get()
        except RuntimeError as error:
            # solving was stopped (e.g. by --time-limit); use the best model found so far
            print(f"flaspland: clingo was stopped ({error})")

        if last is None:
            return

        self.model = last
        self.stats = ctl.statistics

        # capture output actions for renderer
        self.action_list = build_action_list([last])
        if cost:
            optimal = result is not None and result.exhausted
            print(f"flaspland: using model {count} with cost {cost} "
                  f"({'optimal' if optimal else 'optimality not proven'})")
        else:
            print(f"flaspland: using model {count}")


# let's see later whether we even need this
class FlatlandReplan(Application):
    """ takes an environment, a set of secondary encodings, and additional context """
    program_name = "flatland"
    version = "1.0"
