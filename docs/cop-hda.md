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


# Procedural Determinism: Magic Numbers & Noise Layering

To keep the **"Pro Move"** of hash-based determinism, you should definitely hardcode these numbers—but you should choose them strategically.

The goal of these numbers (often called "magic numbers" in procedural generation) is to ensure that different noise layers—like your **Dirt** and your **Scratches**—don't overlap or look like they are "twinned." If you used the same offset for both, a scratch would always appear exactly where a piece of dirt is, which looks fake.

---

## 1. Use "Large Prime" Hardcoding
The industry standard is to use large prime numbers or numbers with no common factors. This prevents **"aliasing"** or repeating patterns.

You should define a unique "Prime Offset" for each major noise type in your **Master Copernicus HDA**. This ensures that even though they all use the same `variation_seed`, they are sampling completely different neighborhoods of the 3D noise field.

### Example HDA Logic (Inside VEX or Parameter Expressions):

| Noise Layer | Multiplier X | Multiplier Y | Multiplier Z |
| :--- | :--- | :--- | :--- |
| **Dirt Noise** | 133.19 | 777.43 | -512.23 |
| **Scratch Noise** | 911.67 | -233.11 | 444.89 |
| **Micro-Bump** | 1024.5 | 15.9 | 888.31 |

By hardcoding these, you ensure that `gold_polished_dusty` will always have the exact same dirt and the exact same scratches every time you hit render, which is vital for your training consistency.

---

## 2. Why "Randomizing" is the Enemy
If you used a `rand()` function inside Houdini to pick those multipliers, you would break the pipeline:

* **Lost Reproducibility:** If you sent the file to a render farm or a colleague, their `rand()` might return a different value, and your "Material Hero" would look different.
* **Training Noise:** For an INR (Neural Network) to converge, the "Ground Truth" must be absolute. If the labels in your JSON point to an image that changes slightly every time you open the file, the network will struggle to map the text prompt to the visual features.

---

## 3. The "Infinite Fabric" Concept
Think of procedural noise as an infinite fabric wrapped around the universe.

1.  **The Noise Node** defines the pattern of the fabric.
2.  **The `variation_seed`** determines where you "cut" the fabric to dress your Shader Ball.
3.  **The Hardcoded Multipliers** ensure that your "Dirt" fabric and your "Scratch" fabric are being cut from different parts of the universe so they don't look related.

---

## 4. Implementation in `BuildMaterials()`
Since you are using the `variation_seed` as a 0–1 float, your Python script doesn't need to know about these magic numbers. It just passes the `0.123456` value to the HDA.

Inside the HDA, you can use a **Parameter Expression** on the noise offset:
`ch("variation_seed") * 133.19`

---

> ### Summary for the Developer
> **"Hardcode fixed prime-number multipliers for every noise-offset internal to the HDA. This decorrelates the Dirt, Wear, and Bump layers while maintaining the deterministic hash-based results provided by the variation_seed attribute."**

### 15 Safe Prime-Based Multipliers for Copernicus Noise Layers

These multipliers are chosen to be large, prime, or having non-repeating fractional components to ensure that your noise layers (Dirt, Scratches, Wear, etc.) are sampled from mathematically distant "neighborhoods" of the noise field.

| Layer Type | Multiplier X | Multiplier Y | Multiplier Z |
| :--- | :--- | :--- | :--- |
| **Primary Dust** | 173.89 | 541.21 | 227.17 |
| **Secondary Dirt** | 661.91 | 107.09 | 823.43 |
| **Micro-Scratches** | 941.11 | 313.37 | 499.19 |
| **Heavy Gouges** | 127.13 | 761.47 | 907.01 |
| **Edge Wear** | 431.63 | 199.97 | 617.29 |
| **Surface Oxidation** | 853.67 | 467.03 | 131.59 |
| **Water Stains** | 281.81 | 701.53 | 397.69 |
| **Oil/Grease Spots** | 593.59 | 149.23 | 881.71 |
| **Pitting/Corrosion** | 353.17 | 991.49 | 239.11 |
| **Fingerprints** | 719.93 | 523.61 | 167.41 |
| **Thermal Damage** | 443.83 | 827.29 | 601.07 |
| **Paint Flaking** | 317.21 | 103.91 | 773.51 |
| **Micro-Bump/Grain** | 997.33 | 419.59 | 151.01 |
| **Anisotropy Noise** | 647.47 | 383.13 | 919.67 |
| **Generic Var A** | 271.91 | 557.03 | 811.97 |

---

### Implementation Snippet (VEX / Parameter Expression)

If you are inside a **Copernicus Snippet** or a **VOP** node using the `variation_seed` parameter, your offset logic should look like this to ensure total decorrelation:

// Example for the 'Heavy Gouges' layer
float seed = chf("variation_seed");
vector offset = set(seed * 127.13, seed * 761.47, seed * 907.01);

// Apply this offset to your noise sampling
float noise_val = unifiednoise(pos + offset);