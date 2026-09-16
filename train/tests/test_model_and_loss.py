from __future__ import annotations

import unittest

import torch

from train.loss import masked_l1
from train.model import MaterialHeroMLP


class ModelAndLossTests(unittest.TestCase):
    def test_model_shape_and_gradients(self):
        model = MaterialHeroMLP(
            {"base": 3, "color": 2, "finish": 4, "condition": 2},
            bands=3,
            embedding_dim=4,
            width=32,
            blocks=2,
        )
        positions = torch.randn(2, 17, 3)
        normals = torch.nn.functional.normalize(torch.randn(2, 17, 3), dim=-1)
        views = torch.nn.functional.normalize(torch.randn(2, 17, 3), dim=-1)
        tokens = {
            "base": torch.tensor([0, 1]),
            "color": torch.tensor([1, 0]),
            "finish": torch.tensor([2, 3]),
            "condition": torch.tensor([0, 1]),
        }
        prediction = model(positions, normals, views, tokens)
        self.assertEqual(prediction.shape, (2, 17, 3))
        prediction.square().mean().backward()
        self.assertTrue(all(parameter.grad is not None for parameter in model.parameters()))

    def test_masked_l1(self):
        prediction = torch.tensor([[[1.0, 2.0, 4.0], [100.0, 100.0, 100.0]]])
        target = torch.tensor([[[0.0, 0.0, 1.0], [0.0, 0.0, 0.0]]])
        coverage = torch.tensor([[[1.0], [0.0]]])
        self.assertAlmostEqual(float(masked_l1(prediction, target, coverage)), 2.0)


if __name__ == "__main__":
    unittest.main()
