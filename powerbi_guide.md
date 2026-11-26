# Power BI report guide

Use the output file `data/cleaned_packaging_data.csv` as the main Power BI data source.

## 1. Load the data

1. Run `python generate_data.py` and `python clean_data.py`.
2. In Power BI Desktop, select **Get data → Text/CSV**.
3. Select `cleaned_packaging_data.csv`.
4. Confirm data types: `weight_g` is Decimal Number, `recycled_pct` is Decimal Number, and ID/country/material/issue columns are Text.

## 2. Suggested measures

Create these measures in Power BI:

```DAX
Total Packaging Weight (g) =
SUM(cleaned_packaging_data[weight_g])

Average Recycled Content (%) =
AVERAGE(cleaned_packaging_data[recycled_pct])

Total Components =
COUNTROWS(cleaned_packaging_data)

OK Components =
CALCULATE(
    COUNTROWS(cleaned_packaging_data),
    cleaned_packaging_data[issue_type] = "OK"
)

Completeness (%) =
DIVIDE([OK Components], [Total Components], 0) * 100

Components With Issues =
CALCULATE(
    COUNTROWS(cleaned_packaging_data),
    cleaned_packaging_data[issue_type] <> "OK"
)
```

## 3. Build a one-page report

- **KPI cards:** Completeness (%), Total Packaging Weight (g), Average Recycled Content (%).
- **Bar chart:** Axis = material; Values = Total Packaging Weight (g).
- **Stacked column chart:** Axis = country; Legend = material; Values = Total Packaging Weight (g).
- **Table:** product_id, component_id, supplier_id, issue_type, weight_g, recycled_pct.
- **Slicers:** country and material.

## 4. Add a data-quality view

Add a bar chart with `issue_type` as the axis and component count as the value. Keep the detailed issue flags in the table so a user can inspect rows that have more than one missing or mismatched field.

## Notes

This is a practice dashboard built from synthetic data. The sample is designed for demonstrating data preparation and reporting concepts, not for making real regulatory or customer declarations.
