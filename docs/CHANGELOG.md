# Project changelog

This is a concise log of meaningful project changes. It is not a replacement for Git history or `STATUS.md`.

## 2026-08-26

### Documentation baseline

- Reframed the README around the actual Material Hero milestone.
- Established canonical documentation, decision, status, roadmap, specification, runbook, and source-archive roles.
- Audited the material generator, current stress JSON, active Houdini scene, HDA graph, render settings, geometry attributes, and current AOVs.
- Confirmed direct RGB generation, one fixed Sculpted Rubber Toy, controlled lighting, and future neural assets as the accepted project direction.
- Verified the intended material application path: the UI sets `material_id`, then internal HDA Python Script LOPs load JSON values and derive bump mode/cap during the cook.
- Implemented direct bump routing and production stochastic, directional, and cellular bump branches in `neuromat` 1.2; fixed-camera stress-set validation remains pending.
- Identified remaining Phase 1 blockers: bump visual validation, unsupported cracked records, missing shader connections, label QA, dataset automation, and watermarked final renders.

## 2026-08-28

### `neuromat` shader bindings

- Connected HDA `subsurface`, `subsurface_color`, and `thin_walled` values to their MaterialX Standard Surface parameters with relative references.
- Verified the saved scene and HDA contain all five expressions: subsurface, three subsurface-color components, and thin-wall.
- Removed these fields from the HDA blocker list; `k`, metallic flake, and transmission-scatter policy remain unresolved.

### Bump schema simplification

- Removed `cracked` from the generator's valid bump types, so no new Houdini branch is required.
- Remapped all asphalt variants to the existing stochastic bump mode at scale `0.02`.
- Updated the checked-in production library and canonical documentation to match the four-mode HDA contract.

### Metadata-only shader fields

- Classified `k` and `metallic_flake` as unused metadata for Material Hero v1.
- Kept both fields in JSON for compatibility, provenance, and possible future shader work, while explicitly excluding them from required HDA behavior.
- Reduced the unresolved shader-schema work to `transmission_scatter` verification or classification.

## 2026-08-31

### Staged geometry-generalization experiment

- Made the first training release a one-geometry, one-camera prompt-to-RGB baseline conditioned by `P`, `N`, `V`, and alpha.
- Defined Three.js orbit, zoom, and alternate supplied meshes as deliberate out-of-distribution tests rather than promised first-model capabilities.
- Sequenced later dataset/model versions as multi-view on the hero followed by multi-view and multi-geometry training.
- Added Houdini-to-Three.js geometry-buffer calibration as a prerequisite so coordinate mismatch is not confused with model generalization failure.

## 2026-09-02

### Look-dev approval and batch preflight

- Recorded user approval of the fixed-camera stress renders, including stochastic, directional, and cellular bump behavior.
- Verified `material_hero_005.hipnc` and the updated `neuromat` 1.2 HDA as the current external Houdini artifacts.
- Set the repository production material JSON as the planned batch source of truth.
- Identified preflight issues before automation: development JSON still configured in the scene, 805 duplicate-word labels, and apparent camera/resolution discrepancies that required USD-time/fallback inspection.

### Scene and label preflight fixes

- Confirmed that the apparent 50 mm camera value was the USD no-time fallback; frame 1 correctly resolves to the Camera LOP's 28 mm lens.
- Confirmed that the RenderProduct's 2048 × 1080 value was an unauthored fallback and did not override the active RenderSettings resolution.
- Backed up `material_hero_005.hipnc` and changed the active candidate dataset resolution from 1280 × 1280 to 512 × 512.
- Removed template-level `with with` construction, added adjacent-word QA, and made skipped existing labels pass validation.
- Regenerated all 1,806 production labels with seed `42`; zero adjacent duplicates remain and repeated generation produced identical labels.

### Dataset-v0 batch proposal

- Set `E:\Projects\neuron_data\datasets` as the external dataset root.
- Proposed versioned release-candidate directories, deterministic material × geometry × camera paths, multilayer raw EXRs, JSON/JSONL metadata, and validate-before-skip crash recovery.
- Recorded current camera and geometry entity metadata needed for later Houdini-to-Three.js calibration.
- Clarified that the `.hipnc` scene and `.hdanc` HDA can downgrade an Indie session; converted or rebuilt `.hiplc`/`.hdalc` inputs and an unwatermarked pilot remain required.

### Minimal dataset contract accepted

- Replaced the initial production-style manifest and metadata proposal with a minimal folder-indexed dataset suitable for the solo learning project.
- Set dataset v0 to 1024 × 1024 with DOF disabled and one multilayer EXR per material folder containing Beauty, world `P`, smooth unbumped world `N`, world `V`, and material-independent Coverage.
- Excluded `Pz`, variation, dirt, wear, bump, BaseColor, Roughness, and other debug AOVs from dataset output while preserving their material effects in Beauty.
- Kept the material snapshot name `neuron_library_prod.json` and dropped dataset hashes, renamed source copies, manifests, entity records, schemas, progress logs, and automatic validation reports.
- Accepted `{geometry_id}/{camera_id}/{material_id}/render.exr` and folder-existence skipping, with manual folder deletion used to request a rerender.
- Selected a sequential `datagen/datarender.py` script instead of TOPs/PDG; the implementation remains pending.
- Verified that scene 005 already resolves to 1024 × 1024, while DOF is still active and must be disabled during the next Houdini implementation step.
