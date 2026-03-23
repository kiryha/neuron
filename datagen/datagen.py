"""
UI for Houdini Data Generation
"""

import hou
from PySide6 import QtCore, QtWidgets
from datagen.ui import ui_datagen

from datagen.materials import BuildMaterialsData, CreateMaterials
   

class Datagen(QtWidgets.QDialog, ui_datagen.Ui_Datagen):
    def __init__(self):
        super(Datagen, self).__init__()
        self.setupUi(self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        self.btnRun.clicked.connect(self.run)

    def run(self):

        # Generate Expanded Material List
        # materials_data = BuildMaterialsData()
        # materials_data.export()
        # materials_data.display()

        # Create Materials in Houdini
        create_materials = CreateMaterials()
        create_materials.build_library()

def run_datagen():
    datagen = Datagen()
    datagen.show()