-- 1. Packaging weight by country and standardised material.
SELECT country, material, ROUND(SUM(weight_g), 2) AS total_weight_g
FROM cleaned_packaging_data
GROUP BY country, material
ORDER BY country, total_weight_g DESC;

-- 2. Completeness: rows whose primary issue status is OK.
SELECT
    COUNT(*) AS total_rows,
    SUM(CASE WHEN issue_type = 'OK' THEN 1 ELSE 0 END) AS ok_rows,
    ROUND(100.0 * SUM(CASE WHEN issue_type = 'OK' THEN 1 ELSE 0 END) / COUNT(*), 1) AS completeness_pct
FROM cleaned_packaging_data;

-- 3. Rows to investigate, grouped by the primary issue label.
SELECT issue_type, COUNT(*) AS row_count
FROM cleaned_packaging_data
WHERE issue_type <> 'OK'
GROUP BY issue_type
ORDER BY row_count DESC;

-- 4. Product components whose supplier ID did not match the supplier master.
SELECT product_id, component_id, supplier_id, country, material
FROM cleaned_packaging_data
WHERE unknown_supplier = 1
ORDER BY supplier_id, product_id;

-- 5. Suppliers present in the supplier master but not referenced by any product.
SELECT s.supplier_id, s.supplier_name, s.supplier_country
FROM suppliers AS s
LEFT JOIN (
    SELECT DISTINCT supplier_id FROM products_unique
) AS p ON p.supplier_id = s.supplier_id
WHERE p.supplier_id IS NULL;

-- 6. Average declared recycled content by material.
SELECT material, ROUND(AVG(recycled_pct), 1) AS average_recycled_pct,
       COUNT(recycled_pct) AS reported_component_count
FROM cleaned_packaging_data
GROUP BY material
ORDER BY material;

-- 7. Exact duplicate rows found in the original raw source.
SELECT product_id, component_id, country, material, weight, unit,
       recycled_pct, supplier_id, COUNT(*) AS occurrences
FROM products_raw
GROUP BY product_id, component_id, country, material, weight, unit,
         recycled_pct, supplier_id
HAVING COUNT(*) > 1
ORDER BY occurrences DESC, product_id;
