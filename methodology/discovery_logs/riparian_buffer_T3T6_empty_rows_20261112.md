# empty_rows — riparian_buffer targeted discovery for empty headline T3/T6 rows (2026-11-12)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `riparian_buffer_empty_rows_2026-11-12_empty_rows`, ruleset **v1.8.1**, actual family `generic`. Registered by `scripts/register-discovery.py` on 2026-11-12: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `riparian_buffer_empty_rows_2026-11-12_empty_rows`, ledger per `--ledger`.


- Lane `empty_rows` (overnight tranche 2026-11-11). Discovery ruleset v1.8.1. Channel: OpenAlex title.search (EN/ES/FR/PT), Crossref DOI round-trip, Unpaywall hint. Lens (no token) and AGRIS (manual) omitted. No PDFs downloaded.

## Counts (inspected)

| cell | table | process | returned | screened | included |
|---|---|---|---|---|---|
| T6 production_gap | T6 | updated_lit | 143 | 143 | 12 |

Candidates: 12 (1 reuse of existing sources).

## Verbatim queries

#### T6 / updated_lit — T6 production_gap

- `OpenAlex works filter=title.search:("buffer strip" OR "buffer strips" OR "riparian buffer" OR "riparian buffers" OR "conservation buffer") (economic OR economics OR "cost-benefit" OR "land taken" OR "opportunity cost" OR "farm income" OR adoption),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=26, inspected=26)`
- `OpenAlex works filter=title.search:(ribereña OR ribereño OR "mata ciliar" OR "zona ripária" OR "bande riveraine" OR "bandes riveraines" OR "zone tampon") (producción OR rendimiento OR produção OR produtividade OR rendement OR agricole OR agricultura),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=57, inspected=30)`
- `OpenAlex works filter=title.search:("riparian agroforestry" OR "riparian forest buffer" OR "multifunctional buffer" OR "riparian buffer") (biomass OR fodder OR timber OR harvest OR economic OR economics),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=53, inspected=30)`
- `OpenAlex works filter=title.search:(riparian OR streamside OR "stream bank" OR streambank) (crop OR crops OR farmland OR cropland OR pasture OR livestock) (yield OR production OR income OR loss OR economic),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=16, inspected=16)`
- `OpenAlex works filter=title.search:(riparian OR "buffer strip" OR "buffer zone") (agriculture OR farm OR farmers OR crop) (review OR "meta-analysis" OR synthesis OR "trade-off" OR tradeoff),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=17, inspected=17)`
- `OpenAlex works filter=title.search:(riparian OR "buffer strip" OR "buffer strips" OR "vegetated buffer" OR "field margin" OR "filter strip") (yield OR "crop production" OR productivity OR profitability OR "income" OR "opportunity cost"),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=111, inspected=30)`

## Screening

Title screen; every inspected record with disposition and reason in staging `screening.json`. Inclusion: practice explicit in title/source (PICOS); claim bears on the target cell. Water harvesting heat cell applies ruling #52 (a capture structure is required: mulch/residue/conservation-agriculture-only excluded).

## Stop reason

Saturation or cap per cell: last queries returned repeats or off-topic records.
