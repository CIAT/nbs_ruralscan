# Deferred registers — T3 / T6 scope cut (2026-09)

**Decision (Pete, 2026-09-17):** T3 (hazard links) and T6 (scorecard/costing) are **removed from the
evidence-extraction exercise**. The task was over-scoped: ~40% of the live EV register targeted
T3/T6, nearly all of it unusable, while the deterministic QA gates (`check_scope`, `check_picos`,
`check_species`) only ever covered T4 — and the synthesis engine never read T3/T6 evidence at all
(`_EMITTABLE_ROLES` = `structural_suitability` + `operational_risk`).

This is a **deferral, not a deletion**. The T3/T6 schema table definitions in
`schema/structure/columns.json` and the populated recipe CSVs
(`schema/recipes/*/T3_nbs_hazard_farming.csv`, `*/T6_nbs_scorecard.csv`) are **kept and frozen** —
M2b Stream A reads T3 fields and M5/T5 join on T6 later. Only extraction, progress tracking, and
dashboard surfaces are stripped. Ruleset bump: see `methodology/RULESET_VERSIONS.md` v1.5.0.

Why this directory and not `schema/registers/_quarantine/`: `_quarantine/` is **gitignored**
(`.gitignore`), so rows moved there would vanish from every other clone — a hard delete, which the
evidence lock forbids. `_quarantine` = contaminated junk; `_deferred` = valid evidence, out of scope.
This directory is tracked.

## Contents

| File | Rows | Source |
|---|---|---|
| `EV_T3_T6_deferred_2026-09.csv` / `.json` | 264 (88 `climate_risk`, 176 `nbs_effect`) | `schema/registers/EV_evidence_register.csv` |
| `progress_ledger_T3_T6_deferred_2026-09.csv` | 157 (T3=78, T6=79) | `pipeline/progress_ledger.csv` |
| `SRCH_T3_T6_deferred_2026-09.csv` | 155 (T3=77, T6=78) | `schema/registers/SRCH_search_register.csv` |

Rows are verbatim snapshots (all columns, `review_state`/`reviewer_ok` untouched — this archive is a
restorable record, not a re-judgement). `climate_risk` emission is deferred entirely (the ledger
mapped it to T3; T2 is hand-authored and no code builds T2 from EV). The riparian pilot's 2
`nbs_effect` rows (PR #234) are archived with the rest — riparian re-piloting happens against T4.

Two SRC rows now have `vars_extracted=""` because all their evidence was T3/T6-scoped:
`quandt_resilience_2017` and `grass_barrier_vfs_runoff_effectiveness_2004`. Their SRC rows are kept
(acquired, cached, DOI-verified) — they simply have no live extraction.

Files here are **outside the structure manifest** — `structure.py` / `generate.py` never validate or
regenerate them.

## Restore procedure

1. Append the archived rows back into their live files (`EV_evidence_register.csv`,
   `pipeline/progress_ledger.csv`, `SRCH_search_register.csv`).
2. Restore the active-table constants: `schema_tools/ledger.py` `TABLES`/`_ROLE` and
   `schema_tools/search_log.py` `TABLES` (re-add `T3`/`T6`), and the
   `SRCH_search_register.table` enum in `schema/structure/columns.json`.
3. Re-add the recipe tables to `generate_dashboard_data()`'s table list and un-skip `_T3`/`_T6`
   discovery logs in `_parse_discovery_logs` (`schema_tools/generate.py`).
4. Resync `SRC.vars_extracted` from the restored EV rows.
5. Restore the extraction contracts from `.agents/skills/_versions/v1.4.2/contracts/` and bump
   the ruleset version.
6. `python3 src/nbs_ruralscan/schema_tools/generate.py schema` and run the full gate suite.
