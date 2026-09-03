"""
UI for Houdini Data Generation
"""

import hou
import json
from PySide6 import QtCore, QtWidgets
from datagen.ui import ui_datagen

from importlib import reload
from datagen import config, materials
from datagen.config import HDA_NAME

reload(materials)
reload(ui_datagen)


STRESS_MATERIAL_IDS = {
    "gold_polished_clean",
    "car_paint_red_matte_dusty",
    "iron_brushed_scratched",
    "glass_polished_clean",
    "glass_matte_clean",
    "honey_satin_dusty",
    "concrete_hammered_clean",
    "rubber_black_polished_scratched",
}


class Datagen(QtWidgets.QDialog, ui_datagen.Ui_Datagen):
    def __init__(self):
        super(Datagen, self).__init__()
        self.setupUi(self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        self.boxJSONName.addItems(config.LIBRARY_JSONS)
        self.materials_data = None
        self.load_materials_data()

        self.btnBuildData.clicked.connect(self.build_materials_data)
        self.btnBuildPrompts.clicked.connect(self.build_prompts)
        self.btnReloadData.clicked.connect(self.load_materials_data)

        self.listMaterials.currentItemChanged.connect(self.apply_material)

    def selected_library_json(self):
        """Return the material-library path selected in the UI."""

        return config.LIBRARY_JSONS[self.boxJSONName.currentText()]

    def load_materials_data(self):
        """
        Load the materials data from the JSON file
        """

        library_json = self.selected_library_json()

        if library_json.exists():
            with open(library_json, "r", encoding="utf-8") as f:
                self.materials_data = json.load(f)
        else:
            hou.ui.displayMessage(
                f"Materials data file not found:\n{library_json}",
                buttons=("OK",),
                severity=hou.severityType.Error,
            )
            return

        self.listMaterials.clear()
        self.materials_list = list(self.materials_data.keys())
        for material in self.materials_list:
            self.listMaterials.addItem(material)
        

    def build_materials_data(self):
        library_json = self.selected_library_json()
        subset_ids = (
            STRESS_MATERIAL_IDS
            if library_json == config.LIBRARY_JSON_DEV
            else None
        )

        materials_data = materials.BuildMaterialsData(library_json)
        materials_data.generate(subset_ids)

    def build_prompts(self):

        # Generate Labels 
        labels = materials.BuildPrompts(self.selected_library_json())
        labels.generate()

    def apply_material(self, current_item, _previous_item):

        if current_item is not None:
            self.set_material(current_item.text())

    def set_material(self, material_id):
        """Set the material on the neuromat HDA."""

        neuromat = hou.node(f"/stage/{HDA_NAME}")
        neuromat.parm("dataset_path").set(
            str(self.selected_library_json().resolve())
        )
        neuromat.parm("material_id").set(material_id)
        


def run_datagen():
    datagen = Datagen()
    datagen.show()
