# Current project status

- Last verified: 2026-09-04
- Repository baseline inspected: `main` at `72d903a`
- Current phase: **Phase 1C dataset rendering, with an accepted early Phase 2B frontend slice and Phase 2A preparation**

## Current objective

Complete the currently running `material_hero_v0` production render without changing the frozen scene, HDA, material library, camera, or render settings. The user reports that part of the material library is already rendered; the current external output count and files have not yet been independently inspected from this repository session.

Training-pipeline development can use a frozen inventory of completed renders for loader validation and deliberate one-material or small-subset overfitting. Definitive full-library training and evaluation wait for render completion, count validation, and representative EXR QA. The accepted local Three.js normal-viewer slice remains implemented and verified.

The accepted learning sequence is: train on one fixed view; test Three.js orbit, zoom, and alternate-mesh inputs as deliberately unsupported cases; add multi-view Houdini data and retrain; then add multi-geometry data and retrain. Improvement between versions is an experiment to measure, not an assumed capability.

## Verified working artifacts

### Repository

- `datagen/materials.py` is the current material and label generator.
- `datagen/datarender.py` creates the camera dome and implements sequential dataset rendering from the DEV or PROD material library selected in its UI.
- Dataset rendering is sequential and uses Houdini's native **Interrupt** window. Existing folders are counted before restart and reported as `RESUME completed/total`; only missing folders are queued. A separate Qt whole-dataset window was removed because the blocking USD Render ROP prevented it from repainting reliably.
- At dataset-render start, Datarender creates a missing `{geometry_id}/{camera_id}/{camera_id}.json` from the cooked USD camera and Render Settings resolution and leaves an existing record unchanged. If Houdini does not expose a cooked stage at that moment, it falls back to the simple look-at Camera LOP and Render Settings parameters used by this project. The web app uses this small record to reconstruct the training view; it is not a model input.
- Single-camera mode renders the named `/cameras/cam_###` prim; multi-camera mode dynamically reads Camera LOPs inside `/stage/camera_dome`.
- Geometry switching is not implemented. The currently connected `neuromat` geometry is rendered, and the geometry-name field supplies only its dataset folder name.
- `datagen/ui/ui_datarender.py` is generated from the user-authored `ui_datarender.ui`.
- The generator defines 56 bases, 5 finishes, 4 conditions, 10 colors, and 4 categories.
- Compatibility filtering produces **1,806** material records.
- Current bump-type distribution is 1,143 stochastic, 396 directional, and 267 cellular records.
- A full regeneration plus validation of all 1,806 records passes with no unsupported bump modes.
- `datagen/data/neuron_library_prod.json` is the accepted render-system material source of truth.
- Both Houdini tools expose `neuron_library_dev` and `neuron_library_prod` selectors, with DEV first and selected by default.
- In Datagen, reload, material generation, prompt generation, and material application use the selected library. DEV generation writes the eight-material stress set; PROD generation writes all 1,806 records.
- Applying a material also sets `neuromat.dataset_path` to the selected repository JSON before setting `material_id`.
- `train/train_hero.py` and `train/loss.py` are empty.
- `docs/tutorials/training-a-text-conditioned-image-model.md` is a comprehensive educational guide to text-conditioned image training. Its coordinate-MLP design and training plan are recommendations pending an explicit architecture decision.
- `neuron/` contains only a package scaffold.
- The React app loads the Sculpted Rubber Toy and lets the user inspect world-space `N`, `P`, or `V` on a black background with OrbitControls and no grid. The active selector defaults to `N`.
- `neuron_dev.bat` launches the local Vite server at `http://127.0.0.1:5173` with hot reload; `neuron.bat` continues to serve the latest production build through FastAPI.
- `public/geometry/material_hero/sculpted-rubber-toy.glb` is the accepted single web geometry. The current export is a valid 12,253,276-byte binary glTF.
- `public/cameras/material_hero/cam_001.json` is the active copied dataset camera record.
- The app loads `cam_001.json`, derives vertical field of view from its lens/aperture/aspect, applies its position and up vector, and resets to that dataset view. OrbitControls pivots around world origin because every Houdini dataset camera aims at origin; the JSON `target` is only a forward-axis reference point. Its half-float geometry target uses the JSON resolution and retains the selected raw `N`, `P`, or `V` values; display encoding is applied only to the viewport preview. The bottom-center prompt field does not yet trigger inference.
- The hero GLB remains at its exported identity transform in Three.js; no application-side centering or scaling is applied.
- No geometry metadata file, separate proxy/calibration LODs, geometry hash, or formal pixel-precise Houdini-to-Three.js calibration gate is required for v0. Camera matching uses the per-camera dataset JSON, while geometry transform and `P`/`N`/`V` conventions remain explicit application requirements.
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
- DOF is disabled in scene 006. The visible `Enable Depth of Field` parameter and its underlying `enabledof` value are both off (`0`). Camera f-stop `1.2` remains authored but has no effect while the master toggle is off; the internal `disableDepthOfField = false` value is not a reliable inverse-status check for this Karma node.

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
- Interactive selections are transient; Datagen and Datarender set `dataset_path` in memory, and the batch renderer overrides `material_id` for every batch item.

## Current incomplete or incorrect state

### Bump implementation

- The production bump switch now uses direct `bump_type_int` selection.
- Inputs are connected as none `0`, stochastic `1`, directional `2`, and cellular `3`.
- Stochastic, directional, and cellular networks are present in the production material graph.
- The final selected height is scaled, capped, and passed through MaterialX bump before the Standard Surface normal input.
- Structural implementation is complete for these four modes; the fixed-camera stress renders were visually approved by the user on 2026-09-02.
- Asphalt is explicitly mapped to stochastic bump at scale `0.02`; the generator and checked-in production library no longer contain the unsupported `cracked` mode.

### Material application path

- Datagen sets the HDA `dataset_path` from its **Material Library JSON** selection and then changes the HDA `material_id` string.
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

**Verified in the live Datarender DEV pilot at `E:\Projects\neuron_data\datasets\material_hero_v0` on 2026-09-03:**

- One `sculpted_rubber_toy/cam_001/{material_id}/render.exr` file for each of the eight DEV records, with no missing or unexpected material folders.
- Every EXR is readable, 512 × 512, finite, and contains multipart Beauty RGBA (`C`), `P`, `V`, and `Nb` with the expected channel names.
- Beauty alpha ranges from `0` to `1`; all materials share the same underlying silhouette, with small stochastic antialiasing differences at low sampling.
- The beauty previews are framed consistently and show distinct intended materials. Transmissive glass is visibly noisy at these test settings, so this pilot validates automation rather than final image quality.
- This pilot directory cannot be continued directly as the 1024 × 1024 production dataset: folder-existence skipping would retain the eight low-quality images.

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
- The JSON snapshot and folder names are the training-data index; no manifest or geometry/dataset records are required. One minimal camera JSON per camera folder is retained for web-view matching.
- Implemented camera stage: `datarender.py` creates an unconnected `/stage/camera_dome` subnet containing sequential Camera LOPs that author `/cameras/cam_###` prims. The user connects the subnet manually.
- Camera positions use a full-sphere Fibonacci distribution, look at world origin, and share a distance derived from the UI focal length, approximate object size, and margin multiplier; no geometry bounds are read.
- Implemented render stage: for every selected camera and JSON material ID, set the Karma camera, set `neuromat.material_id`, write `render.exr`, and invoke `/stage/usdrender_rop1` at the current frame.
- When rendering starts, Datarender sets `neuromat.dataset_path` to the selected repository JSON, renders every record in it, copies that JSON once into the dataset root, and creates any missing per-camera JSON from the cooked USD camera and resolution. `P`, `Nb`, `V`, and `C.A` remain the complete model-context contract; no geometry metadata is written.
- Resume behavior: skip when the material folder exists; delete the folder manually to request a rerender.

## Open risks before dataset acceptance

| Priority | Blocker | Required resolution |
| --- | --- | --- |
| P0 | Production dataset render is incomplete | Finish the current batch, confirm 1,806 material folders, and inspect representative EXRs before definitive training |
| P1 | Unresolved transmission-scatter policy | Verify or explicitly classify `transmission_scatter` behavior |
| P1 | Karma XPU reported one critical error and used only Embree CPU | Inspect Houdini's Log Viewer and decide whether GPU rendering must be restored before the full 1,806-material run |

## Next exact actions

1. Let the current `material_hero_v0` production render finish without changing its frozen inputs or settings.
2. In parallel, use a fixed list of completed renders to implement and validate the training loader, then intentionally overfit one material and a small subset after the first architecture is accepted.
3. After rendering, confirm 1,806 material folders and inspect representative metal, dielectric, organic, translucent, bump, dirt, and wear outputs.
4. Inspect the Karma critical error and CPU-only XPU device state if it continues to affect render reliability or timing.
5. Resolve or explicitly classify `transmission_scatter` behavior.
6. Freeze training splits and run the first reproducible full-library model experiment.
7. Extend the camera-matched web buffer path with Coverage and prompt-driven inference.

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
