# Release a Material Hero dataset

Use this runbook after the HDA passes the stress set. A full batch is not the first test of the render pipeline.

## 1. Freeze release inputs

Assign a dataset release candidate and preserve:

- Git commit;
- Houdini version;
- scene path, version, timestamp, and hash;
- HDA path, version, timestamp, and hash;
- material JSON snapshot and hash;
- label-generator version and seed;
- camera-set snapshot and hash;
- renderer, samples, resolution, denoising, OCIO, and output settings.

Copy mutable JSON/configuration into the release metadata. External paths alone are not reproducible records.

## 2. Pass preflight gates

Do not proceed unless:

- all generated bump enums map to valid HDA branches;
- all eight stress materials passed beauty and AOV review;
- label validation passes with no duplicate words or contradictions;
- repeated test renders are deterministic;
- alpha, `P`, `Pz`, and `N` definitions are documented;
- final rendering produces no watermark;
- output storage and estimated render time are acceptable.

## 3. Create a pilot

Render all eight stress materials through a small but representative camera subset.

The pilot must exercise:

- frontal, profile, high, low, and rear views;
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
- `P`, `Pz`, and `N` are finite and aligned;
- material and camera IDs are valid;
- each expected material × camera pair appears exactly once;
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

The historical target of 1,806 materials × 200 cameras equals 361,200 frames. Reduce camera count or retained debug passes if the pilot shows that this scale is unnecessary or impractical.

## 6. Assign splits

Assign train/validation/test by material ID before final packaging:

- keep all views of a material together;
- reserve exact combinations for compositional testing;
- preserve category and attribute coverage across splits;
- version the assignment;
- never reshuffle silently between experiments.

## 7. Run the production batch

- Use frozen inputs only.
- Write progress and failures to a resumable job record.
- Retry failed frames without rewriting verified frames unless the renderer cannot guarantee equivalent output.
- Do not change lighting, HDA, labels, camera definitions, or color configuration mid-release.
- If a critical defect is found, stop and create a new release candidate rather than mixing revisions.

## 8. Final validation

Repeat pilot validation across the complete release and additionally check:

- expected total counts;
- missing or duplicated frame keys;
- unexpected uniform/black/NaN images;
- image statistics by material and camera;
- split leakage;
- checksums;
- representative contact sheets across every category and bump type.

## 9. Publish the release record

The release is complete when it contains:

- dataset-level metadata;
- immutable material and camera snapshots;
- frame manifest;
- split assignment;
- validation report;
- checksums;
- known limitations;
- instructions for the training loader.

Update [STATUS.md](../STATUS.md), [CHANGELOG.md](../CHANGELOG.md), and [ROADMAP.md](../ROADMAP.md) with the released version and the next training action.
