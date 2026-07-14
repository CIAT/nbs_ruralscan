# Ruleset versions — search & extraction instructions

Semantic version log for the **discovery-search + evidence-extraction instructions** (the
extract-evidence skill + the search protocol). Every `SRCH.ruleset_version` and
`EV.ruleset_version` pins to a version here, so any past search/extraction is reproducible
with the **exact** instructions that governed it. The full prompt text for each version is
archived under [`.agents/skills/_versions/<version>/`](../.agents/skills/_versions/).

**Bump + snapshot whenever** the extract-evidence skill, the screening funnel/criteria, the
search protocol, or the discovery channels change. Patch = clarification; minor = new
rule/defect-code/check; major = a process change.

| version | date | scope of change | snapshot |
|---|---|---|---|
| **v1.0** | 2026-06-26 | Baseline. Formalises the search + extraction instructions used through the June 2026 agroforestry sweeps: the 4 discovery processes (stock · updated_lit · grey · tool); the 5-step screening funnel (frame · source-type · relevance · six-axis credibility · saturation-stop); the extract-evidence defect catalogue incl. wrong_table/wrong_practice/relationship_missed/constrained_aoi/uninterpretable_weight/speculative/insufficient_context; grey-lit positive-bias discount; PICOS practice-in-source; deterministic guards (validate_sources · check_numbers · check_scope · check_picos · quarantine). | `.agents/skills/_versions/v1.0/` |
| **v1.1** | 2026-06-29 | Search-protocol clarifications (no extraction-skill change). (1) **Generic vs sub-practice search** — `family=""` is the practice-wide *parent* search; `family=F#` is sub-practice-targeted; the union of sub-practice searches ≠ the parent (no summing); a family with no targeted row is "covered by the generic net, not targeted", never "done". (2) **Verbatim search-term capture** — `SRCH.search_terms` is the exact query string run (from config/Annex/run-script), never a from-memory paraphrase; cite the source file in `SRCH.note`. (3) **Synonym policy** — practice searches OR the full synonym set; sub-practice searches inherit parent synonyms + add family vocab; omission is a logged decision. Prompted by the 2026-06-29 finding that backfilled stocktake terms were a paraphrase that dropped the climate block + synonyms + misfiled `silvopastoral`. | `.agents/skills/_versions/v1.1/` |
| **v1.2** | 2026-07-14 | Extract-evidence defect-catalogue additions (2026-07 sweep-retro). (1) **#15 Species/crop evidence → TAG + KEEP, never drop** — route per-taxon claims via `claim_scope`+`taxon` (synthesis filters from practice T4 but retains for reuse); the mis-tag (species claim left `practice_technology`) is the defect. New guard **`check_species.py`**. (2) **#13 `unusable_value`** (renamed from `uninterpretable_weight`) — broadened to weight-with-no-scale OR land-cover-with-no-class-list; new `check_scope` signal `land_cover_no_classes`. (3) new `check_scope` `land_capability` signal for `constrained_aoi` (residual/marginal-land classifications). (4) reason-code cleanup: `cross_row_stitch`→`table_error`; per-card drop now requires a coded reason. Trigger: triage of 165 unincorporated QA decisions. | `.agents/skills/_versions/v1.2/` |
