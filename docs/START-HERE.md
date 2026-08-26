# Start here

Last reviewed: 2026-08-26

Neuron is currently focused on **Material Hero**: a text-conditioned image generator that renders the appearance of one fixed Sculpted Rubber Toy under controlled cameras and studio lighting.

The immediate task is to finish Houdini data generation. Training and application integration come afterward. The broader neural-asset engine remains a later research direction.

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

Houdini generates deterministic multi-view renders of a single hero object using a combinatorial material library and canonical text descriptions. A future model will learn a direct mapping from material text plus camera and fixed-surface context to rendered RGB. The Neuron application will let a user enter a prompt such as `gold brushed dirty`, orbit the hero, and receive a consistent neural rendering. It will not generate shader parameters, texture maps, arbitrary objects, or editable lighting in the first version.

## Current pipeline

```text
Material definitions and labels
          |
          v
JSON-driven neuromat HDA
          |
          v
Karma multi-view RGB + alpha + geometry/camera metadata
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
- **Hero geometry**: the fixed Sculpted Rubber Toy used in every v1 generation.
- **`neuromat`**: the master JSON-driven Houdini material HDA.
- **Material library**: deterministic JSON records combining base, finish, condition, and optional color.
- **Stress set**: eight representative materials used to validate all important HDA branches before scaling up.
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
