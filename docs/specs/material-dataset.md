# Material dataset specification

Status: **Partially implemented; fixed-view v0 batch contract proposed and pilot not yet rendered**

Last reviewed: 2026-09-02

## Purpose

Dataset v0 teaches a model to generate the fixed Material Hero's RGB appearance from material text and one fixed camera/surface context. Later versioned releases add multiple cameras and then multiple geometries. Every release must be deterministic, traceable, comparable with earlier releases, and free of watermarks or undocumented changes.

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

The production render-system source is `datagen/data/neuron_library_prod.json`. It contains all 1,806 records and its current SHA-256 is `2d7bdcfe36ba06271b2b99d4c38530e3702a83f2abd40028ce1984654e314140`.

The external `E:\Projects\neuron_data\neuron_library.json` remains the interactive stress subset. It is not the production batch source. At the start of a release candidate, copy the repository production JSON into the release's `inputs` directory, verify its hash, and point `neuromat.dataset_path` at that frozen snapshot for the entire render.

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

The stress set is a QA tool. Passing it does not prove that every full-library record is supported, so the complete generated library must also pass schema validation. Asphalt uses the supported stochastic bump mode.

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
| View direction `V` | Camera-relative surface direction | Required; may be stored or deterministically derived from `P` and camera metadata |
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

- Use one fixed Sculpted Rubber Toy and transform for v0.
- Use one frozen studio-lighting setup.
- Keep HDRI, light intensity, exposure, render engine, samples, color management, and background identical across materials.
- Use deterministic material seeds.
- Do not use camera-dependent material projection.
- Preserve linear render data and record the OCIO/color-space interpretation.
- Do not use watermarked Houdini Apprentice renders in the released training set.
- Freeze the HDA, scene, material JSON, and render configuration before the full run.

## Camera and geometry sequence

### Dataset v0 — fixed view

- One Sculpted Rubber Toy and one fixed camera
- Approximately 1,806 beauty frames before exclusions or corrections
- Candidate raw render resolution: 512 × 512
- Camera: `/cameras/camera`, perspective 28 mm, with the active square-image `expandAperture` conform policy; the effective square-view field of view is approximately 41.03°
- One aligned geometry-buffer set may be shared by every material because `P`, `N`, `V`, and alpha are invariant across material changes
- Camera transform, intrinsics, geometry hash, and buffer conventions remain recorded even though they are constant

### Dataset v1 — multi-view hero

- The same hero rendered under a controlled camera dome
- Camera count, resolution, and storage budget remain open until a small pilot is measured
- Historical planning mentioned roughly 200 cameras, but that is not an accepted requirement
- Cameras use stable IDs and remain identical for every material

### Dataset v2 — multi-view, multi-geometry

- Several normalized geometries rendered across the approved camera set
- Geometry IDs, hashes, transforms, scale rules, and normal-generation rules become required metadata
- The geometry suite and position-normalization convention must be accepted before rendering

Each release must preserve the earlier evaluation cases so improvements from view diversity and then geometry diversity can be compared without changing every other variable at once.

## Houdini-to-Three.js calibration

Before judging model output from the application, reproduce the v0 hero and camera in Three.js and compare its `P`, `N`, `V`, alpha, projection, and silhouette against Houdini. Record coordinate handedness, space, units, object transform, camera convention, pixel origin, normal interpolation, edge coverage, and vertical image orientation. A mismatch here is an input-pipeline defect, not evidence about learned generalization.

## Dataset root and release identity

The accepted external dataset root is:

```text
E:\Projects\neuron_data\datasets
```

Never render directly into an unversioned `images` directory. Every attempt uses a release-candidate ID such as `material_hero_v0_rc001`. A release candidate remains mutable only while it is marked `in_progress`; a completed release is immutable and corrections create a new ID.

## Proposed v0 raw-render layout

```text
E:\Projects\neuron_data\datasets\
  material_hero_v0_rc001\
    dataset.json
    inputs\
      materials.json
      scene.hipnc-or-hiplc
      neuromat.hdanc-or-hdalc
      source_hashes.json
    entities\
      materials.json
      geometries.json
      cameras.json
      lights.json
    jobs\
      expected.jsonl
      progress.jsonl
      failures.jsonl
    renders\
      sculpted_rubber_toy\
        cam_0000\
          gold_polished_clean.exr
          ...
    previews\
    reports\
      validation_report.json
      checksums.txt
```

This layout is ready for later cameras and meshes: they add sibling camera and geometry directories without changing the work-item key or manifest schema. It avoids creating 1,806 tiny material directories.

The raw pilot should use one multilayer EXR per material × geometry × camera tuple. This matches the current Karma product and keeps beauty and AOVs atomically aligned. After the pilot, release packaging may extract training-friendly beauty images and deduplicate invariant fixed-view geometry buffers; raw source renders remain unchanged.

## Work-item and file naming

The logical work-item key is:

```text
(material_id, geometry_id, camera_id)
```

The frame ID is `{material_id}__{geometry_id}__{camera_id}`. The physical raw path is derived deterministically as `renders/{geometry_id}/{camera_id}/{material_id}.exr`.

For v0 this produces 1,806 expected work items from:

```text
1,806 materials × 1 geometry × 1 camera
```

IDs may contain lowercase ASCII letters, digits, and underscores only. Do not derive filenames from free-form labels.

## Resumable rendering

File existence alone is not a sufficient success check. For every expected work item:

1. Render to a temporary name such as `{material_id}.partial.exr`.
2. Open the result and validate resolution, required subimages/channels, finite values, and nonzero file size.
3. Rename the validated file to its final `.exr` name.
4. Append a completion record with file size, checksum, duration, attempt number, and source hashes to `progress.jsonl`.

On restart, derive the expected work-item list again. Skip a final EXR only after it passes the same lightweight validation; rerender missing, partial, unreadable, or contract-mismatched files. Append failures rather than overwriting history. This makes the folder scan useful without mistaking a truncated crash output for a completed frame.

## Dataset and entity metadata

`dataset.json` records the release ID and state, creation time, Houdini and Karma versions, render engine, resolution, samples, denoising, pixel filter, color configuration, AOV contract, coordinate conventions, and hashes of every frozen input.

`cameras.json` records for every `camera_id`:

- USD prim path and frame/time code;
- projection, focal length, horizontal and vertical aperture;
- image resolution, pixel aspect, and aspect-ratio conform policy;
- clipping range, focus distance, f-stop, shutter, and any lens shift;
- complete camera-to-world and world-to-camera matrices;
- the final pixel-space intrinsic matrix after resolution and conform policy are applied.

The current v0 entity is `/cameras/camera` at frame `1`: a 28 mm perspective camera. The Camera LOP authors millimeter UI values in USD's camera-unit convention, so raw USD values must not be relabeled as millimeters without conversion.

`geometries.json` records for every `geometry_id`:

- USD prim path, source path or embedded-scene identity, and content hash;
- object-to-world transform, stage units, up axis, and bounds;
- topology counts, normal interpolation, UV set, subdivision state, and relevant primvars.

The current v0 entity is `/GEO/material_hero` with identity transform, 1,611,108 points, and 3,239,506 faces on a Y-up stage with `metersPerUnit = 1`.

`lights.json` records each light prim, transforms, HDRI path and hash, color, intensity, exposure, and any renderer-specific settings. `materials.json` is the frozen production-library snapshot indexed by material ID.

Every progress/final frame row also records render duration, attempt, output size and checksum, and the hashes or IDs of the material, geometry, camera, lighting, scene, HDA, and render configuration that produced it.

## Logical manifest schema

The serialization format remains open, but each frame must logically provide:

```json
{
  "frame_id": "gold_polished_clean_hero_cam_0000",
  "material_id": "gold_polished_clean",
  "geometry_id": "sculpted_rubber_toy",
  "camera_id": "cam_0000",
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
    "view_direction": "...",
    "depth": "..."
  }
}
```

The example matrices are placeholders for shape only. Real matrices must contain full validated values and documented conventions.

The `view_direction` path may be omitted when the release contract specifies a deterministic derivation from `P` and camera metadata. The validator must reproduce and check that derivation.

Use JSONL for expected work items, render progress, failures, and the final frame manifest. Use ordinary JSON for dataset-level and entity metadata. The pilot must validate this serialization before decision O-003 is closed.

## Proposed packaged-release layout

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
    view_direction/       optional when derived deterministically
    depth/
  debug/                 optional
  validation_report.json
  checksums.txt
```

Do not organize the only copy exclusively as thousands of material folders if that makes validation and sequential loading difficult. The manifest is the authoritative index regardless of physical layout.

## Split policy

- Assign splits by `material_id` before rendering or packaging.
- Keep every camera view of a material in the same split.
- For multi-geometry releases, define separate seen-geometry and held-out-geometry evaluations without weakening the material-ID split.
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

Visual QA for v0 must hold the camera constant across materials. Multi-view releases additionally hold material constant across cameras; multi-geometry releases also hold prompt and camera constant across geometries.

## Release identity

Every dataset release should record:

- release version and timestamp;
- Git commit;
- active scene and HDA versions plus hashes;
- Houdini and renderer versions;
- material library hash;
- geometry or geometry-set hashes;
- camera-set hash;
- render settings and color configuration;
- manifest and split hashes;
- known limitations.
