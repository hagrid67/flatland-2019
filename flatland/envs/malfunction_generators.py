"""Malfunction generators for rail systems"""

from typing import Callable, NamedTuple, Optional, Tuple

import msgpack
import numpy as np
from numpy.random.mtrand import RandomState

from flatland.envs.agent_utils import EnvAgent

Malfunction = NamedTuple('Malfunction', [('num_broken_steps', int)])
MalfunctionGenerator = Callable[[EnvAgent], Optional[Malfunction]]
MalfunctionProcessData = NamedTuple('MalfunctionProcessData',
                                    [('malfunction_rate', float), ('min_duration', int), ('max_duration', int)])


def _malfunction_prob(rate: float) -> float:
    """
    Probability of a single agent to break. According to Poisson process with given rate
    :param rate:
    :return:
    """
    if rate <= 0:
        return 0.
    else:
        return 1 - np.exp(- (1 / rate))


def malfunction_from_file(filename) -> Tuple[MalfunctionGenerator, MalfunctionProcessData]:
    """
    Utility to load pickle file

    Parameters
    ----------
    input_file : Pickle file generated by env.save() or editor

    Returns
    -------
    Tuple[float, int, int] with mean_malfunction_rate, min_number_of_steps_broken, max_number_of_steps_broken
    """
    with open(filename, "rb") as file_in:
        load_data = file_in.read()
    data = msgpack.unpackb(load_data, use_list=False, encoding='utf-8')
    # TODO: make this better by using namedtuple in the pickle file
    data['malfunction'] = MalfunctionProcessData._make(data['malfunction'])
    if "malfunction" in data:
        # Mean malfunction in number of time steps
        mean_malfunction_rate = data["malfunction"].malfunction_rate

        # Uniform distribution parameters for malfunction duration
        min_number_of_steps_broken = data["malfunction"].min_duration
        max_number_of_steps_broken = data["malfunction"].max_duration
    else:
        # Mean malfunction in number of time steps
        mean_malfunction_rate = 0.
        # Uniform distribution parameters for malfunction duration
        min_number_of_steps_broken = 0
        max_number_of_steps_broken = 0

    def generator(agent: EnvAgent, np_random: RandomState) -> Optional[Malfunction]:
        """
        Generate malfunctions for agents
        Parameters
        ----------
        agent
        np_random

        Returns
        -------
        int: Number of time steps an agent is broken
        """
        if agent.malfunction_data['malfunction'] < 1:
            if np_random.rand() < _malfunction_prob(mean_malfunction_rate):
                num_broken_steps = np_random.randint(min_number_of_steps_broken,
                                                     max_number_of_steps_broken + 1) + 1
                return Malfunction(num_broken_steps)
        return Malfunction(0)

    return generator, MalfunctionProcessData(mean_malfunction_rate, min_number_of_steps_broken,
                                             max_number_of_steps_broken)


def malfunction_from_params(parameters: dict) -> Tuple[MalfunctionGenerator, MalfunctionProcessData]:
    """
    Utility to load malfunction from parameters

    Parameters
    ----------
    parameters containing
    malfunction_rate : float how many time steps it takes for a sinlge agent befor it breaks
    min_duration : int minimal duration of a failure
    max_number_of_steps_broken : int maximal duration of a failure

    Returns
    -------
    Tuple[float, int, int] with mean_malfunction_rate, min_number_of_steps_broken, max_number_of_steps_broken
    """
    mean_malfunction_rate = parameters['malfunction_rate']
    min_number_of_steps_broken = parameters['min_duration']
    max_number_of_steps_broken = parameters['max_duration']

    def generator(agent: EnvAgent, np_random: RandomState) -> Optional[Malfunction]:
        """
        Generate malfunctions for agents
        Parameters
        ----------
        agent
        np_random

        Returns
        -------
        int: Number of time steps an agent is broken
        """
        if agent.malfunction_data['malfunction'] < 1:
            if np_random.rand() < _malfunction_prob(mean_malfunction_rate):
                num_broken_steps = np_random.randint(min_number_of_steps_broken,
                                                     max_number_of_steps_broken + 1) + 1
                return Malfunction(num_broken_steps)
        return Malfunction(0)

    return generator, MalfunctionProcessData(mean_malfunction_rate, min_number_of_steps_broken,
                                             max_number_of_steps_broken)


def no_malfunction_generator() -> Tuple[MalfunctionGenerator, MalfunctionProcessData]:
    """
    Utility to load malfunction from parameters

    Parameters
    ----------
    input_file : Pickle file generated by env.save() or editor

    Returns
    -------
    Tuple[float, int, int] with mean_malfunction_rate, min_number_of_steps_broken, max_number_of_steps_broken
    """
    # Mean malfunction in number of time steps
    mean_malfunction_rate = 0.

    # Uniform distribution parameters for malfunction duration
    min_number_of_steps_broken = 0
    max_number_of_steps_broken = 0

    def generator(agent: EnvAgent, np_random: RandomState) -> Optional[Malfunction]:
        return Malfunction(0)

    return generator, MalfunctionProcessData(mean_malfunction_rate, min_number_of_steps_broken,
                                             max_number_of_steps_broken)
