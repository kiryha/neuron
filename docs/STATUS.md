# Current project status

- Last verified: 2026-09-16
- Repository baseline inspected: `main` at `7a09552`
- Current phase: **Phase 2A learning baseline; production dataset repair pending for six EXRs**

## Current objective

Repair the six corrupt production EXRs, then run the first reproducible full-library coordinate-MLP experiment using the frozen material-level splits. The loader, validator, model, masked loss, trainer, checkpoint evaluator, one-material overfit, and eight-material prompt-conditioning stress run are implemented and verified.

The accepted learning sequence is: train on one fixed view; test Three.js orbit, zoom, and alternate-mesh inputs as deliberately unsupported cases; add multi-view Houdini data and retrain; then add multi-geometry data and retrain. Improvement between versions is an experiment to measure, not an assumed capability.

## Verified working artifacts

### Repository

- `datagen/materials.py` is the current material and label generator.
- `datagen/datarender.py` creates the camera dome and implements sequential dataset rendering from the DEV or PROD material library selected in its UI.
- Dataset rendering checks existing folders, reports `RESUME completed/total`, and calls the blocking USD Render ROP for each missing material one at a time. The next material is not submitted until the call returns and a non-empty `render.exr` exists. There is no whole-dataset progress bar.
- `datarender_headless.bat` loads the hardcoded production `.hiplc` and material JSON through Houdini 22's `hython.exe`, rendering without the Houdini GUI while streaming the same `Dataset Render Started`, `RESUME`, and `RENDER` reports to a console. The original in-Houdini Datarender UI remains available.
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
- `train/` contains a working multipart-EXR reader, full-read validator, deterministic material splits, sampled-pixel data path, coordinate-conditioned residual MLP, coverage-weighted L1 loss, trainer, checkpoint evaluator, and unit tests.
- The accepted v0 baseline has 822,723 parameters and conditions on Fourier-encoded `P`, normalized `Nb`/`V`, and learned categorical embeddings for base, color, finish, and condition.
- A 5,000-step `gold_polished_clean` overfit reached full-frame linear-RGB L1 `0.035157`; its target/prediction comparison is visually close.
- The best checkpoint from an eight-material, 5,000-step stress run reached mean full-frame L1 `0.039920`. All eight target/prediction pairs show distinct, appropriate appearances; polished glass is the hardest case at `0.127516`.
- Four unit tests covering vocabularies, deterministic/disjoint splits, loss behavior, model shape, and gradients pass under the isolated `.venv` environment.
- `docs/tutorials/training-a-text-conditioned-image-model.md` is a comprehensive educational guide to text-conditioned image training. Its coordinate-MLP design is now the implemented and verified first baseline.
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
  - Modified: 2026-09-03 22:21
- Active HDA resolved by scene 006: `hda\lop_KKO8--neuromat-1.3.hdalc`
  - Type: `KKO8::neuromat::1.3`
  - Modified: 2026-09-03 16:23
- Generated JSON: `E:\Projects\neuron_data\neuron_library.json`
  - Current content: eight-material stress subset
  - Modified: 2026-04-16 15:39
- Workstation NVIDIA driver: **582.78**. Verified after reboot with `nvidia-smi` and Houdini 22.0.368 `hgpuinfo`; a temporary GPU-only Karma XPU smoke render completed with one `Optix` device, 100% GPU contribution, and an empty device-error field. The former OptiX ABI failure on driver 539.19 is resolved.
- The external stress JSON remains useful for look-dev, but it is not the production batch source.
- `datagen/hips/` contains older scene-006 and `neuromat` 1.2 snapshots. The external scene and its resolved 1.3 HDA are authoritative.

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

**Verified by a full decode audit of the production `cam_001` directory on 2026-09-16:**

- All 1,806 expected material folders and non-empty `render.exr` files exist, with no unexpected folders.
- 1,800 EXRs fully decode at 1024 × 1024 with finite `C`, `P`, `V`, and `Nb` data and the required channels.
- Six EXRs are corrupt and must be rerendered: `car_paint_purple_brushed_clean`, `car_paint_red_satin_dusty`, `car_paint_teal_matte_clean`, `car_paint_teal_polished_clean`, `plastic_abs_black_matte_scratched`, and `plastic_abs_black_polished_clean`.

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
- Resume behavior: skip only when the material folder contains a non-empty final `render.exr`. Existing empty folders and folders containing only `render_part.exr` are reused and rerendered; deleting them manually is unnecessary.

## Open risks before dataset acceptance

| Priority | Blocker | Required resolution |
| --- | --- | --- |
| P0 | Six of 1,806 production EXRs are corrupt | Delete only the six named material folders and resume the deterministic render, then rerun the full-read validator |
| P1 | Unresolved transmission-scatter policy | Verify or explicitly classify `transmission_scatter` behavior |

## Next exact actions

1. Rerender the six corrupt material folders and rerun `train/validate_dataset.py` across all 1,806 records.
2. Add an I/O-efficient full-library training schedule, preserve the frozen material splits, and run the first reproducible full experiment.
3. Evaluate train, validation, and compositional-test IDs and compare against prompt-agnostic and nearest-material baselines.
4. Resolve or explicitly classify `transmission_scatter` behavior.
5. Load a saved checkpoint in a clean process, then integrate prompt-driven inference with the camera-matched Three.js `P`/`N`/`V`/Coverage buffers.

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
