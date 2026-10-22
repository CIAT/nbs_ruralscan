#!/usr/bin/env python3
"""Build a ROW-review batch (generated T3/T6 rows) for the review page (docs/review.html).

    python3 scripts/build-row-review-batch.py <batch_id> --nbs <nbs_id> --title "..." \
        [--rows rows.csv | --all-rollups] [--notes "..."]

`rows.csv` columns: record_id (required), question (optional: why this row needs a look).
`--all-rollups` takes every NbS roll-up row (no family, no scope) from both tables. Writes
`docs/review/<batch_id>.json` with ``"kind": "rows"`` (one card per generated row: class,
confidence, prose, statement, family vote, held-out units and the evidence it rests on, each
unit with its citation and a trimmed verbatim quote) and adds the batch to
`docs/review/index.json` with kind "rows". Reads the recipe tables + EV/SRC registers only;
never edits them. Decisions come back through scripts/apply-row-review-export.py.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "schema" / "recipes"
EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
SRC = ROOT / "schema" / "registers" / "SRC_source_register.csv"
OUT = ROOT / "docs" / "review"
TABLES = {"T3": "T3_nbs_hazard_farming.csv", "T6": "T6_nbs_scorecard.csv"}
QUOTE_MAX = 400
#: row reject codes (the page carries the same list + gloss)
ROW_REASONS = [
    "wrong_class",
    "wrong_confidence",
    "prose_misleading",
    "evidence_misrouted",
    "should_be_split",
    "other",
]


def _j(s: str | None, default=None):
    if not s:
        return default
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return default


def _trim(q: str, n: int = QUOTE_MAX) -> str:
    q = " ".join((q or "").split())
    return q if len(q) <= n else q[: n - 1].rstrip() + "…"


def load_rows(nbs_id: str, recipes: Path = RECIPES) -> list[tuple[str, dict]]:
    out = []
    for table, fname in TABLES.items():
        p = recipes / nbs_id / fname
        if not p.exists():
            continue
        with p.open(newline="", encoding="utf-8") as f:
            out += [(table, r) for r in csv.DictReader(f)]
    return out


def is_rollup(r: dict) -> bool:
    return (
        not (r.get("suitability_family_id") or "").strip()
        and not (r.get("scope_type") or "").strip()
    )


def _unit(eid: str, ev: dict, src: dict) -> dict:
    r = ev.get(eid)
    if not r:
        return {"evidence_id": eid, "missing": True}
    rel = _j(r.get("relationship"), {}) or {}
    s = src.get(r.get("source_id", ""), {})
    return {
        "evidence_id": eid,
        "source_id": r.get("source_id", ""),
        "citation": s.get("citation", ""),
        "variable": r.get("variable", ""),
        "direction": rel.get("direction", ""),
        "strength": rel.get("strength_class", ""),
        "claim_basis": r.get("claim_basis", ""),
        "suitability_family_id": r.get("suitability_family_id", ""),
        "page": r.get("page", ""),
        "review_state": r.get("review_state", ""),
        "quote": _trim(r.get("quote", "")),
    }


def card(table: str, r: dict, ev: dict, src: dict, question: str = "") -> dict:
    j = _j(r.get("justification"), {}) or {}
    if table == "T6":
        target = {"priority": r.get("variable_id", "")}
        target_label = r.get("variable_id", "")
        cls_field = "effect_direction"
        confidence = r.get("effect_confidence", "")
        mech_col, cond_col = "effect_mechanism", "conditionality"
    else:
        role = r.get("risk_role", "")
        target = {
            "hazard": r.get("hazard_type", ""),
            "farming_system": r.get("farming_system", ""),
            "risk_role": role,
        }
        target_label = f"{r.get('hazard_type', '')} × {r.get('farming_system', '')}"
        if role and role != "livelihood_mitigation":
            target_label += f" ({role})"
        cls_field = (
            "asset_sensitivity" if role == "asset_threat" else "mitigation_potential"
        )
        confidence = r.get("confidence", "")
        mech_col, cond_col = "mitigation_mechanism", "caveats"
    held = j.get("held_out_of_class") or {}
    return {
        "record_id": r.get("record_id", ""),
        "table": table,
        "nbs_id": r.get("nbs_id", ""),
        "suitability_family_id": r.get("suitability_family_id", ""),
        "scope": ":".join(
            x for x in (r.get("scope_type", ""), r.get("scope_id", "")) if x
        ),
        "target": target,
        "target_label": target_label,
        "class": {"field": cls_field, "value": r.get(cls_field, "")},
        "confidence": confidence,
        "evidence_level": r.get("evidence_level", ""),
        "agreement_level": r.get("agreement_level", ""),
        "data_deficient": bool(j.get("data_deficient")),
        "data_deficient_reason": j.get("data_deficient_reason", ""),
        "conflicting": bool(j.get("conflicting")),
        "mechanism": j.get("mechanism") or r.get(mech_col, ""),
        "conditionality": j.get("conditionality") or r.get(cond_col, ""),
        "statement": j.get("statement", ""),
        "pool_note": j.get("pool_note", ""),
        "family_vote": j.get("family_vote") or None,
        "held_out_of_class": [
            {"reason": k, "units": [_unit(e, ev, src) for e in (ids or [])]}
            for k, ids in held.items()
        ],
        "evidence": [_unit(e, ev, src) for e in (_j(r.get("evidence_ids"), []) or [])],
        "question": question,
    }


def build_cards(
    nbs_id: str,
    wanted: dict[str, str] | None = None,
    all_rollups: bool = False,
    recipes: Path = RECIPES,
    ev_path: Path = EV,
    src_path: Path = SRC,
) -> tuple[list[dict], list[str]]:
    """Cards for the wanted record_ids ({id: question}) and/or every roll-up row."""
    wanted = wanted or {}
    with ev_path.open(newline="", encoding="utf-8") as f:
        ev = {r["evidence_id"]: r for r in csv.DictReader(f)}
    with src_path.open(newline="", encoding="utf-8") as f:
        src = {r["source_id"]: r for r in csv.DictReader(f)}
    cards, seen = [], set()
    for table, r in load_rows(nbs_id, recipes):
        rid = r.get("record_id", "")
        if rid in wanted or (all_rollups and is_rollup(r)):
            cards.append(card(table, r, ev, src, wanted.get(rid, "")))
            seen.add(rid)
    return cards, [k for k in wanted if k not in seen]


def write_batch(
    batch_id: str,
    title: str,
    cards: list[dict],
    notes: str = "",
    out_dir: Path = OUT,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    p = out_dir / f"{batch_id}.json"
    p.write_text(
        json.dumps(
            {
                "kind": "rows",
                "batch": {
                    "id": batch_id,
                    "title": title,
                    "date": today,
                    "notes": notes,
                    "n": len(cards),
                    "kind": "rows",
                },
                "reasons": ROW_REASONS,
                "rows": cards,
            },
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    idx_p = out_dir / "index.json"
    idx = (
        json.loads(idx_p.read_text(encoding="utf-8"))
        if idx_p.exists()
        else {"batches": []}
    )
    idx["batches"] = [b for b in idx["batches"] if b["id"] != batch_id] + [
        {
            "id": batch_id,
            "title": title,
            "date": today,
            "n": len(cards),
            "file": f"review/{batch_id}.json",
            "kind": "rows",
        }
    ]
    idx_p.write_text(
        json.dumps(idx, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return p


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("batch_id")
    ap.add_argument("--nbs", required=True)
    ap.add_argument("--title", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--rows", help="CSV with record_id[,question]")
    g.add_argument("--all-rollups", action="store_true")
    ap.add_argument("--notes", default="")
    a = ap.parse_args(argv)
    wanted: dict[str, str] = {}
    if a.rows:
        with open(a.rows, newline="", encoding="utf-8") as f:
            wanted = {
                r["record_id"].strip(): (r.get("question") or "").strip()
                for r in csv.DictReader(f)
                if (r.get("record_id") or "").strip()
            }
    cards, missing = build_cards(a.nbs, wanted, a.all_rollups)
    write_batch(a.batch_id, a.title, cards, a.notes)
    print(
        f"{len(cards)} row card(s) → docs/review/{a.batch_id}.json; missing ids: {missing}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
