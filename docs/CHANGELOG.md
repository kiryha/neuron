# Project changelog

This is a concise log of meaningful project changes. It is not a replacement for Git history or `STATUS.md`.

## 2026-08-26

### Documentation baseline

- Reframed the README around the actual Material Hero milestone.
- Established canonical documentation, decision, status, roadmap, specification, runbook, and source-archive roles.
- Audited the material generator, current stress JSON, active Houdini scene, HDA graph, render settings, geometry attributes, and current AOVs.
- Confirmed direct RGB generation, one fixed Sculpted Rubber Toy, controlled lighting, and future neural assets as the accepted project direction.
- Verified the intended material application path: the UI sets `material_id`, then internal HDA Python Script LOPs load JSON values and derive bump mode/cap during the cook.
- Implemented direct bump routing and production stochastic, directional, and cellular bump branches in `neuromat` 1.2; fixed-camera stress-set validation remains pending.
- Identified remaining Phase 1 blockers: bump visual validation, unsupported cracked records, missing shader connections, label QA, dataset automation, and watermarked final renders.

## 2026-08-28

### `neuromat` shader bindings

- Connected HDA `subsurface`, `subsurface_color`, and `thin_walled` values to their MaterialX Standard Surface parameters with relative references.
- Verified the saved scene and HDA contain all five expressions: subsurface, three subsurface-color components, and thin-wall.
- Removed these fields from the HDA blocker list; `k`, metallic flake, and transmission-scatter policy remain unresolved.

### Bump schema simplification

- Removed `cracked` from the generator's valid bump types, so no new Houdini branch is required.
- Remapped all asphalt variants to the existing stochastic bump mode at scale `0.02`.
- Updated the checked-in production library and canonical documentation to match the four-mode HDA contract.

### Metadata-only shader fields

- Classified `k` and `metallic_flake` as unused metadata for Material Hero v1.
- Kept both fields in JSON for compatibility, provenance, and possible future shader work, while explicitly excluding them from required HDA behavior.
- Reduced the unresolved shader-schema work to `transmission_scatter` verification or classification.

## 2026-08-31

### Staged geometry-generalization experiment

- Made the first training release a one-geometry, one-camera prompt-to-RGB baseline conditioned by `P`, `N`, `V`, and alpha.
- Defined Three.js orbit, zoom, and alternate supplied meshes as deliberate out-of-distribution tests rather than promised first-model capabilities.
- Sequenced later dataset/model versions as multi-view on the hero followed by multi-view and multi-geometry training.
- Added Houdini-to-Three.js geometry-buffer calibration as a prerequisite so coordinate mismatch is not confused with model generalization failure.

## 2026-09-02

### Look-dev approval and batch preflight

- Recorded user approval of the fixed-camera stress renders, including stochastic, directional, and cellular bump behavior.
- Verified `material_hero_005.hipnc` and the updated `neuromat` 1.2 HDA as the current external Houdini artifacts.
- Set the repository production material JSON as the planned batch source of truth.
- Identified preflight issues before automation: development JSON still configured in the scene, 805 duplicate-word labels, and apparent camera/resolution discrepancies that required USD-time/fallback inspection.

### Scene and label preflight fixes

- Confirmed that the apparent 50 mm camera value was the USD no-time fallback; frame 1 correctly resolves to the Camera LOP's 28 mm lens.
- Confirmed that the RenderProduct's 2048 × 1080 value was an unauthored fallback and did not override the active RenderSettings resolution.
- Backed up `material_hero_005.hipnc` and changed the active candidate dataset resolution from 1280 × 1280 to 512 × 512.
- Removed template-level `with with` construction, added adjacent-word QA, and made skipped existing labels pass validation.
- Regenerated all 1,806 production labels with seed `42`; zero adjacent duplicates remain and repeated generation produced identical labels.

### Dataset-v0 batch proposal

- Set `E:\Projects\neuron_data\datasets` as the external dataset root.
- Proposed versioned release-candidate directories, deterministic material × geometry × camera paths, multilayer raw EXRs, JSON/JSONL metadata, and validate-before-skip crash recovery.
- Recorded current camera and geometry entity metadata needed for later Houdini-to-Three.js calibration.
- Clarified that the `.hipnc` scene and `.hdanc` HDA can downgrade an Indie session; converted or rebuilt `.hiplc`/`.hdalc` inputs and an unwatermarked pilot remain required.

### Minimal dataset contract accepted

- Replaced the initial production-style manifest and metadata proposal with a minimal folder-indexed dataset suitable for the solo learning project.
- Set dataset v0 to 1024 × 1024 with DOF disabled and one multilayer EXR per material folder containing Beauty, world `P`, smooth unbumped world `N`, world `V`, and material-independent Coverage.
- Excluded `Pz`, variation, dirt, wear, bump, BaseColor, Roughness, and other debug AOVs from dataset output while preserving their material effects in Beauty.
- Kept the material snapshot name `neuron_library_prod.json` and dropped dataset hashes, renamed source copies, manifests, entity records, schemas, progress logs, and automatic validation reports.
- Accepted `{geometry_id}/{camera_id}/{material_id}/render.exr` and folder-existence skipping, with manual folder deletion used to request a rerender.
- Selected a sequential `datagen/datarender.py` script instead of TOPs/PDG; the implementation remains pending.
- Verified that scene 005 already resolves to 1024 × 1024, while DOF is still active and must be disabled during the next Houdini implementation step.

### Datagen helper cleanup

- Moved the active `set_material()` helper onto the `Datagen` class in `datagen/datagen.py` and updated the UI callback to call it directly.
- Deleted the obsolete `datagen/tools.py`, including its unused partial `apply_material()` implementation.
- Recorded the standing constraint that Codex must never edit or save HIP files; required scene edits remain user-operated.

## 2026-09-03

### Indie scene and dataset-buffer validation

- Replaced the active noncommercial artifacts with `material_hero_006.hiplc` and `lop_KKO8.neuromat.1.2.otllc`; retained `datagen/hips/` files as repository snapshots while the newer external scene remains authoritative.
- Validated an unwatermarked 1024 × 1024 Indie EXR containing Beauty RGBA, world `P`, unbumped `Nb`, and world `V`, with no non-finite pixels or obsolete debug AOVs.
- Numerically verified that `V` is unit length and matches `normalize(camera_position - P)` with the intended surface-to-camera sign.
- Accepted Beauty alpha (`C.A`) as material-independent Coverage because the library changes transmission but does not drive opacity; removed the separate Coverage-AOV requirement.
- Confirmed by read-only scene inspection that DOF is still enabled (`fStop = 1.2`, `disableDepthOfField = off`) and must be disabled by the user before the automated pilot.
- Implemented the minimal sequential `datagen/datarender.py` hython renderer with explicit geometry/camera lists, stress-set default, opt-in full render, production-library snapshotting, material-folder skipping, and no HIP save operation.
- Verified CLI parsing, dry-run planning, existing-folder skip behavior, Indie-license detection, required Houdini nodes, and the current geometry/camera USD prim paths without launching a render.

### DOF and render-automation correction

- Verified that scene 006 already has the user-facing `Enable Depth of Field` control disabled; read-only inspection reports its underlying `enabledof` parameter as `0`.
- Corrected the earlier inference from camera f-stop and the confusing internal `disableDepthOfField` value. An authored f-stop does not turn DOF on while the master checkbox is off.
- Removed the premature untracked `datagen/datarender.py` draft. Render automation is again planned and will be implemented in stages from the user's forthcoming functionality description.

### Project-wide simplicity rule

- Made minimal, learning-focused implementation an explicit project decision: add only required core functionality and defer production-style metadata, hashes, manifests, validation frameworks, and abstraction layers until a concrete need appears.

### Web geometry simplification

- Verified the user-exported `public/models/material_hero/sculpted-rubber-toy.glb` as a 12,253,888-byte binary glTF and accepted it as the single Material Hero web geometry.
- Dropped the proposed geometry metadata file, separate proxy/calibration LODs, geometry hash requirement, and formal pixel-precise Houdini-to-Three.js calibration gate for v0.
- Retained the application contract to rasterize `P`, smooth unbumped `N`, Coverage, and derived `V` from the exported mesh, with the training-camera pose used as a practical reference rather than a numerical cross-renderer acceptance test.

### Local normal-viewer milestone

- Accepted an early, local-only frontend slice that replaces the placeholder with the exported hero GLB and displays its smooth world-space normal pass.
- Set the normal data convention to float `[-1, 1]` with `N * 0.5 + 0.5` used only for RGB display.
- Kept the camera orbitable and required reset to a stable app-authored reference position, target, and field of view.
- Deferred prompt UI, model inference, `P`/`V`/Coverage passes, FastAPI changes, and Hugging Face deployment.

### Datarender camera-dome stage

- Generated `datagen/ui/ui_datarender.py` from the user-authored UI containing camera-count, focal-length, and object-size inputs.
- Implemented `datagen/datarender.py` camera-dome creation using an upper-hemisphere Fibonacci distribution, world-origin look-at, and simple size/focal-length framing.
- Kept the created `/stage/camera_dome` subnet unconnected for manual Solaris wiring; the tool does not inspect geometry bounds, find existing cameras, change Karma Render Settings, or render images.
- Verified the implementation in a fresh unsaved Houdini scene with eight 28 mm cameras and a 2 m object-size input.
- Extended the UI with a frame-margin multiplier, changed camera placement from an upper hemisphere to a full Fibonacci sphere, and used the margin directly in the camera-distance calculation.
- Verified eight 28 mm cameras with a 2 m object and margin `1.25`; the resulting common camera distance is approximately `3.567 m`, with cameras present above and below the object.
- Changed generated camera names and USD prim paths to three-digit padding: `cam_000`, `cam_001`, and so on.

### Local normal-viewer implementation

- Replaced the placeholder sphere with the current 12,253,276-byte Sculpted Rubber Toy GLB.
- Added an explicit world-space normal shader, RGB display encoding, and a 1024 x 1024 half-float normal render target.
- Kept OrbitControls and added a verified top-right `Reset Camera` control that restores the app-authored reference view.
- Added a bottom-center prompt field that accepts text but intentionally has no submission or inference behavior.
- Kept the implementation local-only, confirmed a clean Vite production build, and visually verified the app with no browser warnings or errors.
- Added `neuron_dev.bat` as the double-click Vite hot-reload launcher on `127.0.0.1:5173`, leaving `neuron.bat` as the built FastAPI launcher.

### Datarender dataset loop

- Added UI controls for dataset root/name, single or dome-camera rendering, and a geometry folder name; regenerated the PySide binding.
- Implemented sequential rendering of the material JSON configured on `neuromat.dataset_path`, including one-time JSON snapshot copying and existing-material-folder skipping.
- Single-camera mode resolves the entered name under `/cameras`; multi-camera mode dynamically reads Camera LOPs from `/stage/camera_dome`.
- Deferred geometry switching: the connected `neuromat` geometry is rendered and the UI geometry name is used only as its folder ID.
- Kept the dataset metadata minimal: no camera transform or geometry record is written because the EXR already contains `P`, `Nb`, `V`, and `C.A`.
- Smoke-tested camera discovery, JSON copying, and folder skipping without launching Karma; a live pilot remains pending.

### Explicit DEV/PROD library selection

- Replaced the single material-library configuration path with named DEV and PROD paths mapped to `neuron_library_dev.json` and `neuron_library_prod.json`.
- Added the user-authored **Material Library JSON** combo to Datagen and Datarender and regenerated both PySide UI bindings.
- Made DEV the safe default: Datagen builds its eight-material stress subset, while PROD builds the full 1,806-material library; reload and prompt generation use the selected file.
- Made material application and dataset rendering set `neuromat.dataset_path` to the selected JSON before applying or rendering materials.
- Smoke-tested both generator counts and Datarender's selected-path, snapshot-copy, render, and restart-skip behavior without launching Karma.

### First live Datarender pilot

- Inspected the first eight-material DEV dataset rendered through Datarender at 512 × 512 under low-quality settings.
- Verified eight expected `cam_001` material folders, eight readable finite multipart EXRs, the DEV JSON snapshot, and the required `C`, `P`, `V`, and `Nb` channels.
- Confirmed consistent framing and visibly distinct material responses; glass remains too noisy for final-quality approval at the test settings.
- Recorded that PROD must use a clean output directory after a low-resolution pilot because the simple folder-existence resume rule would otherwise retain and mix the eight test renders.
- Added explicit `Dataset Render Started...` and successful `Dataset Render Complete!` console messages around the render loop.
- Added a native Houdini dataset-progress dialog showing overall and current-item progress. Cancel/Escape interrupts before the next item and reports that the last render folder may require manual cleanup.
- Replaced the resetting per-image progress with one whole-dataset bar, initialized from existing material folders so resumed renders begin at their actual completed fraction.
- Disabled verbose `hou.RopNode.render()` output, removing the redundant timestamped `usdrender_rop1 frame 1` console lines while retaining explicit material `RENDER` messages.
- Corrected nested Houdini progress handling: the USD Render ROP retains its indeterminate current-image bar while a second, persistent **Dataset Render** bar reports the completed/total count and resume fraction.
- Replaced the outer native interrupt operation after live testing showed that the USD Render ROP hides it. A separate modeless Qt window titled **Render Dataset Progress** now displays stable overall percentage, completed/total, current material, and a **Cancel Render** button while Houdini retains its own current-image Interrupt window.
- Removed the custom **Render Dataset Progress** window after live testing showed a blank, unpainted dialog while the blocking USD Render ROP owned Houdini's UI thread. Restored Houdini's reliable native **Interrupt** window while retaining sequential rendering, folder pre-scan/resume, and quiet console output.
- Added one non-overwriting `{geometry_id}/{camera_id}/camera.json` per selected dataset camera. Datarender now records the cooked USD world position/forward target/up, millimeter lens and aperture, and cooked Render Settings resolution for Three.js reference-camera matching; documented the remaining geometry and `P`/`N`/`V` convention requirements in the application specification.
- Added a Camera LOP fallback for camera JSON creation after the live Render Settings node returned no cooked USD stage. The fallback reads the Datarender-created look-at camera and Render Settings parameters without changing the JSON contract or overwriting existing files.
- Renamed each dataset camera record from the generic `camera.json` to `{camera_id}.json`, for example `{geometry_id}/cam_001/cam_001.json`, so the filename remains identifiable when copied elsewhere.

## 2026-09-04

### Web asset layout

- Renamed `public/models/` to `public/geometry/` so browser mesh assets are not confused with trained AI models, and updated the Material Hero loader path.
- Reserved `public/cameras/material_hero/{camera_id}.json` for unchanged copies of selected dataset camera records; no placeholder camera file was added before the final dataset camera exists.
