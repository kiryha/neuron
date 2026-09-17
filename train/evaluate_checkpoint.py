"""Render full-frame comparisons for a Material Hero checkpoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageDraw

from .data import MaterialBatchSource, PositionNormalization, load_material_library
from .model import MaterialHeroMLP
from .train_hero import choose_device, render_full_frame, save_preview


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument(
        "--material-id",
        action="append",
        help="Evaluate this material ID; repeat as needed. Defaults to training IDs.",
    )
    parser.add_argument(
        "--split",
        choices=("train", "validation", "test"),
        help="Evaluate a frozen split stored in the checkpoint metadata.",
    )
    parser.add_argument(
        "--metrics-only",
        action="store_true",
        help="Compute metrics without writing one PNG per material or a montage.",
    )
    parser.add_argument("--device", default="auto", choices=("auto", "cuda", "cpu"))
    parser.add_argument("--no-amp", action="store_true")
    parser.add_argument("--inference-chunk", type=int, default=65_536)
    parser.add_argument("--montage-width", type=int, default=768)
    parser.add_argument("--output-dir", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    device = choose_device(args.device)
    use_amp = device.type == "cuda" and not args.no_amp
    checkpoint_path = args.checkpoint.resolve()
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    metadata = checkpoint["metadata"]

    vocabularies = metadata["vocabularies"]
    vocabulary_sizes = {
        field: len(values) for field, values in vocabularies.items()
    }
    model = MaterialHeroMLP(vocabulary_sizes, **metadata["model"]).to(device)
    model.load_state_dict(checkpoint["model"])

    camera_root = Path(metadata["camera_root"])
    records = load_material_library(metadata["library_path"])
    normalization_json = metadata["position_normalization"]
    normalization = PositionNormalization(
        center=tuple(normalization_json["center"]),
        scale=float(normalization_json["scale"]),
    )
    if args.material_id and args.split:
        raise ValueError("Use either --material-id or --split, not both")
    material_ids = (
        args.material_id
        or (metadata["splits"][args.split] if args.split else None)
        or metadata["training_ids"]
    )
    source = MaterialBatchSource(
        camera_root,
        records,
        vocabularies,
        normalization,
        cache_items=max(1, min(len(material_ids), 8)),
    )

    evaluation_name = f"evaluation-step-{checkpoint['step']:06d}"
    if args.split:
        evaluation_name += f"-{args.split}"
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else checkpoint_path.parent / evaluation_name
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics: dict[str, float] = {}
    rows: list[tuple[str, Image.Image]] = []
    for material_id in material_ids:
        loss, target, prediction, coverage = render_full_frame(
            model,
            source,
            material_id,
            device,
            use_amp,
            args.inference_chunk,
        )
        metrics[material_id] = loss
        if not args.metrics_only:
            comparison_path = output_dir / f"{material_id}.png"
            save_preview(comparison_path, target, prediction, coverage)
            comparison = Image.open(comparison_path).convert("RGB")
            height = round(comparison.height * args.montage_width / comparison.width)
            comparison = comparison.resize(
                (args.montage_width, height), Image.Resampling.LANCZOS
            )
            rows.append((material_id, comparison))
        print(f"material={material_id} full_frame_l1={loss:.6f}", flush=True)

    if rows:
        label_height = 24
        montage = Image.new(
            "RGB",
            (
                args.montage_width,
                sum(image.height + label_height for _, image in rows),
            ),
            "black",
        )
        draw = ImageDraw.Draw(montage)
        y = 0
        for material_id, comparison in rows:
            draw.text((8, y + 4), f"{material_id} — target | prediction", fill="white")
            y += label_height
            montage.paste(comparison, (0, y))
            y += comparison.height
        montage.save(output_dir / "montage.png")

    loss_values = np.asarray(list(metrics.values()), dtype=np.float64)
    result = {
        "checkpoint": str(checkpoint_path),
        "step": checkpoint["step"],
        "mean_full_frame_l1": float(loss_values.mean()),
        "median_full_frame_l1": float(np.median(loss_values)),
        "p90_full_frame_l1": float(np.percentile(loss_values, 90)),
        "materials": metrics,
    }
    with (output_dir / "metrics.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
    print(f"mean_full_frame_l1={result['mean_full_frame_l1']:.6f}")
    print(f"output_dir={output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
