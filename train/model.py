"""Coordinate-conditioned Material Hero baseline."""

from __future__ import annotations

import math

import torch
from torch import nn


class FourierPosition(nn.Module):
    def __init__(self, bands: int):
        super().__init__()
        frequencies = (2.0 ** torch.arange(bands, dtype=torch.float32)) * math.pi
        self.register_buffer("frequencies", frequencies, persistent=True)

    @property
    def output_dim(self) -> int:
        return 3 + 2 * 3 * int(self.frequencies.numel())

    def forward(self, positions: torch.Tensor) -> torch.Tensor:
        angles = positions[..., None] * self.frequencies
        return torch.cat(
            [positions, angles.sin().flatten(-2), angles.cos().flatten(-2)],
            dim=-1,
        )


class MaterialEncoder(nn.Module):
    fields = ("base", "color", "finish", "condition")

    def __init__(self, vocabulary_sizes: dict[str, int], embedding_dim: int):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.tables = nn.ModuleDict(
            {
                field: nn.Embedding(vocabulary_sizes[field], embedding_dim)
                for field in self.fields
            }
        )

    @property
    def output_dim(self) -> int:
        return len(self.fields) * self.embedding_dim

    def forward(self, token_ids: dict[str, torch.Tensor]) -> torch.Tensor:
        return torch.cat(
            [self.tables[field](token_ids[field]) for field in self.fields],
            dim=-1,
        )


class ResidualBlock(nn.Module):
    def __init__(self, width: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.LayerNorm(width),
            nn.Linear(width, width),
            nn.SiLU(),
            nn.Linear(width, width),
        )

    def forward(self, values: torch.Tensor) -> torch.Tensor:
        return values + self.net(values)


class MaterialHeroMLP(nn.Module):
    def __init__(
        self,
        vocabulary_sizes: dict[str, int],
        *,
        bands: int = 6,
        embedding_dim: int = 16,
        width: int = 256,
        blocks: int = 6,
        condition_material: bool = True,
    ):
        super().__init__()
        self.condition_material = condition_material
        self.position = FourierPosition(bands)
        self.material = (
            MaterialEncoder(vocabulary_sizes, embedding_dim)
            if condition_material
            else None
        )
        geometry_dim = self.position.output_dim + 3 + 3
        material_dim = self.material.output_dim if self.material is not None else 0
        self.input = nn.Sequential(
            nn.Linear(geometry_dim + material_dim, width),
            nn.SiLU(),
        )
        self.blocks = nn.Sequential(*[ResidualBlock(width) for _ in range(blocks)])
        self.output = nn.Linear(width, 3)

    def forward(
        self,
        positions: torch.Tensor,
        normals: torch.Tensor,
        view_directions: torch.Tensor,
        token_ids: dict[str, torch.Tensor],
    ) -> torch.Tensor:
        geometry = torch.cat(
            [self.position(positions), normals, view_directions], dim=-1
        )
        if self.material is not None:
            material = self.material(token_ids)
            material = material[:, None, :].expand(-1, positions.shape[1], -1)
            geometry = torch.cat([geometry, material], dim=-1)
        hidden = self.input(geometry)
        return self.output(self.blocks(hidden))
