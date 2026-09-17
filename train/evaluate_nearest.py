"""Evaluate a deterministic nearest-training-material image baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .data import MaterialRecord, load_material_library, make_material_splits
from .exr import read_exr_parts


FIELD_WEIGHTS = {"base": 4, "color": 2, "finish": 1, "condition": 1}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("camera_root", type=Path)
    parser.add_argument("--split", choices=("validation", "test"), required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def categorical_distance(left: MaterialRecord, right: MaterialRecord) -> int:
    return sum(
        FIELD_WEIGHTS[field]
        for field in FIELD_WEIGHTS
        if left.tokens()[field] != right.tokens()[field]
    )


def nearest_training_id(
    target: MaterialRecord,
    training_ids: list[str],
    records: dict[str, MaterialRecord],
) -> str:
    return min(
        training_ids,
        key=lambda material_id: (
            categorical_distance(target, records[material_id]),
            material_id,
        ),
    )


def full_frame_l1(target: np.ndarray, prediction: np.ndarray) -> float:
    coverage = target[..., 3:4]
    error = np.abs(prediction[..., :3] - target[..., :3]) * coverage
    return float(error.sum() / max(float(coverage.sum()) * 3.0, 1e-8))


def main() -> int:
    args = parse_args()
    camera_root = args.camera_root.resolve()
    library_path = camera_root.parents[1] / "neuron_library_prod.json"
    records = load_material_library(library_path)
    splits = make_material_splits(records, args.seed)

    results: dict[str, dict[str, object]] = {}
    losses: list[float] = []
    for index, material_id in enumerate(splits[args.split], start=1):
        nearest_id = nearest_training_id(records[material_id], splits["train"], records)
        target = read_exr_parts(camera_root / material_id / "render.exr")["C"]
        prediction = read_exr_parts(camera_root / nearest_id / "render.exr")["C"]
        loss = full_frame_l1(target, prediction)
        losses.append(loss)
        results[material_id] = {
            "nearest_training_material": nearest_id,
            "categorical_distance": categorical_distance(
                records[material_id], records[nearest_id]
            ),
            "full_frame_l1": loss,
        }
        if index % 25 == 0 or index == len(splits[args.split]):
            print(f"evaluated={index}/{len(splits[args.split])}", flush=True)

    values = np.asarray(losses, dtype=np.float64)
    report = {
        "baseline": "nearest training material",
        "field_weights": FIELD_WEIGHTS,
        "split": args.split,
        "count": len(losses),
        "mean_full_frame_l1": float(values.mean()),
        "median_full_frame_l1": float(np.median(values)),
        "p90_full_frame_l1": float(np.percentile(values, 90)),
        "materials": results,
    }
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    print(json.dumps({key: value for key, value in report.items() if key != "materials"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
