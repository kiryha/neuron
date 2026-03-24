"""
UI for Houdini Data Generation
"""

import hou
from PySide6 import QtCore, QtWidgets
from datagen.ui import ui_datagen

from importlib import reload
from datagen import materials
reload(materials)
reload(ui_datagen)
   

class Datagen(QtWidgets.QDialog, ui_datagen.Ui_Datagen):
    def __init__(self):
        super(Datagen, self).__init__()
        self.setupUi(self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        self.btnBuildData.clicked.connect(self.build_materials_data)
        self.btnBuildPrompts.clicked.connect(self.build_prompts)
        self.btnBuildMaterials.clicked.connect(self.build_materials)

    def build_materials_data(self):

        # Generate Expanded Material List
        materials_data = materials.BuildMaterialsData()
        materials_data.generate()

    def build_prompts(self):

        # Generate Labels 
        labels = materials.BuildPrompts()
        labels.generate()

    def build_materials(self):

        # Create Materials in Houdini
        build_materials = materials.BuildMaterials()
        build_materials.build_library()

def run_datagen():
    datagen = Datagen()
    datagen.show()