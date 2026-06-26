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

Log via `schema_tools/search_log.py` (`log_search(...)` / CLI `log`). `suitability_family_id=""` = a table-level / all-families search (the default for a broad sweep); a specific family = a sub-practice-targeted search.

## How it locks together (one source of truth, layered)
1. **`SRCH`** = the search *protocol* (this record).
2. **Progress ledger** (`progress_ledger.csv`) = the search *status* (`searched` not_started/in_progress/done) per (NbS × table × category × family). **`ledger.check` FAILS the build if `searched=done` has no matching `SRCH` row** — you cannot claim a search without its logged protocol.
3. **Discovery logs** (`methodology/discovery_logs/*.md`) = the narrative companion (PRISMA-lite prose).
4. **`EV.ruleset_version` / `SRCH.ruleset_version`** trace every datum back to the search + the exact instructions that found it.

## Version control of the instructions (reproducibility)
The search/extraction instructions are versioned: [`methodology/RULESET_VERSIONS.md`](RULESET_VERSIONS.md) (semver · date · change) + archived prompt snapshots under [`.agents/skills/_versions/<version>/`](../.agents/skills/_versions/). Bump + snapshot on any change to the screening funnel, defect catalogue, or discovery protocol. A past search is reproducible with the snapshot its `ruleset_version` points to.

## Status (v1.0, 2026-06-26)
Backfilled the existing agroforestry searches into `SRCH` at `family=""` (table-level — the June sweeps were not sub-practice-targeted). Going forward, searches are logged **per sub-practice** so each family's coverage across the 4 processes is explicit. See the per-family gaps in the agroforestry recipe (synthesis #114 is gated on this being complete + logged).
