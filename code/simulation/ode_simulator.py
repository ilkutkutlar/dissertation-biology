import matplotlib.pyplot as plt
from scipy.integrate import odeint

from models.simulation_settings import SimulationSettings
from structured_results import StructuredResults


class OdeSimulator:
    """
    :param Network net:
    :param SimulationSettings sim:
    """

    def __init__(self, net, sim):
        self.net = net
        self.sim = sim

        # time grid -> The time space for which the equations will be solved
        self.time_space = sim.generate_time_space()

    def _dy_dt(self, y, t):
        """
        Calculate the change in the values of species of the network

        :param List[float] y: List of values
        :param int t: Not used
        :param Network net: The Network which acts as the context for the given values
        """

        changes = {s: 0 for s in self.net.species}

        # This is just y with each value labelled with its corresponding species name
        unpacked = {s: y[i] for i, s in enumerate(self.net.species)}

        for r in self.net.reactions:
            rate = r.rate(unpacked)

            if r.left:
                for x in r.left:
                    changes[x] -= rate

            if r.right:
                for x in r.right:
                    changes[x] += rate

        return list(changes.values())

    """
    Simulate class network and return results
    :returns np.ndarray of simulation results
    """

    def simulate(self):
        # Build the initial state
        y0 = [self.net.species[key] for key in self.net.species]

        # solve the ODEs
        solution = odeint(self._dy_dt, y0, self.time_space)

        return solution

    """
    Visualise given results
    :param np.ndarray results: A two dimensional NumPy array containing results
        in the format where the ith array inside 'results' has the values
        for each species at time i. 
    """

    def visualise(self, results):
        values = StructuredResults.label_results(results, self.net.species)

        plt.figure()

        for s in self.sim.plotted_species:
            plt.plot(self.time_space, values[s], label=s)

        plt.xlabel("Time (s)")
        plt.ylabel("Concentration")
        plt.legend(loc=0)
        plt.title("Results")

        plt.draw()
        plt.show()
