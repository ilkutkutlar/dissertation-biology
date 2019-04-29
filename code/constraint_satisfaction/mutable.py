from models.reg_type import RegType


class VariableMutable:
    """
            :param float lower_bound, upper_bound: defines the interval of values to be tried for this parameter.
            :param float increments: increments define the step between lower_bound & upper_bound,
                e.g. l = 10, u = 11, increment = 0.5 would produce 10, 10.5 and 11 as the values to be tried for this parameter.
        """

    def __init__(self, variable_name, lower_bound, upper_bound, increments):
        self.variable_name = variable_name
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.increments = increments
        self.current_value = self.lower_bound

    def is_next(self):
        if self.current_value + self.increments > self.upper_bound:
            return False
        else:
            return True

    def next(self):
        if self.is_next():
            self.current_value += self.increments
            return True
        else:
            return False

    def __str__(self):
        lo = str(self.lower_bound)
        hi = str(self.upper_bound)
        step = str(self.increments)
        return "{}: ({} to {}) step: {}".format(self.variable_name, lo, hi, step)


class ReactionMutable(VariableMutable):
    """
    :param str reaction_name: If the parameter is defined in a reaction, this is the reaction_name where
                the parameter is. Else, it is empty string ("")
    """

    def __init__(self, variable_name, lower_bound, upper_bound, increments, reaction_name):
        super().__init__(variable_name, lower_bound, upper_bound, increments)
        self.reaction_name = reaction_name

    def __str__(self):
        lo = str(self.lower_bound)
        hi = str(self.upper_bound)
        step = str(self.increments)
        return "{}: ({} to {}) step: {} in {}".format(self.variable_name, lo, hi, step, self.reaction_name)


class RegulationMutable:
    """
    :param str reaction_name: The name of the reaction which can potentially do regulation
    :param List[str] possible_regulators: The list of species which this reaction can potentially be regulated by
    :param VariableMutable k_variable: k variable mutable associated with this regulation
    :param List[RegType] possible_reg_types: All possible regulation types accepted
    :param bool is_installed: Whether this regulation is installed in the network
    """

    def __init__(self, reaction_name, possible_regulators, k_variable, possible_reg_types, is_installed, hill_coeff):
        self.reaction_name = reaction_name
        self.possible_regulators = possible_regulators
        self.possible_reg_types = possible_reg_types
        self.k_variable = k_variable

        self.hill_coeff = hill_coeff
        self.is_installed = is_installed
        self.current_regulator = 0 if possible_regulators else None
        self.current_reg_type = 0 if possible_reg_types else None

    def is_next(self):
        if not self.is_installed:
            return True
        else:
            if self.k_variable.next():
                return True
            else:
                if self.current_reg_type < len(self.possible_reg_types):
                    return True
                else:
                    if self.current_regulator < len(self.possible_regulators):
                        return True
                    else:
                        return False

    def next(self):
        if not self.is_installed:
            self.is_installed = True
            return True
        else:
            # for x in to_species:
            #   for y in reg_types:
            #       for z in k:

            if self.k_variable.next():
                self.k_variable.next()
                return True
            else:
                if self.current_reg_type < len(self.possible_reg_types) - 1:
                    self.current_reg_type += 1
                    return True
                else:
                    if self.current_regulator < len(self.possible_regulators) - 1:
                        self.current_regulator += 1
                        return True
                    else:
                        return False

    def __str__(self):
        # return "{}: ({} to {}) step: {}".format(self.variable_name, lo, hi, step)

        # self.reaction_name = reaction_name
        # self.possible_regulators = possible_regulators
        # self.possible_reg_types = possible_reg_types
        # self.k_variable = k_variable

        regulators = "{"
        for r in self.possible_regulators:
            regulators += r + ", "
        regulators = regulators[0:len(regulators) - 2]
        regulators += "}"

        reg_types = "{"
        for r in self.possible_reg_types:
            reg_types += "Act." if r == RegType.ACTIVATION else "Rep."
            reg_types += ", "
        reg_types = reg_types[0:len(reg_types) - 2]
        reg_types += "}"

        return "{}: regulated by {} with {} \n    with {}". \
            format(self.reaction_name, regulators, reg_types, str(self.k_variable))


class GlobalParameterMutable(VariableMutable):
    def __init__(self, variable_name, lower_bound, upper_bound, increments):
        super().__init__(variable_name, lower_bound, upper_bound, increments)
