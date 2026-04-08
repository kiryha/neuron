"""
Material Generator for Houdini

Run in Cursor Terminal
python -m datagen.materials
"""

import json
import hashlib
import logging
import random
import re
from pathlib import Path
from itertools import product

from .config import LIBRARY_JSON, MATLIB_NODE

logger = logging.getLogger(__name__)
LIST_TO_CREATE = ["gold_polished_clean", "car_paint_red_matte_dusty", "iron_brushed_scratched", 
                  "glass_polished_clean", "glass_matte_clean", "honey_satin_dusty", "concrete_hammered_clean", "rubber_black_polished_scratched"]


class BuildMaterialsData:
    def __init__(self):
        # 1. PHYSICAL CATEGORIES (Shader Models)
        self.CATEGORIES = {
            "metal": {"metalness": 1.0, "has_k": True, "subsurface": 0.0, "coat": 0.0, "coat_roughness": 0.0},
            "dielectric": {"metalness": 0.0, "has_k": False, "subsurface": 0.0, "coat": 0.0, "coat_roughness": 0.0},
            "organic": {"metalness": 0.0, "has_k": False, "subsurface": 0.2, "coat": 0.0, "coat_roughness": 0.0},
            "translucent": {"metalness": 0.0, "has_k": False, "transmission": 1.0, "transmission_dispersion": 1.0, "base_value": 0.0, "coat": 0.0, "coat_roughness": 0.0}
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
            "gold": {"cat": "metal", "base_color": [1.0, 0.85, 0.5], "specular_ior": 0.47, "k": 2.83},
            "silver": {"cat": "metal", "base_color": [0.97, 0.96, 0.91], "specular_ior": 0.18, "k": 3.42},
            "copper": {"cat": "metal", "base_color": [0.95, 0.64, 0.54], "specular_ior": 1.1, "k": 2.5},
            "iron": {"cat": "metal", "base_color": [0.56, 0.57, 0.58], "specular_ior": 2.9, "k": 3.0},
            "aluminum": {"cat": "metal", "base_color": [0.91, 0.92, 0.92], "specular_ior": 1.2, "k": 7.0},
            "titanium": {"cat": "metal", "base_color": [0.54, 0.51, 0.47], "specular_ior": 2.16, "k": 3.58},
            "steel": {"cat": "metal", "base_color": [0.42, 0.43, 0.45], "specular_ior": 2.4, "k": 3.2},
            "brass": {"cat": "metal", "base_color": [0.88, 0.72, 0.4], "specular_ior": 0.44, "k": 2.4},
            "chrome": {"cat": "metal", "base_color": [0.55, 0.55, 0.57], "specular_ior": 3.1, "k": 3.3},
            "platinum": {"cat": "metal", "base_color": [0.68, 0.66, 0.62], "specular_ior": 2.3, "k": 4.1},
            "lead": {"cat": "metal", "base_color": [0.3, 0.3, 0.32], "specular_ior": 2.0, "k": 3.5},
            "tin": {"cat": "metal", "base_color": [0.75, 0.75, 0.76], "specular_ior": 1.5, "k": 4.5},
            "nickel": {"cat": "metal", "base_color": [0.66, 0.6, 0.54], "specular_ior": 2.3, "k": 3.4},
            "cobalt": {"cat": "metal", "base_color": [0.67, 0.68, 0.69], "specular_ior": 2.2, "k": 4.0},
            "bronze": {"cat": "metal", "base_color": [0.7, 0.5, 0.3], "specular_ior": 0.5, "k": 3.5},

            # --- STONES & CERAMICS (Dielectrics: High IOR) ---
            "marble": {"cat": "dielectric", "base_color": [0.9, 0.9, 0.9], "specular_ior": 1.48, "k": 0.0, "subsurface": 0.1},
            "granite": {"cat": "dielectric", "base_color": [0.4, 0.4, 0.4], "specular_ior": 1.6, "k": 0.0, "specular_roughness_min": 0.55},
            "concrete": {"cat": "dielectric", "base_color": [0.5, 0.5, 0.5], "specular_ior": 1.6, "k": 0.0, "specular_roughness_min": 0.68},
            "brick": {"cat": "dielectric", "base_color": [0.5, 0.2, 0.15], "specular_ior": 1.5, "k": 0.0, "specular_roughness_min": 0.74},
            "porcelain": {"cat": "dielectric", "base_color": [0.95, 0.95, 0.95], "specular_ior": 1.5, "k": 0.0, "subsurface": 0.2},
            "terracotta": {"cat": "dielectric", "base_color": [0.6, 0.3, 0.2], "specular_ior": 1.6, "k": 0.0, "specular_roughness_min": 0.72},
            "slate": {"cat": "dielectric", "base_color": [0.2, 0.22, 0.25], "specular_ior": 1.55, "k": 0.0, "specular_roughness_min": 0.65},
            "sandstone": {"cat": "dielectric", "base_color": [0.7, 0.6, 0.45], "specular_ior": 1.5, "k": 0.0, "specular_roughness_min": 0.78},
            "obsidian": {"cat": "dielectric", "base_color": [0.02, 0.02, 0.03], "specular_ior": 1.48, "k": 0.0},
            "basalt": {"cat": "dielectric", "base_color": [0.1, 0.1, 0.1], "specular_ior": 1.7, "k": 0.0, "specular_roughness_min": 0.55},

            # --- PLASTICS & SYNTHETICS ---
            "plastic_abs": {"cat": "dielectric", "base_color": [0.1, 0.1, 0.1], "specular_ior": 1.54, "k": 0.0, "colorable": True},
            "plastic_pvc": {"cat": "dielectric", "base_color": [0.8, 0.8, 0.8], "specular_ior": 1.52, "k": 0.0, "colorable": True},
            "rubber": {"cat": "dielectric", "base_color": [0.05, 0.05, 0.05], "specular_ior": 1.51, "k": 0.0, "colorable": True},
            "carbon_fiber": {"cat": "dielectric", "base_color": [0.02, 0.02, 0.02], "specular_ior": 1.6, "k": 0.0, "specular_anisotropy": 0.5, "coat": 1.0},
            "bakelite": {"cat": "dielectric", "base_color": [0.2, 0.1, 0.05], "specular_ior": 1.6, "k": 0.0},
            "silicone": {"cat": "dielectric", "base_color": [0.7, 0.7, 0.7], "specular_ior": 1.43, "k": 0.0, "subsurface": 0.4, "colorable": True},
            "epoxy_resin": {"cat": "dielectric", "base_color": [0.8, 0.7, 0.5], "specular_ior": 1.55, "k": 0.0, "subsurface": 0.3},
            "car_paint": {"cat": "dielectric", "base_color": [0.5, 0.0, 0.0], "specular_ior": 1.5, "k": 0.0, "coat": 1.0, "metallic_flake": 0.6, "colorable": True},

            # --- FABRICS (Anisotropic/Microfiber logic) ---
            "silk": {"cat": "dielectric", "base_color": [0.8, 0.2, 0.5], "specular_ior": 1.5, "k": 0.0, "specular_anisotropy": 0.9, "colorable": True, "hint": "shimmering fabric with directional sheen"},
            "cotton": {"cat": "dielectric", "base_color": [0.9, 0.9, 0.9], "specular_ior": 1.3, "k": 0.0, "specular_roughness_min": 0.92, "colorable": True, "hint": "soft, matte fibrous weave"},
            "velvet": {"cat": "dielectric", "base_color": [0.1, 0.02, 0.05], "specular_ior": 1.5, "k": 0.0, "sheen": 1.0, "colorable": True, "hint": "deep pile fabric with edge highlights"},

            # --- MISC ---
            "asphalt": {"cat": "dielectric", "base_color": [0.05, 0.05, 0.05], "specular_ior": 1.55, "k": 0.0, "specular_roughness_min": 0.88, "bump_type": "cracked"},

            # --- ORGANICS (High SSS) ---
            "oak_wood": {"cat": "organic", "base_color": [0.35, 0.25, 0.15], "specular_ior": 1.5, "k": 0.0},
            "pine_wood": {"cat": "organic", "base_color": [0.7, 0.5, 0.3], "specular_ior": 1.5, "k": 0.0},
            "mahogany": {"cat": "organic", "base_color": [0.2, 0.05, 0.02], "specular_ior": 1.5, "k": 0.0},
            "leather_tan": {"cat": "organic", "base_color": [0.4, 0.2, 0.1], "specular_ior": 1.48, "k": 0.0},
            "leather_black": {"cat": "organic", "base_color": [0.05, 0.05, 0.05], "specular_ior": 1.5, "k": 0.0},
            "paper": {"cat": "organic", "base_color": [0.9, 0.9, 0.85], "specular_ior": 1.5, "k": 0.0, "subsurface": 0.1, "specular_roughness_min": 0.78},
            "cardboard": {"cat": "organic", "base_color": [0.5, 0.4, 0.3], "specular_ior": 1.5, "k": 0.0, "specular_roughness_min": 0.82},
            "cork": {"cat": "organic", "base_color": [0.6, 0.4, 0.3], "specular_ior": 1.2, "k": 0.0, "specular_roughness_min": 0.85},
            "clay": {"cat": "organic", "base_color": [0.5, 0.35, 0.3], "specular_ior": 1.6, "k": 0.0, "subsurface": 0.15, "specular_roughness_min": 0.55},
            "skin_human": {"cat": "organic", "base_color": [0.8, 0.6, 0.5], "specular_ior": 1.4, "k": 0.0, "subsurface": 0.8, "sss_color": [1.0, 0.2, 0.1], "hint": "human skin with deep red subsurface scattering"},

            # --- TRANSLUCENTS (Refraction & Jewels) ---
            "glass": {"cat": "translucent", "base_color": [1.0, 1.0, 1.0], "specular_ior": 1.52, "k": 0.0},
            "water": {"cat": "translucent", "base_color": [0.9, 1.0, 1.0], "specular_ior": 1.33, "k": 0.0},
            "ice": {"cat": "translucent", "base_color": [0.8, 0.9, 1.0], "specular_ior": 1.31, "k": 0.0},
            "diamond": {"cat": "translucent", "base_color": [1.0, 1.0, 1.0], "specular_ior": 2.42, "k": 0.0, "transmission_dispersion": 55.0},
            "emerald": {"cat": "translucent", "base_color": [0.1, 0.8, 0.2], "specular_ior": 1.57, "k": 0.0, "transmission_dispersion": 40.0},
            "ruby": {"cat": "translucent", "base_color": [0.9, 0.0, 0.1], "specular_ior": 1.76, "k": 0.0, "transmission_dispersion": 42.0},
            "amber": {"cat": "translucent", "base_color": [1.0, 0.6, 0.1], "specular_ior": 1.54, "k": 0.0, "subsurface": 0.5,
                      "transmission_depth": 5.0, "transmission_scatter": [0.6, 0.3, 0.05]},
            "honey": {"cat": "translucent", "base_color": [0.8, 0.5, 0.1], "specular_ior": 1.5, "k": 0.0, "subsurface": 0.8,
                      "transmission_depth": 3.0, "transmission_scatter": [0.8, 0.5, 0.1]},
        }

        # 3. FINISHES (Physical Surface State)
        self.FINISHES = {
            "polished": {"specular_roughness": 0.02, "specular_anisotropy": 0.0, "bump_scale": 0.0, "noise_scale": 1.0, "hint": "mirror-like and smooth"},
            "matte": {"specular_roughness": 0.9, "specular_anisotropy": 0.0, "bump_scale": 0.0, "noise_scale": 1.0, "hint": "dull and non-reflective"},
            "satin": {"specular_roughness": 0.25, "specular_anisotropy": 0.1, "bump_scale": 0.02, "noise_scale": 1.0, "hint": "soft semi-gloss sheen"},
            "brushed": {"specular_roughness": 0.35, "specular_anisotropy": 0.8, "bump_scale": 0.1, "noise_scale": 0.5, "bump_type": "directional", "hint": "directional micro-scratches"},
            "hammered": {"specular_roughness": 0.15, "bump_scale": 0.5, "noise_scale": 2.0, "bump_type": "cellular", "hint": "indented with small craters"}
        }

        # 4. CONDITIONS (Environmental Wear)
        self.CONDITIONS = {
            "clean": {"dirt": 0.0, "wear": 0.0, "hint": "pristine condition"},
            "dusty": {"dirt": 0.6, "wear": 0.1, "hint": "covered in fine grey particles"},
            "rusted": {"dirt": 0.8, "wear": 0.4, "only_for": ["metal"], "hint": "oxidized with flaky corrosion"},
            "scratched": {"dirt": 0.1, "wear": 0.9, "hint": "showing heavy surface abrasions"}
        }

    PARAM_DEFAULTS = {
        "base_value": 1.0,
        "base_color": [0.5, 0.5, 0.5],
        "metalness": 0.0,
        "specular_ior": 1.5,
        "k": 0.0,
        "specular_roughness": 0.5,
        "specular_anisotropy": 0.0,
        "subsurface": 0.0,
        "sss_color": [1.0, 1.0, 1.0],
        "coat": 0.0,
        "coat_roughness": 0.0,
        "sheen": 0.0,
        "transmission": 0.0,
        "transmission_color": [1.0, 1.0, 1.0],
        "transmission_depth": 0.0,
        "transmission_scatter": [0.0, 0.0, 0.0],
        "transmission_dispersion": 0.0,
        "thin_walled": False,
        "bump_scale": 0.0,
        "bump_type": "none",
        "noise_scale": 1.0,
        "dirt": 0.0,
        "wear": 0.0,
    }

    def _build_entity(self, tech_id, b_name, f_name, c_name, base, category, finish, cond, color_override=None):
        params = {**self.PARAM_DEFAULTS, **self.CATEGORIES[category], **base, **finish, **cond}

        # Finishes use metal-centric roughness; porous / fibrous bases need a floor so
        # e.g. hammered concrete stays matte. specular_roughness: 0 = mirror, 1 = diffuse.
        rough_floor = params.pop("specular_roughness_min", None)
        if rough_floor is not None:
            params["specular_roughness"] = max(float(rough_floor), float(params.get("specular_roughness", 0.5)))

        if color_override:
            params["color"] = color_override

        # Layered shader logic: promote clearcoat flag into render-ready params
        if params.get("coat", 0.0) > 0:
            params["clearcoat_weight"] = 1.0
            params["coat_roughness"] = params.get("coat_roughness", 0.03)
            params.setdefault("metallic_flake", 0.0)
        else:
            params["clearcoat_weight"] = 0.0
            params["metallic_flake"] = 0.0

        # Transmission model for translucent materials
        if category == "translucent":
            params["transmission_color"] = params.get("base_color", [1.0, 1.0, 1.0])
            params["base_color"] = [0.0, 0.0, 0.0]

            if "transmission_depth" not in base:
                params["transmission_depth"] = 1.0

            if any(kw in b_name for kw in ("bubble", "window")):
                params["thin_walled"] = True

        for key in ("cat", "colorable", "only_for"):
            params.pop(key, None)

        # Create a high-entropy hash
        hash_obj = hashlib.md5(tech_id.encode())
        seed_float = int(hash_obj.hexdigest()[:8], 16) / float(0xFFFFFFFF)
        params["variation_seed"] = round(seed_float, 6)

        semantic_hints = [base.get("hint", b_name), finish["hint"], cond["hint"]]
        if params.get("transmission", 0.0) > 0:
            semantic_hints.extend(["Refractive", "Translucent"])
            if any(params.get("transmission_scatter", [0, 0, 0])):
                semantic_hints.append("Volumetric")

        return {
            "id": tech_id,
            "metadata": {"base": b_name, "category": category, "finish": f_name, "condition": c_name},
            "parameters": params,
            "semantic_hints": semantic_hints
        }

    def generate(self):

        print(">> Building materials data...")

        library = {}

        for b_name, f_name, c_name in product(self.BASES, self.FINISHES, self.CONDITIONS):
            base = self.BASES[b_name]
            category = base["cat"]
            cond = self.CONDITIONS[c_name]

            if "only_for" in cond and category not in cond["only_for"]:
                continue

            finish = self.FINISHES[f_name]

            if base.get("colorable"):
                for color_name, color_val in self.COLOR_PALETTE.items():
                    tech_id = f"{b_name}_{color_name}_{f_name}_{c_name}"
                    if LIST_TO_CREATE and tech_id not in LIST_TO_CREATE:
                        continue
                    library[tech_id] = self._build_entity(
                        tech_id, b_name, f_name, c_name,
                        base, category, finish, cond, color_override=color_val
                    )
            else:
                tech_id = f"{b_name}_{f_name}_{c_name}"
                if LIST_TO_CREATE and tech_id not in LIST_TO_CREATE:
                    continue
                library[tech_id] = self._build_entity(
                    tech_id, b_name, f_name, c_name,
                    base, category, finish, cond
                )

        # Save to JSON
        with open(LIBRARY_JSON, "w") as f:
            json.dump(library, f, indent=4)

        print(">> Materials data built")
        
        return library


class BuildPrompts:
    """Generates natural-language labels for every material in neuron_library.json.

    Three-step pipeline per entry:
        A. Token Mapping    - expands brief semantic hints into richer noun phrases.
        B. Template Select  - randomly picks from sentence structures (seeded RNG).
        C. Assembly         - injects expanded tokens, validates grammar artefacts.
    """

    DEFAULT_SEED = 42

    # ── Step A: Token Mapping ───────────────────────────────────
    # Expands brief semantic_hints into richer descriptions.  Entries that are
    # already multi-word (e.g. "human skin with deep red subsurface scattering")
    # pass through unchanged because they won't match any key here.

    TOKEN_MAP = {
        # --- Metals ---
        "gold":      "precious 24k gold metal",
        "silver":    "refined sterling silver metal",
        "copper":    "warm reddish copper metal",
        "iron":      "raw industrial iron",
        "aluminum":  "lightweight aluminum metal",
        "titanium":  "aerospace-grade titanium metal",
        "steel":     "structural carbon steel",
        "brass":     "warm golden brass alloy",
        "chrome":    "highly reflective chrome metal",
        "platinum":  "rare platinum metal",
        "lead":      "dense heavy lead metal",
        "tin":       "malleable tin metal",
        "nickel":    "hardened nickel metal",
        "cobalt":    "deep blue-grey cobalt metal",
        "bronze":    "aged copper-tin bronze alloy",

        # --- Stones & Ceramics ---
        "marble":     "veined natural marble stone",
        "granite":    "speckled granite stone",
        "concrete":   "industrial poured concrete",
        "brick":      "kiln-fired clay brick",
        "porcelain":  "fine white porcelain ceramic",
        "terracotta": "earthy terracotta clay",
        "slate":      "layered dark slate stone",
        "sandstone":  "natural sedimentary sandstone",
        "obsidian":   "volcanic obsidian glass",
        "basalt":     "dark volcanic basalt rock",

        # --- Plastics & Synthetics ---
        "plastic_abs":  "ABS plastic polymer",
        "plastic_pvc":  "PVC plastic polymer",
        "rubber":       "vulcanized rubber",
        "carbon_fiber": "woven carbon fiber composite",
        "bakelite":     "vintage bakelite resin",
        "silicone":     "flexible silicone polymer",
        "epoxy_resin":  "cast epoxy resin",
        "car_paint":    "automotive car paint",

        # --- Organics ---
        "oak_wood":      "natural oak hardwood",
        "pine_wood":     "light-grained pine wood",
        "mahogany":      "rich dark mahogany wood",
        "leather_tan":   "tan leather hide",
        "leather_black": "black leather hide",
        "paper":         "thin cellulose paper",
        "cardboard":     "corrugated cardboard",
        "cork":          "natural cork bark",
        "clay":          "moldable wet clay",

        # --- Translucents ---
        "glass":   "transparent optical glass",
        "water":   "clear liquid water",
        "ice":     "frozen crystalline ice",
        "diamond": "brilliant-cut diamond gemstone",
        "emerald": "deep green emerald gemstone",
        "ruby":    "vivid red ruby gemstone",
        "amber":   "fossilized amber resin",
        "honey":   "viscous golden honey",

        # --- Misc ---
        "asphalt": "weathered road asphalt",

        # --- Condition normalisation (makes "pristine condition" predicate-safe) ---
        "pristine condition": "in pristine condition",
    }

    # ── Step B: Sentence Templates ──────────────────────────────
    # Base (the noun) is placed early in every template so generative models
    # prioritise the core material over modifiers.

    TEMPLATES = [
        # Direct
        "A close-up view of {base} with a {finish} surface, {condition}.",
        # Descriptive
        "Detailed 3D render showing a {base} material with {finish} texture, {condition}.",
        # Cinematic
        "Macro photography of {base}. The surface displays {finish} and is {condition}.",
        # Technical
        "High-fidelity PBR material study: {base} exhibiting {finish} properties, {condition}.",
        # Studio
        "{base} under controlled studio lighting, {finish} surface detail, {condition}.",
        # Photorealistic
        "Photorealistic rendering of {base} with {finish} qualities, {condition}.",
    ]

    def __init__(self, json_path=None, seed=None, overwrite=False):
        self.json_path = Path(json_path) if json_path else LIBRARY_JSON
        self.seed = seed if seed is not None else self.DEFAULT_SEED
        self.overwrite = overwrite

    # ── hint processing ─────────────────────────────────────────

    def _expand(self, token: str) -> str:
        """Look up *token* in the expansion map; return it unchanged if absent."""
        return self.TOKEN_MAP.get(token, token)

    def _extract_color(self, tech_id: str, metadata: dict) -> str | None:
        """Detect an embedded palette colour in colorable-material IDs.

        Non-colorable ID layout:  {base}_{finish}_{condition}
        Colorable ID layout:      {base}_{color}_{finish}_{condition}
        """
        prefix = metadata["base"] + "_"
        suffix = "_" + metadata["finish"] + "_" + metadata["condition"]
        if tech_id.startswith(prefix) and tech_id.endswith(suffix):
            middle = tech_id[len(prefix):-len(suffix)]
            if middle:
                return middle.replace("_", " ")
        return None

    def _validate(self, text: str) -> str:
        """Remove double spaces, stray commas, and ensure capitalisation."""
        text = re.sub(r" {2,}", " ", text)
        text = re.sub(r",\s*\.", ".", text)
        text = re.sub(r",\s*$", "", text)
        text = text.strip()
        if text:
            text = text[0].upper() + text[1:]
        return text

    # ── Step C: label construction ──────────────────────────────

    def _build_label(self, entry: dict, rng: random.Random) -> str:
        hints = entry["semantic_hints"]
        metadata = entry["metadata"]
        tech_id = entry["id"]

        base = self._expand(hints[0])
        finish = self._expand(hints[1])
        condition = self._expand(hints[2])

        color = self._extract_color(tech_id, metadata)
        if color:
            base = f"{color} {base}"

        template = rng.choice(self.TEMPLATES)
        label = template.format(base=base, finish=finish, condition=condition)
        return self._validate(label)

    def generate(self) -> dict:
        """Process every entry in *neuron_library.json*, write back, return the dict."""

        print(">> Building prompts...")

        if not self.json_path.exists():
            raise FileNotFoundError(
                f"Material library not found: {self.json_path}\n"
                "Run  python -m datagen.materials  first to generate it."
            )

        with open(self.json_path, "r") as f:
            library = json.load(f)

        rng = random.Random(self.seed)
        generated, skipped = 0, 0

        for tech_id, entry in library.items():
            if entry.get("semantic_label") and not self.overwrite:
                skipped += 1
                rng.choice(self.TEMPLATES)      # advance RNG to keep determinism
                continue
            entry["semantic_label"] = self._build_label(entry, rng)
            generated += 1

        with open(self.json_path, "w") as f:
            json.dump(library, f, indent=4)

        logger.info("Label generation complete: %d generated, %d skipped", generated, skipped)

        print(">> Prompts built")

        return library


class BuildMaterials:
    """Builds a USD MaterialX library inside Houdini Solaris from
    neuron_library.json produced by BuildMaterialsData."""

    PARAM_MAP = {
        "base_color":      "base_color",
        "metalness":  "metalness",
        "specular_ior":        "specular_IOR",
        "specular_roughness":      "specular_roughness",
        "specular_anisotropy": "specular_anisotropy",
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
            if json_key == "base_color":
                surface.parmTuple(mtlx_parm).set(value)
            else:
                surface.parm(mtlx_parm).set(float(value))

    def build_material(self, matlib, mat_id, entry):
        existing = matlib.node(mat_id)
        if existing:
            surface = existing.node("mtlxstandard_surface")
            if surface:
                self._apply_params(surface, entry.get("parameters", {}))
                return
        surface = self._create_builder(matlib, mat_id)
        self._apply_params(surface, entry.get("parameters", {}))

    def build_library(self):

        print(">> Building library...")

        stage = self.hou.node("/stage")
        matlib = stage.node(MATLIB_NODE)
        if matlib is None:
            matlib = stage.createNode("materiallibrary", MATLIB_NODE)
            matlib.moveToGoodPosition()

        if LIST_TO_CREATE:
            entries = {k: self.materials_data[k] for k in LIST_TO_CREATE}
        else:
            entries = self.materials_data

        created, updated = 0, 0
        for mat_id, entry in entries.items():
            is_update = matlib.node(mat_id) is not None
            self.build_material(matlib, mat_id, entry)
            if is_update:
                updated += 1
            else:
                created += 1

        matlib.layoutChildren()

        print(f">> Library built: {created} created, {updated} updated")