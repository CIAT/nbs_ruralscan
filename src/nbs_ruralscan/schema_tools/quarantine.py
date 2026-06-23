"""Auto-quarantine off-scope / wrong-practice evidence (QA guard "B", 2026-06-23).

2026-06-23 human QA dropped 61/102 reviewed units (60%) — dominated by off-scope
extraction (study-site / problem-statement / biomass / mapped-result *descriptions*) and
wrong-practice mis-mapping (reforestation, CSA umbrella tagged as agroforestry). The
deterministic checks (`check_scope`, `check_picos`) already flag these; this module ACTS on
them — soft-deleting (`review_state=dropped`) so they stop polluting the live register and
the AI-flagged worklist, while staying fully reversible + auditable (the locked soft-delete
model). Chosen over a build-FAIL because the signals are regex proxies: the reviewer keeps
the final call (re-open restores the row); the guard just stops junk reaching them by default.

SAFETY — never re-quarantines a row a human has touched:
  * `reviewer_ok=true`           — already signed off
  * `review_state` already set   — already dropped/quarantined
  * evidence_id in `review_log`  — a human applied a decision (incl. a re-open)
  * evidence_id in `decisions.json` — a human has an in-progress decision

Each quarantined row is stamped `[AUTO-QUARANTINE <kind>:<signal>]` in `attribution`
(idempotent) so the dashboard's dropped view + git history show exactly why.

Run on the WRITE path of `generate.py` only (never on `--check`, which must not mutate).
CLI: `python -m nbs_ruralscan.schema_tools.quarantine schema [--apply]` (default = dry-run).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from nbs_ruralscan.schema_tools import check_picos, check_scope

ROOT = Path(__file__).resolve().parents[3]
_MARKER = "[AUTO-QUARANTINE "


def _human_touched(schema_root: Path) -> set[str]:
    """evidence_ids a human has decided on (applied review_log OR in-progress decisions)."""
    touched: set[str] = set()
    rl = schema_root.parent / "pipeline" / "metrics" / "review_log.csv"
    if rl.exists():
        with rl.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("evidence_id"):
                    touched.add(r["evidence_id"])
    dj = schema_root.parent / "pipeline" / "review" / "decisions.json"
    if dj.exists():
        try:
            touched.update(json.loads(dj.read_text(encoding="utf-8")).keys())
        except (json.JSONDecodeError, OSError):
            pass
    return touched


def _tool_evidence_ids(root: Path) -> set[str]:
    """evidence_ids whose source is a tool — exempt from the paper-section scope signals.

    Tool EV is interrogated differently (code/criteria via file_line/section provenance);
    its "soil carbon" is a suitability *criterion*, not a carbon-accounting section, so the
    off-scope/PICOS proxies (built for papers) false-positive on it. Skip tool-channel rows.
    """
    src = root / "registers" / "SRC_source_register.csv"
    tool_sids: set[str] = set()
    if src.exists():
        with src.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if (r.get("source_category") or "") == "tool":
                    tool_sids.add(r.get("source_id", ""))
    ev = root / "registers" / "EV_evidence_register.csv"
    ids: set[str] = set()
    if tool_sids and ev.exists():
        with ev.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("source_id") in tool_sids:
                    ids.add(r.get("evidence_id", ""))
    return ids


def candidates(schema_root: str | Path = "schema") -> list[dict]:
    """Eligible auto-quarantine rows: [{evidence_id, kind, signal, snippet}] (no mutation)."""
    root = Path(schema_root)
    ev = root / "registers" / "EV_evidence_register.csv"
    if not ev.exists():
        return []
    flags: dict[str, dict] = {}
    for f in check_scope.check(ev):
        flags.setdefault(f["evidence_id"], {"kind": "off_scope", **f})
    for f in check_picos.check(ev):  # wrong-practice; don't overwrite an off_scope hit
        flags.setdefault(f["evidence_id"], {"kind": "wrong_practice", **f})
    touched = _human_touched(root) | _tool_evidence_ids(root)
    out = []
    for eid, f in flags.items():
        if eid in touched:
            continue
        out.append(
            {
                "evidence_id": eid,
                "kind": f["kind"],
                "signal": f["signal"],
                "snippet": f.get("snippet", ""),
            }
        )
    return out


def apply(schema_root: str | Path = "schema") -> list[dict]:
    """Set review_state=dropped + stamp attribution for every candidate. Idempotent."""
    root = Path(schema_root)
    ev = root / "registers" / "EV_evidence_register.csv"
    cands = {c["evidence_id"]: c for c in candidates(root)}
    if not cands:
        return []
    with ev.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        rows = list(reader)
    applied: list[dict] = []
    for r in rows:
        c = cands.get(r.get("evidence_id", ""))
        if not c:
            continue
        if (r.get("review_state") or "") == "dropped":
            continue
        r["review_state"] = "dropped"
        stamp = f"{_MARKER}{c['kind']}:{c['signal']}]"
        if _MARKER not in (r.get("attribution") or ""):
            r["attribution"] = (
                (r.get("attribution") or "").rstrip() + " " + stamp
            ).strip()
        applied.append(c)
    if applied:
        with ev.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
    return applied


def main(argv: list[str] | None = None) -> int:
    import sys

    argv = argv if argv is not None else sys.argv[1:]
    root = next((a for a in argv if not a.startswith("-")), "schema")
    do_apply = "--apply" in argv
    if do_apply:
        applied = apply(root)
        print(
            f"AUTO-QUARANTINE: dropped {len(applied)} off-scope/wrong-practice unit(s)."
        )
    else:
        applied = candidates(root)
        print(f"AUTO-QUARANTINE (dry-run): {len(applied)} candidate(s) — pass --apply:")
    for c in applied:
        print(f"  [{c['kind']}/{c['signal']}] {c['evidence_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
