# Brittany topographic-index paper — bounded T4/operational review

Reviewed 2026-11-05 under extraction v1.9.4 and T4 review contract. Source: `wet_potential_topographic_index_brittany_2014`, Ariesty et al. (2014), *Modelling of Potential Wetlands based on a Topographic Index in Brittany, France*. DOI `10.19028/jtep.02.1.73-80` already verified in acquisition queue; no new DOI assertion or metadata rewrite.

## Outcome

**Zero eligible T4 or operational EV units.** This paper models potential wetland **occurrence** from hydromorphic-soil maps and topographic index. It does not test restoration/rewetting establishment, new-wetland creation feasibility, a degraded-wetland gate, or implementation barriers. Its directional and numerical findings are real, retained below and in the source inventory; absence of numeric calibration is NOT the exclusion reason. Scope is the reason. Do not turn its regional occurrence classifier into a global restoration curve.

All 8 PDF pages (printed73–80), 15 figures and all 10 Table1 rows reviewed. Four soil-coding criteria individually inventoried. `dispositions.json`/CSV contain46 anchored dispositions, including29 contiguous native text excerpts, the complete table values, graphical content, source conflicts, and lineage. `native_pages.txt` retains the full text layer. PNGs for PDF2–7 were visually inspected. No supplementary file identified in paper; external source soil maps are not a new acquired dataset or an approved intake adapter.

## Relationships retained outside EV

- Topographic index is used, with explicitly increasing probability of predicted wetland occurrence as index increases (PDF4, printed76). Source formula: TI=ln(alpha/tan beta), with drainage area alpha and slope beta (PDF3 image). This is one composite variable; no independent slope weight or response inferred.
- Regional threshold4.7 applies to Brittany occurrence map (PDF6); site-specific Table1 thresholds3.8–5.9 and hydromorphic soil shares9.8–54.6% retained individually. No suitability scores/endpoints/exclusion interpretation.
- Four source soil criteria: substrate, hydromorphy, solum type, depth. French legal soil-profile criteria classify wetlands; they are not restoration soil-depth envelopes. Original image provenance retained for the profile classes (Fig4) and coded example (Fig5).
- Main-paper calibration explicitly depends on chosen catchment maps. Ten maps cover1%of Brittany; seven calibrate/three validate, across120combinations. Gross agreement mean73%/median72%; predicted/observed area ratio mean1.4/median1.3;75%of runs overestimate and14%predict at least twice mapped wetlands. These measure classification performance, not NbS efficacy.

## Unresolved native-source conflicts

1. Watershed2: prose PDF5 reports threshold5.2 with9.8%hydromorphic soil; Table1 reports5.9. Both retained; no silent correction.
2. Hydromorph classes: prose PDF3 gives0–2dry,3–4moderate,6–9very hydromorphic; Fig7 brace appears to include5–9 as very hydromorphic. Class5 stays ambiguous.
3. Methods call50m DTM `ketinggian` (height), while Fig9 labels `DTM50m`; no invented conversion or terrain resolution rule.
4. Conclusion PDF8 calls1/250000 more precise than method maps1/25000–1/50000. Preserve inconsistency; no dataset recommendation inferred.
5. Queue family says restoration/rewetting but discovery note says creation. Neither practice is empirically validated by this source. Do not silently change source scope.

## Identity and checks

Opening English title matches queue title. Team SharePoint-library mirror and corpus PDF are byte-identical, SHA256 recorded in `validation.json`. Canonical SRC/EV search by source ID, title, author and DOI found no existing source/evidence duplicate. Deterministic PDF index built with table extraction enabled; it detected zero table objects despite visible Table1. Therefore full native Table1 text and visual inspection supplied row coverage; zero detected tables is not zero actual tables. No OCR pages flagged.

`package_for_extraction_multi` produced page-stamped retrieval bundle; full-paper inspection covered more than retrieval hits. Empty EV batch `validate_units([])` returns no errors. Central `ingest-effects-staging.py --dry-run --allow-structural --allow-operational` reports0staged, gates clean, no writes. This validates the empty admission, not scientific validation of classifier. Native anchor substring checks pass for29excerpts. All figures have source PDF/page provenance plus staged rendered images.

Queue/SRC/EV/ledger/review/git untouched. Suggested queue note in `metadata_suggestion.json`; retain acquired identity and record this as audited zero-T4 closure, not `extracted=done` or blanket `swept`. No human approvals assigned. Tidal/salt-marsh family stays parked; this paper creates no reason to reopen it.

## Retrospective

Existing defects #8/#16/#34 prevented occurrence/site descriptors from becoming practice suitability. Full-table sweep caught discrepancy missed by abstract's4.7summary. No new defect category established; no learning cursor or ledger advanced. Parent owns central retrospective and independent review.
