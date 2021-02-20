import matplotlib.pyplot as plt
from scipy.integrate import odeint

from structured_results import StructuredResults


class OdeSimulator:

    @staticmethod
    def _dy_dt(y, t, net):
        """
        Calculate the change in the values of species of the network

        :param List[float] y: List of values
        :param int t: Not used
        :param Network net: The Network which acts as the context for the given values
        """

        changes = {s: 0 for s in net.species}

        # This is just y with each value labelled with its corresponding species name
        unpacked = {s: y[i] for i, s in enumerate(net.species)}

        for r in net.reactions:
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
    @staticmethod
    def simulate(net, sim):
        # Build the initial state
        y0 = [net.species[key] for key in net.species]

        # solve the ODEs
        solution = odeint(OdeSimulator._dy_dt, y0, sim.generate_time_space(), (net,))

        return solution

    """
    Visualise given results
    :param np.ndarray results: A two dimensional NumPy array containing results
        in the format where the ith array inside 'results' has the values
        for each species at time i. 
    """
    @staticmethod
    def visualise(net, sim, results):
        values = StructuredResults.label_results(results, net.species)

        plt.figure()

        for s in sim.plotted_species:
            plt.plot(sim.generate_time_space(), values[s], label=s)

        plt.xlabel("Time (s)")
        plt.ylabel("Concentration")
        plt.legend(loc=0)
        plt.title("Results")

        plt.draw()
        plt.show()
