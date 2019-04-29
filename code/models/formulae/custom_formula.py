from libsbml._libsbml import parseL3Formula

import helper
from models.formulae.formula import Formula


class CustomFormula(Formula):
    """
    :param str rate_function:
    :param Dict[str, float] parameters:
    :param Network net:
    """

    def __init__(self, rate_function, parameters, net, time_multiplier):
        self.rate_function = rate_function
        self.net = net
        self.parameters = parameters  # Local parameters of this reaction
        self.time_multiplier = time_multiplier

    def compute(self, state):
        # rate_function is str, use this function to convert to AST object.
        rate_function_ast = parseL3Formula(self.get_formula_string())
        eval_result = helper.safe_evaluate_ast(rate_function_ast, self.rate_function,
                                               species=state, symbols=self.net.symbols,
                                               parameters=self.parameters)
        return eval_result / self.time_multiplier

    def mutate(self, mutation):
        self.parameters.update({mutation.variable_name: mutation.current_value})

    def get_params(self):
        return list(self.parameters.keys())

    def get_formula_string(self):
        return str(self.rate_function).replace("**", "^")

    def __str__(self):
        rate_function_ast = str(self.rate_function)

        params = ""
        for p in self.parameters:
            params += "\n       • " + p + ": " + str(self.parameters[p])

        string = "Type: Custom Reaction" + "\n"
        string += "Rate function: " + rate_function_ast + "\n\n"
        string += "== Parameters == \n"
        string += params

        return string

    def str_variables(self):
        params = ""
        if self.parameters:
            for p in self.parameters:
                params += p + ": " + str(self.parameters[p]) + "\n"

        return params
