# Priority spatial-resource coverage closeout

2 November 2026. Scope: the current agroforestry, forest-restoration and mangrove T4 recovery work, with a separate check of project-named tools. This is an inventory/reconciliation audit, not a new discovery sweep, extraction, human review or assertion of coverage across every NbS. Baseline and reproducible stocktake counts are in `inventory_summary.json`.

## Decision

**High-priority resource coverage is not yet demonstrated complete.** The main remaining problem is reconciling and using resources already held, not searching for more literature. Freeze the list below. Secondary references and additional tools must not become an open-ended follow-up chain.

The frozen peer-reviewed stocktake has **22 High-labelled rows in the focal categories; all 22 PDFs were located by normalized filename in the team-library mirror.** This establishes file availability, not bibliographic identity or full-text review. Eight have identified canonical SRC records with evidence; eight are priority method/identity gaps; six require separate species/crop/conservation scope treatment or are misclassified. The original stocktake's labels and DOI strings are not authoritative metadata. No DOI was newly promoted or inferred.

`priority_stocktake.csv` lists every row, file location, known canonical identity, current EV counts and disposition. “Evidence present” does not mean all criteria are captured, calibrated or approved. No overall completion percentage is claimed.

## Fixed priority closeout list

These eight studies already exist in the team stocktake; resolve their identity and source-method coverage as one batch. Start with opening-page identity and existing aliases, then assess actual spatial variables, directions, source values and the distinction between establishment eligibility and investment priority. Do not register all eight automatically.

| Resource | Why it belongs in this fixed batch | Current disposition |
|---|---|---|
| Crouzeilles 2020, targeted natural regeneration | Direct practice-targeting method | File present; no reconciled canonical identity/evidence found |
| Molin 2018, landscape-scale cost-effective restoration | Compares restoration approaches spatially | File present; no reconciled canonical identity/evidence found |
| Rajaonarivelo & Williams 2022, Madagascar suitability | Explicit LMIC forest-restoration suitability | File present; no reconciled canonical identity/evidence found |
| Orsi & Geneletti 2009, Chiapas restoration priorities | Explicit LMIC landscape-restoration method | File present; priorities must be separated from suitability |
| Morán-Ordóñez 2022, Costa Rica multi-objective planning | Spatial trade-offs and restoration pathways | File present; do not substitute the different Langhans 2022 record |
| Valente 2021, forest-restoration water-service priorities | Explicit spatial criteria and service-priority method | File present; benefit priority is not automatically T4 eligibility |
| Blanco-Sacristán 2022, Red Sea mangrove potential | Direct mangrove spatial-potential method | File present; habitat history/species/native-nonforest scope needs review |
| Strassburg 2020, global ecosystem-restoration priorities | Major spatial optimization method already selected as High | Canonical queue acquired; no EV; priority/optimization referral may be the correct outcome |

Two High-labelled grey entries also require a fixed identity/coverage resolution:

1. **Chazdon & Guariguata, Decision support tools for forest landscape restoration (2018).** Publisher identity verified at [CIFOR-ICRAF](https://www.cifor-icraf.org/knowledge/publication/6792/). This is a different publication from the fully inventoried IUFRO World Series 34. No matching canonical title record or full-method audit found. Review this synthesis itself; do not chase every tool it cites.
2. **UN-REDD cocoa-agroforestry opportunity mapping, Côte d’Ivoire (2021).** High stocktake entry lacks reconciled identity/coverage. Its recorded link points to a SARE project, not a verified copy of the named report. Resolve the identity before acquisition or extraction; do not assume the link proves coverage.

These are ten fixed source dispositions to resolve, not ten promised new evidence sources. The existing seven-codebase audit has one shared code-admission issue, separately recorded below; no need to reread all repositories.

## Already covered: reuse rather than repeat

- **ROAM:** 64 native spreads, 28 numbered tables plus Appendix A1, 22 figures and 133 criterion/candidate rows accounted for in `../roam_wocat_t4_20261102/`. No EV is a valid result where claims are priorities, unresolved mappings or examples.
- **WRI global forest-restoration atlas:** two companion publications, seven pages, original canopy/population/method values and limitations preserved in `../t4_primary_methods_20261102/atlas_review.md`. Same lineage; not two independent validations.
- **IUFRO WS34:** 75 pages and complete table accounting in `../t4_iufro_review_20261102/`. This does not cover the distinct CIFOR tools synthesis above.
- **Mangrove restoration-potential report:** `worthington_spalding_2018_restoration_potential` has three active T4 and two operational units; full guidance inventory and transfer holds remain in `../mangrove_guidance_20261029/`. GMW display code was inspected separately; displaying a score is not reconstructing its method.
- **Lewis 2005:** already read and inventoried in `../restoration_source_review_20261028/`, including its table and tidal figures. The previous suggestion to reacquire it was duplicate work and is cancelled. Reuse the existing hydroperiod holds if relevant; no new primary-reference chase.
- **Williams 2024 and Cook-Patton 2020:** registered evidence exists. Their paper-level representation does not establish complete code or supplement coverage; do not reopen them solely because a companion repository might exist.
- **Agroforestry high-priority records:** Brandt, Castle, Mendonça 2022/2023, Palma, Mucida and Sperandio have canonical evidence. Use existing agroforestry audits and limits; no fresh search.

## Tools and code: actual coverage

| Resource/group | What is already accounted for | Remaining disposition |
|---|---|---|
| Castle/saraheb3 GEE agroforestry | Commit-pinned source and EV; practice settings and geometry documented in the June tools log | Existing review/transfer limits; not a new acquisition |
| World Bank ProGreen | Classifier and all 30 notebook cells; weights, inputs, mapping and implementation conflicts | Selected-code coverage complete for bounded audit; admission and substantive holds, not validated global rules |
| Afforestation Tracker | Full selected classifier/configuration/data path and divergent point/raster rules | Same code-admission issue; low provisional credibility, no threshold transfer |
| Scotland reforestation | Selected preprocessing, four scenarios, predictor/model workflow | Same admission issue; woodland/species and national-policy context |
| Mini-Buoy | Eight indicators, complete warning set, instrument processing, literal screening band | High relevance to mangrove site assessment; code admission plus calibration/reference-site context remain |
| Mangrove Vulnerability Model | Selected recruitment, hydroperiod normalization and configuration | Species/process model; keep scenario semantics, not generic restoration cutoff |
| DFMFON | Selected species recruitment and implementation probes | Species/process context and code defects retained; no global rules |
| LEAF | 111 configuration entries, 12 code blocks and probes | Configuration-version and species/process holds; not a tested general suitability tool |
| GMW alerts and atlas code | Pinned selected notebooks and provenance checked | Extent monitoring/display referrals; original restoration-score derivation not established by display code |
| D4R / D4Ag / BiodiversityR | TOOL entries and explicit species-selection routing | Retain as species/implementation resources; not missing practice-level thresholds |
| ESI/IBSTI and African remote-sensing targeting | TOOL method entries with purpose and scope | Method referrals, not evidence that every implementation has been reviewed |
| RePlant Alfa / Regenmapper | Historical discovery leads, no verified canonical implementation review located | Secondary regional follow-ups; deferred from this closeout unless a specific unresolved priority criterion requires them |

The first three code audits are in `../forest_code_20261029/`; Mini-Buoy/Mangrove Vulnerability Model/DFMFON in `../mangrove_code_20261029/`; LEAF in `../leaf_atlas_review_20261029/`; GMW in `../mangrove_tool_followup_20261029/`. All seven selected codebases have documented findings. Their queue status `acquired` must not be interpreted as “never inspected.” Their absence from EV must not be interpreted as “nothing useful.” The shared repository-identity/file-line admission limitation is explicit; either resolve it once or preserve a bounded method-referral disposition. It must not generate seven serial PRs.

## Project-named tool check and identity corrections

- **D4R is Diversity for Restoration**, confirmed by its [primary Alliance page](https://alliancebioversityciat.org/tools-innovations/diversity-restoration-d4r). The TOOL registry has this identity; the methodology/agent-guide expansion “Data for Resilience” conflicts with it. D4R recommends species and seed sources for specified sites. Correct the naming in the eventual consolidated repair; do not silently change structural routing.
- **MapAWD is Mapping for Alternate Wetting and Drying**, confirmed by [IRRI](https://ghgmitigation.irri.org/resources/mrv-toolbox/mapawd). It is an Excel/VBA rice-practice suitability tool using water balance, rice extent, season, rainfall, PET and percolation. “Mapping Agriculture's Water Demand” is an incorrect expansion. No TOOL/SRC entry found in this audit. This is a project-wide rice/AWD method gap, not a forest/mangrove evidence gap. Native workbook intake remains paused under the project's format rule; documentation can be assessed through an approved format without executing VBA.
- **Africa Agriculture Adaptation Atlas:** primary [Alliance catalogue record](https://alliancebioversityciat.org/publications-data/africa-agricultultural-adaptation-atlas) describes spatial adaptation notebooks; [Atlas](https://adaptationatlas.cgiar.org/) is the named platform. No dedicated TOOL/SRC identity found. This is a cross-cutting M2/M3/M4 architecture/method referral, not automatically T4 establishment evidence. No notebooks/code were reviewed during this check. Coordinate with the relevant track before claiming project-wide resource coverage.

Only named-resource identity checks were made online. No broad literature/code search, new discovery count, SRCH/ledger completion, acquisition or extraction is claimed. Primary links checked 2 November 2026. The original TOR artifact itself was not located/re-read; “project-named” refers to the repository methodology's list.

## Scope routing and stop rule

Ceccarelli, Sahana and Hu are separately flagged species/habitat-model resources; Schroth is a crop/context check; Wang 2017 is a conservation/ROI method check. These are retained, not discarded or promoted automatically into practice-level thresholds. Alevizos macroalgae is an obvious stocktake category mismatch and is outside this forest/mangrove batch.

Finish when the ten fixed priority sources above each have verified identity and a source-linked disposition: criteria captured, reviewed method referral, explicit scope exclusion, or unresolved access/identity hold. For included methods, preserve variables, directions and source values even when no calibrated function is available. An access hold does not count as completed coverage. Resolve the shared code-admission decision once. Keep MapAWD and AAAA visible as cross-track gaps rather than falsely marking project-wide completeness.

Publish one consolidated closeout/repair PR if registers or methodology need changes. No citation-chasing expansion, no per-source PR, no invented numeric calibration, no human approval, and no effect-lane edits. This report itself is saved for review; no new approval request is created.
