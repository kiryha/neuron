"""OpenImageIO helpers for Material Hero multipart EXR files."""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable

import numpy as np

try:
    import OpenImageIO as oiio
except ImportError as exc:  # pragma: no cover - depends on the runtime environment
    raise RuntimeError(
        "OpenImageIO is required to read Material Hero EXRs. "
        "Install the Python OpenImageIO package or run with Houdini's hython."
    ) from exc


REQUIRED_PART_CHANNELS = {
    "C": ("R", "G", "B", "A"),
    "P": ("P.x", "P.y", "P.z"),
    "V": ("V.x", "V.y", "V.z"),
    "Nb": ("Nb.x", "Nb.y", "Nb.z"),
}


class ExrReadError(RuntimeError):
    """Raised when a Material Hero EXR cannot satisfy the dataset contract."""


@contextmanager
def _silence_native_stderr(enabled: bool):
    """Temporarily silence native-library stderr during expected corrupt-file checks."""

    if not enabled:
        yield
        return

    saved_stderr = os.dup(2)
    null_stderr = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(null_stderr, 2)
        yield
    finally:
        os.dup2(saved_stderr, 2)
        os.close(saved_stderr)
        os.close(null_stderr)


def read_exr_parts(
    path: str | Path,
    required_parts: Iterable[str] = REQUIRED_PART_CHANNELS,
    *,
    quiet_errors: bool = False,
) -> dict[str, np.ndarray]:
    """Fully decode selected multipart EXR subimages as float32 arrays."""

    exr_path = Path(path)
    image_input = oiio.ImageInput.open(str(exr_path))
    if image_input is None:
        detail = oiio.geterror() or "unknown OpenImageIO error"
        raise ExrReadError(f"Cannot open {exr_path}: {detail}")

    required = set(required_parts)
    parts: dict[str, np.ndarray] = {}
    try:
        subimage = 0
        while image_input.seek_subimage(subimage, 0):
            spec = image_input.spec()
            name = spec.getattribute("name") or spec.getattribute("oiio:subimagename")
            if name in required:
                expected_channels = REQUIRED_PART_CHANNELS[name]
                actual_channels = tuple(spec.channelnames)
                if actual_channels != expected_channels:
                    raise ExrReadError(
                        f"{exr_path} part {name!r} has channels {actual_channels}; "
                        f"expected {expected_channels}"
                    )
                with _silence_native_stderr(quiet_errors):
                    pixels = image_input.read_image(oiio.FLOAT)
                if pixels is None:
                    detail = image_input.geterror() or "unknown pixel-read error"
                    raise ExrReadError(
                        f"Cannot decode {exr_path} part {name!r}: {detail}"
                    )
                pixels = np.asarray(pixels, dtype=np.float32)
                if pixels.shape != (spec.height, spec.width, spec.nchannels):
                    raise ExrReadError(
                        f"{exr_path} part {name!r} decoded as {pixels.shape}; "
                        f"expected {(spec.height, spec.width, spec.nchannels)}"
                    )
                if not np.isfinite(pixels).all():
                    invalid_count = int(pixels.size - np.isfinite(pixels).sum())
                    raise ExrReadError(
                        f"{exr_path} part {name!r} contains {invalid_count} non-finite values"
                    )
                parts[name] = pixels
            subimage += 1
    finally:
        image_input.close()

    missing = required - parts.keys()
    if missing:
        raise ExrReadError(f"{exr_path} is missing parts: {sorted(missing)}")

    shapes = {(pixels.shape[0], pixels.shape[1]) for pixels in parts.values()}
    if len(shapes) != 1:
        raise ExrReadError(f"{exr_path} has misaligned part resolutions: {sorted(shapes)}")

    return parts
