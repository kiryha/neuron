from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

from train.data import build_vocabularies, load_material_library, make_material_splits
from train.evaluate_nearest import categorical_distance, nearest_training_id
from train.train_hero import epoch_material_schedule


class MaterialDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[2]
        cls.records = load_material_library(root / "datagen/data/neuron_library_prod.json")

    def test_library_and_vocabularies(self):
        self.assertEqual(len(self.records), 1_806)
        vocabularies = build_vocabularies(self.records.values())
        self.assertEqual(len(vocabularies["base"]), 56)
        self.assertEqual(len(vocabularies["color"]), 11)
        self.assertEqual(len(vocabularies["finish"]), 5)
        self.assertEqual(len(vocabularies["condition"]), 4)

    def test_splits_are_complete_disjoint_and_deterministic(self):
        first = make_material_splits(self.records, seed=42)
        second = make_material_splits(self.records, seed=42)
        self.assertEqual(first, second)

        train = set(first["train"])
        validation = set(first["validation"])
        test = set(first["test"])
        self.assertFalse(train & validation)
        self.assertFalse(train & test)
        self.assertFalse(validation & test)
        self.assertEqual(train | validation | test, set(self.records))

        train_groups = {
            (
                self.records[mid].base,
                self.records[mid].finish,
                self.records[mid].condition,
            )
            for mid in train
        }
        test_groups = {
            (
                self.records[mid].base,
                self.records[mid].finish,
                self.records[mid].condition,
            )
            for mid in test
        }
        self.assertFalse(train_groups & test_groups)

    def test_epoch_schedule_covers_every_material_and_reuses_groups(self):
        material_ids = ["a", "b", "c", "d", "e"]
        schedule = list(
            epoch_material_schedule(
                material_ids,
                materials_per_step=2,
                updates_per_material_batch=3,
                epochs=2,
                rng=np.random.default_rng(42),
            )
        )
        self.assertEqual(len(schedule), 2 * 3 * 3)
        for epoch in (1, 2):
            epoch_groups = [group for item_epoch, _, group in schedule if item_epoch == epoch]
            unique_groups = epoch_groups[::3]
            self.assertEqual(sorted(sum(unique_groups, [])), material_ids)
            for start in range(0, len(epoch_groups), 3):
                self.assertEqual(epoch_groups[start : start + 3], [epoch_groups[start]] * 3)

    def test_nearest_material_prefers_matching_base(self):
        target = self.records["gold_polished_clean"]
        candidates = ["silver_polished_clean", "gold_matte_clean"]
        nearest = nearest_training_id(target, candidates, self.records)
        self.assertEqual(nearest, "gold_matte_clean")
        self.assertLess(
            categorical_distance(target, self.records[nearest]),
            categorical_distance(target, self.records["silver_polished_clean"]),
        )


if __name__ == "__main__":
    unittest.main()
