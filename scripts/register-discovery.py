#!/usr/bin/env python3
"""Register the output of a bounded discovery round (search_protocol.md).

Takes the discovery agents' candidate files (staging, gitignored) and performs the
orchestrator-owned registration steps so none of them is ever hand-claimed:

    * acquisition queue rows (``pipeline/acquisition_queue.csv``, status ``pending``) with the
      discovery tags carried in ``note`` and the *family* ids validated against
      ``FAM`` (sub-practice ids are mapped to their family; unknown tags are rejected)
    * ``SRCH`` protocol rows per (table × process) with the VERBATIM query sections lifted from
      each agent's report, PRISMA counts and the discovery-log reference
    * progress-ledger stamps (``searched`` / ``screened``) at the status you pass per process
    * a tracked copy of each agent report under ``methodology/discovery_logs/``

Then run ``verify_metadata.py verify`` (DOI round-trip stamps) and ``acquire-queue.py``.

Usage::

    python3 scripts/register-discovery.py water_harvesting_conservation \\
        --date 2026-10-05 --ruleset v1.6.0 \\
        --candidates lit=pipeline/staging/discovery/wh_T3T6_lit_candidates.json \\
                     ml=pipeline/staging/discovery/wh_multilingual_candidates.json \\
                     grey=pipeline/staging/discovery/wh_grey_mel_candidates.json \\
        --reports lit=...report.md ml=...report.md grey=...report.md \\
        --log-names lit=wh_T3T6_synthesis_2026-10.md ml=... grey=... \\
        --ledger updated_lit=done grey=in_progress stock=done

Candidate JSON may be a list or ``{"candidates": [...]}``. Each candidate needs at least
``candidate_id``, ``citation``; optional ``doi``, ``url``/``oa_url``, ``oa_status``,
``process`` (updated_lit | grey | stock | tool), ``tables`` (``T4`` | ``T3`` | ``T6`` | ``T3|T6``),
``families``, ``hazards``, ``t6_targets``, ``method_subtype``, ``proposed_benchmark_tier``,
``tier_rationale``, ``study_scope``, ``income_groups_covered``, ``language``, ``report_number_or_handle``,
``relevance_note``.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from nbs_ruralscan.schema_tools import discovery_registration as registration

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "pipeline/acquisition_queue.csv"
SRC = ROOT / "schema/registers/SRC_source_register.csv"
FAM = ROOT / "schema/registers/FAM_family_registry.csv"
LOGS = ROOT / "methodology/discovery_logs"
ledger, search_log = registration.ledger, registration.search_log
_load_candidates = registration._load_candidates
_norm_title = registration._norm_title
_sections = registration._sections
_title_of = registration._title_of


def main(argv: list[str] | None = None) -> int:
    paths = replace(
        registration.DiscoveryRegistrationPaths.from_root(ROOT),
        queue=QUEUE,
        sources=SRC,
        families=FAM,
        logs=LOGS,
    )
    return registration.main(argv, paths=paths)


if __name__ == "__main__":
    raise SystemExit(main())
