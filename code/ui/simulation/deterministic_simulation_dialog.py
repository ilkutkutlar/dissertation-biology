import threading

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout

from models.simulation_settings import SimulationSettings
from ui import common_widgets


class DeterministicSimulationDialog(QDialog):

    def _ok_button_clicked(self):
        time_text = self.time_field.text().strip()

        end_time = float(time_text) if time_text else 1
        sampling_rate = int(end_time)

        species = list()
        for x in range(0, self.species_checkboxes.count()):
            checkbox = self.species_checkboxes.itemAt(x).widget()
            if checkbox.isChecked():
                species.append(checkbox.text())

        self.close()

        s = SimulationSettings(0, end_time, sampling_rate, [s.strip() for s in species])
        self.handler(s)

    """
    :param Callable[[SimulationSettings], None] handler: The handler for the dialog's ok button.
    """

    def __init__(self, handler):
        super().__init__()
        main = QVBoxLayout()
        fields = QFormLayout()
        self.handler = handler

        self.time_field = QLineEdit()
        self.time_field.setValidator(QIntValidator())
        fields.addRow(QLabel("Simulation time"), self.time_field)

        self.species_checkboxes = common_widgets.make_species_checkboxes_layout()

        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(self._ok_button_clicked)

        main.addLayout(fields)
        main.addWidget(QLabel("Which species to show: "))
        main.addLayout(self.species_checkboxes)
        main.addWidget(self.ok_button)

        self.setMinimumWidth(200)
        self.setWindowTitle("Simulation settings")
        self.setLayout(main)
        self.exec_()
