# Resume Houdini work

Use this runbook when returning to Material Hero look-dev after a break. The current checkpoint is always maintained in [STATUS.md](../STATUS.md).

## 1. Confirm the active artifacts

Do not begin from the older files stored in the repository.

- Project root: `C:\Users\kko8\OneDrive\projects\neuron\prod\3D`
- Active scene: `scenes\material_hero_005.hipnc`
- Active HDA: `hda\lop_KKO8.neuromat.1.2.hdanc`
- Material JSON: `E:\Projects\neuron_data\neuron_library.json`

Before editing, confirm file modification times and check [STATUS.md](../STATUS.md) for a newer version.

## 2. Preserve a recoverable state

Before changing the HDA graph:

1. Save a scene backup or increment the scene version.
2. Back up or increment the HDA definition.
3. Record the current material ID and render settings.
4. Do not overwrite the last known working HDA backup.

Houdini scenes and HDAs are binary and live outside Git, so the backup is part of the project history rather than a convenience.

## 3. Verify the scene before look-dev

Expected top-level LOP nodes include:

- `GEO`
- `domelight2`
- `camera`
- `karmarendersettings`
- `usdrender_rop1`
- `neuromat`

Expected baseline:

- HDA type `KKO8::neuromat::1.2` or its deliberate successor
- Sculpted Rubber Toy visible
- 28 mm test camera
- studio HDRI at exposure `-0.5`
- Karma XPU
- 1024 × 1024 candidate dataset render
- 128 path-traced samples
- denoiser off
- depth of field disabled for dataset renders

If these differ intentionally, update the status and dataset specification before using the result as a new baseline.

## 4. Confirm geometry support signals

The displayed hero should contain:

- point `P`;
- point `ao`;
- point `convex_macro` and `concave_macro`;
- point `convex_micro` and `concave_micro`;
- vertex `uv`.

Inspect masks on the final render geometry, not only on a lower-resolution intermediate mesh. Dirt and wear depend on these attributes matching the shaded surface.

## 5. Confirm the material library mode

The current Houdini UI method `build_materials_data()` writes the eight-material stress subset. Calling `BuildMaterialsData().generate()` without a subset writes the full 1,806-record library to the same external JSON path.

Before pressing either action:

- know which library size is intended;
- preserve the previous JSON if it is needed for comparison;
- do not assume the file contains the full library merely because it is named `neuron_library.json`.

After generation, build labels and validate every record. Existing labels are skipped unless overwrite is enabled.

Selecting an item in the Houdini UI intentionally changes only `material_id`. Cooking the HDA runs its internal `read_JSON_data`, `set_bump_type`, and `set_bump_cap` Python Script LOPs, which update the material parameters. This is the expected interactive path and the planned basis for batching.

The UI helper `Datagen.set_material()` lives in `datagen/datagen.py` and only changes the HDA `material_id`. The obsolete partial `datagen/tools.py` module has been removed.

## 6. Validate the current bump implementation

The production switch now directly maps none, stochastic, directional, and cellular, and all four inputs are connected. The next task is visual approval rather than branch construction.

Recommended order:

1. Confirm direct mode selection with the bump diagnostic.
2. Test stochastic using `rubber_black_polished_scratched` and polished glass/gold cases.
3. Test directional using `iron_brushed_scratched`.
4. Test cellular using `concrete_hammered_clean`.
5. Compare all results under one fixed camera and lighting setup.
6. Change one parameter group at a time if tuning is required and save comparable renders.
7. Include asphalt in the full-library scan and judge its stochastic breakup before release.

## 7. Validate the complete shader contract

After bump branches:

1. Verify variation remains subtle and does not read as dirt.
2. Verify dirt follows AO/concavity without becoming a shadow duplicate.
3. Verify wear follows convex/exposed areas and remains distinct from dirt.
4. Verify bump changes highlight response without changing silhouette.
5. Verify the implemented SSS, subsurface-color, and thin-wall references. Treat `k` and metallic flake as metadata-only; verify or explicitly classify transmission-scatter behavior.
6. Clamp physical ranges without silently flattening intended material differences.

## 8. Stress-set render order

Use one fixed camera and lighting setup:

1. `gold_polished_clean`
2. `car_paint_red_matte_dusty`
3. `iron_brushed_scratched`
4. `glass_polished_clean`
5. `glass_matte_clean`
6. `honey_satin_dusty`
7. `concrete_hammered_clean`
8. `rubber_black_polished_scratched`

For every material inspect:

- beauty;
- material-independent Coverage;
- world `P`, smooth unbumped world `N`, and world `V`;
- expected branch selection;
- prompt/visual agreement.

Use a contact sheet when possible so differences are judged under the same view and display transform.

## 9. Lock RenderVars and color

Before camera automation:

- disable camera depth of field;
- keep only Beauty, world `P`, smooth unbumped world `N`, world `V`, and material-independent Coverage;
- remove `Pz`, variation, dirt, wear, bump, BaseColor, Roughness, and other debug RenderVars from dataset output;
- confirm the EXR channels and display interpretation manually with the eight-material pilot.

Do not change these definitions after starting the full dataset.

## 10. End-of-session handoff

Before closing Houdini:

1. Save the HDA and scene using deliberate versions.
2. Record the last successful and failed material/render.
3. Record exact parameter changes and whether they were only tests.
4. Update [STATUS.md](../STATUS.md).
5. Append a concise entry to [CHANGELOG.md](../CHANGELOG.md).
6. Update [`neuromat-hda.md`](../specs/neuromat-hda.md) if the interface or branch contract changed.

## Final-render warning

Current `.hipnc`/`.hdanc` development assets and observed Apprentice renders are noncommercial/watermarked. Installing an Indie license is not sufficient by itself: loading a noncommercial scene or HDA can downgrade an Indie session. Convert or rebuild the active files as `.hiplc`/`.hdalc`, restart in Indie mode, and prove the exact batch path with an unwatermarked pilot before launching final training renders.
