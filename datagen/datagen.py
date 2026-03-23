"""
UI for Houdini Data Generation
"""

import hou
from PySide6 import QtCore, QtWidgets
from datagen.ui import ui_datagen

from datagen.materials import MaterialGenerator

class Datagen(QtWidgets.QDialog, ui_datagen.Ui_Datagen):
    def __init__(self):
        super(Datagen, self).__init__()
        self.setupUi(self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        self.btnRun.clicked.connect(self.run)

    def run(self):
        material_generator = MaterialGenerator()
        material_generator.export()
        material_generator.display()

def run_datagen():
    datagen = Datagen()
    datagen.show()