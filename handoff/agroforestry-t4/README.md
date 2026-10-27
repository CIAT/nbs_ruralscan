# Agroforestry T4 — developer handoff

## Inspect T4 in the existing dashboard

Use [Evidence Query → T4 analysis](../../docs/dashboard.html#t4/global): **Evidence trail · Suitability & weights · Global synthesis · Rules & method**. One read-only inspection surface; evidence decisions remain in QA/QC. Developer packages below are versioned downloads, not additional live dashboards.

**Current developer package: [developer-v0.1.4](developer-v0.1.4/README.md), 27 October 2026.** Start with the [implementation task brief for Diego and Brayden](START_HERE.md), [developer table](developer-v0.1.4/developer_table.csv), [machine contract](developer-v0.1.4/developer_contract.json) and [implementation guide](IMPLEMENTATION.md). Rebuild and selection rules are documented in [the method](../../methodology/T4_developer_contract.md).

This package is generated from a verified corpus recompile, including Haile's restored SOC continuation bands. It contains 26 configured mappings plus 12 operational reference rows and 40 response conformance cases. Country-specific selections remain unset; the approved partial terrain-and-soil policy pins three functions and weights without granting regional transfer. Package version 0.1.4 uses contract/selection format 0.2.0. Pilot testing remains Diego's work.

The configured rows are **10 numeric responses, 7 categorical host gates, 1 hard legal exclusion and 8 operational scenarios**. Numeric responses cover rainfall, temperature, slope, elevation, soil pH, soil organic carbon and NDVI.

The [earlier developer package](developer-v0.1.0/README.md) and [v0.1.5 evidence catalogue](v0.1.5/README.md) remain immutable historical snapshots. Use the existing dashboard for ongoing inspection; do not start a new review in an archived HTML report.

The editable source remains `schema/recipes/agroforestry/T4_suitability_mappings.csv`; its JSON is generated. Versioned handoff files are generated snapshots, not alternative editable schema tables. Do not substitute historical synthesis intermediates for the live recipe.

Provider-checked assets, units and remaining soil-depth questions: [dataset input handoff](DATASET_INPUTS.md). The v0.1.4 bundle includes source compatibility findings, an explicit unselected 0–30 cm soil-input proposal, complete planted land-cover class documentation, and the assessed legal-mask contract. Earlier versions remain unchanged.

## Configuration decisions

[First-pass decision table](FIRST_PASS_DECISIONS.md) records approved response choices, aggregation and weights, with worked examples. The new package includes the policy and six aggregation/gate conformance cases. Target transfer and input validation remain open.

## What the first pass establishes

- A traceable configuration: theme → variable group → canonical variable → dataset, with source profiles and evidence identifiers.
- Numeric and categorical rules in one table; M2b operational scenarios and evidence shown as a separate module, kept out of core suitability scoring.
- Dataset resolution, time period, choice rationale, alternatives and local upload requirements visible.
- Every current structural/operational evidence record accounted for, including quarantine, qualitative evidence and calibration holds.
- Within-study relative importance supplied separately from runtime weights. A ratio above one means greater importance than the stated comparator, not an automatic suitability weight; alternative source models remain separate.

## What it does not establish

Regional numeric profiles still need explicit source/context selection; shared agroforestry evidence does not automatically apply to every system. FMNR rainfall remains contextual evidence without an executable cutoff. Related proxies are grouped, not silently merged; missing units and soil-depth differences remain meaningful.

Climate BIND selects CHELSA while recipe rows still identify WorldClim. Runtime must reconcile the selected dataset, band and unit before execution. Other variables without a global BIND override retain the recipe dataset. Dataset choices are existing configured preferences, not a new quality benchmark. Finer pixels alone do not establish better data.

The planted-silvoarable legal gate requires an assessed exclusion mask with target rules and coverage; protected-area categories alone do not determine permission. See [gate inputs](DATASET_INPUTS.md#planted-silvoarable-host-and-legal-gates). Four local inputs remain: field-boundary zones, grazing confirmation, farmland context, and ungrazed forage management. These affect particular gate branches; they do not imply every branch is blocked. GPW + GLW4 does not replace local grazing confirmation. Boundary plantings are placement zones/line lengths, not planted pixel area.

No raster run, complete M1 runner, or pilot validation is claimed. Missing inputs remain unknown. Eight soft operational scenarios belong to M2b/implementation guidance.

## Reproduce and version

`PYTHONPATH=src python3 scripts/build-t4-developer.py --output /tmp/t4-developer-options` builds a fresh full-corpus options package. Add `--country` only to resolve a target's datasets; it does not select or approve regional functions. Verify with `--verify /tmp/t4-developer-options` against the matching source checkout. The manifest records source commit and input/output hashes. Preserve published versions; advance the package version before publishing a new bundle. Use GitHub for delivery; no separate upload or message to Diego is required.

For data-only audit reconciliation, `scripts/audit-t4-compilation.py agroforestry OUTPUT --data-only` consumes fresh `draft/report.json` and `approved/report.json` under `OUTPUT`. It validates authorized source completions independently and preserves their separate human review status. Historical HTML reports remain untouched.
