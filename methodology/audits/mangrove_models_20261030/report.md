# Bounded mangrove model-source extraction — 2026-10-30

## Result

Current extraction skill v1.9.2; authorised mangrove_restoration /
mangrove_restoration__tidal_coastal / T4 plus separate operational-risk claims.
Five unapproved Worthington & Spalding (2018) units: three structural (two categorical
exclusions and one direction/proximity claim) and two operational (tenure and community
support). Zero calibrated functions, zero runtime weights, no analytical-table synthesis.
Source remains **in_progress** because model mapping/calibration and other lanes remain.
Rodríguez-Rodríguez et al. (2016) remains acquired in the queue, with no SRC/EV promotion:
its species/model claims are preserved in the inventory, not silently discarded.

## Source identity and credibility

Both source opening titles and cache/library hashes were verified in the preceding
acquisition audit. Both deterministic indexes now include table extraction (15 pages/1
machine-detected table for Rodríguez; 36 pages/16 for Worthington). Machine table counts
are not completeness verdicts: Rodríguez Table1 and Table2 were inspected explicitly;
Table2 was also rendered and visually checked. Page-stamped passage packages were built
with package_for_extraction_multi, force=True, full_tables=True (gitignored staging).

Worthington: medium tier. Strength: expert-derived model and review, no independent
predictive validation established. Transparency: seven model inputs and exclusion logic
named, but weights/functions absent. Authority/venue: TNC/IUCN/Cambridge institutional
report. Transfer: worldwide scope, including tropical developing-country contexts, but
historical-loss extent and local feasibility caveats bind use. Recency: 2018 historical
baseline, not a current legal/dataset endorsement. Seminality: relevant original MRP
method report; no is_seminal flag asserted. Independence: authors advocate restoration
and developed the tool; their model and review are not extra independent votes.

Rodríguez: provisional medium candidate, not promoted. Measured monitoring used to
calibrate a species growth model; fit differs by station and independent validation is
not established. Transparent parameter changes and limitations, peer-reviewed Caldasia
article, Colombian case-specific transfer, 2016 model version, no seminality claim.
Original code supplied by Twilley is acknowledged; public code release is unverified.
A numeric salinity-growth model is not a ready-made generic suitability function.

## Coverage and preserved holds

claim_inventory.json contains 45 explicit items, including every member of the seven-input
MRP model list, both exclusion classes, Tables2.1/2.2/3.1/3.2/8.1 output-versus-input
classification, both Rodríguez tables (five sites each; all 15 recruitment constants),
four growth modifiers, three species-specific salinity limits, and source conflicts.

Inspected substantive locations: Worthington PDF7–12 and28–34; Rodríguez PDF3–13
(methods, results, limitations, acknowledgements). Front/title pages checked for identity.
This is not a claim of complete extraction of all51 pages. Worthington PDF14–27 carbon,
coastal protection, fisheries and conservation chapters remain separate effect/referral
work; figures/maps outside the named locations are not digitised here. Bibliography and
introductory material are not independent primary evidence.

Key holds:

- Tidal range is not tidal inundation duration; sediment change is not sediment retention.
  Historical loss-patch mean area is not minimum restorable area or standing forest size.
  Six MRP inputs therefore stay visible as ontology/calibration holds. Proximity has a
  compatible distance-to-forest mapping restricted to mangrove propagule sources.
- MRP historical-loss focus omits pre-1996 opportunities. No universal opportunity mask
  derived from the report footprint. Prose score1–100, >=60 high-restorability caption,
  and fractional table averages are retained without silently normalising them.
- Rodríguez's70/85/100 salinity-unit limits retain species and cited-primary attribution.
  No canonical salinity variable; units are not soil EC. Avicennia occurrence above120
  on PDF12–13 conflicts with interpreting100 as a universal maximum. No resolved envelope.
- Model calibration/recruitment constants, mortality assumptions, available-light equation
  and forecast basal areas stay source/model context. They do not become T4 breakpoints.
- Operational tenure and community support go to M2b Stream B/M6, not suitability scores.
  Speculative finance proposals and historic international commitments remain M6 pointers.

## Adversarial check

Performed by coordinating agent; no independent second reviewer claimed.
Variable use: seven MRP factors accounted for; original weights absent. Direction: one
qualified inverse-distance direction, not three scalar curves. Calibration: none.
Scope: masks refer to historical mangrove losses; permanently subtidal water differs
from normal tidal inundation. Urban rationale continues on PDF11; no new legal claim.
Community support maps to the governance component of extension_governance, not measured
extension-service access. Table coverage: regional outcome aggregates and site parameters
kept separate from input responses; all species columns preserved in inventory.
No existing reviewer approvals or source/evidence rows were replaced.

## Retrospective

Initial new-batch checks found two short quotes (urban and community). Existing catalogue
rules9/18 and T4 context requirements applied more strictly: widened native context,
recorded within-run before/after anchors, revalidated. No new defect class or ruleset
change invented. This is the concrete correction for the dominant insufficient_context
feedback; final new-batch number/context/scope/species/quote/direction checks are clean.

sweep_metrics.py logged mangrove_models_20261030. Global number-provenance5.2% and verify0.1%
are unchanged rounded rates against a different corpus/review snapshot; these are not
proof of improvement from five qualitative records. New-batch rates/flags assessed
separately. Global learning cursor unchanged because the complete feedback set was not
processed. Source completeness kept in_progress. Current ledger API stores authored
searched/screened/verified stages; verified marked in_progress. Extraction/review facts
remain register-derived; no new search completion claimed.

Validation: 48 focused tests pass; full generation/provenance passes; structure0 errors
(with existing warnings). Repeat dry-run adds0 duplicates. Final quote strings trim only
trailing line whitespace, preserve native text, and pass the central quote gate again;
generated review artifacts refreshed through schema_tools.generate.refresh_review_state.
All5741 previous evidence rows and628 previous source rows are field-for-field preserved.
