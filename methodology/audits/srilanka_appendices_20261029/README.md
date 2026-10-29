# Sri Lanka mangrove guidelines: appendices, 29 October 2026

Screened PDF150–194 of the existing, verified publisher artifact under the bounded T4/operational review scope and extraction ruleset v1.8.0. This adds **45 pages**, bringing explicit coverage to **118 of 194 pages**. The remaining 76 pages are individually identified in `validation.json` and `page_coverage.json`. This is not whole-source completion.

The appendices supply germination diagrams, field survey and nursery forms, an identification key, acknowledgements and blank field-note pages. **No new EV units were emitted.** Sampling prescriptions, blank data fields and worked examples do not establish suitability thresholds or measured effects. Existing ownership, community and funding evidence remains unchanged; repeated advice is not another independent study.

## Retained implementation tools and source issues

- Forms 1A/1B record vegetation and fauna across the proposed restoration area, its periphery and the nearest natural mangrove patch. Preserve the distinction between field checklist, sampled observation and suitability rule. Survey coverage, transect dimensions and density calculations are sampling instructions.
- Form 2 records past degradation, ongoing threats, mitigation, settlements and ownership. Forms 4/6 support nursery accounting and seedling baselines. Form 4's numerical row is explicitly an example, not observed performance.
- Form 5 is a useful Module 6 hand-off checklist: baseline surveys, mapped plots, ownership, budget availability, hydrological works, species/planting plans, protection and dated activities. These are **paper implementation tools**, not codebases. No software repository is identified in this appendix pass. Its historical approval fields are not promoted as current legal requirements.
- Form 3 (PDF171) labels pH under **water**, whereas Form 5 (PDF174) refers to **soil pH (Form 3)**. Preserve this measurement-compartment mismatch; do not map the field to soil pH silently. Form 3's PDF172 prompt for an approved analysis method is followed by blank space, confirmed visually. No missing method is invented.
- The identification key (PDF180–181) contains disconnected routes: 8B leads to 10, leaving step 11 unreachable from the start; 13B leads to 17, leaving step 16 unreachable. The printed routes are visually confirmed. Retain as a source-quality hold before digitisation, not an invitation to repair the taxonomy or infer species tolerances.
- Image-only anatomy diagrams were visually reviewed as nursery morphology. Blank/field-note pages PDF188–193 were visually checked, so sparse text is not misreported as unread substantive material.

## Audit and limits

`source_inventory.json` preserves all 45 native page anchors and page-specific dispositions, including every form continuation and the species-key text. `validation.json` records artifact identity and 16 visual checks; all 45 anchors exactly match the cached PDF. Historical name/contact lists are not used as present-day contacts or additional evidence sources.

No SRC, EV, SRCH, progress-ledger, review or metric row changed. This was a source-coverage review with zero extraction, not a new discovery search or extraction sweep. No quality-rate improvement or human approval is claimed. No Python/runtime/schema change was made; validation is limited to audit consistency, source containment, coverage arithmetic and diff scope. Earlier mudflat, species-chart and mapping holds remain in the preceding audits.
