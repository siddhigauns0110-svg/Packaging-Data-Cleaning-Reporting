"""Clean packaging data with Pandas and produce audit-friendly outputs."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

MATERIAL_MAP = {
    "carton": "Cardboard",
    "cardboard": "Cardboard",
    "corrugated": "Cardboard",
    "pet": "Plastic",
    "plastic": "Plastic",
    "glass": "Glass",
    "aluminium": "Aluminium",
    "aluminum": "Aluminium",
}


def clean_packaging_data(products: pd.DataFrame, suppliers: pd.DataFrame):
    """Return cleaned data, removed duplicate rows, and a quality summary."""
    required_product_columns = {
        "product_id", "component_id", "country", "material",
        "weight", "unit", "recycled_pct", "supplier_id",
    }
    missing = required_product_columns - set(products.columns)
    if missing:
        raise ValueError(f"Products file is missing columns: {sorted(missing)}")
    if not {"supplier_id", "supplier_name", "supplier_country"}.issubset(suppliers.columns):
        raise ValueError("Suppliers file must contain supplier_id, supplier_name, supplier_country")

    raw = products.copy()
    duplicate_mask = raw.duplicated(keep="first")
    duplicates = raw.loc[duplicate_mask].copy()
    unique = raw.loc[~duplicate_mask].copy()

    unique["material_original"] = unique["material"]
    unique["material"] = (
        unique["material"].fillna("").astype(str).str.strip().str.lower()
        .map(MATERIAL_MAP).fillna("Other")
    )
    unique["unit"] = unique["unit"].fillna("").astype(str).str.strip().str.lower()
    unique["weight"] = pd.to_numeric(unique["weight"], errors="coerce")
    unique["recycled_pct"] = pd.to_numeric(unique["recycled_pct"], errors="coerce")

    unique["weight_g"] = unique["weight"]
    kg_mask = unique["unit"].eq("kg")
    g_mask = unique["unit"].eq("g")
    unique.loc[kg_mask, "weight_g"] = unique.loc[kg_mask, "weight"] * 1000
    unique.loc[~(kg_mask | g_mask), "weight_g"] = pd.NA

    # Left join deliberately preserves product rows with unmatched supplier IDs.
    cleaned = unique.merge(suppliers, on="supplier_id", how="left", indicator=True)
    cleaned["unknown_supplier"] = cleaned["_merge"].eq("left_only")
    cleaned["missing_weight"] = cleaned["weight_g"].isna()
    cleaned["missing_recycled_pct"] = cleaned["recycled_pct"].isna()

    # One primary issue label per row; the detailed flags above preserve overlaps.
    cleaned["issue_type"] = "OK"
    cleaned.loc[cleaned["unknown_supplier"], "issue_type"] = "Unknown supplier"
    cleaned.loc[cleaned["missing_recycled_pct"], "issue_type"] = "Missing recycled %"
    cleaned.loc[cleaned["missing_weight"], "issue_type"] = "Missing weight"

    cleaned = cleaned.drop(columns=["_merge"])
    issue_counts = cleaned["issue_type"].value_counts().to_dict()
    summary = pd.DataFrame([
        {"metric": "raw_rows", "value": len(raw)},
        {"metric": "unique_rows_after_deduplication", "value": len(cleaned)},
        {"metric": "duplicate_rows_removed", "value": len(duplicates)},
        {"metric": "ok_rows", "value": int((cleaned["issue_type"] == "OK").sum())},
        {"metric": "completeness_pct", "value": round((cleaned["issue_type"] == "OK").mean() * 100, 1)},
        {"metric": "missing_weight_rows", "value": int(cleaned["missing_weight"].sum())},
        {"metric": "missing_recycled_pct_rows", "value": int(cleaned["missing_recycled_pct"].sum())},
        {"metric": "unknown_supplier_rows", "value": int(cleaned["unknown_supplier"].sum())},
    ])
    for issue, count in issue_counts.items():
        summary.loc[len(summary)] = {"metric": f"primary_issue_{issue.lower().replace(' ', '_').replace('%', 'pct')}", "value": count}

    return cleaned, duplicates, summary


def main():
    products = pd.read_csv(DATA_DIR / "products_raw.csv", keep_default_na=True)
    suppliers = pd.read_csv(DATA_DIR / "suppliers.csv")
    cleaned, duplicates, summary = clean_packaging_data(products, suppliers)

    cleaned.to_csv(DATA_DIR / "cleaned_packaging_data.csv", index=False)
    duplicates.to_csv(DATA_DIR / "duplicate_rows.csv", index=False)
    summary.to_csv(DATA_DIR / "data_quality_summary.csv", index=False)

    print(summary.to_string(index=False))
    print(f"\nWrote cleaned data ({len(cleaned)} rows) and {len(duplicates)} duplicate rows.")


if __name__ == "__main__":
    main()
