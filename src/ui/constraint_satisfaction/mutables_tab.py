from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QListWidget, QHBoxLayout, QPushButton, QWidget

from ui.constraint_satisfaction.add_mutable_dialog import AddMutableDialog
from ui.gene_presenter import GenePresenter


class MutablesTab(QWidget):
    def __init__(self):
        super().__init__()

        self.mutables_list = QListWidget()
        self.mutables_list.setFont(QFont("Oxygen", 16))

        mutables_buttons_layout = QHBoxLayout()
        self.add_mutable_button = QPushButton("Add Mutable")
        self.add_mutable_button.clicked.connect(self._add_mutable_clicked)
        mutables_buttons_layout.addWidget(self.add_mutable_button)
        self.remove_mutable_button = QPushButton("Remove Mutable")
        self.remove_mutable_button.clicked.connect(self._remove_mutable_clicked)
        mutables_buttons_layout.addWidget(self.remove_mutable_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(mutables_buttons_layout)
        main_layout.addWidget(self.mutables_list)
        self.setLayout(main_layout)
        self._update_mutables_list()

    def _update_mutables_list(self):
        self.mutables_list.clear()

        for m in GenePresenter.get_instance().get_mutables():
            self.mutables_list.addItem(str(m))

    def _add_mutable_clicked(self):
        dia = AddMutableDialog()
        dia.finished.connect(self._update_mutables_list)
        dia.exec_()

    def _remove_mutable_clicked(self):
        i = self.mutables_list.currentRow()
        GenePresenter.get_instance().remove_mutable(i)
        self._update_mutables_list()
