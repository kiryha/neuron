# `neuromat` HDA specification

Status: **Bump branches implemented; visual and full shader-contract validation pending**

Last reviewed: 2026-08-26

## Purpose

`neuromat` is the single master MaterialX HDA used to turn a deterministic material JSON record into a rendered Material Hero appearance and diagnostic signals.

It is intentionally a controlled dataset shader, not a universal material-authoring system.

## Active artifacts

- Scene: `C:\Users\kko8\OneDrive\projects\neuron\prod\3D\scenes\material_hero_004.hipnc`
- HDA: `C:\Users\kko8\OneDrive\projects\neuron\prod\3D\hda\lop_KKO8.neuromat.1.2.hdanc`
- Node: `/stage/neuromat`
- Type: `KKO8::neuromat::1.2`
- JSON: `E:\Projects\neuron_data\neuron_library.json`

Repository files under `datagen/hips/` are older references, not the active definitions.

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
- `k`
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
- `metallic_flake`

### `procedural_parameters`

- `variation_seed`
- `bump_scale`
- `bump_type`
- `noise_scale`
- `dirt`
- `wear`

The generator validates these records before writing JSON. Material application is intentionally cook-driven:

1. The Houdini UI calls `datagen/tools.py::set_material`, changing the HDA `material_id`.
2. Internal Python Script LOP `read_JSON_data` reads the HDA `dataset_path`, resolves that ID, and writes the record’s values onto the HDA.
3. Internal Python Script LOP `set_bump_type` converts none, stochastic, directional, and cellular strings to integer modes; unknown strings currently default to stochastic mode `1`.
4. Internal Python Script LOP `set_bump_cap` calculates the safety cap from finish and condition.

This path is verified working interactively and is intentionally compatible with future batching: a work item can set one material ID and cook the HDA. `datagen/tools.py::apply_material` is an older partial alternative and is not the active UI path.

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
| `stochastic` | Polished/matte/satin micro-breakup | Implemented; visual approval pending |
| `directional` | Brushed grain and aligned scratches | Implemented; visual approval pending |
| `cellular` | Hammered/pitted response | Implemented; visual approval pending |
| `cracked` | Asphalt macro cracking | Emitted by generator, no HDA branch |

The final selector must use one explicit mapping shared by JSON validation, HDA menu values, and shader switch inputs. Do not use an offset expression that relies on unconnected slots.

## Current bump implementation

The live production switch now selects the direct integer mode with all four intended inputs connected.

- Stochastic combines two object-space Fractal 3D noises at `noise_scale × 50` and `× 120`, octaves `3 / 2`, and weights `0.7 / 0.3`.
- Directional combines anisotropic UV noise at `noise_scale × (80, 8)` with stochastic breakup at weights `0.8 / 0.2`.
- Cellular combines object-space cellular noise at `noise_scale × 18` with stochastic breakup at weights `0.85 / 0.15`.
- The selected height is scaled by `bump_scale`, limited by `bump_cap`, and converted through MaterialX bump.

Implementation does not equal approval. The next gate is a fixed-camera comparison of the stress materials, followed by a small multi-camera pilot.

## Shader integration

Required behavior:

- JSON base color is modified only by controlled variation and dirt.
- JSON roughness is modified by variation, dirt, and wear without invalid ranges.
- Metalness, IOR, transmission, coat, and other identity parameters are not randomly altered.
- Bump modifies the normal response physically through MaterialX.
- Translucent and SSS materials remain visually distinguishable and stable.

Known current gaps:

- `subsurface`, `subsurface_color`, and `thin_walled` are not connected to the live Standard Surface result.
- `k` and `metallic_flake` are not consumed by the production graph.
- The treatment of `transmission_scatter` requires verification in Karma/MaterialX.

Any unsupported JSON parameter must be connected, explicitly removed from the v1 schema, or documented as metadata-only. Silent no-op parameters are not acceptable in the final library.

## Current RenderVars

- Beauty
- `P`
- `Pz`
- `N`
- Variation mask
- Dirt mask
- Wear mask
- Bump debug signal

Required checks before lock:

- confirm beauty alpha rather than assuming a separate Alpha RenderVar;
- document coordinate space and normalization for `P`, `Pz`, and `N`;
- identify bump output as scalar height or altered normal;
- decide whether BaseColor and Roughness are retained as auxiliary outputs.

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
