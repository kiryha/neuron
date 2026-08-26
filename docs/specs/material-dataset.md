# Material dataset specification

Status: **Partially implemented; render and manifest contract not frozen**

Last reviewed: 2026-08-26

## Purpose

The dataset teaches a model to generate the fixed Material Hero’s final RGB appearance from material text and camera/surface context. It must be deterministic, traceable, multi-view consistent, and free of watermarks or undocumented changes.

## Current material catalog

The canonical generator is `datagen/materials.py`.

| Dimension | Current value |
| --- | ---: |
| Base materials | 56 |
| Finishes | 5 |
| Conditions | 4 |
| Optional colors | 10 |
| Categories | 4 |
| Valid combinations after filtering | 1,806 |

Finishes:

- `polished`
- `matte`
- `satin`
- `brushed`
- `hammered`

Conditions:

- `clean`
- `dusty`
- `rusted`
- `scratched`

Categories:

- `metal`
- `dielectric`
- `organic`
- `translucent`

The generated library currently lives at `E:\Projects\neuron_data\neuron_library.json`. At the latest verification it contained the stress subset, not all 1,806 records.

## Stress set

The following eight materials cover the major material, transmission, coating, darkness, and bump paths:

1. `gold_polished_clean`
2. `car_paint_red_matte_dusty`
3. `iron_brushed_scratched`
4. `glass_polished_clean`
5. `glass_matte_clean`
6. `honey_satin_dusty`
7. `concrete_hammered_clean`
8. `rubber_black_polished_scratched`

The stress set is a QA tool. Passing it does not prove that every full-library record is supported; the 12 cracked asphalt records require separate resolution.

## Material record contract

Each material JSON record contains:

```text
id
metadata
  base
  category
  finish
  condition
  color_name?
shader_parameters
procedural_parameters
semantic
```

The complete parameter contract is documented in [`neuromat-hda.md`](neuromat-hda.md), while label semantics are documented in [`label-engine.md`](label-engine.md).

The material library used for a render must be copied or hashed into the dataset release. A mutable external JSON path is not sufficient provenance.

## Frame contract

### Core training data

| Data | Purpose | Requirement |
| --- | --- | --- |
| Beauty RGB | Model target | Required |
| Alpha/coverage | Fixed silhouette and valid-pixel mask | Required |
| World position `P` | Surface coordinate input/debugging | Required for the planned baseline |
| Surface normal `N` | Orientation input | Required for the planned baseline |
| Camera depth `Pz` | Geometry and projection validation | Required |
| Camera transform | Reproduce rays and view direction | Required |
| Camera intrinsics | Reproduce projection | Required |
| Material ID | Join frame to material record | Required |
| Compact prompt | Support application-style input | Required |
| Semantic label | Descriptive text conditioning/augmentation | Required |

### Recommended auxiliary data

- Raw BaseColor
- Raw Roughness
- Material category and token fields

These can help debugging or auxiliary supervision but are not generated products and are not required for the direct-RGB objective.

### Look-dev/debug data

- Variation mask
- Dirt mask
- Wear mask
- Scalar bump height or altered normal, explicitly named
- AO and curvature when useful

Debug data may be excluded from the final training package after the pilot proves it is unnecessary.

## Render rules

- Use one fixed Sculpted Rubber Toy and transform.
- Use one frozen studio-lighting setup.
- Keep HDRI, light intensity, exposure, render engine, samples, color management, and background identical across materials.
- Use deterministic material seeds.
- Do not use camera-dependent material projection.
- Preserve linear render data and record the OCIO/color-space interpretation.
- Do not use watermarked Houdini Apprentice renders in the released training set.
- Freeze the HDA, scene, material JSON, and render configuration before the full run.

## Camera plan

Historical planning targeted roughly 200 dome cameras. That count is **not yet locked**.

At 1,806 materials and 200 cameras, the full matrix would contain 361,200 frames before AOV multiplication. A small pilot must measure render time, storage, loading performance, and whether that camera density is necessary before committing to the full matrix.

The final camera set must:

- cover the hero without severe redundancy;
- preserve a constant, documented focal length unless variation is intentional;
- use stable camera IDs;
- record camera-to-world transform and intrinsics;
- avoid accidental clipping or framing changes;
- remain identical for every material.

## Logical manifest schema

The serialization format remains open, but each frame must logically provide:

```json
{
  "frame_id": "gold_polished_clean_cam_0042",
  "material_id": "gold_polished_clean",
  "camera_id": "cam_0042",
  "split": "train",
  "compact_prompt": "gold polished clean",
  "semantic_label": "...",
  "camera_to_world": [[0, 0, 0, 0]],
  "intrinsics": [[0, 0, 0], [0, 0, 0], [0, 0, 1]],
  "paths": {
    "beauty": "...",
    "alpha": "...",
    "position": "...",
    "normal": "...",
    "depth": "..."
  }
}
```

The example matrices are placeholders for shape only. Real matrices must contain full validated values and documented conventions.

For scale, a JSONL frame manifest plus separate dataset-level and material-level metadata is recommended, but this remains open decision O-003.

## Proposed release layout

```text
dataset_release/
  dataset.json
  materials.json
  cameras.json
  frames.jsonl
  splits.json
  images/
    beauty/
    alpha/
    position/
    normal/
    depth/
  debug/                 optional
  validation_report.json
  checksums.txt
```

Do not organize the only copy exclusively as thousands of material folders if that makes validation and sequential loading difficult. The manifest is the authoritative index regardless of physical layout.

## Split policy

- Assign splits by `material_id` before rendering or packaging.
- Keep every camera view of a material in the same split.
- Include a compositional holdout where base, finish, color, or condition concepts are individually represented in training but an exact combination is not.
- Do not tune against the final test split.
- Store the split assignment as versioned data.

## Validation requirements

Before release, automatically verify:

- every manifest path exists;
- image dimensions and channel types match the contract;
- values are finite and ranges are plausible;
- alpha and geometry AOVs align with beauty;
- IDs are unique;
- material and camera foreign keys resolve;
- all views of one material share one split;
- no watermark is present;
- no unexpected lighting, exposure, or color changes occurred;
- repeated pilot renders are deterministic within a defined tolerance.

Visual QA must include contact sheets holding camera constant across materials and holding material constant across cameras.

## Release identity

Every dataset release should record:

- release version and timestamp;
- Git commit;
- active scene and HDA versions plus hashes;
- Houdini and renderer versions;
- material library hash;
- camera-set hash;
- render settings and color configuration;
- manifest and split hashes;
- known limitations.
