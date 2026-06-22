"""QA/QC performance stats — measure how well the AI verify-flag system actually works.

The relationship-verify pass FLAGS some EV units (verdict=mismatch/unsupported) and silently
PASSES the rest. Humans then review both (logged in pipeline/metrics/review_log.csv). Crossing
the AI verdict with the human decision gives a confusion matrix — the only honest way to know
whether the AI is catching real errors or crying wolf (and whether it's letting errors through):

                    human: GOOD (ok)            human: BAD (drop / missed_error)
  AI flagged    FP  (false_flag)            TP  (real error caught)
  AI passed     TN  (confirmed_pass)        FN  (error the AI missed — found in spot-check)

precision = TP/(TP+FP)  — of what the AI flagged, how much was real.
recall_est = TP/(TP+FN) — estimate ONLY (FN comes from sampled passes, not a full census).

Stats reflect APPLIED/logged decisions (the durable record), not in-session unapplied ones.
Shipped into dashboard_data.json by generate.py; rendered in the QA/QC tab's Stats view.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LOG = ROOT / "pipeline" / "metrics" / "review_log.csv"

_FLAGGED = {"mismatch", "unsupported"}
# The verify-flag pass only checks NUMBER/RELATIONSHIP provenance. A pass it "let through"
# is only a false negative if the human dropped it for a reason WITHIN that remit. Drops for
# SCOPE/quality reasons (off_scope, wrong_practice, …) are a different failure class the verify
# pass never checks (that's check_scope/check_quote) — counting them as FN unfairly blames it.
_VERIFY_REMIT = {
    "smuggled_number",
    "cross_row_stitch",
    "wrong_variable",
    "table_garble",
    "missed_error",
}
_SCOPE_QUALITY = {"off_scope", "wrong_practice", "species_envelope", "quote_too_narrow"}


def _pct(n: int, d: int) -> float | None:
    return round(100 * n / d, 1) if d else None


def compute(log_path: str | Path | None = None) -> dict:
    """Read review_log.csv -> QA/QC performance summary (confusion matrix + tallies)."""
    path = Path(log_path) if log_path else LOG
    rows: list[dict] = []
    if path.exists():
        with path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    # De-dup: the log appends on every apply run, so raw rows over-count a re-applied
    # decision (220 raw -> 68 distinct, 2026-06-22). Count distinct reviews.
    from nbs_ruralscan.schema_tools.review import latest_review_rows

    rows = latest_review_rows(rows)

    by_reviewer: Counter = Counter()
    by_decision: Counter = Counter()
    by_reason: Counter = Counter()
    by_verdict: Counter = Counter()
    tp = fp = tn = fn = 0
    tp_removed = tp_corrected = 0
    out_of_remit = (
        0  # AI passed; human dropped for SCOPE/quality (not the verify pass's job)
    )
    queried = (
        0  # 'query' = tentatively kept + open question — a 3rd outcome, not good/bad
    )

    for r in rows:
        verdict = (r.get("verdict") or "").strip().lower()
        dec = (r.get("decision") or "").strip().lower()
        reason = (r.get("reason") or "").strip().lower()
        by_reviewer[(r.get("reviewer") or "unknown").strip() or "unknown"] += 1
        by_decision[dec or "blank"] += 1
        by_reason[reason or "unspecified"] += 1
        by_verdict[verdict or "pass"] += 1
        if dec in ("flag", "query"):
            # tentatively kept, unresolved — exclude from the good/bad confusion matrix
            queried += 1
            continue
        flagged = verdict in _FLAGGED
        if flagged:
            if dec == "drop":
                tp += 1
                tp_removed += 1  # caught a real error -> removed
            elif dec == "ok" and reason == "false_flag":
                fp += 1  # AI was wrong -> false alarm
            elif dec == "ok":
                tp += 1
                tp_corrected += 1  # caught a real problem -> auto-fix accepted, kept
            # blank decision: undecided, not counted
        else:  # AI passed; this row is a human spot-check of a pass
            if dec == "ok":
                tn += 1
            elif dec == "drop":
                if reason in _SCOPE_QUALITY:
                    # scope/quality issue — outside the verify pass's remit, NOT an FN
                    out_of_remit += 1
                elif reason in _VERIFY_REMIT:
                    fn += 1  # verify pass genuinely let a number/relationship error through
                else:
                    # blank / 'other' / unspecified — ambiguous; don't blame the verify pass
                    out_of_remit += 1

    return {
        "total_reviews": len(rows),
        "queried": queried,
        "n_reviewers": len(by_reviewer),
        "by_reviewer": dict(by_reviewer.most_common()),
        "by_decision": dict(by_decision),
        "by_reason": dict(by_reason.most_common()),
        "by_verdict": dict(by_verdict),
        "flag_eval": {
            "tp": tp,
            "fp": fp,
            "n": tp + fp,
            "precision_pct": _pct(tp, tp + fp),
            "tp_removed": tp_removed,
            "tp_corrected": tp_corrected,
        },
        "pass_eval": {
            "tn": tn,
            "fn": fn,
            "out_of_remit": out_of_remit,  # scope/quality drops — not the verify pass's job
            "checked": tn + fn + out_of_remit,
            "fn_rate_pct": _pct(fn, tn + fn),  # FN only over verify-relevant passes
        },
        # recall is unknowable until passes are spot-checked (no FN evidence otherwise)
        "recall_est_pct": _pct(tp, tp + fn) if (tn + fn) > 0 else None,
        "errors_caught": tp,
        "errors_missed_in_sample": fn,
    }


def main(argv: list[str] | None = None) -> int:
    import json
    import sys

    s = compute(argv[0] if argv else None)
    json.dump(s, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
