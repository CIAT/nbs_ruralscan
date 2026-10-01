# Round 2 discovery: grey literature + WOCAT practice database (WH + FR, T4)

**Date:** 2026-09-30 · **Run:** `round2_grey_wocat_2026-09` · **Ruleset:** v1.6.0 · **By:** Namita-J / Claude

Round 1 corpora were built largely for T3/T6 (effects and costs), so few sources state
where a practice fits. Round 2 targets the two channels that do: **authoritative agency
guidance** (#4 in the options note) and the **WOCAT SLM technologies database** (#2).
Every source is tagged `SRC.extraction_run_id = round2_grey_wocat_2026-09`, so the QA/QC
dashboard's **Search round** filter separates it from Round 1.

## Decisions (Namita, 2026-09-30)

- DOI-less sources: a **title check** replaces the DOI round-trip (`verify_metadata.py
  verify-titles`), plus a publisher-domain download.
- Cap of **15 WOCAT sheets per family**, one per country first.
- **Timber plantations / woodlots are out of scope** (production forestry, not restoration).
- WOCAT records are kept as **down-weighted expert assertion**, as observed-presence
  evidence rather than thresholds.

## WOCAT SLM technologies database

Title search at `wocat.net/en/database/list/?type=technologies&q=<term>`, 56 queries over
11 families (terms in `SRCH`).

| Stage | Count |
|---|---|
| Unique technologies retrieved | 143 |
| Excluded at title screen (FMNR, agroforestry systems, paddy, high-income, plantations) | 46 |
| Excluded by the 15-per-family cap | 21 |
| Included and acquired | 76 |
| Passed the title check | 76 |
| Yielded units (2 have the section split across a page break) | 74 |

**314 units**: aridity 73, slope 62, rainfall 53, soil texture 51, soil depth 50, water
table 25. 15 are `crop_specific` (olive, tea, maize sheets).

**How they are used.** Each sheet says where ONE documented case is applied, and every
sheet carries the same fields. So the records are `observed_presence` evidence: they are
catalogued and reviewable, but the engine keeps them out of support percentages and
threshold synthesis (`recipe.family.is_observed_presence`). Their intended use is an
**observed envelope across many cases**, which is a synthesis feature not built yet.

**Caught by the title check:** the legacy qcat endpoint `/summary/<id>/` uses a different
id scheme. WOCAT #1336 "Fanya juu terraces (Kenya)" came back as "Rainwater Cellars
(China)". All sheets were re-fetched from `wocat.net/en/database/technologies/<id>/pdf/`.

## Grey literature

| Document | Acquired | Units | Note |
|---|---|---|---|
| Critchley & Siegert 1991, FAO water harvesting manual, ch. 5 | web snapshot | 19 | per-technique 'Suitability' blocks |
| Mekdaschi Studer & Liniger 2013, WOCAT water-harvesting guidelines | PDF | 22 | group overviews; embedded case sheets skipped |
| Liniger et al. 2011, SLM in Practice (TerrAfrica/FAO) | PDF | 8 | group 'Applicability' blocks |
| Global Mangrove Alliance 2023, mangrove restoration guidelines | PDF | 3 | first evidence for FR `mangrove_coastal` |
| FAO 2010, Guidelines on spate irrigation | PDF | 0 | design and hydraulics, no siting thresholds |
| FAO 2015, Forestry Paper 175 (drylands restoration) | PDF | 0 | process guidance |
| ITTO 2020, FLR guidelines (PS-24) | PDF | 0 | process guidance |
| IUCN / WRI 2014, ROAM guide | PDF | 0 | assessment framework; no thresholds |
| Oweis, Prinz & Hachum 2001 (ICARDA) | PDF (scan) | — | **needs OCR** |
| Hudson 1987, FAO Soils Bulletin 57 | — | — | HTML-only on FAO; snapshot pending |
| Mati 2007, 100 ways to manage water | — | — | no live publisher copy |
| Lewis & Brown 2014, ecological mangrove rehabilitation | — | — | only on a third-party archive (fails the domain rule) |
| FAO 2019, ANR manual | already registered | — | registered for agroforestry; FR re-read pending |

**52 units** from grey literature, all `literature_relationship` / `expert_assertion`, so
they can set thresholds (weighted 0.5 in synthesis).

## Also caught (older queue rows, not registered)

- `comparing_mcda_prioritize_wetland_sites_2017`: the cached PDF is a different 2022
  paper.
- `floodplain_restoration_flood_risk_lower_missouri_2015`: the cached file is the whole
  edited book, not the chapter.

## Families that had no evidence before this round

| Family | Units now |
|---|---|
| water_harvesting__spate | WOCAT 5 sheets + Critchley 5 + WOCAT guidelines 2 |
| water_harvesting__rooftop | WOCAT 2 sheets + WOCAT guidelines 2 |
| forest_restoration__mangrove_coastal | WOCAT 3 sheets + GMA 3 |
| forest_restoration__protection_cbfm | WOCAT 2 sheets |
