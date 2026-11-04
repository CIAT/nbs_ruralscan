# Agroforestry: 184 claims versus 26 mappings

4 November 2026. Bounded register/compiler audit and developer presentation repair.
No new paper extraction, source verification sweep, human decision or analytical calibration.

## Result

The v0.1.6 developer package adds a searchable **source relationship catalogue** alongside
the existing numeric table and plots. All 184 non-dropped structural claims are present,
with source wording/classes, family/scope, human approval flag, compiler disposition,
explicit mapping links, context, quotes, page/locator and lineage. Users can filter to the
83 unlinked selection/qualitative/categorical records under review. Species/crop records
remain labelled; no practice-level applicability is inherited from them.

The original 26 mappings comprise ten numeric responses, seven host gates, one hard legal
exclusion and eight operational scenarios. Only 21 of the 184 claims are explicit mapping
references. This is a traceability count, not the total number of claims useful for variable
selection or source importance. The three shaded-crop gates also cite an effect claim
outside the structural denominator. The new catalogue does not conceal that mismatch by
counting the effect claim as an additional structural claim.

## Root cause and learning

In `synthesis.synthesise`, evidence types other than `literature_relationship` and `expert`
are assigned `selection_only` before relationship decoding. All 56 unlinked selection-only
records in this batch are `scoping_candidate`. That gate can correctly prevent unapproved
numeric compilation while incorrectly suggesting that a claim has no usable relationship.

**36 of those 56 records contain stored direction wording, shapes or class information.**
This is a mechanical visibility flag, not 36 validated suitability relationships: source
land-capability context and `class_scores=not_extracted` also require inspection. The raw
field is always shown, so the detector never fabricates a missing class or direction.
The other 20 have no matching structured signal; this does not prove the paper lacks one.

The 16 qualitative and 11 categorical records are also shown independently of the numeric
compiler. Source-response curves are not drawn where calibration is missing. No automatic
evidence-type promotion, class-to-score conversion or threshold correction occurs.

## What the 83-record audit preserves

[83_claim_inventory.csv](83_claim_inventory.csv) accounts for 56 selection-only, 16
qualitative and 11 categorical claims. Each row has the original relationship, source
page, approval flag, compiler status, next review caution and same-source-variable peers.
Peers are comparison candidates, not declared duplicates or extra independent votes.
`build_audit.py` reproduces the inventory from the versioned package. Quotes and full
context are in the relationship catalogue rather than duplicated in this CSV.

Concrete issues found in stored quotes/context:

- Ahmad 2020 directions, Nath ranked soil/terrain classes, and Singh response shapes
  remain readable despite selection-only status. Shapes without endpoints stay uncalibrated.
- Nath CEC ranges overlap; available-water-capacity/texture codes need a codebook; subsoil
  depth/measurement semantics remain distinct. Do not fix source classes by interpolation.
- Haile/Chuma/Nath elevation/aspect and Ahmad NDVI records have same-source comparison
  candidates; preserve lineage and compare to existing compiled claims before adding votes.
- Yadav temperature discussion concerns species-distribution model importance, not a
  practice-level temperature response. Scope/attribution needs review.
- The Mali fertilizer-use record describes adoption, not soil-fertility suitability.
- Weston rainfall is study-site context; Sprenkle's canopy cutoff is an accounting
  convention; neither is a biological eligibility threshold.
- FAO fertilizer response is recorded in forest-restoration context. Check practice and role.
- Mucida protected areas and Baldwin buffers/parcel exclusions are local/project rules,
  not globally transferable legal masks.
- Rootstock prerequisites remain informative but the project's locked routing keeps this
  enabling evidence outside core T4. Flag for human role review; no silent reassignment.
- Castle's temperature-tagged definition uses days: verify the measured variable before mapping.

These are review cautions from existing records, not completed re-extractions from primary
sources. The catalogue makes this evidence accessible now. Correcting the flagged register
rows or choosing new numeric functions remains a separate audited review action.

## Rules and validation

Ruleset **v1.9.4**, defect **#54**, and the T4 developer contract now require separate
relationship visibility and compilation checks. The versioned skill/contract/command
snapshot is retained. Future package builds automatically emit the catalogue; package
verification requires both catalogue outputs from v0.1.6 onward.

75 targeted tests passed, covering developer packages/views, corpus reconciliation,
numeric bands, T4 compilation and the new catalogue. Regression tests cover scoping
candidate directions/classes, scope and dropped-record separation, explicit mapping
links, unknown direction, contextual numbers and HTML escaping. Package hashes and all
relative links pass; the Pages copy matches the versioned handoff byte-for-byte.

The 26 mapping CSV rows, function options/intervals and both conformance files are
byte-identical to v0.1.5. The rebuilt run contract picks up existing main's stricter host
combination wording; approved policies are unchanged. No schema/register, ledger, review
decision or historical evidence ruleset stamp changed. No visual browser check is claimed.

This is a presentation/compiler retrospective, not an extraction sweep: no new sweep
completion, review approval, declining source-error rate or review-feedback cursor advance
is claimed. Learning is embodied in the generator, tests and versioned instructions.
