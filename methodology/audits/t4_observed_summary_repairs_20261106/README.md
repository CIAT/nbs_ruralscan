# Observed rainfall summary corrections — review drafts

6 November 2026. Follow-up to the bounded T4 source checks. **Thirteen correction drafts are prepared; none is applied.** Existing dashboard cards retain high-priority Hold status and now state the exact proposed old/new summary maximum. Use Query to request correction; Keep by itself approves the stored record and does not apply a patch.

The source-selected rainfall classes are already preserved correctly. Four stored summary maxima are 1 mm; nine are 750 mm despite higher selected classes. Drafts change only `relationship.observed_max` to the outer endpoint of the existing selected classes. They preserve the source quote, class list, units, `observed_presence` meaning, gaps, practice/scope, approval state and all other relationship fields. A summary correction does not resolve any separate source contradiction or create a suitability threshold, support vote or mapping.

`correction_drafts.csv` gives the compact old/new table. `correction_drafts.json` retains full proposed relationships, current evidence fingerprints, artifact hashes and caveats. The 13 source quotes/hashes were rechecked against cached pages. Any future application must first confirm the evidence fingerprint and explicit approval scope; this file is not an automatically applicable approval.

## Guard against recurrence

`check_numbers.observed_range_mismatches` checks summary bounds only when every selected class is an explicit closed numeric interval in the same literal unit. Measured extrema may fall within the outer selected bins; the guard checks compatibility, not forced equality with bin endpoints. It handles ordinary, nonbreaking, thin and narrow nonbreaking thousands spaces. Present summary fields must be finite numbers; strings, booleans, containers and null are rejected at intake, while absent summaries remain optional. It does not infer missing bounds, choose locale-dependent punctuation, convert units, parse prose classes, fill disjoint gaps or infer ecological response. Unsupported forms remain for source review; a clean result is not proof of scientific plausibility.

The ordinary number-provenance checker intentionally permits alternative numeric readings, so a token `1` inside `1 000` can pass containment. The new independent consistency check catches that semantic summary failure while preserving existing quote-token behavior. Historical register findings are advisory; new staged intake rejects inconsistent summaries before publication. No existing evidence is altered or automatically quarantined.

The register scan finds **14** such records: the 13 reviewed active-batch cases and one rooftop-water-harvesting record already in the held/parked batch (`ev_wh_precip_wocat1497_1`). The rooftop record remains parked and receives no correction draft or reopened review request. `guard_findings.json` records this distinction's input findings; it is not a new source-check completion claim.

## Bounded retrospective and validation

This implements existing numeric fidelity and observed-context safeguards under v1.9.8, not a new scientific eligibility rule. Historical ruleset stamps and archived instructions remain unchanged. No source/register, recipe, approval, review log, family definition, learning cursor or progress-ledger stage changes.

Regression cases cover split thousands, disjoint classes, decimal bounds, open-ended/mixed-unit/ambiguous classes, missing summaries and quote containment that would otherwise hide the error. A real cached-PDF intake test rejects a 1 mm summary, accepts the faithful 1,500 mm summary, and proves neither the input claim nor register is rewritten by validation. Existing observed-presence exclusion from T4 votes/thresholds remains tested.

Validation: 124 focused number-provenance, intake, observed-presence and dashboard-priority tests pass; Ruff lint/format pass. Independent review verified closure of the malformed-summary type bypass and compatibility with measured extrema inside overlapping or disjoint classes. Generated-data validation reports zero stale files. Evidence records and prior review decisions remain unchanged.
