# Project roadmap

The roadmap is gate-based rather than date-based. Do not start a later gate merely because earlier work is tedious; finish the minimum acceptance criteria and move on.

## Phase 1A — Lock the Material Hero HDA

Status: **In progress**

Goal: one deterministic JSON-driven material asset that renders every supported library record correctly enough for training.

Deliverables:

- Correct direct bump routing for none, stochastic, directional, and cellular — implemented, visual validation pending
- Standard Surface bindings for subsurface, subsurface color, and thin-wall — implemented, stress validation pending
- Verified material-ID-driven HDA cook path suitable for interactive and batch operation
- Tuned and approved stochastic, directional, and cellular bump
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

Status: **Planned**

Goal: define exactly what one training frame contains and prove it with a small multi-camera pilot.

Deliverables:

- Camera distribution and intrinsics
- Beauty, alpha, `P`, `Pz`, and `N` definitions
- Optional auxiliary/debug AOV definitions
- Linear color and OCIO metadata
- Dataset naming and logical manifest schema
- Material-library snapshot and label validation
- Dataset validator
- Render/storage/time estimate

Exit gate:

- A pilot covering all stress materials and several cameras loads without manual repair.
- All views of a material can be grouped into one dataset split.
- Re-rendering the pilot is deterministic.
- Outputs contain no Houdini watermark.

## Phase 1C — Render the dataset

Status: **Planned**

Goal: generate the approved dataset without changing its material, lighting, camera, color, or metadata contract mid-run.

Deliverables:

- Automated material × camera render graph
- Resume/retry behavior
- Complete manifests and material snapshot
- Validation report and checksums
- Train/validation/test assignment by material ID

Exit gate:

- Every manifest row resolves to valid files and metadata.
- No material or camera IDs are missing or duplicated.
- Train, validation, and test sets have no cross-view material leakage.

## Phase 2A — Establish a learning baseline

Status: **Planned**

Goal: prove that text and fixed-surface context can predict the hero’s RGB appearance.

Start with the smallest understandable model and a small subset. Do not begin with a large diffusion system.

Deliverables:

- Dataset loader
- Controlled text tokenizer/encoder baseline
- Camera and surface-context preparation
- Direct RGB predictor
- Checkpoint and experiment configuration
- Overfit-one-material and overfit-small-subset tests

Exit gate:

- The model can intentionally overfit a tiny sample.
- It can reconstruct held-out views of seen materials better than a prompt-agnostic baseline.

## Phase 2B — Material Hero training

Status: **Planned**

Goal: generate stable views of the fixed hero from material prompts, including held-out prompt combinations.

Deliverables:

- Full training and evaluation loop
- Material-level data splits
- Compositional holdout evaluation
- Multi-view consistency evaluation
- Reproducible model artifact and prompt vocabulary

Exit gate:

- Prompt changes produce the intended material attributes.
- The Sculpted Rubber Toy identity and silhouette remain stable across views.
- Held-out material combinations perform meaningfully above baseline.

## Phase 3 — Material Hero application

Status: **Scaffold only**

Goal: enter a prompt, control the camera, and display the generated Material Hero in the Neuron web application.

Deliverables:

- Model-loading and render API
- Prompt validation
- Camera-to-inference integration
- Proxy/neural display behavior
- Error and progress feedback
- Docker/Hugging Face deployment

Exit gate:

- A clean checkout can load the published model and serve the demo.
- A user can render supported prompts from multiple camera views.

## Later research — persistent neural assets

Status: **Vision only**

Material Hero may become the first packaged `.neuron` asset. Later work can investigate persistent objects, environments, versioned edits, scene composition, lighting interaction, deformation, and animation.

Keep this direction in the project architecture, but do not design or implement the general engine until Material Hero has demonstrated persistent model loading, prompt conditioning, and camera-consistent rendering.
