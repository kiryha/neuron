# Material Hero v0 training report

Status: **Verified final training checkpoint; fixed-view web integration verified**

Date: 2026-09-16

## Result

The selected Material Hero v0 model is the structured-token, coordinate-conditioned
MLP trained for ten complete shuffled passes over 1,448 training materials. The
stable package is:

```text
train/outputs/material-hero-v0-final/
```

The checkpoint is `material_hero_v0.pt`, step 18,100, with SHA-256:

```text
d2a1c9e9640e360444efd591bcee19d1e95b890780ad313e6cb60648d3065934
```

The package also contains the exact configuration, metadata, training history,
full evaluation reports, baseline reports, qualitative grid, and manifest.

## Dataset gate

- Dataset: `material_hero_v0`, Sculpted Rubber Toy, `cam_001`
- Expected and present materials: 1,806
- Full multipart EXRs decoded: 1,806
- Validation failures after rerender: 0
- Required 1024 × 1024 parts: Beauty `C`, world `P`, world `V`, smooth world `Nb`
- All required values finite with the expected channel layout

Frozen material-level split counts:

| Split | Materials | Purpose |
| --- | ---: | --- |
| Train | 1,448 | Optimization |
| Validation | 186 | Unseen material IDs |
| Compositional test | 172 | Held-out `(base, finish, condition)` groups |

## Model and training

- Inputs: Fourier-encoded normalized `P`, unit `Nb`, unit `V`, and learned base/color/finish/condition embeddings
- Output: deterministic linear foreground RGB
- Architecture: six Fourier bands, 16-dimensional embeddings, width 256, six residual blocks
- Parameters: 822,723
- Loss: coverage-weighted foreground L1
- Optimizer: AdamW, learning rate `1e-3`, weight decay `1e-6`
- CUDA automatic mixed precision on the RTX A1000 6GB Laptop GPU
- Schedule: ten shuffled epochs, four materials per loaded group, five random-pixel updates per group, 4,096 visible pixels per material and update
- Total optimization steps: 18,100
- Checkpoint selection: lowest mean full-frame L1 over eight fixed held-out validation materials

## Quantitative evaluation

All neural results below were produced by loading the saved checkpoint in a new
process and rendering every material in the named split.

| Method | Split | Mean L1 | Median L1 | P90 L1 |
| --- | --- | ---: | ---: | ---: |
| Conditioned MLP | Validation | **0.05868** | 0.04395 | **0.12230** |
| Nearest training material | Validation | 0.06957 | **0.03970** | 0.17182 |
| Prompt-agnostic MLP | Validation | 0.16816 | 0.16577 | 0.26321 |
| Conditioned MLP | Compositional test | **0.05505** | 0.04158 | **0.11076** |
| Nearest training material | Compositional test | 0.06172 | **0.03851** | 0.15226 |
| Prompt-agnostic MLP | Compositional test | 0.16177 | 0.15455 | 0.27317 |

The conditioned model reduces mean error by about 15.7% versus nearest-material
lookup on validation and 10.8% on the compositional test. Its largest advantage
is in high-error cases: P90 improves by about 28.8% and 27.3%, respectively.
Against the prompt-agnostic model, conditioning reduces mean error by roughly
two-thirds. This verifies that material tokens materially affect the output.

The nearest-material baseline uses deterministic weighted categorical distance:
base `4`, color `2`, finish `1`, condition `1`. It has a slightly lower median,
but materially worse mean and tail error because it cannot synthesize held-out
attribute combinations.

## Qualitative result and limitations

The package's `qualitative.png` compares target on the left with prediction on
the right for twelve diverse held-out materials. Color, broad reflectance,
silhouette-aligned variation, and many material-family differences transfer well.
Fine high-frequency reflections and refraction are smoother than the target.
Polished diamond and satin glass are the clearest hard cases.

This checkpoint is deliberately limited to:

- one fixed Sculpted Rubber Toy;
- one fixed `cam_001` view;
- fixed lighting, exposure, and background contract;
- controlled base/color/finish/condition tokens rather than free-form language;
- deterministic output rather than stochastic generation.

These are v0 scope constraints, not claims of general camera, geometry, relighting,
or unrestricted text-to-image support.

## Verification

- The complete dataset passed the full-read validator after the six rerenders.
- The training run completed all 18,100 planned steps.
- Full validation and compositional-test evaluation completed in clean processes.
- The packaged checkpoint passed strict state-dictionary reconstruction.
- The packaged copy was loaded again in a separate process and reproduced
  `car_paint_yellow_polished_clean` full-frame L1 `0.083207`.
- Seven unit tests pass for vocabularies, splits, epoch scheduling, nearest-material
  selection, model gradients, prompt-agnostic construction, and masked loss.

The packaged checkpoint is integrated through FastAPI and the Three.js viewer. A verified browser run rasterized the fixed hero at `cam_001`, submitted raw `P`, `N`, `V`, and Coverage, and displayed a `gold polished clean` RGBA prediction. Runtime preserves the packaged position normalization, renormalizes `N` and `V`, predicts linear RGB, and uses Coverage as output alpha.
