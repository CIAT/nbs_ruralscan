#!/usr/bin/env python3
"""Apply a bundle-annotation backfill to EV context (review theme 1A, ruleset v1.6.7).

    python3 scripts/apply-bundle-backfill.py pipeline/staging/bundle_backfill.json [--dry-run]

Input: `{evidence_id: {attribution, bundle_components[], component_share_pct, component_share_kind,
component_share_basis, component_share_page, nbs_component, note, recommend, recommend_why}}`.
Only `context` changes: quote, page, relationship and claim are untouched. A share is refused
unless `component_share_basis` is verbatim on `component_share_page` of the cached PDF — the
same discipline as a quote. `recommend = exclude` is NOT applied here: dropping evidence is a
review decision, made in the review page or `apply-review-export.py`.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
CORPUS = ROOT / ".cache" / "corpus"
FIELDS = (
    "attribution",
    "bundle_components",
    "component_share_pct",
    "component_share_kind",
    "nbs_component",
)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s or "")).strip()


def verify_basis(source_id: str, page: int | None, basis: str | None) -> str:
    if not basis:
        return ""
    if not page:
        return "share basis given without a page"
    pdf = CORPUS / f"{source_id}.pdf"
    if not pdf.exists():
        return f"no cached PDF for {source_id}"
    import fitz

    with fitz.open(pdf) as doc:
        if page < 1 or page > len(doc):
            return f"page {page} out of range"
        if _norm(basis) not in _norm(doc[page - 1].get_text()):
            return f"share basis not verbatim on page {page}"
    return ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("payload")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    data = json.loads(Path(a.payload).read_text(encoding="utf-8"))
    with EV.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        cols = list(rd.fieldnames or [])
        rows = list(rd)
    applied, refused, excl = 0, [], []
    for r in rows:
        p = data.get(r["evidence_id"])
        if not p:
            continue
        why = verify_basis(
            r["source_id"],
            p.get("component_share_page"),
            p.get("component_share_basis"),
        )
        if why:
            refused.append((r["evidence_id"], why))
            continue
        ctx = json.loads(r["context"] or "{}")
        for k in FIELDS:
            if p.get(k) not in (None, "", []):
                ctx[k] = p[k]
        bits = [
            f"bundle check 2026-10-12: {p.get('note') or ''}".strip(),
            f"NbS component: {p.get('nbs_component')}"
            if p.get("nbs_component")
            else "",
            f"share basis (p{p.get('component_share_page')}): {p.get('component_share_basis')}"
            if p.get("component_share_basis")
            else "",
        ]
        add = "process: " + "; ".join(b for b in bits if b)
        prev = str(ctx.get("note") or "")
        if add not in prev:
            ctx["note"] = (prev + " | " if prev else "") + add
        r["context"] = json.dumps(ctx, ensure_ascii=False)
        applied += 1
        if p.get("recommend") == "exclude":
            excl.append((r["evidence_id"], p.get("recommend_why") or ""))
    for eid, why in refused:
        print("REFUSED", eid, why)
    print(f"annotated {applied} unit(s); refused {len(refused)}")
    for eid, why in excl:
        print(f"  RECOMMENDED EXCLUDE (needs a review decision): {eid} — {why}")
    if a.dry_run:
        return 0
    with EV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print("now: python3 src/nbs_ruralscan/schema_tools/generate.py schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
