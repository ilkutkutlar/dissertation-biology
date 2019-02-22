from typing import Callable, Tuple


class Constraint:
    species: str
    value_constraint: Callable[[float], bool]
    time_period: Tuple[float, float]
    pretty_print: str

    """
    :param str species: The name of the species for which the constraint applies
    :param Callable[[float], float] value_constraint: A function which, given the current value, evaluates how
        close/far it is from the desired value e.g. f = lambda v: v - 100, places a constraint for value
        to be below 100. If v = 120, then this will give a result which is > 0, indicating that the constraint
        has not been satisfied.
    :param Tuple[float, float] time_period: defines the time period for which the given value constraint
        be satisfied
    """

    def __init__(self, species: str, value_constraint: Callable[[float], float], time_period: Tuple[float, float]):
        self.species = species
        self.value_constraint = value_constraint
        self.time_period = time_period

    def __str__(self):
        return self.pretty_print
