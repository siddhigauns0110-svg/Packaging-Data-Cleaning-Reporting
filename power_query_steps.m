// Power Query M example.
// Update the file paths to the location of your generated CSV files.

let
    ProductsSource = Csv.Document(
        File.Contents("C:\\YOUR_PROJECT_PATH\\data\\products_raw.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    ProductsHeaders = Table.PromoteHeaders(ProductsSource, [PromoteAllScalars=true]),
    ProductsTypes = Table.TransformColumnTypes(ProductsHeaders, {
        {"product_id", type text}, {"component_id", type text},
        {"country", type text}, {"material", type text},
        {"weight", type number}, {"unit", type text},
        {"recycled_pct", type number}, {"supplier_id", type text}
    }),
    Deduplicated = Table.Distinct(ProductsTypes),
    TrimmedText = Table.TransformColumns(Deduplicated, {
        {"material", each Text.Lower(Text.Trim(_)), type text},
        {"unit", each Text.Lower(Text.Trim(_)), type text}
    }),
    StandardMaterial = Table.ReplaceValue(TrimmedText, "carton", "Cardboard", Replacer.ReplaceText, {"material"}),
    CardboardVariant = Table.ReplaceValue(StandardMaterial, "cardboard", "Cardboard", Replacer.ReplaceText, {"material"}),
    CorrugatedVariant = Table.ReplaceValue(CardboardVariant, "corrugated", "Cardboard", Replacer.ReplaceText, {"material"}),
    PlasticVariant = Table.ReplaceValue(CorrugatedVariant, "pet", "Plastic", Replacer.ReplaceText, {"material"}),
    PlasticTextVariant = Table.ReplaceValue(PlasticVariant, "plastic", "Plastic", Replacer.ReplaceText, {"material"}),
    GlassVariant = Table.ReplaceValue(PlasticTextVariant, "glass", "Glass", Replacer.ReplaceText, {"material"}),
    AluminiumVariant = Table.ReplaceValue(GlassVariant, "aluminium", "Aluminium", Replacer.ReplaceText, {"material"}),
    AluminumVariant = Table.ReplaceValue(AluminiumVariant, "aluminum", "Aluminium", Replacer.ReplaceText, {"material"}),
    AddWeightGrams = Table.AddColumn(AluminumVariant, "weight_g", each
        if [weight] = null then null
        else if [unit] = "kg" then [weight] * 1000
        else if [unit] = "g" then [weight]
        else null, type number),
    SuppliersSource = Csv.Document(
        File.Contents("C:\\YOUR_PROJECT_PATH\\data\\suppliers.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    SuppliersHeaders = Table.PromoteHeaders(SuppliersSource, [PromoteAllScalars=true]),
    SuppliersTypes = Table.TransformColumnTypes(SuppliersHeaders, {
        {"supplier_id", type text}, {"supplier_name", type text},
        {"supplier_country", type text}
    }),
    MergedSuppliers = Table.NestedJoin(AddWeightGrams, {"supplier_id"}, SuppliersTypes, {"supplier_id"}, "Supplier", JoinKind.LeftOuter),
    ExpandedSupplier = Table.ExpandTableColumn(MergedSuppliers, "Supplier", {"supplier_name", "supplier_country"}, {"supplier_name", "supplier_country"}),
    AddMissingWeight = Table.AddColumn(ExpandedSupplier, "missing_weight", each [weight_g] = null, type logical),
    AddMissingRecycled = Table.AddColumn(AddMissingWeight, "missing_recycled_pct", each [recycled_pct] = null, type logical),
    AddUnknownSupplier = Table.AddColumn(AddMissingRecycled, "unknown_supplier", each [supplier_name] = null, type logical),
    AddIssueType = Table.AddColumn(AddUnknownSupplier, "issue_type", each
        if [missing_weight] then "Missing weight"
        else if [missing_recycled_pct] then "Missing recycled %"
        else if [unknown_supplier] then "Unknown supplier"
        else "OK", type text)
in
    AddIssueType
