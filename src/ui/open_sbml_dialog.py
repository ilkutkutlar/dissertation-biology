from PyQt5.QtWidgets import QFileDialog, QMessageBox

import helper
from input_output.sbml_parser import SbmlParser
from ui.gene_presenter import GenePresenter


class OpenSbmlDialog(QFileDialog):

    def __init__(self, parent):
        super().__init__()
        self.setFileMode(QFileDialog.AnyFile)

        filename = self.getOpenFileName(self, "Open file", ".", "XML Files (*.xml);; All Files (*.*)")

        if filename:
            net = SbmlParser.parse(filename[0])
            if not net:
                helper.show_error_message("An error occurred while opening the SBML file.")

            GenePresenter.get_instance().network = net

            message = QMessageBox()
            message.setText("SBML file has been opened")
            message.exec_()

            parent.species_tab.update_ui()
            parent.reactions_tab.update_ui()
