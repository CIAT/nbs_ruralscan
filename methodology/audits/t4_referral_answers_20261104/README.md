# T4 audit referral answers — 4 November 2026

This batch answers the 17 remaining source-investigation groups in the T4 clarification queue, across 11 sources. It adds source context to existing review cards; it does not approve evidence, edit the Evidence Register or review log, extract new units, or generate analytical thresholds.

## Findings

- Five records describe source-specific suitability ranks or a model-variable definition. Their transfer, calibration and interpretation still require human review.
- Twelve records describe observed practice locations, policy or accounting targets, expert design estimates, or individual sites. These do not establish general T4 establishment limits.

The answers preserve explicit holds: Castle supplementary Table S1 was not recovered; Haile pH ranges remain malformed in the source; Haile soil-carbon units require confirmation and its continuation must be considered as one source-variable vote. No missing values or repaired thresholds are invented.

## Review semantics

The follow-up register uses `status=resolved` to record that the source question has an answer. The clarification service presents these records as **answer_ready**, awaiting a human evidence decision. This is not evidence approval or completion of QA/QC.

After this batch the clarification service reports 47 answer-ready groups and 312 resolved groups, with no groups awaiting source investigation. These counts describe clarification groups only; they do not measure overall corpus review completion. New reviewer questions can reopen investigation.

## Provenance and validation

`answers.json` records each evidence ID, answer, inspected PDF pages, cached-file SHA-256 and outstanding human decision. Existing evidence-field hashes in the follow-up register invalidate answers if their checked content changes. Cached source pages and surrounding context were read; Ahmad and Haile tables, WOCAT checkboxes and the INAB caption were also inspected visually.

`validation.json` records queue and coverage checks. The Evidence Register and review log remain byte-for-byte unchanged. Targeted clarification and T4-recovery tests pass (63 tests). The full suite passes: 992 tests, with five existing SWIG deprecation warnings (142.15 seconds).
