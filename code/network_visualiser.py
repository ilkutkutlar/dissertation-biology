import networkx as nx
import matplotlib.pyplot as plt
from PyQt5.QtGui import QImage
from graphviz import Digraph

from matplotlib.patches import ArrowStyle

from models.formulae.degradation_formula import DegradationFormula
from models.formulae.transcription_formula import TranscriptionFormula
from models.formulae.translation_formula import TranslationFormula
from models.network import Network
from models.reaction import Reaction
from models.reg_type import RegType
from models.regulation import Regulation


class NetworkVisualiser:

    @staticmethod
    def _network_to_reaction_graphviz(net):
        g = Digraph(format='png', engine='neato')

        for s in net.species:
            g.node(s, s)

        for r in net.reactions:
            if isinstance(r.rate_function, TranscriptionFormula):
                if r.rate_function.regulators:
                    for reg in r.rate_function.regulators:
                        arrow = "normal" if reg.reg_type == RegType.ACTIVATION else "tee"
                        g.edge(reg.from_gene, reg.to_gene, arrowhead=arrow)

        return g

    @staticmethod
    def _network_to_gene_graphviz(net):
        g = Digraph(format='png', engine='neato')

        genes = NetworkVisualiser._get_network_genes(net)

        for gene in genes:
            name = NetworkVisualiser._get_gene_name(gene)
            label = NetworkVisualiser._get_gene_label(gene)
            g.node(name, label)

        for r in NetworkVisualiser._get_regulated_reactions(net):
            for regulator in r.rate_function.regulators:
                # TODO: Check whether it found something!
                regulating_gene = list(filter(lambda x: x[1] == regulator.from_gene, genes))[0]
                regulating_gene_name = NetworkVisualiser._get_gene_name(regulating_gene)

                regulated_gene = list(filter(lambda x: x[0] == regulator.to_gene, genes))[0]
                regulated_gene_name = NetworkVisualiser._get_gene_name(regulated_gene)

                arrow = "normal" if regulator.reg_type == RegType.ACTIVATION else "tee"
                g.edge(regulating_gene_name, regulated_gene_name, arrowhead=arrow)

        return g

    @staticmethod
    def _get_gene_name(gene):
        return gene[0] + gene[1]

    @staticmethod
    def _get_gene_label(gene):
        return gene[1]

    @staticmethod
    def _get_network_genes(net):
        genes = []

        for r in net.reactions:
            if isinstance(r.rate_function, TranslationFormula):
                f = r.rate_function
                mrna = f.mrna_species
                protein = r.right[0]
                genes.append((mrna, protein))

        return genes

    @staticmethod
    def _get_regulated_reactions(net):
        regulated_reactions = []
        for r in net.reactions:
            if isinstance(r.rate_function, TranscriptionFormula):
                if r.rate_function.regulators:
                    regulated_reactions.append(r)
        return regulated_reactions

    @staticmethod
    def visualise(net, network_type):
        if network_type == "reaction":
            g = NetworkVisualiser._network_to_reaction_graphviz(net)
        else:
            g = NetworkVisualiser._network_to_gene_graphviz(net)

        g.render("temp")
        im = QImage("temp.png")
        return im
