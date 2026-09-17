# Material Hero training

This directory contains the fixed-view Material Hero v0 training pipeline. It
predicts linear foreground RGB from world-space `P`, smooth `Nb`, view direction
`V`, and controlled base/color/finish/condition tokens.

Run commands from the repository root with the project `.venv` active, or call
`.venv\Scripts\python.exe` explicitly.

## Dataset validation

```powershell
.venv\Scripts\python.exe -m train.validate_dataset `
  E:\Projects\neuron_data\datasets\material_hero_v0\sculpted_rubber_toy\cam_001
```

Validation fully decodes every expected multipart EXR and checks the 1024 × 1024
`C`, `P`, `V`, and `Nb` contract. A folder count alone is not sufficient.

## Training stages

Use a one-material run to prove intentional overfitting, then the eight-material
stress set, and only then a full-library run. Full training uses deterministic
material-level splits and epoch scheduling. `--updates-per-material-batch`
amortizes large EXR decoding over several random pixel batches.

```powershell
.venv\Scripts\python.exe -m train.train_hero CAMERA_ROOT `
  --epochs 10 `
  --updates-per-material-batch 5 `
  --materials-per-step 4 `
  --pixels-per-material 4096 `
  --run-name full-v0-001
```

Repeat `--preview-material-id ID` to select several held-out materials. Their
mean full-frame L1 chooses `best.pt`.

## Run artifacts

- `config.json`: exact command configuration.
- `metadata.json`: vocabularies, frozen splits, normalization, model shape, and IDs.
- `history.json`: per-step sampled loss and periodic full-frame validation loss.
- `preview_*.png`: target on the left and prediction on the right.
- `best.pt`: checkpoint with the lowest configured preview-set mean.
- `latest.pt`: checkpoint at the final completed step.

Run directories under `train/outputs/` are intentionally ignored by Git.

## Checkpoint evaluation

Evaluate a frozen split without writing hundreds of large PNG files:

```powershell
.venv\Scripts\python.exe -m train.evaluate_checkpoint `
  train\outputs\full-v0-001\best.pt `
  --split validation `
  --metrics-only
```

For a compact qualitative comparison, pass a short repeated list of
`--material-id` arguments and omit `--metrics-only`.

The deterministic nearest-material baseline is evaluated separately:

```powershell
.venv\Scripts\python.exe -m train.evaluate_nearest CAMERA_ROOT `
  --split validation `
  --output train\outputs\full-v0-001\nearest-validation.json
```

Use `--prompt-agnostic` with `train_hero` to train the geometry-only ablation.
It uses the same architecture family and schedule but removes all material
embeddings.
