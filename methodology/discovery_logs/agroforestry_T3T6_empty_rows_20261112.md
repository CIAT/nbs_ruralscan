# empty_rows — agroforestry targeted discovery for empty headline T3/T6 rows (2026-11-12)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `agroforestry_empty_rows_2026-11-12_empty_rows`, ruleset **v1.8.1**, actual family `generic`. Registered by `scripts/register-discovery.py` on 2026-11-12: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `agroforestry_empty_rows_2026-11-12_empty_rows`, ledger per `--ledger`.


- Lane `empty_rows` (overnight tranche 2026-11-11). Discovery ruleset v1.8.1. Channel: OpenAlex title.search (EN/ES/FR/PT), Crossref DOI round-trip, Unpaywall hint. Lens (no token) and AGRIS (manual) omitted. No PDFs downloaded.

## Counts (inspected)

| cell | table | process | returned | screened | included |
|---|---|---|---|---|---|
| T3 asset_threat heat_stress | T3 | updated_lit | 123 | 123 | 7 |
| T3 asset_threat extreme_rainfall | T3 | updated_lit | 55 | 55 | 9 |

Candidates: 16 (1 reuse of existing sources).

## Verbatim queries

#### T3 / updated_lit — T3 asset_threat heat_stress

- `OpenAlex works filter=title.search:(agroforestry OR "shade tree" OR "shade trees" OR "tree seedlings" OR "farm trees" OR parkland OR "planted trees") (heat OR heatwave OR "high temperature" OR "heat stress" OR scorch OR "thermal stress") (mortality OR survival OR damage OR establishment OR dieback),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=3, inspected=3)`
- `OpenAlex works filter=title.search:agroforestry (survival OR mortality OR "tree establishment" OR "seedling establishment"),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=22, inspected=22)`
- `OpenAlex works filter=title.search:(trees OR tree) (farms OR farmland OR "on farm" OR "on-farm" OR smallholder OR parklands) (mortality OR dieback OR "die-off" OR survival),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=10, inspected=10)`
- `OpenAlex works filter=title.search:(agroforesterie OR agroflorestal OR agroflorestais OR agroforestal OR agroforestales) (chaleur OR température OR calor OR temperatura OR sécheresse OR seca OR sequía) (mortalité OR survie OR mortalidad OR sobrevivencia OR sobrevivência OR mortalidade),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=0, inspected=0)`
- `OpenAlex works filter=title.search:(agroforestry OR silvopastoral OR silvopasture OR "tree-crop") ("heat wave" OR heatwave OR "heat stress" OR "extreme temperature" OR "extreme temperatures" OR "temperature extremes"),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=18, inspected=18)`
- `OpenAlex works filter=title.search:("heat stress" OR heatwave OR "heat wave" OR "extreme heat" OR "high temperature") ("tree mortality" OR "seedling survival" OR "seedling mortality" OR "leaf scorch" OR "tree dieback") ,publication_year:>2004 sort=relevance_score:desc per-page=30 (count=9, inspected=9)`
- `OpenAlex works filter=title.search:(parkland OR "Faidherbia" OR "Vitellaria" OR "shea" OR "baobab" OR "Acacia senegal") (mortality OR dieback OR decline OR survival) (heat OR temperature OR drought OR climate),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=0, inspected=0)`
- `OpenAlex works filter=title.search:("tree planting" OR "planted trees" OR "planted seedlings" OR "restoration plantings" OR "tree-planting") (survival OR mortality OR outcomes) (global OR review OR "meta-analysis" OR drivers OR climate OR temperature),publication_year:>2004 sort=relevance_score:desc per-page=30 (count=6, inspected=6)`
- `OpenAlex works filter=title.search:(Sahel OR "Great Green Wall" OR "dryland" OR "drylands" OR "semi-arid") ("tree planting" OR seedlings OR "planted trees" OR reforestation OR afforestation) (survival OR mortality OR failure),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=27, inspected=27)`
- `OpenAlex works filter=title.search:("shade tree" OR "shade trees" OR "agroforestry tree" OR "agroforestry trees" OR "agroforestry species") ("climate change" OR heat OR temperature OR drought),publication_year:>2004 sort=relevance_score:desc per-page=30 (count=25, inspected=25)`
- `OpenAlex works filter=title.search:(coffee OR cocoa OR cacao) (agroforestry OR shade) (heat OR temperature OR extreme OR "climate change") (mortality OR damage OR vulnerability OR tolerance OR survival),publication_year:>2004 sort=relevance_score:desc per-page=30 (count=3, inspected=3)`
- `OpenAlex works filter=title.search:(agroforestry OR "tree planting" OR "farmer managed" OR "on-farm" OR "smallholder") (tree OR trees OR seedling OR seedlings) (survival OR mortality OR "establishment failure") (drought OR heat OR temperature OR climate),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=0, inspected=0)`

#### T3 / updated_lit — T3 asset_threat extreme_rainfall

- `OpenAlex works filter=title.search:(coffee OR cocoa OR cacao OR banana OR agroforestry) (hurricane OR typhoon OR cyclone OR "tropical storm") (damage OR impact OR recovery OR resilience),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=13, inspected=13)`
- `OpenAlex works filter=title.search:(agroforestry OR agroforests OR "shade trees" OR "home garden" OR "homegardens" OR "tree crops") (storm OR typhoon OR hurricane OR cyclone OR "extreme rainfall" OR "heavy rainfall" OR flood OR flooding) (damage OR loss OR resilience OR recovery OR mortality),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=7, inspected=7)`
- `OpenAlex works filter=title.search:(agroforestal OR agroflorestal OR agroforesterie OR "sistemas agroforestales" OR "café") (huracán OR huracan OR tormenta OR "lluvias intensas" OR ouragan OR cyclone OR furacão OR "chuvas intensas") ,publication_year:>1994 sort=relevance_score:desc per-page=30 (count=2, inspected=2)`
- `OpenAlex works filter=title.search:("extreme rainfall" OR "extreme precipitation" OR "heavy rainfall" OR "intense rainfall" OR "excess rainfall") (trees OR "tree crops" OR orchards OR plantations OR coffee OR cocoa) (damage OR loss OR mortality OR yield),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=2, inspected=2)`
- `OpenAlex works filter=title.search:("contour hedgerow" OR "contour hedgerows" OR "hedgerow intercropping" OR "alley cropping" OR "live barriers" OR "grass strips" OR "vegetative barriers") ("heavy rain" OR "extreme rainfall" OR "intense rainfall" OR storm OR "rainfall intensity" OR failure OR damage OR breach),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=1, inspected=1)`
- `OpenAlex works filter=title.search:(agroforestry OR coffee OR "tree cover" OR "farm trees" OR "tree crops" OR plantation) (landslide OR landslides OR "mass movement" OR "rainfall-induced"),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=33, inspected=30)`

## Screening

Title screen; every inspected record with disposition and reason in staging `screening.json`. Inclusion: practice explicit in title/source (PICOS); claim bears on the target cell. Water harvesting heat cell applies ruling #52 (a capture structure is required: mulch/residue/conservation-agriculture-only excluded).

## Stop reason

Saturation or cap per cell: last queries returned repeats or off-topic records.
