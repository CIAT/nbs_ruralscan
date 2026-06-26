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
