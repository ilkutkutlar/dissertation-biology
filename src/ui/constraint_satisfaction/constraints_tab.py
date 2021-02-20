# 100 - y => min is 100
# y - 100 => max is 100
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QListWidget, QHBoxLayout, QPushButton, QWidget, QVBoxLayout

from ui.constraint_satisfaction.add_constraint_dialog import AddConstraintDialog
from ui.gene_presenter import GenePresenter


class ConstraintsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.constraints_list = QListWidget()
        self.constraints_list.setFont(QFont("Oxygen", 16))

        constraints_buttons_layout = QHBoxLayout()
        self.add_constraint_button = QPushButton("Add Constraint")
        constraints_buttons_layout.addWidget(self.add_constraint_button)
        self.add_constraint_button.clicked.connect(self._add_constraint_clicked)

        self.remove_constraint_button = QPushButton("Remove Constraint")
        self.remove_constraint_button.clicked.connect(self._remove_constraint_clicked)
        constraints_buttons_layout.addWidget(self.remove_constraint_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(constraints_buttons_layout)
        main_layout.addWidget(self.constraints_list)
        self.setLayout(main_layout)
        self._update_constraints_list()

    def _update_constraints_list(self):
        self.constraints_list.clear()

        for c in GenePresenter.get_instance().get_constraints():
            self.constraints_list.addItem(str(c))

    def _add_constraint_clicked(self):
        dia = AddConstraintDialog()
        dia.finished.connect(self._update_constraints_list)
        dia.exec_()

    def _remove_constraint_clicked(self):
        i = self.constraints_list.currentRow()
        GenePresenter.get_instance().remove_constraint(i)
        self._update_constraints_list()
