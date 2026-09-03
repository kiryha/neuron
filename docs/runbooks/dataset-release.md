# Release a Material Hero dataset

Use this runbook after the HDA passes the stress set. A full batch is not the first test of the render pipeline.

## 1. Freeze release inputs

Create a versioned release-candidate directory under `E:\Projects\neuron_data\datasets`, for example `material_hero_v0_rc001`. Never mix corrected renders into an already completed release.

Assign a dataset release candidate and preserve:

- Git commit;
- Houdini version;
- scene path, version, timestamp, and hash;
- HDA path, version, timestamp, and hash;
- material JSON snapshot and hash;
- label-generator version and seed;
- geometry or geometry-set snapshot and hash;
- camera-set snapshot and hash;
- renderer, samples, resolution, denoising, OCIO, and output settings.

Copy mutable JSON/configuration into the release metadata. External paths alone are not reproducible records.

For the current v0 candidate, copy `datagen/data/neuron_library_prod.json` to `inputs/materials.json`, verify SHA-256 `2d7bdcfe36ba06271b2b99d4c38530e3702a83f2abd40028ce1984654e314140`, and drive the HDA from that frozen snapshot for the whole run.

## 2. Pass preflight gates

Do not proceed unless:

- all generated bump enums map to valid HDA branches;
- all eight stress materials passed beauty and AOV review;
- label validation passes with no duplicate words or contradictions;
- repeated test renders are deterministic;
- alpha, `P`, `Pz`, `N`, and `V` definitions or derivation are documented;
- final rendering produces no watermark;
- output storage and estimated render time are acceptable.

## 3. Create a pilot

For dataset v0, render all eight stress materials through the one fixed production camera.

The pilot must exercise:

- convex and concave geometry regions;
- metal, dark dielectric, coat, transmission, SSS, and each bump family;
- the exact production file-writing and manifest path.

Do not manually rename or repair pilot files. Fix automation and rerender so the same process can scale.

## 4. Validate the pilot automatically

Check:

- manifest parses successfully;
- all paths resolve;
- image dimensions and channels match the contract;
- matrices have expected shapes and finite values;
- alpha overlaps beauty correctly;
- `P`, `Pz`, `N`, and stored or derived `V` are finite and aligned;
- material and camera IDs are valid;
- each expected material appears exactly once at the fixed camera;
- labels pass current QA;
- no watermark or unexpected border is present.

Generate a machine-readable validation report and a human-viewable contact sheet.

## 5. Estimate the full run

Use measured pilot data to calculate:

- seconds per frame and per material;
- total GPU/render hours;
- bytes per frame by pass;
- total release size;
- temporary working-space requirement;
- upload and training-read cost.

Dataset v0 contains approximately 1,806 beauty frames before exclusions or corrections. The historical 200-camera target is not part of v0; estimate camera count and retained passes separately when preparing the later multi-view release.

## 6. Assign splits

Assign train/validation/test by material ID before final packaging:

- keep all present or future views of a material together;
- reserve exact combinations for compositional testing;
- preserve category and attribute coverage across splits;
- version the assignment;
- never reshuffle silently between experiments.

## 7. Run the production batch

- Use frozen inputs only.
- Write expected jobs, progress, and failures as append-safe JSONL records.
- Render each tuple to a `.partial.exr`, validate it, then rename it to `renders/{geometry_id}/{camera_id}/{material_id}.exr`.
- On restart, skip only final EXRs that still pass the lightweight resolution/channel/readability checks.
- Retry failed frames without rewriting verified frames unless the renderer cannot guarantee equivalent output.
- Do not change lighting, HDA, labels, camera definitions, or color configuration mid-release.
- If a critical defect is found, stop and create a new release candidate rather than mixing revisions.

## 8. Final validation

Repeat pilot validation across the complete release and additionally check:

- expected total counts;
- missing or duplicated frame keys;
- unexpected uniform/black/NaN images;
- image statistics by material and, for later releases, camera and geometry;
- split leakage;
- checksums;
- representative contact sheets across every category and bump type.

## 9. Publish the release record

The release is complete when it contains:

- dataset-level metadata;
- immutable material, geometry, and camera snapshots;
- frame manifest;
- split assignment;
- validation report;
- checksums;
- known limitations;
- instructions for the training loader.

Update [STATUS.md](../STATUS.md), [CHANGELOG.md](../CHANGELOG.md), and [ROADMAP.md](../ROADMAP.md) with the released version and the next training action.
