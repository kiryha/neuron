# `neuromat` HDA specification

Status: **Bump branches and dataset RenderVars validated; full shader-contract validation pending**

Last reviewed: 2026-09-03

## Purpose

`neuromat` is the single master MaterialX HDA used to turn a deterministic material JSON record into a rendered Material Hero appearance and diagnostic signals.

It is intentionally a controlled dataset shader, not a universal material-authoring system.

## Active artifacts

- Scene: `C:\Users\kko8\OneDrive\projects\neuron\prod\3D\scenes\material_hero_006.hiplc`
- HDA: `C:\Users\kko8\OneDrive\projects\neuron\prod\3D\hda\lop_KKO8.neuromat.1.2.otllc`
- Node: `/stage/neuromat`
- Type: `KKO8::neuromat::1.2`
- Interactive stress JSON: `E:\Projects\neuron_data\neuron_library.json`
- Production batch source: `datagen/data/neuron_library_prod.json`, copied into each release as a frozen snapshot

Repository files under `datagen/hips/` are snapshots. The checked-in HDA matches the active external HDA, but the current external scene is newer than its repository snapshot and remains authoritative.

## Architectural constraints

- One HDA serves all material records.
- Material identity and controls originate in JSON.
- UV projection remains acceptable for the fixed hero.
- Baked AO and curvature signals support dirt and wear.
- COPS and MaterialX may both contribute procedural signals.
- Lighting and camera must not change material-space patterns.
- Identical material IDs must reproduce identical parameters and masks.
- Keep the graph minimal enough to inspect and debug manually.

## JSON contract

### `metadata`

- `base`
- `category`
- `finish`
- `condition`
- optional `color_name`

### `shader_parameters`

- `base_value`
- `base_color`
- `metalness`
- `specular_ior`
- `k` (metadata-only in v1)
- `specular_roughness`
- `specular_anisotropy`
- `subsurface`
- `subsurface_color`
- `coat`
- `coat_roughness`
- `sheen`
- `transmission`
- `transmission_color`
- `transmission_depth`
- `transmission_scatter`
- `transmission_dispersion`
- `thin_walled`
- `metallic_flake` (metadata-only in v1)

`k` and `metallic_flake` remain physically under `shader_parameters` for compatibility with existing libraries and possible future shader experiments. They are explicitly unused metadata in Material Hero v1: the production graph ignores them, their values do not affect rendered pixels, and no HDA binding is required. New code must not assume that every key under `shader_parameters` is render-facing.

### `procedural_parameters`

- `variation_seed`
- `bump_scale`
- `bump_type`
- `noise_scale`
- `dirt`
- `wear`

The generator validates these records before writing JSON. Material application is intentionally cook-driven:

1. The Houdini UI calls `datagen/datagen.py::Datagen.set_material`, changing the HDA `material_id`.
2. Internal Python Script LOP `read_JSON_data` reads the HDA `dataset_path`, resolves that ID, and writes the record’s values onto the HDA.
3. Internal Python Script LOP `set_bump_type` converts none, stochastic, directional, and cellular strings to integer modes; unknown strings currently default to stochastic mode `1`.
4. Internal Python Script LOP `set_bump_cap` calculates the safety cap from finish and condition.

This path is verified working interactively and is intentionally compatible with future batching: a work item can set one material ID and cook the HDA. The obsolete partial `datagen/tools.py::apply_material` alternative has been removed.

## Mask behavior

### Variation

Purpose:

- subtle material-wide color/value variation;
- small roughness breakup;
- removal of perfectly uniform synthetic appearance.

Constraints:

- not cavity-driven;
- not edge-driven;
- must not read as dirt, stains, or large blobs;
- deterministic from material seed.

### Dirt

Purpose:

- broad contamination;
- increased response in occluded and concave regions;
- contamination tint and roughness increase.

Inputs:

- baked AO;
- concavity;
- broad procedural breakup;
- JSON `dirt` intensity.

### Wear

Purpose:

- abrasion on exposed/convex regions;
- localized scratches or worn response;
- roughness and possibly color modification appropriate to the material family.

Inputs:

- macro and micro convexity;
- higher-frequency breakup;
- JSON `wear` intensity.

### Bump

Purpose:

- view-dependent micro-surface response;
- visible distinction between procedural finish families;
- no large-scale silhouette deformation.

Inputs:

- `bump_type`;
- `bump_scale`;
- `noise_scale`;
- `variation_seed`;
- internal safety cap.

## Bump branch contract

| Type | Intended use | Required HDA state |
| --- | --- | --- |
| `none` | Intentionally smooth surface | Implemented; returns zero |
| `stochastic` | Polished/matte/satin micro-breakup | Implemented; stress renders approved |
| `directional` | Brushed grain and aligned scratches | Implemented; stress renders approved |
| `cellular` | Hammered/pitted response | Implemented; stress renders approved |

The final selector must use one explicit mapping shared by JSON validation, HDA menu values, and shader switch inputs. The validated v1 contract contains only none, stochastic, directional, and cellular. Do not use an offset expression that relies on unconnected slots.

## Current bump implementation

The live production switch now selects the direct integer mode with all four intended inputs connected.

- Stochastic combines two object-space Fractal 3D noises at `noise_scale × 50` and `× 120`, octaves `3 / 2`, and weights `0.7 / 0.3`.
- Directional combines anisotropic UV noise at `noise_scale × (80, 8)` with stochastic breakup at weights `0.8 / 0.2`.
- Cellular combines object-space cellular noise at `noise_scale × 18` with stochastic breakup at weights `0.85 / 0.15`.
- The selected height is scaled by `bump_scale`, limited by `bump_cap`, and converted through MaterialX bump.

The fixed-camera stress comparison was visually approved on 2026-09-02. The next gate is the fixed-camera dataset-v0 pilot. Camera-dome work begins only after the first trained model and its Three.js out-of-distribution tests are understood.

## Shader integration

Required behavior:

- JSON base color is modified only by controlled variation and dirt.
- JSON roughness is modified by variation, dirt, and wear without invalid ranges.
- Metalness, IOR, transmission, coat, and other identity parameters are not randomly altered.
- Bump modifies the normal response physically through MaterialX.
- Translucent and SSS materials remain visually distinguishable and stable.

Current coverage and exclusions:

- `subsurface`, `subsurface_color`, and `thin_walled` are connected through relative references from the HDA interface to Standard Surface.
- `k` and `metallic_flake` are intentionally not consumed because they are metadata-only in v1.
- The treatment of `transmission_scatter` requires verification in Karma/MaterialX.

Any unsupported JSON parameter must be connected, explicitly removed from the v1 schema, or documented as metadata-only. Silent no-op parameters are not acceptable in the final library.

## Current dataset RenderVars

- Beauty RGBA (`C.RGB` target and `C.A` Coverage)
- world-space `P`
- smooth, unbumped world-space `Nb` sourced from `N_base`
- normalized world-space `V` from surface toward camera

The 2026-09-03 Indie pilot verified these four EXR subimages at 1024 × 1024 with no watermark or non-finite values. `V` numerically matches `normalize(camera_position - P)` with mean dot product `0.9999999`.

No separate Coverage RenderVar is required. Transmission does not drive Standard Surface opacity in the current library, so `C.A` remains geometry coverage for glass and opaque materials. Keep opacity at `1` and do not introduce cutout, holdout, or shadow-catcher alpha without revisiting this contract.

`Pz`, variation, dirt, wear, bump, BaseColor, Roughness, and other debug RenderVars are disabled for dataset output. The procedural effects remain active in Beauty.

## Stress-set expectations

| Material | Primary coverage |
| --- | --- |
| `gold_polished_clean` | Metal, polished response, stochastic micro-breakup |
| `car_paint_red_matte_dusty` | Color palette, coat, matte, dirt |
| `iron_brushed_scratched` | Directional bump, anisotropy, wear |
| `glass_polished_clean` | Transmission and dispersion |
| `glass_matte_clean` | Frosted transmission and roughness |
| `honey_satin_dusty` | Transmission/SSS behavior and sticky contamination |
| `concrete_hammered_clean` | Cellular bump |
| `rubber_black_polished_scratched` | Dark dielectric, stochastic bump, wear |

## Versioning and validation

Before material graph changes:

- create a recoverable HDA backup or incremented definition;
- preserve the working scene;
- record the selected material and test settings.

Before declaring the HDA locked:

- render the stress set from one fixed camera;
- inspect beauty and every retained AOV;
- confirm each bump branch by bypassing ambiguity rather than judging only the final beauty;
- switch away and back to each material and confirm deterministic output;
- scan all 1,806 records for unsupported enum values and parameter ranges;
- update [STATUS.md](../STATUS.md) and [CHANGELOG.md](../CHANGELOG.md).

## Non-goals

- Universal material support
- Perfect object-space/triplanar projection
- Per-material custom node graphs
- Large displacement or geometry modification
- Random lighting or procedural seeds during dataset rendering
