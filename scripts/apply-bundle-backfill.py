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
import sys
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.schema_tools.record_publication import edit_records  # noqa: E402
from nbs_ruralscan.schema_tools.review_inputs import ReviewInputs  # noqa: E402
from nbs_ruralscan.schema_tools.specialist_records import (  # noqa: E402
    evidence,
    json_field,
    keyed_records,
    source_pdf,
    rebuild_command,
    write_table,
)
from nbs_ruralscan.schema_tools.check_context import ATTRIBUTION, SHARE_KIND  # noqa: E402

EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
CORPUS = ROOT / ".cache" / "corpus"
FIELDS = (
    "attribution",
    "bundle_components",
    "component_share_pct",
    "component_share_kind",
    "nbs_component",
)


def _norm(s: str | None) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s or "")).strip()


def verify_basis(
    source_id: str, page: int | None, basis: str | None, *, corpus: Path = CORPUS
) -> str:
    if not basis:
        return ""
    if not _norm(basis):
        return "empty component share basis"
    if not isinstance(page, int) or isinstance(page, bool) or not page:
        return "share basis given without a page"
    pdf = source_pdf(corpus, source_id)
    if not pdf.exists():
        return f"no cached PDF for {source_id}"
    import fitz

    with fitz.open(pdf) as doc:
        if page < 1 or page > len(doc):
            return f"page {page} out of range"
        if _norm(basis) not in _norm(doc[page - 1].get_text()):
            return f"share basis not verbatim on page {page}"
    return ""


def annotate(ev: Path, payload: Path, corpus: Path, inputs: ReviewInputs) -> None:
    data = keyed_records(payload, array=False)
    cols, rows = evidence(ev, "context")
    applied, refused, excl = 0, [], []
    for r in rows:
        p = data.get(r["evidence_id"])
        if p is None:
            continue
        eid = r["evidence_id"]
        if not p or any(
            p.get(k) not in (None, "") and not isinstance(p[k], str)
            for k in (
                "component_share_basis",
                "attribution",
                "component_share_kind",
                "nbs_component",
                "note",
                "recommend",
                "recommend_why",
            )
        ):
            raise ValueError(f"Malformed bundle annotation for {eid}")
        components = p.get("bundle_components")
        if components is not None and (
            not isinstance(components, list)
            or not all(isinstance(v, str) and v.strip() for v in components)
        ):
            raise ValueError(f"Malformed bundle_components for {eid}")
        if (
            p.get("attribution")
            and p["attribution"] not in ATTRIBUTION
            or p.get("component_share_kind")
            and p["component_share_kind"] not in SHARE_KIND
        ):
            raise ValueError(f"Invalid bundle attribution or share kind for {eid}")
        share = p.get("component_share_pct")
        basis = p.get("component_share_basis")
        if share not in (None, ""):
            if (
                isinstance(share, bool)
                or not isinstance(share, (str, int, float))
                or not 0 <= float(share) <= 100
            ):
                raise ValueError(f"Invalid component_share_pct for {eid}")
            if not _norm(basis):
                refused.append((eid, "component share has no verbatim basis"))
                continue
        if _norm(basis):
            inputs.include([source_pdf(corpus, r["source_id"])])
        why = verify_basis(
            r["source_id"],
            p.get("component_share_page"),
            basis,
            corpus=corpus,
        )
        if why:
            refused.append((r["evidence_id"], why))
            continue
        ctx = json_field(r, "context")
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
    if applied:
        write_table(ev, cols, rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument(
        "payload", type=Path, help="JSON input file; use a path without symlinks"
    )
    ap.add_argument("--root", type=Path, default=ROOT, help="Selected data root")
    ap.add_argument("--corpus-dir", type=Path, help="Selected PDF directory")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    root = a.root.resolve()
    ev = root / EV.relative_to(ROOT)
    corpus = (
        a.corpus_dir.resolve()
        if a.corpus_dir is not None
        else root / CORPUS.relative_to(ROOT)
    )
    inputs = ReviewInputs([a.payload])
    edit_records(
        [ev],
        lambda files: annotate(files[ev], a.payload, corpus, inputs),
        inputs=inputs,
        dry_run=a.dry_run,
    )
    if not a.dry_run:
        print(
            f"now: {rebuild_command(root, corpus if a.corpus_dir is not None else None)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
