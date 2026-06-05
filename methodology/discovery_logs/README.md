# Discovery logs — PRISMA-lite per NbS × table

Per-NbS × per-table record of the bounded discovery sweep that produced the
corresponding evidence-register state. Markdown, not a schema register — see
[`../T4_generation_method.md`](../T4_generation_method.md) "Reproducible
discovery log (PRISMA-lite)" for the rationale.

## File naming

`<nbs_id>_<table>.md` — e.g. `agroforestry_T4.md`, `agroforestry_T6.md`,
`water_harvesting_conservation_T4.md`.

## Template

```
# Discovery log — <NbS> × <table>

**Date(s):** <YYYY-MM-DD..YYYY-MM-DD>
**Author(s):** <names>
**Seed-set rule:** T4 method §3 bounded authority-weighted seed-set.

## Sources & databases queried

- WB rural-NbS catalogue: <query / filter>
- WOCAT: <query / filter>
- EGM (3ie/Campbell/CEE): <query / filter>
- IPCC AR6 WGII: <chapter / section>
- FAO TECA + Ecocrop: <filter>
- ICRAF Agroforestree: <filter>
- Major meta-analyses (Web of Science / Scopus): <query>
- MEL/MELIA: <project list>
- ...

## PRISMA-lite counts

| Stage | Count | Notes |
|---|---:|---|
| Returned (raw) | | |
| After deduplication | | |
| After relevance screen (practice × outcome × system) | | |
| After credibility screen (six-axis rubric) | | |
| Included in SRC register | | |

## Inclusions

List of SRC entries created/updated in this pass, with their assigned
`benchmark_tier` and the axes that drove the tier.

## Exclusions

Source + reason (typically: out-of-scope NbS, low credibility, advocacy
COI, English-language gate, etc.).

## Notes

Any judgement calls worth recording — e.g. LMIC-preference tie-breaks,
seminality calls, decisions to admit Low-tier sources.
```

Logs commit alongside the per-paper sweep commits so the audit trail tracks
EV register growth.
