"""Sweep metrics — the measurement half of the iterative-learning loop.

After each extraction sweep, log the register's quality metrics to an append-only
ledger (`pipeline/metrics/sweep_log.csv`) and print the delta vs the previous sweep.
Tracking flag-rates sweep-over-sweep is how we PROVE the pipeline is getting better:
if the number-provenance flag rate or the verify mismatch rate isn't falling, the
extraction spec / checks need another turn of the screw.

Run: `uv run python3 src/nbs_ruralscan/schema_tools/sweep_metrics.py --label <name>`
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

from nbs_ruralscan.schema_tools.check_numbers import check as check_numbers

ROOT = Path(__file__).resolve().parents[3]
LEDGER = ROOT / "pipeline" / "metrics" / "sweep_log.csv"
FIELDS = [
    "date",
    "label",
    "sources",
    "units",
    "numeric",
    "numberprov_flagged",
    "verify_mismatch",
    "verify_unsupported",
    "low_confidence",
    "numberprov_rate_pct",
    "verify_rate_pct",
]


def compute(label: str) -> dict:
    reg = ROOT / "schema" / "registers"
    with (reg / "EV_evidence_register.csv").open(encoding="utf-8") as f:
        ev = list(csv.DictReader(f))
    with (reg / "SRC_source_register.csv").open(encoding="utf-8") as f:
        src = list(csv.DictReader(f))

    numeric = [r for r in ev if (r.get("relationship") or "").strip()]
    attrs = [r.get("attribution") or "" for r in ev]
    mismatch = sum(1 for a in attrs if "[VERIFY-FLAG mismatch" in a)
    unsupported = sum(1 for a in attrs if "[VERIFY-FLAG unsupported" in a)
    low = sum(1 for r in ev if r.get("extraction_confidence") == "low")
    nprov = len(check_numbers(ROOT / "schema"))

    n_num = len(numeric) or 1
    return {
        "date": datetime.now(timezone.utc).date().isoformat(),
        "label": label,
        "sources": len(src),
        "units": len(ev),
        "numeric": len(numeric),
        "numberprov_flagged": nprov,
        "verify_mismatch": mismatch,
        "verify_unsupported": unsupported,
        "low_confidence": low,
        "numberprov_rate_pct": round(100 * nprov / n_num, 1),
        "verify_rate_pct": round(100 * (mismatch + unsupported) / n_num, 1),
    }


def _last() -> dict | None:
    if not LEDGER.exists():
        return None
    rows = list(csv.DictReader(LEDGER.open(encoding="utf-8")))
    return rows[-1] if rows else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--label", required=True, help="short sweep name, e.g. 'track2-agroforestry'"
    )
    args = ap.parse_args()

    prev = _last()
    row = compute(args.label)
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    new = not LEDGER.exists()
    with LEDGER.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)

    print(f"\n=== sweep '{args.label}' logged to {LEDGER.relative_to(ROOT)} ===")
    for k in FIELDS:
        if k in ("date", "label"):
            continue
        cur = row[k]
        if prev and k in prev:
            try:
                d = float(cur) - float(prev[k])
                arrow = "↓" if d < 0 else ("↑" if d > 0 else "=")
                print(f"  {k:22} {cur!s:>8}   ({arrow}{abs(d):g} vs {prev['label']})")
                continue
            except ValueError:
                pass
        print(f"  {k:22} {cur!s:>8}")
    if prev:
        print(
            "\nGoal: numberprov_rate_pct and verify_rate_pct should TREND DOWN each sweep.\n"
            "If they don't, tighten the extract-evidence defect catalogue / add a check."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
