# Pete's T4 review — 19 October 2026

Imported `review_agroforestry-t4-compilation-oct19_Pete_Steward_2026-10-19.csv` through `apply-review-export.py` on isolated branch `codex/t4-review-oct19`. The branch preserves the earlier T4 trial and incorporates committed review-round work through `7b7667d`. Shared checkout was not switched.

## Decisions applied

- Six approvals, five holds, one rejection. All twelve original notes/verdicts are preserved in the export and review log.
- `ev_T4_slope_seja2022_1`: soft-deleted as off-scope site description; never physically removed.
- Held records remain in the draft lane but are excluded from approval-filtered output. Holds explicitly clear earlier approval.
- No numerical relationships, variable labels, or family definitions were rewritten from button presses or inferred from notes.

## Result

All-active draft now has six generic rows (previous trial: five). Approval-filtered draft has four generic rows (previous trial: five). Four crop-specific candidate rows remain separate from generic F5; none enter the approval-filtered crop output.

The important recovery is planted-silvoarable slope: rejecting the mapped-terrain envelope leaves the approved Wotlolan hard upper limit, **35% slope = approximately 19.3 degrees**. Output is a `threshold` with `above_is_suitable=false`, rather than an invented trapezoid or the former 8% minimum. This records that source's rule; it is not a claim of universal applicability.

The held ≥90 cm soil-depth example is absent from approval-filtered output. It stays visible in the all-active draft for context review.

## Follow-ups from Pete's notes

1. **FMNR definition:** consider a semi-arid/Sahelian FMNR applicability scope instead of averaging disparate agroforestry systems. This is a methodological proposal, not a ratified change. Keep the study-area record held; approved WOCAT rainfall remains source evidence, not proof of universal physiological limits.
2. **Cross-family rainfall:** Haile remains held. Do not combine its rainfall preferences with FMNR into one generic catch-all average. Review family applicability before inheritance.
3. **Soil-depth context:** provide the surrounding INAB land-capability class definitions and example explanation. The current highlighted single-site statement was insufficient for a decision.
4. **WOCAT slope question, clarified:** does the sheet merely report that this documented farm is flat (0–2%), or does it state that FMNR cannot work on steeper land? Only the latter could justify an upper suitability limit. Current record remains held pending adequate context.
5. **Canopy scale:** preserve the concern that a coarse pixel can contain separate forest and cropland patches without trees growing within cropland. Dataset fitness must establish within-cropland/rangeland tree cover at an appropriate spatial grain before a canopy eligibility threshold is used.
6. **Numerical class tables:** Haile and Nath approvals are retained. Their original class tables remain in the disposition report; no loss of payload, and no automatic conversion of “low suitability” into exclusion. Semantic class/dataset mapping still required.
7. **Approvals versus encoded corrections:** approval of the Castle frost-free-period concern and WRI rainfall record is logged. Their existing encodings are not silently relabelled or rewritten. Those adjustments need explicit source-grounded correction through the evidence workflow.

## Importer fixes

Two bugs discovered while applying this export were fixed with regression coverage:

- A new reviewer/note on an already-approved record must be logged. Only an identical latest decision by that reviewer, with matching current state, is a no-op replay.
- A hold must clear `reviewer_ok`; otherwise previously approved records leak into approval-filtered synthesis.

All twelve resulting states and exact notes were checked against the supplied CSV. Live T4 recipe is unchanged; `draft/` and `approved/` contain isolated post-review candidate tables and full reports.

## Validation

- Full test suite: **357 passed**; review/T4/T3/T6 focused suite: 131 passed.
- All twelve verdicts and exact notes match the export; each is logged once. Archived export hash matches the Downloads original.
- All five holds are excluded from approval-filtered output; rejected record remains retained with `review_state=dropped`.
- Ruff lint/format and changed-file type checks pass. Whole-repository type check retains existing diagnostics outside these edits.
- Schema generator check: zero stale files. Structure check: zero errors (existing warnings remain).
- No live T4 recipe replacement or publication to main.
