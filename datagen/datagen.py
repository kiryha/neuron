"""
UI for Houdini Data Generation
"""

import hou
import json
from PySide6 import QtCore, QtWidgets
from datagen.ui import ui_datagen

from importlib import reload
from datagen import materials
from datagen import tools

reload(materials)
reload(tools)
reload(ui_datagen)
   

class Datagen(QtWidgets.QDialog, ui_datagen.Ui_Datagen):
    def __init__(self):
        super(Datagen, self).__init__()
        self.setupUi(self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        self.materials_data = None
        self.load_materials_data()

        self.btnBuildData.clicked.connect(self.build_materials_data)
        self.btnBuildPrompts.clicked.connect(self.build_prompts)
        self.btnApplyMaterial.clicked.connect(self.apply_material)

    def load_materials_data(self):
        """
        Load the materials data from the JSON file
        """
        with open(materials.LIBRARY_JSON, "r") as f:
            self.materials_data = json.load(f)

        self.materials_list = list(self.materials_data.keys())

        for material in self.materials_list:
            self.listMaterials.addItem(material)

    def build_materials_data(self):

        # Generate Expanded Material List
        materials_data = materials.BuildMaterialsData()
        materials_data.generate()

    def build_prompts(self):

        # Generate Labels 
        labels = materials.BuildPrompts()
        labels.generate()

    def apply_material(self):
        material_id = self.listMaterials.currentItem().text()
        tools.apply_material(material_id)
        


def run_datagen():
    datagen = Datagen()
    datagen.show()