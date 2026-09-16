"""Full-read validation for a Material Hero camera directory."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

try:
    from .exr import ExrReadError, read_exr_parts
except ImportError:  # Allow direct execution with Houdini's hython.
    from exr import ExrReadError, read_exr_parts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "camera_root",
        type=Path,
        help="Directory containing cam_###.json and one folder per material.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Validate only the first N sorted material IDs.",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=100,
        help="Print progress after this many files.",
    )
    return parser.parse_args()


def validate(camera_root: Path, limit: int | None, progress_every: int) -> int:
    camera_root = camera_root.resolve()
    dataset_root = camera_root.parents[1]
    library_path = dataset_root / "neuron_library_prod.json"
    camera_json = camera_root / f"{camera_root.name}.json"

    if not library_path.is_file():
        raise FileNotFoundError(f"Missing dataset library snapshot: {library_path}")
    if not camera_json.is_file():
        raise FileNotFoundError(f"Missing camera record: {camera_json}")

    with library_path.open("r", encoding="utf-8") as handle:
        library = json.load(handle)

    expected_ids = sorted(library)
    actual_ids = sorted(path.name for path in camera_root.iterdir() if path.is_dir())
    missing_ids = sorted(set(expected_ids) - set(actual_ids))
    unexpected_ids = sorted(set(actual_ids) - set(expected_ids))

    print(f"dataset_root={dataset_root}")
    print(f"camera_root={camera_root}")
    print(f"expected_materials={len(expected_ids)}")
    print(f"material_folders={len(actual_ids)}")
    print(f"missing_materials={len(missing_ids)}")
    print(f"unexpected_materials={len(unexpected_ids)}")

    failures: list[tuple[str, str]] = []
    if missing_ids:
        failures.extend((material_id, "missing material folder") for material_id in missing_ids)
    if unexpected_ids:
        failures.extend((material_id, "unexpected material folder") for material_id in unexpected_ids)

    selected_ids = expected_ids if limit is None else expected_ids[:limit]
    started = time.perf_counter()
    for index, material_id in enumerate(selected_ids, start=1):
        exr_path = camera_root / material_id / "render.exr"
        if not exr_path.is_file() or exr_path.stat().st_size == 0:
            failures.append((material_id, "missing or empty render.exr"))
            continue
        try:
            parts = read_exr_parts(exr_path, quiet_errors=True)
            if parts["C"].shape != (1024, 1024, 4):
                raise ExrReadError(
                    f"Beauty has shape {parts['C'].shape}; expected (1024, 1024, 4)"
                )
            for part_name in ("P", "V", "Nb"):
                if parts[part_name].shape != (1024, 1024, 3):
                    raise ExrReadError(
                        f"{part_name} has shape {parts[part_name].shape}; "
                        "expected (1024, 1024, 3)"
                    )
        except (OSError, ExrReadError) as exc:
            failures.append((material_id, str(exc)))

        if progress_every > 0 and (index % progress_every == 0 or index == len(selected_ids)):
            elapsed = time.perf_counter() - started
            print(
                f"validated={index}/{len(selected_ids)} failures={len(failures)} "
                f"elapsed_seconds={elapsed:.1f}",
                flush=True,
            )

    print(f"validation_failures={len(failures)}")
    for material_id, detail in failures:
        print(f"FAIL {material_id}: {detail}")
    return 1 if failures else 0


def main() -> int:
    args = parse_args()
    try:
        return validate(args.camera_root, args.limit, args.progress_every)
    except (FileNotFoundError, NotADirectoryError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
