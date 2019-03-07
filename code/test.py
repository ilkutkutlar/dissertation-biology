from math import log, e

from models.formulae.degradation_formula import DegradationFormula
from models.formulae.transcription_formula import TranscriptionFormula
from models.formulae.translation_formula import TranslationFormula
from models.input_gate import InputGate
from models.network import Network
from models.reaction import Reaction
from models.reg_type import RegType
from models.regulation import Regulation
from models.simulation_settings import SimulationSettings
from constraint_satisfaction.constraint import Constraint
from constraint_satisfaction.mutable import RegulationMutable, VariableMutable
from constraint_satisfaction.constraint_satisfaction import ConstraintSatisfaction
from simulation.ode_simulator import OdeSimulator


def get_repressilator():
    # region Constants

    ps_active = 0.5  # Promoter strength (active)
    ps_repr = 5 * (10 ** -4)  # Promoter strength (repressed)
    transcription_rate_active = ps_active * 60
    transcription_rate_repr = ps_repr * 60

    # Decay-related values
    mRNA_half_life = 2
    protein_half_life = 10
    mRNA_decay_rate = log(2, e) / mRNA_half_life
    protein_decay_rate = log(2, e) / protein_half_life

    # Translation-related values
    translation_efficiency = 19.97
    translation_rate = translation_efficiency * mRNA_decay_rate

    # Other values
    hill_coeff = 2  # Hill coefficient
    Km = 40  # Activation coefficient

    # Derived values

    # Active transcription rate (rescaled?)
    alpha = transcription_rate_active * translation_efficiency * protein_half_life / (log(2, e) * Km)
    # Repressed transcription rate (rescaled?)
    alpha0 = transcription_rate_repr * translation_efficiency * protein_half_life / (log(2, e) * Km)
    # Translation rate
    beta = protein_decay_rate / mRNA_decay_rate

    # endregion

    species = {"tetr_mrna": 80, "cl_mrna": 50,
               "laci_p": 10, "cl_p": 10, "tetr_p": 10, "laci_mrna": 100}

    laci_reg = Regulation("cl_p", "laci_mrna", RegType.REPRESSION, Km)
    tetr_reg = Regulation("laci_p", "tetr_mrna", RegType.REPRESSION, Km)
    cl_reg = Regulation("tetr_p", "cl_mrna", RegType.REPRESSION, Km)

    laci_trans = TranscriptionFormula(alpha, "laci_mrna")
    laci_trans.set_regulation(hill_coeff, [laci_reg])

    tetr_trans = TranscriptionFormula(alpha, "tetr_mrna")
    tetr_trans.set_regulation(hill_coeff, [tetr_reg])

    cl_trans = TranscriptionFormula(alpha, "cl_mrna")
    cl_trans.set_regulation(hill_coeff, [cl_reg])

    reactions = [Reaction("laci_trans", [], ["laci_mrna"], laci_trans),
                 Reaction("tetr_trans", [], ["tetr_mrna"], tetr_trans),
                 Reaction("cl_trans", [], ["cl_mrna"], cl_trans),

                 Reaction("laci_mrna_deg", ["laci_mrna"], [], DegradationFormula(mRNA_decay_rate, "laci_mrna")),
                 Reaction("tetr_mrna_deg", ["tetr_mrna"], [], DegradationFormula(mRNA_decay_rate, "tetr_mrna")),
                 Reaction("cl_mrna_deg", ["cl_mrna"], [], DegradationFormula(mRNA_decay_rate, "cl_mrna")),

                 Reaction("laci_p_trans", ["laci_mrna"], ["laci_p"], TranslationFormula(beta, "laci_mrna")),
                 Reaction("tetr_p_trans", ["tetr_mrna"], ["tetr_p"], TranslationFormula(beta, "tetr_mrna")),
                 Reaction("cl_p_trans", ["cl_mrna"], ["cl_p"], TranslationFormula(beta, "cl_mrna")),

                 Reaction("laci_p_deg", ["laci_p"], [], DegradationFormula(protein_decay_rate, "laci_p")),
                 Reaction("tetr_p_deg", ["tetr_p"], [], DegradationFormula(protein_decay_rate, "tetr_p")),
                 Reaction("cl_p_deg", ["cl_p"], [], DegradationFormula(protein_decay_rate, "cl_p"))]

    repressilator = Network()
    repressilator.species = species
    repressilator.reactions = reactions

    return repressilator


def get_test_network1():
    species = {"px": 100, "py": 100, "pz": 30, "x": 100, "y": 25, "z": 20}

    x_trans = TranscriptionFormula(5, "x")

    y_trans = TranscriptionFormula(60, "y")
    y_trans.set_regulation(1, [Regulation("px", "y", RegType.REPRESSION, 40)])

    z_trans = TranscriptionFormula(20, "z")
    z_trans.set_regulation(2, [Regulation("py", "z", RegType.ACTIVATION, 40)])

    reactions = [Reaction("x_trans", [], ["x"], x_trans),
                 Reaction("y_trans", [], ["y"], y_trans),
                 Reaction("z_trans", [], ["z"], z_trans),

                 Reaction("x_deg", ["x"], [], DegradationFormula(0.01, "x")),
                 Reaction("y_deg", ["y"], [], DegradationFormula(0.01, "y")),
                 Reaction("z_deg", ["z"], [], DegradationFormula(0.1, "z")),

                 Reaction("px_deg", ["px"], [], DegradationFormula(0.01, "px")),
                 Reaction("py_deg", ["py"], [], DegradationFormula(0.01, "py")),
                 Reaction("pz_deg", ["pz"], [], DegradationFormula(0.01, "pz")),

                 Reaction("px_translation", [], ["px"], TranslationFormula(0.2, "x")),
                 Reaction("py_translation", [], ["py"], TranslationFormula(5, "y")),
                 Reaction("pz_translation", [], ["pz"], TranslationFormula(1, "z"))]

    net1: Network = Network()
    net1.species = species
    net1.reactions = reactions

    return net1


def get_test_network2():
    species = {"px": 100, "py": 100, "pz": 30, "x": 25, "y": 25, "z": 25}

    x_trans = TranscriptionFormula(5, "x")

    y_trans = TranscriptionFormula(5, "y")

    z_trans = TranscriptionFormula(5, "z")
    z_trans.set_regulation(2,
                           [Regulation("py", "z", RegType.ACTIVATION, 40),
                            Regulation("px", "z", RegType.ACTIVATION, 80)],
                           InputGate.AND)

    reactions = [Reaction("x_trans", [], ["x"], x_trans),
                 Reaction("y_trans", [], ["y"], y_trans),
                 Reaction("z_trans", [], ["z"], z_trans),

                 # Reaction("x_deg", ["x"], [], DegradationFormula(0.01, "x")),
                 # Reaction("y_deg", ["y"], [], DegradationFormula(0.01, "y")),
                 # Reaction("z_deg", ["z"], [], DegradationFormula(0.01, "z")),

                 # Reaction("px_deg", ["px"], [], DegradationFormula(0.01, "px")),
                 # Reaction("py_deg", ["py"], [], DegradationFormula(0.01, "py")),
                 # Reaction("pz_deg", ["pz"], [], DegradationFormula(0.01, "pz")),

                 Reaction("px_translation", [], ["px"], TranslationFormula(0.2, "x")),
                 Reaction("py_translation", [], ["py"], TranslationFormula(5, "y")),
                 Reaction("pz_translation", [], ["pz"], TranslationFormula(1, "z"))]

    net2 = Network()
    net2.species = species
    net2.reactions = reactions

    return net2


def get_large_network():
    species = {"mA": 0, "pA": 0,
               "mB": 50, "pB": 0,
               "mC": 30, "pC": 0,
               "mD": 45, "pD": 0,
               "mE": 20, "pE": 0,
               "mF": 35, "pF": 0,
               "mG": 35, "pG": 0,
               "mH": 55, "pH": 0,
               "mI": 75, "pI": 0,
               "mJ": 85, "pJ": 0,
               "mX": 110, "pX": 0,
               "mY": 30, "pY": 0,
               "mZ": 140, "pZ": 0}

    reactions = []

    n = 2
    gate = InputGate.AND
    k = 40

    a_trans = TranscriptionFormula(16, "mA")
    a_trans.set_regulation(n, [Regulation("pB", "mA", RegType.REPRESSION, k)])

    b_trans = TranscriptionFormula(17, "mB")
    b_trans.set_regulation(n, [Regulation("pE", "mB", RegType.ACTIVATION, k)])

    c_trans = TranscriptionFormula(5, "mC")
    c_trans.set_regulation(n, [Regulation("pY", "mC", RegType.REPRESSION, k)])

    d_trans = TranscriptionFormula(14, "mD")
    d_trans.set_regulation(n, [Regulation("pD", "mD", RegType.ACTIVATION, k),
                               Regulation("pB", "mD", RegType.REPRESSION, k)])

    e_trans = TranscriptionFormula(35, "mE")
    e_trans.set_regulation(n, [Regulation("pB", "mE", RegType.REPRESSION, k)])

    f_trans = TranscriptionFormula(18, "mF")
    f_trans.set_regulation(n,
                           [Regulation("pF", "mF", RegType.REPRESSION, k),
                            Regulation("pG", "mF", RegType.ACTIVATION, k)],
                           input_gate=gate)

    g_trans = TranscriptionFormula(7, "mG")
    g_trans.set_regulation(n, [Regulation("pE", "mG", RegType.REPRESSION, k)])

    h_trans = TranscriptionFormula(20, "mH")

    i_trans = TranscriptionFormula(27, "mI")
    i_trans.set_regulation(n, [Regulation("pH", "mI", RegType.ACTIVATION, k)])

    j_trans = TranscriptionFormula(24, "mJ")
    j_trans.set_regulation(n, [Regulation("pI", "mJ", RegType.ACTIVATION, k),
                               Regulation("pH", "mJ", RegType.ACTIVATION, k)],
                           input_gate=gate)

    x_trans = TranscriptionFormula(29, "mX")
    x_trans.set_regulation(n, [Regulation("pZ", "mX", RegType.REPRESSION, k)])

    y_trans = TranscriptionFormula(21, "mY")
    y_trans.set_regulation(n, [Regulation("pB", "mY", RegType.ACTIVATION, k)])

    z_trans = TranscriptionFormula(8, "mZ")
    z_trans.set_regulation(n, [Regulation("pX", "mZ", RegType.ACTIVATION, k)])

    reactions = [Reaction("a_trans", [], ["mA"], a_trans),
                 Reaction("b_trans", [], ["mB"], b_trans),
                 Reaction("c_trans", [], ["mC"], c_trans),
                 Reaction("d_trans", [], ["mD"], d_trans),
                 Reaction("e_trans", [], ["mE"], e_trans),
                 Reaction("f_trans", [], ["mF"], f_trans),
                 Reaction("g_trans", [], ["mG"], g_trans),
                 Reaction("h_trans", [], ["mH"], h_trans),
                 Reaction("i_trans", [], ["mI"], i_trans),
                 Reaction("j_trans", [], ["mJ"], j_trans),
                 Reaction("x_trans", [], ["mX"], x_trans),
                 Reaction("y_trans", [], ["mY"], y_trans),
                 Reaction("z_trans", [], ["mZ"], z_trans)]

    deg_rates_mrna = [0.095, 0.014, 0.098, 0.043, 0.091, 0.047, 0.074, 0.022, 0.085, 0.092, 0.028, 0.038, 0.045]
    deg_rates_protein = [0.035, 0.093, 0.075, 0.025, 0.045, 0.064, 0.068, 0.084, 0.03, 0.094, 0.066, 0.053, 0.084]
    all_deg_rates = deg_rates_mrna + deg_rates_protein
    translation_rates = [0.5, 8.8, 7.9, 2.7, 1.5, 3.6, 1.8, 9.5, 8.0, 6.4, 7.4, 1.6, 6.5]

    for s, r in zip(species.keys(), all_deg_rates):
        reactions.append(Reaction(s + "_deg", [s], [], DegradationFormula(r, s)))

    for i, r in zip(range(1, 26, 2), translation_rates):
        spec = list(species.keys())[i]
        mrna = list(species.keys())[i - 1]
        reactions.append(Reaction(spec + "_translation", [], [spec], TranslationFormula(r, mrna)))

    net = Network()
    net.species = species
    net.reactions = reactions
    return net

if __name__ == '__main__':
    # repressilator_sim = SimulationSettings(0, 10 * 60, 1000, ["laci_p", "tetr_p", "cl_p"])
    #
    # net = get_test_network1()
    # net1_sim = SimulationSettings(0, 100, 100, ["x", "y", "z"])
    #
    # mutables = [RegulationMutable("y_trans", ["px", "py", "pz"], VariableMutable("k", 1, 50, 1),
    #                               [RegType.ACTIVATION, RegType.REPRESSION], True)]
    # constraints = [Constraint("y", lambda x: x - 50, (20, 40))]
    # schedule = ReverseEngineering.generate_schedule(100)
    #
    # n = ReverseEngineering.find_network(net, net1_sim, mutables, constraints, schedule)
    #
    # print(n.get_reaction_by_name("y_trans"))
    # OdeSimulator.visualise(n, net1_sim, OdeSimulator.simulate(n, net1_sim))
    get_large_network()