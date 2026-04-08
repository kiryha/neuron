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
    hada_node.parm("material_id").set(material_data.get("id")) 
    shader = material_data.get("shader_parameters") or material_data.get("parameters") or {}
    proc = material_data.get("procedural_parameters") or {}

    hada_node.parm("variation_seed").set(float(proc.get("variation_seed")))

    hada_node.parm("base_value").set(shader.get("base_value"))
    hada_node.parmTuple("base_color").set(shader.get("base_color"))
    hada_node.parm("metalness").set(shader.get("metalness"))

    hada_node.parm("specular_roughness").set(shader.get("specular_roughness"))
    hada_node.parm("specular_ior").set(shader.get("specular_ior"))
    hada_node.parm("specular_anisotropy").set(shader.get("specular_anisotropy"))

    hada_node.parm("transmission").set(shader.get("transmission"))
    hada_node.parm("transmission_dispersion").set(shader.get("transmission_dispersion"))
    hada_node.parmTuple("transmission_color").set(shader.get("transmission_color"))
    hada_node.parm("transmission_depth").set(shader.get("transmission_depth"))
    hada_node.parmTuple("transmission_scatter").set(shader.get("transmission_scatter"))

    hada_node.parm("subsurface").set(shader.get("subsurface"))
    hada_node.parm("coat").set(shader.get("coat"))
    hada_node.parm("coat_roughness").set(shader.get("coat_roughness"))

    hada_node.parm("bump_scale").set(proc.get("bump_scale"))

    hada_node.parm("thin_walled").set(shader.get("thin_walled"))
