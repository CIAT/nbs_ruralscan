#!/usr/bin/env python3
"""Backfill SRC.study_country for stocktake sources from the stocktake registers.

The pre-repo stocktake batch was registered into SRC_source_register without copying
geography, so ~22 sources show no location in the QA card. The geography was recorded
all along in the stocktake benchmark CSVs (peer_reviewed -> Geographic_Scope, grey_lit ->
Geography). This copies a concise study_country back into SRC for any row that has none.

Traceable, idempotent, non-destructive:
- only fills rows whose study_country / region / aez are ALL empty (never overwrites);
- matches a stocktake row by DOI first, then by exact (case-folded) title;
- derives a short country string from the verbose Geographic_Scope.

Run from the repo root:  python3 scripts/backfill_stocktake_geo.py
Then regenerate:         python3 src/nbs_ruralscan/schema_tools/generate.py schema
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.schema_tools.record_publication import edit_records  # noqa: E402
from nbs_ruralscan.schema_tools.review_inputs import ReviewInputs  # noqa: E402
from nbs_ruralscan.schema_tools.specialist_records import read_table, write_table  # noqa: E402

_ABBR = {
    "democratic republic of congo": "DR Congo",
    "united kingdom": "UK",
    "united states": "United States",
    "the netherlands": "Netherlands",
}


def _norm_doi(d: str) -> str:
    return (
        (d or "")
        .strip()
        .lower()
        .replace("https://doi.org/", "")
        .replace("http://doi.org/", "")
        .rstrip("/")
    )


def _norm_title(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").strip().lower())


def _abbr(country: str) -> str:
    c = country.strip()
    return _ABBR.get(c.lower(), c)


def concise_country(scope: str) -> str:
    """Derive a short study_country from a verbose Geographic_Scope string."""
    scope = (scope or "").strip()
    if not scope:
        return ""
    segments = [s.strip() for s in re.split(r"[|;]", scope) if s.strip()]

    # 1) Multi-country: take the listed countries (drop a leading region label).
    m = re.search(r"multi-country:\s*([^|]+)", scope, re.I)
    if m:
        parts = [p.strip() for p in m.group(1).split(";") if p.strip()]
        if len(parts) > 1 and re.search(
            r"asia|africa|america|europe|region|sahel", parts[0], re.I
        ):
            parts = parts[1:]
        parts = [_abbr(p) for p in parts]
        if len(parts) <= 3:
            return ", ".join(parts)
        return ", ".join(parts[:2]) + f" +{len(parts) - 2}"

    nationals: list[str] = []
    continentals: list[str] = []
    for seg in segments:
        low = seg.lower()
        if low.startswith("national:"):
            nationals.append(_abbr(seg.split(":", 1)[1]))
        elif low.startswith("continental:"):
            continentals.append(seg.split(":", 1)[1].strip())

    nationals = [n for n in dict.fromkeys(nationals) if n]
    if nationals:
        if len(nationals) == 1:
            return nationals[0]
        if len(nationals) <= 3:
            return ", ".join(nationals)
        # many countries -> report the continental scope if we have it
        if continentals:
            return f"{continentals[0]} (multi)"
        return ", ".join(nationals[:2]) + f" +{len(nationals) - 2}"
    if continentals:
        return continentals[0]
    if re.search(r"global", scope, re.I):
        return "Global"

    # Fallback (no National/Multi/Continental token): the stocktake scope lists the country
    # LAST, so take the final segment's last comma-part (e.g. "…; India" -> India;
    # "Sub-national: US Midwest" -> United States).
    last_seg = segments[-1] if segments else ""
    val = last_seg.split(":", 1)[-1]
    toks = [t.strip() for t in val.split(",") if t.strip()]
    cand = toks[-1] if toks else val.strip()
    if re.search(r"\bus\b|united states|midwest", cand, re.I):
        return "United States"
    return _abbr(cand)


def _load_geo_lookup(peer: Path, grey: Path) -> tuple[dict[str, str], dict[str, str]]:
    """(by_doi, by_title) -> raw Geographic_Scope / Geography string."""
    by_doi: dict[str, str] = {}
    by_title: dict[str, str] = {}
    if peer.exists():
        _, peer_rows = read_table(
            peer, ("Geographic_Scope", "doi_extracted", "oa_title")
        )
        for r in peer_rows:
            scope = (r.get("Geographic_Scope") or "").strip()
            if not scope:
                continue
            d = _norm_doi(r.get("doi_extracted", ""))
            if d:
                by_doi.setdefault(d, scope)
            t = _norm_title(r.get("oa_title", ""))
            if t:
                by_title.setdefault(t, scope)
    if grey.exists():
        _, grey_rows = read_table(grey, ("Geography", "Source_title"))
        for r in grey_rows:
            scope = (r.get("Geography") or "").strip()
            if not scope:
                continue
            t = _norm_title(r.get("Source_title", ""))
            if t:
                by_title.setdefault(t, scope)
    return by_doi, by_title


def _fill(src: Path, peer: Path, grey: Path) -> tuple[list[tuple[str, str]], list[str]]:
    by_doi, by_title = _load_geo_lookup(peer, grey)
    cols, rows = read_table(
        src, ("source_id", "study_country", "region", "aez", "doi", "citation")
    )
    ids = [r["source_id"] for r in rows]
    if len(ids) != len(set(ids)) or any(not sid.strip() for sid in ids):
        raise ValueError("Missing or duplicate source_id in source register")
    filled = []
    skipped_no_match: list[str] = []

    for r in rows:
        has_geo = any(
            (r.get(f) or "").strip() for f in ("study_country", "region", "aez")
        )
        if has_geo:
            continue
        scope = by_doi.get(_norm_doi(r.get("doi", "")))
        if not scope:
            scope = by_title.get(_norm_title(r.get("citation", "")))
        if not scope:
            skipped_no_match.append(r.get("source_id", ""))
            continue
        country = concise_country(scope)
        if country:
            r["study_country"] = country
            filled.append((r["source_id"], country))
    if filled:
        write_table(src, cols, rows)
    return filled, skipped_no_match


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0] if __doc__ else None
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Checkout containing the source register and stocktake",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview matching sources and countries"
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    src = root / "schema/registers/SRC_source_register.csv"
    if not src.exists():
        print(f"SRC register not found: {src}")
        return 1
    stocktake = root / "reference/stocktake"
    peer = stocktake / "peer_reviewed_benchmarked.csv"
    grey = stocktake / "grey_lit_benchmarked.csv"
    filled, skipped_no_match = edit_records(
        [src],
        lambda private: _fill(private[src], peer, grey),
        inputs=ReviewInputs([peer, grey]),
        dry_run=args.dry_run,
    )
    for sid, country in filled:
        print(f"  {sid:28} -> {country}")
    action = "would fill" if args.dry_run else "filled"
    print(f"\n{action} study_country on {len(filled)} source(s)")
    if skipped_no_match:
        print(f"no stocktake match (left blank): {len(skipped_no_match)}")
        for sid in skipped_no_match:
            print(f"  - {sid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
