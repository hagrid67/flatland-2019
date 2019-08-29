"""Schedule generators (railway undertaking, "EVU")."""
import warnings
from typing import Tuple, List, Callable, Mapping, Optional, Any

import msgpack
import numpy as np

from flatland.core.grid.grid4_utils import get_new_position
from flatland.core.transition_map import GridTransitionMap
from flatland.envs.agent_utils import EnvAgentStatic

AgentPosition = Tuple[int, int]
ScheduleGeneratorProduct = Tuple[List[AgentPosition], List[AgentPosition], List[AgentPosition], List[float]]
ScheduleGenerator = Callable[[GridTransitionMap, int, Optional[Any]], ScheduleGeneratorProduct]


def speed_initialization_helper(nb_agents: int, speed_ratio_map: Mapping[float, float] = None) -> List[float]:
    """
    Parameters
    -------
    nb_agents : int
        The number of agents to generate a speed for
    speed_ratio_map : Mapping[float,float]
        A map of speeds mappint to their ratio of appearance. The ratios must sum up to 1.

    Returns
    -------
    List[float]
        A list of size nb_agents of speeds with the corresponding probabilistic ratios.
    """
    if speed_ratio_map is None:
        return [1.0] * nb_agents

    nb_classes = len(speed_ratio_map.keys())
    speed_ratio_map_as_list: List[Tuple[float, float]] = list(speed_ratio_map.items())
    speed_ratios = list(map(lambda t: t[1], speed_ratio_map_as_list))
    speeds = list(map(lambda t: t[0], speed_ratio_map_as_list))
    return list(map(lambda index: speeds[index], np.random.choice(nb_classes, nb_agents, p=speed_ratios)))


def complex_schedule_generator(speed_ratio_map: Mapping[float, float] = None) -> ScheduleGenerator:
    def generator(rail: GridTransitionMap, num_agents: int, hints: Any = None):
        start_goal = hints['start_goal']
        start_dir = hints['start_dir']
        agents_position = [sg[0] for sg in start_goal[:num_agents]]
        agents_target = [sg[1] for sg in start_goal[:num_agents]]
        agents_direction = start_dir[:num_agents]

        if speed_ratio_map:
            speeds = speed_initialization_helper(num_agents, speed_ratio_map)
        else:
            speeds = [1.0] * len(agents_position)

        return agents_position, agents_direction, agents_target, speeds

    return generator


def sparse_schedule_generator(speed_ratio_map: Mapping[float, float] = None) -> ScheduleGenerator:
    def generator(rail: GridTransitionMap, num_agents: int, hints: Any = None):
        train_stations = hints['train_stations']
        agent_start_targets_nodes = hints['agent_start_targets_nodes']
        num_agents = hints['num_agents']
        # Place agents and targets within available train stations
        agents_position = []
        agents_target = []
        agents_direction = []
        for agent_idx in range(num_agents):
            # Set target for agent
            current_target_node = agent_start_targets_nodes[agent_idx][1]
            target_station_idx = np.random.randint(len(train_stations[current_target_node]))
            target = train_stations[current_target_node][target_station_idx]
            tries = 0
            while (target[0], target[1]) in agents_target:
                target_station_idx = np.random.randint(len(train_stations[current_target_node]))
                target = train_stations[current_target_node][target_station_idx]
                tries += 1
                if tries > 100:
                    warnings.warn("Could not set target position, removing an agent")
                    break
            agents_target.append((target[0], target[1]))

            # Set start for agent
            current_start_node = agent_start_targets_nodes[agent_idx][0]
            start_station_idx = np.random.randint(len(train_stations[current_start_node]))
            start = train_stations[current_start_node][start_station_idx]
            tries = 0
            while (start[0], start[1]) in agents_position:
                tries += 1
                if tries > 100:
                    warnings.warn("Could not set start position, please change initial parameters!!!!")
                    break
                start_station_idx = np.random.randint(len(train_stations[current_start_node]))
                start = train_stations[current_start_node][start_station_idx]

            agents_position.append((start[0], start[1]))

            # Orient the agent correctly
            for orientation in range(4):
                transitions = rail.get_transitions(start[0], start[1], orientation)
                if any(transitions) > 0:
                    agents_direction.append(orientation)
                    continue

        if speed_ratio_map:
            speeds = speed_initialization_helper(num_agents, speed_ratio_map)
        else:
            speeds = [1.0] * len(agents_position)

        return agents_position, agents_direction, agents_target, speeds

    return generator


def random_schedule_generator(speed_ratio_map: Mapping[float, float] = None) -> ScheduleGenerator:
    """
    Given a `rail' GridTransitionMap, return a random placement of agents (initial position, direction and target).

    Parameters
    -------
        rail : GridTransitionMap
            The railway to place agents on.
        num_agents : int
            The number of agents to generate a speed for
        speed_ratio_map : Mapping[float,float]
            A map of speeds mappint to their ratio of appearance. The ratios must sum up to 1.
    Returns
    -------
        Tuple[List[Tuple[int,int]], List[Tuple[int,int]], List[Tuple[int,int]], List[float]]
        initial positions, directions, targets speeds
    """

    def generator(rail: GridTransitionMap, num_agents: int, hints: Any = None) -> ScheduleGeneratorProduct:

        valid_positions = []
        for r in range(rail.height):
            for c in range(rail.width):
                if rail.get_full_transitions(r, c) > 0:
                    valid_positions.append((r, c))
        if len(valid_positions) == 0:
            return [], [], [], []

        if len(valid_positions) < num_agents:
            warnings.warn("schedule_generators: len(valid_positions) < num_agents")
            return [], [], [], []

        agents_position_idx = [i for i in np.random.choice(len(valid_positions), num_agents, replace=False)]
        agents_position = [valid_positions[agents_position_idx[i]] for i in range(num_agents)]
        agents_target_idx = [i for i in np.random.choice(len(valid_positions), num_agents, replace=False)]
        agents_target = [valid_positions[agents_target_idx[i]] for i in range(num_agents)]
        update_agents = np.zeros(num_agents)

        re_generate = True
        cnt = 0
        while re_generate and cnt < 100:
            cnt += 1
            # update position
            for i in range(num_agents):
                if update_agents[i] == 1:
                    x = np.setdiff1d(np.arange(len(valid_positions)), agents_position_idx)
                    agents_position_idx[i] = np.random.choice(x)
                    agents_position[i] = valid_positions[agents_position_idx[i]]
                    x = np.setdiff1d(np.arange(len(valid_positions)), agents_target_idx)
                    agents_target_idx[i] = np.random.choice(x)
                    agents_target[i] = valid_positions[agents_target_idx[i]]
            update_agents = np.zeros(num_agents)

            # agents_direction must be a direction for which a solution is
            # guaranteed.
            agents_direction = [0] * num_agents
            re_generate = False
            for i in range(num_agents):
                valid_movements = []
                if rail.is_dead_end(agents_position[i]):
                    print("   dead_end", agents_position[i])
                for direction in range(4):
                    position = agents_position[i]
                    moves = rail.get_transitions(position[0], position[1], direction)
                    for move_index in range(4):
                        if moves[move_index]:
                            valid_movements.append((direction, move_index))

                valid_starting_directions = []
                for m in valid_movements:
                    new_position = get_new_position(agents_position[i], m[1])
                    if m[0] not in valid_starting_directions and rail.check_path_exists(new_position, m[0],
                                                                                        agents_target[i]):
                        valid_starting_directions.append(m[0])

                if len(valid_starting_directions) == 0:
                    update_agents[i] = 1
                    print("reset position for agents:", i, agents_position[i], agents_target[i])
                    print("   dead_end", rail.is_dead_end(agents_position[i]))
                    re_generate = True
                    break
                else:
                    agents_direction[i] = valid_starting_directions[
                        np.random.choice(len(valid_starting_directions), 1)[0]]

        if re_generate:
            print("re_generate")

        agents_speed = speed_initialization_helper(num_agents, speed_ratio_map)
        return agents_position, agents_direction, agents_target, agents_speed

    return generator


def schedule_from_file(filename) -> ScheduleGenerator:
    """
    Utility to load pickle file

    Parameters
    -------
    input_file : Pickle file generated by env.save() or editor

    Returns
    -------
    Tuple[List[Tuple[int,int]], List[Tuple[int,int]], List[Tuple[int,int]], List[float]]
        initial positions, directions, targets speeds
    """

    def generator(rail: GridTransitionMap, num_agents: int, hints: Any = None) -> ScheduleGeneratorProduct:
        with open(filename, "rb") as file_in:
            load_data = file_in.read()
        data = msgpack.unpackb(load_data, use_list=False)

        # agents are always reset as not moving
        agents_static = [EnvAgentStatic(d[0], d[1], d[2], moving=False) for d in data[b"agents_static"]]
        # setup with loaded data
        agents_position = [a.position for a in agents_static]
        agents_direction = [a.direction for a in agents_static]
        agents_target = [a.target for a in agents_static]

        return agents_position, agents_direction, agents_target, [1.0] * len(agents_position)

    return generator
