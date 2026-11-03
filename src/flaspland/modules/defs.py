from flatland.envs.rail_env import RailEnvActions

DIR_MAP = {0:'n', 1:'e', 2:'s', 3:'w'}
ACTION_MAP = {RailEnvActions.MOVE_LEFT:'move_left', RailEnvActions.MOVE_FORWARD:'move_forward', RailEnvActions.MOVE_RIGHT:'move_right', RailEnvActions.STOP_MOVING:'wait'}
STATE_MAP = {0:'waiting', 1:'ready to depart', 2:'malfunction (off map)', 3:'moving', 4:'stopped', 5:'malfunction (on map)', 6:'done'}
