# Discovery log — Agroforestry · linear_boundary · T4

- Run `targeted_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** targeted discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 1450 | 36 | 6 |
| updated_lit | 45 | 17 | 5 |
| grey | 28 | 18 | 4 |
| tool | 2 | 2 | 1 |

### Verbatim search terms

- **stock:** `OpenAlex title.search boolean queries: (1) (windbreak OR shelterbelt OR shelterbelts) AND (suitability OR siting OR establishment OR design OR wind); (2) (shelterbelt OR windbreak) AND (crop OR yield OR agriculture OR farmland); (3) (hedgerow OR "living fence" OR "live fence" OR "contour hedge") AND (agroforestry OR suitability OR erosion OR slope OR farm); (4) ("riparian buffer" OR "vegetative buffer" OR "buffer strip") AND (suitability OR siting OR placement OR watershed OR agricultural); sort=cited_by_count:desc`
- **updated_lit:** `OpenAlex title.search, filter from_publication_date:2015-01-01, sort=cited_by_count:desc: (5) (windbreak OR shelterbelt OR hedgerow OR "living fence" OR "riparian buffer") AND (GIS OR "suitability mapping" OR "spatial prioritization" OR "spatial prioritisation" OR "multi-criteria"); (6) (windbreak OR shelterbelt OR "living fence" OR hedgerow) AND (Africa OR Sahel OR "Latin America" OR tropical OR smallholder OR "wind erosion")`
- **grey:** `WebSearch (EN+ES): "windbreak shelterbelt design site selection field manual FAO smallholder wind erosion guidelines"; "WOCAT SLM technology living fence contour hedgerow windbreak land suitability requirements"; "CIPAV cercas vivas setos forrajeros establecimiento condiciones suelo clima ganaderia Colombia"; "riparian buffer siting tool NRCS forest buffer suitability model GIS chesapeake prioritization"`
- **tool:** `GitHub API search/repositories: q="windbreak shelterbelt suitability GIS"; q="riparian buffer GIS"; q="hedgerow detection remote sensing"; q="riparian forest buffer prioritization" (Accept: application/vnd.github+json). Platforms: Maryland Watershed Resources Registry / Chesapeake riparian prioritization; WOCAT QCat.`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|

## Gaps / next iteration

The TOOL axis is the real gap: no open-source code repository with extractable, hardcoded F4 line-planting suitability weights/thresholds exists on GitHub (search totals 0-2, all low-signal); the only operational suitability model found (Maryland WRR/Chesapeake riparian scorer) is a closed web app with no pinnable source. Dedicated spatial-suitability METHOD literature for F4 is also thin (only ~5 GIS/MCDA title-hits), with the single strong match (Saskatchewan fuzzy-logic) being temperate and paywalled. LMIC coverage is uneven — good for contour hedgerows (Philippines, Kenya) and living fences (CIPAV Colombia, WOCAT), but windbreak/shelterbelt siting evidence skews heavily temperate (China, Europe, N. America); next iteration should target Sahel/dryland windbreak and African/Latin-American riparian-buffer siting rules, and snapshot specific WOCAT technology records for structured extraction.
