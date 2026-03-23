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
    """Batch-builds a USD MaterialX library inside Houdini Solaris from the
    neuron_library.json manifest produced by BuildMaterialsData.

    Idempotent: re-running will skip materials whose nodes already exist.
    """

    MATLIB_PATH = "/stage/materials"
    SURFACE_NODE = "standard_surface1"

    # JSON key -> mtlxstandard_surface parm name
    PARAM_MAP = {
        "color":      "base_color",
        "metalness":  "metalness",
        "ior":        "specular_ior",
        "k":          "specular_extinction",
        "rough":      "specular_roughness",
        "anisotropy": "specular_anisotropy",
    }

    def __init__(self, json_path=None):
        import hou
        self._hou = hou

        self._json_path = Path(json_path) if json_path else LIBRARY_JSON
        self._library = self._load_library()

    def _load_library(self):
        if not self._json_path.exists():
            raise FileNotFoundError(
                f"Material library not found: {self._json_path}  "
                f"(run BuildMaterialsData.export() first)"
            )
        with open(self._json_path, "r") as f:
            return json.load(f)

    def _ensure_matlib(self):
        """Return the /stage/materials materiallibrary LOP, creating it if needed."""
        hou = self._hou
        node = hou.node(self.MATLIB_PATH)
        if node is not None:
            return node

        stage = hou.node("/stage")
        if stage is None:
            raise RuntimeError("No /stage context found — open a Solaris/LOPs desktop first")

        node = stage.createNode("materiallibrary", "materials")
        node.moveToGoodPosition()
        logger.info("Created %s", self.MATLIB_PATH)
        return node

    def _apply_params(self, surface_node, params):
        """Map JSON parameters onto the mtlxstandard_surface node."""
        for json_key, mtlx_parm in self.PARAM_MAP.items():
            value = params.get(json_key)
            if value is None:
                continue

            parm = surface_node.parm(mtlx_parm)
            parm_tuple = surface_node.parmTuple(mtlx_parm)

            if json_key == "color" and parm_tuple is not None:
                parm_tuple.set(value)
            elif parm is not None:
                parm.set(float(value))
            else:
                logger.warning(
                    "Parm '%s' not found on %s — skipping",
                    mtlx_parm, surface_node.path(),
                )

        if params.get("has_k"):
            fresnel_parm = surface_node.parm("specular_fresnel_mode")
            if fresnel_parm is not None:
                fresnel_parm.set(1)
            else:
                logger.debug(
                    "No specular_fresnel_mode parm on %s — MaterialX version "
                    "may not support complex IOR toggle",
                    surface_node.path(),
                )

    def _build_material(self, matlib, mat_id, entry):
        """Add a material slot to the materiallibrary and configure its shader.

        The materiallibrary's children live in a VOP context, so we add
        entries via the multiparm and then work with the auto-created
        VOP subnet that Houdini populates with default MaterialX nodes.
        """
        params = entry.get("parameters", {})

        if matlib.node(mat_id) is not None:
            logger.debug("Skipping existing material: %s", mat_id)
            return

        # Add a new multiparm slot — this triggers child-subnet creation
        num_parm = matlib.parm("num_materials")
        idx = num_parm.eval() + 1
        num_parm.set(idx)

        # Point the slot at the right USD prim path
        self._set_parm(matlib, f"matpathprefix{idx}", "/materials/")
        self._set_parm(matlib, f"matpath{idx}", mat_id)

        # Locate the auto-created child builder (name stored in matnode parm)
        node_parm = matlib.parm(f"matnode{idx}")
        auto_name = node_parm.eval() if node_parm else None
        builder = matlib.node(auto_name) if auto_name else None

        if builder is None:
            # Fallback: create a VOP subnet and wire up a default MaterialX chain
            builder = matlib.createNode("subnet", mat_id)
            self._create_mtlx_network(builder)
        else:
            builder.setName(mat_id, unique_name=True)

        if node_parm:
            node_parm.set(builder.name())

        # The auto-created builder should already contain standard_surface1
        surface = builder.node(self.SURFACE_NODE)
        if surface is None:
            surface = self._create_mtlx_network(builder)

        self._apply_params(surface, params)
        builder.layoutChildren()
        logger.info("Built material: %s", mat_id)

    @staticmethod
    def _set_parm(node, name, value):
        parm = node.parm(name)
        if parm is not None:
            parm.set(value)
        else:
            logger.warning("Parm '%s' not found on %s", name, node.path())

    def _create_mtlx_network(self, builder):
        """Build a minimal MaterialX VOP chain inside a builder subnet."""
        surface = builder.createNode("mtlxstandard_surface", self.SURFACE_NODE)
        surfmat = builder.createNode("mtlxsurfacematerial", "surfacematerial1")
        surfmat.setInput(0, surface, 0)

        output = builder.node("suboutput1")
        if output:
            output.setInput(0, surfmat, 0)

        return surface

    def build_library(self):
        """Main entry point — iterate the manifest and build every material."""

        list_to_create = ["gold_polished_clean"]

        matlib = self._ensure_matlib()
        built, skipped, errors = 0, 0, 0

        if list_to_create:
            entries = {k: self._library[k] for k in list_to_create if k in self._library}
            missing = set(list_to_create) - set(entries)
            if missing:
                logger.warning("IDs not found in manifest: %s", missing)
        else:
            entries = self._library

        for mat_id, entry in entries.items():
            try:
                if matlib.node(mat_id) is not None:
                    skipped += 1
                    continue
                self._build_material(matlib, mat_id, entry)
                built += 1
            except Exception:
                errors += 1
                logger.exception("Failed to build material '%s'", mat_id)

        matlib.layoutChildren()
        logger.info(
            "Library complete — %d built, %d skipped, %d errors (total manifest: %d)",
            built, skipped, errors, len(entries),
        )
        return {"built": built, "skipped": skipped, "errors": errors}