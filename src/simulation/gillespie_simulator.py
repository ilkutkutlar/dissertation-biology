from math import *
from random import *
from typing import List, Tuple, Dict
import numpy as np

import matplotlib.pyplot as plt

from models.network import Network

SimulationResults = List[Tuple[float, Dict[str, float]]]


class GillespieSimulator:

    @staticmethod
    def _calculate_r0(net):
        """
        Calculate the sum of all reactions rates in the given network
        :param Network net: Network
        """

        r0 = 0
        for reaction in net.reactions:
            t = reaction.rate(net.species)
            r0 += t

        return r0

    @staticmethod
    def _get_delta_time(r0):
        """
        Calculate the time after which the next random reaction will occur
        :param float r0: sum of all reaction rates
        :returns float of time for the next random reaction
        """

        s1 = random()  # To pick time
        epsilon = 0.001  # To avoid division by zero
        lam = (1 / (r0 + epsilon))
        return lam * pow(e, -lam * s1)

    @staticmethod
    def _apply_change_vector(state, change):
        """
        Adds a given change vector to the network's state vector
        :param Dict[str, float] state: Current network state
        :param Dict[str, float] change: Change vector
        :returns Dict[str, float] of new network state
        """

        ret = state.copy()
        for x in state:
            ret[x] = state[x] + change[x]
        return ret

    @staticmethod
    def _get_next_state(net, r0):
        """
        Return the next state of the network after a random reaction has occurred
        :param Network net: network for which to get next state
        :param float r0: total of reaction propensities
        :returns next network state
        """

        vj = GillespieSimulator._pick_next_reaction(net, r0)
        return GillespieSimulator._apply_change_vector(net.species, vj) if vj else net.species

    @staticmethod
    def _pick_weighted_random(items, probabilities):
        i = np.random.choice(len(items), 1, p=probabilities)
        return items[i[0]]

    @staticmethod
    def _pick_next_reaction(net, r0):
        """
        returns a Dict[str, float] representing the
        change vector of the reaction chosen randomly,
        which will happen next
        :param Network net: network for which to pick next reaction
        :param float r0: total reaction propensities
        :returns Dict[str, float] of change vector of picked reaction
        """

        propensities = []
        for reaction in net.reactions:
            try:
                div_result = reaction.rate(net.species) / r0
            except ZeroDivisionError:
                div_result = reaction.rate(net.species) / 1
            propensities.append(div_result)

        random_reaction = GillespieSimulator._pick_weighted_random(net.reactions, propensities)
        return random_reaction.change_vector(net.species)

    """
    Performs a Gillespie simulation of the given network in the given
    interval (dictated by the simulation setting given) and returns
    a list of results.
    :param Network net: to simulate
    :param SimulationSettings sim: for simulation
    :returns SimulationResults of the simulation
    """

    @staticmethod
    def simulate(net, sim):
        t = 0
        results = []

        while t <= int(sim.end_time):
            r0 = GillespieSimulator._calculate_r0(net)

            delta_time = GillespieSimulator._get_delta_time(r0)
            # Advance time
            t = t + delta_time
            # Apply one reaction chosen randomly
            net.species = GillespieSimulator._get_next_state(net, r0)

            results.append((t, net.species))

        return results

    """
    Visualises a given set of Gillespie simulation results where
    simulation properties are dictated by the given simulation settings
    object
    :param SimulationResults results: to be visualised
    :param SimulationSettings sim: for the visualisation
    """

    @staticmethod
    def visualise(results, sim):
        # plot results
        plt.figure()

        times = []
        plottings = {}

        # species: (species title, species name)
        for species in sim.plotted_species:
            plottings[species] = []

        for x in results:
            times.append(x[0])

            for species in sim.plotted_species:
                plottings[species].append(x[1][species])

        for species in sim.plotted_species:
            plt.plot(times, plottings[species], label=species)

        plt.xlabel("Time (s)")
        plt.ylabel("Concentration")
        plt.legend(loc=0)
        plt.title("Results")

        plt.draw()
        plt.show()
