# Agroforestry — focused OpenAlex sweep (2026-06)

**Date(s):** June 2026.
**Author(s):** Pete Steward (orchestrated).
**Purpose:** A focused, capped OpenAlex search for **high-value agroforestry-suitability papers MISSED by the stocktake** — recent (≥2024, beyond the stocktake window) or otherwise not caught. **Separate from the stocktake** (which was its own OpenAlex run, Apr–Jun 2026; see the Stocktake tab / `reference/stocktake/`).

**Keyword basis:** derived from the 5 High-tier AF stocktake papers (suitability mapping · spatial priority indicators · climate-smart targeting · silvoarable) → `agroforestry × (suitability | land evaluation | priority areas | multicriteria/GIS | silvopasture | opportunity mapping)`. OpenAlex title-search, `from_publication_date:2024-01-01`, `type:article`, sorted by citations.

**Caps (bounded sweep):** retrieve ≤200/query · screen ≤50 abstracts · acquire+extract ≤15. Actual: 6 queries.

## PRISMA-lite counts
- **Retrieved (unique):** 31
- **After dedup vs the 220-row stocktake:** 29
- **Screened:** 29 (all; small pool)
- **Selected (high-value / novel, all open-access):** 6 → acquire + extract
- **Deferred (backlog for a later pass):** 23 — kept in `reference/discovery/openalex_candidates.csv` (status column)

## Resumability
`reference/discovery/openalex_candidates.csv` is the **candidate ledger** (title · year · cites · OA · doi · venue · status · sweep). Future sweeps dedup against this **and** the stocktake, and work the `deferred` backlog. Status: `selected` → extracting; `deferred` → not yet screened-in; later `extracted` / `rejected`.

## Selected for extraction (6, all OA)
1. The potential of agroforestry to buffer climate change impacts on suitability (2024, 17 cites)
2. Scaling agroforestry land suitability analysis in Odisha — machine learning (2026)
3. Enhancing ecosystem services to mitigate agro-environmental pressures (2026)
4. Assessing soil & land suitability of an olive–maize agroforestry system (2024)
5. Enhancing coffee agroforestry suitability using geospatial analysis (2024)
6. Soil quality in land-suitability analysis of coffee agroforestry (2024)

## Extraction outcome (2026-06-19, run `openalex_af_2026-06`)
Of the 6 selected, **4 acquired** (2 acquire-failed: olive–maize 403, Gedeo coffee landing-only). All 4 extracted via the deterministic pipeline (`build_index` → `package_for_extraction` → page-stamped `EvidenceUnit` → `validate_units` → staging), then centrally gated (verbatim quote + `check_numbers` + `check_scope` + `check_quote`).

| source_id | tier | family | units | notes |
|---|---|---|---|---|
| abigaba_2024 | Medium | shaded_perennial | 9 | coffee/banana climate optima = `species_specific` (taxon); shade-cover thresholds = practice |
| affan_2024 | Low | shaded_perennial | 8 | FAO S1–N soil-quality bands; coffee pH/temp = species; slope/texture = practice |
| mantino_2026 | Medium | silvopastoral | 3 | mostly qualitative; SOC + canopy are T6 effects; GIS criteria cited to Gabourel-Landaverde 2025 (not reproduced) |
| singh_2026 | Medium | planted_silvoarable | 11 | general AF MCDM/ML; soil_ph has numeric classes; ML feature weights tagged `ml_importance` (no shape params) |

**Total: 31 EvidenceUnits, 443/443 verbatim-verified, 0 number/scope/quote flags.** SRC `source_category=updated_lit`. Ledger: agroforestry·T4/T6·updated_lit stamped (searched=in_progress — capped, 23 deferred; screened=done; verified=in_progress — central guardrail passed, pending QA-review sign-off).

**Follow-ups:** (a) catalogue the 4 PDFs to the SharePoint library + set `library_path` (provenance note); (b) work the 23 deferred candidates; (c) re-run synthesis if these should refresh T4 mapping params (held — alters analytical values).
