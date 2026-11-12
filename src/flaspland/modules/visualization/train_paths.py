from __future__ import annotations
from .curves import CURVES, Point, CurveSegment, DIRECTION_TO_ROTATION, get_rotation, ROTATION_OFFSETS
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

"""
Module for handling train paths and movements as well as signals within the visualization.
"""

@dataclass
class TrainState:
    """
    TrainState holds all information about a train at a series of timesteps with same coordinates and status,
    except for the action, which is handled by the Movement class.
    During segment building, each TrainState is assigned incoming and outgoing CurveSegments 
    (only outcoming for READY_TO_DEPART, only incoming for ARRIVED).
    `display_rotation` is used for generating 'wait' paths when the train is stopped.
    """
    timestep: int
    coords: Point
    duration: int
    status: str
    rotation: int
    display_rotation: int = None
    center_offset: Point = None
    incoming_segment: CurveSegment = None
    outgoing_segment: CurveSegment = None

    def get_wait_path(self, cell_size) -> CurveSegment:
        center_offset = self.get_center_offset()
        offset = ROTATION_OFFSETS[self.display_rotation] * 0.0001
        start = Point(0.5, 0.5) + center_offset
        end = start + offset
        wait_segment = CurveSegment(
            start=start,
            end=end
        ).translate(self.coords)
        wait_path = wait_segment.standalone_path(cell_size)
        return wait_path

    def get_center_offset(self) -> Point:
        if self.center_offset is None:
            self.center_offset = Point(0, 0)
        return self.center_offset

    def get_display_rotation(self) -> int:
        if self.display_rotation is not None:
            return self.display_rotation, self.get_center_offset()
        return self.rotation, self.get_center_offset()

class Movement:
    """
    Movement represents a train action ('move_forward', 'move_right', 'move_left') that 
    connects two TrainStates over a series of timesteps (depending on train speed).
    It holds the motion path and keypoints for animating the train movement between the two states.
    No movement is created for 'wait' actions; their paths are generated directly from the TrainState, 
    using `get_wait_path()`.
    """
    def __init__(self, train_path: TrainPath, action: str, start: int, duration: int):
        self.train_path = train_path
        self.action = action
        self.start = start
        self.duration = duration
        self.from_state = None
        self.to_state = None
        self.keypoints = self.calculate_keypoints()
        self.motion_path = ""

    def calculate_keypoints(self) -> list[float, float]:
        key_points = [0.0]
        for i in range(1, self.duration + 1):
            kp = i / self.duration
            key_points.append(kp)
        return key_points

    def get_motion_info(self, cell_size: int, timestep) -> str:
        """
        Returns the motion path and animation keypoints for the train at the given timestep.
        """
        logger.debug(f"Getting motion info for movement {self} at timestep {timestep}, \nkeypoints={self.keypoints}")
        if not self.motion_path:
            self.motion_path = self.build_motion_path(cell_size)
        keypoint_idx = timestep - self.start
        return self.motion_path, [self.keypoints[keypoint_idx], self.keypoints[keypoint_idx + 1]]

    def build_motion_path(self, cell_size: int) -> str:
        path_string = self.from_state.outgoing_segment.standalone_path(cell_size)
        path_string += self.to_state.incoming_segment.segment_path(cell_size)
        return path_string
    
    def set_states(self):
        from_state_idx = self.train_path.timestep_state_mapping[self.start]
        self.from_state = self.train_path.states[from_state_idx]
        to_state_idx = self.train_path.timestep_state_mapping[self.start + self.duration]
        self.to_state = self.train_path.states[to_state_idx]
    
    def __str__(self):
        return f"Movement(action={self.action}, start={self.start}, duration={self.duration}, keypoints={self.keypoints}, motion_path={self.motion_path})"

class TrainPath:
    """
    TrainPath is the main class for building the display states and motion paths for a single train.
    It is initialized with the train_id, train_info (dict passed by the environment), 
    timeframe (total timesteps), and cell_size (for SVG scaling).
    When initialized, it builds the main TrainStates and Movements for the train.
    The main method is `get_display_states()`, which returns a dict of display states for each timestep,
    including action, status, position, motionPath, signal, opacity, and keyPoints.    
    """
    def __init__(self, train_id: int, train_info: dict, timeframe: int, cell_size: int, log_states=True):
        self.train_id = train_id
        self.speed = train_info['speed']
        self.train_info = train_info
        self.timeframe = timeframe
        self.cell_size = cell_size
        self.states: list[dict] = []
        self.initial_state = None
        self.arrival_state = None
        self.timestep_state_mapping: dict[int, int] = {}
        self.movements: list[Movement] = []
        self.timestep_movement_mapping: dict[int, int] = {}
        self.path_string = ""
        logger.debug(f"Initializing TrainPath for train {train_id} with time frame {timeframe}")
        self.build_states()
        self.build_segments()
        if log_states:
            # for debugging: write main states to file
            with open(LOG_DIR / f"train_{train_id}_states.log", "w") as f:
                f.write(f"Timestep-State mapping:\n{self.timestep_state_mapping}\nStates:\n")
                for i, state in enumerate(self.states):
                    f.write(f"{i}: " + state.__str__() + "\n")
            with open(LOG_DIR / f"train_{train_id}_movements.log", "w") as f:
                f.write(self.timestep_movement_mapping.__str__() + "\n")
                for i, action in enumerate(self.movements):
                    f.write(f"{i}: " + action.__str__() + "\n")
        logger.debug(f"Finished initializing TrainPath for train {train_id}")
        
    def build_states(self):
        """
        Build the main TrainStates for the train by parsing the train_info path.
        Adds 'ARRIVED' state when the train reaches its destination (not automatically provided by the toolkit), 
        and then fills in 'PARKED' state until timeframe.
        Consecutive timesteps with same coordinates and status are merged into a single TrainState with duration.
        Also builds the list of Movements for non-wait actions, linking them to the TrainStates.
        """
        logger.debug(f"Parsing states for TrainPath {self.train_id}")
        timestep = 0
        last_coords = None
        last_state = None
        while timestep <= self.timeframe:
            current_state = self.trainstate_at(timestep)
            logger.debug(f"Processing timestep {timestep} for train {self.train_id}:\n{current_state}")
            coords = current_state.coords
            status = current_state.status
            if status == "READY_TO_DEPART":
                # train is ready to depart but hasn't moved yet. Ignore the move action
                current_state.display_rotation = current_state.rotation
                self.states.append(current_state)
                self.timestep_state_mapping[timestep] = len(self.states) - 1
                logger.debug(f"Adding READY_TO_DEPART state for train {self.train_id} at timestep {timestep}:\n{current_state}")
            elif coords and not coords.is_none():
                if not last_coords:
                    self.initial_state = current_state
                    self.states.append(current_state)
                    last_state = current_state
                    last_coords = coords
                    logger.debug(f"Adding initial state for train {self.train_id} at timestep {timestep}:\n{current_state}")
                elif coords == last_coords and status == last_state.status:
                    # still moving but coordinates haven't changed yet
                    last_state.duration += 1
                else:
                    self.states.append(current_state)
                    last_coords = coords
                    last_state = current_state
                    logger.debug(f"Adding new state for train {self.train_id} at timestep {timestep}:\n{current_state}")
                self.timestep_state_mapping[timestep] = len(self.states) - 1
                logger.debug(f"Processed state for train {self.train_id} at timestep {timestep}:\n{current_state}\nmapping {self.timestep_state_mapping[timestep]}")

                if timestep not in self.timestep_movement_mapping:
                    action = self.action_at(timestep)
                    if action != "wait":
                        movement = Movement(self, action, timestep, self.speed)
                        logger.debug(f"Adding movement for train {self.train_id} at timestep {timestep}:\n{movement}")
                        self.movements.append(movement)
                        for i in range(timestep, timestep + self.speed):
                            self.timestep_movement_mapping[i] = len(self.movements) - 1
            timestep += 1
        last_timestep = self.states[-1].timestep + self.states[-1].duration
        dest_coords = Point.from_dict(self.train_info['end']['position'])
        distance_to_destination = self.states[-1].coords.distance_to(dest_coords)
        if distance_to_destination == 1:
            last_coords = dest_coords
            status = "ARRIVED"
            logger.debug(f"Adjusting last coordinates for train {self.train_id} to destination coords: {dest_coords}")
        else:
            status = "NOT_ARRIVED"
            last_coords = self.states[-1].coords + ROTATION_OFFSETS[self.states[-1].rotation]
            logger.warning(f"Train {self.train_id} does not appear to have reached its destination! Last coords: {self.states[-1].coords}, dest coords: {dest_coords}, setting last coords to: {last_coords}")
        arrival_state = TrainState(
            timestep = last_timestep,
            coords = last_coords,
            duration = 1,
            status = status,
            rotation = get_rotation(self.states[-1].coords, last_coords)
        )
        logger.debug(f"Created arrival state for train {self.train_id}:\n{arrival_state}")
        self.arrival_state = arrival_state
        self.states.append(arrival_state)
        logger.debug(f"Adding ARRIVED state for train {self.train_id} at timestep {last_timestep}:\n{arrival_state}")
        self.timestep_state_mapping[last_timestep] = len(self.states) - 1

        if last_timestep < self.timeframe:
            self.timestep_state_mapping[last_timestep] = len(self.states) - 1
            last_timestep += 1
            duration = self.timeframe - last_timestep + 1
            last_state = TrainState(
                timestep=last_timestep,
                coords=None,
                duration=duration,
                status="ARRIVED",
                rotation=arrival_state.rotation,
                display_rotation=arrival_state.rotation
            )
            self.states.append(last_state)
            for i in range(last_timestep, self.timeframe + 1):
                self.timestep_state_mapping[i] = len(self.states) - 1

    def build_segments(self):
        """
        Build the CurveSegments for each TrainState, and the overall motion path for the train.
        Most states have two segments: an incoming segment and an outgoing segment, 
        joined in the middle of the cell (with an offset for curves).
        The incoming segment connects to the outgoing segment of the prior state.
        The outgoing segment connects to the incoming segment of the next state.
        Each movement connects two states, and the motion paths are built from the segments of these linked states.
        """
        for i in range(1, len(self.states)):
            # we don't need to build segments for the last state (train has arrived and is stopped)
            logger.debug(f"\ntrain={self.train_id}, i={i}/{len(self.states)}, building segments for state: {self.states[i]}")
            coords = self.states[i].coords
            rotation = self.states[i].rotation
            status = self.states[i].status
            if i == 1:
                curve = CURVES[(rotation, rotation)]
                outgoing = curve['outgoing'].translate(coords)
                self.states[i].outgoing_segment = outgoing
                self.path_string = outgoing.standalone_path(self.cell_size)
                self.states[i].display_rotation = rotation
            elif status == "WAITING":
                # don't need to build any segments for waiting state, take display rotation from last state (if it exists)
                if self.states[i-1].display_rotation is not None:
                    self.states[i].display_rotation = self.states[i-1].display_rotation
                    self.states[i].center_offset = self.states[i-1].center_offset
                else:
                    self.states[i].display_rotation = rotation
                logger.debug(f"waiting state for train {self.train_id}, skipping segment building")
                continue
            elif status in ["ARRIVED", "NOT_ARRIVED"]:
                curve = CURVES[(rotation, rotation)]
                incoming = curve['incoming'].translate(coords)
                self.states[i].display_rotation = rotation
                self.states[i].center_offset = curve['mid']
                self.states[i].incoming_segment = incoming
                self.path_string += incoming.segment_path(self.cell_size)
                logger.debug(f"Updated arrival state for train {self.train_id} at index {i}:\n{self.states[i]}")
                # we don't need to build any more segments after arrival
                break
            else:
                # train is moving, build incoming and outgoing segments
                next_coordinates = self.states[i+1].coords
                offset = 2
                while next_coordinates == coords:
                    next_coordinates = self.states[i + offset].coords
                    offset += 1
                logger.debug(f"current coords at i={i}: {coords}, rotation={rotation}, next coords: {next_coordinates}")
                out_rotation = get_rotation(coords, next_coordinates)
                logger.debug(f"getting curve for (in={rotation}, out={out_rotation})")
                curve = CURVES[(rotation, out_rotation)]
                incoming = curve['incoming'].translate(coords)
                outgoing = curve['outgoing'].translate(coords)
                self.states[i].display_rotation = curve['rotation']
                self.states[i].center_offset = curve['mid']
                self.states[i].incoming_segment = incoming
                self.states[i].outgoing_segment = outgoing
                if self.states[i-1].coords != coords:
                    self.path_string += incoming.segment_path(self.cell_size)
                    self.path_string += outgoing.segment_path(self.cell_size)
                logger.debug(f"Built segments for train {self.train_id} at state index {i}:\nIncoming: {incoming}\nOutgoing: {outgoing}")
            logger.debug(f"i={i}, {self.states[i]}")

    def get_motion_info(self, timestep) -> tuple[str, list[float]]:
        """
        Returns the motion path and animation keypoints for the train at the given timestep.
        """
        timestep = timestep - 1 # motion only starts one timestep AFTER action is initiated
        movement_idx = self.timestep_movement_mapping.get(timestep, None)
        # if there is no movement for this timestep, return wait path for current state
        if movement_idx is None:
            state_idx = self.timestep_state_mapping.get(timestep, None)
            if state_idx is None:
                # no entry for this timestep, default to initial wait path
                state = self.initial_state
                return state.get_wait_path(self.cell_size), [0.0, 1.0]
            else:
                state = self.states[state_idx]
                if state.status == "READY_TO_DEPART":
                    # state = self.states[state_idx + 1]
                    state = self.initial_state
                    return state.get_wait_path(self.cell_size), [0.0, 1.0]
                elif state.status in ["ARRIVED", "NOT_ARRIVED"] and state.coords is None:
                    return self.arrival_state.get_wait_path(self.cell_size), [0.0, 1.0]
                logger.debug(f"No movement found for train {self.train_id} at timestep {timestep}, defaulting to wait path for state index {state_idx}")
                state = self.states[state_idx]
                return state.get_wait_path(self.cell_size), [0.0, 1.0]
        movement = self.movements[movement_idx]
        movement.set_states()
        return movement.get_motion_info(self.cell_size, timestep)
    
    def display_info(self, timestep: int) -> float:
        """
        Called to get the display info for the train at a given timestep,
        which contains all info necessary for animating the train in the HTML visualization.
        Returns a dict with action, status, position, motionPath, signal, opacity, and keyPoints.
        """
        state_index = self.timestep_state_mapping.get(timestep, None)
        logger.debug(f"\nGetting display info for train {self.train_id} at timestep {timestep}, state_index={state_index}")
        state = None
        if state_index is not None:
            logger.debug(f"state_index found for timestep {timestep}: {state_index}")
            state = self.states[state_index]
            status = state.status
        else:
            logger.debug(f"No state_index found for timestep {timestep}, defaulting to initial PARKED state")
            # no entry for this timestep, default to initial wait path
            status = "PARKED"
        motion_path, keypoints = self.get_motion_info(timestep)
        opacity = 1.0
        if status == "PARKED":
            opacity = 0.0
        elif status in ["ARRIVED", "NOT_ARRIVED"]:
            if not state.coords or state.coords.is_none():
                opacity = 0.0
            else:
                opacity = 1.0
        elif status == "READY_TO_DEPART":
            opacity = 1.0
        action = self.action_at(timestep)
        if state:
            position = state.coords
        else:
            position = self.coords_at(timestep)
        # when moving, signal is not displayed
        signal = None
        if action == "wait":
            # when waiting, signal is red if the train waits at the next timestep, too
            signal = "red"
        else:
            if self.action_at(timestep - 1) == "wait":
                signal = "green"
        return {
            "action": action,
            "status": status,
            "position": f"{int(position.x)},{int(position.y)}" if position and not position.is_none() else "n/a",
            "motionPath": motion_path,
            "signal": signal,
            "opacity": opacity,
            "keyPoints": f"{keypoints[0]};{keypoints[1]}",
        }
    
    def get_display_states(self) -> dict[int, dict]:
        """
        Called to get the full display states for the train over all timesteps,
        which contain all info necessary for animating the train in the HTML visualization.
        Returns a dict mapping timestep to display info dict.
        """
        display_states = {}
        for timestep in range(self.timeframe + 1):
            logger.debug(f"\nCalling display info for train {self.train_id} at timestep {timestep}")
            display_states[timestep] = self.display_info(timestep)
            logger.debug(f"Display info for train {self.train_id} at timestep {timestep}:\n{display_states[timestep]}")
        return display_states

    def get_signal_at(self, timestep: int) -> Signal | None:
        """
        Returns the signal info for the train at the given timestep.
        """
        coords = self.coords_at(timestep)
        if coords is None or coords.is_none():
            return None
        signal_state = None
        action = self.action_at(timestep)
        if action == "wait":
            signal_state = "red"
        else:
            if self.action_at(timestep - 1) == "wait":
                signal_state = "green"
        if signal_state is None:
            return None
        display_rotation, offset = self.display_rotation_offset_at(timestep)
        return Signal(
            coords = self.coords_at(timestep),
            rotation = self.rotation_at(timestep),
            display_rotation = display_rotation,
            offset = offset,
            states = {timestep: signal_state}
        )

    def get_signal_list(self) -> SignalList:
        """
        Returns a SignalList containing the signal info for the train over all timesteps,
        that can be merged with other SignalLists.
        """
        signal_list = SignalList()
        for timestep in range(self.timeframe + 1):
            signal_list.add_signal(self.get_signal_at(timestep))
        return signal_list
    
    def trainstate_at(self, timestep: int) -> TrainState:
        """
        If the timestep has already been recorded in the timestep_state_mapping, returns that TrainState.
        Otherwise, constructs a new TrainState from the train_info dict.
        """
        if timestep in self.timestep_state_mapping:
            return self.states[self.timestep_state_mapping[timestep]]
        return TrainState(
            timestep=timestep,
            coords=self.coords_at(timestep),
            duration=1,
            status=self.status_at(timestep),
            rotation=self.rotation_at(timestep)
        )

    def display_rotation_offset_at(self, timestep: int) -> tuple[int, Point]:
        """
        Returns the display rotation for the train at the given timestep.
        """
        return self.trainstate_at(timestep).get_display_rotation()
    
    def coords_at(self, timestep: int) -> Point:
        """
        Looks up the coordinates for the given timestep from the train_info dict.
        """
        if timestep in self.train_info['path']:
            step_dict = self.train_info['path'][timestep]
            coords = Point.from_dict(step_dict['position'])
            return coords
        else:
            logger.debug(f"Coordinates for train {self.train_id} at timestep {timestep} not found.")
            return None
        
    def action_at(self, timestep: int) -> str:
        """
        Looks up the action for the given timestep from the train_info dict.
        If the action is not found, returns 'wait' (before departure/after arrival).
        """
        if timestep in self.train_info['path']:
            step_dict = self.train_info['path'][timestep]
            return step_dict.get('action', None)
        else:
            return 'wait'
        
    def status_at(self, timestep: int) -> str:
        """
        Looks up the status (WAITING, READY_TO_DEPART, MOVING, STOPPED) for the given timestep from the train_info dict.
        """
        if timestep in self.train_info['path']:
            step_dict = self.train_info['path'][timestep]
            return step_dict.get('status', None)
        else:
            return None
    
    def rotation_at(self, timestep: int) -> str:
        """
        Looks up the direction for the given timestep from the train_info dict,
        and converts it to rotation in degrees.
        """
        if timestep in self.train_info['path']:
            rotation = DIRECTION_TO_ROTATION.get(self.train_info['path'][timestep]['direction'], None)
            return rotation
        else:
            return None

    def get_path_string(self) -> str:
        return self.path_string


class Signal:
    def __init__(self, coords, rotation, display_rotation, offset, states):
        self.coords = coords
        self.rotation = rotation
        self.display_rotation = display_rotation
        self.offset = offset
        self.states = states

    def __repr__(self):
        return f"Signal(coords={self.coords}, rotation={self.rotation}, display_rotation={self.display_rotation}, offset={self.offset}, states={self.states})"

    def get_display_states(self, timeframe: int) -> dict[int, dict]:
        display_states = {}
        for timestep in range(timeframe + 1):
            # signals should be red by default if no state is specified
            if timestep in self.states:
                display_states[timestep] = self.states[timestep]
            else:
                # if no more train will pass through this signal, we turn it off (signal not displayed anymore)
                display_states[timestep] = "off"
                # try to find the next state for this signal, and use its color
                i = timestep
                while i <= timeframe and i not in self.states:
                    i += 1
                if i <= timeframe and i in self.states:
                    display_states[timestep] = self.states[i]

        return display_states

class SignalList:
    def __init__(self):
        self.signals = []

    def add_signal(self, signal: Signal):
        if signal is None:
            return
        # check if there is a signal at the same position and rotation
        for existing_signal in self.signals:
            if existing_signal.coords == signal.coords and existing_signal.rotation == signal.rotation:
                # update the states of the existing signal
                existing_signal.states.update(signal.states)
                return
        self.signals.append(signal)

    def extend(self, other_signal_list: "SignalList"):
        for signal in other_signal_list.get_signals():
            self.add_signal(signal)

    def update_states(self, train_paths: list[TrainPath]):
        for signal in self.signals:
            for train_path in train_paths:
                for train_state in train_path.states:
                    if train_state.coords == signal.coords and train_state.rotation == signal.rotation:
                        timestep = train_state.timestep
                        if train_path.action_at(timestep) != 'wait':
                            signal.states[timestep] = "green"
                            logger.debug(f"Signal at {signal.coords} turned green at timestep {timestep}")

    def get_signals(self):
        return self.signals

    def __repr__(self):
        return f"SignalList(signals={self.signals})"

    def __iter__(self):
        return iter(self.signals)

    def __len__(self):
        return len(self.signals)

    def get_display_states(self, timeframe: int) -> dict[int, dict]:
        display_states = {}
        for i, signal in enumerate(self.signals):
            display_states[i] = signal.get_display_states(timeframe)
        return display_states