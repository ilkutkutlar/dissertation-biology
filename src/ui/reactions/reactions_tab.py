from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPalette, QFont
from PyQt5.QtWidgets import QWidget, QListWidget, QLabel, QGridLayout, QScrollArea, QHBoxLayout, QPushButton, \
    QVBoxLayout, QComboBox

from network_visualiser import NetworkVisualiser
from ui.gene_presenter import GenePresenter
from ui.reactions.add_reaction_dialog import AddReactionDialog


class ReactionsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.grid = QGridLayout()

        self._init_reactions_list()
        self._init_reaction_details()
        self._init_buttons()

        self.network_image_combo = self._make_network_image_combo()
        self.network_image, network_image_area = self._make_image_panel()
        self.update_ui()

        self.grid.addWidget(self.reactions_list, 0, 0)
        self.grid.addWidget(self.aux, 0, 1)

        self.main_layout.addLayout(self.grid)
        self.main_layout.addLayout(self.buttons_layout)
        self.main_layout.addWidget(self.network_image)
        self.main_layout.addWidget(self.network_image_combo)

        self.setLayout(self.main_layout)

    @staticmethod
    def _make_image_panel():
        scroll_area = QScrollArea()
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        network_image = QLabel()
        # network_image.setSizePolicy(
        #     QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        # network_image.setScaledContents(True)
        network_image.setMinimumHeight(300)
        network_image.setMinimumWidth(300)
        scroll_area.setWidget(network_image)

        return network_image, scroll_area

    def _make_network_image_combo(self):
        combo = QComboBox()
        combo.addItem("Reaction view")
        combo.addItem("Gene view")
        combo.currentIndexChanged.connect(self.update_ui)
        combo.setMaximumWidth(200)
        return combo

    def _init_reaction_details(self):
        self.aux = QScrollArea()
        layout = QVBoxLayout()
        self.reaction_details = QLabel()
        self.reaction_details.setFont(QFont("Oxygen", 14))
        self.reaction_details.setAlignment(Qt.AlignLeft)
        self.reaction_details.setMinimumWidth(200)
        self.reaction_details.setWordWrap(True)
        layout.addWidget(self.reaction_details)
        self.aux.setLayout(layout)

    def _init_buttons(self):
        self.buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self._add_reaction_clicked)

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self._remove_reaction_clicked)

        self.buttons_layout.addWidget(self.add_button)
        self.buttons_layout.addWidget(self.remove_button)

    def _init_reactions_list(self):
        self.reactions_list = QListWidget()
        self.reactions_list.setFont(QFont("Oxygen", 14))

        self.reactions_list.itemClicked.connect(self._reaction_list_clicked)
        self.reactions_list.setMinimumHeight(200)

    def _add_reaction_clicked(self):
        def dialog_finished():
            self.update_ui()

        dialog = AddReactionDialog()
        dialog.finished.connect(dialog_finished)
        dialog.exec_()

    def _remove_reaction_clicked(self):
        i = self.reactions_list.currentRow()
        GenePresenter.get_instance().remove_reaction_by_index(i)
        self.update_ui()

    def _reaction_list_clicked(self):
        index = self.reactions_list.currentRow()
        chosen_reaction = GenePresenter.get_instance().get_reactions()[index]
        self.reaction_details.setText(str(chosen_reaction))

    def update_ui(self):
        g = GenePresenter.get_instance()

        self.reactions_list.clear()
        for s in g.get_reactions():
            self.reactions_list.addItem(s.name)

        view = "reaction" if self.network_image_combo.currentIndex() == 0 else "gene"

        im = NetworkVisualiser.visualise(g.network, view)
        self.network_image.setPixmap(QPixmap.fromImage(im))
        self.network_image.setAlignment(Qt.AlignCenter)
        self.network_image.setBackgroundRole(QPalette.Dark)