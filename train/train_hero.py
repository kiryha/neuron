"""Train the first coordinate-conditioned Material Hero RGB baseline."""

from __future__ import annotations

import argparse
import json
import random
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from .data import (
    MaterialBatchSource,
    PositionNormalization,
    build_vocabularies,
    encode_record,
    load_material_library,
    make_material_splits,
    normalize_directions,
)
from .exr import read_exr_parts
from .loss import masked_l1
from .model import MaterialHeroMLP


STRESS_SET = (
    "gold_polished_clean",
    "car_paint_red_matte_dusty",
    "iron_brushed_scratched",
    "glass_polished_clean",
    "glass_matte_clean",
    "honey_satin_dusty",
    "concrete_hammered_clean",
    "rubber_black_polished_scratched",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("camera_root", type=Path)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--material-id",
        action="append",
        help="Train only on this material ID; repeat to select several.",
    )
    selection.add_argument(
        "--stress-set",
        action="store_true",
        help="Train on the canonical eight-material stress set.",
    )
    parser.add_argument("--steps", type=int, default=10_000)
    parser.add_argument("--materials-per-step", type=int, default=4)
    parser.add_argument("--pixels-per-material", type=int, default=4_096)
    parser.add_argument("--width", type=int, default=256)
    parser.add_argument("--blocks", type=int, default=6)
    parser.add_argument("--bands", type=int, default=6)
    parser.add_argument("--embedding-dim", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-6)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--cache-items", type=int, default=4)
    parser.add_argument("--log-every", type=int, default=10)
    parser.add_argument("--preview-every", type=int, default=100)
    parser.add_argument("--checkpoint-every", type=int, default=500)
    parser.add_argument("--inference-chunk", type=int, default=65_536)
    parser.add_argument("--reference-material", default="gold_polished_clean")
    parser.add_argument("--device", default="auto", choices=("auto", "cuda", "cpu"))
    parser.add_argument("--no-amp", action="store_true")
    parser.add_argument("--run-name")
    parser.add_argument("--output-root", type=Path, default=Path("train/outputs"))
    return parser.parse_args()


def choose_device(requested: str) -> torch.device:
    if requested == "auto":
        requested = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(requested)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but torch.cuda.is_available() is false")
    return device


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def to_torch_batch(
    batch: dict[str, np.ndarray | dict[str, np.ndarray]],
    device: torch.device,
) -> dict[str, torch.Tensor | dict[str, torch.Tensor]]:
    converted: dict[str, torch.Tensor | dict[str, torch.Tensor]] = {}
    for key in ("P", "N", "V", "rgb", "coverage"):
        converted[key] = torch.from_numpy(batch[key]).to(device)
    converted["tokens"] = {
        field: torch.from_numpy(values).to(device)
        for field, values in batch["tokens"].items()
    }
    return converted


def linear_to_srgb(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, 0.0, None)
    return np.where(
        values <= 0.0031308,
        values * 12.92,
        1.055 * np.power(values, 1.0 / 2.4) - 0.055,
    )


def save_preview(
    output_path: Path,
    target: np.ndarray,
    prediction: np.ndarray,
    coverage: np.ndarray,
) -> None:
    coverage = np.clip(coverage, 0.0, 1.0)
    target_display = linear_to_srgb(target) * coverage
    prediction_display = linear_to_srgb(prediction) * coverage
    comparison = np.concatenate([target_display, prediction_display], axis=1)
    encoded = (np.clip(comparison, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)
    Image.fromarray(encoded, mode="RGB").save(output_path)


def render_full_frame(
    model: MaterialHeroMLP,
    source: MaterialBatchSource,
    material_id: str,
    device: torch.device,
    use_amp: bool,
    chunk_size: int,
) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    parts = source.cache.get(source.exr_path(material_id))
    beauty = parts["C"]
    coverage = beauty[..., 3:4]
    visible = np.flatnonzero(coverage.reshape(-1) > 0)
    prediction = np.zeros_like(beauty[..., :3], dtype=np.float32).reshape(-1, 3)

    record = source.records[material_id]
    encoded = encode_record(record, source.vocabularies)
    token_ids = {
        field: torch.tensor([value], device=device, dtype=torch.long)
        for field, value in encoded.items()
    }

    model.eval()
    with torch.inference_mode():
        for start in range(0, visible.size, chunk_size):
            indices = visible[start : start + chunk_size]
            positions = source.position_normalization.apply(
                parts["P"].reshape(-1, 3)[indices]
            )
            normals = normalize_directions(parts["Nb"].reshape(-1, 3)[indices])
            views = normalize_directions(parts["V"].reshape(-1, 3)[indices])
            p = torch.from_numpy(positions[None]).to(device)
            n = torch.from_numpy(normals[None]).to(device)
            v = torch.from_numpy(views[None]).to(device)
            with torch.autocast(
                device_type=device.type,
                dtype=torch.float16,
                enabled=use_amp,
            ):
                chunk = model(p, n, v, token_ids)
            prediction[indices] = chunk[0].float().cpu().numpy()

    prediction = prediction.reshape(beauty.shape[0], beauty.shape[1], 3)
    target = beauty[..., :3]
    error = np.abs(prediction - target) * coverage
    loss = float(error.sum() / max(float(coverage.sum()) * 3.0, 1e-8))
    model.train()
    return loss, target, prediction, coverage


def save_checkpoint(
    path: Path,
    model: MaterialHeroMLP,
    optimizer: torch.optim.Optimizer,
    scaler: torch.amp.GradScaler,
    step: int,
    best_preview_loss: float,
    metadata: dict[str, object],
) -> None:
    torch.save(
        {
            "step": step,
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "scaler": scaler.state_dict(),
            "best_preview_loss": best_preview_loss,
            "metadata": metadata,
        },
        path,
    )


def main() -> int:
    args = parse_args()
    if args.steps <= 0 or args.pixels_per_material <= 0 or args.materials_per_step <= 0:
        raise ValueError("steps, pixels-per-material, and materials-per-step must be positive")

    seed_everything(args.seed)
    camera_root = args.camera_root.resolve()
    dataset_root = camera_root.parents[1]
    library_path = dataset_root / "neuron_library_prod.json"
    records = load_material_library(library_path)
    vocabularies = build_vocabularies(records.values())
    splits = make_material_splits(records, args.seed)

    if args.material_id:
        training_ids = list(args.material_id)
        selection_name = "materials"
    elif args.stress_set:
        training_ids = list(STRESS_SET)
        selection_name = "stress"
    else:
        training_ids = splits["train"]
        selection_name = "full"

    unknown = sorted(set(training_ids) - records.keys())
    if unknown:
        raise ValueError(f"Unknown material IDs: {unknown}")
    missing = [
        material_id
        for material_id in training_ids
        if not (camera_root / material_id / "render.exr").is_file()
    ]
    if missing:
        raise FileNotFoundError(f"Missing training EXRs: {missing[:10]}")

    reference_path = camera_root / args.reference_material / "render.exr"
    position_normalization = PositionNormalization.from_parts(
        read_exr_parts(reference_path)
    )

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_name = args.run_name or f"{timestamp}-{selection_name}"
    output_dir = args.output_root.resolve() / run_name
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Refusing to overwrite non-empty run directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    device = choose_device(args.device)
    use_amp = device.type == "cuda" and not args.no_amp
    vocabulary_sizes = {
        field: len(values) for field, values in vocabularies.items()
    }
    model_config = {
        "bands": args.bands,
        "embedding_dim": args.embedding_dim,
        "width": args.width,
        "blocks": args.blocks,
    }
    model = MaterialHeroMLP(vocabulary_sizes, **model_config).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)
    source = MaterialBatchSource(
        camera_root,
        records,
        vocabularies,
        position_normalization,
        cache_items=args.cache_items,
    )

    preview_material = training_ids[0]
    metadata: dict[str, object] = {
        "camera_root": str(camera_root),
        "library_path": str(library_path),
        "training_ids": training_ids,
        "splits": splits,
        "vocabularies": vocabularies,
        "position_normalization": position_normalization.to_json(),
        "model": model_config,
        "seed": args.seed,
    }
    config = vars(args).copy()
    config["camera_root"] = str(camera_root)
    config["output_root"] = str(args.output_root.resolve())
    with (output_dir / "config.json").open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)
    with (output_dir / "metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)

    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    print(f"run_dir={output_dir}")
    print(f"device={device} amp={use_amp}")
    if device.type == "cuda":
        print(f"gpu={torch.cuda.get_device_name(device)}")
    print(f"parameters={parameter_count}")
    print(f"training_materials={len(training_ids)}")
    print(f"preview_material={preview_material}")
    print(f"position_normalization={asdict(position_normalization)}")

    rng = np.random.default_rng(args.seed)
    history: list[dict[str, float | int]] = []
    best_preview_loss = float("inf")
    started = time.perf_counter()
    model.train()

    for step in range(1, args.steps + 1):
        chosen = rng.choice(
            training_ids,
            size=args.materials_per_step,
            replace=len(training_ids) < args.materials_per_step,
        ).tolist()
        numpy_batch = source.sample_batch(chosen, args.pixels_per_material, rng)
        batch = to_torch_batch(numpy_batch, device)

        optimizer.zero_grad(set_to_none=True)
        with torch.autocast(
            device_type=device.type,
            dtype=torch.float16,
            enabled=use_amp,
        ):
            prediction = model(batch["P"], batch["N"], batch["V"], batch["tokens"])
            loss = masked_l1(prediction, batch["rgb"], batch["coverage"])

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        loss_value = float(loss.detach().cpu())
        history.append({"step": step, "train_loss": loss_value})
        if step == 1 or step % args.log_every == 0:
            elapsed = time.perf_counter() - started
            print(
                f"step={step}/{args.steps} train_l1={loss_value:.6f} "
                f"elapsed_seconds={elapsed:.1f}",
                flush=True,
            )

        if step == 1 or step % args.preview_every == 0 or step == args.steps:
            preview_loss, target, preview, coverage = render_full_frame(
                model,
                source,
                preview_material,
                device,
                use_amp,
                args.inference_chunk,
            )
            history[-1]["preview_l1"] = preview_loss
            save_preview(
                output_dir / f"preview_{step:06d}.png",
                target,
                preview,
                coverage,
            )
            print(f"step={step} preview_l1={preview_loss:.6f}", flush=True)
            if preview_loss < best_preview_loss:
                best_preview_loss = preview_loss
                save_checkpoint(
                    output_dir / "best.pt",
                    model,
                    optimizer,
                    scaler,
                    step,
                    best_preview_loss,
                    metadata,
                )

        if step % args.checkpoint_every == 0 or step == args.steps:
            save_checkpoint(
                output_dir / "latest.pt",
                model,
                optimizer,
                scaler,
                step,
                best_preview_loss,
                metadata,
            )
            with (output_dir / "history.json").open("w", encoding="utf-8") as handle:
                json.dump(history, handle, indent=2)

    print(f"training_complete best_preview_l1={best_preview_loss:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
