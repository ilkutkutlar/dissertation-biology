import numpy as np


class SimulationSettings:
    """
    :param float start_time: of simulation
    :param float end_time: of simulation
    :param int precision: how many data points in the given time period
    :param List[str] plotted_species: Which species to plot in the visualisation
    """

    def __init__(self, start_time, end_time, precision, plotted_species):
        self.plotted_species = plotted_species
        self.start_time = start_time
        self.end_time = end_time
        self.precision = precision

    """
    Return time space using the simulation settings
    """

    def generate_time_space(self):
        return np.linspace(self.start_time, self.end_time, self.precision)
