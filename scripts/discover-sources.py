#!/usr/bin/env python3
"""Run one discovery query against a bibliographic source and stage candidates.

    python3 scripts/discover-sources.py lens "<query>" --out pipeline/staging/discovery/<name>.json \\
        [--size 50] [--year-from 2015] [--process updated_lit] [--tables "T3|T6"] [--reviews]
    python3 scripts/discover-sources.py agris "<query>" [--lang fr] --out <template.json>
    python3 scripts/discover-sources.py review-terms

``lens`` needs ``LENS_TOKEN``. ``--reviews`` ANDs the protocol's systematic-review term block.
``agris`` writes a candidate TEMPLATE + the browser URL (AGRIS is manual: no scraping).
Staged files feed ``scripts/register-discovery.py`` unchanged. Writes only under
``pipeline/staging/``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.ingest import discovery_sources as ds  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    lens = sub.add_parser("lens")
    lens.add_argument("query")
    lens.add_argument("--out", required=True)
    lens.add_argument("--size", type=int, default=50)
    lens.add_argument("--year-from", type=int, default=None)
    lens.add_argument("--process", default="updated_lit")
    lens.add_argument("--tables", default="T3|T6")
    lens.add_argument("--reviews", action="store_true")
    ag = sub.add_parser("agris")
    ag.add_argument("query")
    ag.add_argument("--lang", default="en")
    ag.add_argument("--tables", default="T3|T6")
    ag.add_argument("--out", required=True)
    sub.add_parser("review-terms")
    a = ap.parse_args(argv)
    if a.cmd == "review-terms":
        print(ds.review_type_block())
        return 0
    out = Path(a.out)
    if ROOT / "pipeline" / "staging" not in out.resolve().parents:
        print("refusing: --out must be under pipeline/staging/", file=sys.stderr)
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)
    if a.cmd == "lens":
        q = f"({a.query}) AND ({ds.review_type_block()})" if a.reviews else a.query
        cands = ds.lens_search(
            q, size=a.size, year_from=a.year_from, process=a.process, tables=a.tables
        )
        out.write_text(
            json.dumps(
                {"query": q, "source_db": "lens", "candidates": cands},
                ensure_ascii=False,
                indent=1,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"{len(cands)} candidate(s) → {out}")
        return 0
    tpl = ds.agris_candidate_template(a.query, lang=a.lang, tables=a.tables)
    out.write_text(
        json.dumps(
            {
                "query": a.query,
                "source_db": "agris",
                "search_url": tpl["_search_url"],
                "candidates": [tpl],
            },
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"AGRIS is manual. Open:\n  {tpl['_search_url']}\nscreen the list, fill one entry per record in {out}, then register."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
