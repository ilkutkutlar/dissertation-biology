from models.formulae.formula import Formula


class DegradationFormula(Formula):
    """
    :param float rate:
    :param str decaying_species:
    """

    def __init__(self, rate, decaying_species):
        self.rate = rate
        self.decaying_species = decaying_species

    def compute(self, state):
        return self.rate * state[self.decaying_species]

    def mutate(self, mutation):
        if mutation.variable_name == "rate":
            self.rate = mutation.current_value

    def get_params(self):
        return ["rate"]

    def get_formula_string(self):
        return "{}*{}".format(self.decaying_species, str(self.rate))

    def __str__(self):
        rate = str(self.rate)

        string = "Type: Degradation" + "\n"
        string += "Rate: " + rate + "\n"

        return string

    def str_variables(self):
        rate = str(self.rate)
        string = "Rate: " + rate

        return string
