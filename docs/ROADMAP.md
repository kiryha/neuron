# Project roadmap

The roadmap is gate-based rather than date-based. Do not start a later gate merely because earlier work is tedious; finish the minimum acceptance criteria and move on.

## Phase 1A — Lock the Material Hero HDA

Status: **In progress**

Goal: one deterministic JSON-driven material asset that renders every supported library record correctly enough for training.

Deliverables:

- Correct direct bump routing for none, stochastic, directional, and cellular — implemented and visually approved
- Standard Surface bindings for subsurface, subsurface color, and thin-wall — implemented, stress validation pending
- Verified material-ID-driven HDA cook path suitable for interactive and batch operation
- Tuned and approved stochastic, directional, and cellular bump — verified in fixed-camera stress renders
- Full-library confirmation that every generated bump mode maps to the HDA — verified
- Variation, dirt, and wear validation
- Required shader parameters connected or explicitly classified; `k` and metallic flake are metadata-only, while transmission-scatter remains pending
- Stress-set look-dev renders
- Frozen HDA version and recoverable scene

Exit gate:

- All eight stress materials pass visual QA.
- No material ID silently falls through an unconnected branch.
- Selecting a material ID cooks the matching JSON record and updates the intended HDA fields.
- Reapplying a material produces the same graph inputs and pixels.

## Phase 1B — Freeze the dataset contract

Status: **In progress**

Goal: define exactly what the fixed-view v0 training release contains and prove it with a small material pilot.

Deliverables:

- One fixed 28 mm training camera preserved in the versioned HIP scene
- 1024 × 1024 Beauty RGBA, world `P`, smooth unbumped world `Nb`, and world `V`; `C.A` is material-independent Coverage
- Depth of field disabled
- Debug AOVs excluded from dataset output
- Fixed linear color and OCIO setup in the versioned HIP scene
- Minimal `{geometry_id}/{camera_id}/{material_id}/render.exr` naming contract
- Unchanged `neuron_library_prod.json` snapshot beside the renders
- Shared Houdini/Three.js `P`/`N`/`V`/Coverage convention, with Houdini Coverage read from `C.A`
- Render/storage/time estimate

Exit gate:

- A pilot covering all stress materials at the fixed camera loads without manual repair.
- Geometry AOVs, beauty, labels, and material IDs remain aligned.
- Re-rendering the pilot is deterministic.
- Outputs contain no Houdini watermark.

## Phase 1C — Render the dataset

Status: **Planned**

Goal: generate the approved dataset without changing its material, lighting, camera, color, or output contract mid-run.

Deliverables:

- Sequential `datagen/datarender.py` fixed-camera renderer — planned for staged implementation
- Folder-existence skip behavior and manual folder-deletion rerender workflow — accepted design, not implemented
- Complete material folders and copied material-library snapshot
- Manual count and representative visual checks

Exit gate:

- The number of rendered material folders matches the production JSON.
- Representative outputs are manually approved.
- The training loader can scan folders and join each material ID to the copied JSON.

## Phase 2A — Establish a learning baseline

Status: **Planned**

Goal: prove that text and fixed-surface context can predict the hero’s RGB appearance.

Start with the smallest understandable model and a small subset. Do not begin with a large diffusion system.

Deliverables:

- Dataset loader
- Controlled text tokenizer/encoder baseline
- Fixed-camera and surface-context preparation
- Direct RGB predictor
- Checkpoint and experiment configuration
- Overfit-one-material and overfit-small-subset tests

Exit gate:

- The model can intentionally overfit a tiny sample.
- It can reconstruct the fixed view for held-out materials better than prompt-agnostic and nearest-material baselines.

## Phase 2B — Three.js out-of-distribution laboratory

Status: **Planned; local normal-viewer slice accepted for early implementation**

Goal: run the v0 model from the exported hero GLB at the training-camera reference pose, then observe what the fixed-view model does under unsupported camera and supplied-mesh changes.

The first slice may be implemented before model training: a local-only, orbitable world-space normal-pass viewer with a reset to a stable app-authored reference camera. This validates mesh loading and the first geometry-buffer path without adding prompt, inference, backend, or deployment work.

Deliverables:

- Local 1024 x 1024 world-space normal-pass viewer using `public/models/material_hero/sculpted-rubber-toy.glb`
- Orbit controls and reset to the app-authored reference camera and target
- Three.js float-buffer rendering for `P`, smooth unbumped `N`, and Coverage plus deterministic `V` derivation
- Load `public/models/material_hero/sculpted-rubber-toy.glb` as the single v0 web geometry
- Prompt inference and generated-RGB display
- Orbit, zoom, and alternate-mesh controls marked out of distribution
- Repeatable evaluation scenes, prompts, captures, and measurements

Exit gate:

- The exported hero mesh produces the required geometry buffers and an inference result at the training-camera reference pose.
- Unsupported-view and unsupported-geometry failures can be reproduced and compared with later checkpoints.

## Phase 2C — Multi-view extension

Status: **Planned**

Goal: add controlled camera diversity for the same hero and measure whether orbit behavior improves.

Deliverables:

- Measured camera-dome pilot and accepted camera count
- Versioned multi-view dataset using the same material split
- Retrained checkpoint with otherwise comparable experiment configuration
- Seen, interpolated, and held-out-camera evaluation

Exit gate:

- Novel-view behavior improves measurably over v0 on the standardized app tests.
- Exact-view material quality does not regress without explanation.

## Phase 2D — Multi-geometry extension

Status: **Planned**

Goal: add geometry diversity and measure whether switching supplied meshes improves.

Deliverables:

- Accepted geometry suite and normalization convention
- Versioned multi-view, multi-geometry dataset
- Seen- and held-out-geometry splits
- Retrained checkpoint and comparison against v0 and the multi-view checkpoint

Exit gate:

- Geometry-switching behavior improves measurably on the standardized test meshes.
- Remaining limitations are documented rather than presented as universal material rendering.

## Phase 3 — Material Hero application

Status: **Scaffold only**

Goal: package the experimental material-rendering laboratory into a clear Neuron web application and deploy the selected checkpoints.

Deliverables:

- Model-loading and render API
- Prompt validation
- Three.js geometry-buffer-to-inference integration
- Dataset/model version selection or comparison
- Proxy/neural display behavior
- Error and progress feedback
- Docker/Hugging Face deployment

Exit gate:

- A clean checkout can load the published model and serve the demo.
- A user can render supported prompts, identify the loaded training scope, and distinguish the training-camera reference pose from out-of-distribution requests.

## Later research — persistent neural assets

Status: **Vision only**

Material Hero may become the first packaged `.neuron` asset. Later work can investigate persistent objects, environments, versioned edits, scene composition, lighting interaction, deformation, and animation.

Keep this direction in the project architecture, but do not design or implement the general engine until Material Hero has demonstrated persistent model loading, prompt conditioning, and camera-consistent rendering.
