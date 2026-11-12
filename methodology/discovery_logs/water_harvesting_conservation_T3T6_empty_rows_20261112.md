# empty_rows — water_harvesting_conservation targeted discovery for empty headline T3/T6 rows (2026-11-12)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `water_harvesting_conservation_empty_rows_2026-11-12_empty_rows`, ruleset **v1.8.1**, actual family `generic`. Registered by `scripts/register-discovery.py` on 2026-11-12: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `water_harvesting_conservation_empty_rows_2026-11-12_empty_rows`, ledger per `--ledger`.


- Lane `empty_rows` (overnight tranche 2026-11-11). Discovery ruleset v1.8.1. Channel: OpenAlex title.search (EN/ES/FR/PT), Crossref DOI round-trip, Unpaywall hint. Lens (no token) and AGRIS (manual) omitted. No PDFs downloaded.

## Counts (inspected)

| cell | table | process | returned | screened | included |
|---|---|---|---|---|---|
| T3 heat_stress livelihood_mitigation | T3 | updated_lit | 182 | 182 | 7 |

Candidates: 7 (0 reuse of existing sources).

## Verbatim queries

#### T3 / updated_lit — T3 heat_stress livelihood_mitigation

- `OpenAlex works filter=title.search:("conservation agriculture" OR "no-till" OR "zero tillage" OR mulch OR mulching OR "residue") ("climate stress" OR "climate extremes" OR "high temperature" OR "heat stress" OR "terminal heat" OR "warm" OR "temperature") (meta-analysis OR "meta-regression" OR review OR "adaptive capacity"),publication_year:>2004 sort=relevance_score:desc per-page=30 (count=11, inspected=11)`
- `OpenAlex works filter=title.search:("conservation agriculture" OR "no-till" OR "zero tillage" OR "residue retention" OR "crop residue") ("heat stress" OR "terminal heat" OR "high temperature" OR "heat" OR "temperature extremes") (yield OR wheat OR maize OR crop),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=6, inspected=6)`
- `OpenAlex works filter=title.search:("cosecha de agua" OR "captación de agua" OR "conservación de suelos" OR "colheita de água" OR "captação de água" OR "conservation des eaux et des sols" OR "collecte des eaux" OR paillage OR acolchado OR "cobertura morta") ("estrés térmico" OR "estresse térmico" OR "stress thermique" OR "alta temperatura" OR "altas temperaturas" OR "température du sol" OR "temperatura do solo" OR "temperatura del suelo"),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=10, inspected=10)`
- `OpenAlex works filter=title.search:(zaï OR "demi-lunes" OR "cordons pierreux" OR "diguettes" OR "collecte des eaux" OR "captación de agua de lluvia" OR "cosecha de agua" OR "captação de água de chuva" OR "barraginhas") (température OR chaleur OR climat OR temperatura OR calor OR clima OR rendement OR rendimiento),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=0, inspected=0)`
- `OpenAlex works filter=title.search:("water harvesting" OR "rainwater harvesting" OR "water points" OR "farm ponds" OR "earth dams" OR "sand dams") (livestock OR cattle OR goats OR pastoralists) (heat OR temperature OR "dry season" OR drought),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=2, inspected=2)`
- `OpenAlex works filter=title.search:("farm pond" OR "farm ponds" OR "harvested water" OR "harvested rainwater" OR "rainwater harvesting") ("supplemental irrigation" OR "supplementary irrigation" OR "life-saving irrigation" OR "critical irrigation"),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=45, inspected=30)`
- `OpenAlex works filter=title.search:("rainwater harvesting" OR "water harvesting" OR "in-situ water harvesting" OR "in situ moisture conservation") ("climate change" OR temperature OR heat OR warming OR "climate extremes" OR "extreme events") (yield OR crop OR crops OR adaptation OR resilience),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=52, inspected=30)`
- `OpenAlex works filter=title.search:(zai OR "planting pits" OR "planting basins" OR "half-moon" OR "half moons" OR demi-lunes OR "tied ridges" OR "tied ridging" OR "contour bunds" OR "stone bunds" OR terraces OR "micro-catchment" OR "microcatchment" OR "farm pond" OR "farm ponds") (temperature OR heat OR warming OR "climate change" OR "climate variability" OR "dry spell" OR "dry spells"),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=176, inspected=30)`
- `OpenAlex works filter=title.search:("supplemental irrigation" OR "supplementary irrigation" OR "deficit irrigation" OR irrigation) ("heat stress" OR "heat wave" OR heatwave OR "extreme heat" OR "high temperature") (mitigate OR mitigation OR alleviate OR alleviation OR buffer OR reduce OR cooling),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=35, inspected=30)`
- `OpenAlex works filter=title.search:("terminal heat" OR "heat stress" OR "high temperature") (wheat OR maize OR chickpea OR rice OR sorghum OR millet) (mulch OR mulching OR "residue retention" OR "zero tillage" OR "conservation agriculture" OR "rainwater harvesting" OR "soil moisture conservation"),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=6, inspected=6)`
- `OpenAlex works filter=title.search:("water harvesting" OR "rainwater harvesting" OR "soil water conservation" OR "soil and water conservation" OR mulching OR mulch OR "conservation agriculture" OR "tied ridges" OR zai OR "planting pits" OR "farm pond" OR "supplemental irrigation") ("heat stress" OR "high temperature" OR "heat wave" OR heatwave OR "extreme heat" OR "terminal heat" OR "canopy temperature" OR "soil temperature"),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=354, inspected=30)`

## Screening

Title screen; every inspected record with disposition and reason in staging `screening.json`. Inclusion: practice explicit in title/source (PICOS); claim bears on the target cell. Water harvesting heat cell applies ruling #52 (a capture structure is required: mulch/residue/conservation-agriculture-only excluded).

## Stop reason

Saturation or cap per cell: last queries returned repeats or off-topic records.
