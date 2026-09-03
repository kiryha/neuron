# Render a Material Hero dataset

Use this runbook after the HDA and dataset scene match the accepted contract. Dataset v0 intentionally relies on a small Python script and manual inspection.

## 1. Freeze the inputs

Use the versioned Houdini scene and HDA selected for the render. Do not modify them after the full batch starts.

Create:

```text
E:\Projects\neuron_data\datasets\material_hero_v0
```

Copy `datagen/data/neuron_library_prod.json` unchanged to the dataset root as `neuron_library_prod.json`. Point `neuromat.dataset_path` at this copied snapshot for the render. No checksum or renamed source copy is required.

## 2. Confirm the scene contract

Before rendering, confirm:

- 1024 × 1024 resolution;
- one fixed 28 mm camera for v0;
- depth of field disabled;
- fixed Sculpted Rubber Toy geometry and studio lighting;
- Karma XPU and the accepted sample count;
- Beauty RGBA, world `P`, smooth unbumped world `Nb`, and world `V` only; use `C.A` as material-independent Coverage;
- no `Pz`, variation, dirt, wear, bump, BaseColor, Roughness, or other debug AOVs;
- the active Indie `.hiplc` scene and `.otllc` HDA produce no watermark.

## 3. Implement and run the eight-material pilot

`datagen/datarender.py` is not implemented yet. Define and implement its functionality in the user-directed stages before adding concrete commands to this runbook. The tool must use Houdini's `hython`, render sequentially, and never edit or save the HIP file.

After the tool is implemented and scene preflight passes, run the eight-material pilot using the documented command. Do not run the complete 1,806-material batch until the pilot is approved.

Expected path example:

```text
material_hero_v0\sculpted_rubber_toy\cam_000\gold_polished_clean\render.exr
```

Manually open representative EXRs and confirm resolution, channels, prompt/material agreement, unbumped `Nb`, material-independent `C.A` Coverage, absence of DOF, and absence of a watermark. Compare opaque and strongly transmissive alpha images at the same camera.

Interrupt and restart the pilot once. Existing material folders should be skipped.

## 4. Estimate the full run

Use the pilot to estimate approximate time per material and total disk usage for all 1,806 records. No formal report is required.

## 5. Run the complete dataset

- Use the copied `neuron_library_prod.json`.
- Run the complete sequential batch with the command established during staged `datarender.py` implementation.
- Existing `{geometry_id}/{camera_id}/{material_id}` folders are skipped.
- To rerender a material, delete its folder manually and rerun the script.
- Do not change the scene, HDA, JSON snapshot, camera, lighting, render settings, or output channels during the run.

The folder-existence resume rule deliberately performs no file validation. If Houdini crashes after creating a folder, inspect that folder manually and delete it if the render is incomplete.

## 6. Finish the dataset

After rendering:

- compare the number of material folders with the 1,806 JSON records;
- manually inspect representative metal, dielectric, organic, translucent, bump, dirt, and wear results;
- keep the copied JSON beside the renders;
- leave training splits and any training-specific conversion to the training implementation.

Update [STATUS.md](../STATUS.md), [CHANGELOG.md](../CHANGELOG.md), and [ROADMAP.md](../ROADMAP.md) before moving to model training.
