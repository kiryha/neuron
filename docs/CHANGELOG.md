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
