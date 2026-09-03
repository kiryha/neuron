# Material Hero model specification

Status: **Planned; staged input/output experiment accepted, architecture open**

Last reviewed: 2026-09-02

## Objective

Train a small, understandable model that directly generates rendered RGB from a material description and rasterized surface context. The first release uses one Sculpted Rubber Toy and one fixed camera; later releases add camera and geometry diversity to measure how generalization changes.

Material Hero is a constrained text-to-image problem. It is not a general text-to-image model, text-to-3D model, material-map generator, or relighting system.

## Functional contract

For visible surface points, the intended relationship is:

```text
RGB = F(P, N, V, text)
```

Where:

- `P` is a visible surface position in a documented coordinate space.
- `N` is the corresponding surface normal.
- `V` is view direction derived from the active camera.
- `text` describes material appearance.
- `RGB` is the final rendered appearance under the fixed Houdini studio setup.

The exact network may operate per surface sample or on rasterized image buffers. The first implementation is not required to learn geometry, density, or ray-marched occupancy.

## Fixed and variable factors

| Factor | First training release |
| --- | --- |
| Geometry | Fixed Sculpted Rubber Toy |
| Geometry transform and scale | Fixed |
| Material appearance | Controlled by text |
| Camera | One fixed training camera; runtime changes are deliberate out-of-distribution tests |
| Lighting/HDRI | Fixed and baked into learned appearance |
| Exposure and color management | Fixed and recorded |
| Background | Fixed or composited using geometry Coverage |
| Random generation seed | Deferred; deterministic first release |

## Inputs

### Required logical inputs

- Material prompt or its encoded representation
- World-space surface position `P`
- Smooth, unbumped world-space surface normal `N`
- World-space view direction `V`
- Material-independent foreground Coverage

Houdini provides the training buffers. The application is planned to rasterize corresponding buffers from supplied Three.js meshes and cameras. At the exact training geometry and camera, those buffers must be calibrated against Houdini before model behavior is judged. Orbit, zoom, and alternate meshes remain out of distribution until represented in a later training release.

### Prompt inputs

The first model uses a controlled material vocabulary derived from:

- base material;
- optional color;
- finish;
- condition.

Training records preserve both a compact prompt such as `gold brushed dirty` and a longer deterministic semantic label. The training policy may use one or both, but the application must support compact prompts from the accepted vocabulary.

## Output

- Final rendered RGB image or foreground RGB samples that assemble into that image
- Display alpha is derived from the supplied geometry Coverage unless an experiment explicitly predicts it

PBR parameters, BaseColor maps, Roughness maps, normal maps, shader graphs, density, and geometry are not required model outputs.

## Recommended first baseline

Begin with the smallest model that can prove the data path:

1. Load Beauty, `P`, smooth unbumped `N`, `V`, and Coverage from each 1024 × 1024 material EXR.
2. Encode controlled material tokens with a small learned embedding.
3. Use positional/Fourier features only where a simple MLP cannot reproduce spatial detail.
4. Predict linear foreground RGB.
5. Composite with Coverage/background for display.
6. Reproduce the fixed training buffers in Three.js and compare inference against the Houdini-buffer baseline.

This baseline is preferred over starting with a diffusion model because it is easier to implement, debug, overfit intentionally, and relate back to the known geometry. A diffusion or image-space refinement stage can be evaluated later if the baseline cannot represent the required detail.

## Staged training sequence

### Dataset/model v0 — fixed-view baseline

- One Sculpted Rubber Toy, one camera, and fixed lighting
- One 1024 × 1024 multilayer EXR per material containing Beauty plus aligned `P`, `N`, `V`, and Coverage
- Smoke-test one material, overfit a small material subset, then train the approved material library
- Confirm prompt conditioning and exact-view reconstruction before evaluating unsupported inputs

### Runtime v0 — out-of-distribution observation

- Recreate the training geometry and camera in Three.js as the calibration case
- Orbit and zoom the hero without claiming novel-view support
- Supply several additional meshes and observe failure or partial transfer without claiming geometry support
- Save comparable outputs for the same prompts, cameras, and meshes

### Dataset/model v1 — multi-view extension

- Render the same hero under a controlled camera dome
- Keep model architecture and evaluation prompts as stable as practical
- Retrain and measure improvement on orbit, interpolation, and held-out camera tests

### Dataset/model v2 — multi-geometry extension

- Render several normalized geometries from multiple cameras
- Define geometry-aware splits and at least one held-out geometry
- Retrain and measure improvement when switching supplied Three.js meshes

### Controlled comparison rules

- Preserve the same material splits, evaluation prompts, calibration camera, and named test meshes across versions.
- Keep architecture, training budget, resolution, and random seeds unchanged where practical; record every intentional difference.
- Compare v0, multi-view, and multi-geometry checkpoints on the same exact-view, orbit/zoom, and geometry-switch test grid.
- Archive model, dataset, application, and geometry-buffer versions with every result.

## Dataset split rules

- Every camera view of a material belongs to the same split.
- Do not randomly split frames across train and validation.
- Keep a standard validation set for unseen material IDs.
- Keep a compositional test set for combinations such as a base, finish, and condition not seen together during training.
- Store the split assignment with the training experiment rather than in the Houdini render dataset.

## Loss and color rules

- Train against the documented linear beauty data unless an experiment explicitly evaluates another representation.
- Apply loss only where coverage is valid, or explicitly include a separately weighted background objective.
- Do not hide watermarks, mislabeled pixels, or invalid AOV regions with training-time hacks; correct the dataset.
- Establish a simple prompt-agnostic baseline to measure whether text conditioning adds value.

Exact losses, feature encodings, model width, and optimizer settings remain experiment choices rather than dataset requirements.

## Evaluation

Minimum evaluation should include:

- Reconstruction error at the exact v0 training geometry and camera
- Houdini-buffer versus Three.js-buffer output at the matched training pose
- Unsupported orbit, zoom, and alternate-geometry results for v0, clearly labeled as out of distribution
- Novel-view performance after multi-view training
- Seen- and held-out-geometry performance after multi-geometry training
- Material-level validation on entirely held-out material IDs
- Compositional prompt evaluation
- Silhouette stability
- Cross-view identity and spatial-detail consistency
- Attribute checks for base, color, finish, and condition

Qualitative grids should hold camera constant while changing prompt, and hold prompt constant while changing camera.

## Known challenges

- Transparent and refractive materials may require more than a purely local surface function.
- Sharp view-dependent metal reflections require accurate view conditioning.
- Houdini and Three.js differences in geometry, transforms, projection, normals, sampling, or edge coverage can masquerade as model-generalization failures.
- One deterministic procedural example per prompt does not teach multiple valid samples for the same prompt.
- Long semantic labels and compact UI prompts must share a compatible text representation.
- A model can memorize material IDs without learning compositional semantics; held-out combinations are required to detect this.

## Acceptance criteria for the first trained model

- It intentionally overfits a tiny dataset, proving the training path is correct.
- Different supported prompts produce visibly appropriate appearances.
- The exact training geometry and camera reproduce documented validation renders using calibrated Three.js buffers.
- Orbit, zoom, and alternate-mesh outputs can be generated and recorded, but are not required to be correct for v0.
- Results outperform prompt-agnostic and nearest-material baselines.
- A saved checkpoint can reproduce documented validation renders from a clean process.

## Non-goals

- Generated geometry or object creation
- Reliable arbitrary-view or arbitrary-geometry rendering in v0
- Reusable PBR material export
- Free-form unsupported natural-language understanding
- User-controlled lighting or environment changes
- Multiple stochastic variations of one prompt
- Multiple neural assets or scene composition
