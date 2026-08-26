# BRIEF: NEURON LABEL ENGINE (PHASE 2)

To ensure the AI doesn't overfit to a single sentence structure, the engine must use a **Template-Based Randomized Constructor**. This creates "Semantic Diversity," preventing the model from just memorizing specific word orders.

---

## 1. Objective
Create a Python class `LabelEngine` that iterates through the `neuron_library.json` and generates high-fidelity, natural language descriptions (prompts) for every material. These prompts will be saved back into the JSON as the `good_label` key.

## 2. Input Data Schema
The engine must utilize the following keys from each JSON entry:

* **id**: (e.g., `gold_polished_clean`)
* **metadata**: (specifically `base`, `finish`, `condition`)
* **semantic_hints**: The list of descriptive phrases (e.g., `["gold", "mirror-like and smooth", "pristine condition"]`)

## 3. Core Logic: The Semantic Assembly
The engine should follow a three-step "Evolution" process for each label:

### Step A: Token Mapping
The engine should maintain a dictionary to "expand" technical terms if the `semantic_hints` are too brief.
* **gold** -> "precious 24k gold metal"
* **polished** -> "highly reflective, mirror-finish surface"
* **dirty** -> "accumulated grime and industrial grease"

### Step B: Sentence Templates
To avoid repetitive training data, the engine must randomly select from at least 4 different sentence structures for each material.

| Template Type | Structure |
| :--- | :--- |
| **Template 1 (Direct)** | "A close-up view of [Finish] [Base] in [Condition]." |
| **Template 2 (Descriptive)** | "Detailed 3D render showing a [Base] material with a [Finish] texture, currently [Condition]." |
| **Template 3 (Cinematic)** | "Macro photography of [Base]. The surface is [Finish] and shows signs of being [Condition]." |
| **Template 4 (Technical)** | "High-fidelity PBR material study: [Condition] [Base] with [Finish] properties." |

### Step C: The Constructor
The engine will inject the `semantic_hints` (or the expanded tokens) into the chosen template.

> **Example ID:** `iron_brushed_rusted`
> **Hints:** `["iron", "linear micro-grooves", "flaky corrosion"]`
> **Output:** "Macro photography of iron. The surface is characterized by linear micro-grooves and shows signs of being covered in flaky corrosion."

---

## 4. Technical Requirements
* **Idempotency**: If a `good_label` already exists, the script should have a flag to either skip or overwrite.
* **Random Seed**: Use a fixed seed for the random template selection so that the labels remain consistent across runs unless explicitly changed.
* **Validation**: Ensure there are no double spaces or trailing commas in the final string.
* **Batch Processing**: The tool should be able to process all 1,980 materials in a single execution.

## 5. Deliverables
1.  A Python script `label_engine.py`.
2.  An updated `neuron_library.json` where every entry now includes a `good_label` string.
3.  A short log file showing 5-10 sample "Technical ID -> Good Label" conversions for quality insurance.

---

### Pro-Tip for the Developer:
When assembling the `good_label`, the developer should ensure that the **"Base" (the noun) is always the focal point** of the sentence. Generative models prioritize the first few tokens of a prompt, so "Gold" should appear earlier in the string than "Scratched" to ensure the AI learns the core material before the modifiers.



This diagram helps visualize how the "Label Engine" moves technical IDs into a semantic space where the AI can cluster "Gold" and "Silver" near each other while separating "Polished" from "Rusted" along a different axis.