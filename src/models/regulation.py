from models.reg_type import RegType


class Regulation:
    def __init__(self, from_gene, to_gene, reg_type, k):
        self.from_gene = from_gene
        self.to_gene = to_gene
        self.reg_type = reg_type
        self.k = k

    def __str__(self):
        sign = " ⟶ " if self.reg_type == RegType.ACTIVATION else " ⊣ "
        return "Reg: " + self.from_gene + sign + self.to_gene
