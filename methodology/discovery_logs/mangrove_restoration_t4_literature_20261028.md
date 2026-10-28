# Bounded T4 literature/stocktake discovery — mangrove_restoration

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `mangrove_restoration_t4_discovery_20261028_literature`, ruleset **v1.8.1**, actual family `mangrove_restoration__tidal_coastal`. Registered by `scripts/register-discovery.py` on 2026-10-28: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `mangrove_restoration_t4_discovery_20261028_literature`, ledger per `--ledger`.


Date: 28 October 2026. Ruleset v1.8.1. Exact family: `mangrove_restoration__tidal_coastal`. Discovery only; no PDF acquired, EV emitted, source quality ratified, human approval granted or schema changed in this lane.

## Result

26 unique recorded screening decisions: 9 stocktake and 17 fresh literature/citation records. Six candidate identities retained for intake and scope review, including explicitly labelled species/transfer holds. Candidate count is not an executable-rule count. Unknown total unique web results stays null; no search-engine total used. OpenAlex requests each returned five records, preserved separately in `mangrove_restoration_openalex_attempt.json`; duplicate titles and already known sources are not extra votes.

## Reconciliation and scope

Current SRC, acquisition queue, first-pass audit and original benchmarked stocktake were checked. Existing-source rediscoveries are marked `reuse` in screening; do not add duplicate papers or overwrite extracted/reviewed state. The source inventory and original-artifact reconciliation in the first-pass staging remain source-of-truth for previously located PDFs. Targeted searches do not establish generic parent-NbS completeness. Original stocktake contains many additional records outside this bounded screened subset.

All candidate DOIs except blank ones were round-trip matched against Crossref title/author records in `../crossref_metadata.json`. A blank DOI is intentionally unverified, not a claim that the paper lacks one. Candidates retain exact publisher/author-manuscript URLs. Acquisition needs its own verification stamp, opening-artifact identity check, team library/cache, table/figure/supplement inventory and canonical-source reuse checks. Discovery snippets cannot become quotes or thresholds.

## Verbatim queries

- `"mangrove restoration" "hydrological" "elevation" site selection suitability`
- `"restauración de manglares" "aptitud" hidrología`
- `"restauration mangrove" "hydrologie" choix sites étude`
- `"restauração manguezais" "adequabilidade" hidrologia plantio`
- `"restauración manglares" "microtopografía" "hidrológica"`
- `"mangrove restoration" "site selection" "2024" "2025" hydrology`
- `OpenAlex filter=title.search:mangrove restoration hydrological; per-page=5; mailto=p.steward@cgiar.org`
- `"Ecological engineering for successful management and restoration of mangrove forests" Lewis 2005`
- `"Determining hydrological flow paths" restoration mangrove Pérez 2020`
- `"Remote Sensing and GIS Applications for Suitable Mangrove Afforestation Area Selection" Hossain 2003`

## Screening rationale

See `screening.json` for each inspected title, URL, disposition, scope rationale and source of relevance. See `candidates.json` for separate method, intended lane, transfer/species caveats and six-axis assessment limits. Provisional tiers are capped at medium pending full-text credibility/validation assessment; no title-derived quality assignment. Within-study criterion weights are not source-quality weights or runtime MCDA weights.

## Channels and languages

Actually used: local stocktake/SRC/queue, web search in EN/ES/FR/PT, primary citation follow-up, OpenAlex title search, Crossref metadata. Lens skipped: `LENS_TOKEN` absent (token value never read/logged). AGRIS manual browser lane not run; no fabricated search. WoS/Scopus/CAB/ProQuest/Google Scholar not run, per project channel policy. Grey/tool sources surfaced by functional terms are referrals only; dedicated grey/tool agents own those processes. No independent grey/tool protocol row is claimed by this lane.

## Stop reason and remaining work

Stopped at six retained candidate identities and bounded unique screening set, not saturation. No search/acquisition/extraction-complete ledger stage marked. Source-level practice applicability, native non-forest/coastal habitat safeguards, numeric/table fidelity, original citation lineages and supplements require intake/full reading. No contact with authors. No broad paywall labels applied; OA recovery belongs to acquisition. Future publication-date anomalies remain holds rather than silently entering an as-of-28-October pool.

Mangrove caveat: planting, natural recruitment after hydrological repair and mixed ecological/operational decision analysis stay separate. Preserve vertical datum, inundation duration/frequency, spatial support and taxa. Hossain’s mudflat planting premise needs habitat-history/safeguard review. Newer Saudi paper has January 2027 issue date; held pending actual online date. Primary hydrology references prioritized over new reviews that repeat them.

## Reproducibility files

Final candidates, screening decisions and exact protocol JSON are tracked beside this report under `methodology/discovery_logs/restoration_t4_20261028/literature/mangrove_restoration/`. Central metadata verification and scope screening precede registration; candidate counts are not evidence counts.
