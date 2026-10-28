# Extraction sweep retrospective — the iterative-learning loop

> Run this after EVERY extraction sweep. The point: each sweep makes the pipeline
> measurably better than the last. Measure → diagnose new defects → encode them as a
> spec rule + (where possible) an automated check → re-measure next sweep.

## Why
Quote-verbatim ≠ faithful. The first two sweeps had ~40% of numeric units flagged on
relationship-faithfulness. We only improve if we (a) measure the flag rate every sweep and
(b) feed each new defect pattern back into the spec and the automated checks.

## The loop (after a sweep's units are merged + gated)

1. **Measure.** `uv run python3 src/nbs_ruralscan/schema_tools/sweep_metrics.py --label <sweep>`
   — appends quality metrics to `pipeline/metrics/sweep_log.csv` and prints the delta vs the
   previous sweep. **`numberprov_rate_pct` and `verify_rate_pct` must trend DOWN.**

2. **Gate.** Confirm green: `validate_sources` (verbatim+page), `check_numbers` (number
   provenance), `structure`, `pytest`.

3. **Triage flags.** Read the [VERIFY-FLAG …] units + `check_numbers` misses. Group by
   defect type. Ask: is any pattern NOT already in the extract-evidence skill's defect
   catalogue?

4. **Encode the learning** (this is the ratchet — do at least one each sweep if flags > 0):
   - New defect pattern → add it to the defect catalogue in
     `.agents/skills/source-command-extract-evidence/references/defects.md`, referenced by the canonical skill. Bump the ruleset and snapshot the skill, contracts and command together.
   - Deterministically detectable? → add/extend a check in `schema_tools/check_numbers.py`
     (or a sibling checker) so it's caught for free next time, not by an LLM pass.
   - Schema gap? → a `methodology/schema_changes/` record + issue.

5. **Commit** `chore(retro): sweep <label> — <one-line learning>` including the ledger row
   and any spec/check changes.

6. **Trend check.** If a rate did NOT fall vs last sweep, the spec change in step 4 was
   insufficient — tighten it before the next sweep.

## QA/QC review feeds the loop (reason codes)

Human verify-flag review (QA/QC tab / `review.py`) is the other signal source. Each decision
carries a **reason code** — `smuggled_number · cross_row_stitch · wrong_variable ·
table_garble · off_scope · quote_too_narrow · false_flag · accepted_correction · other` —
logged to `pipeline/metrics/review_log.csv` on apply. In the retrospective:

1. `sweep_metrics.py` prints the **review reason tally**.
2. Route the **top reason** to its fix:
   - `smuggled_number` → already caught by `check_numbers.py`; tighten extraction spec.
   - `cross_row_stitch` / `table_garble` → improve `ingest/pdf.py` table handling + spec
     ("quote a whole table row+header, never stitch rows").
   - `wrong_variable` → VONT aliases + spec proxy rules (SOM≠SOC …).
   - `quote_too_narrow` → spec: capture wider context.
   - `off_scope` → tighten **screening** (down-weight that source class / venue).
   - `false_flag` → loosen the verifier (it over-flagged).
3. Re-measure next sweep — the routed reason's rate should fall.

This turns QA/QC from "clean this batch" into "the pipeline learns from every review."

## Pre-LLM triage (efficiency)
`check_numbers.py` is free and deterministic. Run it FIRST; only send its flagged units +
the `extraction_confidence=low` ones to the (expensive) adversarial relationship-verify.
Over sweeps, as the spec tightens, fewer units should reach the LLM pass.

## What "better" looks like
- `numberprov_rate_pct` ↓ (fewer smuggled numbers)
- `verify_rate_pct` ↓ (fewer faithfulness defects)
- catalogue grows; share of defects caught deterministically (vs by LLM) grows.


## 21 October 2026 — T4 omission feedback

Pete identified weight-only Ahmad records despite Table 2 giving suitability directions and additional soil criteria. Conflicting old skill advice treated uncalibrated direction as unusable, while catalogue #12 required preserving relationships. Ruleset v1.6.16 removes that conflict and supplies a mandatory extraction/adversarial-review contract. Review must audit omissions, table coverage and shared weights, not only fidelity of emitted records. This instruction update is not a completed evidence backfill: Ahmad directions, six soil properties and categorical exclusions still require source-provenanced extraction/review. Existing human decisions remain unchanged. No extraction sweep or improved defect-rate claim is made here.


## 21 October 2026 — bounded agroforestry T4 re-review

Scope: 16 sources reached through live T4 evidence links plus recent recovery sources; no new discovery or full corpus sweep. Three source-review agents used v1.6.16 contract; remaining three sources were checked by the coordinating agent. Inventories and unresolved claims live in `pipeline/t4_audit/agroforestry/bounded_review_2026-10-21/`.

53 pending companions were staged. One Chuma land-use record was automatically quarantined because it documents model use without classes; its model-use metadata remains available. No prior human approval was changed. Six Ahmad soil-property mappings and categorical exclusions remain source-inventory holds. Conflicting Haile table weights now suppress a settled effective weight. New regression checks cover current live-source coverage, approval preservation, image identity, lineage/context-separated directions and conflicting weights.

Numeric provenance caught comma-separated categorical codes being parsed as decimals/thousands; source codes are now explicit lists. Whole-table Mushtaq quotes were narrowed to the relevant row with a separate native caption/header. Short native table-row quotes retain separate header provenance; advisory width flags are not treated as automatic evidence rejection. Global metrics are recorded but do not demonstrate a full-sweep improvement. Existing source/mapping defects remain explicit review items rather than silently rewriting approved evidence.

## Feedback accounting (v1.7.0)

`learnings.status` distinguishes the historical count estimate from content fingerprints.
Changed decisions/reasons/notes on an existing evidence × reviewer pair count as new learning
work; repeated applies with unchanged content do not. `learnings.record` records the complete
current feedback snapshot: use it only after reading that complete set. A bounded maintenance
pass reports its exact scope and leaves the global cursor unchanged. Flag-rate comparisons
require comparable scope and denominators; a smaller/easier batch is not proof of improvement.
