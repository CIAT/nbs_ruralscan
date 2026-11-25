# v2.2 visual methodology review — 24 November 2026

Authorised by Pete for review. Previous v2.1 preserved under docs/redesign-v2-1; current review under docs/redesign.

- Climate hazards to rural livelihoods remain distinct from soil erosion, project asset hazards and project-caused environmental/social impacts.
- One TTL-facing soil erosion concern replaces the parallel degradation entry. This is a display decision, not a claim that soil organic carbon and erosion are equivalent. Scientific registers remain unchanged.
- Table 3.4 and its maps use C5 classes and direction. Country shares use the same cuts as the selected opportunity space. Worse means the worst class for 2/3 classes and worst two for five classes.
- Infrastructure screen overlays available hazard footprints with road/facility inventories or gridded population. Exposure units remain km, facilities and people; missing coverage and inventory incompleteness must be reported. Historical burns are not prospective wildfire probability.
- Fictional Haiti example allows one exposure indicator and weight, showing base and selected scores/ranks. No claim of avoided damage, service protection, catchment connection or engineering suitability. It does not alter the Sierra Leone walkthrough.
- Infrastructure priority is a proposed extension requiring T5/method ratification before analytical implementation. Population exposure must replace overlapping population/livelihood inputs where necessary to avoid double-counting. No schema changes in this review.
- Section 6 describes comparable exposure context only; no invented practice-specific totals or protective-effect scores.
- ESF prompts in 4.3 use existing desk evidence and open questions. Borrower/specialist assessment, engagement and local verification belong to feasibility, design and implementation. No formal Bank risk classification, compliance judgement or automatic consent determination.

Source: World Bank Environmental and Social Standards, https://www.worldbank.org/en/projects-operations/environmental-and-social-framework/brief/environmental-and-social-standards (reviewed 24 November 2026). Existing ESF review and local-check decisions remain applicable.

## 25 November — existing evidence companion

Pete authorised a 3.5 mechanism panel linked to Section 5, using existing T3/T6 evidence only. `scripts/build-infrastructure-evidence.py` exports selected global/all-farming-system synthesis rows, referenced evidence quotes and source metadata, with SHA-256 input hashes. No new literature review, synthesis or analytical ratings. Snapshot generated from the primary checkout using `python3 scripts/build-infrastructure-evidence.py --source-root /Users/pstewarda/Documents/rprojects/nbs_ruralscan`; that checkout contains newer evidence than this UI branch. Rebuild from the integrated CSV state after merge.

The UI prefers the selected family row and labels a wider NbS fallback explicitly. Assisted regeneration is not silently equated with passive regeneration. Only T3 livelihood-mitigation/both rows enter the mitigation view; pure asset-threat rows are excluded. Missing hazard rows mean no matching evidence in this snapshot, not proof of no effect. T6 soil-erosion evidence is related context for flood/landslide, not a surrogate hazard-mitigation rating. T3 and T6 confidence remain attached to their stated outcomes. Source review flags are displayed without claiming synthesis approval. Dropped/quarantined dependencies raise a review hold.

Section 5 retains exposure-only arithmetic. Evidence ratings are not multipliers and do not prove that the selected NbS would protect any exposed asset. Feasibility establishes spatial pathways, event severity, scale, design and damage/service outcomes. Both pages follow selected practices and persisted exposure hazard; archive v2.1 is unchanged.
