# Copernicus HDA: The Texture Engine Blueprint

The goal of your manual look-dev is to build a **Master Copernicus HDA** (Houdini Digital Asset). Instead of creating thousands of unique textures, you are creating a single, intelligent "Texture Engine" that generates different results based on the JSON parameters you feed it.

Here is the blueprint for the outputs you need to define and how they integrate into your `BuildMaterials` class.

---

## 1. The Output of Look-Dev: The "Big Four" Masks

Your Copernicus HDA should have one set of inputs (Seed, Dirt, Wear, etc.) and four primary output connectors. These outputs are not "colors" but **spatial probability maps**.

| Output Map | Logic | What it Teaches the AI |
| :--- | :--- | :--- |
| **Wear Mask** | High-frequency scratches + Edge highlights (via Curvature). | That edges are sharper/shinier than flat surfaces. |
| **Dirt Mask** | Low-frequency smudges + Crevice accumulation (via AO). | That "occlusion" leads to a loss of reflectivity and color shifts. |
| **Micro-Bump** | Directional "Brushed" lines or Cellular "Hammered" pits. | How micro-geometry affects the "shape" of a highlight (Anisotropy). |
| **Variation Map** | A subtle, multi-octave fractal noise. | That no real-world surface is perfectly uniform in color. |

---

## 2. The Finite Set of Procedural "DNA"

You don't need a unique Copernicus network for every material. You only need a few **Base Logic Groups** that you toggle via your script. During look-dev, build these three distinct procedural "flavors":

* **The "Linear" Engine:** (For brushed finishes). Uses directional anisotropic noise.
* **The "Cellular" Engine:** (For hammered or cast finishes). Uses Voronoi/Worley noise to create physical indentations.
* **The "Stochastic" Engine:** (For polished or matte finishes). Uses Fractal/Perlin noise for organic dust and smudges.

In your `BuildMaterials()` script, you will look at the `bump_type` in your JSON (e.g., directional, cellular) and tell the Copernicus HDA which "Flavor" to activate.

---

## 3. How BuildMaterials() Utilizes the Look-Dev

Once you have your Master Copernicus HDA, your Python script becomes a "Wiring Engine." Here is the logic the developer will add to the `_create_builder` method:

### Step A: Instance the Copernicus HDA
Inside each material subnet, the script will create an instance of your look-dev HDA.

### Step B: Driving the HDA with JSON
The script "pushes" the JSON data into the HDA parameters.

### Step C: The MaterialX "Mix" Nodes
Instead of a direct value, the script wires the Copernicus outputs into MaterialX Mix nodes.

* **Base Color:** `mtlxmix` (Input A: JSON Color | Input B: Dirt Color | Mask: Cop Dirt Mask).
* **Roughness:** `mtlxmultiply` (Input A: JSON Rough | Input B: Cop Wear Mask).

---

## 4. Why this is "Neural Hero" Grade

By using this HDA approach, you are ensuring **Coordinate Consistency**.

Because your HDA uses **Tri-planar projection** based on $P$ (position), the "Scratches" aren't just pixels—they are mathematical locations in 3D space. When you move the camera for your 200 renders, the INR (Neural Network) will see that a scratch at coordinates $(0.5, 0.2, 0.1)$ is consistent across every single frame.

---

## Summary Checklist for Look-Dev:

* [ ] Build a Copernicus HDA with inputs for Seed, Dirt, Wear, and Bump.
* [ ] Sample via Tri-planar inside the HDA so no UVs are required.
* [ ] Define the "Mix Logic" for how dirt should change a color (does it get darker? Browner?).
* [ ] Test the "Seed"—change the seed and ensure the scratches move to entirely new, random locations.