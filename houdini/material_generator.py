# Expanded Material Dictionary
MATERIAL_BASES = {
    "gold":      {"cat": "metal",      "col": [1.0, 0.8, 0.4], "met": 1.0, "ior": 1.5},
    "iron":      {"cat": "metal",      "col": [0.5, 0.5, 0.5], "met": 1.0, "ior": 1.5},
    "plastic":   {"cat": "dielectric", "col": [0.2, 0.2, 0.8], "met": 0.0, "ior": 1.45},
    "wood":      {"cat": "organic",    "col": [0.3, 0.2, 0.1], "met": 0.0, "ior": 1.5},
    "concrete":  {"cat": "dielectric", "col": [0.5, 0.5, 0.5], "met": 0.0, "ior": 1.6},
}

# Adjective Logic (Modifiers)
ADJECTIVES = {
    "polished": {"rough_off": -0.5, "bump": 0.0, "clip": "highly reflective and smooth"},
    "brushed":  {"rough_off": 0.1,  "anis": 0.8, "clip": "with directional micro-scratches"},
    "dirty":    {"alb_mult": 0.7,  "rough_off": 0.3, "clip": "covered in environmental grime"},
    "worn":     {"bump": 0.4,      "rough_off": 0.2, "clip": "showing signs of heavy use and age"}
}

def generate_training_set():
    for base, b_data in MATERIAL_BASES.items():
        # Select valid adjectives for this category
        valid_adjectives = list(ADJECTIVES.keys())
        if b_data['cat'] != "metal":
            valid_adjectives.remove("brushed") # Metals are brushed, wood is 'sanded'

        for adj in valid_adjectives:
            # Final Prompt Construction
            final_prompt = f"A {adj} {base} surface, {ADJECTIVES[adj]['clip']}."
            
            # This 'task' goes to the Houdini TOP Network
            print(f"TASK: Render {base} as {adj} | PROMPT: {final_prompt}")

generate_training_set()