# Label engine specification

Status: **Implemented and full-library duplicate-word QA verified**

Last reviewed: 2026-09-02

## Purpose

The label engine converts deterministic technical material records into controlled natural-language descriptions for training. Labels must describe the rendered facts without introducing framing, physics, or condition contradictions.

The implementation is `BuildPrompts` in `datagen/materials.py`.

## Material text representations

Every dataset material should preserve two forms:

### Compact prompt

A direct application-style prompt derived from structured metadata:

```text
gold polished clean
car paint red matte dusty
iron brushed scratched
```

This supports the intended Neuron prompt bar and controlled-vocabulary testing.

### Semantic label

A deterministic descriptive sentence assembled from authored semantic fields and a controlled template family:

```text
Photorealistic material study of raw industrial iron, with brushed grain interrupted by deeper scratches; with heavy handling wear and usage marks.
```

Training may use compact prompts, semantic labels, or controlled augmentation between them. Both must remain traceable to the same `material_id`.

## Semantic record

Current records may contain:

- `base_phrase`
- `finish_adjective`
- `finish_description`
- `condition_phrase`
- `condition_mode`
- `composition_style`
- `semantic_tags`
- `semantic_hints`
- `semantic_label`

The structured fields are the meaning. Templates provide shallow wording variation; they must not invent new material behavior.

## Determinism

- Material variation seed is derived from the MD5 hash of `material_id` and stored as a float in `[0, 1]`.
- Label templates use a fixed random seed of `42` by default.
- Entries are processed in sorted material-ID order.
- Existing labels are skipped unless overwrite is explicitly enabled.
- Existing labels are still validated when overwrite is disabled.

Changing the template list, sort order, seed, or overwrite behavior can change labels and therefore requires a new material-library/dataset version.

## Template families

Current families are selected by semantic condition mode:

- pristine;
- abrasion;
- contamination;
- aging;
- pristine frosted/translucent specializations.

Allowed shells remain close to:

- close-up;
- material study;
- texture study;
- photorealistic material study.

Do not add cinematic scenes, camera motion, unrelated objects, environments, or uncontrolled physics synonyms.

## Composition rules

- Put the base material early in the description.
- Preserve color when the material is colorable.
- Describe finish once.
- Describe condition once.
- Keep contamination wording appropriate to the material, such as adhered dust for sticky materials.
- Keep frosted-glass transmission language distinct from mirror-polished language.
- Do not imply geometry changes that the HDA does not render.
- Do not describe unsupported lighting, framing, or environmental changes.

## Required validation

For every generated label:

- non-empty string;
- no repeated adjacent words such as `with with`;
- no doubled punctuation, trailing separators, or repeated long clauses;
- no duplicated dirt/dust wording;
- no mirror wording for frosted material;
- required semantic content tokens are present;
- material ID, metadata, semantic fields, and label remain mutually consistent.

Run validation against both newly generated labels and existing labels. Skipping an existing label must not skip QA.

## Verified full-library result

The production library was regenerated with seed `42` and `overwrite=True` on 2026-09-02. The generator templates no longer add a connector before `finish_description`, because every authored finish description already begins with `with`.

All 1,806 production records pass adjacent-duplicate QA, including zero occurrences of `with with`. Repeating the full regeneration produced identical labels.

## Prompt aliases

The application may accept friendly vocabulary that differs from metadata, for example `dirty` when the canonical condition is `dusty`. Alias normalization must be explicit and versioned rather than silently changing labels.

Initial examples:

| User token | Canonical token |
| --- | --- |
| `dirty` | `dusty` |
| `gray` | `grey` |

The complete alias list remains planned and must be shared by application validation and training prompt augmentation.

## Acceptance criteria

- Repeated runs with the same seed and source library produce identical labels.
- All 1,806 full-library records pass schema and label validation.
- Compact prompts can be reconstructed deterministically from metadata.
- Labels contain no duplicate words or contradictions.
- The stress-set labels are manually reviewed before the dataset pilot.
- Dataset releases include the exact material/label snapshot used for rendering and training.
