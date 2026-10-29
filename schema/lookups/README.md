# Lookups (outside the column manifest)

Small deterministic lookup tables read by the T3/T6 cell-synthesis engine
(`methodology/T3_T6_generation_method.md`). Like `theme_weights`, they are configuration, not
schema tables, so `structure.py` does not validate them.

| File | Content | Source |
|---|---|---|
| `ipcc_confidence_matrix.csv` | `evidence_level` x `agreement_level` -> `confidence` (5 levels) | Mastrandrea et al. (2010) IPCC AR5 guidance note on uncertainties, Fig. 1.11 in AR5 WGII; unchanged in AR6. Method section 7.4. |
| `wb_income_groups.csv` | ISO3 -> World Bank income group (`low` / `lower_middle` / `upper_middle` / `high`) and pooled band (`lic_lmic` / `upper_middle` / `high`) | World Bank Indicators API `api.worldbank.org/v2/country` (current FY classification), fetched 2026-09-30. Aggregates and unclassified economies excluded. Refresh yearly (July) and record the date here. |
| `m2b_variable_policy.csv` | variables that may NOT be emitted as `use_role=operational_risk` (`exclude`: ingest refuses) or that are feasibility-level detail (`flag`: `check_scope` advisory) | Pete's M2b review 2026-10-22 (catalogue #50) |

The income lookup back-fills `SRC.study_income_group` from `study_country` and `EV.context.income_group`
from `context.country`; the band drives the transferability distance (method section 5.2).
