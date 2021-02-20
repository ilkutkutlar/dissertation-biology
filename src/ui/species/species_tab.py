from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QInputDialog, QGridLayout, \
    QLabel

from ui.gene_presenter import GenePresenter


class SpeciesTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.main_layout = QVBoxLayout()

        list_style = """
            QListWidget#species_list{
                
            }
        
            QListWidget#species_list::item {
                padding: 10px;
            }
            
            QListWidget#species_list::item:selected {
                padding: 0px;
                background-color: #3577dd;
                color: white;
            }
        """
        self.setStyleSheet(list_style)

        self.species_list = QListWidget()
        self.species_list.setFont(QFont("Oxygen", 14))
        self.species_list.setObjectName("species_list")

        self.update_ui()
        self.buttons_layout = QHBoxLayout()
        self._init_buttons()

        self.main_layout.addWidget(QLabel("Species of the network and their initial concentration."))
        self.main_layout.addWidget(self.species_list)
        self.main_layout.addLayout(self.buttons_layout)
        self.main_layout.setObjectName("main_layout")
        self.setLayout(self.main_layout)

    def _init_buttons(self):
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self._add_species_click_handler)
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self._remove_species_click_handler)
        self.buttons_layout.addWidget(self.add_button)
        self.buttons_layout.addWidget(self.remove_button)

    def update_ui(self):
        self.species_list.clear()
        for s in GenePresenter.get_instance().get_species():
            self.species_list.addItem(s + ": " + str(GenePresenter.get_instance().get_species()[s]))

    def _add_species_click_handler(self):
        (text, ok) = QInputDialog.getText(self, "Add Species", "Write species and initial "
                                                               "concentration in this format: \n"
                                                               "species1: 20.0, species2: 30.0")

        if ok:
            for pair in text.split(','):
                split = pair.strip().split(':')
                species_name = split[0].strip()
                species_concent = float(split[1].strip())
                GenePresenter.get_instance().add_species(species_name, species_concent)

        self.update_ui()
        self.parent.reactions_tab.update_ui()

    def _remove_species_click_handler(self):
        text = self.species_list.item(self.species_list.currentRow()).text()
        species = text.split(':')[0]
        GenePresenter.get_instance().remove_species(species)
        self.update_ui()
        self.parent.reactions_tab.update_ui()
