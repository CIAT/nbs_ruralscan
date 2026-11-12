# empty_rows — wetland_management targeted discovery for empty headline T3/T6 rows (2026-11-12)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `wetland_management_empty_rows_2026-11-12_empty_rows`, ruleset **v1.8.1**, actual family `generic`. Registered by `scripts/register-discovery.py` on 2026-11-12: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `wetland_management_empty_rows_2026-11-12_empty_rows`, ledger per `--ledger`.


- Lane `empty_rows` (overnight tranche 2026-11-11). Discovery ruleset v1.8.1. Channel: OpenAlex title.search (EN/ES/FR/PT), Crossref DOI round-trip, Unpaywall hint. Lens (no token) and AGRIS (manual) omitted. No PDFs downloaded.

## Counts (inspected)

| cell | table | process | returned | screened | included |
|---|---|---|---|---|---|
| T3 waterlogging livelihood_mitigation | T3 | updated_lit | 118 | 118 | 7 |

Candidates: 7 (2 reuse of existing sources).

## Verbatim queries

#### T3 / updated_lit — T3 waterlogging livelihood_mitigation

- `OpenAlex works filter=title.search:(humedal OR humedales OR "zonas húmedas" OR "zone humide" OR "zones humides" OR "áreas úmidas" OR várzea OR "zonas úmidas") (encharcamiento OR anegamiento OR drenaje OR engorgement OR drainage OR encharcamento OR alagamento OR drenagem) (agricultura OR agrícola OR cultivos OR agricole OR cultures OR lavoura),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=3, inspected=3)`
- `OpenAlex works filter=title.search:(rewetting OR "wetland restoration" OR "restored wetland" OR "peatland restoration" OR "re-wetting" OR "raised water table" OR "raised water level") (adjacent OR neighbouring OR neighboring OR surrounding OR "agricultural land" OR farmland OR farmers OR "off-site"),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=35, inspected=30)`
- `OpenAlex works filter=title.search:(waterlogging OR waterlogged OR "water logging") (management OR mitigation OR reclamation OR remediation OR "fish pond" OR "pond" OR "integrated farming" OR "land shaping"),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=289, inspected=30)`
- `OpenAlex works filter=title.search:(wetland OR wetlands) (restoration OR restored OR conservation OR management) (farmland OR "agricultural land" OR cropland OR crop) (flood OR flooding OR inundation OR waterlogging) (reduction OR reduce OR mitigation OR protection OR damage),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=0, inspected=0)`
- `OpenAlex works filter=title.search:(wetland OR wetlands) (restoration OR restored OR constructed OR created OR "storage") ("flood attenuation" OR "flood storage" OR "peak flow" OR "water storage" OR "farm drainage" OR "drainage water" OR "subsurface drainage"),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=116, inspected=30)`
- `OpenAlex works filter=title.search:(wetland OR wetlands OR floodplain OR marsh OR swamp OR "retention pond" OR "detention pond") (waterlogging OR waterlogged OR "water logging" OR "excess water" OR "high water table" OR "shallow water table" OR drainage) (farmland OR cropland OR crops OR agricultural OR agriculture OR "crop yield"),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=136, inspected=30)`

## Screening

Title screen; every inspected record with disposition and reason in staging `screening.json`. Inclusion: practice explicit in title/source (PICOS); claim bears on the target cell. Water harvesting heat cell applies ruling #52 (a capture structure is required: mulch/residue/conservation-agriculture-only excluded).

## Stop reason

Saturation or cap per cell: last queries returned repeats or off-topic records.
