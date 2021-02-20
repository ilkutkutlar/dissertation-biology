from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QFormLayout, QRadioButton, QGroupBox, QLabel, QLineEdit, QWidget, QComboBox, QCheckBox, \
    QListWidget, QPushButton

import helper
from models.formulae.transcription_formula import TranscriptionFormula
from models.input_gate import InputGate
from models.reaction import Reaction
from models.reg_type import RegType
from models.regulation import Regulation
from ui import common_widgets


class TranscriptionFields(QWidget):
    def __init__(self):
        super().__init__()
        fields = QFormLayout()
        self.regulations = list()

        self.reaction_name = QLineEdit()
        self.transcription_rate = QLineEdit()
        self.transcription_rate.setValidator(helper.get_double_validator())

        self.transcribed_species = common_widgets.make_species_combo()
        self.transcribed_species.currentIndexChanged.connect(self._transcribed_species_current_index_changed)

        self.is_regulated = QCheckBox("Is Regulated")
        self.is_regulated.stateChanged.connect(self._is_regulated_state_changed)

        self.regulation_settings_panel = self._make_regulation_settings_panel()

        fields.addRow(QLabel("Reaction name"), self.reaction_name)
        fields.addRow(QLabel("Transcription rate"), self.transcription_rate)
        fields.addRow(QLabel("Transcribed species: "), self.transcribed_species)
        fields.addRow(self.is_regulated)
        fields.addRow(self.regulation_settings_panel)

        self._is_regulated_state_changed()
        self.setLayout(fields)

    def _transcribed_species_current_index_changed(self):
        for x in self.regulations:
            # Regulations added before the transcribed species was changed still
            # point to the old transcribed species, fix those!
            x.to_gene = self.transcribed_species.currentText()
        self._refresh_regulations_list()

    def _refresh_regulations_list(self):
        self.regulations_list.clear()
        for x in self.regulations:
            self.regulations_list.addItem(str(x))

        # Allow at most two regulations
        if self.regulations_list.count() >= 2:
            self.add_button.setDisabled(True)
        else:
            self.add_button.setDisabled(False)

    def _add_regulation_clicked(self):
        from_gene = self.regulator.currentText()
        to_gene = self.transcribed_species.currentText()
        reg_type = RegType.ACTIVATION if self.activation_radio.isChecked() else RegType.REPRESSION
        k = float(self.k.text())

        r = Regulation(from_gene, to_gene, reg_type, k)
        self.regulations.append(r)
        self._refresh_regulations_list()

    def _make_add_regulation_box(self):
        self.activation_radio = QRadioButton("Activation")
        self.repression_radio = QRadioButton("Repression")

        self.regulator = common_widgets.make_species_combo()
        self.k = QLineEdit()
        self.k.setValidator(helper.get_double_validator())

        self.add_button = QPushButton("Add regulation")
        self.add_button.clicked.connect(self._add_regulation_clicked)

        fields = QFormLayout()
        fields.addRow(self.activation_radio, self.repression_radio)
        fields.addRow(QLabel("Regulating species:"), self.regulator)
        fields.addRow(QLabel("K:"), self.k)
        fields.addRow(self.add_button)

        add_regulation_box = QGroupBox()
        add_regulation_box.setLayout(fields)
        return add_regulation_box

    def _make_regulation_settings_panel(self):
        fields = QFormLayout()

        self.hill = QLineEdit()
        self.hill.setValidator(helper.get_double_validator())

        self.input_gate = QComboBox()
        self.input_gate.addItems(["NONE", "AND", "OR"])

        self.add_regulation_box = self._make_add_regulation_box()

        self.regulations_list = QListWidget()
        self.regulations_list.setFixedHeight(100)

        fields.addRow(QLabel("Hill coefficient: "), self.hill)
        fields.addRow(QLabel("Input gate: "), self.input_gate)
        fields.addRow(QLabel("Regulations"))
        fields.addRow(self.regulations_list)
        fields.addRow(self.add_regulation_box)

        self.activation_radio.setChecked(True)
        return fields

    def _is_regulated_state_changed(self):
        if self.is_regulated.isChecked():
            for w in range(0, self.regulation_settings_panel.count()):
                self.regulation_settings_panel.itemAt(w).widget().setDisabled(False)
        else:
            for w in range(0, self.regulation_settings_panel.count()):
                self.regulation_settings_panel.itemAt(w).widget().setDisabled(True)

            # self.hill_label.setDisabled(True)
            # self.hill.setDisabled(True)
            # self.regulations_label.setDisabled(True)
            # self.input_gate_label.setDisabled(True)
            # self.input_gate.setDisabled(True)
            # self.add_regulation_box.setDisabled(True)

    """
    Get the transcription reaction this form represents
    """

    def get_transcription_reaction(self):
        rate = float(self.transcription_rate.text())
        species = str(self.transcribed_species.currentText())
        f = TranscriptionFormula(rate, species)

        if self.is_regulated.isChecked():
            hill = float(self.hill.text())
            input_gate = self.input_gate.currentText()

            if input_gate == "AND":
                input_gate = InputGate.AND
            elif input_gate == "OR":
                input_gate = InputGate.OR
            else:
                input_gate = InputGate.NONE

            f.set_regulation(hill, self.regulations, input_gate)

        name = self.reaction_name.text()
        return Reaction(name, [], [species], f)
