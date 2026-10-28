# Selecting spatial inputs

Use the dataset requirements in [the developer table](developer_table.csv), with
`dataset_bindings.csv`, `datasets.csv` and `variables.csv` as join references.
The full registries contain other recipes; only linked identifiers are selected.

For each selected variable, verify:

- The dataset measures the same concept, depth, period and units as the selected function.
- The chosen band, scale/offset, missing-value encoding and any derived-variable operation
  are recorded. Similar proxies are not interchangeable without an approved transformation.
- Native spatial and temporal support is suitable for this task. Derive scale-dependent terrain
  variables before aggregation. Resampling cannot improve underlying information resolution.
- The most-specific applicable binding and any upload/fallback flag are retained. Prefer
  fitness-equivalent server-side sources; record asset/version and retrieval steps.
- Host distributions and categorical crosswalks use the recipe's approved definitions. Never
  copy another NbS's land-cover exclusions or host assumptions.

Target country resolves data context; it does not select evidence countries or approve
transfer of a regional response. Missing bindings, mappings and local confirmation stay visible.
No recipe-specific dataset or threshold is approved by this generic checklist.
