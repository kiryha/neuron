"""
UI for Houdini Data Generation
"""

import hou
from PySide6 import QtCore, QtWidgets
from datagen.ui import ui_datagen

from importlib import reload
from datagen import materials
reload(materials)
   

class Datagen(QtWidgets.QDialog, ui_datagen.Ui_Datagen):
    def __init__(self):
        super(Datagen, self).__init__()
        self.setupUi(self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        self.btnRun.clicked.connect(self.run)

    def run(self):

        # # Generate Expanded Material List
        # materials_data = BuildMaterialsData()
        # materials_data.export()
        # materials_data.display()


        # Generate Labels 
        labels = materials.BuildPrompts()
        labels.generate()
        # labels.display()

        # # Create Materials in Houdini
        # build_materials = materials.BuildMaterials()
        # build_materials.build_library()

def run_datagen():
    datagen = Datagen()
    datagen.show()