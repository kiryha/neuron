from __future__ import annotations

import unittest
from pathlib import Path

from train.data import build_vocabularies, load_material_library, make_material_splits


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


if __name__ == "__main__":
    unittest.main()
