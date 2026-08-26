# Material Hero model specification

Status: **Planned; input/output contract accepted, architecture open**

Last reviewed: 2026-08-26

## Objective

Train a small, understandable model that directly generates the rendered RGB appearance of one fixed Sculpted Rubber Toy from a material description and camera/surface context.

Material Hero is a constrained text-to-image problem. It is not a general text-to-image model, text-to-3D model, material-map generator, or relighting system.

## Functional contract

For visible points on the fixed hero surface, the intended relationship is:

```text
RGB = F(P, N, V, text)
```

Where:

- `P` is a position on the fixed hero surface in a documented coordinate space.
- `N` is the corresponding surface normal.
- `V` is view direction derived from the active camera.
- `text` describes material appearance.
- `RGB` is the final rendered appearance under the fixed Houdini studio setup.

The exact network may operate per surface sample, per ray, or on rasterized image buffers. That implementation choice remains open, but the external behavior does not change.

## Fixed and variable factors

| Factor | V1 behavior |
| --- | --- |
| Geometry | Fixed Sculpted Rubber Toy |
| Geometry transform and scale | Fixed |
| Material appearance | Controlled by text |
| Camera | Variable and supplied as context |
| Lighting/HDRI | Fixed and baked into learned appearance |
| Exposure and color management | Fixed and recorded |
| Background | Fixed or composited using geometry alpha |
| Random generation seed | Deferred; deterministic v1 |

## Inputs

### Required logical inputs

- Material prompt or its encoded representation
- Camera intrinsics and pose, or equivalent view rays
- Surface position
- Surface normal
- Foreground coverage/silhouette

The implementation may derive view direction and surface buffers from the fixed proxy geometry instead of loading them from disk at inference time.

### Prompt inputs

The first model uses a controlled material vocabulary derived from:

- base material;
- optional color;
- finish;
- condition.

Training records preserve both a compact prompt such as `gold brushed dirty` and a longer deterministic semantic label. The training policy may use one or both, but the application must support compact prompts from the accepted vocabulary.

## Output

- Final rendered RGB image or foreground RGB samples that assemble into that image
- Display alpha comes from the fixed geometry coverage unless an experiment explicitly predicts it

PBR parameters, BaseColor maps, Roughness maps, normal maps, shader graphs, density, and geometry are not required model outputs.

## Recommended first baseline

Begin with the smallest model that can prove the data path:

1. Rasterize or load `P`, `N`, view direction, and alpha for foreground pixels.
2. Encode controlled material tokens with a small learned embedding.
3. Use positional/Fourier features only where a simple MLP cannot reproduce spatial detail.
4. Predict linear foreground RGB.
5. Composite with the fixed alpha/background for display.

This baseline is preferred over starting with a diffusion model because it is easier to implement, debug, overfit intentionally, and relate back to the known geometry. A diffusion or image-space refinement stage can be evaluated later if the baseline cannot represent the required detail.

## Training sequence

### Smoke test

- One material
- One or a few cameras
- Confirm image loading, coordinate conventions, masking, loss, checkpointing, and reconstruction

### Small-subset overfit

- Several visually distinct materials
- Multiple cameras per material
- Confirm text conditioning changes appearance and camera conditioning changes view

### Generalization experiment

- Full approved dataset or a representative subset
- Split by material ID
- Hold out exact material combinations while retaining their individual concepts elsewhere in training

## Dataset split rules

- Every camera view of a material belongs to the same split.
- Do not randomly split frames across train and validation.
- Keep a standard validation set for unseen material IDs.
- Keep a compositional test set for combinations such as a base, finish, and condition not seen together during training.
- Record split assignment in the dataset manifest so experiments use the same partition.

## Loss and color rules

- Train against the documented linear beauty data unless an experiment explicitly evaluates another representation.
- Apply loss only where coverage is valid, or explicitly include a separately weighted background objective.
- Do not hide watermarks, mislabeled pixels, or invalid AOV regions with training-time hacks; correct the dataset.
- Establish a simple prompt-agnostic baseline to measure whether text conditioning adds value.

Exact losses, feature encodings, model width, and optimizer settings remain experiment choices rather than dataset requirements.

## Evaluation

Minimum evaluation should include:

- Reconstruction error on seen material/view combinations
- Novel-view performance for held-out cameras of seen materials during development experiments
- Material-level validation on entirely held-out material IDs
- Compositional prompt evaluation
- Silhouette stability
- Cross-view identity and spatial-detail consistency
- Attribute checks for base, color, finish, and condition

Qualitative grids should hold camera constant while changing prompt, and hold prompt constant while changing camera.

## Known challenges

- Transparent and refractive materials may require more than a purely local surface function.
- Sharp view-dependent metal reflections require accurate view conditioning.
- One deterministic procedural example per prompt does not teach multiple valid samples for the same prompt.
- Long semantic labels and compact UI prompts must share a compatible text representation.
- A model can memorize material IDs without learning compositional semantics; held-out combinations are required to detect this.

## Acceptance criteria for the first trained model

- It intentionally overfits a tiny dataset, proving the training path is correct.
- Different supported prompts produce visibly appropriate appearances.
- The same prompt remains spatially coherent across camera views.
- The hero silhouette and identity remain fixed.
- Results outperform prompt-agnostic and nearest-material baselines.
- A saved checkpoint can reproduce documented validation renders from a clean process.

## Non-goals

- Arbitrary geometry or object generation
- Reusable PBR material export
- Free-form unsupported natural-language understanding
- User-controlled lighting or environment changes
- Multiple stochastic variations of one prompt
- Multiple neural assets or scene composition
