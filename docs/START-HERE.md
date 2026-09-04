# Start here

Last reviewed: 2026-09-03

Neuron is currently focused on **Material Hero**: a text-conditioned image generator that first learns the appearance of one Sculpted Rubber Toy from one fixed camera and studio-lighting setup.

The overall phase remains Houdini data generation. An isolated local Three.js slice is now implemented: it loads the exported hero GLB, displays its world-space normal pass, supports orbit, resets to a stable reference view, and includes an inactive prompt field. Prompt-driven model integration and deployment remain later work, as does the broader neural-asset engine.

## Reading order

When returning to the project, read:

1. [Project status](STATUS.md) — what works, what is blocked, and the next exact action
2. [Decisions](DECISIONS.md) — accepted architectural and scope choices
3. [Roadmap](ROADMAP.md) — phase gates and completion criteria
4. The relevant specification:
   - [Material Hero model](specs/material-hero-model.md)
   - [Material dataset](specs/material-dataset.md)
   - [`neuromat` HDA](specs/neuromat-hda.md)
   - [Label engine](specs/label-engine.md)
   - [Application](specs/application.md)
5. The relevant runbook:
   - [Resume Houdini work](runbooks/houdini-resume.md)
   - [Release a dataset](runbooks/dataset-release.md)

The public overview and local run instructions are in the repository [README](../README.md).

## Project in one paragraph

Houdini first generates one fixed view of the hero for every material and canonical text description, together with `P`, unbumped `Nb`, `V`, and Beauty-alpha coverage context. The first model learns prompt-conditioned RGB for that view. The Neuron application recreates the geometry buffers in Three.js and intentionally lets the user orbit, zoom, and switch supplied meshes even though those inputs are out of distribution. Later dataset versions add multiple cameras and then multiple geometries so their effect on those failures can be measured. The model does not generate shader parameters, texture maps, geometry, or editable lighting.

## Current pipeline

```text
Material definitions and labels
          |
          v
JSON-driven neuromat HDA
          |
          v
Karma 1024² Beauty RGBA + P/Nb/V EXR per material
          |
          v
Text-conditioned Material Hero model
          |
          v
FastAPI inference + React viewport on Hugging Face Spaces
```

## Source-of-truth hierarchy

Use this order when documents disagree:

1. Current code, generated JSON, active Houdini graph, and rendered pixels
2. Accepted entries in [DECISIONS.md](DECISIONS.md)
3. Canonical files under `docs/specs/`
4. Current state in [STATUS.md](STATUS.md)
5. Historical files and chats under `docs/sources/`

The historical sources explain how the project evolved, but they contain obsolete material counts, old schemas, speculative model architectures, and advice that was never adopted.

## Repository map

```text
datagen/            Material library, label generator, Houdini UI and helpers
datagen/hips/       Historical repository copies of Houdini assets
train/              Empty training scaffold
neuron/             Empty neural-engine package scaffold
src/                React/React Three Fiber application scaffold
public/geometry/    Deployable web geometry, including the reduced Material Hero GLB
public/cameras/     Copied dataset camera records for Three.js reference views
main.py             FastAPI status endpoint and static frontend host
docs/               Canonical project documentation
docs/sources/       Historical briefs and exported AI conversations
```

The active Houdini project is currently external to the repository. Exact paths are maintained in [STATUS.md](STATUS.md) and the [Houdini runbook](runbooks/houdini-resume.md).

## Ten-minute recovery checklist

1. Read [STATUS.md](STATUS.md), especially **Next exact actions**.
2. Check `git status` and do not overwrite unrelated user changes.
3. Confirm the active Houdini scene and HDA paths before opening or editing them.
4. Confirm whether `neuron_library.json` contains the eight-material stress subset or the full library.
5. Work only on the current phase gate in [ROADMAP.md](ROADMAP.md).
6. Before stopping, update status, changelog, and any changed specification.

## Vocabulary

- **Material Hero**: the first Neuron model and application milestone.
- **Hero geometry**: the Sculpted Rubber Toy used for the fixed-view training baseline and later hero multi-view release.
- **`neuromat`**: the master JSON-driven Houdini material HDA.
- **Material library**: deterministic JSON records combining base, finish, condition, and optional color.
- **Stress set**: eight representative materials used to validate all important HDA branches before scaling up.
- **Dataset v0**: one hero geometry and one fixed camera; the first training baseline.
- **Out-of-distribution test**: a camera or supplied mesh not represented in the current training release; output is experimental and may be broken.
- **Canonical prompt**: deterministic natural-language description stored with a material record.
- **Neural asset**: a future versioned, renderable model package; not part of the current implementation.

## Documentation states

Canonical documents use the following meanings:

- **Verified** — inspected in the current artifact or demonstrated by a test/render
- **Implemented** — exists, but may still require validation
- **Planned** — accepted but not implemented
- **Open** — unresolved
- **Historical** — retained for context
- **Superseded** — replaced by a newer decision or implementation
