"""Load source and cleaned CSVs into SQLite, then execute queries.sql."""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"


def main():
    raw_path = DATA_DIR / "products_raw.csv"
    suppliers_path = DATA_DIR / "suppliers.csv"
    clean_path = DATA_DIR / "cleaned_packaging_data.csv"

    if not all(path.exists() for path in [raw_path, suppliers_path, clean_path]):
        raise SystemExit("Input files are missing. Run generate_data.py and clean_data.py first.")

    raw = pd.read_csv(raw_path)
    suppliers = pd.read_csv(suppliers_path)
    cleaned = pd.read_csv(clean_path)

    db_path = DATA_DIR / "packaging_reporting.db"
    with sqlite3.connect(db_path) as conn:
        raw.to_sql("products_raw", conn, if_exists="replace", index=False)
        suppliers.to_sql("suppliers", conn, if_exists="replace", index=False)
        cleaned.to_sql("cleaned_packaging_data", conn, if_exists="replace", index=False)

        # Deduplicated product source for supplier-to-product reconciliation.
        unique = raw.drop_duplicates()
        unique[["supplier_id"]].drop_duplicates().to_sql(
            "products_unique", conn, if_exists="replace", index=False
        )

        sql_text = (ROOT / "queries.sql").read_text(encoding="utf-8")
        statements = [part.strip() for part in sql_text.split(";") if part.strip()]
        for number, statement in enumerate(statements, start=1):
            print(f"\n{'=' * 18} QUERY {number} {'=' * 18}")
            try:
                result = pd.read_sql_query(statement, conn)
                print(result.to_string(index=False) if not result.empty else "(no rows)")
            except Exception as exc:
                print(f"Query failed: {exc}")
                raise

    print(f"\nSQLite database written to: {db_path}")


if __name__ == "__main__":
    main()
