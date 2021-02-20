import copy
import random
import time

from math import e, ceil

import numpy as np

from simulation.ode_simulator import OdeSimulator
from structured_results import StructuredResults


class ConstraintSatisfaction:
    # region find_network methods

    """
    :param StructuredResults results: results of network's simulation
    :param List[Constraint] constraints: list of constraints to evaluate the results against
    :returns float representing evaluating network given the constraints
    """

    @staticmethod
    def _evaluate_network(net, sim, constraints):
        results = StructuredResults(OdeSimulator.simulate(net, sim), list(net.species.keys()),
                                    sim.generate_time_space())
        total = 0

        for c in constraints:
            # All the simulation values in the time range
            vals = results.results_between_times(c.species, c.time_period[0], c.time_period[1])
            # All the simulation values in the time range, which do not satisfy the constraint.
            not_sat = list(filter(lambda v: c.value_constraint(v) > 0, vals))

            if not_sat:
                total += c.value_constraint(np.mean(not_sat))

        return total

    @staticmethod
    def _generate_next_level(net, sim, mutables, constraints):
        level = []

        nodes = []
        for i in range(0, len(mutables)):
            if mutables[i].is_next():
                node = copy.deepcopy(mutables)
                node[i].next()
                nodes.append(node)

        for node in nodes:
            net.mutate(node)
            eval_node = ConstraintSatisfaction._evaluate_network(net, sim, constraints)
            level.append((node, eval_node))

        return level

    """
    :param Network net: The network to modify
    :param SimulationSettings sim: The settings to be used to simulate the network during reverse engineering.
    :param List[Mutable] mutables: List of values which can be mutated during the constraint satisfaction process.
    :param List[Constraint] constraints: The list of constraints which the network must satisfy.
    :param int give_up_time: The time limit after which the process will stop and return None
    """

    @staticmethod
    def find_network(net, sim, mutables, constraints, give_up_time):

        mut_net = copy.deepcopy(net)

        # First, check whether network already satisfies constraints
        evalCurrent = ConstraintSatisfaction._evaluate_network(mut_net, sim, constraints)
        if evalCurrent <= 0:
            return mut_net

        first_level = sorted(ConstraintSatisfaction.
                             _generate_next_level(mut_net, sim, mutables, constraints),
                             reverse=True, key=lambda x: x[1])

        start = time.time()

        stack = first_level
        while stack:
            now = time.time()
            # Check whether the time limit has been reached
            if now - start >= give_up_time:
                return None

            (current, eval_current) = stack.pop()

            if eval_current <= 0:
                return mut_net
            else:
                s = ConstraintSatisfaction._generate_next_level(mut_net, sim, current, constraints)
                stack = sorted(stack + s, reverse=True, key=lambda x: x[1])

        return None

    # endregion

    # region find_closest_network methods

    """
    :param Dict[str, Tuple[float, str]] current: current state of the network's representation used by 
        the simulated annealing algorithm
    :param Dict[str, Mutable] mutables: Variables which can be mutated.
    :returns Dict[str, Tuple[float, str]] of the network state
    """

    @staticmethod
    def _generate_neighbour(mutables):
        # These are the mutables which still have not reached their upperbound value, so they are
        # available for incrementing
        available_mutables = list(filter(lambda x: x.is_next(), list(mutables)))

        nbour = mutables.copy()

        if available_mutables:
            # 1. Choose a random mutable from the mutables list
            r = random.randrange(len(available_mutables))
            rand_mutable = list(available_mutables)[r]

            # 2. Increment mutable by its increment to create a new network,
            # i.e. current network's neighbour
            rand_mutable.next()

        return nbour

    """
    Return true with a probability specified by the prob parameter

    :param float prob: The probability that the function will return True
    """

    @staticmethod
    def _rand_bool(prob):
        # Since using integers for random generation, some precision of p, which is a float,
        # will be lost (e.g. 0.387 would give 2.58397... for 1/p, and no = 3 in this case. Thus
        # rather than the actual probability being 0.387, it will be 0.33.) To avoid this,
        # multiply 2.58397... with precision (say, 100) to get the integer 258. In this case,
        # each number has a probability of being picked 1/258 = 0.00387596, or the first
        # set of 'precision' many values have a probability of 0.387596..., which is accurate
        # to 3 decimal places.

        random.seed()
        precision = 100
        no = ceil(1 / prob) * precision  # Total number of possible
        rand = random.randrange(no)

        # rand has a 'p' probability of being 0 <= rand < precision, thus this effectively
        # ensures True is returned only with probability p
        if 0 <= rand < precision:
            return True
        return False

    """
    Return a schedule to be used with simulated annealing of given length starting from length, 
    ending at 0, stepping by 1.

    :param int length: The length of the produced scheduled.
    """

    @staticmethod
    def generate_schedule(length):
        return {z: (length - z) for z in range(0, length + 1)}

    """
    :param Network net: The network to modify
    :param SimulationSettings sim: The settings to be used to simulate the network during reverse engineering
    :param List[Mutable] mutables: List of values which can be mutated during the optimisation process.
    :param List[Constraint] constraints: The list of constraints which the network must satisfy.
    :param Dict[float, float] schedule: The schedule required by the simulated annealing algorithm.
    """

    @staticmethod
    def find_closest_network(net, sim, mutables, constraints, schedule):
        mut_net = copy.deepcopy(net)

        # First, check whether network already satisfies constraints
        evalCurrent = ConstraintSatisfaction._evaluate_network(mut_net, sim, constraints)
        if evalCurrent <= 0:
            return mut_net

        # Current is the set of values the mutable variables will have -> dict has the value name as key, value as value
        current = mutables

        for t in range(1, len(schedule) - 1):
            T = schedule[t]

            mut_net.mutate(current)
            evalCurrent = ConstraintSatisfaction._evaluate_network(mut_net, sim, constraints)

            if T == 0 or (evalCurrent <= 0):
                return mut_net
            else:
                neighbour = ConstraintSatisfaction._generate_neighbour(mutables)

                mut_net.mutate(neighbour)
                evalNeighbour = ConstraintSatisfaction._evaluate_network(mut_net, sim, constraints)

                delta_e = evalCurrent - evalNeighbour

                # We want to minimise rather than maximise, so delta_e <= 0
                if delta_e <= 0:
                    current = neighbour
                else:
                    p = e ** (-delta_e / T)
                    if p > 0.000001:
                        if ConstraintSatisfaction._rand_bool(p):
                            current = neighbour

        return mut_net

    # endregion
