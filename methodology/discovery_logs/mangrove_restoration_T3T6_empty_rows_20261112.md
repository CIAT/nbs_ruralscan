# empty_rows — mangrove_restoration targeted discovery for empty headline T3/T6 rows (2026-11-12)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `mangrove_restoration_empty_rows_2026-11-12_empty_rows`, ruleset **v1.8.1**, actual family `generic`. Registered by `scripts/register-discovery.py` on 2026-11-12: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `mangrove_restoration_empty_rows_2026-11-12_empty_rows`, ledger per `--ledger`.


- Lane `empty_rows` (overnight tranche 2026-11-11). Discovery ruleset v1.8.1. Channel: OpenAlex title.search (EN/ES/FR/PT), Crossref DOI round-trip, Unpaywall hint. Lens (no token) and AGRIS (manual) omitted. No PDFs downloaded.

## Counts (inspected)

| cell | table | process | returned | screened | included |
|---|---|---|---|---|---|
| T3 asset_threat sedimentation | T3 | updated_lit | 152 | 152 | 11 |
| T6 water_quality_risk | T6 | updated_lit | 115 | 115 | 10 |

Candidates: 21 (0 reuse of existing sources).

## Verbatim queries

#### T3 / updated_lit — T3 asset_threat sedimentation

- `OpenAlex works filter=title.search:mangrove (burial OR "sediment burial" OR smothering OR "sediment deposition" OR sedimentation OR siltation OR "excessive sedimentation") (mortality OR dieback OR death OR survival OR seedlings OR response OR tolerance),publication_year:>1989 sort=relevance_score:desc per-page=30 (count=6, inspected=6)`
- `OpenAlex works filter=title.search:(mangrove OR mangroves) (burial OR buried OR siltation OR "sediment input" OR "sediment load" OR "sediment smothering" OR "high sedimentation"),publication_year:>1989 sort=relevance_score:desc per-page=30 (count=86, inspected=30)`
- `OpenAlex works filter=title.search:(manglar OR manglares OR manguezal OR manguezais OR mangue OR mangrove) (sedimentación OR sedimentação OR assoreamento OR enterramiento OR soterramento OR envasement OR ensablement OR sédimentation) ,publication_year:>1989 sort=relevance_score:desc per-page=30 (count=153, inspected=30)`
- `OpenAlex works filter=title.search:(mangrove OR Avicennia OR Rhizophora OR Sonneratia) (pneumatophore OR pneumatophores OR "root burial" OR "sand burial" OR "mud burial") ,publication_year:>1989 sort=relevance_score:desc per-page=30 (count=98, inspected=30)`
- `OpenAlex works filter=title.search:(mangrove OR mangroves) (restoration OR rehabilitation OR planting OR planted OR replanting) (sediment OR sedimentation OR accretion OR burial OR siltation OR "bed level"),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=105, inspected=30)`
- `OpenAlex works filter=title.search:(mangrove OR Rhizophora OR Avicennia OR Sonneratia OR Kandelia) (seedling OR seedlings OR propagule OR propagules OR saplings) (sediment OR sedimentation OR accretion OR burial OR elevation),publication_year:>1989 sort=relevance_score:desc per-page=30 (count=27, inspected=27)`

#### T6 / updated_lit — T6 water_quality_risk

- `OpenAlex works filter=title.search:(mangrove OR mangroves) (effluent OR wastewater OR "shrimp pond" OR "aquaculture effluent" OR "shrimp farm") (treatment OR removal OR filtration OR purification OR biofilter),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=62, inspected=30)`
- `OpenAlex works filter=title.search:(manglar OR manglares OR manguezal OR manguezais OR mangrove) ("calidad del agua" OR "qualidade da água" OR "qualité de l eau" OR nutrientes OR nutriments OR efluentes OR effluents),publication_year:>1994 sort=relevance_score:desc per-page=30 (count=551, inspected=30)`
- `OpenAlex works filter=title.search:(mangrove OR mangroves) (restored OR restoration OR rehabilitated OR rehabilitation OR planted OR replanted OR reforested OR reforestation) ("water quality" OR nutrient OR nutrients OR nitrogen OR phosphorus OR turbidity OR "suspended solids" OR bacteria OR "heavy metals" OR "trace metals"),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=173, inspected=30)`
- `OpenAlex works filter=title.search:(mangrove OR mangroves) ("water quality" OR "nutrient removal" OR "nutrient retention" OR filtration OR pollution OR pollutant) (review OR "meta-analysis" OR synthesis OR global),publication_year:>1999 sort=relevance_score:desc per-page=30 (count=26, inspected=26)`

## Screening

Title screen; every inspected record with disposition and reason in staging `screening.json`. Inclusion: practice explicit in title/source (PICOS); claim bears on the target cell. Water harvesting heat cell applies ruling #52 (a capture structure is required: mulch/residue/conservation-agriculture-only excluded).

## Stop reason

Saturation or cap per cell: last queries returned repeats or off-topic records.
