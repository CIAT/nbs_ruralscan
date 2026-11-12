# empty_rows — forest_restoration targeted discovery for empty headline T3/T6 rows (2026-11-12)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `forest_restoration_empty_rows_2026-11-12_empty_rows`, ruleset **v1.8.1**, actual family `generic`. Registered by `scripts/register-discovery.py` on 2026-11-12: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `forest_restoration_empty_rows_2026-11-12_empty_rows`, ledger per `--ledger`.


- Lane `empty_rows` (overnight tranche 2026-11-11). Discovery ruleset v1.8.1. Channel: OpenAlex title.search (EN/ES/FR/PT), Crossref DOI round-trip, Unpaywall hint. Lens (no token) and AGRIS (manual) omitted. No PDFs downloaded.

## Counts (inspected)

| cell | table | process | returned | screened | included |
|---|---|---|---|---|---|
| T3 wind_cyclone livelihood_mitigation | T3 | updated_lit | 127 | 127 | 8 |

Candidates: 8 (0 reuse of existing sources).

## Verbatim queries

#### T3 / updated_lit — T3 wind_cyclone livelihood_mitigation

- `OpenAlex works filter=title.search:(Casuarina OR "coastal plantation" OR "coastal plantations" OR "coastal vegetation" OR "coastal forest") (cyclone OR tsunami OR storm OR typhoon) (protection OR damage OR mitigation),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=78, inspected=30)`
- `OpenAlex works filter=title.search:("coastal afforestation" OR "coastal green belt" OR "coastal greenbelt" OR "green belt" OR "bio-shield" OR bioshield OR "coastal shelterbelt" OR "coastal shelter forest" OR "protective forest") (cyclone OR typhoon OR storm OR hurricane OR wind OR protection),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=53, inspected=30)`
- `OpenAlex works filter=title.search:(bosque OR bosques OR reforestación OR floresta OR reflorestamento OR forêt OR reboisement OR "brise-vent" OR "cortinas rompevientos" OR "barreras rompevientos" OR "quebra-vento") (huracán OR ciclón OR viento OR vendaval OR cyclone OR vent OR furacão OR ventos) (daños OR protección OR danos OR proteção OR dégâts OR protection),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=5, inspected=5)`
- `OpenAlex works filter=title.search:(forest OR forests OR "tree cover" OR reforestation OR "planted forest" OR plantation OR "coastal forest") (cyclone OR typhoon OR hurricane OR windstorm) (protection OR damage OR household OR crops OR livelihoods OR houses OR losses),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=180, inspected=30)`
- `OpenAlex works filter=title.search:(shelterbelt OR shelterbelts OR windbreak OR windbreaks OR "coastal shelterbelt" OR "bioshield" OR "green belt" OR greenbelt) (cyclone OR typhoon OR hurricane OR storm OR wind) (damage OR protection OR crop OR houses OR mitigation),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=33, inspected=30)`
- `OpenAlex works filter=title.search:(trees OR "tree cover" OR forest OR forests OR vegetation) (cyclone OR hurricane OR typhoon) (household OR households OR "housing damage" OR "house damage" OR "crop damage" OR "agricultural damage" OR "agricultural losses" OR "economic losses" OR deaths),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=4, inspected=4)`

## Screening

Title screen; every inspected record with disposition and reason in staging `screening.json`. Inclusion: practice explicit in title/source (PICOS); claim bears on the target cell. Water harvesting heat cell applies ruling #52 (a capture structure is required: mulch/residue/conservation-agriculture-only excluded).

## Stop reason

Saturation or cap per cell: last queries returned repeats or off-topic records.
