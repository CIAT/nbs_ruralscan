"""Deterministic CROSSWALK-COVERAGE check (ruleset v1.6.0, method §4).

Every live `nbs_effect` outcome variable must (a) have a VONT id and (b) be routed to at
least one T3/T6 cell by an `XW` row — or it is reported `unmapped` (a state, not an error:
catalogued, feeds no cell). `asset_vulnerability` units bypass XW (their cell is
`context.hazard_type`) but still need a VONT id. Flags (advisory):

* `no_vont_id` — variable not a VONT canonical id (→ ontology triage first)
* `unmapped`   — VONT id exists but no XW row routes it anywhere
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
_EV = _ROOT / "schema" / "registers" / "EV_evidence_register.csv"
_VONT = _ROOT / "schema" / "registers" / "VONT_variable_ontology.csv"
_XW = _ROOT / "schema" / "registers" / "XW_target_crosswalk.csv"


def _col(path: Path, col: str) -> set[str]:
    if not path.exists():
        return set()
    with open(path, encoding="utf-8", newline="") as f:
        return {r[col] for r in csv.DictReader(f) if r.get(col)}


def check(
    ev_path: str | Path | None = None,
    vont_path: str | Path | None = None,
    xw_path: str | Path | None = None,
) -> list[dict]:
    p = Path(ev_path) if ev_path else _EV
    if not p.exists():
        return []
    vont = _col(Path(vont_path) if vont_path else _VONT, "canonical_variable_id")
    xw = _col(Path(xw_path) if xw_path else _XW, "ev_variable")
    counts: dict[tuple[str, str], int] = {}
    with open(p, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if (r.get("review_state") or "") == "dropped":
                continue
            role = r.get("use_role")
            if role not in {"nbs_effect", "asset_vulnerability"}:
                continue
            v = r.get("variable", "")
            if vont and v not in vont:
                counts[("no_vont_id", v)] = counts.get(("no_vont_id", v), 0) + 1
            elif role == "nbs_effect" and v not in xw:
                counts[("unmapped", v)] = counts.get(("unmapped", v), 0) + 1
    return [
        {"signal": sig, "variable": v, "n_units": n}
        for (sig, v), n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    flags = check(argv[0] if argv else None)
    if not flags:
        print(
            "XW CHECK: every active effect variable has a VONT id and a crosswalk route."
        )
        return 0
    print(f"XW CHECK: {len(flags)} variable(s) need attention:")
    for f in flags:
        print(f"  [{f['signal']}] {f['variable']} ({f['n_units']} unit(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
