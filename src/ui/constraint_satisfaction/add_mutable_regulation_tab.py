from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QComboBox, QCheckBox, QGroupBox, \
    QHBoxLayout, QLineEdit, QLabel, QPushButton

import helper
from models.formulae.transcription_formula import TranscriptionFormula
from models.reg_type import RegType
from constraint_satisfaction.mutable import RegulationMutable, VariableMutable
from ui.gene_presenter import GenePresenter


class AddMutableRegulationTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.transcription_reactions_combo = self._make_transcription_reactions_combo()
        self.regulators_list = self._make_regulators_list()
        reg_type_box, self.activation_check, self.repression_check = self._make_reg_type_box()
        k_box, self.lb_edit, self.ub_edit, self.step_edit = self._make_k_box()
        self.add_button = self._make_add_button()
        self.hill_edit = QLineEdit()
        self.hill_edit.setValidator(helper.get_double_validator())

        layout.addWidget(QLabel("This reaction can be regulated..."))
        layout.addWidget(self.transcription_reactions_combo)
        layout.addWidget(QLabel("By one of these species..."))
        layout.addWidget(self.regulators_list)
        layout.addWidget(QLabel("In these ways..."))
        layout.addWidget(reg_type_box)
        layout.addWidget(QLabel("And have a K value with the range..."))
        layout.addWidget(k_box)
        layout.addWidget(QLabel("Will have this immutable hill coefficient..."))
        layout.addWidget(self.hill_edit)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    @staticmethod
    def _make_regulators_list():
        t = QListWidget()

        for s in GenePresenter.get_instance().network.species:
            i = QListWidgetItem()
            i.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            i.setCheckState(Qt.Unchecked)
            i.setText(s)
            t.addItem(i)

        return t

    @staticmethod
    def _make_transcription_reactions_combo():
        c = QComboBox()

        for r in GenePresenter.get_instance().network.reactions:
            if isinstance(r.rate_function, TranscriptionFormula):
                c.addItem(r.name)

        return c

    @staticmethod
    def _make_reg_type_box():
        activation_check = QCheckBox("Activation")
        repression_check = QCheckBox("Repression")

        fields = QHBoxLayout()
        fields.addWidget(activation_check)
        fields.addWidget(repression_check)

        reg_type_box = QGroupBox()
        reg_type_box.setLayout(fields)
        return reg_type_box, activation_check, repression_check

    @staticmethod
    def _make_k_box():
        lb_edit = QLineEdit()
        lb_edit.setValidator(helper.get_double_validator())
        lb_edit.setFixedWidth(60)

        ub_edit = QLineEdit()
        ub_edit.setValidator(helper.get_double_validator())
        ub_edit.setFixedWidth(60)

        step_edit = QLineEdit()
        step_edit.setValidator(helper.get_double_validator())
        step_edit.setFixedWidth(60)

        fields = QHBoxLayout()
        fields.addWidget(lb_edit)
        fields.addWidget(QLabel(" - "))
        fields.addWidget(ub_edit)
        fields.addWidget(QLabel(" Step: "))
        fields.addWidget(step_edit)

        k_box = QGroupBox()
        k_box.setLayout(fields)
        return k_box, lb_edit, ub_edit, step_edit

    def add_button_clicked(self):
        reaction_name = self.transcription_reactions_combo.currentText()

        regulators = []
        for i in range(0, self.regulators_list.count()):
            item = self.regulators_list.item(i)

            if item.checkState() == Qt.Checked:
                regulators.append(item.text())

        reg_types = []
        if self.activation_check.isChecked():
            reg_types.append(RegType.ACTIVATION)
        if self.repression_check.isChecked():
            reg_types.append(RegType.REPRESSION)

        k_lb = float(self.lb_edit.text())
        k_ub = float(self.ub_edit.text())
        k_step = float(self.step_edit.text())

        hill_coeff = float(self.hill_edit.text())

        reg_mut = RegulationMutable(reaction_name, regulators,
                                    VariableMutable("k", k_lb, k_ub, k_step),
                                    reg_types, False, hill_coeff)
        GenePresenter.get_instance().mutables.append(reg_mut)

        # Climb up the hierarchy to find the window and close that.
        self.parent().parent().parent().close()

    def _make_add_button(self):
        button = QPushButton("Add")
        button.clicked.connect(self.add_button_clicked)
        return button
