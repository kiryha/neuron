# Project decisions

This file records accepted choices that should survive individual chats. Implementation detail belongs in specifications; session history belongs in the changelog.

| ID | Status | Confirmed | Decision | Consequence |
| --- | --- | --- | --- | --- |
| D-001 | Accepted | 2026-08-26 | Material Hero is the current product milestone. | General neural assets and scenes must not distract from finishing data, training, and the first app. |
| D-002 | Accepted | 2026-08-26 | The model directly generates rendered RGB appearance. | PBR parameters, shader graphs, and texture maps are not model outputs. |
| D-003 | Superseded | 2026-08-26 | Material Hero v1 uses one fixed Sculpted Rubber Toy geometry. | Superseded by D-016; it remains true for the first training dataset, while later experiments deliberately test additional views and supplied meshes. |
| D-004 | Accepted | 2026-08-26 | Camera and fixed-surface context are part of the learning problem. | Preserve camera metadata, `P`, `N`, view direction derivation, and alpha/silhouette; the exact network architecture remains open. |
| D-005 | Accepted | 2026-08-26 | The first prompt-to-appearance mapping is deterministic. | Multiple samples from one prompt and a generative noise seed are deferred. |
| D-006 | Accepted | 2026-08-26 | Lighting, exposure, color management, geometry transform, and background remain controlled for v1. | The first model learns appearance under one studio setup and is not a relighting model. |
| D-007 | Accepted | 2026-08-26 | UV projection is sufficient for the fixed hero phase. | Do not restart the HDA around triplanar projection unless a demonstrated artifact threatens training. |
| D-008 | Accepted | 2026-08-26 | One master `neuromat` HDA is driven by deterministic JSON records. | Material behavior must remain traceable to material ID and library snapshot. |
| D-009 | Accepted | 2026-08-26 | Dataset splits are made by material ID, not by individual rendered frame. | Every camera view of one material belongs to the same split; compositional holdouts test unseen combinations. |
| D-010 | Accepted | 2026-08-26 | Historical chats and briefs are sources, not specifications. | Canonical truth lives in inspected artifacts, this decision log, and `docs/specs/`. |
| D-011 | Accepted | 2026-08-26 | Watermarked Houdini Apprentice renders are not final training data. | Apprentice can be used for development, but a non-watermarked final-render path is a Phase 1 gate. |
| D-012 | Accepted | 2026-08-26 | Persistent neural assets remain the long-term Neuron direction. | Material Hero should teach reusable packaging and inference concepts, but the general engine is a later phase. |
| D-013 | Accepted | 2026-08-26 | Future scene composition should retain USD-like references, transforms, versions, and overrides. | Neural representations may replace traditional payloads; a full USD replacement is not part of Material Hero. |
| D-014 | Accepted | 2026-08-28 | Remove the unsupported `cracked` bump type and map asphalt to `stochastic` at bump scale `0.02`. | Houdini needs only the existing none, stochastic, directional, and cellular modes; asphalt must be judged during stochastic bump validation. |
| D-015 | Accepted | 2026-08-28 | Treat `k` and `metallic_flake` as unused metadata for Material Hero v1. | Keep their values in JSON for provenance and possible future shader work, but they have no render effect and require no `neuromat` implementation. |
| D-016 | Accepted | 2026-08-31 | Develop geometry generalization as a staged experiment: fixed camera and one hero first; Three.js out-of-distribution orbit, zoom, and mesh tests; then a multi-view dataset; then a multi-view, multi-geometry dataset. | Every stage keeps prompt-to-RGB and `P`/`N`/`V`/alpha conditioning, measures the failures of the previous dataset, and does not claim unsupported views or meshes as working product features. |
| D-017 | Accepted | 2026-09-02 | Store versioned dataset releases under `E:\Projects\neuron_data\datasets`. | Raw renders, frozen inputs, manifests, progress, and validation reports remain outside OneDrive and are grouped by explicit release-candidate ID. |
| D-018 | Accepted | 2026-09-02 | Use 512 × 512 as the dataset-v0 pilot resolution with the existing 28 mm Houdini camera. | Scene 005 now authors 512 × 512; raise it only if the fixed-camera pilot demonstrates material detail that is materially lost at the model's planned 512 × 512 output size. |

## Open decisions

| ID | Question | Needed by |
| --- | --- | --- |
| O-001 | What exact neural architecture is the first baseline: per-surface MLP, image network, or staged comparison? | Before Phase 2A implementation |
| O-002 | What text representation is used first: controlled learned tokens, pretrained encoder, or both? | Before Phase 2A implementation |
| O-003 | Is the scalable frame manifest JSONL, a structured `transforms.json`, or both? | Before Phase 1B pilot |
| O-004 | What are the multi-view render resolution, camera count, and storage budget? | Before the multi-view dataset extension |
| O-006 | Which auxiliary AOVs are worth retaining after the pilot? | Before Phase 1B exit |
| O-007 | Which additional geometries and position-normalization convention are used for multi-geometry training? | Before the multi-geometry dataset extension |

## Adding a decision

Add a row only after the user accepts a choice or implementation makes the choice explicit and it has been verified. Include the date and update any affected specifications and roadmap gates.
