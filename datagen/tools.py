"""
Houdini build and scene management utilities
"""

import json
import hou
from .config import LIBRARY_JSON, HDA_NAME


def apply_material(material_id):
    """Read color from JSON for the given material_id and set it on the neuromat HDA."""

    with open(LIBRARY_JSON, "r") as f:
        library = json.load(f)

    # Get HDA and material data
    hada_node = hou.node(f"/stage/{HDA_NAME}")
    material_data = library.get(material_id)

    # Set HDA properties
    hada_node.parmTuple("base_color").set(material_data.get("parameters", {}).get("base_color"))
    hada_node.parm("variation_seed").set(float(material_data.get("parameters", {}).get("variation_seed")))
    hada_node.parm("specular_ior").set(material_data.get("parameters", {}).get("specular_ior"))
    hada_node.parm("subsurface").set(material_data.get("parameters", {}).get("subsurface"))
    hada_node.parm("coat").set(material_data.get("parameters", {}).get("coat"))
    hada_node.parm("coat_roughness").set(material_data.get("parameters", {}).get("coat_roughness"))
    hada_node.parm("specular_anisotropy").set(material_data.get("parameters", {}).get("specular_anisotropy"))
    hada_node.parm("bump_scale").set(material_data.get("parameters", {}).get("bump_scale"))
