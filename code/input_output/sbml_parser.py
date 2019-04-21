import libsbml

import helper
from models.formulae.custom_formula import CustomFormula
from models.network import Network
from models.reaction import Reaction


# 1. Core objects of libsbml:
# http://sbml.org/Software/libSBML/5.17.0/docs//python-api/group__core.html
# 2. Classes:
# http://sbml.org/Software/libSBML/5.17.0/docs//python-api/annotated.html


class SbmlParser:
    """
    Return dictionary of species in a given model
    :param Any model: A libsbml network model
    :returns Dict[str, float] of species where
        key: species id, value: initial concentration
    """

    @staticmethod
    def _get_species(model):
        species = {s.getId(): s.getInitialAmount() for s in model.getListOfSpecies()}
        return species

    """
    Return all defined symbols in the given model
    :param Any model: a libsbml network model
    :returns Dict[str, float] where key: symbol name, value: symbol value
    """

    @staticmethod
    def _get_symbols(model):
        symbols = {}

        """
         Both list of parameters and rules constitute symbols
         which may be used in the reactions. So, include all
         in a symbol table.
        """

        for param in model.getListOfParameters():
            if param.getConstant():
                symbols[param.getId()] = param.getValue()

        """
        Rules are different to parameters as they can contain symbols
        themselves, which can be the parameters parsed in the above loop.
        """

        for r in model.getListOfRules():
            val = helper.evaluate_ast(r.getMath(), symbols)

            if not val:
                return False

            symbols[r.getId()] = val

        for c in model.getListOfCompartments():
            symbols[c.getId()] = c.getSize()

        return symbols

    """
    Return all reactions in the given model
    :param Any model: a libsbml network model
    :returns List[Reaction] of model's reaction
    """

    @staticmethod
    def _get_reactions(model, time_multiplier):
        # Evaluate and store global parameters in a symbol table
        symbols = SbmlParser._get_symbols(model)
        if not symbols:
            return False

        reactions = []

        for x in model.getListOfReactions():
            rate_function = helper.ast_to_string(x.getKineticLaw().getMath().deepCopy())

            reactants = x.getListOfReactants()
            products = x.getListOfProducts()

            left = [y.getSpecies() for y in reactants]
            right = [y.getSpecies() for y in products]
            parameters = {p.getId(): p.getValue() for p in x.getKineticLaw().getListOfParameters()}

            sbo = x.getSBOTerm()

            # 179 -> Degradation
            # 183 -> Transcription
            # 184 -> Translation

            # if sbo == "179":
            #     r = CustomFormula(rate_function, parameters, symbols)
            # elif sbo == "183":
            #     r = CustomFormula(rate_function, parameters, symbols)
            # elif sbo == "184":
            #     r = CustomFormula(rate_function, parameters, symbols)
            # else:
            #     r = CustomFormula(rate_function, parameters, symbols)

            r = CustomFormula(rate_function, parameters, symbols, time_multiplier)
            reactions.append(Reaction(x.getName(), left, right, r))
        return reactions

    @staticmethod
    def _get_time_multipler(model):
        defs = model.getListOfUnitDefinitions()
        time = defs.get("time")
        time_multiplier = 1.0
        if time:
            time_multiplier = time.getListOfUnits().get(0).getMultiplier()

        return time_multiplier

    """
    Return a Network representing the SBML model in the given SBML file.
    :param str filename: Filename for SBML file
    :returns Network representing given filename
    """

    @staticmethod
    def parse(filename):
        net = Network()
        sbml = libsbml.SBMLReader()

        parsed = sbml.readSBML(filename)
        model = parsed.getModel()

        # Initialise species and their initial amounts
        net.species = SbmlParser._get_species(model)

        time_multipler = SbmlParser._get_time_multipler(model)
        # Parse reactions and create CustomReaction objects
        net.reactions = SbmlParser._get_reactions(model, time_multipler)

        if not net.reactions:
            return False

        return net
