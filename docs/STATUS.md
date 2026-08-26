# Current project status

- Last verified: 2026-08-26
- Repository baseline inspected: `main` at `02ba1a3`
- Current phase: **Phase 1 — finish and validate Houdini data generation**

## Current objective

Finish the `neuromat` HDA, validate the eight-material stress set, and lock the render and manifest contract before building the camera/TOP automation or producing the complete dataset.

## Verified working artifacts

### Repository

- `datagen/materials.py` is the current material and label generator.
- The generator defines 56 bases, 5 finishes, 4 conditions, 10 colors, and 4 categories.
- Compatibility filtering produces **1,806** material records.
- Current bump-type distribution is 1,131 stochastic, 396 directional, 267 cellular, and 12 cracked records.
- The Houdini UI currently generates an eight-material stress subset by default.
- `train/train_hero.py` and `train/loss.py` are empty.
- `neuron/` contains only a package scaffold.
- The React app displays a cyan emissive placeholder sphere.
- `main.py` serves the built frontend and exposes only `/api/status`.

### External Houdini project

- Project root: `C:\Users\kko8\OneDrive\projects\neuron\prod\3D`
- Active scene: `scenes\material_hero_004.hipnc`
  - Modified: 2026-08-26 14:14
- Active HDA: `hda\lop_KKO8.neuromat.1.2.hdanc`
  - Type: `KKO8::neuromat::1.2`
  - Modified: 2026-04-24 15:56
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
- UV-based map projection
- Variation mask affecting appearance
- AO/concavity-driven dirt
- Convexity-driven wear
- MaterialX shader and Karma rendering
- Debug outputs for variation, dirt, wear, and bump

**Current selected material:**

- `iron_brushed_scratched`
- JSON bump type: directional
- Bump scale: `0.1`
- Noise scale: `0.5`
- Dirt: `0.1`
- Wear: `0.9`

## Current incomplete or incorrect state

### Bump routing

- The production bump switch has only `none` and `stochastic` inputs connected.
- JSON/HDA values are intended as none `0`, stochastic `1`, directional `2`, cellular `3`.
- The live selector expression is `ch("../../../bump_type_int") - 1`.
- Therefore a directional material currently selects the stochastic input; cellular selects an unconnected input.
- The Python generator also emits `cracked` for 12 asphalt combinations, but no cracked HDA branch or enum mapping is currently implemented.

### Material application path

- The Houdini UI intentionally changes only the HDA `material_id` string.
- During the HDA cook, `/stage/neuromat/read_JSON_data` loads the record from the configured `dataset_path` and applies metadata, procedural values, base/specular/coat/transmission values, sheen, SSS, and thin-wall values to the HDA.
- `/stage/neuromat/set_bump_type` maps none, stochastic, directional, and cellular to integer modes; an unknown value currently defaults to stochastic mode `1`.
- `/stage/neuromat/set_bump_cap` derives the internal safety cap from finish and condition.
- This design is working interactively and is suitable for future batching by changing one material ID per work item.
- `datagen/tools.py::apply_material()` is an older partial alternative and is not the active UI path; it should be removed or clearly marked legacy later to prevent confusion.

### Stochastic bump checkpoint

Current live settings:

- Coarse frequency: `noise_scale × 6`
- Fine frequency: `noise_scale × 24`
- Coarse/fine octaves: `3 / 2`
- Coarse/fine weights: `0.7 / 0.3`
- General bump cap for the selected material: `0.02`

The last look-dev result read as broad, melted macro-waviness. The next planned test from the HDA discussion was approximately:

- Coarse frequency: `noise_scale × 40`
- Fine frequency: `noise_scale × 160`
- Coarse/fine octaves: `2 / 1`
- Coarse/fine weights: `0.85 / 0.15`
- Test bump height near `0.0015`
- Conservative cap near `0.004–0.006`

These are **planned test values**, not accepted production constants.

### Shader wiring

- `subsurface`, `subsurface_color`, and `thin_walled` are loaded at the HDA interface but are not connected to the live Standard Surface result.
- `k` and `metallic_flake` are present in JSON but are not consumed by the current production shader graph.
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
| P0 | Incomplete bump routing | Implement and validate every bump type emitted by the material generator, or remove unsupported records |
| P0 | No dataset automation or manifest | Build and validate a small camera/material pilot before full scale |
| P1 | Missing shader wiring | Connect or explicitly remove unsupported SSS, thin-wall, `k`, and flake behavior |
| P1 | Label defect | Prevent duplicate words and regenerate/overwrite affected labels |
| P1 | Render contract not frozen | Verify alpha, coordinate spaces, color management, naming, and metadata |
| P2 | One camera only | Implement and validate the planned camera distribution after HDA lock |

## Next exact actions

1. Save a new HDA version or recoverable backup before editing.
2. Replace the temporary offset bump selector with a direct, documented routing scheme.
3. Decide how `cracked` asphalt records are handled: implement the branch or exclude them from v1.
4. Tune stochastic bump on a material whose intended branch is stochastic.
5. Implement and validate directional bump using `iron_brushed_scratched`.
6. Implement and validate cellular bump using `concrete_hammered_clean`.
7. Validate all eight stress materials, including translucent and SSS cases.
8. Resolve missing shader inputs and confirm the final RenderVars.
9. Fix label duplicate-word QA and regenerate the stress labels with overwrite enabled.
10. Render a small multi-camera pilot and validate the manifest before scaling up.

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
