# Discovery search protocol — stepped, logged, auditable

*So that "what searches did we run?" has a clear, queryable answer for every sub-practice.*

## The rule
For **each sub-practice (suitability family) × table (T4/T3/T6)**, run **each of the 4 discovery processes** and **log the protocol** in the `SRCH` register before claiming the search done.

### The 4 discovery processes
(= the ledger categories / dashboard audit-matrix columns)

| process | what it is | channel |
|---|---|---|
| **stock** | the benchmarked stocktake corpus (peer-reviewed, C/I/D tiered) | OpenAlex (historical) |
| **updated_lit** | focused peer-reviewed sweep beyond the stocktake | OpenAlex title-search |
| **grey** | reports / manuals / briefs | web search (EN/ES/FR) + CGSpace DSpace API + WOCAT |
| **tool** | tools / methods / codebases | GitHub + platforms |

## What every search logs (the `SRCH` register)
`schema/registers/SRCH_search_register.csv` — one row per (NbS × family × table × process × run):
- **`search_terms`** — the exact query strings used.
- **`screening_steps`** — the 5-step funnel applied: `frame · source_type · relevance · credibility_six_axis · saturation_stop`.
- **`inclusion_criteria`** — the in/out rule (what counts; what's excluded).
- **`limits`** — caps (e.g. `retrieve≤200/query; screen≤50; extract≤15`).
- **`n_retrieved` · `n_screened` · `n_included`** — PRISMA-lite counts.
- **`search_date` · `run_id` · `searched_by`** — provenance.
- **`ruleset_version`** — which instruction set governed it ([RULESET_VERSIONS.md](RULESET_VERSIONS.md)).
- **`discovery_log_ref`** — link to the narrative discovery log.

Log via `schema_tools/search_log.py` (`log_search(...)` / CLI `log`).

### Generic (parent) search vs sub-practice search — they are NOT the same (v1.1)
`suitability_family_id=""` = the **generic / practice-wide parent search** — one broad query over the
NbS and its synonyms (e.g. the stocktake's `("agroforestry" OR "agro-forestry" OR "trees on farms"
OR "tree-based system*" OR "agrosilvopastoral*" OR "silvopastoral*" …) AND climate AND spatial`).
A specific `family` = a **sub-practice-targeted search** with its own added terms (e.g. F1 adds
`"alley cropping" OR "tree intercropping"`). **The union of the per-sub-practice searches ≠ the
generic parent search** — different nets, different recall; you do not *sum* searches. Both are
logged as separate `SRCH` rows and reported separately. A family with no targeted row inherits
*nothing* automatically — it is shown as "covered by the generic net, not targeted" (the dashboard's
amber banner + the matrix dashed ring), never as "done".

### Search-term capture must be VERBATIM (v1.1)
`SRCH.search_terms` records the **exact query string actually run** — copied from the search
configuration / Annex / run script, never a from-memory paraphrase. (A paraphrase silently dropped
the climate block, all practice synonyms, and misfiled `silvopastoral` as a topic — caught
2026-06-29.) If the verbatim string lives in a file (`OpenAlex_run.R`, `search_string.xlsx`, a
stocktake Annex), transcribe it and cite that file in `SRCH.note`.

### Synonym policy (v1.1)
Practice-level (generic) searches use the **full synonym set** for the NbS (all spelling/term
variants OR'd in the practice block). Sub-practice searches keep the parent synonyms **and** add the
family's own vocabulary. Dropping synonyms narrows recall — default is to include them; any omission
is a logged decision.

## How it locks together (one source of truth, layered)
1. **`SRCH`** = the search *protocol* (this record).
2. **Progress ledger** (`progress_ledger.csv`) = the search *status* (`searched` not_started/in_progress/done) per (NbS × table × category × family). **`ledger.check` FAILS the build if `searched=done` has no matching `SRCH` row** — you cannot claim a search without its logged protocol.
3. **Discovery logs** (`methodology/discovery_logs/*.md`) = the narrative companion (PRISMA-lite prose).
4. **`EV.ruleset_version` / `SRCH.ruleset_version`** trace every datum back to the search + the exact instructions that found it.

## Version control of the instructions (reproducibility)
The search/extraction instructions are versioned: [`methodology/RULESET_VERSIONS.md`](RULESET_VERSIONS.md) (semver · date · change) + archived prompt snapshots under [`.agents/skills/_versions/<version>/`](../.agents/skills/_versions/). Bump + snapshot on any change to the screening funnel, defect catalogue, or discovery protocol. A past search is reproducible with the snapshot its `ruleset_version` points to.

## Status (v1.1, 2026-06-29)
The agroforestry `SRCH` rows are the **generic (practice-wide) parent search** at `family=""` — the
June sweeps were not sub-practice-targeted. Their `search_terms` were re-captured **verbatim** from
the stocktake Annex 1 (`reference/stocktake/_local/stocktake_review.txt`), replacing an earlier
paraphrase. **No sub-practice-targeted search (F1…F6) has been run yet** — those are logged per family
when run, and are NOT covered by the generic parent search. Synthesis #114 is gated on the
per-family searches being run + logged.
