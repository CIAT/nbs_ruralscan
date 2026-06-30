# v1.1 (2026-06-29) — search-protocol clarifications

Extract-evidence skill prompts are **unchanged from v1.0** (carried forward verbatim).
This bump records changes to the **discovery search protocol** only — see
`methodology/search_protocol.md` (the version-controlled protocol doc):

1. **Generic vs sub-practice search** — `family=""` = practice-wide parent search;
   `family=F#` = sub-practice-targeted. Union of sub-practice searches ≠ parent. No summing.
2. **Verbatim search-term capture** — `SRCH.search_terms` = exact query string run; never a
   paraphrase. Cite the source file in `SRCH.note`.
3. **Synonym policy** — practice searches OR the full synonym set; sub-practice searches inherit
   parent synonyms + add family vocab; any omission is a logged decision.

Trigger: 2026-06-29 finding that the backfilled stocktake `search_terms` were a paraphrase that
dropped the climate block + synonyms and misfiled `silvopastoral` as a topic.
