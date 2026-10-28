# Three-source mangrove review — 28 October 2026

This batch reviews three acquired papers together, with one combined audit and PR. The authorised lane remains mangrove tidal/coastal restoration: structural suitability where supported, with operational-risk evidence routed separately to M2b Stream B / Module 6. It does not open a new effect sweep or authorise conversion of naturally unvegetated habitats.

## Results

| Source | Main-paper accounting | New evidence | Remaining disposition |
|---|---|---|---|
| Hossain et al. (2003) | 5 pages; 2 tables; 5 figures | None | Pre-registration practice-boundary hold: newly accreted, naturally grassed mudflat afforestation is not demonstrated restoration of degraded mangrove |
| Pérez-Ceballos et al. (2020) | 20 pages; 8 figures; no main-paper data tables | None | Hydrological intervention design and outcomes retained for their appropriate method/effect lanes; supplemental DOCX and raw data remain unacquired |
| Villarreal-Rosas et al. (2024) | 14 PDF pages (2 repository pages + 12 article pages); 2 tables; 3 figures | 2 operational-risk units | All priority criteria retained outside T4; appendices S1–S6 unacquired; source `in_progress` |

The two new, unapproved units are:

- `ev_mr_governance_villarreal24_20261028`: community governance and engagement are evaluated after prioritisation, with capacity building rather than structural exclusion of low-engagement communities.
- `ev_mr_landaccess_villarreal24_20261028`: local communal assembly approval is needed to implement restoration. This is access to land for intervention, not a measured tenure-security score or a legal rule transferred to another country.

Both use `operational_risk`, retain native page quotes and separately anchored context, and have no numeric relationship, risk score, cutoff or runtime weight. Governance model-use is false because community dynamics were explicitly excluded from ROOT's objective vector. Both records come from the same study; they are different variables, not independent confirmations of one claim. No human approval was granted. No T4 response functions, effect rows or recipe changes were made.

## Coverage and retained values

`page_claim_inventory.json` accounts for every one of the 39 PDF pages and every main-paper table and figure, including continuations and explicit destinations for non-admitted claims. This is main-paper accounting, not a claim that all numeric plots or supplements have been extracted.

`hossain_tables.json` retains all five criteria, their complete 30/30/10/10/20 percent weights, all three class positions, source scores 3/2/1, twelve monthly tidal-extreme pairs, and the illustrated A/B/C inundation durations. Important unresolved points are the native-grass conversion scope, unspecified salinity units, missing middle classes, joint depth/duration interpretation and disagreement between abstract and results area estimates. A score of 1 for “not suitable” is not silently converted into a Boolean exclusion. **Question for the practice ruling:** does deliberate afforestation of newly accreted, naturally grassed mudflats belong in the authorised restoration family? Until resolved, no source/evidence registration from this paper.

`perez_values.json` retains the channel-design dimensions, named-species recovery observations, salinity comparisons, site elevations and cost comparisons with exact pages. These are intervention design, local descriptors or outcomes; they do not define establishment envelopes. The eight figures were inspected. Boxplots and regression panels remain located for a later effect/method pass; individual quantiles and coefficients were not digitised into evidence. The site-reference regression axes appear reversed relative to the methods' response/explanatory wording. “Before” and “during” restoration are also inconsistent across prose and captions. These differences remain open.

`villarreal_metrics.json` retains all ten ROOT objectives with direction and all thirty scenario-result values, plus the three community-dynamics measures. The study ranks sites within a preselected degraded area; rank percentiles and percentage of maximum objective value are not measured success probabilities. Equal weights are source planning choices, not runtime defaults. The 2-km propagule buffer cites a Rhizophora mangle study in Florida; the migration buffer has a different rationale. Maximum historical surface-water extent is not permanent inundation or percent time flooded. No unsuitable proxy was silently renamed to a canonical T4 variable.

`followups.json` records the missing supplements, relevant companion studies, the 2022 final report and the ROOT project as reproducible followups. The paper-referenced ROOT URL was not treated as an inspected or version-pinned codebase. Existing Lewis, Van Loon, Pérez-Ceballos and Teutli identities are named where relevant; rediscovery does not create duplicate independent evidence.

## Credibility and adversarial findings

Hossain: peer-reviewed, locally relevant Bangladesh study with explicit GIS classes and field-supported land classification, but old, no independent validation of its suitability scores, ambiguous salinity units and an unresolved practice boundary. Provisional medium ceiling is retained for discovery only; no SRC tier is assigned in this batch. DANIDA support is disclosed; no independence or seminality bonus is assumed.

Pérez-Ceballos: peer-reviewed empirical work in Mexico, strong method transparency and monitored hydrology/biogeochemistry. The two intervention zones differ in size, timing and channel configuration; their comparison is not randomised. Measured changes improve methodological relevance but do not justify universal microtopographic or hydroperiod thresholds. Its methodological claim of universal application is not adopted as universal ecological transfer. Source states no specific funding or competing interests. No SRC admission was needed for this method/effect inventory.

Villarreal-Rosas: medium-tier peer-reviewed modelling/planning study. Current, transparent main-paper objective set, direct collaboration with Mexican practitioners and communities, and useful operational detail. It has no observed post-restoration validation of the ranked success probabilities, and static proxies cannot represent uncertainty or sea-level/sediment dynamics. Mexico is upper-middle-income; institutional arrangements require local transfer review for LIC/LMIC applications. Practitioner involvement is a relevance strength but not independent external validation. Funding is disclosed in the source. No seminality bonus was assigned.

Adversarial checks covered omissions as well as additions. They kept every criterion and direction in the appropriate lane, prevented priority objectives becoming T4 constraints, separated short-term community capacity from hard exclusion, and retained source conflicts. In particular, Pérez-Ceballos reports planting costs of $62,689–108,828/ha and flow-path restoration of $5,300/ha, but calls the former “92 to 95% higher”. Those numbers imply approximately 92–95% lower cost for flow-path restoration, not only 92–95% higher planting cost. Original values and wording are preserved; no silent arithmetic repair or effect claim was made.

## Progress and retrospective

Queue notes were updated only for these three sources. Hossain and Pérez-Ceballos remain `acquired` with explicit holds; Villarreal-Rosas is `extracted` only in the partial sense and its SRC stays `in_progress`. Verification progress remains `in_progress`. No search was rerun or newly claimed.

The source/evidence preservation audit checks all 541 prior SRC and 5,212 prior EV records against the branch base. Existing human decisions and the global feedback cursor are untouched. The batch adds one SRC and two EV records. Main-paper accounting now covers 8 of the 29 new discovery candidates; **21 candidates plus the separate ITTO reuse task remain**, as do holds and supplements from already-reviewed sources.

This pass exercised existing rules for wrong practice, priority-versus-suitability scope, proxy equivalence, original class/weight preservation and source conflicts. No new defect category or ruleset change is claimed. Global sweep metrics are reported as a snapshot, not evidence that reviewing three sources improved the whole corpus's accuracy. Validation details are in `validation.json`; new-unit checks are in `batch_checks.json`.
