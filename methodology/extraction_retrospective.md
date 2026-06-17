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
     `.agents/skills/source-command-extract-evidence/SKILL.md` AND the active EXTRACT_SPEC.
   - Deterministically detectable? → add/extend a check in `schema_tools/check_numbers.py`
     (or a sibling checker) so it's caught for free next time, not by an LLM pass.
   - Schema gap? → a `methodology/schema_changes/` record + issue.

5. **Commit** `chore(retro): sweep <label> — <one-line learning>` including the ledger row
   and any spec/check changes.

6. **Trend check.** If a rate did NOT fall vs last sweep, the spec change in step 4 was
   insufficient — tighten it before the next sweep.

## Pre-LLM triage (efficiency)
`check_numbers.py` is free and deterministic. Run it FIRST; only send its flagged units +
the `extraction_confidence=low` ones to the (expensive) adversarial relationship-verify.
Over sweeps, as the spec tightens, fewer units should reach the LLM pass.

## What "better" looks like
- `numberprov_rate_pct` ↓ (fewer smuggled numbers)
- `verify_rate_pct` ↓ (fewer faithfulness defects)
- catalogue grows; share of defects caught deterministically (vs by LLM) grows.
