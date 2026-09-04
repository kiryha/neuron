# Project decisions

This file records accepted choices that should survive individual chats. Implementation detail belongs in specifications; session history belongs in the changelog.

| ID | Status | Confirmed | Decision | Consequence |
| --- | --- | --- | --- | --- |
| D-001 | Accepted | 2026-08-26 | Material Hero is the current product milestone. | General neural assets and scenes must not distract from finishing data, training, and the first app. |
| D-002 | Accepted | 2026-08-26 | The model directly generates rendered RGB appearance. | PBR parameters, shader graphs, and texture maps are not model outputs. |
| D-003 | Superseded | 2026-08-26 | Material Hero v1 uses one fixed Sculpted Rubber Toy geometry. | Superseded by D-016; it remains true for the first training dataset, while later experiments deliberately test additional views and supplied meshes. |
| D-004 | Accepted | 2026-08-26 | Camera and fixed-surface context are part of the learning problem. | Store the required model context directly in each EXR as `P`, unbumped `Nb`, `V`, and Beauty alpha Coverage. The per-camera JSON accepted in D-026 is for recreating the training view in the web app, not an additional model input. |
| D-005 | Accepted | 2026-08-26 | The first prompt-to-appearance mapping is deterministic. | Multiple samples from one prompt and a generative noise seed are deferred. |
| D-006 | Accepted | 2026-08-26 | Lighting, exposure, color management, geometry transform, and background remain controlled for v1. | The first model learns appearance under one studio setup and is not a relighting model. |
| D-007 | Accepted | 2026-08-26 | UV projection is sufficient for the fixed hero phase. | Do not restart the HDA around triplanar projection unless a demonstrated artifact threatens training. |
| D-008 | Accepted | 2026-08-26 | One master `neuromat` HDA is driven by deterministic JSON records. | Material behavior must remain traceable to material ID and library snapshot. |
| D-009 | Accepted | 2026-08-26 | Dataset splits are made by material ID, not by individual rendered frame. | Every camera view of one material belongs to the same split; compositional holdouts test unseen combinations. |
| D-010 | Accepted | 2026-08-26 | Historical chats and briefs are sources, not specifications. | Canonical truth lives in inspected artifacts, this decision log, and `docs/specs/`. |
| D-011 | Accepted | 2026-08-26 | Watermarked Houdini Apprentice renders are not final training data. | Apprentice can be used for development, but a non-watermarked final-render path is a Phase 1 gate. |
| D-012 | Accepted | 2026-08-26 | Persistent neural assets remain the long-term Neuron direction. | Material Hero should teach reusable packaging and inference concepts, but the general engine is a later phase. |
| D-013 | Accepted | 2026-08-26 | Future scene composition should retain USD-like references, transforms, versions, and overrides. | Neural representations may replace traditional payloads; a full USD replacement is not part of Material Hero. |
| D-014 | Accepted | 2026-08-28 | Remove the unsupported `cracked` bump type and map asphalt to `stochastic` at bump scale `0.02`. | Houdini needs only the existing none, stochastic, directional, and cellular modes; asphalt must be judged during stochastic bump validation. |
| D-015 | Accepted | 2026-08-28 | Treat `k` and `metallic_flake` as unused metadata for Material Hero v1. | Keep their values in JSON for provenance and possible future shader work, but they have no render effect and require no `neuromat` implementation. |
| D-016 | Accepted | 2026-08-31 | Develop geometry generalization as a staged experiment: fixed camera and one hero first; Three.js out-of-distribution orbit, zoom, and mesh tests; then a multi-view dataset; then a multi-view, multi-geometry dataset. | Every stage keeps prompt-to-RGB and `P`/`N`/`V`/Coverage conditioning, measures the failures of the previous dataset, and does not claim unsupported views or meshes as working product features. |
| D-017 | Accepted | 2026-09-02 | Store versioned datasets under `E:\Projects\neuron_data\datasets`. | Each version is a simple folder containing the material-library snapshot and geometry/camera/material render hierarchy. |
| D-018 | Superseded | 2026-09-02 | Use 512 × 512 as the dataset-v0 pilot resolution with the existing 28 mm Houdini camera. | Superseded by D-019 before rendering began. |
| D-019 | Accepted | 2026-09-02 | Render dataset v0 at 1024 × 1024 with DOF disabled, storing Beauty RGBA, world `P`, smooth unbumped world `Nb`, and world `V` in each multilayer EXR. | `C.A` supplies Coverage per D-022; drop `Pz` and separate variation, dirt, wear, bump, BaseColor, Roughness, and other debug AOVs; repeated geometry buffers are accepted for simplicity. |
| D-020 | Accepted | 2026-09-02 | Use the copied `neuron_library_prod.json` plus `{geometry_id}/{camera_id}/{material_id}/render.exr` folders as the complete training-data index. | No hashes, renamed JSON, dataset/entity records, manifest, schema record, progress log, or validation report are required for v0. The small camera calibration record accepted in D-026 does not replace this index. |
| D-021 | Accepted | 2026-09-02 | Implement render automation as a sequential `datagen/datarender.py` script rather than TOPs/PDG. | Explicit geometry and camera lists preserve future extension; an existing material folder is skipped, and manual folder deletion requests a rerender. |
| D-022 | Accepted | 2026-09-03 | Use Beauty alpha (`C.A`) as material-independent Coverage for Material Hero v0. | The material library drives transmission but not opacity, so opaque and glass materials retain the same geometry alpha; no separate Coverage RenderVar or EXR subimage is required. |
| D-023 | Superseded | 2026-09-03 | Use the single reduced hero export at `public/models/material_hero/sculpted-rubber-toy.glb` as the web application's Material Hero geometry. | Superseded by D-027, which moves browser geometry out of the ambiguous `models` directory. The remaining simplicity constraints still apply. |
| D-024 | Accepted | 2026-09-03 | Keep Neuron implementations limited to the simplest core functionality required for hands-on generative-AI and Houdini data-generation learning. | Do not add production-style metadata, hashes, manifests, validation frameworks, abstraction layers, or reliability systems unless a demonstrated project need requires them. |
| D-025 | Superseded | 2026-09-03 | Build the next application slice as a local-only Three.js viewer of the hero's smooth world-space normal pass, with an orbitable camera and a reset to a stable app-authored reference view. | The normal viewer, orbit control, reset control, and inactive prompt field remain accepted. D-026 and the verified `cam_001.json` integration supersede only the temporary app-authored reference camera. |
| D-026 | Accepted | 2026-09-04 | Store one `{camera_id}.json` under each `{geometry_id}/{camera_id}` dataset folder for recreating the rendered camera in Three.js. | Datarender creates the file from the cooked USD camera and Render Settings resolution when available, otherwise from the project's simple look-at Camera LOP and Render Settings parameters. It never replaces an existing file and stores only camera ID, world position/target/up, focal length, horizontal aperture, and resolution. |
| D-027 | Accepted | 2026-09-04 | Store browser geometry under `public/geometry/` and copied dataset camera records under `public/cameras/material_hero/{camera_id}.json`. | The Material Hero GLB moves to `public/geometry/material_hero/sculpted-rubber-toy.glb`, avoiding confusion with AI model artifacts. Camera JSON contents remain unchanged when copied from the selected dataset camera folder. |

## Open decisions

| ID | Question | Needed by |
| --- | --- | --- |
| O-001 | What exact neural architecture is the first baseline: per-surface MLP, image network, or staged comparison? | Before Phase 2A implementation |
| O-002 | What text representation is used first: controlled learned tokens, pretrained encoder, or both? | Before Phase 2A implementation |
| O-004 | What are the multi-view render resolution, camera count, and storage budget? | Before the multi-view dataset extension |
| O-007 | Which additional geometries and position-normalization convention are used for multi-geometry training? | Before the multi-geometry dataset extension |

## Adding a decision

Add a row only after the user accepts a choice or implementation makes the choice explicit and it has been verified. Include the date and update any affected specifications and roadmap gates.
