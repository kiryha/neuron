"""Material catalog, deterministic splits, and sampled EXR batches."""

from __future__ import annotations

import hashlib
import json
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

from .exr import read_exr_parts


NONE_TOKEN = "<none>"
TOKEN_FIELDS = ("base", "color", "finish", "condition")


@dataclass(frozen=True)
class MaterialRecord:
    material_id: str
    base: str
    color: str
    finish: str
    condition: str
    semantic_label: str

    def tokens(self) -> dict[str, str]:
        return {
            "base": self.base,
            "color": self.color,
            "finish": self.finish,
            "condition": self.condition,
        }


def load_material_library(path: str | Path) -> dict[str, MaterialRecord]:
    with Path(path).open("r", encoding="utf-8") as handle:
        raw_library = json.load(handle)

    records: dict[str, MaterialRecord] = {}
    for material_id, raw in raw_library.items():
        metadata = raw["metadata"]
        semantic = raw.get("semantic", {})
        records[material_id] = MaterialRecord(
            material_id=material_id,
            base=str(metadata["base"]),
            color=str(metadata.get("color_name") or NONE_TOKEN),
            finish=str(metadata["finish"]),
            condition=str(metadata["condition"]),
            semantic_label=str(semantic.get("semantic_label") or material_id),
        )
    return records


def build_vocabularies(
    records: Iterable[MaterialRecord],
) -> dict[str, dict[str, int]]:
    records = tuple(records)
    values = {
        "base": sorted({record.base for record in records}),
        "color": sorted({record.color for record in records}),
        "finish": sorted({record.finish for record in records}),
        "condition": sorted({record.condition for record in records}),
    }
    return {
        field: {value: index for index, value in enumerate(values[field])}
        for field in TOKEN_FIELDS
    }


def encode_record(
    record: MaterialRecord,
    vocabularies: dict[str, dict[str, int]],
) -> dict[str, int]:
    return {
        field: vocabularies[field][record.tokens()[field]]
        for field in TOKEN_FIELDS
    }


def _stable_bucket(value: str, seed: int, buckets: int = 10_000) -> int:
    digest = hashlib.sha256(f"{seed}:{value}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % buckets


def make_material_splits(
    records: dict[str, MaterialRecord],
    seed: int = 42,
) -> dict[str, list[str]]:
    """Create train/validation/compositional-test material-ID splits.

    Complete (base, finish, condition) groups are assigned to the test split.
    Validation IDs are selected from the remaining groups. This keeps every
    future camera view of a material together and makes the test split more
    meaningful than a random frame split.
    """

    test_groups = {
        (record.base, record.finish, record.condition)
        for record in records.values()
        if _stable_bucket(
            f"{record.base}|{record.finish}|{record.condition}", seed
        ) < 1_000
    }

    splits = {"train": [], "validation": [], "test": []}
    for material_id in sorted(records):
        record = records[material_id]
        group = (record.base, record.finish, record.condition)
        if group in test_groups:
            splits["test"].append(material_id)
        elif _stable_bucket(material_id, seed + 1) < 1_100:
            splits["validation"].append(material_id)
        else:
            splits["train"].append(material_id)

    for field in TOKEN_FIELDS:
        all_values = {record.tokens()[field] for record in records.values()}
        train_values = {records[mid].tokens()[field] for mid in splits["train"]}
        missing = all_values - train_values
        if missing:
            raise ValueError(f"Training split is missing {field} tokens: {sorted(missing)}")

    return splits


@dataclass(frozen=True)
class PositionNormalization:
    center: tuple[float, float, float]
    scale: float

    @classmethod
    def from_parts(cls, parts: dict[str, np.ndarray]) -> "PositionNormalization":
        coverage = parts["C"][..., 3] > 0
        visible_positions = parts["P"][coverage]
        minimum = visible_positions.min(axis=0)
        maximum = visible_positions.max(axis=0)
        center = (minimum + maximum) * 0.5
        scale = float(np.max((maximum - minimum) * 0.5))
        if not np.isfinite(scale) or scale <= 0:
            raise ValueError(f"Invalid position scale: {scale}")
        return cls(tuple(float(value) for value in center), scale)

    def apply(self, positions: np.ndarray) -> np.ndarray:
        center = np.asarray(self.center, dtype=np.float32)
        return (positions - center) / np.float32(self.scale)

    def to_json(self) -> dict[str, object]:
        return {"center": list(self.center), "scale": self.scale}


def normalize_directions(values: np.ndarray) -> np.ndarray:
    lengths = np.linalg.norm(values, axis=-1, keepdims=True)
    return values / np.maximum(lengths, np.float32(1e-8))


class ExrCache:
    """Small process-local LRU cache of fully decoded EXRs."""

    def __init__(self, max_items: int = 4):
        self.max_items = max_items
        self._items: OrderedDict[str, dict[str, np.ndarray]] = OrderedDict()

    def get(self, path: Path) -> dict[str, np.ndarray]:
        key = str(path.resolve())
        if key in self._items:
            self._items.move_to_end(key)
            return self._items[key]
        parts = read_exr_parts(path)
        self._items[key] = parts
        self._items.move_to_end(key)
        while len(self._items) > self.max_items:
            self._items.popitem(last=False)
        return parts


class MaterialBatchSource:
    def __init__(
        self,
        camera_root: str | Path,
        records: dict[str, MaterialRecord],
        vocabularies: dict[str, dict[str, int]],
        position_normalization: PositionNormalization,
        cache_items: int = 4,
    ):
        self.camera_root = Path(camera_root)
        self.records = records
        self.vocabularies = vocabularies
        self.position_normalization = position_normalization
        self.cache = ExrCache(cache_items)

    def exr_path(self, material_id: str) -> Path:
        return self.camera_root / material_id / "render.exr"

    def sample_batch(
        self,
        material_ids: list[str],
        pixels_per_material: int,
        rng: np.random.Generator,
    ) -> dict[str, np.ndarray | dict[str, np.ndarray]]:
        sampled: dict[str, list[np.ndarray]] = {
            "P": [],
            "N": [],
            "V": [],
            "rgb": [],
            "coverage": [],
        }
        token_ids = {field: [] for field in TOKEN_FIELDS}

        for material_id in material_ids:
            parts = self.cache.get(self.exr_path(material_id))
            beauty = parts["C"]
            coverage = beauty[..., 3]
            visible = np.flatnonzero(coverage.reshape(-1) > 0)
            if visible.size == 0:
                raise ValueError(f"{material_id} has no covered pixels")
            indices = rng.choice(
                visible,
                size=pixels_per_material,
                replace=visible.size < pixels_per_material,
            )

            positions = parts["P"].reshape(-1, 3)[indices]
            sampled["P"].append(self.position_normalization.apply(positions))
            sampled["N"].append(
                normalize_directions(parts["Nb"].reshape(-1, 3)[indices])
            )
            sampled["V"].append(
                normalize_directions(parts["V"].reshape(-1, 3)[indices])
            )
            sampled["rgb"].append(beauty[..., :3].reshape(-1, 3)[indices])
            sampled["coverage"].append(coverage.reshape(-1, 1)[indices])

            encoded = encode_record(self.records[material_id], self.vocabularies)
            for field in TOKEN_FIELDS:
                token_ids[field].append(encoded[field])

        batch: dict[str, np.ndarray | dict[str, np.ndarray]] = {
            key: np.stack(values).astype(np.float32, copy=False)
            for key, values in sampled.items()
        }
        batch["tokens"] = {
            field: np.asarray(values, dtype=np.int64)
            for field, values in token_ids.items()
        }
        return batch
