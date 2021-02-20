from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFormLayout, QLineEdit, QLabel, QComboBox

import helper
from constraint_satisfaction.mutable import VariableMutable, ReactionMutable, GlobalParameterMutable
from ui.gene_presenter import GenePresenter


class AddMutableValueTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self._init_fields()
        self._init_add_button()
        self.setLayout(self.layout)

    def _init_add_button(self):
        button = QPushButton("Add")
        button.clicked.connect(self._add_clicked_handler)
        self.layout.addWidget(button)

    def _add_clicked_handler(self):
        combo_index = self.mutables_combo.currentIndex()
        mutable_title = self.mutable_combo_values[combo_index][0]
        mutable_reaction = self.mutable_combo_values[combo_index][1]
        is_custom = self.mutable_combo_values[combo_index][2]

        lo = self.lb.text().strip()
        lo = float(lo) if lo != "" else 0.0

        u = self.ub.text().strip()
        u = float(u) if u != "" else 0.0

        i = self.inc.text().strip()
        i = float(i) if i != "" else 0.0

        if mutable_reaction == "":
            if is_custom:
                GenePresenter.get_instance().mutables.append(GlobalParameterMutable(mutable_title, lo, u, i))
            else:
                GenePresenter.get_instance().mutables.append(VariableMutable(mutable_title, lo, u, i))
        else:
            GenePresenter.get_instance().mutables.append(ReactionMutable(mutable_title, lo, u, i, mutable_reaction))

        # Climb up the hierarchy to find the window and close that.
        self.parent().parent().parent().close()

    def _init_fields(self):
        fields = QFormLayout()

        self.mutables_combo, self.mutable_combo_values = self._make_mutables_combo()
        fields.addRow(QLabel("Mutable: "), self.mutables_combo)

        self.lb = QLineEdit()
        self.lb.setValidator(helper.get_double_validator())
        fields.addRow(QLabel("Lower bound"), self.lb)

        self.ub = QLineEdit()
        self.ub.setValidator(helper.get_double_validator())
        fields.addRow(QLabel("Upper bound"), self.ub)

        self.inc = QLineEdit()
        self.inc.setValidator(helper.get_double_validator())
        fields.addRow(QLabel("Increments"), self.inc)

        self.layout.addLayout(fields)

    @staticmethod
    def _make_mutables_combo():
        combo_items = []
        item_values = []

        for s in GenePresenter.get_instance().get_species():
            combo_items.append("Species ⟹ {}".format(s))
            item_values.append((s, "", False))

        for r in GenePresenter.get_instance().get_reactions():
            for p in r.rate_function.get_params():
                combo_items.append("{} ⟹ {}".format(r.name, p))
                item_values.append((p, r.name, False))

        net = GenePresenter.get_instance().network
        for symbol in net.symbols:
            combo_items.append("Global parameter ⟹ {}".format(symbol))
            item_values.append((symbol, "", True))

        combo = QComboBox()
        combo.addItems(combo_items)

        return combo, item_values
