"""Losses for Material Hero training."""

from __future__ import annotations

import torch


def masked_l1(
    prediction: torch.Tensor,
    target: torch.Tensor,
    coverage: torch.Tensor,
) -> torch.Tensor:
    """Coverage-weighted mean absolute RGB error."""

    if prediction.shape != target.shape:
        raise ValueError(
            f"Prediction shape {prediction.shape} does not match target {target.shape}"
        )
    if coverage.shape != prediction.shape[:-1] + (1,):
        raise ValueError(
            f"Coverage shape {coverage.shape} is incompatible with {prediction.shape}"
        )
    weighted_error = (prediction - target).abs() * coverage
    denominator = coverage.sum() * prediction.shape[-1]
    return weighted_error.sum() / denominator.clamp_min(1e-8)
