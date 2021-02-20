from PyQt5.QtWidgets import QListWidget, QLabel, QGridLayout, QPushButton, \
    QVBoxLayout, QDialog, QFormLayout, QLineEdit, QWidget

import helper
from models.formulae.translation_formula import TranslationFormula
from models.formulae.degradation_formula import DegradationFormula
from models.formulae.custom_formula import CustomFormula
from models.reaction import Reaction
from ui import common_widgets
from ui.reactions.add_reaction_dialog_transcription import TranscriptionFields
from ui.gene_presenter import GenePresenter


class AddReactionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.regulations = []

        self.main_layout = QVBoxLayout()
        self.grid = QGridLayout()
        self.properties = QWidget()
        self.properties_layout = QVBoxLayout()
        self.properties.setLayout(self.properties_layout)

        self._init_transcription_fields()
        self._init_translation_fields()
        self._init_degradation_fields()
        self._init_custom_reaction_fields()

        self._init_reaction_types()
        self.grid.addWidget(self.properties, 0, 1)

        self.main_layout.addLayout(self.grid)
        self.setLayout(self.main_layout)
        self._init_ok_button()
        self.setWindowTitle("Add Reaction")

    def _reaction_type_changed_handler(self):
        index = self.reaction_types_list.currentRow()

        self.transcription_fields.hide()
        self.translation_fields.hide()
        self.degradation_fields.hide()
        self.custom_fields.hide()

        if index == 0:  # Transcription
            self.transcription_fields.show()
        elif index == 1:  # Translation
            self.translation_fields.show()
        elif index == 2:  # Degradation
            self.degradation_fields.show()
        else:  # Custom
            self.custom_fields.show()

    def _ok_button_clicked_handler(self):
        index = self.reaction_types_list.currentRow()

        if index == 0:  # Transcription
            GenePresenter.get_instance().add_reaction(self.transcription_fields.get_transcription_reaction())

        elif index == 1:  # Translation
            name = str(self.reaction_name2.text())
            rate = float(self.translation_rate.text())
            translated_mrna = str(self.translated_mrna.currentText())
            produced_protein = str(self.produced_protein.currentText())
            formula = TranslationFormula(rate, translated_mrna)
            GenePresenter.get_instance().add_reaction(Reaction(name, [translated_mrna], [produced_protein], formula))

        elif index == 2:  # Degradation
            name = str(self.reaction_name3.text())
            rate = float(self.decay_rate.text())
            decaying_species = str(self.decaying_species.currentText())
            formula = DegradationFormula(rate, decaying_species)
            GenePresenter.get_instance().add_reaction(Reaction(name, [decaying_species], [], formula))
        else:  # Custom
            name = str(self.reaction_name4.text())
            reactant = str(self.reactant.currentText())
            product = str(self.product.currentText())
            equation = str(self.equation.text())
            formula = CustomFormula(equation, {}, {})
            GenePresenter.get_instance().add_reaction(Reaction(name, [reactant], [product], formula))

        self.close()

    def _init_reaction_types(self):
        self.reaction_types_list = QListWidget()

        self.reaction_types_list.setMinimumWidth(200)
        self.reaction_types_list.setMaximumWidth(200)

        self.reaction_types_list.addItem("Transcription Reaction")
        self.reaction_types_list.addItem("Translation Reaction")
        self.reaction_types_list.addItem("Degradation Reaction")
        self.reaction_types_list.addItem("Custom Reaction")

        self.grid.addWidget(self.reaction_types_list, 0, 0)
        self.reaction_types_list.itemClicked.connect(self._reaction_type_changed_handler)

    def _init_ok_button(self):
        self.ok_button = QPushButton("Add reaction")
        self.ok_button.clicked.connect(self._ok_button_clicked_handler)
        self.main_layout.addWidget(self.ok_button)

    def _init_transcription_fields(self):
        self.transcription_fields = TranscriptionFields()
        self.properties_layout.addWidget(self.transcription_fields)

    def _init_translation_fields(self):
        fields = QFormLayout()

        self.reaction_name2 = QLineEdit()
        fields.addRow(QLabel("Reaction name"), self.reaction_name2)
        self.translation_rate = QLineEdit()
        self.translation_rate.setValidator(helper.get_double_validator())
        fields.addRow(QLabel("Translation rate: "), self.translation_rate)
        self.translated_mrna = common_widgets.make_species_combo()
        fields.addRow(QLabel("Translated mRNA: "), self.translated_mrna)
        self.produced_protein = common_widgets.make_species_combo()
        fields.addRow(QLabel("Produced protein: "), self.produced_protein)

        self.translation_fields = QWidget()
        self.translation_fields.setLayout(fields)
        self.properties_layout.addWidget(self.translation_fields)
        self.translation_fields.hide()

    def _init_degradation_fields(self):
        fields = QFormLayout()

        self.reaction_name3 = QLineEdit()
        fields.addRow(QLabel("Reaction name"), self.reaction_name3)
        self.decay_rate = QLineEdit()
        self.decay_rate.setValidator(helper.get_double_validator())
        fields.addRow(QLabel("Decay rate: "), self.decay_rate)
        self.decaying_species = common_widgets.make_species_combo()
        fields.addRow(QLabel("Decaying species: "), self.decaying_species)

        self.degradation_fields = QWidget()
        self.degradation_fields.setLayout(fields)
        self.properties_layout.addWidget(self.degradation_fields)
        self.degradation_fields.hide()

    def _init_custom_reaction_fields(self):
        fields = QFormLayout()

        self.reaction_name4 = QLineEdit()
        fields.addRow(QLabel("Reaction name"), self.reaction_name4)
        self.equation = QLineEdit()
        fields.addRow(QLabel("Equation: "), self.equation)
        self.reactant = common_widgets.make_species_combo()
        fields.addRow(QLabel("Reactant: "), self.reactant)
        self.product = common_widgets.make_species_combo()
        fields.addRow(QLabel("Product: "), self.product)

        self.custom_fields = QWidget()
        self.custom_fields.setLayout(fields)
        self.properties_layout.addWidget(self.custom_fields)
        self.custom_fields.hide()
