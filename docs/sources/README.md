# Historical source archive

Files in this directory preserve project history, earlier briefs, and external AI conversations. They are intentionally not rewritten to match the latest implementation.

## Archive policy

- Keep source files unchanged whenever practical.
- Add newly imported chats under `chats/`.
- Summarize new chats in [chat-index.md](chat-index.md).
- Promote only accepted decisions into `docs/DECISIONS.md`.
- Promote stable requirements into `docs/specs/` after checking current code and Houdini artifacts.
- Mark obsolete advice in the index rather than deleting historical context.

## Markdown briefs

### [neuromat.md](neuromat.md)

The strongest historical written brief for the Houdini material asset. It established one hero, one HDA, JSON control, UV acceptance, baked AO/curvature, the four signal families, and the AOV plan. It predates the implemented dirt/wear work and the latest bump checkpoint; its ~2,000-material and 200-camera statements are historical targets.

### [material-hero.md](material-hero.md)

An early Phase 1/2 specification. It contains useful synthetic-data principles but also superseded claims about RGB+density, voxel baking, 1,980 materials, fixed output sizes, and masking Apprentice watermarks. Watermarked renders are now rejected rather than masked during training.

### [label-engine.md](label-engine.md)

An early implementation brief for randomized labels. The current code uses deterministic mode-specific template families and a different semantic schema. The historical `good_label` key and four generic cinematic templates are superseded.

### [cop-hda.md](cop-hda.md)

A broad early texture/HDA design collection. Its “Big Four” concept and deterministic seed rationale remain useful. Triplanar requirements, per-material HDA instancing, some MaterialX wiring advice, seven-item stress list, and RGB-density framing are superseded or incomplete.

### [init-prompt.md](init-prompt.md)

The original coding prompt and long-term vision. It documents intended style and stack but proposes files and model behavior that were never implemented. It is project-origin context, not an implementation plan.

## Exported chats

See [chat-index.md](chat-index.md) for adopted decisions, historical checkpoints, and known unreliable advice in each PDF.
