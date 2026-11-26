"""Generate a deterministic, fictional packaging dataset for practice."""
from pathlib import Path
import csv
import random

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

random.seed(42)

suppliers = [
    {"supplier_id": "SUP-001", "supplier_name": "GreenPack Materials", "supplier_country": "India"},
    {"supplier_id": "SUP-002", "supplier_name": "Northstar Paper", "supplier_country": "Germany"},
    {"supplier_id": "SUP-003", "supplier_name": "EcoFlex Packaging", "supplier_country": "France"},
    {"supplier_id": "SUP-004", "supplier_name": "BlueLoop Plastics", "supplier_country": "Netherlands"},
    {"supplier_id": "SUP-005", "supplier_name": "TerraGlass Works", "supplier_country": "Italy"},
    {"supplier_id": "SUP-006", "supplier_name": "Unused Supplier Co", "supplier_country": "Spain"},
]

materials = ["CARTON", "cardboard ", "Corrugated", "PET", "plastic", "Glass", "ALUMINIUM", "aluminum"]
countries = ["India", "Germany", "France", "Netherlands", "Italy"]
units = ["g", "kg"]

rows = []
for i in range(140):
    product_no = (i // 4) + 1
    component_no = (i % 4) + 1
    supplier = suppliers[i % 5]
    material = materials[i % len(materials)]
    unit = units[i % 2]
    weight = round(random.uniform(8, 950), 2)
    if unit == "kg":
        weight = round(weight / 1000, 4)

    rows.append({
        "product_id": f"PROD-{product_no:03d}",
        "component_id": f"COMP-{i + 1:04d}",
        "country": countries[i % len(countries)],
        "material": material,
        "weight": weight,
        "unit": unit,
        "recycled_pct": round(random.uniform(0, 100), 1),
        "supplier_id": supplier["supplier_id"],
    })

# Eight missing weights; two of these also have missing recycled content.
for idx in [4, 17, 28, 39, 52, 67, 81, 96]:
    rows[idx]["weight"] = ""

# Ten missing recycled-content values, including two overlapping missing weights.
for idx in [4, 17, 23, 34, 45, 58, 72, 88, 103, 119]:
    rows[idx]["recycled_pct"] = ""

# Four products/components refer to a supplier not present in suppliers.csv.
for idx in [10, 30, 50, 70]:
    rows[idx]["supplier_id"] = "SUP-UNKNOWN"

# Append six exact duplicates to make the raw file 146 rows.
raw_rows = rows + [dict(rows[i]) for i in [2, 19, 41, 63, 87, 111]]

with (DATA_DIR / "products_raw.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(raw_rows[0].keys()))
    writer.writeheader()
    writer.writerows(raw_rows)

with (DATA_DIR / "suppliers.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(suppliers[0].keys()))
    writer.writeheader()
    writer.writerows(suppliers)

print(f"Created {len(raw_rows)} raw product rows ({len(rows)} unique components).")
print(f"Created {len(suppliers)} supplier records.")
