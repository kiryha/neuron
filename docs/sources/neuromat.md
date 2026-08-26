# New Chat Brief: Build the `neuromat` Material HDA in Houdini Apprentice

I am building `neuromat`, a single master Material HDA for Project Neuron in Houdini Apprentice.  
This chat should help me finish the HDA and get clean, deterministic material renders for dataset generation.

Keep the approach minimal and practical.  
Do not redesign the architecture unless there is a **critical flaw that would break Phase 2 training**.

---

# 1. Project Objective

## Phase 1 — Synthetic Material Dataset
Create a deterministic synthetic render dataset of a single hero asset with many controlled material variations.

Current plan:
- one hero model: sculpted Rubber Toy
- one master material HDA: `neuromat`
- materials driven from JSON
- around 2,000 material variations
- around 200 dome cameras
- rendered with stable lighting and fixed scene setup
- output multiple AOVs / passes for later training

The goal of Phase 1 is **not** to build a perfect universal material system.  
The goal is to generate **clean, consistent, physically plausible** renders that will not poison Phase 2.

## Phase 2 — Train the Material Network
Use the rendered dataset to train the first "Material Hero" network.

High-level target:
- text-conditioned material model
- learns reflectance / appearance from rendered data
- later used inside the broader Neuron pipeline

For Phase 2 to work, Phase 1 must produce data that is:
- deterministic
- consistent across cameras
- consistent across materials
- not dependent on random scene changes
- not contaminated by changing lighting or exposure
- not using camera-space tricks

---

# 2. Current State in Houdini

This is the current setup and should remain the working architecture unless there is a critical issue.

## Geometry / scene state
- one model: sculpted Rubber Toy
- using UVs to project and place COPS textures
- baked AO and curvature exist on geometry points
- these baked signals are available to drive dirt / wear logic

## Shader / material state
- using MaterialX
- using MaterialX Fractal 3D for small noise and other masks
- storing `shader_parameters` and `procedural_parameters` on the asset root
- reading those values inside the MaterialX network
- a `VARIATION` map already exists in COPS
- variation map is projected to geometry using UVs

## Next material tasks
Need to build and wire:
- `DIRT` map
- `WEAR` map
- `BUMP` map

These maps should be driven by:
- JSON parameters
- existing baked AO
- existing baked curvature
- COPS and MaterialX procedural logic

## Render plan
- one material HDA
- JSON-driven material definitions
- later rendered through TOPs
- target scale: 2,000 materials × 200 cameras

---

# 3. Architecture Constraints

Do not change these unless there is a critical failure risk.

## Keep
- one master material HDA
- one hero geometry
- UV-based projection for current stage
- JSON-driven material parameters
- baked AO and curvature as support signals
- COPS for map generation
- MaterialX for shading
- TOPs for final rendering

## Important note about UVs
UV-based projection is acceptable for this stage because:
- we are using one fixed hero mesh
- we need to move quickly
- the immediate goal is material dataset generation on one asset

Do **not** force a triplanar / object-space redesign right now unless UV usage creates a critical training failure.

The only important rule is:
- no camera-dependent texture behavior
- no view-dependent baked maps
- no random reprojection changes between renders

---

# 4. What `neuromat` Must Do

`neuromat` should be a single reusable material HDA that:

1. receives material data from JSON
2. applies base material values
3. generates procedural mask maps
4. combines those masks into a physically plausible MaterialX shader
5. supports predictable debug / AOV output
6. can be rendered repeatedly in batch without surprises

The HDA should be good enough to:
- preview single materials interactively
- validate stress-test materials
- batch render the dataset later

---

# 5. JSON Contract

The material JSON already has a clean split and that structure should be preserved.

Each material entry should include:

## `metadata`
Identity only:
- material id
- base
- category
- finish
- condition
- optional color name
- semantic label / descriptive text

## `shader_parameters`
Material-facing values:
- `base_value`
- `base_color`
- `metalness`
- `specular_ior`
- `k`
- `specular_roughness`
- `specular_anisotropy`
- `subsurface`
- `sss_color`
- `coat`
- `coat_roughness`
- `sheen`
- `transmission`
- `transmission_color`
- `transmission_depth`
- `transmission_scatter`
- `transmission_dispersion`
- `thin_walled`
- `metallic_flake`

## `procedural_parameters`
Mask / texture control:
- `variation_seed`
- `bump_scale`
- `bump_type`
- `noise_scale`
- `dirt`
- `wear`

The HDA should consume these values directly or through attributes copied onto the asset root.

---

# 6. Material Logic We Need

The HDA does not need a huge shading system.  
It needs a **controlled minimal system** that covers the material library correctly.

## Core material families
Support at least:
- metals
- dielectrics
- translucent materials
- organics if already defined in JSON

## Procedural families
Support these procedural branches:
- `stochastic`
- `directional`
- `cellular`
- `none`

Meaning:
- `stochastic`: subtle noise, matte breakup, satin breakup, polished micro-imperfection, dust breakup
- `directional`: brushed / aligned scratch logic
- `cellular`: hammered / crater / pitted logic
- `none`: truly flat procedural branch, use only if intentionally required

---

# 7. The Mask System to Build Now

The current next step is to finish the internal signal system.

We need these maps:

## 7.1 `VARIATION`
Current state:
- already built in COPS
- projected using UVs
- driven by procedural fractal structure

Purpose:
- subtle base color modulation
- subtle roughness breakup
- avoid perfectly flat surfaces

Rule:
- keep it gentle
- it should not become visible dirt or visible wear

## 7.2 `DIRT`
Need to build.

Purpose:
- broad surface contamination
- accumulation in occluded or sheltered areas
- roughness increase
- optional desaturation / greying / dust tint

Primary drivers:
- baked AO
- large-scale procedural noise
- optional breakup distortion
- JSON `dirt` parameter as intensity control

Expected behavior:
- more accumulation in cavities / concave regions
- broad soft patterns, not scratch detail
- should work for both hard surfaces and translucent materials, but subtly

Use cases:
- dusty car paint
- dusty honey
- light contamination on rubber / metal if required

## 7.3 `WEAR`
Need to build.

Purpose:
- exposed edges
- abrasion
- scratches / worn zones
- roughness change
- possibly brightening or darkening depending on material family

Primary drivers:
- baked curvature
- medium / high frequency procedural breakup
- JSON `wear` parameter

Expected behavior:
- edges and exposed forms respond first
- wear should not look like dirt
- wear should be sharper and more localized than dirt

Use cases:
- scratched iron
- worn rubber
- exposed highlights on hard edges

## 7.4 `BUMP`
Need to build.

Purpose:
- micro-surface shape
- physically believable breakup
- procedural family differentiation

Driven by:
- `bump_scale`
- `bump_type`
- `noise_scale`
- `variation_seed`

Branch meaning:
- `stochastic`: fine noise / subtle irregularity
- `directional`: brushed / linear grain
- `cellular`: crater / hammered pattern

Rule:
- keep bump believable
- do not overdrive displacement-like behavior
- this is primarily micro-surface response, not large-scale deformation

---

# 8. Minimal Wiring Strategy

Keep the shader logic simple and stable.

## Base color
Base color should come from JSON, then optionally be modified by:
- `VARIATION`
- `DIRT`

Recommended effect:
- variation = subtle value / saturation shift
- dirt = contamination tint or grey/dust bias

## Roughness
Roughness should come from JSON, then be modified by:
- `VARIATION` slightly
- `DIRT` strongly in contaminated areas
- `WEAR` where abrasion should alter micro-surface response
- `BUMP` should affect shading physically through normal/bump, not fake roughness only

## Metalness / IOR / transmission
These should remain mostly direct JSON-driven values.
Do not procedurally randomize them.

## Coat
Use coat exactly where JSON says so.
Do not invent secondary coat logic unless required.

## Transmission / translucent materials
Keep this controlled and simple.
The important rule is consistency, not physical overcomplication.

---

# 9. Required Render Outputs / AOVs

The dataset must include the right passes for later training.

These are the required passes.

## 9.1 Beauty
Final shaded render.

Purpose:
- main target image for training
- includes full material and lighting response

## 9.2 Alpha / Mask
Binary object coverage.

Purpose:
- object silhouette
- background separation
- occupancy / density support

## 9.3 Depth / `Pz`
Camera depth.

Purpose:
- spatial cue
- helps later training / debugging
- useful for geometry-aware supervision

## 9.4 BaseColor
Raw material base color input.

Purpose:
- material identity signal
- decouples raw albedo from shaded beauty
- especially important for metal / dielectric interpretation

Important:
- do not let this become black for materials that still need a meaningful material-color signal in the dataset logic

## 9.5 Roughness
Raw roughness input.

Purpose:
- supervision for micro-surface behavior
- helps network separate color from reflectance structure

## 9.6 Normals
World-space normals.

Purpose:
- geometric orientation cue
- helps network understand surface direction relative to light and camera

## 9.7 World Position / `P`
World-space position.

Purpose:
- explicit spatial context
- very useful for coordinate-based learning and debugging

---

# 10. Optional Debug / Utility Passes

These are not mandatory for the first dataset, but are useful while building `neuromat`.

## Useful debug passes
- AO
- Curvature
- Variation map
- Dirt map
- Wear map
- Bump strength / preview
- Material ID
- Camera ID

These help validate the material pipeline before launching batch renders.

Use them for lookdev and QA, not necessarily for the final training set unless needed.

---

# 11. Render Specs

Keep render specs simple and stable.

## Scene rules
- fixed hero geometry
- fixed geometry scale
- fixed lighting rig
- fixed exposure
- fixed color management settings
- fixed background
- no random environment changes between materials

## Camera rules
- 200 cameras on a dome
- same focal setup unless there is a deliberate reason to vary it
- same render settings for every material and every camera

## Lighting rules
Lighting must be identical across the whole dataset.

Why:
- the network must learn material behavior, not environment changes

Allowed:
- one fixed HDRI / dome
- optional fixed neutral rim / key setup

Not allowed:
- per-material light randomization
- exposure drift
- camera-dependent light changes

## Output format
Use linear formats appropriate for training.
Prefer consistency over experimentation.

General rule:
- do not bake tone-mapped beauty as the only source of truth
- preserve linear render data where possible

---

# 12. Dataset Manifest / Metadata Requirements

The render dataset step comes after `neuromat`, but the HDA should be built with it in mind.

Each rendered frame should later be traceable to:

- material id
- semantic label
- JSON parameters snapshot or reference
- camera id
- camera transform
- camera intrinsics
- file paths for all passes

A later `transforms.json` / manifest should be able to connect:
- image files
- camera matrices
- material metadata
- semantic text labels

---

# 13. What Must Not Go Wrong

These are the real failure cases for Phase 2.

Avoid these:

## Critical failures
- non-deterministic mask generation
- lighting changes across dataset
- exposure drift
- camera-space procedural tricks
- material values changing outside JSON control
- passes that do not match the beauty render
- mislabeled AOVs
- procedural masks so strong that they override the material identity
- UV artifacts severe enough to create obvious training noise

## Acceptable limitations for now
- one hero asset only
- UV-based texturing
- not fully ideal physical shading
- not fully generalized object-space material projection
- simple procedural logic as long as it is deterministic and visually coherent

---

# 14. Build Order for This Chat

In this new chat, help me in this order:

## Step 1
Review the `neuromat` HDA structure and define the minimal parameter interface.

## Step 2
Design the internal logic for:
- `VARIATION`
- `DIRT`
- `WEAR`
- `BUMP`

using:
- JSON controls
- AO
- curvature
- COPS
- MaterialX procedural textures

## Step 3
Wire these masks into a stable MaterialX shader:
- base color
- roughness
- bump / normal
- transmission / coat where needed

## Step 4
Define the required AOVs and how to extract them cleanly in Solaris / Karma.

## Step 5
Prepare the setup so it can later be rendered through TOPs for:
- 2,000 material variations
- 200 cameras

Do not jump to training code yet.
First finish `neuromat` correctly.

---

# 15. Working Philosophy

I am a solo artist.
This project must move forward.
Perfection is not the goal.

The correct approach is:

- keep it minimal
- keep it deterministic
- keep it physically plausible
- avoid critical mistakes
- accept non-ideal choices if they do not break Phase 2

I do **not** want a big theoretical redesign.
I want a practical path to finish `neuromat`, get good renders, and move to dataset generation next.

---

# 16. Expected Help Style

In this chat, help me with:

- concrete HDA design decisions
- MaterialX wiring logic
- mask-building logic in COPS / MaterialX
- pass / AOV planning
- practical Houdini-specific implementation steps
- debugging suspicious material behavior

Avoid:
- abstract research detours
- large architecture rewrites
- advice that assumes a team or long pipeline schedule
- anything that ignores the current working setup

Start from the current architecture and push it to a clean usable state.