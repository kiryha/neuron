# Current project status

- Last verified: 2026-08-28
- Repository baseline inspected: `main` at `1e57aaf`
- Current phase: **Phase 1 — finish and validate Houdini data generation**

## Current objective

Finish the `neuromat` HDA, validate the eight-material stress set, and lock the render and manifest contract before building the camera/TOP automation or producing the complete dataset.

## Verified working artifacts

### Repository

- `datagen/materials.py` is the current material and label generator.
- The generator defines 56 bases, 5 finishes, 4 conditions, 10 colors, and 4 categories.
- Compatibility filtering produces **1,806** material records.
- Current bump-type distribution is 1,143 stochastic, 396 directional, and 267 cellular records.
- A full regeneration plus validation of all 1,806 records passes with no unsupported bump modes.
- The Houdini UI currently generates an eight-material stress subset by default.
- `train/train_hero.py` and `train/loss.py` are empty.
- `neuron/` contains only a package scaffold.
- The React app displays a cyan emissive placeholder sphere.
- `main.py` serves the built frontend and exposes only `/api/status`.

### External Houdini project

- Project root: `C:\Users\kko8\OneDrive\projects\neuron\prod\3D`
- Active scene: `scenes\material_hero_004.hipnc`
  - Modified: 2026-08-28 13:22
- Active HDA: `hda\lop_KKO8.neuromat.1.2.hdanc`
  - Type: `KKO8::neuromat::1.2`
  - Modified: 2026-08-28 13:20
- Generated JSON: `E:\Projects\neuron_data\neuron_library.json`
  - Current content: eight-material stress subset
  - Modified: 2026-04-16 15:39
- Repository Houdini files under `datagen/hips/` are older copies and are not the active assets.

### Geometry and scene

- Geometry: Sculpted Rubber Toy
- Final displayed geometry: 1,611,108 points and 3,239,506 primitives
- Point attributes: `P`, `ao`, `convex_macro`, `concave_macro`, `convex_micro`, `concave_micro`
- Vertex attribute: `uv`
- Camera: one 28 mm camera
- Dome light: `studio_kontrast_04_2k.hdr`, intensity `1.0`, exposure `-0.5`
- Karma engine: XPU
- Current test resolution: 1280 × 1280
- Current path-traced samples: 64
- Denoiser: off

### Material system

**Implemented and present in the live graph:**

- JSON-driven top-level material parameters
- Internal `/stage/neuromat/read_JSON_data` Python Script LOP that resolves `material_id` from `dataset_path` and applies JSON values during the HDA cook
- Internal bump-type and bump-cap Python Script LOPs
- Standard Surface references for `subsurface`, `subsurface_color`, and `thin_walled`
- UV-based map projection
- Variation mask affecting appearance
- AO/concavity-driven dirt
- Convexity-driven wear
- MaterialX shader and Karma rendering
- Debug outputs for variation, dirt, wear, and bump

**Current selected material:**

- `glass_polished_clean`
- JSON bump type: stochastic
- Bump scale: `0.002`
- Noise scale: `1.0`
- Bump cap: `0.006`

## Current incomplete or incorrect state

### Bump implementation

- The production bump switch now uses direct `bump_type_int` selection.
- Inputs are connected as none `0`, stochastic `1`, directional `2`, and cellular `3`.
- Stochastic, directional, and cellular networks are present in the production material graph.
- The final selected height is scaled, capped, and passed through MaterialX bump before the Standard Surface normal input.
- Structural implementation is complete for these four modes; visual validation across the stress set is still pending.
- Asphalt is explicitly mapped to stochastic bump at scale `0.02`; the generator and checked-in production library no longer contain the unsupported `cracked` mode.

### Material application path

- The Houdini UI intentionally changes only the HDA `material_id` string.
- During the HDA cook, `/stage/neuromat/read_JSON_data` loads the record from the configured `dataset_path` and applies metadata, procedural values, base/specular/coat/transmission values, sheen, SSS, and thin-wall values to the HDA.
- `/stage/neuromat/set_bump_type` maps none, stochastic, directional, and cellular to integer modes; an unknown value currently defaults to stochastic mode `1`.
- `/stage/neuromat/set_bump_cap` derives the internal safety cap from finish and condition.
- This design is working interactively and is suitable for future batching by changing one material ID per work item.
- `datagen/tools.py::apply_material()` is an older partial alternative and is not the active UI path; it should be removed or clearly marked legacy later to prevent confusion.

### Current bump construction

- Stochastic frequencies: `noise_scale × 50` and `noise_scale × 120`
- Stochastic octaves: `3 / 2`
- Stochastic weights: `0.7 / 0.3`
- Directional frequency: `noise_scale × (80, 8)` in UV space
- Directional/stochastic breakup weights: `0.8 / 0.2`
- Cellular frequency: `noise_scale × 18`
- Cellular/stochastic breakup weights: `0.85 / 0.15`
- Polished-clean bump cap: `0.006`; other finish/condition combinations: `0.02`

These are implemented values, not yet approved final look-dev values. Judge them under the fixed camera/light setup before locking the HDA.

### Remaining shader coverage

- `subsurface`, `subsurface_color`, and `thin_walled` are now linked from the HDA interface to the live Standard Surface parameters.
- `k` and `metallic_flake` are present in JSON but are not consumed by the current production shader graph.
- The intended Karma/MaterialX treatment of `transmission_scatter` still requires explicit verification.
- The current bump AOV is derived after `mtlxbump`; its meaning should be documented as altered normal versus scalar height before training use.

### Render outputs

Current RenderVars:

- Beauty (`color4f`)
- World hit position `P`
- Camera depth `Pz`
- Hit normal `N`
- Variation mask
- Dirt mask
- Wear mask
- Bump debug output

There is no separate Alpha RenderVar; confirm that the beauty alpha is correct and stable. BaseColor and Roughness RenderVars are not implemented. They are optional auxiliary/diagnostic outputs for the direct-RGB model, not generated products.

### Labels

- The label engine is deterministic and uses controlled template families.
- Existing stress JSON was generated before the latest validation work and is skipped by default because labels already exist.
- At least one current label contains `with with` (`gold_polished_clean`). Duplicate-word validation must be added or labels must be corrected before dataset release.

## Blockers before a full render

| Priority | Blocker | Required resolution |
| --- | --- | --- |
| P0 | Watermarked/noncommercial development renders | Produce final training images through a suitable non-watermarked Houdini render path |
| P0 | Bump look-dev not validated | Render and review stochastic, directional, and cellular stress materials before automation |
| P0 | No dataset automation or manifest | Build and validate a small camera/material pilot before full scale |
| P1 | Unresolved shader-schema fields | Implement or explicitly classify `k`, metallic flake, and transmission-scatter behavior |
| P1 | Label defect | Prevent duplicate words and regenerate/overwrite affected labels |
| P1 | Render contract not frozen | Verify alpha, coordinate spaces, color management, naming, and metadata |
| P2 | One camera only | Implement and validate the planned camera distribution after HDA lock |

## Next exact actions

1. Render all eight stress materials from the current fixed camera and lighting setup.
2. Inspect beauty plus variation, dirt, wear, and bump/normal diagnostics for each material.
3. Approve or retune stochastic, directional, and cellular bump from those comparisons.
4. Resolve remaining shader-schema fields and confirm the final RenderVars.
5. Fix label duplicate-word QA and regenerate the stress labels with overwrite enabled.
6. Freeze the HDA/scene as the approved material-render baseline.
7. Build the camera dome and render a small stress-material × camera pilot.
8. Validate view consistency, camera metadata, AOV alignment, and manifest structure.
9. Only then automate and launch the full material × camera batch.

## Phase 1 exit criteria

Phase 1 is complete only when:

- every material record maps to supported HDA behavior;
- UI material selection reliably cooks and applies the complete intended JSON record;
- the stress set passes visual and data QA;
- repeated renders are deterministic;
- camera, color, AOV, file, and manifest contracts are frozen;
- final outputs contain no watermark;
- a multi-camera pilot can be loaded by a minimal dataset validator;
- the full material/camera batch can be resumed without manual per-frame intervention.
