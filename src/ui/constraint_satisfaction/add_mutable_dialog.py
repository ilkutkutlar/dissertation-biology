from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget

from ui.constraint_satisfaction.add_mutable_regulation_tab import AddMutableRegulationTab
from ui.constraint_satisfaction.add_mutable_value_tab import AddMutableValueTab


class AddMutableDialog(QDialog):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        tabs = QTabWidget()

        self.values_tab = AddMutableValueTab()
        self.regulations_tab = AddMutableRegulationTab()

        tabs.addTab(self.values_tab, "Value or Reaction")
        tabs.addTab(self.regulations_tab, "Regulation")

        layout.addWidget(tabs)

        self.setLayout(layout)
        self.setWindowTitle("Gene")
        self.show()
