"""Material Hero v0 checkpoint loading, prompt parsing, and fixed-view inference."""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from train.model import MaterialHeroMLP


TOKEN_FIELDS = ("base", "color", "finish", "condition")
ALIASES = {"dirty": "dusty", "gray": "grey"}


class PromptError(ValueError):
    """Raised when a compact material prompt is outside the packaged vocabulary."""


@dataclass(frozen=True)
class ParsedPrompt:
    tokens: dict[str, str]

    @property
    def normalized(self) -> str:
        values = [self.tokens["base"]]
        if self.tokens["color"] != "<none>":
            values.append(self.tokens["color"])
        values.extend((self.tokens["finish"], self.tokens["condition"]))
        return " ".join(value.replace("_", " ") for value in values)


def _words(value: str) -> tuple[str, ...]:
    return tuple(value.replace("_", " ").split())


def _match_prefix(words: list[str], values: dict[str, int]) -> tuple[str, int] | None:
    for value in sorted(values, key=lambda item: len(_words(item)), reverse=True):
        candidate = _words(value)
        if tuple(words[: len(candidate)]) == candidate:
            return value, len(candidate)
    return None


def parse_prompt(prompt: str, vocabularies: dict[str, dict[str, int]]) -> ParsedPrompt:
    words = re.findall(r"[a-z0-9]+", prompt.lower().replace("-", " "))
    words = [ALIASES.get(word, word) for word in words]
    if not words:
        raise PromptError("Describe a material, finish, and condition.")

    matched = _match_prefix(words, vocabularies["base"])
    if matched is None:
        raise PromptError("Start with a supported base material, such as gold or car paint.")
    base, consumed = matched
    words = words[consumed:]

    color = "<none>"
    colors = {key: value for key, value in vocabularies["color"].items() if key != "<none>"}
    matched = _match_prefix(words, colors)
    if matched is not None:
        color, consumed = matched
        words = words[consumed:]

    matched = _match_prefix(words, vocabularies["finish"])
    if matched is None:
        raise PromptError("Add a supported finish: brushed, hammered, matte, polished, or satin.")
    finish, consumed = matched
    words = words[consumed:]

    matched = _match_prefix(words, vocabularies["condition"])
    if matched is None:
        raise PromptError("End with a condition: clean, dusty, rusted, or scratched.")
    condition, consumed = matched
    words = words[consumed:]
    if words:
        raise PromptError(f"Unsupported prompt words: {' '.join(words)}")

    return ParsedPrompt({"base": base, "color": color, "finish": finish, "condition": condition})


def _normalize_directions(values: np.ndarray) -> np.ndarray:
    lengths = np.linalg.norm(values, axis=-1, keepdims=True)
    return values / np.maximum(lengths, np.float32(1e-8))


def _linear_to_srgb(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, 0.0, None)
    return np.where(
        values <= 0.0031308,
        values * 12.92,
        1.055 * np.power(values, 1.0 / 2.4) - 0.055,
    )


class MaterialHeroInference:
    def __init__(self, checkpoint_path: str | Path, chunk_size: int = 65_536):
        self.checkpoint_path = Path(checkpoint_path).resolve()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        checkpoint = torch.load(self.checkpoint_path, map_location=self.device, weights_only=False)
        metadata = checkpoint["metadata"]
        self.vocabularies = metadata["vocabularies"]
        self.material_ids = set(metadata["training_ids"])
        for material_ids in metadata["splits"].values():
            self.material_ids.update(material_ids)
        vocabulary_sizes = {field: len(values) for field, values in self.vocabularies.items()}
        self.model = MaterialHeroMLP(vocabulary_sizes, **metadata["model"]).to(self.device)
        self.model.load_state_dict(checkpoint["model"], strict=True)
        self.model.eval()
        normalization = metadata["position_normalization"]
        self.position_center = np.asarray(normalization["center"], dtype=np.float32)
        self.position_scale = np.float32(normalization["scale"])
        self.chunk_size = chunk_size
        self.step = int(checkpoint["step"])

    def render_png(
        self,
        prompt: str,
        positions: np.ndarray,
        normals: np.ndarray,
        views: np.ndarray,
        coverage: np.ndarray,
        width: int,
        height: int,
    ) -> tuple[bytes, str]:
        parsed = parse_prompt(prompt, self.vocabularies)
        material_id = "_".join(
            value
            for value in (
                parsed.tokens["base"],
                parsed.tokens["color"],
                parsed.tokens["finish"],
                parsed.tokens["condition"],
            )
            if value != "<none>"
        )
        if material_id not in self.material_ids:
            raise PromptError("That material, color, finish, and condition combination is not in Material Hero v0.")
        pixel_count = width * height
        expected_vector_shape = (pixel_count, 3)
        if positions.shape != expected_vector_shape:
            raise ValueError("Position buffer has the wrong size.")
        if normals.shape != expected_vector_shape:
            raise ValueError("Normal buffer has the wrong size.")
        if views.shape != expected_vector_shape:
            raise ValueError("View buffer has the wrong size.")
        if coverage.shape != (pixel_count,):
            raise ValueError("Coverage buffer has the wrong size.")
        if not all(np.isfinite(values).all() for values in (positions, normals, views, coverage)):
            raise ValueError("Geometry buffers contain non-finite values.")

        coverage = np.clip(coverage, 0.0, 1.0)
        visible = np.flatnonzero(coverage > 0.0)
        prediction = np.zeros((pixel_count, 3), dtype=np.float32)
        if visible.size:
            normalized_positions = (positions[visible] - self.position_center) / self.position_scale
            normalized_normals = _normalize_directions(normals[visible])
            normalized_views = _normalize_directions(views[visible])
            token_ids = {
                field: torch.tensor(
                    [self.vocabularies[field][parsed.tokens[field]]],
                    device=self.device,
                    dtype=torch.long,
                )
                for field in TOKEN_FIELDS
            }
            use_amp = self.device.type == "cuda"
            with torch.inference_mode():
                for start in range(0, visible.size, self.chunk_size):
                    end = start + self.chunk_size
                    p = torch.from_numpy(normalized_positions[start:end][None]).to(self.device)
                    n = torch.from_numpy(normalized_normals[start:end][None]).to(self.device)
                    v = torch.from_numpy(normalized_views[start:end][None]).to(self.device)
                    with torch.autocast(
                        device_type=self.device.type,
                        dtype=torch.float16,
                        enabled=use_amp,
                    ):
                        output = self.model(p, n, v, token_ids)
                    prediction[visible[start:end]] = output[0].float().cpu().numpy()

        rgb = (_linear_to_srgb(prediction).clip(0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)
        alpha = (coverage * 255.0 + 0.5).astype(np.uint8)
        rgba = np.concatenate((rgb, alpha[:, None]), axis=1).reshape(height, width, 4)
        output = io.BytesIO()
        Image.fromarray(rgba, mode="RGBA").save(output, format="PNG")
        return output.getvalue(), parsed.normalized
