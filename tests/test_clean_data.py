import sys
from pathlib import Path
import unittest
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clean_data import clean_packaging_data


class CleaningWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.products = pd.DataFrame([
            {"product_id": "P1", "component_id": "C1", "country": "India", "material": " CARTON ",
             "weight": 1.5, "unit": "kg", "recycled_pct": 20, "supplier_id": "S1"},
            {"product_id": "P1", "component_id": "C1", "country": "India", "material": " CARTON ",
             "weight": 1.5, "unit": "kg", "recycled_pct": 20, "supplier_id": "S1"},
            {"product_id": "P2", "component_id": "C2", "country": "France", "material": "Corrugated",
             "weight": "", "unit": "g", "recycled_pct": "", "supplier_id": "MISSING"},
        ])
        self.suppliers = pd.DataFrame([
            {"supplier_id": "S1", "supplier_name": "Supplier One", "supplier_country": "India"}
        ])

    def test_deduplication_and_conversion(self):
        cleaned, duplicates, _ = clean_packaging_data(self.products, self.suppliers)
        self.assertEqual(len(cleaned), 2)
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(cleaned.loc[0, "weight_g"], 1500)
        self.assertEqual(cleaned.loc[0, "material"], "Cardboard")

    def test_left_join_keeps_unknown_supplier(self):
        cleaned, _, _ = clean_packaging_data(self.products, self.suppliers)
        unmatched = cleaned.loc[cleaned["component_id"] == "C2"].iloc[0]
        self.assertTrue(bool(unmatched["unknown_supplier"]))
        self.assertEqual(unmatched["issue_type"], "Missing weight")

    def test_overlapping_flags_are_preserved(self):
        cleaned, _, _ = clean_packaging_data(self.products, self.suppliers)
        row = cleaned.loc[cleaned["component_id"] == "C2"].iloc[0]
        self.assertTrue(bool(row["missing_weight"]))
        self.assertTrue(bool(row["missing_recycled_pct"]))
        self.assertTrue(bool(row["unknown_supplier"]))


if __name__ == "__main__":
    unittest.main()
