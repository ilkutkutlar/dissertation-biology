from PyQt5.QtWidgets import QComboBox, QGridLayout, QCheckBox

from ui.gene_presenter import GenePresenter


def make_species_combo():
    combo = QComboBox()
    for x in GenePresenter.get_instance().get_species():
        combo.addItem(x)
    return combo


def make_species_checkboxes_layout():
    row = 0  # Row number to place the next species
    left = True  # Indicates that the next species must be placed to the left
    g = QGridLayout()

    for x in GenePresenter.get_instance().get_species():
        col = 1 if left else 2  # Column number depending on variable "left"
        g.addWidget(QCheckBox(x), row, col)

        # Switch to next row after adding species to right
        if not left:
            row += 1

        # Switch sides each time
        left = not left

    return g
