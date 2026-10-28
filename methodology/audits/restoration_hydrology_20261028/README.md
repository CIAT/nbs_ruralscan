# Restoration hydrology and forest-scope review — 28 October 2026

This bounded batch follows PR #470. It reads Van Loon et al. (2016), *Hydrological Classification, a Practical Tool for Mangrove Restoration* (26 pages), and Sargsyan et al. (2026), the Sisian afforestation/reforestation study (10 pages). It does not close the discovery corpus.

## Outcome

- Five unapproved **species-specific** mangrove class profiles retained in EV, with the original daily-duration and per-inundation values, species groups, header, page and cited-primary lineage.
- No new practice-level support vote, monotonic direction, numerical weight or executable suitability function. A class range is not automatically an optimum range; genera occurring in several classes are not separate independent studies.
- All **90 rows across seven Van Loon tables** accounted for: 5 historical classes, 6 adapted classes, 7 locations, 23 sites, 23 observed classifications, 3 hydrological comparisons and 23 elevation-only comparisons. Figures relevant to interpretation inspected visually.
- All **five Sisian criteria** retained in the source inventory, including model use, reported bands, raw map legends, supported qualitative comparisons and unresolved conflicts. Source remains acquired but is not admitted to SRC/EV.
- Van Loon remains `in_progress`; queue `extracted` indicates some retained EV, not completed scientific review. Other sources, human approvals, recipes and the learning cursor remain unchanged.

Four of the 29 discovery candidates now have main-paper reviews across this and the previous batch. **25 candidates still lack this review**, including three acquisition blockers, plus the separate ITTO reuse task. The four reviewed sources still carry explicit unresolved claims.

## Hydrology findings and limits

Table 2 uses **minutes per day** and **minutes per inundation** together. Only the first is dimensionally compatible with the ontology's share-of-time variable. Per-inundation duration has a different denominator and remains a distinct-metric ontology hold. No conversion or new variable was silently introduced.

The five species-group profiles retain raw values in `context.reported_values`, with no executable relationship. Header and row are separately anchored on PDF page 4, so review can distinguish elevation, daily duration and event duration. The source's conditional elevation proxy (cm above MSL) is not mapped to generic terrain elevation. The word “Acrosticum” is preserved as printed; taxonomic correction remains review work.

Class 1 (“none”) is retained in the inventory, not discarded. Its paired wetness criteria do not authorize a universal exclusion based on either individual column. Other classes overlap in their species membership. Table 5 also shows discrepancies between observed hydrological and vegetation classes. The authors explicitly caution against rigid use (p20), require local vegetation classes for other regions (pp20–21), and call for prospective restoration-project testing (p21).

The generic classification method's use of both metrics is recorded in the inventory as **species-selection method evidence**, separate from practice-level agreement. It is not smuggled into a structural unit or ingested through an unsupported dataset-role path. Instrument intervals, the 15-minute error filter, measurement-period sensitivity and local site values remain measurement/context information rather than biological thresholds.

The immediate source of Table 2 is Te Brake & Van Huijgevoort's 2008 thesis, with Watson (1928) and Van Loon et al. (2007) as antecedents. The five profiles share this lineage. `primary_followups.json` records title-based recovery tasks; no unverified DOI or acquired-primary claim was added. The DANS dataset is a pointer only under the paused dataset-intake rule.

## Sisian pre-registration hold

The paper mixes forest restoration, afforestation and new plantations without enough detail to establish native ecosystem history or separate the ecological active-planting scope. Its own criteria also conflict:

| Criterion | Retained finding | Unresolved issue |
|---|---|---|
| Elevation | 1,200–2,400 m in abstract/conclusion; 1,300–2,400 m in results/discussion | No lower endpoint chosen; occurrence-derived local selection is not global tolerance |
| Slope | Selected 10–30° band; map displays 0–10, 10–20, 20–30 and 30–50° | Green map colour at 0–10° is a raw-variable legend, not evidence that it is the preferred suitability class |
| Aspect | North, northwest and east selected; discussion distinguishes moisture-demanding from drought-tolerant vegetation | No named species or globally transferable orientation envelope inferred |
| NDVI | Used in overlay | Abstract targets sparse/degraded vegetation; results favour healthy vegetation; raw bins do not resolve selection logic |
| NDMI | Higher vegetation moisture favoured in results | No canonical NDMI mapping; not soil drainage or volumetric soil moisture; no numerical suitability rule recovered |

No model weight or missing cutoff was invented. All map bins and the apparent Figure 6 legend anomaly remain in `sargsyan_criteria_inventory.json`. The HAYANTAR forest-management plan is recorded as an unacquired primary follow-up.

**Review question before registration:** may the mixed-purpose Sisian source enter as a regional method-use profile for active planting, with conflicting calibration held, or should it remain outside that family until its restoration/plantation scope is resolved? This is a hold, not an exclusion or an approval request to accept its numbers. The repository's AGENTS.md requires: “Always validate borderline inclusions/exclusions with a human-in-the-loop review before registration.” Other acquired sources can be processed independently.

## Six-axis credibility assessment

| Axis | Van Loon | Sisian (provisional; not registered) |
|---|---|---|
| Strength | Multi-site observations and sensitivity analysis; no prospective restoration validation | GIS overlay based on occurrence/management criteria; no independent survival or suitability validation |
| Transparency | Field methods, all seven tables and data-archive pointer; inherited classification | Five inputs identified, but contradictory thresholds, unclear index selection and no reproducible overlay logic |
| Authority | Peer-reviewed PLOS ONE | Peer-reviewed Anuário do Instituto de Geociências |
| Context | Vietnam/Indonesia; relevance to tropical restoration, explicitly conditional transfer | Armenian mountain forestry; local occurrence and plantation/restoration mix |
| Recency | 2016; useful method evaluation, not current habitat data | 2026; recency does not repair scope/calibration defects |
| Seminality | No seminality or citation-count claim | None claimed |
| Independence/COI | Instrument-company employment disclosed; study largely predates employment; keep reported limits and do not infer independent intervention efficacy | No funding/conflict declared; management-plan criteria still require source review |
| Summary | **medium**, admitted for retained source profiles | **low provisional**, held before source admission |

## Verification and retrospective

Ruleset v1.8.0, defect catalogue and T4 review contract applied. Both opening-title/DOI identities pass. Deterministic indexes match PDF hashes; all-variable retrieval supports, but does not replace, the full-paper read. The machine detector returned 17 table fragments for Van Loon's seven actual tables, so coverage counts use the visually reconciled source tables, not detector counts.

Central ingestion gates pass on all five units, including separately anchored headers. The initial dry-run rejected the noncanonical context key `study_regions`; it was changed to `region` before ingestion. Source-value semantics were checked against the rendered table; automated numeric provenance checks do not validate every nested reported-value interpretation.

The batch retains short table-row anchors with separately verified caption/header quotations. Any narrow-quote advisory is visible in `batch_checks.json`; it does not justify stitching several rows together or self-granting approval. No new extraction defect class was found: existing table-context, proxy, species-selection and source-completeness rules cover this batch. Global metrics are an administrative snapshot, not evidence of improved error rates. No whole-feedback cursor advancement is claimed.

Validation results: full generation verified 3,877 quotes against 533 cached sources; metadata check passed. Structure and T4 coverage report zero errors (structure has 3,471 existing-framework/reference warnings, including standalone mangrove and unresolved lineage references). The five narrow-row advisories are individually triaged in `quote_flag_triage.json`; all have independently verified caption/header context. Scope, species and relationship-number checks add no flags. Global number-provenance rate remains 5.7%, verification rate 0.1%; no improvement claimed. Preservation checks confirm all 539 prior SRC rows and 5,206 prior EV rows unchanged, only the two intended queue rows changed, and no recipe changed. Idempotent ingestion dry-run adds zero units.
