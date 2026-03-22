# NEURON PROJECT: PHASE 1 & 2 TECHNICAL SPECIFICATION

## 1. PROJECT OVERVIEW: NEURON
Neuron is a next-generation Neural Rendering Engine that replaces traditional PBR textures with Implicit Neural Representations (INRs). It enables "Text-to-Volumetric-Material" synthesis where a single model understands both 3D spatial coordinates and semantic language (CLIP).

### Development Phases
1. **Phase 1: Synthetic Data (Houdini):** Generation of a "Ground Truth" dataset using procedural shaders and automated camera rigs.
2. **Phase 2: Material Hero (INR Training):** Training a Coordinate-MLP conditioned on CLIP text embeddings to learn material physics.
3. **Phase 3: Voxel Baking:** Converting the neural field into a sparse voxel grid for real-time web performance.
4. **Phase 4: Compositional Scene Graph:** Moving from single-asset materials to complex multi-object scenes.
5. **Phase 5: Production UI:** Building the final React/Three.js interface with dynamic neural pings.
6. **Phase 6: Temporal Synthesis:** Integration with Veo/LTX for high-fidelity video and motion synthesis.

---

## 2. PHASE 2: INR TRAINING LOGIC
The "Material Hero" is a Multi-Layer Perceptron (MLP) that acts as a continuous function $F$.
* **Input:** 3D Coordinates $(x, y, z)$, Viewing Direction $(\theta, \phi)$, and CLIP Latent Vector $(w)$.
* **Internal:** Positional Encoding (SIREN or Fourier Features) to resolve high-frequency details (scratches/pores).
* **Output:** RGB Color and Density (Occupancy).
* **Memory Constraint:** Optimized for 6GB VRAM via Ray Sampling (1k-2k pixels per batch) and Mixed Precision (FP16).

---

## 3. PHASE 1: HOUDINI DATA GENERATION SPECS

### Camera & Lighting Setup
* **Camera Dome:** 200 cameras distributed via Geodesic/Fibonacci Sphere patterns.
* **Rig Constraints:** Fixed distance from origin; constant focal length (85mm recommended for "Hero" look).
* **Lighting:** Static HDRI Studio Map (Neutral/High-Contrast) + Subtle 3-point neutral rim lights. Lighting must remain identical across all materials to ensure the AI learns *reflectance*, not *environment*.
* **Resolution:** Render at 720x720 (Houdini Apprentice max). Post-process: Center-crop and downsample to 512x512 for training.

### Render Passes (The Neural Curriculum)
1. **Beauty:** Full PBR render (The target).
2. **Albedo:** Flat base color (Identity).
3. **Alpha/Mask:** Binary occupancy (Shape).
4. **Normals:** World-space surface orientation (Geometry context).

### Folder Structure & Naming
* **Root:** `/dataset/`
* **Subfolders:** Categorized by Technical ID (e.g., `/dataset/gold_brushed_worn/`)
* **File Naming:** `[Base]_[Adjectives]_[CamID].png` (e.g., `gold_brushed_dirty_042.png`).

---

## 4. THE MATERIAL GENERATOR DICTIONARIES

The generator uses a Cartesian Product logic: **[Base Material] x [Adjective Set]**.

### MATERIAL_BASES (The Nouns)
* **Conductors (Metals):** `gold`, `silver`, `copper`, `iron`, `chrome`, `aluminum`, `titanium`, `brass`.
* **Dielectrics (Insulators):** `plastic_abs`, `rubber`, `ceramic`, `concrete`, `marble`, `granite`, `car_paint`, `carbon_fiber`.
* **Organics:** `oak_wood`, `leather`, `denim_fabric`, `linen`, `human_skin`, `clay`, `paper`.
* **Translucents:** `clear_glass`, `frosted_glass`, `water`, `wax`, `emerald`, `ice`.

### ADJECTIVES (The Modifiers)
* **Surface/Finish:** `polished`, `matte`, `satin`, `brushed`, `hammered`, `cast`, `anodized`, `powder_coated`.
* **Condition/Wear:** `clean`, `scratched`, `dented`, `scuffed`, `fingerprinted`, `oily`, `dusty`.
* **Aging/Chemical:** `rusted`, `oxidized`, `tarnished`, `patina`, `corroded`, `pitted`, `ancient`, `faded`.

---

## 5. THE TEMPLATE-BASED CONSTRUCTOR (LABEL EVOLUTION)

This tool bridges the gap between technical "Bad Labels" and semantic "Good Labels."

### The Logic
1. **Tokenization:** Split the Technical ID (e.g., `iron_rusted_pitted`).
2. **Semantic Mapping:** Each token maps to a descriptive phrase:
   - `iron` -> "a heavy industrial iron surface"
   - `rusted` -> "oxidized with deep orange corrosion"
   - `pitted` -> "featuring small craters and physical degradation"
3. **Template Assembly:** Randomly select a sentence structure:
   - "A close-up of [Phrase1], [Phrase2], and [Phrase3]."
   - "Detailed 3D view showing [Phrase1] which is [Phrase2]."
4. **Output (Good Label):** "A close-up of a heavy industrial iron surface, oxidized with deep orange corrosion, and featuring small craters."

---

## 6. CRITICAL PIPELINE CONSIDERATIONS
* **The "Apprentice" Mask:** PyTorch Dataset must include a `hard_mask` for the bottom-right (150x100px) to prevent the model from learning the Houdini logo.
* **Scale Consistency:** All assets are normalized to 1 meter. Texture patterns (bricks/grain) must be scaled relative to this 1m standard.
* **Transforms.json:** The single source of truth. Must contain the `transform_matrix` (4x4), `intrinsic_matrix`, and the `good_label` for every frame.
* **Interpolation Strategy:** Ensure the training set includes "Opposites" (e.g., Polished vs. Matte) so the model can learn the continuous slider between them.