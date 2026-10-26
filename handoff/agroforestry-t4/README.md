# Agroforestry T4 — first-pass release

## Inspect T4 in the existing dashboard

Use [Evidence Query → T4 analysis](../../docs/dashboard.html#t4/global): **Evidence trail · Suitability & weights · Global synthesis · Rules & method**. One read-only inspection surface; evidence decisions remain in QA/QC. Developer packages below are versioned downloads, not additional live dashboards.

**Developer integration:** start with [developer-v0.1.0](developer-v0.1.0/index.html), the generated function/dataset contract, and [implementation notes](IMPLEMENTATION.md). Rebuild and selection rules are documented in [the method](../../methodology/T4_developer_contract.md). This package is generated from a verified corpus recompile; the earlier evidence-review releases remain below for provenance.

**Current release: [v0.1.5](v0.1.5/README.md), 26 October 2026.** Built for inspection ahead of the November World Bank meeting. Pilot testing remains Diego's work.

Start with the [single-table browser view](v0.1.5/index.html) or [readable CSV](v0.1.5/T4_review.csv). The versioned [T4 snapshot](v0.1.5/T4_suitability_mappings.csv) contains **26 rows: 10 numeric responses, 7 categorical host gates, 1 hard legal exclusion and 8 operational scenarios**. Numeric responses cover rainfall, temperature, slope, elevation, soil pH, soil organic carbon and NDVI.

This replaces the stale handoff that described only one numeric row. It packages existing reviewed work; it does not claim ten new rules were extracted during release preparation.

The editable source remains `schema/recipes/agroforestry/T4_suitability_mappings.csv`; its JSON is generated. Versioned handoff files are generated snapshots, not alternative editable schema tables. Do not substitute historical synthesis intermediates for the live recipe.

## What the first pass establishes

- A traceable configuration: theme → variable group → canonical variable → dataset, with source profiles and evidence identifiers.
- Numeric and categorical rules in one table; M2b operational scenarios and evidence shown as a separate module, kept out of core suitability scoring.
- Dataset resolution, time period, choice rationale, alternatives and local upload requirements visible.
- Every current structural/operational evidence record accounted for, including quarantine, qualitative evidence and calibration holds.
- Within-study relative importance supplied separately from runtime weights. A ratio above one means greater importance than the stated comparator, not an automatic suitability weight; alternative source models remain separate.

## What it does not establish

Regional numeric profiles still need explicit source/context selection; shared agroforestry evidence does not automatically apply to every system. FMNR rainfall remains contextual evidence without an executable cutoff. Related proxies are grouped, not silently merged; missing units and soil-depth differences remain meaningful.

Climate BIND selects CHELSA while recipe rows still identify WorldClim. Runtime must reconcile the selected dataset, band and unit before execution. Other variables without a global BIND override retain the recipe dataset. Dataset choices are existing configured preferences, not a new quality benchmark. Finer pixels alone do not establish better data.

The protected-area text threshold needs a legal-mask adapter and clarification of family coverage. Four local inputs remain: field-boundary zones, grazing confirmation, farmland context, and ungrazed forage management. These affect particular gate branches; they do not imply every branch is blocked. GPW + GLW4 does not replace local grazing confirmation. Boundary plantings are placement zones/line lengths, not planted pixel area.

No raster run, complete M1 runner, or pilot validation is claimed. Missing inputs remain unknown. Eight soft operational scenarios belong to M2b/implementation guidance.

## Reproduce and version

`PYTHONPATH=src python3 scripts/release-t4-first-pass.py` builds v0.1.5 from current CSVs. The release manifest records source commit and input/output hashes. Preserve published versions; change the generator version before issuing a subsequent release. Use GitHub for delivery; no separate upload or message to Diego is required.

Rule plots: `uv run --no-project --with matplotlib python scripts/plot-t4-release.py`, then rebuild the release table. v0.1.0 remains preserved.
