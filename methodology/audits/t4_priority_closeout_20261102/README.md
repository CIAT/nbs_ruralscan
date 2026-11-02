# Priority spatial-resource coverage closeout

2 November 2026. Scope: the current agroforestry, forest-restoration and mangrove T4 recovery work, with a separate check of project-named tools. This is an inventory/reconciliation audit, not a new discovery sweep, extraction, human review or assertion of coverage across every NbS. Baseline and reproducible stocktake counts are in `inventory_summary.json`.

## Decision

**The fixed ten-source reconciliation is closed at the targeted-method level.** See [source review](fixed_source_review.md), [70 criterion/group records](criteria_inventory.csv), and [verified identities and file hashes](source_manifest.json). This is not a claim of complete T4 extraction, supplement/code validation, human approval or project-wide coverage. Secondary references do not open another discovery chain.

The frozen peer-reviewed stocktake has **22 High-labelled rows in the focal categories; all 22 PDFs were located by normalized filename in the team-library mirror.** This establishes file availability, not bibliographic identity or full-text review. Eight have identified canonical SRC records, of which four have active evidence; eight were priority method/identity gaps resolved by the fixed review below; six require separate species/crop/conservation scope treatment or are misclassified. The original stocktake's labels and DOI strings are not authoritative metadata. Nine source DOIs in the fixed ten-source review were round-trip checked; none was promoted into SRC or inferred from a title search.

`priority_stocktake.csv` lists every row, file location, known canonical identity, current EV counts and disposition. “Evidence present” does not mean all criteria are captured, calibrated or approved. No overall completion percentage is claimed.

## Fixed priority closeout list

These eight studies already exist in the team stocktake. Opening-page identities and Crossref metadata were checked, followed by a targeted spatial-method review. Source-linked dispositions follow; details and limits are in `fixed_source_review.md`. Registration was not automatic.

| Resource | Why it belongs in this fixed batch | Current disposition |
|---|---|---|
| Crouzeilles 2020, targeted natural regeneration | Direct practice-targeting method | Identity verified; observed-regrowth method reviewed; no generic ecological calibration |
| Molin 2018, landscape-scale cost-effective restoration | Compares restoration approaches spatially | Identity verified; observed-regrowth method reviewed; no generic ecological calibration |
| Rajaonarivelo & Williams 2022, Madagascar suitability | Explicit LMIC forest-restoration suitability | Identity verified; five priority criteria retained with scope limits |
| Orsi & Geneletti 2010 (online 2009), Chiapas restoration priorities | Explicit LMIC landscape-restoration method | Identity verified; need, feasibility and option-ranking stages retained |
| Morán-Ordóñez 2022, Costa Rica multi-objective planning | Spatial trade-offs and restoration pathways | Identity verified; Marxan benefit/cost method reviewed; distinct from Langhans |
| Valente 2021, forest-restoration water-service priorities | Explicit spatial criteria and service-priority method | Identity verified; five water-service criteria retained; formula inconsistency flagged |
| Blanco-Sacristán 2022, Red Sea mangrove potential | Direct mangrove spatial-potential method | Identity verified; assemblage-model referral with habitat-history/scale limits |
| Strassburg 2020, global ecosystem-restoration priorities | Major spatial optimization method already selected as High | Identity verified; multi-biome optimization referral; code available upon request per paper |

Two High-labelled grey entries were also resolved:

1. **Chazdon & Guariguata (2018), Decision support tools for forest landscape restoration.** CIFOR Occasional Paper 183, distinct from IUFRO WS34. Institutional full text recovered; spatial-planning chapter and tool tables reviewed. Qualitative seed-source warning retained; citations remain referrals rather than new acquisition tasks.
2. **Critchley, Sassen & Umunay (2021), Mapping opportunities for cocoa agroforestry in Côte d’Ivoire.** Correct UN-REDD publisher PDF recovered; historical SARE link is wrong. Host-system, canopy/history, climate-model and legal-context rules retained with limitations.

Both grey PDFs are copied to the OneDrive team-library mirror and local cache. Remote synchronization is not independently verified. Exact paths and hashes are in `source_manifest.json`.

These are ten resolved resource dispositions, not ten new EV sources. The shared decision for seven previously inspected codebases is **retain bounded method referrals with admission/substantive holds**; do not reopen them as seven extraction tasks.

## Already covered: reuse rather than repeat

- **ROAM:** 64 native spreads, 28 numbered tables plus Appendix A1, 22 figures and 133 criterion/candidate rows accounted for in `../roam_wocat_t4_20261102/`. No EV is a valid result where claims are priorities, unresolved mappings or examples.
- **WRI global forest-restoration atlas:** two companion publications, seven pages, original canopy/population/method values and limitations preserved in `../t4_primary_methods_20261102/atlas_review.md`. Same lineage; not two independent validations.
- **IUFRO WS34:** 75 pages and complete table accounting in `../t4_iufro_review_20261102/`. This does not cover the distinct CIFOR tools synthesis above.
- **Mangrove restoration-potential report:** `worthington_spalding_2018_restoration_potential` has three active T4 and two operational units; full guidance inventory and transfer holds remain in `../mangrove_guidance_20261029/`. GMW display code was inspected separately; displaying a score is not reconstructing its method.
- **Lewis 2005:** already read and inventoried in `../restoration_source_review_20261028/`, including its table and tidal figures. The previous suggestion to reacquire it was duplicate work and is cancelled. Reuse the existing hydroperiod holds if relevant; no new primary-reference chase.
- **Williams 2024 and Cook-Patton 2020:** registered evidence exists. Their paper-level representation does not establish complete code or supplement coverage; do not reopen them solely because a companion repository might exist.
- **Agroforestry high-priority records:** Brandt, Castle, Mendonça 2022/2023, Palma, Mucida and Sperandio have canonical source records; registration alone does not prove active evidence. Use existing agroforestry audits and limits; no fresh search.

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

- **D4R is Diversity for Restoration**, confirmed by its [primary Alliance page](https://alliancebioversityciat.org/tools-innovations/diversity-restoration-d4r). The TOOL registry has this identity; the methodology expansion “Data for Resilience” was corrected in this batch. D4R recommends species and seed sources for specified sites. Structural routing is unchanged.
- **MapAWD is Mapping for Alternate Wetting and Drying**, confirmed by [IRRI](https://ghgmitigation.irri.org/resources/mrv-toolbox/mapawd). It is an Excel/VBA rice-practice suitability tool using water balance, rice extent, season, rainfall, PET and percolation. The incorrect methodology expansion “Mapping Agriculture's Water Demand” was corrected in this batch. No TOOL/SRC entry found in this audit. This is a project-wide rice/AWD method gap, not a forest/mangrove evidence gap. Native workbook intake remains paused under the project's format rule; documentation can be assessed through an approved format without executing VBA.
- **Africa Agriculture Adaptation Atlas:** primary [Alliance catalogue record](https://alliancebioversityciat.org/publications-data/africa-agricultultural-adaptation-atlas) describes spatial adaptation notebooks; [Atlas](https://adaptationatlas.cgiar.org/) is the named platform. No dedicated TOOL/SRC identity found. This is a cross-cutting M2/M3/M4 architecture/method referral, not automatically T4 establishment evidence. No notebooks/code were reviewed during this check. Coordinate with the relevant track before claiming project-wide resource coverage.

Only named-resource identity checks were made online. No broad literature/code search, new discovery count, SRCH/ledger completion or EV extraction is claimed. Two grey full texts were recovered for this fixed review. Primary links checked 2 November 2026. The original TOR artifact itself was not located/re-read; “project-named” refers to the repository methodology's list.

## Scope routing and stop rule

Ceccarelli, Sahana and Hu are separately flagged species/habitat-model resources; Schroth is a crop/context check; Wang 2017 is a conservation/ROI method check. These are retained, not discarded or promoted automatically into practice-level thresholds. Alevizos macroalgae is an obvious stocktake category mismatch and is outside this forest/mangrove batch.

The ten fixed resources now each have verified identity and a source-linked targeted-method disposition. Criteria, directions and reported values are retained even without calibrated functions. Supplement, calibration, mapping, policy and code limits remain explicit; this does not stamp any extraction or human-review stage complete. MapAWD and AAAA remain cross-track gaps rather than false project-wide completeness.

One consolidated documentation/identity-repair PR closes this batch. No citation-chasing expansion, per-source PR, invented calibration, human approval or effect-lane edits.
