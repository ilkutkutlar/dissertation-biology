from models.formulae.formula import Formula
from models.input_gate import InputGate
from models.reg_type import RegType

"""
Based on an ODE model and uses the Hill equation to calculate
    the promoter strength when being regulated by a TF:

    Hill equation for repressor bindings:
    beta * ( 1 / ( 1 + ([TF]/K)^n) )

    Hill equation for activator bindings:
    beta * ([TF]^n / (K^n + [TF]^n) )

    beta    : Maximal transcription rate (promoter strength)
    [TF]    : The concentration of Transcription Factor that is regulating this promoter
    K       : Dissociation constant, the probability that the TF will dissociate from the
                binding site it is now bound to. Equal to Kb/Kf where Kf = rate of TF binding and
                Kb = rate of TF unbinding.
    n       : Hill coefficient. Assumed to be 1 by default.

    Source: An introduction to systems biology : design principles of biological circuits, Uri Alon
    Previous Source: https://link.springer.com/chapter/10.1007/978-94-017-9514-2_5
"""


class TranscriptionFormula(Formula):
    """
    :param float rate:
    :param str transcribed_species:
    """

    def __init__(self, rate,
                 transcribed_species):
        self.rate = rate
        self.transcribed_species = transcribed_species

        self.hill_coeff = None
        self.regulators = None
        self.input_gate = None

    def set_regulation(self, hill_coeff, regulators, input_gate=InputGate.NONE):
        self.hill_coeff = hill_coeff
        self.regulators = regulators
        self.input_gate = input_gate

    @staticmethod
    def _hill_activator(tf, n, k):
        """
        :param float tf: transcription factor concentration
        :param float n: Hill coefficient
        :param float k: Dissociation constant
        :returns float of regulation factor
        """

        a = pow(tf, n)
        b = pow(k, n) + pow(tf, n)
        return a / b

    @staticmethod
    def _hill_repressor(tf, n, k):
        """
        :param float tf: transcription factor concentration
        :param float n: Hill coefficient
        :param float k: Dissociation constant
        :returns float of regulation factor
        """

        c = 1 + pow(tf / k, n)
        return 1 / c

    @staticmethod
    def _hill_or_gate(one, two, n, state):
        """
         Based on: https://www.pnas.org/content/pnas/100/21/11980.full.pdf
        :param Regulation one: first regulation
        :param Regulation two: second regulation
        :param float n: Hill coefficient
        :param Dict[str, float] state: Network state
        :return: float result of running hill equation with the given parameters
        """

        a = (pow(state[one.from_gene] / one.k, n))
        b = (pow(state[two.from_gene] / two.k, n))
        c = (1 + a + b)

        if one.reg_type == RegType.ACTIVATION and two.reg_type == RegType.ACTIVATION:
            return (a + b) / c
        elif one.reg_type == RegType.ACTIVATION and two.reg_type == RegType.REPRESSION:
            return (a + 1) / c
        elif one.reg_type == RegType.REPRESSION and two.reg_type == RegType.ACTIVATION:
            return (1 + b) / c
        else:  # Repression, repression
            return 1 / c

    @staticmethod
    def _hill_and_gate(one, two, n, state):
        """
        Based on: https://www.pnas.org/content/pnas/100/21/11980.full.pdf
        :param Regulation one: first regulation
        :param Regulation two: second regulation
        :param float n: Hill coefficient
        :param Dict[str, float] state: Network state
        :return: float result of running hill equation with the given parameters
        """

        one_concent = state[one.from_gene]
        two_concent = state[two.from_gene]

        one_act = TranscriptionFormula._hill_activator(one_concent, n, one.k)
        one_rep = TranscriptionFormula._hill_repressor(one_concent, n, one.k)

        two_act = TranscriptionFormula._hill_activator(two_concent, n, two.k)
        two_rep = TranscriptionFormula._hill_repressor(two_concent, n, two.k)

        if one.reg_type == RegType.ACTIVATION and two.reg_type == RegType.ACTIVATION:
            return one_act * two_act
        elif one.reg_type == RegType.ACTIVATION and two.reg_type == RegType.REPRESSION:
            return one_act * two_rep
        elif one.reg_type == RegType.REPRESSION and two.reg_type == RegType.ACTIVATION:
            return one_rep * two_act
        else:  # Repression, repression
            return one_rep * two_rep

    def compute(self, state):
        # Protein regulates mRNA
        if not self.regulators:
            h = 1
        elif len(self.regulators) == 1:
            h = self._h_single(state)
        elif len(self.regulators) == 2:
            h = self._h_combinatorial(state)
        else:
            h = 0

        return h * self.rate

    """
    Return regulation strength when species is regulated by a single TF
    """

    def _h_single(self, state):
        reg = self.regulators[0]
        reg_concent = state[reg.from_gene]

        if reg.reg_type == RegType.ACTIVATION:
            h = self._hill_activator(reg_concent, self.hill_coeff, reg.k)
        else:
            h = self._hill_repressor(reg_concent, self.hill_coeff, reg.k)

        return h

    """
    Return regulation strength when species is regulated by multiple TFs
    """

    def _h_combinatorial(self, state):
        one = self.regulators[0]
        two = self.regulators[1]

        if self.input_gate == InputGate.AND:
            h = self._hill_and_gate(one, two, self.hill_coeff, state)
        elif self.input_gate == InputGate.OR:
            h = self._hill_or_gate(one, two, self.hill_coeff, state)
        else:
            h = 1

        return h

    def mutate(self, mutation):
        for m in mutation:
            if m == "rate":
                self.rate = mutation[m][0]
            else:  # m == "hill_coeff":
                self.hill_coeff = mutation[m][0]

    def get_params(self):
        return ["rate", "hill_coeff"]

    def __str__(self):
        trans_rate = str(self.rate)
        hill_coeff = str(self.hill_coeff)

        string = "Type: Transcription" + "\n"

        string += "Rate: " + trans_rate + "\n\n"

        string += "== Regulation == \n"
        string += "Hill coefficient: " + hill_coeff + "\n\n"

        if self.regulators:
            for r in self.regulators:
                from_gene = r.from_gene
                sign = " ⭢ " if r.reg_type == RegType.ACTIVATION else " ⊣ "
                to_gene = r.to_gene
                string += from_gene + sign + to_gene + "\n"
                string += "    - K: " + str(r.k) + "\n\n"
        else:
            string += "Not regulated"

        return string
