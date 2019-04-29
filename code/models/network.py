from constraint_satisfaction.mutable import ReactionMutable, VariableMutable, RegulationMutable, GlobalParameterMutable
from models.input_gate import InputGate
from models.regulation import Regulation


class Network:

    def __init__(self):
        self.species = dict()  # of Dict[str, float]
        self.reactions = list()  # of Reaction
        self.symbols = dict()

    """
    Change species concentrations of network using a change vector
    :param Dict[str, float] change: key: species name, value: concentration change by
    """

    def apply_change_vector(self, change):
        for x in change:
            self.species[x] += change[x]

    """
    Mutate species and reactions of the network
    :param Dict[str, Tuple[float, str]] mutations: key: mutable name, value: (new value, reaction name)
    """

    def mutate(self, mutations):
        for m in mutations:
            if isinstance(m, ReactionMutable):
                r = self.get_reaction_by_name(m.reaction_name)
                r.rate_function.mutate(m)
            elif isinstance(m, GlobalParameterMutable):
                self.symbols[m.variable_name] = m.current_value
            elif isinstance(m, VariableMutable):
                self.species[m.variable_name] = m.current_value
            elif isinstance(m, RegulationMutable):
                self._mutate_regulation(m)

    def _mutate_regulation(self, m):
        # Find the reaction this RegulationMutable refers to
        # If it doesn't exist, maybe_reaction will return None
        maybe_reaction = \
            list(filter(lambda x: x.name == m.reaction_name, self.reactions))

        if maybe_reaction:  # Reaction exists
            # Get reaction's TranscriptionFormula
            transcription = maybe_reaction[0].rate_function

            if m.is_installed:
                # The regulator species that needs to be installed
                the_regulator = m.possible_regulators[m.current_regulator]
                # The regulation object which corresponds to this regulator
                the_regulation = transcription.get_regulation(the_regulator)

                if the_regulation:  # Regulation already installed, just change the parameters.
                    the_regulation.reg_type = m.possible_reg_types[m.current_reg_type]
                    the_regulation.k = m.k_variable.current_value
                else:  # Regulation not installed, install it now.
                    if len(transcription.regulators) == 0:
                        # No regulators have been installed yet, so set common regulation parameters
                        transcription.set_regulation(m.hill_coeff, [], InputGate.AND)

                    new_reg = Regulation(m.possible_regulators[m.current_regulator],
                                         transcription.transcribed_species,
                                         m.possible_reg_types[m.current_reg_type],
                                         m.k_variable.current_value)

                    transcription.regulators.append(new_reg)

            else:
                the_regulation = transcription.get_regulation(m.current_regulator)
                if the_regulation:
                    transcription.regulators.remove(the_regulation)

    """
    Return reaction with given name
    :param str name: Name of reaction
    :returns Reaction if found, None if not
    """

    def get_reaction_by_name(self, name):
        t = list(filter(lambda r: r.name == name, self.reactions))
        if t:
            return t[0]
        else:
            return None

    def __str__(self):
        ret = "\nSpecies: \n"
        for x in self.species:
            ret += "    " + x + ": " + str(self.species[x]) + "\n"

        ret += "\nReactions: \n"
        for x in self.reactions:
            ret += "    " + str(x) + "\n"

        return ret

    def str_variables(self):
        ret = "\n== Species == \n\n"
        for x in self.species:
            ret += x + ": " + str(self.species[x]) + "\n"

        if self.symbols:
            ret += "\n== Symbols == \n\n"
            for s in self.symbols:
                ret += s + ": " + str(self.symbols[s]) + "\n"

        ret += "\n== Reactions == \n\n"
        for x in self.reactions:
            string = x.str_variables()
            if len(string) != 0:
                ret += string + "\n"

        return ret
