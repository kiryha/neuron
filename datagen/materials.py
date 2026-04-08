"""
Material data generator for Neuron (deterministic JSON for Houdini / MaterialX wiring).

Authoring data lives in ``MaterialSpec`` (frozen). Run:

    BuildMaterialsData().generate()
    BuildMaterialsData().generate(subset_ids={"gold_polished_clean", ...})  # optional debug subset
"""

from __future__ import annotations

import hashlib
import json
import logging
import random
import re
from copy import deepcopy
from itertools import product
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .config import LIBRARY_JSON, MATLIB_NODE

logger = logging.getLogger(__name__)

# Keys written to shader_parameters (render-facing only).
SHADER_PARAMETER_KEYS = (
    "base_value",
    "base_color",
    "metalness",
    "specular_ior",
    "k",
    "specular_roughness",
    "specular_anisotropy",
    "subsurface",
    "sss_color",
    "coat",
    "coat_roughness",
    "sheen",
    "transmission",
    "transmission_color",
    "transmission_depth",
    "transmission_scatter",
    "transmission_dispersion",
    "thin_walled",
    "clearcoat_weight",
    "metallic_flake",
)

PROCEDURAL_PARAMETER_KEYS = (
    "variation_seed",
    "bump_scale",
    "bump_type",
    "noise_scale",
    "dirt",
    "wear",
)

VALID_CATEGORIES = frozenset({"metal", "dielectric", "organic", "translucent"})
VALID_BUMP_TYPES = frozenset({"none", "directional", "cellular", "cracked"})

# `k` is stored for conductor / metal shading metadata for future MaterialX networks; it is not
# guaranteed to map 1:1 to a specific published MaterialX node until the shader graph is finalized.

_SHADER_DEFAULTS: dict[str, Any] = {
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
    "clearcoat_weight": 0.0,
    "metallic_flake": 0.0,
}

_PROCEDURAL_DEFAULTS: dict[str, Any] = {
    "bump_scale": 0.0,
    "bump_type": "none",
    "noise_scale": 1.0,
    "dirt": 0.0,
    "wear": 0.0,
}

_CATEGORY_SHADER_DEFAULTS: dict[str, dict[str, Any]] = {
    "metal": {
        "metalness": 1.0,
        "subsurface": 0.0,
        "coat": 0.0,
        "coat_roughness": 0.0,
        "transmission": 0.0,
        "transmission_dispersion": 0.0,
    },
    "dielectric": {
        "metalness": 0.0,
        "subsurface": 0.0,
        "coat": 0.0,
        "coat_roughness": 0.0,
        "transmission": 0.0,
        "transmission_dispersion": 0.0,
    },
    "organic": {
        "metalness": 0.0,
        "subsurface": 0.2,
        "coat": 0.0,
        "coat_roughness": 0.0,
        "transmission": 0.0,
        "transmission_dispersion": 0.0,
    },
    "translucent": {
        "metalness": 0.0,
        "transmission": 1.0,
        "transmission_dispersion": 0.0,
        "base_value": 0.0,
        "coat": 0.0,
        "coat_roughness": 0.0,
    },
}

_COLOR_PALETTE: dict[str, list[float]] = {
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

# Compatibility: skip combos that are physically silly or need artist-only overrides.
_POLISHED_DISALLOWED_BASES = frozenset(
    {
        "concrete",
        "brick",
        "paper",
        "cardboard",
        "cork",
        "cotton",
        "sandstone",
        "terracotta",
        "asphalt",
        "clay",
    }
)

_HAMMERED_DISALLOWED_BASES = frozenset(
    {
        "glass",
        "glass_window",
        "water",
        "ice",
        "diamond",
        "emerald",
        "ruby",
        "amber",
        "honey",
        "paper",
        "cardboard",
        "cork",
        "cotton",
        "silk",
        "velvet",
        "skin_human",
    }
)

_SATIN_DISALLOWED_BASES = frozenset({"water"})

# Minimum specular roughness after merging finishes (material-class floors).
_SPECULAR_ROUGHNESS_FLOOR_BY_BASE: dict[str, float] = {
    "rubber": 0.15,
    "silicone": 0.12,
}

# Bases that always keep volumetric / transmission character regardless of finish adjective.
_TRANSMISSION_LOCK_BASES = frozenset({"honey", "amber"})


def _deep_freeze(obj: Any) -> Any:
    if isinstance(obj, dict):
        return MappingProxyType({k: _deep_freeze(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return tuple(_deep_freeze(x) for x in obj)
    return obj


def _freeze_root_mapping(d: dict[str, Any]) -> MappingProxyType:
    return MappingProxyType({k: _deep_freeze(v) for k, v in d.items()})


_BASE_TOKEN_MAP_RAW: dict[str, str] = {
    "gold": "precious 24k gold metal",
    "silver": "refined sterling silver metal",
    "copper": "warm reddish copper metal",
    "iron": "raw industrial iron",
    "aluminum": "lightweight aluminum metal",
    "titanium": "aerospace-grade titanium metal",
    "steel": "structural carbon steel",
    "brass": "warm golden brass alloy",
    "chrome": "highly reflective chrome metal",
    "platinum": "rare platinum metal",
    "lead": "dense heavy lead metal",
    "tin": "malleable tin metal",
    "nickel": "hardened nickel metal",
    "cobalt": "deep blue-grey cobalt metal",
    "bronze": "aged copper-tin bronze alloy",
    "marble": "veined natural marble stone",
    "granite": "speckled granite stone",
    "concrete": "industrial poured concrete",
    "brick": "kiln-fired clay brick",
    "porcelain": "fine white porcelain ceramic",
    "terracotta": "earthy terracotta clay",
    "slate": "layered dark slate stone",
    "sandstone": "natural sedimentary sandstone",
    "obsidian": "volcanic obsidian glass",
    "basalt": "dark volcanic basalt rock",
    "plastic_abs": "ABS plastic polymer",
    "plastic_pvc": "PVC plastic polymer",
    "rubber": "vulcanized rubber",
    "carbon_fiber": "woven carbon fiber composite",
    "bakelite": "vintage bakelite resin",
    "silicone": "flexible silicone polymer",
    "epoxy_resin": "cast epoxy resin",
    "car_paint": "automotive car paint",
    "oak_wood": "natural oak hardwood",
    "pine_wood": "light-grained pine wood",
    "mahogany": "rich dark mahogany wood",
    "leather_tan": "tan leather hide",
    "leather_black": "black leather hide",
    "paper": "thin cellulose paper",
    "cardboard": "corrugated cardboard",
    "cork": "natural cork bark",
    "clay": "moldable wet clay",
    "glass": "transparent optical glass",
    "glass_window": "thin plate glass window",
    "water": "clear liquid water",
    "ice": "frozen crystalline ice",
    "diamond": "brilliant-cut diamond gemstone",
    "emerald": "deep green emerald gemstone",
    "ruby": "vivid red ruby gemstone",
    "amber": "fossilized amber resin",
    "honey": "viscous golden honey",
    "asphalt": "weathered road asphalt",
    "silk": "shimmering silk fabric",
    "cotton": "woven cotton fabric",
    "velvet": "deep-pile velvet fabric",
    "skin_human": "human skin with subsurface scattering",
}


# --- Authoring tables (physical vs semantic separated) ---

_BASES: dict[str, dict[str, Any]] = {
    "gold": {
        "cat": "metal",
        "physical": {"base_color": [1.0, 0.85, 0.5], "specular_ior": 0.47, "k": 2.83},
        "semantic": {"base_phrase": "precious 24k gold metal"},
    },
    "silver": {
        "cat": "metal",
        "physical": {"base_color": [0.97, 0.96, 0.91], "specular_ior": 0.18, "k": 3.42},
        "semantic": {"base_phrase": "refined sterling silver metal"},
    },
    "copper": {
        "cat": "metal",
        "physical": {"base_color": [0.95, 0.64, 0.54], "specular_ior": 1.1, "k": 2.5},
        "semantic": {"base_phrase": "warm reddish copper metal"},
    },
    "iron": {
        "cat": "metal",
        "physical": {"base_color": [0.56, 0.57, 0.58], "specular_ior": 2.9, "k": 3.0},
        "semantic": {"base_phrase": "raw industrial iron"},
    },
    "aluminum": {
        "cat": "metal",
        "physical": {"base_color": [0.91, 0.92, 0.92], "specular_ior": 1.2, "k": 7.0},
        "semantic": {"base_phrase": "lightweight aluminum metal"},
    },
    "titanium": {
        "cat": "metal",
        "physical": {"base_color": [0.54, 0.51, 0.47], "specular_ior": 2.16, "k": 3.58},
        "semantic": {"base_phrase": "aerospace-grade titanium metal"},
    },
    "steel": {
        "cat": "metal",
        "physical": {"base_color": [0.42, 0.43, 0.45], "specular_ior": 2.4, "k": 3.2},
        "semantic": {"base_phrase": "structural carbon steel"},
    },
    "brass": {
        "cat": "metal",
        "physical": {"base_color": [0.88, 0.72, 0.4], "specular_ior": 0.44, "k": 2.4},
        "semantic": {"base_phrase": "warm golden brass alloy"},
    },
    "chrome": {
        "cat": "metal",
        "physical": {"base_color": [0.55, 0.55, 0.57], "specular_ior": 3.1, "k": 3.3},
        "semantic": {"base_phrase": "highly reflective chrome metal"},
    },
    "platinum": {
        "cat": "metal",
        "physical": {"base_color": [0.68, 0.66, 0.62], "specular_ior": 2.3, "k": 4.1},
        "semantic": {"base_phrase": "rare platinum metal"},
    },
    "lead": {
        "cat": "metal",
        "physical": {"base_color": [0.3, 0.3, 0.32], "specular_ior": 2.0, "k": 3.5},
        "semantic": {"base_phrase": "dense heavy lead metal"},
    },
    "tin": {
        "cat": "metal",
        "physical": {"base_color": [0.75, 0.75, 0.76], "specular_ior": 1.5, "k": 4.5},
        "semantic": {"base_phrase": "malleable tin metal"},
    },
    "nickel": {
        "cat": "metal",
        "physical": {"base_color": [0.66, 0.6, 0.54], "specular_ior": 2.3, "k": 3.4},
        "semantic": {"base_phrase": "hardened nickel metal"},
    },
    "cobalt": {
        "cat": "metal",
        "physical": {"base_color": [0.67, 0.68, 0.69], "specular_ior": 2.2, "k": 4.0},
        "semantic": {"base_phrase": "deep blue-grey cobalt metal"},
    },
    "bronze": {
        "cat": "metal",
        "physical": {"base_color": [0.7, 0.5, 0.3], "specular_ior": 0.5, "k": 3.5},
        "semantic": {"base_phrase": "aged copper-tin bronze alloy"},
    },
    "marble": {
        "cat": "dielectric",
        "physical": {"base_color": [0.9, 0.9, 0.9], "specular_ior": 1.48, "k": 0.0, "subsurface": 0.1},
        "semantic": {"base_phrase": "veined natural marble stone"},
    },
    "granite": {
        "cat": "dielectric",
        "physical": {"base_color": [0.4, 0.4, 0.4], "specular_ior": 1.6, "k": 0.0, "specular_roughness_min": 0.55},
        "semantic": {"base_phrase": "speckled granite stone"},
    },
    "concrete": {
        "cat": "dielectric",
        "physical": {"base_color": [0.5, 0.5, 0.5], "specular_ior": 1.6, "k": 0.0, "specular_roughness_min": 0.68},
        "semantic": {"base_phrase": "industrial poured concrete"},
    },
    "brick": {
        "cat": "dielectric",
        "physical": {"base_color": [0.5, 0.2, 0.15], "specular_ior": 1.5, "k": 0.0, "specular_roughness_min": 0.74},
        "semantic": {"base_phrase": "kiln-fired clay brick"},
    },
    "porcelain": {
        "cat": "dielectric",
        "physical": {"base_color": [0.95, 0.95, 0.95], "specular_ior": 1.5, "k": 0.0, "subsurface": 0.2},
        "semantic": {"base_phrase": "fine white porcelain ceramic"},
    },
    "terracotta": {
        "cat": "dielectric",
        "physical": {"base_color": [0.6, 0.3, 0.2], "specular_ior": 1.6, "k": 0.0, "specular_roughness_min": 0.72},
        "semantic": {"base_phrase": "earthy terracotta clay"},
    },
    "slate": {
        "cat": "dielectric",
        "physical": {"base_color": [0.2, 0.22, 0.25], "specular_ior": 1.55, "k": 0.0, "specular_roughness_min": 0.65},
        "semantic": {"base_phrase": "layered dark slate stone"},
    },
    "sandstone": {
        "cat": "dielectric",
        "physical": {"base_color": [0.7, 0.6, 0.45], "specular_ior": 1.5, "k": 0.0, "specular_roughness_min": 0.78},
        "semantic": {"base_phrase": "natural sedimentary sandstone"},
    },
    "obsidian": {
        "cat": "dielectric",
        "physical": {"base_color": [0.02, 0.02, 0.03], "specular_ior": 1.48, "k": 0.0},
        "semantic": {"base_phrase": "volcanic obsidian glass"},
    },
    "basalt": {
        "cat": "dielectric",
        "physical": {"base_color": [0.1, 0.1, 0.1], "specular_ior": 1.7, "k": 0.0, "specular_roughness_min": 0.55},
        "semantic": {"base_phrase": "dark volcanic basalt rock"},
    },
    "plastic_abs": {
        "cat": "dielectric",
        "colorable": True,
        "physical": {"base_color": [0.1, 0.1, 0.1], "specular_ior": 1.54, "k": 0.0},
        "semantic": {"base_phrase": "ABS plastic polymer"},
    },
    "plastic_pvc": {
        "cat": "dielectric",
        "colorable": True,
        "physical": {"base_color": [0.8, 0.8, 0.8], "specular_ior": 1.52, "k": 0.0},
        "semantic": {"base_phrase": "PVC plastic polymer"},
    },
    "rubber": {
        "cat": "dielectric",
        "colorable": True,
        "physical": {"base_color": [0.05, 0.05, 0.05], "specular_ior": 1.51, "k": 0.0},
        "semantic": {"base_phrase": "vulcanized rubber"},
    },
    "carbon_fiber": {
        "cat": "dielectric",
        "physical": {"base_color": [0.02, 0.02, 0.02], "specular_ior": 1.6, "k": 0.0, "specular_anisotropy": 0.5, "coat": 1.0},
        "semantic": {"base_phrase": "woven carbon fiber composite"},
    },
    "bakelite": {
        "cat": "dielectric",
        "physical": {"base_color": [0.2, 0.1, 0.05], "specular_ior": 1.6, "k": 0.0},
        "semantic": {"base_phrase": "vintage bakelite resin"},
    },
    "silicone": {
        "cat": "dielectric",
        "colorable": True,
        "physical": {"base_color": [0.7, 0.7, 0.7], "specular_ior": 1.43, "k": 0.0, "subsurface": 0.4},
        "semantic": {"base_phrase": "flexible silicone polymer"},
    },
    "epoxy_resin": {
        "cat": "dielectric",
        "physical": {"base_color": [0.8, 0.7, 0.5], "specular_ior": 1.55, "k": 0.0, "subsurface": 0.3},
        "semantic": {"base_phrase": "cast epoxy resin"},
    },
    "car_paint": {
        "cat": "dielectric",
        "colorable": True,
        "physical": {
            "base_color": [0.5, 0.0, 0.0],
            "specular_ior": 1.5,
            "k": 0.0,
            "coat": 1.0,
            "metallic_flake": 0.6,
        },
        "semantic": {"base_phrase": "automotive car paint"},
    },
    "silk": {
        "cat": "dielectric",
        "colorable": True,
        "physical": {"base_color": [0.8, 0.2, 0.5], "specular_ior": 1.5, "k": 0.0, "specular_anisotropy": 0.9},
        "semantic": {"base_phrase": "shimmering silk fabric"},
    },
    "cotton": {
        "cat": "dielectric",
        "colorable": True,
        "physical": {"base_color": [0.9, 0.9, 0.9], "specular_ior": 1.3, "k": 0.0, "specular_roughness_min": 0.92},
        "semantic": {"base_phrase": "woven cotton fabric"},
    },
    "velvet": {
        "cat": "dielectric",
        "colorable": True,
        "physical": {"base_color": [0.1, 0.02, 0.05], "specular_ior": 1.5, "k": 0.0, "sheen": 1.0},
        "semantic": {"base_phrase": "deep-pile velvet fabric"},
    },
    "asphalt": {
        "cat": "dielectric",
        "physical": {
            "base_color": [0.05, 0.05, 0.05],
            "specular_ior": 1.55,
            "k": 0.0,
            "specular_roughness_min": 0.88,
            "bump_type": "cracked",
            "bump_scale": 0.35,
        },
        "semantic": {"base_phrase": "weathered road asphalt"},
        # Re-assert macro road breakup after finish/condition procedural merges.
        "procedural_layer": {"bump_type": "cracked", "bump_scale": 0.35},
    },
    "oak_wood": {
        "cat": "organic",
        "physical": {"base_color": [0.35, 0.25, 0.15], "specular_ior": 1.5, "k": 0.0},
        "semantic": {"base_phrase": "natural oak hardwood"},
    },
    "pine_wood": {
        "cat": "organic",
        "physical": {"base_color": [0.7, 0.5, 0.3], "specular_ior": 1.5, "k": 0.0},
        "semantic": {"base_phrase": "light-grained pine wood"},
    },
    "mahogany": {
        "cat": "organic",
        "physical": {"base_color": [0.2, 0.05, 0.02], "specular_ior": 1.5, "k": 0.0},
        "semantic": {"base_phrase": "rich dark mahogany wood"},
    },
    "leather_tan": {
        "cat": "organic",
        "physical": {"base_color": [0.4, 0.2, 0.1], "specular_ior": 1.48, "k": 0.0},
        "semantic": {"base_phrase": "tan leather hide"},
    },
    "leather_black": {
        "cat": "organic",
        "physical": {"base_color": [0.05, 0.05, 0.05], "specular_ior": 1.5, "k": 0.0},
        "semantic": {"base_phrase": "black leather hide"},
    },
    "paper": {
        "cat": "organic",
        "physical": {"base_color": [0.9, 0.9, 0.85], "specular_ior": 1.5, "k": 0.0, "subsurface": 0.1, "specular_roughness_min": 0.78},
        "semantic": {"base_phrase": "thin cellulose paper"},
    },
    "cardboard": {
        "cat": "organic",
        "physical": {"base_color": [0.5, 0.4, 0.3], "specular_ior": 1.5, "k": 0.0, "specular_roughness_min": 0.82},
        "semantic": {"base_phrase": "corrugated cardboard"},
    },
    "cork": {
        "cat": "organic",
        "physical": {"base_color": [0.6, 0.4, 0.3], "specular_ior": 1.2, "k": 0.0, "specular_roughness_min": 0.85},
        "semantic": {"base_phrase": "natural cork bark"},
    },
    "clay": {
        "cat": "organic",
        "physical": {"base_color": [0.5, 0.35, 0.3], "specular_ior": 1.6, "k": 0.0, "subsurface": 0.15, "specular_roughness_min": 0.55},
        "semantic": {"base_phrase": "moldable wet clay"},
    },
    "skin_human": {
        "cat": "organic",
        "physical": {
            "base_color": [0.8, 0.6, 0.5],
            "specular_ior": 1.4,
            "k": 0.0,
            "subsurface": 0.8,
            "sss_color": [1.0, 0.2, 0.1],
        },
        "semantic": {"base_phrase": "human skin with subsurface scattering"},
    },
    "glass": {
        "cat": "translucent",
        "physical": {"base_color": [1.0, 1.0, 1.0], "specular_ior": 1.52, "k": 0.0, "thin_walled": False},
        "semantic": {"base_phrase": "transparent optical glass"},
        "finish_overrides": {
            "matte": {
                "shader": {
                    "specular_roughness": 0.88,
                    "transmission": 0.9,
                    "transmission_scatter": [0.12, 0.12, 0.12],
                }
            }
        },
    },
    "glass_window": {
        "cat": "translucent",
        "physical": {"base_color": [1.0, 1.0, 1.0], "specular_ior": 1.52, "k": 0.0, "thin_walled": True},
        "semantic": {"base_phrase": "thin plate glass window"},
    },
    "water": {
        "cat": "translucent",
        "physical": {"base_color": [0.9, 1.0, 1.0], "specular_ior": 1.33, "k": 0.0, "thin_walled": False},
        "semantic": {"base_phrase": "clear liquid water"},
    },
    "ice": {
        "cat": "translucent",
        "physical": {"base_color": [0.8, 0.9, 1.0], "specular_ior": 1.31, "k": 0.0, "thin_walled": False},
        "semantic": {"base_phrase": "frozen crystalline ice"},
    },
    "diamond": {
        "cat": "translucent",
        "physical": {"base_color": [1.0, 1.0, 1.0], "specular_ior": 2.42, "k": 0.0, "transmission_dispersion": 55.0},
        "semantic": {"base_phrase": "brilliant-cut diamond gemstone"},
    },
    "emerald": {
        "cat": "translucent",
        "physical": {"base_color": [0.1, 0.8, 0.2], "specular_ior": 1.57, "k": 0.0, "transmission_dispersion": 40.0},
        "semantic": {"base_phrase": "deep green emerald gemstone"},
    },
    "ruby": {
        "cat": "translucent",
        "physical": {"base_color": [0.9, 0.0, 0.1], "specular_ior": 1.76, "k": 0.0, "transmission_dispersion": 42.0},
        "semantic": {"base_phrase": "vivid red ruby gemstone"},
    },
    "amber": {
        "cat": "translucent",
        "physical": {
            "base_color": [1.0, 0.6, 0.1],
            "specular_ior": 1.54,
            "k": 0.0,
            "subsurface": 0.5,
            "transmission_depth": 5.0,
            "transmission_scatter": [0.6, 0.3, 0.05],
        },
        "semantic": {"base_phrase": "fossilized amber resin"},
    },
    "honey": {
        "cat": "translucent",
        "physical": {
            "base_color": [0.8, 0.5, 0.1],
            "specular_ior": 1.5,
            "k": 0.0,
            "subsurface": 0.8,
            "transmission_depth": 3.0,
            "transmission_scatter": [0.8, 0.5, 0.1],
        },
        "semantic": {"base_phrase": "viscous golden honey"},
    },
}

_FINISHES: dict[str, dict[str, Any]] = {
    "polished": {
        "shader": {"specular_roughness": 0.02, "specular_anisotropy": 0.0},
        "procedural": {"bump_scale": 0.0, "noise_scale": 1.0, "bump_type": "none"},
        "semantic": {"adjective": "polished", "description": "with a mirror-like smooth reflectance"},
    },
    "matte": {
        "shader": {"specular_roughness": 0.9, "specular_anisotropy": 0.0},
        "procedural": {"bump_scale": 0.0, "noise_scale": 1.0, "bump_type": "none"},
        "semantic": {"adjective": "matte", "description": "with a diffuse low-reflectance surface"},
    },
    "satin": {
        "shader": {"specular_roughness": 0.25, "specular_anisotropy": 0.1},
        "procedural": {"bump_scale": 0.02, "noise_scale": 1.0, "bump_type": "none"},
        "semantic": {"adjective": "satin", "description": "with a soft semi-gloss sheen"},
    },
    "brushed": {
        "shader": {"specular_roughness": 0.35, "specular_anisotropy": 0.8},
        "procedural": {"bump_scale": 0.1, "noise_scale": 0.5, "bump_type": "directional"},
        "semantic": {"adjective": "brushed", "description": "with directional micro-scratches"},
    },
    "hammered": {
        "shader": {"specular_roughness": 0.15, "specular_anisotropy": 0.0},
        "procedural": {"bump_scale": 0.5, "noise_scale": 2.0, "bump_type": "cellular"},
        "semantic": {"adjective": "hammered", "description": "with small crater-like indentations"},
    },
}

_CONDITIONS: dict[str, dict[str, Any]] = {
    "clean": {
        "procedural": {"dirt": 0.0, "wear": 0.0},
        "semantic": {"phrase": "in pristine condition"},
    },
    "dusty": {
        "procedural": {"dirt": 0.6, "wear": 0.1},
        "semantic": {"phrase": "covered in fine grey dust"},
    },
    "rusted": {
        "procedural": {"dirt": 0.8, "wear": 0.4},
        "semantic": {"phrase": "oxidized with flaky corrosion"},
        "only_for": ["metal"],
    },
    "scratched": {
        "procedural": {"dirt": 0.1, "wear": 0.9},
        "semantic": {"phrase": "showing heavy surface abrasions"},
    },
}


class MaterialSpec:
    """
    Frozen authoring tables for material generation.

    Consume these as read-only; ``deepcopy`` / ``dict()`` when building mutable merge state.
    Private ``_*`` dicts above exist only to construct this namespace—avoid mutating them.
    """

    SHADER_DEFAULTS = _deep_freeze(_SHADER_DEFAULTS)
    PROCEDURAL_DEFAULTS = _deep_freeze(_PROCEDURAL_DEFAULTS)
    CATEGORY_SHADER_DEFAULTS = _freeze_root_mapping(_CATEGORY_SHADER_DEFAULTS)
    COLOR_PALETTE = _freeze_root_mapping(_COLOR_PALETTE)
    POLISHED_DISALLOWED_BASES = _POLISHED_DISALLOWED_BASES
    HAMMERED_DISALLOWED_BASES = _HAMMERED_DISALLOWED_BASES
    SATIN_DISALLOWED_BASES = _SATIN_DISALLOWED_BASES
    SPECULAR_ROUGHNESS_FLOOR_BY_BASE = MappingProxyType(_SPECULAR_ROUGHNESS_FLOOR_BY_BASE)
    TRANSMISSION_LOCK_BASES = _TRANSMISSION_LOCK_BASES
    BASES = _freeze_root_mapping(_BASES)
    FINISHES = _freeze_root_mapping(_FINISHES)
    CONDITIONS = _freeze_root_mapping(_CONDITIONS)
    BASE_TOKEN_MAP = _freeze_root_mapping(_BASE_TOKEN_MAP_RAW)
    TOKEN_MAP = BASE_TOKEN_MAP


def _mutable_authoring_copy(obj: Any) -> Any:
    """Deep unwrap frozen spec nodes (MappingProxyType, tuples) into plain dict/list for merging."""
    if isinstance(obj, MappingProxyType):
        return {k: _mutable_authoring_copy(v) for k, v in obj.items()}
    if isinstance(obj, dict):
        return {k: _mutable_authoring_copy(v) for k, v in obj.items()}
    if isinstance(obj, tuple):
        return [_mutable_authoring_copy(x) for x in obj]
    if isinstance(obj, list):
        return [_mutable_authoring_copy(x) for x in obj]
    return obj


def generate_variation_seed(tech_id: str) -> float:
    """
    Derive a stable procedural seed from the material id.

    Same tech_id must always yield the same seed so masks and dataset rows are reproducible across
    machines and reruns; dataset consistency is preferred over extra randomness.
    """
    hash_obj = hashlib.md5(tech_id.encode())
    seed_float = int(hash_obj.hexdigest()[:8], 16) / float(0xFFFFFFFF)
    return round(seed_float, 6)


def combo_allowed(b_name: str, f_name: str, category: str, cond_entry: dict[str, Any]) -> bool:
    only_for = cond_entry.get("only_for")
    if only_for is not None and category not in only_for:
        return False
    if f_name == "polished" and b_name in MaterialSpec.POLISHED_DISALLOWED_BASES:
        return False
    if f_name == "hammered" and b_name in MaterialSpec.HAMMERED_DISALLOWED_BASES:
        return False
    if f_name == "satin" and b_name in MaterialSpec.SATIN_DISALLOWED_BASES:
        return False
    return True


def build_metadata(
    b_name: str,
    f_name: str,
    c_name: str,
    category: str,
    color_name: str | None,
) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "base": b_name,
        "category": category,
        "finish": f_name,
        "condition": c_name,
    }
    if color_name is not None:
        meta["color_name"] = color_name
    return meta


def build_shader_parameters(merged_shader: dict[str, Any]) -> dict[str, Any]:
    return {k: deepcopy(merged_shader[k]) for k in SHADER_PARAMETER_KEYS if k in merged_shader}


def build_procedural_parameters(merged_proc: dict[str, Any]) -> dict[str, Any]:
    return {k: deepcopy(merged_proc[k]) for k in PROCEDURAL_PARAMETER_KEYS if k in merged_proc}


def build_semantic_payload(
    b_name: str,
    f_name: str,
    c_name: str,
    base_sem: dict[str, Any],
    finish_sem: dict[str, Any],
    cond_sem: dict[str, Any],
    shader: dict[str, Any],
    color_name: str | None,
    token_map: Any,
) -> dict[str, Any]:
    base_phrase = base_sem.get("base_phrase") or token_map.get(b_name, b_name.replace("_", " "))
    if color_name:
        base_phrase = f"{color_name} {base_phrase}"

    finish_adjective = finish_sem.get("adjective", f_name.replace("_", " "))
    finish_description = finish_sem.get("description", "")
    condition_phrase = cond_sem.get("phrase", "")

    hints: list[str] = [
        base_phrase.strip(),
        f"{finish_adjective} finish".strip(),
        condition_phrase.strip(),
    ]
    if float(shader.get("transmission", 0.0)) > 0.0:
        hints.append("translucent")
        if any(float(x) > 0.0 for x in shader.get("transmission_scatter", [0.0, 0.0, 0.0])):
            hints.append("volumetric scattering")

    return {
        "base_phrase": base_phrase.strip(),
        "finish_adjective": finish_adjective,
        "finish_description": finish_description,
        "condition_phrase": condition_phrase,
        "semantic_hints": hints,
    }


def validate_material_entry(entry: dict[str, Any]) -> None:
    meta = entry["metadata"]
    shader = entry["shader_parameters"]
    proc = entry["procedural_parameters"]
    category = meta["category"]

    if category not in VALID_CATEGORIES:
        raise ValueError(f"Unknown category {category!r} for {entry['id']!r}")

    bc = shader["base_color"]
    if len(bc) != 3 or not all(isinstance(x, (int, float)) for x in bc):
        raise ValueError(f"{entry['id']}: base_color must be length-3 numeric")
    if not all(0.0 <= float(x) <= 1.0 for x in bc):
        raise ValueError(f"{entry['id']}: base_color channels must be in [0, 1]")

    def _01(name: str) -> None:
        v = float(shader[name])
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"{entry['id']}: {name} must be in [0, 1], got {v}")

    for key in (
        "metalness",
        "specular_roughness",
        "specular_anisotropy",
        "coat",
        "coat_roughness",
        "clearcoat_weight",
        "subsurface",
        "transmission",
        "sheen",
        "metallic_flake",
    ):
        _01(key)

    sss = shader["sss_color"]
    if len(sss) != 3 or not all(0.0 <= float(x) <= 1.0 for x in sss):
        raise ValueError(f"{entry['id']}: sss_color invalid")

    tc = shader["transmission_color"]
    if len(tc) != 3 or not all(0.0 <= float(x) <= 1.0 for x in tc):
        raise ValueError(f"{entry['id']}: transmission_color invalid")

    ts = shader["transmission_scatter"]
    if len(ts) != 3 or not all(float(x) >= 0.0 for x in ts):
        raise ValueError(f"{entry['id']}: transmission_scatter invalid")

    disp = float(shader["transmission_dispersion"])
    if disp < 0.0 or disp > 120.0:
        raise ValueError(f"{entry['id']}: transmission_dispersion out of sane range")

    if category == "metal" and float(shader["metalness"]) != 1.0:
        raise ValueError(f"{entry['id']}: metals must have metalness 1.0")
    if category in ("dielectric", "organic", "translucent") and float(shader["metalness"]) != 0.0:
        raise ValueError(f"{entry['id']}: non-metal category must have metalness 0.0")

    tr = float(shader["transmission"])
    if category == "translucent" and tr <= 0.0:
        raise ValueError(f"{entry['id']}: translucent materials need transmission > 0")
    if category != "translucent" and tr != 0.0:
        raise ValueError(f"{entry['id']}: opaque category must have transmission 0.0")

    if proc["bump_type"] not in VALID_BUMP_TYPES:
        raise ValueError(f"{entry['id']}: unknown bump_type {proc['bump_type']!r}")

    if proc["bump_type"] != "none" and float(proc["bump_scale"]) <= 0.0:
        raise ValueError(f"{entry['id']}: bump_type {proc['bump_type']!r} expects bump_scale > 0")

    if not isinstance(shader["thin_walled"], bool):
        raise ValueError(f"{entry['id']}: thin_walled must be bool")

    vs = float(proc["variation_seed"])
    if not 0.0 <= vs <= 1.0:
        raise ValueError(f"{entry['id']}: variation_seed must be in [0, 1]")

    cn = meta.get("color_name")
    if cn is not None:
        expected = MaterialSpec.COLOR_PALETTE.get(cn)
        if expected is None:
            raise ValueError(f"{entry['id']}: unknown color_name {cn!r}")
        if [round(float(x), 6) for x in bc] != [round(float(x), 6) for x in expected]:
            raise ValueError(f"{entry['id']}: base_color must match palette for color_name {cn!r}")

    cond = meta["condition"]
    if cond == "rusted" and category != "metal":
        raise ValueError(f"{entry['id']}: rusted condition only valid for metals")

    if "only_for" in entry:
        raise ValueError(f"{entry['id']}: stray only_for leaked into entry")

    sem = entry.get("semantic") or {}
    for field in ("base_phrase", "finish_adjective", "finish_description", "condition_phrase"):
        val = sem.get(field, "")
        if not isinstance(val, str) or not val.strip():
            raise ValueError(f"{entry['id']}: semantic.{field} must be a non-empty string")


def _merge_physical_layers(
    category: str,
    base_entry: dict[str, Any],
    f_name: str,
    c_name: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return merged shader and procedural dicts (pre-transmission and coat promotion)."""
    shader: dict[str, Any] = {
        **deepcopy(dict(MaterialSpec.SHADER_DEFAULTS)),
        **deepcopy(dict(MaterialSpec.CATEGORY_SHADER_DEFAULTS[category])),
    }
    proc: dict[str, Any] = {**deepcopy(dict(MaterialSpec.PROCEDURAL_DEFAULTS))}

    base_phys = deepcopy(base_entry["physical"])
    rough_floor = base_phys.pop("specular_roughness_min", None)

    _proc_default_keys = dict(MaterialSpec.PROCEDURAL_DEFAULTS).keys()
    for key, val in base_phys.items():
        if key in _proc_default_keys or key in ("bump_scale", "bump_type", "noise_scale", "dirt", "wear"):
            proc[key] = val
        else:
            shader[key] = val

    finish = MaterialSpec.FINISHES[f_name]
    shader.update(deepcopy(dict(finish["shader"])))
    proc.update(deepcopy(dict(finish["procedural"])))

    cond = MaterialSpec.CONDITIONS[c_name]
    proc.update(deepcopy(dict(cond["procedural"])))

    if rough_floor is not None:
        shader["specular_roughness"] = max(float(rough_floor), float(shader["specular_roughness"]))

    fo = (base_entry.get("finish_overrides") or {}).get(f_name)
    if fo:
        if "shader" in fo:
            shader.update(deepcopy(fo["shader"]))
        if "procedural" in fo:
            proc.update(deepcopy(fo["procedural"]))

    co = (base_entry.get("condition_overrides") or {}).get(c_name)
    if co:
        if "shader" in co:
            shader.update(deepcopy(co["shader"]))
        if "procedural" in co:
            proc.update(deepcopy(co["procedural"]))

    pl = base_entry.get("procedural_layer")
    if pl:
        proc.update(deepcopy(pl))

    return shader, proc


def _apply_category_transmission_model(
    category: str,
    shader: dict[str, Any],
    base_phys_snapshot: dict[str, Any],
) -> None:
    if category != "translucent":
        return
    shader["transmission_color"] = deepcopy(shader.get("base_color", [1.0, 1.0, 1.0]))
    shader["base_color"] = [0.0, 0.0, 0.0]
    if "transmission_depth" not in base_phys_snapshot:
        shader["transmission_depth"] = 1.0


def _apply_coat_and_flake(shader: dict[str, Any]) -> None:
    if float(shader.get("coat", 0.0)) > 0.0:
        shader["clearcoat_weight"] = 1.0
        cr = float(shader.get("coat_roughness", 0.03))
        if cr <= 0.0:
            cr = 0.03
        shader["coat_roughness"] = cr
        shader.setdefault("metallic_flake", 0.0)
    else:
        shader["clearcoat_weight"] = 0.0
        shader["metallic_flake"] = 0.0


def _apply_transmission_lock(b_name: str, shader: dict[str, Any], locked_snapshot: dict[str, Any]) -> None:
    if b_name not in MaterialSpec.TRANSMISSION_LOCK_BASES:
        return
    for key in ("transmission", "transmission_depth", "transmission_scatter", "subsurface"):
        if key in locked_snapshot:
            shader[key] = deepcopy(locked_snapshot[key])


def _apply_elastomer_roughness_floor(b_name: str, shader: dict[str, Any]) -> None:
    floor = MaterialSpec.SPECULAR_ROUGHNESS_FLOOR_BY_BASE.get(b_name)
    if floor is None:
        return
    shader["specular_roughness"] = max(floor, float(shader["specular_roughness"]))


def build_material_entry(
    tech_id: str,
    b_name: str,
    f_name: str,
    c_name: str,
    color_name: str | None,
    color_override: list[float] | None,
    token_map: dict[str, str],
) -> dict[str, Any]:
    base_entry = _mutable_authoring_copy(MaterialSpec.BASES[b_name])
    category = base_entry["cat"]
    cond_entry = MaterialSpec.CONDITIONS[c_name]

    if not combo_allowed(b_name, f_name, category, cond_entry):
        raise RuntimeError(f"Internal error: disallowed combo {tech_id}")

    base_phys_snap = deepcopy(base_entry["physical"])
    shader, proc = _merge_physical_layers(category, base_entry, f_name, c_name)

    if color_override is not None:
        shader["base_color"] = deepcopy(color_override)

    locked_transmission_snapshot = {
        k: deepcopy(shader[k])
        for k in ("transmission", "transmission_depth", "transmission_scatter", "subsurface")
        if k in shader
    }

    _apply_category_transmission_model(category, shader, base_phys_snap)
    _apply_coat_and_flake(shader)
    _apply_transmission_lock(b_name, shader, locked_transmission_snapshot)
    _apply_elastomer_roughness_floor(b_name, shader)

    thin = base_phys_snap.get("thin_walled")
    if thin is not None:
        shader["thin_walled"] = bool(thin)

    proc["variation_seed"] = generate_variation_seed(tech_id)

    meta = build_metadata(b_name, f_name, c_name, category, color_name)
    shader_out = build_shader_parameters(shader)
    proc_out = build_procedural_parameters(proc)

    sem = build_semantic_payload(
        b_name,
        f_name,
        c_name,
        base_entry.get("semantic", {}),
        MaterialSpec.FINISHES[f_name]["semantic"],
        MaterialSpec.CONDITIONS[c_name]["semantic"],
        shader_out,
        color_name,
        token_map,
    )

    entry = {
        "id": tech_id,
        "metadata": meta,
        "shader_parameters": shader_out,
        "procedural_parameters": proc_out,
        "semantic": sem,
    }
    validate_material_entry(entry)
    return entry


class BuildMaterialsData:
    """Deterministic generator for neuron_library.json material records."""

    def generate(self, subset_ids: set[str] | None = None) -> dict[str, dict[str, Any]]:
        print(">> Building materials data...")
        token_map = MaterialSpec.BASE_TOKEN_MAP
        library: dict[str, dict[str, Any]] = {}

        for b_name, f_name, c_name in product(MaterialSpec.BASES, MaterialSpec.FINISHES, MaterialSpec.CONDITIONS):
            base_entry = MaterialSpec.BASES[b_name]
            category = base_entry["cat"]
            cond_entry = MaterialSpec.CONDITIONS[c_name]
            if not combo_allowed(b_name, f_name, category, cond_entry):
                continue

            if base_entry.get("colorable"):
                for color_name, color_val in MaterialSpec.COLOR_PALETTE.items():
                    tech_id = f"{b_name}_{color_name}_{f_name}_{c_name}"
                    if subset_ids is not None and tech_id not in subset_ids:
                        continue
                    library[tech_id] = build_material_entry(
                        tech_id, b_name, f_name, c_name, color_name, color_val, token_map
                    )
            else:
                tech_id = f"{b_name}_{f_name}_{c_name}"
                if subset_ids is not None and tech_id not in subset_ids:
                    continue
                library[tech_id] = build_material_entry(
                    tech_id, b_name, f_name, c_name, None, None, token_map
                )

        LIBRARY_JSON.parent.mkdir(parents=True, exist_ok=True)
        with open(LIBRARY_JSON, "w", encoding="utf-8") as f:
            json.dump(library, f, indent=4)

        print(">> Materials data built")
        return library


class BuildPrompts:
    """Deterministic natural-language labels for neuron_library.json."""

    DEFAULT_SEED = 42

    TOKEN_MAP = MaterialSpec.TOKEN_MAP

    TEMPLATES = [
        "A close-up of {base_phrase}, {finish_description}, {condition_phrase}.",
        "Photorealistic material study of {base_phrase} with a {finish_adjective} finish, {condition_phrase}.",
    ]

    def __init__(self, json_path: Path | str | None = None, seed: int | None = None, overwrite: bool = False):
        self.json_path = Path(json_path) if json_path else LIBRARY_JSON
        self.seed = seed if seed is not None else self.DEFAULT_SEED
        self.overwrite = overwrite

    def _validate_text(self, text: str) -> str:
        text = re.sub(r" {2,}", " ", text)
        text = re.sub(r",\s*\.", ".", text)
        text = re.sub(r",\s*$", "", text)
        text = text.strip()
        if text:
            text = text[0].upper() + text[1:]
        return text

    def _build_label(self, entry: dict[str, Any], rng: random.Random) -> str:
        sem = entry.get("semantic") or {}
        base_phrase = sem.get("base_phrase", "")
        finish_description = sem.get("finish_description", "")
        finish_adjective = sem.get("finish_adjective", "")
        condition_phrase = sem.get("condition_phrase", "")

        template = rng.choice(self.TEMPLATES)
        label = template.format(
            base_phrase=base_phrase,
            finish_description=finish_description,
            finish_adjective=finish_adjective,
            condition_phrase=condition_phrase,
        )
        return self._validate_text(label)

    def generate(self) -> dict[str, Any]:
        print(">> Building prompts...")

        if not self.json_path.exists():
            raise FileNotFoundError(
                f"Material library not found: {self.json_path}\n"
                "Run BuildMaterialsData().generate() first to generate it."
            )

        with open(self.json_path, "r", encoding="utf-8") as f:
            library = json.load(f)

        rng = random.Random(self.seed)
        generated, skipped = 0, 0

        for _tech_id, entry in library.items():
            sem = entry.setdefault("semantic", {})
            if sem.get("semantic_label") and not self.overwrite:
                skipped += 1
                rng.choice(self.TEMPLATES)
                continue
            sem["semantic_label"] = self._build_label(entry, rng)
            generated += 1

        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(library, f, indent=4)

        logger.info("Label generation complete: %d generated, %d skipped", generated, skipped)
        print(">> Prompts built")
        return library

