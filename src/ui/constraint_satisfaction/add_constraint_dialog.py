import re

from PyQt5.QtWidgets import QDialog, QLabel, QFormLayout, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox

import helper
from constraint_satisfaction.constraint import Constraint
from ui import common_widgets
from ui.gene_presenter import GenePresenter


class AddConstraintDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self._init_fields()
        self._init_button()

        self.setMinimumWidth(350)
        self.setLayout(self.layout)

    def _button_clicked(self):
        sign = self.sign_combo.currentText()
        species = self.lhs.currentText()
        value = float(self.rhs.text())
        t0 = float(self.time_lb.text())
        t1 = float(self.time_ub.text())

        if sign == "<=":
            cons = lambda v: v - value
        elif sign == ">=":
            cons = lambda v: value - v
        else:
            helper.show_error_message("Constraint syntax error: Unrecognised sign")
            self.close()
            return

        c = Constraint(species, cons, (t0, t1))
        c.pretty_print = species + sign + str(value) + " for time: " + str(t0) + "s - " + str(t1) + "s"
        GenePresenter.get_instance().add_constraint(c)
        self.close()

    def _init_button(self):
        self.button = QPushButton("Add Constraint")
        self.button.clicked.connect(self._button_clicked)
        self.layout.addWidget(self.button)

    def _init_fields(self):
        fields = QFormLayout()

        self.lhs = common_widgets.make_species_combo()
        self.rhs = QLineEdit()
        self.rhs.setValidator(helper.get_double_validator())
        self.rhs.setPlaceholderText("Constraint value")
        self.sign_combo = QComboBox()
        self.sign_combo.addItems([">=", "<="])

        constraint_box = QHBoxLayout()
        constraint_box.addWidget(self.lhs)
        constraint_box.addWidget(self.sign_combo)
        constraint_box.addWidget(self.rhs)
        fields.addRow("Constraint (e.g. X >= 20)", constraint_box)

        self.time_lb = QLineEdit()
        self.time_lb.setValidator(helper.get_double_validator())
        self.time_lb.setPlaceholderText("Start")
        self.time_ub = QLineEdit()
        self.time_ub.setValidator(helper.get_double_validator())
        self.time_ub.setPlaceholderText("End")

        time_box = QHBoxLayout()
        time_box.addWidget(self.time_lb)
        time_box.addWidget(QLabel("-"))
        time_box.addWidget(self.time_ub)
        fields.addRow("Time period (e.g. 0 - 20)", time_box)

        self.layout.addLayout(fields)
