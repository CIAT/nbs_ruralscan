# Forest active planting and mangrove T4: bounded first pass

28 October 2026. Base `f18ff3252f14d0b7c3594a6babe96a4039e2710e`, latest main when work began. Hardening PR #464 was merged before this worktree was created. Extraction ruleset **v1.8.0**, including its archived snapshot, was used. This task explicitly authorised T4; pilot/runtime work remains with Diego and Brayden.

## Result and limits

This is a reproducible **evidence and held-rule first pass**, not a calibrated or spatially executable release. Eight new claims from four already registered, team-accessible sources passed central staging gates and independent adversarial review. None received human approval. The current reviewed-only compiler therefore produces no executable T4 mapping for either recipe. The new header-only CSVs express that state; they do not mean that restoration is unsuitable or that no evidence exists.

The forest CSV previously contained 11 unapproved generated mappings, including a retired mangrove-family mapping and a plantation reference left in active planting. The starting CSV is preserved in the forest audit directory. Reviewed-only regeneration removes those mappings. All existing EV rows, prior reviews and the independent forest families remain intact. Unreviewed diagnostic trials are retained separately and are not approved response options. No agroforestry mask, score scale, aggregation or weight vector is inherited.

| Scope | Starting active T4/operational EV | Added | Current active | Current approved |
|---|---:|---:|---:|---:|
| All forest families | 210 | 3 | 213 | 0 |
| Forest active planting | 71 | 3 | 74 | 0 |
| Mangrove tidal/coastal | 39 | 5 | 44 | 0 |

Forest starts with 110 structural and 100 operational records; additions are two structural and one operational. Mangrove starts with 12 structural and 27 operational; additions are four structural and one operational. Forest's one previously dropped T4 record remains dropped. Forest has 53 reporting sources across active records; mangrove has 17. These are not screened-corpus denominators.

## Reconciliation before extraction

The lane inventories reconcile SRC, EV, acquisition queue, SRCH/discovery logs, source artifacts, stocktake papers and review history. The independent reviewer inspected the shared review log, dashboard decisions and pending decision files in both the main checkout and prior handoff worktree. No matching historical decisions were found for the starting 249 active T4/operational records in those surfaces. Mangrove effect records do have earlier decisions; those were not mistaken for T4 approvals. No inference was made from `reviewer_ok` alone, no pending review was overwritten, and no blanket repeat-review assignment was issued.

The forest inventory distinguishes passive regeneration, assisted regeneration, active planting, protection/CBFM, plantations and cross-family material. The standalone signed mangrove family supersedes the historical forest F4 proposal. Planting versus ecological/hydrological restoration stays explicit within its one approved family.

Existing source IDs were reused. The WB Bangladesh source was already registered for mangrove effect work; its new T4 work is recorded against that same identity in `artifact_identity.json`, preserving method references to Gijón Mancheño and World Bank rather than claiming an independent model lineage. No duplicate source vote or silent new SRC scope was created.

Exactly one SRCH row explicitly covers mangrove/its old family for T4 (grey, September 2026). Keyword mentions in other searches are not mangrove search completion. Forest's existing family/process logs remain available in `search_protocol_existing.csv`. No new literature search was run or backfilled: original scoping papers were still available to recover. Stocktake, updated-literature, grey and tool gaps remain distinct; none is stamped complete by this pass.

### Original scoping-library recovery

Three priority terrestrial stocktake PDFs and all eight mangrove stocktake PDFs were found in the team OneDrive/SharePoint stocktake mirror. Their prior absence from SRC/queue/cache matching was an **intake/reconciliation gap**, not absence of literature. Exact paths, hashes and unverified stocktake identities are retained. DOI/title matching and canonical library intake remain required before registering them. Stocktake DOI values in these inventories are explicitly unverified candidates, not approved SRC/queue metadata.

Two additional scoping papers were read without creating EV:

- **Rajaonarivelo and Williams (2022), Madagascar:** 18 pages; Tables 4–5 visually inspected. This is an FLR priority model. Forest distance is justified through natural-regeneration seed supply; soil erosion is restoration need; access is operational. The reported ecological/socioeconomic hierarchy and weights cannot become an active-planting establishment vector. Candidate source values are retained in the bounded source note below.
- **Aduana-Alcantara et al. (2023):** all nine pages read; pages 3–5 visually inspected. Four WLC inputs (elevation, slope, precipitation, air temperature), equal weights assumed, ordinal scores 1–4. Referenced Tables 1–2 and Figure 2 are absent from this artifact. The reported 8–42°C short-period tolerance cannot be relabelled annual-mean calibration. Its 30-arcsecond inputs and elevation-as-inundation proxy remain source limitations. See `aduana_inventory.json`.

Other recovered originals remain queued for metadata/intake and full reading, not counted as completed extraction. No new broad discovery is justified until this existing pool is reconciled.

## Bounded source coverage

Three registered forest sources were inspected: Zomer, Oliveira and Fahrudin. The interpreted inventory has 61 coverage items; the 372 machine table rows are navigation output, not a claim that each was independently reviewed. Two registered mangrove sources were inspected: GMA guidelines and World Bank Bangladesh. The mangrove inventory has 92 selected claim/table/figure/hold rows and a 193-page accounting that explicitly marks unswept pages. Supplement and figure omissions remain holds. Full-corpus or full-source completion is not claimed.

The eight admitted claims retain categorical choices, habitat history, local tidal datums, method prerequisites and operational feasibility without inventing response scores. The staged inundation-frequency candidate was withdrawn before ingestion because frequency is not duration. No ontology substitution was made.

### Rules held from execution

| Source/claim | What is retained | Why execution is held |
|---|---|---|
| Chazdon population classes | Wide-scale versus mosaic restoration context | “Typically below 10/km²” is not a planting limit; the following class also includes restoration plantations |
| Zomer CDM-AR | Original cover, aridity, elevation, land-use classes; 1990 eligibility and 1991 proxy context | Historical programme/productivity screen includes plantations/ANR/agroforestry and excludes enrichment; not a universal planting envelope |
| Zomer protected areas | Source map exclusion | No evidence of a universal legal ban on restoration inside protected areas |
| Oliveira slope | Cited planting difficulty above 75% plus actual inclusion of those slopes | Unconditional ceiling contradicts source allocation; cited primary and supplements remain outstanding |
| Fahrudin | Target domain, ES priority inputs and wildfire-model importance | Equal weights/Gini values are not establishment suitability weights; soil-depth/data-source ambiguities remain |
| GMA inundation | Species-dependent establishment guidance | “Most species” does not justify a universal 50% ceiling; hydroperiod denominator and target community matter |
| GMA elevation | Mean sea level to highest astronomical tide, with indicative site-varying planes | No transferable absolute-metre function or terrestrial DEM equivalence |
| GMA historical habitat | Prior natural mangrove occurrence and cause of loss | Requires explicit habitat-history/safeguard mapping, not a blanket current-cover mask |
| WB Bangladesh proximity | Regional 10 km screening choice, joint foreshore/embankment/land-use context | Benefit-oriented constrained AOI, unresolved model lineage, no global exclusion tail |
| WOCAT environment | Observed case conditions | Observations do not create general cutoffs |

Hard legal exclusions require applicable local law and an explicit dataset crosswalk. Native non-forest ecosystems are not treated as planting opportunities merely because canopy is low. Soft tenure, access, labour, finance and governance remain M2b/M6 references. No species envelope is admitted to a general restoration function.

## Counts, datasets and weights

`coverage.csv` separates recorded reporting sources, explicit variable use, direction and approved calibrated contributors by family, role, scope and variable. Exact source/evidence memberships are inspectable. Shared-source or unresolved secondary lineage is not claimed independent agreement. Unknown screened N and headline n/N percentages remain blank; quality-weighted support is also blank. Within-study source weights are retained where observed and are not runtime weights.

`dataset_requirements.csv` records VONT candidates, existing context-binding candidates, canonical units and scale constraints. These are **input requirements and existing candidates**, not newly approved bindings. Mangrove elevation requires local tidal references; hydroperiod needs duration/frequency/level distinguished; proximity requires mangrove habitat rather than a generic terrestrial forest layer. Native-ecosystem and historical-land-use gates still require explicit policy and data decisions. No spatial data were downloaded or tested.

Developer CSV/JSON packages rebuild the authoritative CSV and preserve all relevant evidence accounting, operational references, unknowns, empty approved function pools and blocked readiness. There are no calibrated response curves to draw. Existing dashboard Studies panels show source claims and directions; function panels explicitly contain no approved curve rather than a fabricated response. Package conformance examples cannot exercise a nonexistent function; regression tests instead verify absent approval, unknown weights, method separation, provenance-note freshness and evidence visibility.

## Review workflow and technical repairs

All review remains in the existing dashboard. Forest and mangrove now use its existing T4 panels, with separate snapshots. Eighteen source-audit notes appear on the same QA/QC evidence cards, with the extracted rule, intended use, source check and remaining decision. Responses use the existing card controls. Notes are pinned to evidence identity/location/meaning; semantic edits invalidate them. They do not modify approvals.

Technical fixes made without methodological decisions:

1. New compiler rows no longer receive an invented equal-weight default; existing configured values are preserved without calling them approved.
2. Developer and dashboard text no longer inherit agroforestry's aggregation, host-combination or score conventions.
3. Empty-core dashboards default to structural holds even when operational references are linked.
4. T4 model-use, reported-value and tidal-reference metadata is accepted by the role-specific context gate; effect claims retain their stricter vocabulary and shared context checks remain enforced.
5. The land-class checker now recognises “agricultural”, “forested”, “tundra” and “non-vegetated”. Two new categorical records auto-quarantined by that lexical defect were reopened through the audited review API, without approval.
6. Existing clarification replies support all T4/operational recipes, not only agroforestry.
7. Standalone T4 recipes appear without requiring fabricated T0 metadata; every recipe exposes the existing all-systems view.

## Genuine decisions remaining

These are not requests to reapprove completed family decisions or clear technical errors:

- Which historical programme/regional source profiles, if any, may transfer to the active-planting use cases, and under what native-ecosystem, enrichment and land-history conditions? No candidate global mask is activated.
- How should distinct growing-season temperature, tidal elevation, inundation frequency/duration/level and unmapped salinity/redox variables be represented and bound? Proxy substitution remains prohibited.
- Which compatible source functions, aggregation and criterion weights should be selected after admissible numeric tables and ecological contexts are established? Current evidence does not justify offering a ready global vector.

Missing originals, missing tables/supplements, code snapshots and metadata intake are work holds, not methodological questions for Pete. No mangrove family split or species/community maximum is proposed as approved.

## Reproduction and validation

See [regeneration commands](../../handoff/restoration-t4-first-pass/REGENERATE.md). The source audit folders contain immutable first-pass inventories; rerun extraction scripts write only staging. Central ingestion preserves review state: exact duplicates are idempotent, while replay of the original staging after the audited reopen refuses the changed attribution rather than overwriting it. Developer exports reject drift from the audited recipe and verify all required input/output hashes.

The retrospective is recorded in [the bounded retrospective](../../pipeline/t4_audit/forest_restoration/first_pass_2026-10-28/RETROSPECTIVE.md). Progress remains `verified=in_progress` for the touched existing lanes; no source-complete, search-complete or reviewed-complete claim was added. The global learning cursor was not advanced beyond uninspected feedback.

Validation: full suite **952 passed**, followed by **19 passed** for the final dashboard-discovery regression and historical review-meaning checks. Ruff lint/format, focused type checks, schema structure and both developer-package manifests pass. Source scripts reproduce three forest and five mangrove staged claims. Browser checks confirm recipe switching, all-systems operational references, active-planting structural holds and standalone mangrove visibility. No spatial execution or human approval was performed.
