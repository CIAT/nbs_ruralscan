# Ruleset v1.3 — 2026-07-18

Snapshot of the extract-evidence skill + command in force from v1.3. Pin: `SRCH.ruleset_version` / `EV.ruleset_version = v1.3`.

## Change vs v1.2

**Catalogue #16 — `site_context` (single-study site context ≠ suitability rule).**
The #1 recurring reviewer complaint in the 2026-07 FMNR QA: a study's own site descriptors
(rainfall 900 mm, temp 28 °C, Lixisol soils, 30 trees·ha⁻¹), figure captions, and region
descriptors were extracted as `structural_suitability`. Sharpens #8 from "wrong *section*"
to "wrong *kind of claim*":

- A `structural_suitability` unit must encode a **rule that GENERALISES** (threshold / range /
  gradient / requirement / comparison across suitable-vs-unsuitable land).
- A lone report of the study's own location is **n = 1 context** — "where did you work?", not
  "where does the practice work?" — and must NOT be extracted as suitability. A range/number in
  the sentence does not make it a rule; the study/figure/region FRAMING disqualifies it.
- **"Constrain by observed distribution" is a run-time DATASET-gating layer** (mask by a
  MapSPAM / EO host-distribution map, via BIND) — **not** a licence to encode one paper's site
  measurement as a T4 threshold.
- Single-site observation → drop, or if a genuine outcome route to T6.

New deterministic guard: `check_scope.py` `site_context` signal (FRAME or site-occurrence
direction, MINUS a suitability criterion, MINUS a distributional generalisation). Tuned to
6/6 of the 2026-07 FMNR site-context drops with 0 genuine-rule false-positives (validated
against Pete's merged QA decisions).

## Also in this release (infra, not a rule change)

`review_server.py` decisions-store write is now atomic (temp file + `os.replace` under a
threading lock). Fixes a concurrent-write race (an `/api/decision` write interleaving the
`/api/submit` rewrite) that left a valid-prefix + stale-tail `decisions.json`, failed to
parse, and silently hid all pending decisions from the dashboard.

## Trigger

2026-07 FMNR (agroforestry F2 regeneration_farmland) sweep + Pete's QA review — study context
repeatedly extracted as biophysical suitability, plus the decisions.json corruption during
review submit.
