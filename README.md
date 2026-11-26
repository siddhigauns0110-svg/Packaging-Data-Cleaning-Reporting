# Packaging Data Cleaning & Reporting

A practical data-cleaning and reporting project using **synthetic packaging compliance data**. It demonstrates how to combine product and supplier files, remove duplicates, standardise material names, convert mixed weight units, flag data-quality issues, validate results with SQL, and prepare a Power BI report.

> **Important:** All data in this repository is fictional and generated for practice. This project is not a regulatory compliance assessment and does not claim experience with SAP or live EPR reporting.

## Project workflow

1. Generate two source files: product packaging components and suppliers.
2. Remove duplicate component rows and retain a separate duplicate audit file.
3. Standardise material labels and convert all weights to grams.
4. Left-join suppliers so products with unmatched supplier IDs remain visible.
5. Assign a data-quality status to each component.
6. Load the source and cleaned data into SQLite and run seven SQL checks.
7. Use the cleaned output in Power BI for a simple reporting page.

## Repository structure

```text
Packaging-Data-Cleaning-Reporting/
├── data/                         # Generated CSVs and analysis outputs
├── generate_data.py               # Creates deterministic synthetic source data
├── clean_data.py                  # Pandas cleaning and data-quality checks
├── load_and_check.py              # Loads CSVs into SQLite and runs SQL
├── queries.sql                    # Seven reporting/reconciliation queries
├── power_query_steps.m            # Power Query M transformation example
├── powerbi_guide.md               # Instructions for building the report
├── tests/
│   └── test_clean_data.py         # Basic checks for the cleaning workflow
└── requirements.txt
```

## Dataset

Run `python generate_data.py` to create:

- `data/products_raw.csv`: 146 rows, representing 140 unique packaging components plus 6 intentional duplicate rows.
- `data/suppliers.csv`: 6 suppliers, including one supplier with no product records.

The generated sample includes:
- duplicate component rows;
- inconsistent material labels such as `CARTON`, `cardboard `, and `Corrugated`;
- weights recorded in grams and kilograms;
- 8 missing weights;
- 10 missing recycled-content values, with 2 of those rows also missing weight;
- 4 product rows referencing a supplier absent from the supplier file;
- one listed supplier with no associated product rows.

## Quick start

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
python generate_data.py
python clean_data.py
python load_and_check.py
```

The cleaning script writes:
- `data/cleaned_packaging_data.csv`
- `data/duplicate_rows.csv`
- `data/data_quality_summary.csv`

The SQL runner creates `data/packaging_reporting.db` and prints the seven query results.

## Cleaning decisions

- **Duplicates:** remove exact duplicate rows and save them separately for traceability.
- **Material names:** map common variants to a consistent category.
- **Units:** create `weight_g`; kilogram values are multiplied by 1,000.
- **Supplier reconciliation:** use a left join from products to suppliers to avoid silently losing unmatched products.
- **Issue status:** apply a consistent priority: Missing weight → Missing recycled % → Unknown supplier → OK. The detailed missing-value columns remain available, so overlapping issues are not lost from the dataset.

## SQL checks

The queries cover:
1. packaging weight by country and material;
2. completeness percentage;
3. row counts by issue type;
4. products with an unknown supplier;
5. suppliers with no products;
6. average recycled content by material;
7. duplicate rows in the raw source.

The synthetic dataset is designed to produce **120 OK rows out of 140 unique components (85.7%)** using the single-priority status label.

## Power BI report

Follow [powerbi_guide.md](powerbi_guide.md) to create a one-page report with KPI cards, material and country charts, a data-issues table, and country/material slicers.

## What this project demonstrates

- cleaning and standardising imperfect source data;
- combining datasets and reconciling unmatched records;
- unit conversion and data validation;
- SQL reporting and audit-friendly duplicate tracking;
- preparing a repeatable workflow and dashboard-ready output.

It is a portfolio exercise using generated data. Real-world deployment would require validated business rules, source-system extracts, agreed definitions, access controls, and applicable regulatory guidance.

## Tools

Python · Pandas · SQLite · SQL · Power Query (M) · Power BI
