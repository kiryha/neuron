# Current project status

- Last verified: 2026-09-03
- Repository baseline inspected: `main` at `7e268d7`
- Current phase: **Phase 1 — finish and validate Houdini data generation**

## Current objective

Disable DOF in scene 006, then run the implemented `datagen/datarender.py` renderer as an eight-material, one-hero, one-camera pilot.

The accepted learning sequence is: train on one fixed view; test Three.js orbit, zoom, and alternate-mesh inputs as deliberately unsupported cases; add multi-view Houdini data and retrain; then add multi-geometry data and retrain. Improvement between versions is an experiment to measure, not an assumed capability.

## Verified working artifacts

### Repository

- `datagen/materials.py` is the current material and label generator.
- `datagen/datarender.py` is the implemented sequential hython renderer. It defaults to the stress set, supports explicit `--all`/`--materials` selection and `--dry-run`, snapshots the production JSON once, skips existing material folders, and never saves the HIP file.
- The generator defines 56 bases, 5 finishes, 4 conditions, 10 colors, and 4 categories.
- Compatibility filtering produces **1,806** material records.
- Current bump-type distribution is 1,143 stochastic, 396 directional, and 267 cellular records.
- A full regeneration plus validation of all 1,806 records passes with no unsupported bump modes.
- `datagen/data/neuron_library_prod.json` is the accepted render-system material source of truth.
- The Houdini UI currently generates an eight-material stress subset by default.
- `train/train_hero.py` and `train/loss.py` are empty.
- `neuron/` contains only a package scaffold.
- The React app displays a cyan emissive placeholder sphere.
- `main.py` serves the built frontend and exposes only `/api/status`.

### External Houdini project

- Project root: `C:\Users\kko8\OneDrive\projects\neuron\prod\3D`
- Active scene: `scenes\material_hero_006.hiplc`
  - Modified: 2026-09-03 11:15
- Active HDA: `hda\lop_KKO8.neuromat.1.2.otllc`
  - Type: `KKO8::neuromat::1.2`
  - Modified: 2026-09-03 10:30
- Generated JSON: `E:\Projects\neuron_data\neuron_library.json`
  - Current content: eight-material stress subset
  - Modified: 2026-04-16 15:39
- The external stress JSON remains useful for look-dev, but it is not the production batch source.
- `datagen/hips/` contains Indie snapshots of scene 006 and the HDA. The checked-in HDA matches the active external file; the external scene is newer than its repository snapshot and is authoritative.

### Geometry and scene

- Geometry: Sculpted Rubber Toy
- Final displayed geometry: 1,611,108 points and 3,239,506 primitives
- Point attributes include `P`, `N_base`, `ao`, `convex_macro`, `concave_macro`, `convex_micro`, and `concave_micro`.
- Vertex attribute: `uv`
- Camera: `/cameras/camera`, one 28 mm perspective camera at frame 1; the apparent USD `50` value was the no-time schema fallback, not the cooked lens
- Dome light: `studio_kontrast_04_2k.hdr`, intensity `1.0`, exposure `-0.5`
- Karma engine: XPU
- Current candidate dataset resolution: 1024 × 1024
- Current path-traced samples: 128
- Denoiser: off
- The active `/Render/rendersettings` prim resolves to 1024 × 1024. `/Render/Products/renderproduct` reports 2048 × 1080 only as an unauthored USD fallback, so it does not override the active resolution.
- DOF is accepted as disabled for dataset v0, but read-only inspection of scene 006 still finds camera f-stop `1.2` and Render Settings `disableDepthOfField = false`.

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

- The saved scene currently has `material_id = iron_brushed_scratched`.
- Interactive selections are transient; `datarender.py` overrides `dataset_path` and `material_id` in memory for every batch item.

## Current incomplete or incorrect state

### Bump implementation

- The production bump switch now uses direct `bump_type_int` selection.
- Inputs are connected as none `0`, stochastic `1`, directional `2`, and cellular `3`.
- Stochastic, directional, and cellular networks are present in the production material graph.
- The final selected height is scaled, capped, and passed through MaterialX bump before the Standard Surface normal input.
- Structural implementation is complete for these four modes; the fixed-camera stress renders were visually approved by the user on 2026-09-02.
- Asphalt is explicitly mapped to stochastic bump at scale `0.02`; the generator and checked-in production library no longer contain the unsupported `cracked` mode.

### Material application path

- The Houdini UI intentionally changes only the HDA `material_id` string.
- During the HDA cook, `/stage/neuromat/read_JSON_data` loads the record from the configured `dataset_path` and applies metadata, procedural values, base/specular/coat/transmission values, sheen, SSS, and thin-wall values to the HDA.
- `/stage/neuromat/set_bump_type` maps none, stochastic, directional, and cellular to integer modes; an unknown value currently defaults to stochastic mode `1`.
- `/stage/neuromat/set_bump_cap` derives the internal safety cap from finish and condition.
- This design is working interactively and is suitable for future batching by changing one material ID per work item.
- The UI helper `Datagen.set_material()` now lives directly on the `Datagen` class in `datagen/datagen.py`; the obsolete partial `datagen/tools.py` module has been removed.

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
- `k` and `metallic_flake` are explicitly classified as unused metadata for v1. They remain in JSON for provenance/future work but are intentionally ignored by the production graph and do not affect pixels.
- The intended Karma/MaterialX treatment of `transmission_scatter` still requires explicit verification.
- The current bump AOV is derived after `mtlxbump`, but it is no longer part of the accepted dataset output and will be disabled before the pilot.

### Render outputs

**Verified in `concrete_hammered_clean.exr` rendered from scene 006 on 2026-09-03:**

- 1024 × 1024 Beauty RGBA (`C`)
- World position `P`
- Smooth, unbumped world normal `Nb`, sourced from `N_base`
- Normalized world view direction `V`, from surface toward camera
- No obsolete debug AOVs and no non-finite values
- No Houdini Apprentice watermark; the render used an Indie `.usd`

`V` has mean length `1.0`, mean unit-length error `1.1e-7`, and mean dot product `0.9999999` against `normalize(camera_position - P)`. `Nb` and `V` should be renormalized in the data loader after pixel filtering, especially around silhouettes and internal visibility boundaries.

Coverage is now defined as Beauty alpha `C.A`; no separate Coverage subimage is required. The library drives transmission but not Standard Surface opacity, and the user verified that glass remains alpha `1` on covered interior pixels. Keep opacity fixed at `1`; cutouts, holdouts, and alpha-changing shadow-catcher behavior are outside this contract.

`Pz`, variation, dirt, wear, bump, BaseColor, Roughness, and other diagnostic outputs are excluded from the dataset. Their underlying material effects remain visible in `C.RGB`.

### Labels

- The label engine is deterministic and uses controlled template families.
- Templates no longer insert a second `with` before finish descriptions, and adjacent duplicate words are rejected by both entry and assembled-label validation.
- Existing labels are validated even when overwrite is disabled.
- All 1,806 production labels were regenerated with seed `42`; zero adjacent duplicates remain.

### Dataset batch design

- Accepted external root: `E:\Projects\neuron_data\datasets`.
- Dataset directory: `material_hero_v0`.
- Copy `neuron_library_prod.json` unchanged into the dataset root; no checksum or renamed copy is required.
- One multilayer EXR is stored at `{geometry_id}/{camera_id}/{material_id}/render.exr`.
- The JSON snapshot and folder names are the dataset index; no manifest or camera/geometry/dataset records are required.
- Implemented automation: sequential `datagen/datarender.py` with explicit geometry and camera lists.
- Resume behavior: skip when the material folder exists; delete the folder manually to request a rerender.
- Verified without rendering: syntax and CLI parsing; two-material dry-run; existing-folder skip behavior; required Houdini nodes and USD geometry/camera prims; Indie license detection.

## Blockers before a full render

| Priority | Blocker | Required resolution |
| --- | --- | --- |
| P0 | Automated pilot not yet run | Disable DOF, then run `datagen/datarender.py` on the eight-material fixed-camera stress set |
| P1 | Unresolved transmission-scatter policy | Verify or explicitly classify `transmission_scatter` behavior |
| P1 | DOF remains enabled in scene 006 | User disables DOF before the automated pilot; Codex must not edit or save the HIP file |
| P1 | Karma XPU reported one critical error and used only Embree CPU | Inspect Houdini's Log Viewer and decide whether GPU rendering must be restored before the full 1,806-material run |

## Next exact actions

1. User disables DOF in scene 006 and refreshes the repository scene snapshot after the final user-operated save; Codex must never edit or save the HIP file.
2. Run `datagen/datarender.py --dry-run`, then run the default eight-material pilot.
3. Inspect the Karma critical error and CPU-only XPU device state before estimating the full render.
4. Manually inspect the pilot, including an opaque-versus-glass `C.A` comparison and restart/skip test.
5. Resolve or explicitly classify `transmission_scatter` behavior before the full batch.
6. Run `datagen/datarender.py --all` only after the pilot is approved.
7. Reproduce the Houdini training camera and hero buffers in Three.js and compare `P`, `N`, `V`, Coverage, silhouette, and projection.
8. Train the first model and record exact-view, orbit/zoom, and alternate-mesh results.
9. Only after the fixed-view baseline is understood, build a camera-dome pilot for the next dataset version.

## Phase 1 exit criteria

Phase 1 is complete only when:

- every material record maps to supported HDA behavior;
- UI material selection reliably cooks and applies the complete intended JSON record;
- the stress set passes visual and data QA;
- repeated renders are deterministic;
- fixed camera, color, AOV, and file contracts are frozen;
- final outputs contain no watermark;
- a fixed-camera pilot can be loaded by the training-data reader;
- rerunning the full batch skips existing material folders, with incomplete folders handled manually.
