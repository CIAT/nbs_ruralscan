"""Deterministic TRACEABLE-ACCOUNT check for generated T3/T6 rows (contract §5).

The prose writer may introduce nothing that is not in the row's used units. Checks, for a
JSON file of generated rows against the EV register:

* `number_not_in_evidence` — a numeric literal in `statement` / `evidence_summary` /
                             `agreement_note` / mechanism / conditionality that appears in no
                             cited unit's quote or `relationship` numbers
* `cited_id_not_used`      — an evidence_id named in the account that is not in the row's
                             `evidence_ids`
* `evidence_id_unknown`    — an `evidence_ids` entry that is not a live EV row
* `evidence_id_dropped`    — an `evidence_ids` entry whose EV row is `review_state=dropped`

Counts, ranks and agreement shares the ENGINE writes into the account (n, weights, A) are
whitelisted: they are derived, not evidence.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

from .check_numbers import _nums

_ROOT = Path(__file__).resolve().parents[3]
_EV = _ROOT / "schema" / "registers" / "EV_evidence_register.csv"
_EID = re.compile(r"\bev_[a-z0-9_]+\b")
_PROSE_FIELDS = (
    "statement",
    "evidence_summary",
    "agreement_note",
    "mechanism",
    "conditionality",
)


def _load_ev(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8", newline="") as f:
        return {r["evidence_id"]: r for r in csv.DictReader(f)}


def _unit_numbers(row: dict) -> set[str]:
    nums = _nums(row.get("quote") or "")
    rel = row.get("relationship") or ""
    try:
        rel_o = json.loads(rel) if isinstance(rel, str) else rel
    except Exception:
        rel_o = {}
    if isinstance(rel_o, dict):
        for k in ("magnitude", "magnitude_low", "magnitude_high", "n"):
            v = rel_o.get(k)
            if isinstance(v, (int, float)):
                nums |= _nums(str(v))
    return nums


def check_row(row: dict, ev: dict[str, dict]) -> list[dict]:
    rid = row.get("record_id", "")
    acc = row.get("justification") or {}
    if not isinstance(acc, dict):
        return []
    ids = set(row.get("evidence_ids") or [])
    flags: list[dict] = []
    for eid in sorted(ids):
        if ev and eid not in ev:
            flags.append(
                {"signal": "evidence_id_unknown", "record_id": rid, "detail": eid}
            )
        elif ev and (ev[eid].get("review_state") or "") == "dropped":
            flags.append(
                {"signal": "evidence_id_dropped", "record_id": rid, "detail": eid}
            )
    allowed = set()
    for eid in ids:
        if eid in ev:
            allowed |= _unit_numbers(ev[eid])
    # engine-derived numbers are not evidence claims
    whitelist = {str(row.get("n_sources", "")), str(len(ids))}
    app = row.get("applicability") or {}
    whitelist |= {
        str(app.get("n_sources_in_scope", "")),
        str(app.get("weight_share_in_context", "")),
    }
    whitelist |= {str(acc.get("agreement", ""))}
    for fld in _PROSE_FIELDS:
        text = acc.get(fld)
        if not text:
            continue
        chunks = text if isinstance(text, list) else [text]
        for chunk in chunks:
            s = str(chunk)
            for cid in _EID.findall(s):
                if cid not in ids:
                    flags.append(
                        {
                            "signal": "cited_id_not_used",
                            "record_id": rid,
                            "detail": f"{fld}: {cid}",
                        }
                    )
            if fld == "agreement_note":
                continue  # engine-written counts/shares, not evidence numbers
            s_wo_ids = _EID.sub(" ", s)
            for n in _nums(s_wo_ids) - allowed - whitelist:
                if ev:
                    flags.append(
                        {
                            "signal": "number_not_in_evidence",
                            "record_id": rid,
                            "detail": f"{fld}: {n}",
                        }
                    )
    return flags


def check(rows_path: str | Path, ev_path: str | Path | None = None) -> list[dict]:
    rows = json.loads(Path(rows_path).read_text(encoding="utf-8"))
    ev = _load_ev(Path(ev_path) if ev_path else _EV)
    out: list[dict] = []
    for r in rows:
        out += check_row(r, ev)
    return out


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("usage: check_account.py <generated_rows.json> [EV.csv]")
        return 2
    flags = check(argv[0], argv[1] if len(argv) > 1 else None)
    if not flags:
        print(
            "ACCOUNT CHECK: every number and id in the traceable accounts traces to a used unit."
        )
        return 0
    print(f"ACCOUNT CHECK: {len(flags)} flag(s):")
    for f in flags[:60]:
        print(f"  [{f['signal']}] {f['record_id']}: {f['detail']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
