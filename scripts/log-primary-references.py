#!/usr/bin/env python3
"""Turn second-hand evidence into a discovery list (review theme 6).

    python3 scripts/log-primary-references.py [--nbs <id>] [--out pipeline/staging/primaries.csv]

Pete, 2026-10-12, on a review citing other people's figures: *"use the publications
referenced not a secondary interpretation."* A `claim_basis = cited_secondary` unit already
carries a lower weight, but the fix is to go and get the original. This lists every active
cited-secondary unit with the primary it names (`relationship.lineage_of` / the author-year
in its quote), grouped by how much it is currently carrying — so the acquisition round
targets the ones that actually set classes.

Writes a CSV for the acquisition queue, never the register.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
SRC = ROOT / "schema" / "registers" / "SRC_source_register.csv"
RECIPES = ROOT / "schema" / "recipes"
#: "(Watson et al. 2016)", "Filoso et al. (2017)", "(Mitsch and Gosselink, 2015)"
_CITE = re.compile(
    r"\(?\b([A-Z][A-Za-zÀ-ɏ'-]+(?:\s+(?:et\s+al\.?|and|&)\s+[A-Z][A-Za-zÀ-ɏ'-]+)?)"
    r"[,\s]+\(?((?:19|20)\d{2})[a-z]?\)?"
)


def _cited_in(text: str) -> list[str]:
    out, seen = [], set()
    for who, year in _CITE.findall(text or ""):
        key = f"{who} {year}"
        if key.lower() not in seen:
            seen.add(key.lower())
            out.append(key)
    return out


def _placements() -> Counter:
    """How many generated rows each evidence_id sits in (its reach)."""
    c: Counter = Counter()
    for d in sorted(RECIPES.glob("*")):
        for stem in (
            "T3_nbs_hazard_farming",
            "T6_nbs_scorecard",
            "T6E_economic_profile",
        ):
            f = d / f"{stem}.csv"
            if not f.exists():
                continue
            with f.open(newline="", encoding="utf-8") as fh:
                for r in csv.DictReader(fh):
                    try:
                        for eid in json.loads(r.get("evidence_ids") or "[]"):
                            c[eid] += 1
                    except json.JSONDecodeError:
                        continue
    return c


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--nbs")
    ap.add_argument("--out", default="pipeline/staging/primary_references.csv")
    a = ap.parse_args(argv)
    src = {r["source_id"]: r for r in csv.DictReader(SRC.open(encoding="utf-8"))}
    reach = _placements()
    rows = []
    with EV.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("claim_basis") != "cited_secondary":
                continue
            if (r.get("review_state") or "") == "dropped":
                continue
            if a.nbs and r["nbs_id"] != a.nbs:
                continue
            rel = json.loads(r["relationship"] or "{}")
            named = (r.get("lineage_of") or "").strip() or "; ".join(
                _cited_in(r.get("quote", "") + " " + str(rel.get("outcome_raw") or ""))
            )
            rows.append(
                {
                    "evidence_id": r["evidence_id"],
                    "nbs_id": r["nbs_id"],
                    "variable": r["variable"],
                    "rows_it_feeds": reach.get(r["evidence_id"], 0),
                    "reporting_source": r["source_id"],
                    "reporting_citation": (
                        src.get(r["source_id"], {}).get("citation") or ""
                    )[:160],
                    "primary_named": named,
                    "page": r.get("page", ""),
                    "quote": (r.get("quote") or "")[:300],
                }
            )
    rows.sort(key=lambda x: (-x["rows_it_feeds"], x["nbs_id"], x["evidence_id"]))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    named = sum(1 for r in rows if r["primary_named"])
    print(
        f"{len(rows)} cited-secondary unit(s); {named} name a primary; "
        f"{sum(1 for r in rows if r['rows_it_feeds'] > 0)} currently feed a generated row → {out}"
    )
    print("top by reach:")
    for r in rows[:10]:
        print(
            f"  {r['rows_it_feeds']:>2} rows  {r['evidence_id'][:48]:48s} {r['primary_named'][:50] or '(no primary named)'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
