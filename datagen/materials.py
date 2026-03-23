"""
Material Generator for Houdini

Run in Cursor Terminal
python -m datagen.materials
"""

import json
import hashlib
import logging
from pathlib import Path
from itertools import product

from .config import LIBRARY_JSON

logger = logging.getLogger(__name__)

class BuildMaterialsData:
    def __init__(self):
        # 1. PHYSICAL CATEGORIES (Shader Models)
        self.CATEGORIES = {
            "metal": {"metalness": 1.0, "has_k": True, "sss": 0.0, "clearcoat": 0.0, "clearcoat_rough": 0.0},
            "dielectric": {"metalness": 0.0, "has_k": False, "sss": 0.0, "clearcoat": 0.0, "clearcoat_rough": 0.0},
            "organic": {"metalness": 0.0, "has_k": False, "sss": 0.2, "clearcoat": 0.0, "clearcoat_rough": 0.0},
            "translucent": {"metalness": 0.0, "has_k": False, "refraction": 1.0, "clearcoat": 0.0, "clearcoat_rough": 0.0}
        }

        # Color palette for materials where color is not a defining physical property
        self.COLOR_PALETTE = {
            "red": [0.8, 0.05, 0.05],
            "blue": [0.05, 0.15, 0.8],
            "green": [0.05, 0.6, 0.1],
            "yellow": [0.9, 0.8, 0.1],
            "orange": [0.9, 0.4, 0.05],
            "white": [0.9, 0.9, 0.9],
            "black": [0.02, 0.02, 0.02],
            "grey": [0.4, 0.4, 0.4],
            "teal": [0.1, 0.6, 0.6],
            "purple": [0.4, 0.05, 0.6],
        }

        # 2. BASES (The Nouns)
        self.BASES = {
            # --- METALS (Conductors: High K, 0% Diffuse) ---
            "gold": {"cat": "metal", "color": [1.0, 0.85, 0.5], "ior": 0.47, "k": 2.83},
            "silver": {"cat": "metal", "color": [0.97, 0.96, 0.91], "ior": 0.18, "k": 3.42},
            "copper": {"cat": "metal", "color": [0.95, 0.64, 0.54], "ior": 1.1, "k": 2.5},
            "iron": {"cat": "metal", "color": [0.56, 0.57, 0.58], "ior": 2.9, "k": 3.0},
            "aluminum": {"cat": "metal", "color": [0.91, 0.92, 0.92], "ior": 1.2, "k": 7.0},
            "titanium": {"cat": "metal", "color": [0.54, 0.51, 0.47], "ior": 2.16, "k": 3.58},
            "steel": {"cat": "metal", "color": [0.42, 0.43, 0.45], "ior": 2.4, "k": 3.2},
            "brass": {"cat": "metal", "color": [0.88, 0.72, 0.4], "ior": 0.44, "k": 2.4},
            "chrome": {"cat": "metal", "color": [0.55, 0.55, 0.57], "ior": 3.1, "k": 3.3},
            "platinum": {"cat": "metal", "color": [0.68, 0.66, 0.62], "ior": 2.3, "k": 4.1},
            "lead": {"cat": "metal", "color": [0.3, 0.3, 0.32], "ior": 2.0, "k": 3.5},
            "tin": {"cat": "metal", "color": [0.75, 0.75, 0.76], "ior": 1.5, "k": 4.5},
            "nickel": {"cat": "metal", "color": [0.66, 0.6, 0.54], "ior": 2.3, "k": 3.4},
            "cobalt": {"cat": "metal", "color": [0.67, 0.68, 0.69], "ior": 2.2, "k": 4.0},
            "bronze": {"cat": "metal", "color": [0.7, 0.5, 0.3], "ior": 0.5, "k": 3.5},

            # --- STONES & CERAMICS (Dielectrics: High IOR) ---
            "marble": {"cat": "dielectric", "color": [0.9, 0.9, 0.9], "ior": 1.48, "k": 0.0, "sss": 0.1},
            "granite": {"cat": "dielectric", "color": [0.4, 0.4, 0.4], "ior": 1.6, "k": 0.0},
            "concrete": {"cat": "dielectric", "color": [0.5, 0.5, 0.5], "ior": 1.6, "k": 0.0},
            "brick": {"cat": "dielectric", "color": [0.5, 0.2, 0.15], "ior": 1.5, "k": 0.0},
            "porcelain": {"cat": "dielectric", "color": [0.95, 0.95, 0.95], "ior": 1.5, "k": 0.0, "sss": 0.2},
            "terracotta": {"cat": "dielectric", "color": [0.6, 0.3, 0.2], "ior": 1.6, "k": 0.0},
            "slate": {"cat": "dielectric", "color": [0.2, 0.22, 0.25], "ior": 1.55, "k": 0.0},
            "sandstone": {"cat": "dielectric", "color": [0.7, 0.6, 0.45], "ior": 1.5, "k": 0.0},
            "obsidian": {"cat": "dielectric", "color": [0.02, 0.02, 0.03], "ior": 1.48, "k": 0.0},
            "basalt": {"cat": "dielectric", "color": [0.1, 0.1, 0.1], "ior": 1.7, "k": 0.0},

            # --- PLASTICS & SYNTHETICS ---
            "plastic_abs": {"cat": "dielectric", "color": [0.1, 0.1, 0.1], "ior": 1.54, "k": 0.0, "colorable": True},
            "plastic_pvc": {"cat": "dielectric", "color": [0.8, 0.8, 0.8], "ior": 1.52, "k": 0.0, "colorable": True},
            "rubber": {"cat": "dielectric", "color": [0.05, 0.05, 0.05], "ior": 1.51, "k": 0.0, "colorable": True},
            "carbon_fiber": {"cat": "dielectric", "color": [0.02, 0.02, 0.02], "ior": 1.6, "k": 0.0, "anisotropy": 0.5, "clearcoat": 1.0},
            "bakelite": {"cat": "dielectric", "color": [0.2, 0.1, 0.05], "ior": 1.6, "k": 0.0},
            "silicone": {"cat": "dielectric", "color": [0.7, 0.7, 0.7], "ior": 1.43, "k": 0.0, "sss": 0.4, "colorable": True},
            "epoxy_resin": {"cat": "dielectric", "color": [0.8, 0.7, 0.5], "ior": 1.55, "k": 0.0, "sss": 0.3},
            "car_paint": {"cat": "dielectric", "color": [0.5, 0.0, 0.0], "ior": 1.5, "k": 0.0, "clearcoat": 1.0, "metallic_flake": 0.6, "colorable": True},

            # --- FABRICS (Anisotropic/Microfiber logic) ---
            "silk": {"cat": "dielectric", "color": [0.8, 0.2, 0.5], "ior": 1.5, "k": 0.0, "anisotropy": 0.9, "colorable": True, "hint": "shimmering fabric with directional sheen"},
            "cotton": {"cat": "dielectric", "color": [0.9, 0.9, 0.9], "ior": 1.3, "k": 0.0, "rough": 0.95, "colorable": True, "hint": "soft, matte fibrous weave"},
            "velvet": {"cat": "dielectric", "color": [0.1, 0.02, 0.05], "ior": 1.5, "k": 0.0, "sheen": 1.0, "colorable": True, "hint": "deep pile fabric with edge highlights"},

            # --- MISC ---
            "asphalt": {"cat": "dielectric", "color": [0.05, 0.05, 0.05], "ior": 1.55, "k": 0.0, "rough": 0.9, "bump_type": "cracked"},

            # --- ORGANICS (High SSS) ---
            "oak_wood": {"cat": "organic", "color": [0.35, 0.25, 0.15], "ior": 1.5, "k": 0.0},
            "pine_wood": {"cat": "organic", "color": [0.7, 0.5, 0.3], "ior": 1.5, "k": 0.0},
            "mahogany": {"cat": "organic", "color": [0.2, 0.05, 0.02], "ior": 1.5, "k": 0.0},
            "leather_tan": {"cat": "organic", "color": [0.4, 0.2, 0.1], "ior": 1.48, "k": 0.0},
            "leather_black": {"cat": "organic", "color": [0.05, 0.05, 0.05], "ior": 1.5, "k": 0.0},
            "paper": {"cat": "organic", "color": [0.9, 0.9, 0.85], "ior": 1.5, "k": 0.0, "sss": 0.1},
            "cardboard": {"cat": "organic", "color": [0.5, 0.4, 0.3], "ior": 1.5, "k": 0.0},
            "cork": {"cat": "organic", "color": [0.6, 0.4, 0.3], "ior": 1.2, "k": 0.0},
            "clay": {"cat": "organic", "color": [0.5, 0.35, 0.3], "ior": 1.6, "k": 0.0, "sss": 0.15},
            "skin_human": {"cat": "organic", "color": [0.8, 0.6, 0.5], "ior": 1.4, "k": 0.0, "sss": 0.8, "sss_color": [1.0, 0.2, 0.1], "hint": "human skin with deep red subsurface scattering"},

            # --- TRANSLUCENTS (Refraction & Jewels) ---
            "glass": {"cat": "translucent", "color": [1.0, 1.0, 1.0], "ior": 1.52, "k": 0.0},
            "water": {"cat": "translucent", "color": [0.9, 1.0, 1.0], "ior": 1.33, "k": 0.0},
            "ice": {"cat": "translucent", "color": [0.8, 0.9, 1.0], "ior": 1.31, "k": 0.0},
            "diamond": {"cat": "translucent", "color": [1.0, 1.0, 1.0], "ior": 2.42, "k": 0.0},
            "emerald": {"cat": "translucent", "color": [0.1, 0.8, 0.2], "ior": 1.57, "k": 0.0},
            "ruby": {"cat": "translucent", "color": [0.9, 0.0, 0.1], "ior": 1.76, "k": 0.0},
            "amber": {"cat": "translucent", "color": [1.0, 0.6, 0.1], "ior": 1.54, "k": 0.0, "sss": 0.5},
            "honey": {"cat": "translucent", "color": [0.8, 0.5, 0.1], "ior": 1.5, "k": 0.0, "sss": 0.8},
        }

        # 3. FINISHES (Physical Surface State)
        self.FINISHES = {
            "polished": {"rough": 0.02, "anisotropy": 0.0, "bump_scale": 0.0, "noise_scale": 1.0, "hint": "mirror-like and smooth"},
            "matte": {"rough": 0.9, "anisotropy": 0.0, "bump_scale": 0.0, "noise_scale": 1.0, "hint": "dull and non-reflective"},
            "satin": {"rough": 0.25, "anisotropy": 0.1, "bump_scale": 0.02, "noise_scale": 1.0, "hint": "soft semi-gloss sheen"},
            "brushed": {"rough": 0.35, "anisotropy": 0.8, "bump_scale": 0.1, "noise_scale": 0.5, "bump_type": "directional", "hint": "directional micro-scratches"},
            "hammered": {"rough": 0.15, "bump_scale": 0.5, "noise_scale": 2.0, "bump_type": "cellular", "hint": "indented with small craters"}
        }

        # 4. CONDITIONS (Environmental Wear)
        self.CONDITIONS = {
            "clean": {"dirt": 0.0, "wear": 0.0, "hint": "pristine condition"},
            "dusty": {"dirt": 0.6, "wear": 0.1, "hint": "covered in fine grey particles"},
            "rusted": {"dirt": 0.8, "wear": 0.4, "only_for": ["metal"], "hint": "oxidized with flaky corrosion"},
            "scratched": {"dirt": 0.1, "wear": 0.9, "hint": "showing heavy surface abrasions"}
        }

    def _build_entity(self, tech_id, b_name, f_name, c_name, base, category, finish, cond, color_override=None):
        params = {**self.CATEGORIES[category], **base, **finish, **cond}

        if color_override:
            params["color"] = color_override

        # Layered shader logic: promote clearcoat flag into render-ready params
        if params.get("clearcoat", 0.0) > 0:
            params["clearcoat_weight"] = 1.0
            params["clearcoat_rough"] = params.get("clearcoat_rough", 0.03)
            params.setdefault("metallic_flake", 0.0)
        else:
            params["clearcoat_weight"] = 0.0
            params["metallic_flake"] = 0.0

        for key in ("cat", "colorable", "only_for"):
            params.pop(key, None)

        params["variation_seed"] = int(hashlib.md5(tech_id.encode()).hexdigest()[:8], 16)

        return {
            "id": tech_id,
            "metadata": {"base": b_name, "category": category, "finish": f_name, "condition": c_name},
            "parameters": params,
            "semantic_hints": [base.get("hint", b_name), finish["hint"], cond["hint"]]
        }

    def generate(self):
        library = {}

        for b_name, f_name, c_name in product(self.BASES, self.FINISHES, self.CONDITIONS):
            base = self.BASES[b_name]
            category = base["cat"]
            cond = self.CONDITIONS[c_name]

            if "only_for" in cond and category not in cond["only_for"]:
                continue

            finish = self.FINISHES[f_name]

            # For colorable materials, generate one variant per palette color
            if base.get("colorable"):
                for color_name, color_val in self.COLOR_PALETTE.items():
                    tech_id = f"{b_name}_{color_name}_{f_name}_{c_name}"
                    library[tech_id] = self._build_entity(
                        tech_id, b_name, f_name, c_name,
                        base, category, finish, cond, color_override=color_val
                    )
            else:
                tech_id = f"{b_name}_{f_name}_{c_name}"
                library[tech_id] = self._build_entity(
                    tech_id, b_name, f_name, c_name,
                    base, category, finish, cond
                )

        return library

    def export(self, filepath=None):
        filepath = Path(filepath) if filepath else LIBRARY_JSON
        filepath.parent.mkdir(parents=True, exist_ok=True)
        data = self.generate()
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        return data

    def display(self, columns=None, limit=None):
        library = self.generate()
        items = list(library.items())
        if limit:
            items = items[:limit]
        if columns is None:
            columns = ["color", "ior", "rough", "clearcoat_weight"]

        col_w = {c: max(len(c), 8) for c in columns}
        id_w = max(len(tid) for tid, _ in items)

        header = f"{'TECH ID':<{id_w}} | " + " | ".join(f"{c:<{col_w[c]}}" for c in columns)
        print(header)
        print("-" * len(header))
        for tid, entry in items:
            vals = entry["parameters"]
            row = f"{tid:<{id_w}} | " + " | ".join(f"{str(vals.get(c, '')):<{col_w[c]}}" for c in columns)
            print(row)
        print(f"\nTotal: {len(library)} materials")

class CreateMaterials:
    """Builds a USD MaterialX library inside Houdini Solaris from
    neuron_library.json produced by BuildMaterialsData."""

    PARAM_MAP = {
        "color":      "base_color",
        "metalness":  "metalness",
        "ior":        "specular_IOR",
        "rough":      "specular_roughness",
        "anisotropy": "specular_anisotropy",
    }

    def __init__(self, json_path=None):
        import hou
        self.hou = hou

        self.json_path = Path(json_path) if json_path else LIBRARY_JSON
        self.materials_data = self.load_materials_data()

    def load_materials_data(self):
        if not self.json_path.exists():
            raise FileNotFoundError(
                f"Material library not found: {self.json_path}  "
                f"Create Materials data first!"
            )
        with open(self.json_path, "r") as f:
            return json.load(f)

    def _create_builder(self, matlib, mat_id):
        """Create a material subnet with the standard MaterialX node chain."""
        builder = matlib.createNode("subnet", mat_id, run_init_scripts=False)
        builder.setMaterialFlag(True)

        builder.createNode("subinput", "inputs")

        surface = builder.createNode("mtlxstandard_surface", "mtlxstandard_surface")
        surface.setGenericFlag(self.hou.nodeFlag.VopShowCompressedParams, True)
        surface_out = builder.createNode("subnetconnector", "surface_output")
        surface_out.parm("connectorkind").set("output")
        surface_out.parm("parmname").set("surface")
        surface_out.parm("parmlabel").set("surface")
        surface_out.parm("parmtype").set("surface")
        surface_out.setInput(0, surface, 0)

        disp = builder.createNode("mtlxdisplacement", "mtlxdisplacement")
        disp_out = builder.createNode("subnetconnector", "displacement_output")
        disp_out.parm("connectorkind").set("output")
        disp_out.parm("parmname").set("displacement")
        disp_out.parm("parmlabel").set("displacement")
        disp_out.parm("parmtype").set("displacement")
        disp_out.setInput(0, disp, 0)

        builder.layoutChildren()
        return surface

    def _apply_params(self, surface, params):
        """Map JSON parameters onto the mtlxstandard_surface parms."""
        for json_key, mtlx_parm in self.PARAM_MAP.items():
            value = params.get(json_key)
            if value is None:
                continue
            if json_key == "color":
                surface.parmTuple(mtlx_parm).set(value)
            else:
                surface.parm(mtlx_parm).set(float(value))


    def build_material(self, matlib, mat_id, entry):
        surface = self._create_builder(matlib, mat_id)
        self._apply_params(surface, entry.get("parameters", {}))

    def build_library(self):
        list_to_create = ["gold_polished_clean", "rubber_grey_satin_scratched"]

        stage = self.hou.node("/stage")
        matlib = stage.createNode("materiallibrary", "neuron_materials")
        matlib.moveToGoodPosition()

        if list_to_create:
            entries = {k: self.materials_data[k] for k in list_to_create}
        else:
            entries = self.materials_data

        for mat_id, entry in entries.items():
            self.build_material(matlib, mat_id, entry)

        matlib.layoutChildren()
        print(f">> Library complete: {len(entries)} materials built")