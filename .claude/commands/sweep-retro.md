---
description: Run the post-sweep extraction retrospective (measure -> diagnose -> encode learnings)
---

Run the extraction-sweep retrospective defined in `methodology/extraction_retrospective.md`.
Steps:
1. `uv run python3 src/nbs_ruralscan/schema_tools/sweep_metrics.py --label <sweep-name>` and report the deltas vs the previous sweep (numberprov_rate_pct and verify_rate_pct must trend DOWN).
2. Run the gates: validate_sources, check_numbers, structure, pytest.
3. Triage the [VERIFY-FLAG ...] units + check_numbers misses; group by defect type.
4. For any defect pattern not already covered: add it to the defect catalogue in `.agents/skills/source-command-extract-evidence/SKILL.md` (+ the active EXTRACT_SPEC), and add a deterministic check to `schema_tools/check_numbers.py` if detectable.
5. Commit `chore(retro): sweep <label> — <learning>` with the ledger row + any spec/check changes.
6. If a flag rate did not fall vs last sweep, tighten the spec before the next sweep.
