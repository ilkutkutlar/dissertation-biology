import matplotlib.pyplot as plt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QWidget, QTabWidget, QComboBox, QGroupBox, \
    QLabel, QLineEdit, QFormLayout, QDialog, QScrollArea

import helper
from constraint_satisfaction.constraint_satisfaction import ConstraintSatisfaction
from network_visualiser import NetworkVisualiser
from simulation.ode_simulator import OdeSimulator
from structured_results import StructuredResults
from ui.constraint_satisfaction.constraints_tab import ConstraintsTab
from ui.constraint_satisfaction.mutables_tab import MutablesTab
from ui.gene_presenter import GenePresenter
from ui.simulation.deterministic_simulation_dialog import DeterministicSimulationDialog


class ConstraintSatisfactionModifyTab(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.addTab(MutablesTab(), "Mutables")
        self.tabs.addTab(ConstraintsTab(), "Constraints")

        self.main_layout.addWidget(self.tabs)
        self.main_layout.addWidget(self._get_run_panel())
        self._method_combo_index_changed()
        self.setLayout(self.main_layout)

    def _constraint_satisfaction_handler(self, s):
        g = GenePresenter.get_instance()

        if self.method_combo.currentIndex() == 0:
            give_up_time = int(self.give_up_edit.text())
            t = ConstraintSatisfaction.find_network(
                g.network, s, g.get_mutables(),
                g.get_constraints(), give_up_time)
        else:
            temperature = int(self.temperature_edit.text())
            schedule = ConstraintSatisfaction.generate_schedule(temperature)
            t = ConstraintSatisfaction.find_closest_network(
                g.network, s, g.get_mutables(),
                g.get_constraints(), schedule)

        if t:
            variables_dialog = QDialog()

            scroll = QScrollArea()
            scroll.setWidget(QLabel(t.str_variables()))

            layout = QVBoxLayout()
            layout.addWidget(scroll)

            ok_button = QPushButton("OK")
            ok_button.clicked.connect(lambda _: variables_dialog.close())
            layout.addWidget(ok_button)

            variables_dialog.setLayout(layout)
            variables_dialog.setMinimumWidth(300)
            variables_dialog.exec_()

            def draw_simulation():
                results = OdeSimulator.simulate(t, s)
                values = StructuredResults.label_results(results, t.species)
                for species in s.plotted_species:
                    plt.plot(s.generate_time_space(), values[species], label=species)
                plt.xlabel("Time (s)")
                plt.ylabel("Concentration")
                plt.legend(loc=0)
                plt.title("Results")
                plt.draw()

            plt.figure()

            plt.subplot(2, 1, 1)
            draw_simulation()

            plt.subplot(2, 1, 2)
            im = NetworkVisualiser.visualise_as_image(t, "gene")
            plt.imshow(im)
            plt.show()

        else:
            helper.show_error_message("No matching network found within the given parameters.")

    def _run_button_click_handler(self):
        DeterministicSimulationDialog(self._constraint_satisfaction_handler)

    def _get_annealing_panel(self):
        annealing_panel = QWidget()
        self.temperature_edit = QLineEdit()
        self.temperature_edit.setValidator(QIntValidator())
        annealing_layout = QFormLayout()
        annealing_layout.addRow(QLabel("Search extensiveness (typical value 100)"), self.temperature_edit)
        annealing_panel.setLayout(annealing_layout)
        annealing_panel.setVisible(False)
        return annealing_panel

    def _get_best_first_panel(self):
        best_first_panel = QWidget()
        self.give_up_edit = QLineEdit()
        self.give_up_edit.setValidator(QIntValidator())
        best_first_layout = QFormLayout()
        best_first_layout.addRow(QLabel("Duration (seconds)"), self.give_up_edit)
        best_first_panel.setLayout(best_first_layout)
        best_first_panel.setVisible(False)
        return best_first_panel

    def _method_combo_index_changed(self):
        if self.method_combo.currentIndex() == 0:
            self.best_first_panel.setVisible(True)
            self.annealing_panel.setVisible(False)
        else:
            self.best_first_panel.setVisible(False)
            self.annealing_panel.setVisible(True)

    def _get_method_combo(self):
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Find exact match", "Find closest match"])
        self.method_combo.currentIndexChanged.connect(self._method_combo_index_changed)
        return self.method_combo

    def _get_run_button(self):
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self._run_button_click_handler)
        return self.run_button

    def _get_run_options_panel(self):
        mode_layout = QFormLayout()
        mode_layout.addRow(QLabel("Search method"), self._get_method_combo())

        self.annealing_panel = self._get_annealing_panel()
        self.best_first_panel = self._get_best_first_panel()

        run_options_box = QVBoxLayout()
        run_options_box.addLayout(mode_layout)
        run_options_box.addWidget(self.annealing_panel)
        run_options_box.addWidget(self.best_first_panel)
        return run_options_box

    def _get_run_panel(self):
        run_group_box = QGroupBox()
        run_panel = QVBoxLayout()
        run_panel.addLayout(self._get_run_options_panel())
        run_panel.addWidget(self._get_run_button())
        run_group_box.setLayout(run_panel)
        return run_group_box
