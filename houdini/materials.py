import json
from pathlib import Path
from itertools import product

from config import LIBRARY_JSON

class MaterialGenerator:
    def __init__(self):
        # 1. PHYSICAL CATEGORIES (Shader Models)
        self.CATEGORIES = {
            "metal": {"metalness": 1.0, "has_k": True, "sss": 0.0},
            "dielectric": {"metalness": 0.0, "has_k": False, "sss": 0.0},
            "organic": {"metalness": 0.0, "has_k": False, "sss": 0.2},
            "translucent": {"metalness": 0.0, "has_k": False, "refraction": 1.0}
        }

        # 2. BASES (The Nouns)
        self.BASES = {
            "gold": {"cat": "metal", "color": [1.0, 0.85, 0.5], "ior": 0.47, "k": 2.83},
            "copper": {"cat": "metal", "color": [0.95, 0.64, 0.54], "ior": 1.1, "k": 2.5},
            "iron": {"cat": "metal", "color": [0.56, 0.57, 0.58], "ior": 2.9, "k": 3.0},
            "plastic": {"cat": "dielectric", "color": [0.1, 0.1, 0.1], "ior": 1.5},
            "concrete": {"cat": "dielectric", "color": [0.5, 0.5, 0.5], "ior": 1.6},
            "marble": {"cat": "dielectric", "color": [0.9, 0.9, 0.9], "ior": 1.48},
            "oak_wood": {"cat": "organic", "color": [0.3, 0.2, 0.1], "ior": 1.5},
            "glass": {"cat": "translucent", "color": [1.0, 1.0, 1.0], "ior": 1.52}
        }

        # 3. FINISHES (Physical Surface State)
        self.FINISHES = {
            "polished": {"rough": 0.02, "anisotropy": 0.0, "hint": "mirror-like and smooth"},
            "matte": {"rough": 0.9, "anisotropy": 0.0, "hint": "dull and non-reflective"},
            "satin": {"rough": 0.25, "anisotropy": 0.1, "hint": "soft semi-gloss sheen"},
            "brushed": {"rough": 0.35, "anisotropy": 0.8, "hint": "directional micro-scratches"},
            "hammered": {"rough": 0.15, "bump_type": "cellular", "hint": "indented with small craters"}
        }

        # 4. CONDITIONS (Environmental Wear)
        self.CONDITIONS = {
            "clean": {"dirt": 0.0, "wear": 0.0, "hint": "pristine condition"},
            "dusty": {"dirt": 0.6, "wear": 0.1, "hint": "covered in fine grey particles"},
            "rusted": {"dirt": 0.8, "wear": 0.4, "only_for": ["metal"], "hint": "oxidized with flaky corrosion"},
            "scratched": {"dirt": 0.1, "wear": 0.9, "hint": "showing heavy surface abrasions"}
        }

    def generate(self):
        library = {}
        
        # Cartesian Product: Base x Finish x Condition
        for b_name, f_name, c_name in product(self.BASES, self.FINISHES, self.CONDITIONS):
            
            base = self.BASES[b_name]
            category = base["cat"]
            cond = self.CONDITIONS[c_name]
            
            # --- COMPATIBILITY FILTER ---
            # Skip if condition is category-specific and doesn't match
            if "only_for" in cond and category not in cond["only_for"]:
                continue

            tech_id = f"{b_name}_{f_name}_{c_name}"
            finish = self.FINISHES[f_name]

            # Build the flat parameter set for Houdini
            params = {**self.CATEGORIES[category], **base, **finish, **cond}
            
            library[tech_id] = {
                "id": tech_id,
                "metadata": {"base": b_name, "category": category, "finish": f_name, "condition": c_name},
                "parameters": params,
                "semantic_hints": [base.get("hint", b_name), finish["hint"], cond["hint"]]
            }
            
        return library

    def export(self, filepath=None):
        filepath = Path(filepath) if filepath else LIBRARY_JSON
        filepath.parent.mkdir(parents=True, exist_ok=True)
        data = self.generate()
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        return data

    def display(self, limit=None):
        library = self.generate()
        print(f"{'TECH ID':<35} | {'CATEGORY':<12} | {'COLOR'}")
        print("-" * 70)
        for i, (tid, entry) in enumerate(library.items()):
            if limit and i >= limit:
                break
            color = entry["parameters"]["color"]
            cat = entry["metadata"]["category"]
            print(f"{tid:<35} | {cat:<12} | {color}")
        print(f"\nTotal: {len(library)} materials")


if __name__ == "__main__":
    generator = MaterialGenerator()
    generator.export()
    generator.display()