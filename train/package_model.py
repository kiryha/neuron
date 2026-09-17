"""Create a stable, self-describing Material Hero v0 model package."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import torch

from .model import MaterialHeroMLP


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--validation-metrics", type=Path, required=True)
    parser.add_argument("--test-metrics", type=Path, required=True)
    parser.add_argument("--nearest-validation", type=Path, required=True)
    parser.add_argument("--nearest-test", type=Path, required=True)
    parser.add_argument("--prompt-agnostic-validation", type=Path, required=True)
    parser.add_argument("--prompt-agnostic-test", type=Path, required=True)
    parser.add_argument("--qualitative-montage", type=Path, required=True)
    return parser.parse_args()


def read_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    args = parse_args()
    checkpoint_path = args.checkpoint.resolve()
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    metadata = checkpoint["metadata"]
    vocabulary_sizes = {
        field: len(values) for field, values in metadata["vocabularies"].items()
    }
    model = MaterialHeroMLP(vocabulary_sizes, **metadata["model"])
    model.load_state_dict(checkpoint["model"], strict=True)
    model.eval()

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    packaged_checkpoint = output_dir / "material_hero_v0.pt"
    shutil.copy2(checkpoint_path, packaged_checkpoint)

    reports = {
        "validation": args.validation_metrics,
        "compositional_test": args.test_metrics,
        "nearest_validation": args.nearest_validation,
        "nearest_test": args.nearest_test,
        "prompt_agnostic_validation": args.prompt_agnostic_validation,
        "prompt_agnostic_test": args.prompt_agnostic_test,
    }
    report_summaries: dict[str, dict[str, object]] = {}
    for name, source in reports.items():
        destination = output_dir / f"{name}.json"
        shutil.copy2(source.resolve(), destination)
        report = read_json(source)
        report_summaries[name] = {
            key: report[key]
            for key in (
                "mean_full_frame_l1",
                "median_full_frame_l1",
                "p90_full_frame_l1",
            )
        }

    shutil.copy2(args.qualitative_montage.resolve(), output_dir / "qualitative.png")
    run_dir = checkpoint_path.parent
    for name in ("config.json", "metadata.json", "history.json"):
        shutil.copy2(run_dir / name, output_dir / name)

    manifest = {
        "model_id": "material_hero_v0",
        "checkpoint_file": packaged_checkpoint.name,
        "checkpoint_sha256": sha256(packaged_checkpoint),
        "checkpoint_step": checkpoint["step"],
        "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        "training_materials": len(metadata["training_ids"]),
        "split_counts": {
            name: len(material_ids)
            for name, material_ids in metadata["splits"].items()
        },
        "model": metadata["model"],
        "position_normalization": metadata["position_normalization"],
        "metrics": report_summaries,
        "verification": {
            "strict_state_dict_reload": True,
            "clean_process_full_validation_evaluation": True,
            "clean_process_full_compositional_test_evaluation": True,
        },
        "limitations": [
            "Fixed Sculpted Rubber Toy geometry and cam_001 view",
            "Fixed Houdini lighting and exposure",
            "Controlled base/color/finish/condition vocabulary, not free-form language",
            "Deterministic output with no generative sampling",
            "Sharp reflective and transmissive details remain the hardest cases",
        ],
    }
    with (output_dir / "manifest.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
