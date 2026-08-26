# Neuron repository guidance

This repository contains the Material Hero phase of Neuron. The immediate goal is to finish a deterministic Houdini dataset, train a text-conditioned model that directly generates rendered RGB images of one fixed hero object, and integrate that model into the web application.

## Read before working

Read these files in order:

1. `docs/START-HERE.md`
2. `docs/STATUS.md`
3. `docs/DECISIONS.md`
4. The specification relevant to the task
5. The matching runbook when operating Houdini or releasing data

`docs/sources/` contains historical briefs and exported chats. Use it for provenance and rationale, not as the current specification.

## Source-of-truth order

When information conflicts, prefer:

1. Inspected runtime artifacts: current code, generated JSON, active Houdini scene/HDA, and rendered output
2. Accepted decisions in `docs/DECISIONS.md`
3. Canonical specifications in `docs/specs/`
4. Current handoff state in `docs/STATUS.md`
5. Historical material in `docs/sources/`

Do not turn an AI suggestion into a project requirement unless the user accepts it or it is implemented and verified.

## Documentation maintenance

After meaningful work:

- Update `docs/STATUS.md` with the verified result and next exact action.
- Append a short entry to `docs/CHANGELOG.md` for material repository, Houdini, dataset, model, or application changes.
- Update the relevant specification when an interface or requirement changed.
- Add an entry to `docs/DECISIONS.md` only for an actual project decision, not routine implementation detail.
- Update `docs/sources/chat-index.md` when new external conversations are imported.

Use these state labels consistently:

- **Verified**: inspected in the current artifact or demonstrated by a test/render.
- **Implemented**: present, but not necessarily validated end to end.
- **Planned**: accepted direction that is not implemented.
- **Open**: unresolved choice or question.
- **Historical**: context that may no longer be current.
- **Superseded**: explicitly replaced by a later decision or implementation.

Keep `docs/STATUS.md` concise. It should describe the present, not accumulate history.

## External Houdini workspace

The active Houdini project is outside this Git repository:

- Project: `C:\Users\kko8\OneDrive\projects\neuron\prod\3D`
- Active scene: `scenes\material_hero_004.hipnc`
- Active HDA: `hda\lop_KKO8.neuromat.1.2.hdanc`
- Generated material JSON: `E:\Projects\neuron_data\neuron_library.json`

Treat repository copies under `datagen/hips/` as historical unless `docs/STATUS.md` says otherwise. Do not overwrite or relocate external Houdini files without explicit user authorization. Inspect exact paths and preserve backups before changing HDA definitions or scenes.

## Current scope boundaries

- Generate final RGB appearance, not PBR maps or shader parameters.
- Use one fixed Sculpted Rubber Toy geometry for Material Hero v1.
- Keep lighting controlled and fixed for the first model.
- Preserve camera and geometry metadata for multi-view training.
- Do not begin the general neural-asset engine while Material Hero is incomplete.
- Keep implementation minimal and understandable for a solo learning project.
