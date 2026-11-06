#!/usr/bin/env python3
"""Promote acquired acquisition-queue rows into the Source Register (SRC).

    python3 scripts/promote-queue-to-src.py --run-id <id> --nbs <nbs_id> \
        --sources <ids.txt | lane.json ...> --meta <overrides.json> [--extractor "..."] [--dry-run]

Mechanical fields come from the queue row + the cached artefact (citation, verified DOI, url,
library path, sha1, access, process → source_category/source_kind, note tags → method_type /
study_country / income group). Judgement fields (benchmark_tier, venue_type, region, overrides
of country / income group) come from `--meta` = {source_id: {...}} authored by the orchestrator
from the six-axis rubric (T4 method §3). Rows already in SRC are skipped. Queue `status` is NOT
touched here — the orchestrator marks `extracted` only for sources that produced EV rows.
"""

from __future__ import annotations

from pathlib import Path

from nbs_ruralscan.schema_tools import source_promotion as promotion

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "pipeline/acquisition_queue.csv"
SRC = ROOT / "schema/registers/SRC_source_register.csv"
CORPUS = ROOT / ".cache/corpus"
_ids = promotion._ids


def build_row(q: dict, meta: dict, cols: list[str], a) -> dict:
    """Retain the importable row builder with this script's corpus default."""
    return promotion.build_row(q, meta, cols, a, corpus=CORPUS)


def main(argv: list[str] | None = None) -> int:
    return promotion.main(
        argv, paths=promotion.SourcePromotionPaths(QUEUE, SRC, CORPUS)
    )


if __name__ == "__main__":
    raise SystemExit(main())
