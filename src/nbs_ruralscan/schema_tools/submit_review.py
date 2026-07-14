"""Headless apply of the local QA decisions — the non-UI half of the dashboard's
"Apply decisions & rebuild", for scripts/submit-review.sh.

Reads the per-reviewer decision store (pipeline/review/decisions.json), reduces it to
CONSENSUS decisions (a flag is applied only when every reviewer who decided it agrees; a
disagreement is left as a conflict and skipped), applies them to the CURRENT registers via
`apply_decisions`, and regenerates the JSON. Because it runs against whatever EV rows exist
*now*, it applies surgically — so a reviewer whose local branch drifted from main never
reverts other people's rows (the recurring pain that buried tiny review edits in 50k-line
generated-JSON churn + stale-branch reverts).

CLI:  uv run python3 -m nbs_ruralscan.schema_tools.submit_review
"""

from __future__ import annotations

import json
from pathlib import Path

from nbs_ruralscan.schema_tools.generate import generate
from nbs_ruralscan.schema_tools.review import apply_decisions

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / "pipeline" / "review" / "decisions.json"


def _load_store() -> dict:
    if not STORE.exists():
        return {}
    raw = STORE.read_bytes()
    try:
        return json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError:
        return json.loads(raw.decode("cp1252"))  # tolerate a stray Windows byte


def consensus_decisions(store: dict) -> tuple[dict, list[str]]:
    """Reduce the (evidence_id × reviewer) store to a flat {evidence_id: {...}} of AGREED
    decisions + a list of conflicted evidence_ids. Mirrors the dashboard /api/apply logic."""
    decisions: dict = {}
    conflicts: list[str] = []
    for eid, byrev in store.items():
        decs = {rv: v for rv, v in byrev.items() if (v.get("decision") or "").strip()}
        if not decs:
            continue
        vals = {v["decision"] for v in decs.values()}
        if len(vals) == 1:
            entry = {
                "decision": next(iter(vals)),
                "reason": ";".join(
                    sorted(
                        {v.get("reason", "") for v in decs.values() if v.get("reason")}
                    )
                ),
                "note": " | ".join(
                    v.get("note", "") for v in decs.values() if v.get("note")
                ),
                "reviewer": ",".join(sorted(decs.keys())),
            }
            # a `reclassify` decision carries the target claim_scope + taxon — preserve them
            # through the consensus reduction so apply_decisions can retag the row.
            _tax = next((v.get("taxon") for v in decs.values() if v.get("taxon")), "")
            _cs = next(
                (v.get("claim_scope") for v in decs.values() if v.get("claim_scope")),
                "",
            )
            if _tax:
                entry["taxon"] = _tax
            if _cs:
                entry["claim_scope"] = _cs
            decisions[eid] = entry
        else:
            conflicts.append(eid)
    return decisions, conflicts


def main() -> int:
    store = _load_store()
    decisions, conflicts = consensus_decisions(store)
    if not decisions:
        print("submit_review: no agreed decisions to apply (nothing to do).")
        if conflicts:
            print(
                f"  ({len(conflicts)} conflicted, left pending: {', '.join(conflicts)})"
            )
        return 0
    res = apply_decisions(decisions, "consensus")
    generate(ROOT / "schema")
    print(f"submit_review: applied {res}")
    if conflicts:
        print(f"  conflicts skipped (left pending): {', '.join(conflicts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
