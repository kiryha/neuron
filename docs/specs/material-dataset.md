# Material dataset specification

Status: **Dataset-v0 EXR and camera-record contract implemented; live final-quality stress-set pilot pending**

Last reviewed: 2026-09-04

## Purpose

Dataset v0 teaches a model to generate the fixed Material Hero's RGB appearance from material text and one fixed camera/surface context. The first implementation is intentionally a small solo-learning pipeline, not a production asset-management system.

Later datasets add multiple cameras and then multiple geometries without changing the basic directory hierarchy or render loop.

## Material catalog

The canonical generator is `datagen/materials.py`.

| Dimension | Current value |
| --- | ---: |
| Base materials | 56 |
| Finishes | 5 |
| Conditions | 4 |
| Optional colors | 10 |
| Categories | 4 |
| Valid combinations after filtering | 1,806 |

The repository authoring source is:

```text
datagen/data/neuron_library_prod.json
```

The Houdini tools offer two explicit material-library choices:

| UI name | File | Contents |
| --- | --- | ---: |
| `neuron_library_dev` | `datagen/data/neuron_library_dev.json` | Eight-material stress set |
| `neuron_library_prod` | `datagen/data/neuron_library_prod.json` | Full 1,806-material library |

DEV is listed first and is the default when either tool opens. In Datagen, **Build Materials Data** writes the stress subset for DEV and the full library for PROD; **Build Material Prompts** and **Reload Data** operate on the selected file. Applying a listed material sets `neuromat.dataset_path` to that file before setting `material_id`.

At dataset creation, copy that file unchanged into the dataset root using the same filename. The copied JSON is the material and label snapshot used by the render and later by the training loader. No checksum, renamed copy, material manifest, or duplicate material record is required.

The external `E:\Projects\neuron_data\neuron_library.json` remains the interactive eight-material stress subset and is not the production batch source.

## Stress set

The following eight materials cover the major material, transmission, coating, darkness, and bump paths:

1. `gold_polished_clean`
2. `car_paint_red_matte_dusty`
3. `iron_brushed_scratched`
4. `glass_polished_clean`
5. `glass_matte_clean`
6. `honey_satin_dusty`
7. `concrete_hammered_clean`
8. `rubber_black_polished_scratched`

Use these eight materials for the first automation pilot before rendering all 1,806 records.

## Dataset-v0 render contract

Every material render is one 1024 × 1024 multilayer EXR containing:

| Output | Meaning | Use |
| --- | --- | --- |
| Beauty `C.RGB` | Final material appearance | Model target |
| Beauty `C.A` | Material-independent object coverage/silhouette | Valid-pixel mask |
| `P` | World-space surface position | Model geometry input |
| `Nb` | Smooth, unbumped world-space surface normal; logical model input `N` | Model orientation input |
| `V` | Normalized world-space direction from the surface point toward the camera | Model view input |

The EXR does not include `Pz`, variation, dirt, wear, bump, BaseColor, Roughness, or other diagnostic AOVs. Variation, dirt, wear, and bump continue to affect Beauty; only their separate debug outputs are disabled.

`Nb` should match the smooth/interpolated geometry normal that can later be reproduced in Three.js. It is named `Nb` in the EXR to distinguish it from the bumped shading normal and becomes logical input `N` in the model. Do not use the normal after MaterialX bump. Do not switch to faceted `Ng` unless comparison with Three.js demonstrates that it is the intended convention.

Coverage is read from `C.A`; there is no separate Coverage AOV. MaterialX transmission is allowed to vary, but Standard Surface opacity remains `1`, so alpha describes geometry visibility rather than optical transmission. Do not introduce opacity maps, cutouts, holdouts, shadow-catcher alpha, or another feature that changes Beauty alpha without revisiting this contract. Fractional silhouette pixels are intentional antialiased coverage.

For one geometry and camera, the underlying `P`, `Nb`, `V`, and `C.A` fields are material-independent. Separately rendered pixels need not be bit-identical because stochastic subpixel sampling and antialiasing can differ, especially at silhouettes and fine visibility boundaries. Repeating the buffers in every EXR is intentional: it keeps each training example self-contained and avoids a separate shared-buffer system. At 1024 × 1024, simplicity is more important than eliminating this disk duplication.

Because these buffers are constant across dataset v0, the first model may learn to ignore them. They become informative when later datasets introduce camera and geometry variation.

## Fixed scene rules

- Geometry: Sculpted Rubber Toy at `/GEO/material_hero`.
- Camera: `cam_000`, using the existing `/cameras/camera` 28 mm perspective view.
- Resolution: 1024 × 1024.
- Aspect policy: the existing square-image `expandAperture` policy.
- Depth of field: disabled.
- Lighting, geometry transform, camera, samples, color configuration, and background remain fixed across every material.
- Material bump affects shading only and does not alter `Nb` or `C.A` Coverage.
- Final renders must not contain the Houdini Apprentice watermark.

Scene 006 resolves to 1024 × 1024 and its Indie pilot is unwatermarked. The visible `Enable Depth of Field` parameter is off, and read-only inspection confirms its underlying `enabledof` value is `0`. The authored camera f-stop `1.2` does not enable DOF while this master toggle is off.

## Dataset location and layout

Dataset root:

```text
E:\Projects\neuron_data\datasets
```

Dataset v0 layout:

```text
E:\Projects\neuron_data\datasets\
  material_hero_v0\
    neuron_library_prod.json
    sculpted_rubber_toy\
      cam_000\
        cam_000.json
        gold_polished_clean\
          render.exr
        iron_brushed_scratched\
          render.exr
        ...
```

Path meanings:

```text
{dataset}/{geometry_id}/{camera_id}/{material_id}/render.exr
```

- `sculpted_rubber_toy` is a `geometry_id`.
- `cam_000` is a `camera_id`.
- `gold_polished_clean` is a `material_id`.
- IDs, rather than semantic labels, are used in paths.

The material-library snapshot and path structure remain the training-data index. Dataset v0 has no `dataset.json`, frame manifest, geometry record, light record, schema record, checksum file, or validation report. Each camera folder additionally contains one small `{camera_id}.json` used to reproduce the training view in Three.js; it is not required for locating training samples.

The versioned HIP scene and HDA remain in the Houdini project rather than being copied into the dataset. They must not be changed after the full render starts. If the scene, HDA, output contract, or material library changes, create a new dataset directory such as `material_hero_v0_1` instead of mixing incompatible renders.

## Render automation

The implementation is `datagen/datarender.py`. It uses ordinary sequential Python rather than TOPs/PDG and never saves the loaded HIP file. Camera-dome creation and the minimal dataset render loop are implemented.

### Camera-dome stage

The user-authored `datagen/ui/ui_datarender.ui` provides camera count, focal length in millimeters, approximate object size in meters, and a frame-margin multiplier. Its **Create Camera Dome** button creates an unconnected Camera Dome subnet in `/stage`; the user connects the subnet manually.

Inside the subnet, Camera LOPs are connected sequentially between the subnet input and output. They author `/cameras/cam_000`, `/cameras/cam_001`, and so on. Positions use a full-sphere Fibonacci distribution, every camera looks at world origin, and every camera uses the requested focal length.

Object size is a simple framing input, not measured geometry. Camera distance uses the fixed 20.955 mm aperture and is multiplied by the UI frame margin: `1.0` adds no extra space and the default `1.25` moves cameras 25% farther away. Values below `1.0` are rejected. The tool does not inspect geometry bounds, find or update existing cameras, connect itself to the root network, change Karma Render Settings, or render images.

### Dataset render stage

The **Material Library JSON** combo offers `neuron_library_dev` and `neuron_library_prod`, with DEV selected by default. When **Render Dataset** is pressed, the tool sets `/stage/neuromat.dataset_path` to the selected repository JSON, reads every material ID from it, and copies that JSON into the selected dataset directory if a same-named snapshot is not already present.

At render start, the tool checks `{geometry_id}/{camera_id}/{camera_id}.json` for every selected camera. An existing file is left unchanged. If it is missing, Datarender reads the cooked USD camera and cooked Render Settings resolution. If the Render Settings LOP does not expose a cooked stage, it falls back to the matching look-at Camera LOP's position, target, lens, and aperture plus the Render Settings resolution parameters. This fallback intentionally supports the simple cameras created by Datarender and rejects a non-look-at camera. The tool writes:

```json
{
  "camera_id": "cam_000",
  "position": [-1.0, 1.0, 2.0],
  "target": [-0.6, 0.8, 1.1],
  "up": [0.1, 0.97, -0.2],
  "focal_length_mm": 28.0,
  "horizontal_aperture_mm": 20.955,
  "resolution": [1024, 1024]
}
```

`position`, `target`, and `up` are world-space values. `target` is a point one world unit along the camera's cooked forward direction; it is suitable for Three.js `lookAt` and does not claim to preserve the original Houdini look-at control point. The lens values are converted from USD camera units to millimeters. No camera matrix, USD prim path, clipping range, schema version, or checksum is stored.

When **Single Camera** is enabled, the camera-name field supplies a bare name such as `cam_001`, which resolves to `/cameras/cam_001`. When it is disabled, the tool dynamically reads and sorts every Camera LOP directly inside `/stage/camera_dome` and uses each node's authored primitive path.

Multiple geometry switching is not implemented. The tool always renders whatever geometry is currently connected to `neuromat`; the geometry-name field is used only as the output folder ID, regardless of the Single Geometry checkbox.

For every selected camera and sorted material ID, the tool:

1. Sets the Karma Render Settings camera.
2. Sets `/stage/neuromat.material_id`.
3. Sets the output path to `{geometry_id}/{camera_id}/{material_id}/render.exr`.
4. Invokes `/stage/usdrender_rop1` for the current frame.

Pressing **Render Dataset** uses Houdini's native interrupt operation. Before rendering, the tool counts existing material folders, prints `RESUME {completed}/{total}` when applicable, and queues only missing folders. During an active USD render, Houdini may replace the outer progress display with its own indeterminate `Rendering Image` bar and **Interrupt** button. The blocking Render ROP prevents a separate Qt progress window from repainting reliably, so graphical whole-dataset percentage is intentionally not provided.

The native window title is controlled internally by Houdini and remains **Interrupt**. Pressing **Interrupt** may stop the active `husk`; if it finishes the current image first, the queued cancellation is detected before another dataset item is completed.

The console prints `Dataset Render Started...` before iteration begins and `Dataset Render Complete!` only after every selected item has rendered or been skipped successfully. Cancellation instead prints `Dataset Render Interrupted!` and reminds the user that the last rendered material folder may need to be inspected or deleted before resuming.

The camera JSON is for initializing the matching Three.js view. It is not fed to the model: `P`, `Nb`, `V`, and `C.A` already contain the geometry and view context required for training. The implementation has no job database, manifest, retry manager, checksum generation, or automatic image validation.

## Resume after interruption

Before rendering a material, check whether its material folder exists:

```text
{dataset}/{geometry_id}/{camera_id}/{material_id}/
```

- Folder exists: skip it.
- Folder does not exist: render it.
- To rerender a material: manually delete that material folder and run the script again.

This intentionally accepts the possibility that a crash leaves an incomplete folder that is skipped later. The user will inspect and correct those cases manually.

On restart, Datarender scans all requested camera/material folders before opening the progress dialog. Existing folders count as completed progress and are summarized once in the console instead of printing one `SKIP` line per material.

## Training lookup

The training loader does not need a frame manifest:

1. Scan the geometry/camera/material folders for `render.exr`.
2. Read `material_id` from the folder name.
3. Look up the compact prompt and semantic label in the copied `neuron_library_prod.json`.
4. Read target RGB from `C.RGB`, Coverage from `C.A`, and geometry inputs from `P`, `Nb`, and `V`.

The training loader does not need `{camera_id}.json`. The web application copies the chosen camera record unchanged to `public/cameras/material_hero/{camera_id}.json` and uses it to initialize the reference Three.js camera.

Train/validation/test splits are created and stored by the training implementation, not by Houdini render automation.

## Dataset sequence

### Dataset v0 — fixed view

- 1,806 materials.
- One Sculpted Rubber Toy.
- One fixed camera.
- 1024 × 1024.

### Dataset v1 — multi-view hero

- Add camera folders beside `cam_000`.
- Keep the same material-folder and EXR contract.
- Camera count is chosen after the v0 model and a small multi-view pilot.

### Dataset v2 — multi-view and multi-geometry

- Add geometry folders beside `sculpted_rubber_toy`.
- Keep the same camera/material nesting and EXR contract.
- Geometry normalization and the test-geometry set are decided before that render.

## Manual acceptance checks

Before the full v0 batch:

- Render the eight-material stress set through `datarender.py`.
- Run the final approval pilot with the exact production resolution, samples, camera, lighting, and AOV settings; a low-quality automation test is not sufficient for look approval.
- Open representative EXRs and confirm 1024 × 1024 Beauty RGBA, `P`, `Nb`, and `V`.
- Confirm `Nb` is unbumped and `C.A` Coverage is identical for opaque and transmissive stress materials.
- Confirm DOF is absent.
- Confirm the output has no watermark.
- Confirm the selected camera folder contains a readable `{camera_id}.json` with the expected lens and resolution.
- Interrupt and restart the pilot once to verify folder-based skipping.
- Do not reuse low-resolution pilot material folders for the production render because folder-existence skipping will preserve them.

After the full render, manually check the expected material count and inspect representative materials before starting training.
