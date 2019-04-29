from PyQt5.QtWidgets import QTabWidget, QFileDialog
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QAction, QMessageBox

from input_output.sbml_saver import SbmlSaver
from simulation.ode_simulator import OdeSimulator
from ui.gene_presenter import GenePresenter
from ui.open_sbml_dialog import OpenSbmlDialog
from ui.reactions.reactions_tab import ReactionsTab
from ui.constraint_satisfaction.constraint_satisfaction_tab import ConstraintSatisfactionModifyTab
from ui.simulation.deterministic_simulation_dialog import DeterministicSimulationDialog
from ui.simulation.stochastic_simulation_dialog import StochasticSimulationDialog
from ui.species.species_tab import SpeciesTab


class GeneWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        tabs = QTabWidget()

        self.species_tab = SpeciesTab(self)
        self.reactions_tab = ReactionsTab()
        self.rev_eng_modify_tab = ConstraintSatisfactionModifyTab()
        tabs.addTab(self.species_tab, "Species")
        tabs.addTab(self.reactions_tab, "Reactions")
        tabs.addTab(self.rev_eng_modify_tab, "Constraint Satisfaction")

        self._init_menubar()

        layout.addWidget(tabs)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.setWindowTitle("Gene")
        self.show()

    def _deterministic_simulation_clicked(self):
        def handler(s):
            net = GenePresenter.get_instance().network
            OdeSimulator.visualise(net, s, OdeSimulator.simulate(net, s))

        DeterministicSimulationDialog(handler)

    def _stochastic_simulation_clicked(self):
        StochasticSimulationDialog()

    def _save_file_as_sbml_clicked(self):
        net = GenePresenter.get_instance().network
        d = QFileDialog()
        filename = d.getSaveFileName(self, "Save file", ".", "XML Files (*.xml)")

        if filename:
            SbmlSaver.save_network_to_file(net, filename[0] + ".xml")

    def _help_units_clicked(self):
        units_message = QMessageBox()
        units_message.setIcon(QMessageBox.Information)
        units_message.setWindowTitle("Units")
        units_message.setStandardButtons(QMessageBox.Ok)

        units = """
        The quantities used in this programme have these units:
        
        Time: seconds
        Species: molecules
        Transcription rate: molecules/second
        Translation rate: molecules/mRNA molecules/second
        Degradation rate: molecules/second
        """

        units_message.setText(units)
        units_message.exec_()

    def _help_user_manual_clicked(self):
        user_manual_message = QMessageBox()
        user_manual_message.setWindowTitle("User's Manual")
        user_manual_message.setStandardButtons(QMessageBox.Ok)

        user_manual = """
                This programme has three main functions:
                
                === 1. Designing a gene regulatory network ===
                
                · The network is modelled as a series of chemical reactions.
                
                · You have to add every species in the "Species" tab before using them in a reaction.
                You have to add mRNA and protein associated with a gene separately.
                
                · "Reactions" tab allows adding network reactions (such as transcription, translation, etc.)
                The tab also offers a visualisation of the network.
                Regulation relationships of the network are specified when adding transcription reactions.
                
                === 2. Simulating networks ===
                
                · Two types of simulation are supported: Deterministic and Stochastic.
                · Both can be achieved through the "Simulate" menu.
                
                
                === 3. Constraint satisfaction (explained below) ===
                
                · Constraint satisfaction allows modifying a network to fit a set of constraints (e.g. species
                X <= 100 between seconds 0 to 20).
                
                · "Mutables" are variables which are allowed to vary in order to satisfy the constraints.
                · "Constraints" are all the constraints which have to be satisfied.
                
                Constraint satisfaction modes:
                1. Exact match: Find a network which exactly matches the required network.
                2. Closest match: If no network exactly satisfies all the constraints, 
                    finds a network which comes closest to satisfying all of them.
                """

        user_manual_message.setText(user_manual)
        user_manual_message.exec_()

    def _init_menubar(self):
        self.menubar = self.menuBar()

        # File menu
        file = self.menubar.addMenu("File")

        open_file = QAction("Open SBML file", self)
        open_file.triggered.connect(lambda _: OpenSbmlDialog(self))
        file.addAction(open_file)

        save_file = QAction("Save as SBML file", self)
        save_file.triggered.connect(self._save_file_as_sbml_clicked)
        file.addAction(save_file)

        # Simulate menu
        simulate = self.menubar.addMenu("Simulate")

        deterministic = QAction("Deterministic (ODE model)", self)
        deterministic.triggered.connect(self._deterministic_simulation_clicked)
        simulate.addAction(deterministic)

        stochastic = QAction("Stochastic (Gillespie Algorithm)", self)
        stochastic.triggered.connect(self._stochastic_simulation_clicked)
        simulate.addAction(stochastic)

        # Help menu
        help_menu = self.menubar.addMenu("Help")

        help_units = QAction("Units", self)
        help_units.triggered.connect(self._help_units_clicked)
        help_menu.addAction(help_units)

        help_user_manual = QAction("User's Manual", self)
        help_user_manual.triggered.connect(self._help_user_manual_clicked)
        help_menu.addAction(help_user_manual)


app = QApplication([])
g = GeneWindow()
app.exec_()
