# Bounded T4 literature/stocktake discovery — forest_restoration

Date: 28 October 2026. Ruleset v1.8.1. Exact family: `forest_restoration__active_planting`. Discovery only; no PDF acquired, EV emitted, source quality ratified, human approval granted or schema changed in this lane.

## Result

26 unique recorded screening decisions: 12 stocktake and 14 fresh literature/citation records. Six candidate identities retained for intake and scope review, including explicitly labelled species/transfer holds. Candidate count is not an executable-rule count. Unknown total unique web results stays null; no search-engine total used. OpenAlex requests each returned five records, preserved separately in `forest_restoration_openalex_attempt.json`; duplicate titles and already known sources are not extra votes.

## Reconciliation and scope

Current SRC, acquisition queue, first-pass audit and original benchmarked stocktake were checked. Existing-source rediscoveries are marked `reuse` in screening; do not add duplicate papers or overwrite extracted/reviewed state. The source inventory and original-artifact reconciliation in the first-pass staging remain source-of-truth for previously located PDFs. Targeted searches do not establish generic parent-NbS completeness. Original stocktake contains many additional records outside this bounded screened subset.

All candidate DOIs except blank ones were round-trip matched against Crossref title/author records in `../crossref_metadata.json`. A blank DOI is intentionally unverified, not a claim that the paper lacks one. Candidates retain exact publisher/author-manuscript URLs. Acquisition needs its own verification stamp, opening-artifact identity check, team library/cache, table/figure/supplement inventory and canonical-source reuse checks. Discovery snippets cannot become quotes or thresholds.

## Verbatim queries

- `reforestation afforestation site suitability indigenous species GIS soil slope Mahdavi 2017`
- `reforestación aptitud terreno establecimiento restauración forestal análisis multicriterio`
- `reboisement aptitude station restauration forestière cartographie critères sol`
- `reflorestamento aptidão implantação restauração florestal critérios solo declividade`
- `"Determination of suitable areas" "reforestation" Mahdavi`
- `"reforestation" "suitability" soil depth restoration 2024 2025`
- `"Determination of suitable areas for reforestation and afforestation with indigenous species"`
- `"reforestation" "site suitability" "soil" "2024"`
- `"reforestación" "aptitud" "restauración" multicriterio suelo`
- `"restauração florestal" "aptidão" "plantio" multicritério`
- `OpenAlex filter=title.search:reforestation suitability; per-page=5; mailto=p.steward@cgiar.org`
- `"Change Detection and Land Suitability Analysis" Nurda 2020`
- `"Determination of suitable areas" Mahdavi Ghasemi Jafarzadeh 2017 Caspian`
- `"Determination of suitable areas for reforestation" "cjes"`
- `"Mapping Land Suitability to Guide Landscape Restoration in the Amazon" restoration plantations natural regeneration`
- `"Evaluating suitability of land for forest landscape restoration" Chen 2021 indicators`

## Screening rationale

See `screening.json` for each inspected title, URL, disposition, scope rationale and source of relevance. See `candidates.json` for separate method, intended lane, transfer/species caveats and six-axis assessment limits. Provisional tiers are capped at medium pending full-text credibility/validation assessment; no title-derived quality assignment. Within-study criterion weights are not source-quality weights or runtime MCDA weights.

## Channels and languages

Actually used: local stocktake/SRC/queue, web search in EN/ES/FR/PT, primary citation follow-up, OpenAlex title search, Crossref metadata. Lens skipped: `LENS_TOKEN` absent (token value never read/logged). AGRIS manual browser lane not run; no fabricated search. WoS/Scopus/CAB/ProQuest/Google Scholar not run, per project channel policy. Grey/tool sources surfaced by functional terms are referrals only; dedicated grey/tool agents own those processes. No independent grey/tool protocol row is claimed by this lane.

## Stop reason and remaining work

Stopped at six retained candidate identities and bounded unique screening set, not saturation. No search/acquisition/extraction-complete ledger stage marked. Source-level practice applicability, native non-forest/coastal habitat safeguards, numeric/table fidelity, original citation lineages and supplements require intake/full reading. No contact with authors. No broad paywall labels applied; OA recovery belongs to acquisition. Future publication-date anomalies remain holds rather than silently entering an as-of-28-October pool.

Forest caveat: Chen/Poccard/Nurda are promising criteria sources but broad FLR/allocation/forest-extension methods; active planting must be demonstrated in the underlying source. Ioki and Mahdavi remain species-specific; Sisian may mix restoration and plantation goals. Plantation and regeneration evidence never inherit active-planting eligibility.

## Reproducibility files

Final candidates, screening decisions and exact protocol JSON are tracked beside this report under `methodology/discovery_logs/restoration_t4_20261028/literature/forest_restoration/`. Central metadata verification and scope screening precede registration; candidate counts are not evidence counts.
