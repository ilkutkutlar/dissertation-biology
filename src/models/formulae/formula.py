from abc import ABC, abstractmethod


class Formula(ABC):
    """
    Return the result of computing the formula.
    :param Dict[str, float] Network state: key: species name, value: concentration
    :returns float of result
    """

    @abstractmethod
    def compute(self, state):
        pass

    """
    Change value of given variables in the formula
    :param Dict[str, Tuple[float, str]] mutation: dictionary of variables to mutate
    """

    @abstractmethod
    def mutate(self, mutation):
        pass

    @abstractmethod
    def get_params(self):
        pass

    @staticmethod
    def get_formula_string():
        pass
