# Bounded mangrove coastal-guide effects — 2026-10-30

## Result

Four active, unapproved narrative effect units from Spalding et al. (2014): coastal
erosion reduction, atmospheric carbon removal/retention, nutrient removal and
sediment trapping. All describe mechanisms of existing mangroves in conservation/
restoration guidance; `comparator=existing_forest` and context notes explicitly
prevent interpreting them as measured restoration-versus-baseline responses.
No effect magnitude, strength rating, threshold or runtime rule was inferred.

Two other new wind/surge summaries were ingested, then **soft-quarantined during
self-review** after canonical-source reconciliation found McIvor2012b already cached
and represented. They remain as dropped audit records, not independent support.
This was an AI intake correction, not a human review decision; no existing records
or approvals were changed. Their exact existing-source/EV links are retained in
self_review_quarantine.json. Active staging now contains only the four active units;
its repeat dry-run adds zero. Initial six-record intake and final dispositions remain
visible in staged_units.json.

## Scope, provenance and credibility

Applied extraction skill v1.9.2, effect contract and direction addendum. Read the
coastal guide's substantive body text and references; deterministic42-page index
built with table extraction, then page-stamped multi-variable packages generated.
Source identity, publisher download and team-library path were verified in the
preceding acquisition audit. One SRC row promoted, retained **in_progress**, not swept.
Queue status extracted means records were produced; it does not imply full coverage.

Tier medium: institutional expert guidance synthesises evidence rather than measuring
new interventions. Methods are explicit enough to follow mechanisms and review
references; underlying experiments/validation need separate inspection. Authors and
TNC/Wetlands International provide relevant expertise. Global coastal scope includes
LMICs but every coastline has context limits.2014 publication is historical; no
seminality override asserted. Shared authorship and conservation advocacy limit its
independence from parent reviews and other TNC reports.

Erosion retains `cited_secondary` with McIvor2013 elevation-review lineage; that review
is an intermediate source, not the original experiment. Carbon, nutrient and sediment
paragraphs are labelled `expert_assertion`, not primary measurements. Water purification
includes its capacity caveat; source wording about inert nitrogen is preserved rather
than silently corrected into a new mechanistic claim. Carbon is narrative removal,
not an annual rate, net GHG budget or mature-stock conversion.

## Coverage and remaining work

claim_inventory.json accounts for42 items, including the five-hazard property matrix,
wave13–66%/100m, surge5–50cm/km, tsunami5–30%, elevation up to10mm/yr, severe-event
limitations, ordinary-versus-storm wave distinctions, green-grey bundles, restoration
constraints, operational guidance, economics and tools. Numeric values stay in the
inventory with exact pages and explicit holds; no mapping of waves to flood depth,
soil elevation to sediment-removal percentage, or recruitment to income.

Image-only/low-text pages and table geometry remain unverified. Figure/code methods
were not digitised or inspected. Protected-area, species-site, mid-tide and restoration
feasibility passages remain deferred T4/M6 pointers under the effect-lane pause.
No opportunistic suitability extraction.

Other acquired sources (Hutchison biomass, Sanderman carbon and Hutchison fisheries)
remain acquired, unpromoted and unextracted in this batch. Their opening/source-type
triage and stock-rate/fisheries mapping holds carry forward; full-paper accounting is
still owed. Losada remains on its DataCite/Crossref metadata-provider hold. This batch
does not complete the five-source backlog.

## Retrospective and adversarial check

Self-review found the two secondary duplicates after intake. Corrected with reversible
quarantine and preserved canonical links. Apply existing catalogue#25/#32/#48 earlier:
check named upstream reviews against SRC/EV **before** admitting summaries. No new
ontology, ruleset or defect category introduced. Also checked direction on named
outcomes, existing-forest comparator, mechanisms, missing magnitudes, atomic claims,
quote context and attribution. No independent reviewer claimed.

Global metrics logged: number-provenance5.1%, verify0.1%, both unchanged rounded rates.
Different cumulative denominators and four qualitative active units cannot establish
pipeline improvement. New-batch checks are separately clean. Global learning cursor
unchanged because the full human-feedback set was not processed. T3/T6 grey verification
marked in_progress via ledger API; no search completion, human review or synthesis.

Validation:48 focused tests pass; seven new-batch checks clear (number, context, scope,
species, quote, direction, bands); full provenance verifies4306 quotes against626
cached sources, with1478 exemptions including dropped records. Structure0 errors,
3806 existing/content warnings. All5778 previous EV and633 previous SRC rows remain
field-for-field unchanged. Review log, SRCH history and learning cursor unchanged.

Final formatting pass removed only trailing PDF line whitespace from new quotes and
matching direction cues. Central active-unit gate and seven checks rerun clean;
review artifacts regenerated through `generate.refresh_review_state`. Existing records
still unchanged; `git diff --check` clean. No source words or numeric values altered.
