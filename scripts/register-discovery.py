#!/usr/bin/env python3
"""Register the output of a synthesis-first discovery round (search_protocol.md).

Takes the discovery agents' candidate files (staging, gitignored) and performs the
orchestrator-owned registration steps so none of them is ever hand-claimed:

    * acquisition queue rows (``pipeline/acquisition_queue.csv``, status ``pending``) with the
      discovery tags carried in ``note`` and the agroforestry/WH *family* ids validated against
      ``FAM`` (sub-practice ids are mapped to their family; unknown tags are dropped + reported)
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
``process`` (updated_lit | grey | stock | tool), ``tables`` (``T3`` | ``T6`` | ``T3|T6``),
``families``, ``hazards``, ``t6_targets``, ``method_subtype``, ``proposed_benchmark_tier``,
``tier_rationale``, ``study_scope``, ``income_groups_covered``, ``language``, ``report_number_or_handle``,
``relevance_note``.
"""

from __future__ import annotations

import argparse
import csv
import json
import io
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from nbs_ruralscan.schema_tools import ledger, search_log
from nbs_ruralscan.schema_tools.verify_metadata import _title_of
from nbs_ruralscan.ingest.integrity import atomic_write, validate_source_id

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "pipeline" / "acquisition_queue.csv"
SRC = ROOT / "schema" / "registers" / "SRC_source_register.csv"
FAM = ROOT / "schema" / "registers" / "FAM_family_registry.csv"
LOGS = ROOT / "methodology" / "discovery_logs"
STEPS = "frame · source_type · relevance · credibility_six_axis · saturation_stop"
ROUTE_OA = "OA — browser/repository download (no institutional access needed)"


def _rd(p: Path) -> list[dict[str, str]]:
    with p.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _wr(p: Path, rows: list[dict[str, Any]], cols: list[str]) -> None:
    buffer = io.StringIO(newline="")
    w = csv.DictWriter(
        buffer, fieldnames=cols, lineterminator="\n", extrasaction="ignore"
    )
    w.writeheader()
    w.writerows(rows)
    atomic_write(p, buffer.getvalue().encode("utf-8"))


def _load_candidates(p: Path) -> list[dict[str, Any]]:
    d = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(d, dict):
        d = d.get("candidates", d.get("items"))
    if not isinstance(d, list) or any(not isinstance(x, dict) for x in d):
        raise ValueError(f"{p}: expected a candidate list, not an empty fallback")
    return d


def _norm_title(t: str) -> str:
    return re.sub(r"[^\w]+", " ", (t or "").casefold(), flags=re.UNICODE).strip()


def _sections(report: str, pattern: str, stop: str = r"^## |^### ") -> str:
    """Concatenate every report section whose heading matches ``pattern`` (verbatim queries)."""
    out: list[str] = []
    for m in re.finditer(pattern, report, flags=re.M | re.I):
        rest = report[m.end() :]
        n = re.search(stop, rest, flags=re.M)
        out.append((rest[: n.start()] if n else rest).strip())
    return "\n\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("nbs_id")
    ap.add_argument("--date", required=True)
    ap.add_argument(
        "--ruleset",
        required=True,
        help="Actual ruleset used for this search; never inferred",
    )
    ap.add_argument("--candidates", nargs="+", required=True, metavar="LANE=PATH")
    ap.add_argument("--reports", nargs="+", default=[], metavar="LANE=PATH")
    ap.add_argument("--log-names", nargs="+", default=[], metavar="LANE=NAME.md")
    ap.add_argument("--ledger", nargs="+", default=[], metavar="PROCESS=STATUS")
    ap.add_argument("--assigned", default="Namita-J")
    ap.add_argument("--run-prefix", default="")
    args = ap.parse_args(argv)

    def kv(items):
        result = {}
        for item in items:
            key, separator, value = item.partition("=")
            if not separator or not key or not value or key in result:
                ap.error(f"invalid or duplicate keyed argument: {item!r}")
            result[key] = value
        return result

    cand_files, reports, log_names = (
        kv(args.candidates),
        kv(args.reports),
        kv(args.log_names),
    )
    ledger_status = kv(args.ledger)
    run_prefix = (
        args.run_prefix or f"{args.nbs_id.split('_')[0]}_synthesis_first_{args.date}"
    )

    # Validate the entire batch and read reports before the first write.
    candidates = {
        lane: _load_candidates(Path(path)) for lane, path in cand_files.items()
    }
    report_text = {
        lane: Path(path).read_text(encoding="utf-8") for lane, path in reports.items()
    }
    if set(reports) != set(cand_files) or set(log_names) != set(cand_files):
        ap.error("candidates, reports and log-names must name exactly the same lanes")
    if len(set(log_names.values())) != len(log_names):
        ap.error("each lane needs a distinct tracked log filename")
    for lane, xs in candidates.items():
        if not xs:
            ap.error(
                f"{lane}: empty candidate lane; record the zero-yield search explicitly with search_log.log_search (table/process required)"
            )
        if lane not in report_text or lane not in log_names:
            ap.error(
                f"{lane}: --reports and --log-names required for reproducible searches"
            )
        if Path(log_names[lane]).name != log_names[lane] or not log_names[
            lane
        ].endswith(".md"):
            ap.error(f"{lane}: log name must be a Markdown filename")
        if not _sections(
            report_text[lane], r"^#{2,3} .*(verbatim|queries|channel \d).*$"
        ):
            ap.error(f"{lane}: report needs a verbatim query section")
        if len({x.get("candidate_id") for x in xs}) != len(xs):
            ap.error(f"{lane}: duplicate candidate IDs within lane")
        for x in xs:
            validate_source_id(x.get("candidate_id", ""))
            if not str(x.get("citation") or "").strip():
                ap.error(f"{lane}: candidate citation missing")
            if (
                x.get("process") or ("grey" if lane == "grey" else "updated_lit")
            ) not in search_log.CATEGORIES:
                ap.error(f"{lane}: unknown discovery process")
            if not set((x.get("tables") or "T3|T6").split("|")) <= set(
                search_log.TABLES
            ):
                ap.error(f"{lane}: unsupported table tag")
    if not set(ledger_status) <= set(search_log.CATEGORIES) or any(
        v not in {"in_progress", "done"} for v in ledger_status.values()
    ):
        ap.error("--ledger requires known processes and in_progress/done status")
    searched_processes = {
        x.get("process") or ("grey" if lane == "grey" else "updated_lit")
        for lane, xs in candidates.items()
        for x in xs
    }
    if not set(ledger_status) <= searched_processes:
        ap.error("--ledger cannot claim a process absent from this batch")
    fam_rows = [r for r in _rd(FAM) if r["nbs_id"] == args.nbs_id]
    if not fam_rows:
        ap.error(f"unknown NbS {args.nbs_id!r}; no registered suitability families")
    fams = {r["suitability_family_id"] for r in fam_rows}
    sub2fam = {r["subpractice_id"]: r["suitability_family_id"] for r in fam_rows}

    def famlist(xs: Any) -> tuple[list[str], list[str]]:
        out, bad = [], []
        for f in xs or []:
            g = f if f in fams else sub2fam.get(f, "")
            if g and g not in out:
                out.append(g)
            elif not g:
                bad.append(f)
        return out, bad

    for lane, xs in candidates.items():
        for x in xs:
            if not isinstance(x.get("families", []), list):
                ap.error(f"{lane}: families must be a list")
            _, bad = famlist(x.get("families"))
            if bad:
                ap.error(
                    f"{lane}: unknown/wrong-NbS family tags {bad}; resolve before registration"
                )
    # Search date must be valid before writing the queue.
    from datetime import datetime

    datetime.strptime(args.date, "%Y-%m-%d")
    tracked_reports = {}
    for lane, txt in report_text.items():
        first = txt.index("\n") if "\n" in txt else len(txt)
        hdr = (
            f"\n> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). "
            f"Run `{run_prefix}_{lane}`, ruleset **{args.ruleset}**, synthesis-first rule (Pete 2026-10-01). "
            f"Registered by `scripts/register-discovery.py` on {args.date}: candidates → `pipeline/acquisition_queue.csv` (status `pending`), "
            f"SRCH rows `{run_prefix}_{lane}`, ledger per `--ledger`.\n\n"
        )
        tracked_reports[lane] = txt[: first + 1] + hdr + txt[first + 1 :]
        destination = LOGS / log_names[lane]
        if (
            destination.exists()
            and destination.read_text(encoding="utf-8") != tracked_reports[lane]
        ):
            ap.error(
                f"tracked discovery log differs: {destination}; use a new run/log name to preserve search history"
            )
    q = _rd(QUEUE)
    qcols = list(q[0].keys())
    sources = _rd(SRC)
    # A known identity is not necessarily an already-covered NbS/table. Dropping
    # cross-scope candidates would lose future extraction work while SRCH still
    # records their inclusion. Reuse requires an explicit canonical-source route.
    seen_sources = q + sources
    for lane, xs in candidates.items():
        for candidate in xs:
            candidate_doi = (candidate.get("doi") or "").strip().casefold()
            candidate_title = _norm_title(candidate["citation"])
            matches = [
                row
                for row in seen_sources
                if (
                    candidate_doi
                    and candidate_doi == (row.get("doi") or "").strip().casefold()
                )
                or candidate_title == _norm_title(row.get("citation", ""))
            ]
            if not matches:
                family_ids, _ = famlist(candidate.get("families"))
                seen_sources.append(
                    {
                        "source_id": candidate["candidate_id"],
                        "citation": candidate["citation"],
                        "doi": candidate_doi,
                        "nbs_id": args.nbs_id,
                        "tables": candidate.get("tables") or "T3|T6",
                        "family": "|".join(family_ids),
                    }
                )
                continue
            if candidate_doi and any(
                candidate_doi == (row.get("doi") or "").strip().casefold()
                and _norm_title(_title_of(candidate["citation"]))
                != _norm_title(_title_of(row.get("citation", "")))
                for row in matches
            ):
                ap.error(
                    f"{lane}: same DOI has different citation titles; verify identity before deduplication"
                )
            declared_scopes = {
                nbs.strip()
                for row in matches
                for nbs in (row.get("nbs_ids") or row.get("nbs_id") or "").split("|")
                if nbs
            }
            requested_tables = set((candidate.get("tables") or "T3|T6").split("|"))
            existing_tables = {
                table
                for row in matches
                if args.nbs_id
                in {token.strip() for token in (row.get("nbs_id") or "").split("|")}
                for table in (row.get("tables") or "").split("|")
                if table
            }
            requested_families, _ = famlist(candidate.get("families"))
            existing_families = {
                family
                for row in matches
                if args.nbs_id
                in {token.strip() for token in (row.get("nbs_id") or "").split("|")}
                for family in (row.get("family") or "").split("|")
                if family
            }
            if (
                args.nbs_id not in declared_scopes
                or not requested_tables <= existing_tables
                or not set(requested_families) <= existing_families
            ):
                ids = sorted({row["source_id"] for row in matches})
                ap.error(
                    f"{lane}: known source {ids} needs new NbS/table reuse tracking for "
                    f"{args.nbs_id} {sorted(requested_tables)} families={requested_families}; "
                    "candidate retained, not discarded as duplicate"
                )
    known_doi = {(r["doi"] or "").lower() for r in q} | {
        (r.get("doi") or "").lower() for r in _rd(SRC)
    }
    known_title = {_norm_title(r["citation"]) for r in q} | {
        _norm_title(r["citation"]) for r in _rd(SRC)
    }
    ids = {r["source_id"] for r in q} | {r["source_id"] for r in _rd(SRC)}

    added: list[tuple[str, str]] = []
    dropped: list[tuple[str, str, str]] = []
    bad_fams: Counter = Counter()
    per_lane_proc: dict[str, Counter] = defaultdict(Counter)
    for lane, path in cand_files.items():
        for x in candidates[lane]:
            sid = x["candidate_id"]
            doi = (x.get("doi") or "").strip()
            if doi and doi.lower() in known_doi:
                dropped.append((lane, sid, "duplicate DOI"))
                continue
            if _norm_title(x.get("citation", "")) in known_title:
                dropped.append((lane, sid, "duplicate title"))
                continue
            if sid in ids:
                ap.error(
                    f"{lane}: source_id collision for {sid}; assign a distinct identity rather than discard the candidate"
                )
            process = x.get("process") or ("grey" if lane == "grey" else "updated_lit")
            per_lane_proc[lane][process] += 1
            fam, bad = famlist(x.get("families"))
            for b in bad:
                bad_fams[b] += 1
            oa = str(x.get("oa_status") or "")
            rg = oa.startswith("rg_flag")
            blocker = ""
            if rg:
                blocker = "OA (websearch:researchgate/unverified) — HUMAN CHECK"
            elif oa.startswith("paywalled"):
                blocker = "OA recovery needed — candidate labelled paywalled; verify Unpaywall AND web-search evidence before institutional referral"
            elif "archived" in oa:
                blocker = (
                    "publisher link dead — archived copy; HUMAN: mirror to SharePoint"
                )
            grey = process in ("grey", "stock", "tool")
            tags = []
            for k in (
                "method_subtype",
                "language",
                "study_scope",
                "income_groups_covered",
                "claim_scope_risk",
                "evaluation_design",
                "report_number_or_handle",
            ):
                if x.get(k):
                    tags.append(f"{k}={x[k]}")
            for k in ("hazards", "t6_targets"):
                if x.get(k):
                    tags.append(
                        f"{k}={','.join(x[k]) if isinstance(x[k], list) else x[k]}"
                    )
            tags.append(f"families={'|'.join(fam)}")
            hes = x.get("has_effect_sizes", x.get("has_quantified_outcomes"))
            tags.append(f"has_effect_sizes={hes}")
            tags.append(
                f"proposed_tier={x.get('proposed_benchmark_tier')} ({str(x.get('tier_rationale') or '')[:110]})"
            )
            note = (
                f"{run_prefix} (ruleset {args.ruleset}, synthesis-first). process={process}; "
                + "; ".join(tags)
                + "; "
                + str(x.get("relevance_note") or "")[:220]
            )
            q.append(
                {c: "" for c in qcols}
                | dict(
                    source_id=sid,
                    nbs_id=args.nbs_id,
                    family="|".join(fam),
                    tables=x.get("tables") or "T3|T6",
                    citation=x["citation"],
                    doi=doi,
                    url=x.get("oa_url") or x.get("url") or "",
                    access_status="oa" if oa in {"oa", "open_access"} else "unknown",
                    blocker=blocker,
                    access_route=("web (publisher domain)" if grey else ROUTE_OA),
                    target_library_path="",
                    status="pending",
                    assigned=args.assigned,
                    date_added=args.date,
                    note=note,
                    doi_verified="",
                    duplicate_of="",
                    title_verified="",
                )
            )
            ids.add(sid)
            if doi:
                known_doi.add(doi.lower())
            known_title.add(_norm_title(x["citation"]))
            added.append((lane, sid))
    _wr(QUEUE, q, qcols)
    print(
        f"queue +{len(added)} (dropped {len(dropped)}: {Counter(d for _, _, d in dropped)})"
    )
    if bad_fams:
        print(f"  family tags not in FAM (dropped from `family`): {dict(bad_fams)}")

    # SRCH rows: one per (table × process) per lane, verbatim queries from the lane's report
    tables: set[str] = set()
    for lane, path in cand_files.items():
        for x in candidates[lane]:
            tables |= set((x.get("tables") or "T3|T6").split("|"))
    table_list = sorted(tables)
    for lane, path in cand_files.items():
        cands = candidates[lane]
        if not cands:
            continue
        report = (
            Path(reports[lane]).read_text(encoding="utf-8") if lane in reports else ""
        )
        terms = (
            _sections(report, r"^#{2,3} .*(verbatim|queries|channel \d).*$")
            or f"(see {log_names.get(lane, 'discovery log')})"
        )
        procs = Counter(
            x.get("process") or ("grey" if lane == "grey" else "updated_lit")
            for x in cands
        )
        for process, n in procs.items():
            for table in table_list:
                n_tbl = sum(
                    1
                    for x in cands
                    if (
                        x.get("process")
                        or ("grey" if lane == "grey" else "updated_lit")
                    )
                    == process
                    and table in (x.get("tables") or "T3|T6").split("|")
                )
                if n_tbl == 0:
                    continue
                search_log.log_search(
                    nbs=args.nbs_id,
                    search_date=args.date,
                    table=table,
                    category=process,
                    family="",
                    ruleset_version=args.ruleset,
                    run_id=f"{run_prefix}_{lane}",
                    searched_by="discovery-agent (opus) / orchestrator",
                    screening_steps=STEPS,
                    search_terms=f"[{lane} lane, {process}] " + terms,
                    inclusion_criteria=(
                        "SYNTHESIS-FIRST (Pete 2026-10-01): meta-analyses / systematic reviews / maps / EGMs / reviews first, then MEL & impact-assessment grey literature; "
                        "primaries only where a hazard / target / family has no synthesis; PADs excluded; datasets used as seed lists only. "
                        f"NbS {args.nbs_id}, table {table}; practice must be explicit (PICOS)."
                    ),
                    limits="retrieve<=200/query; screen<=80; include<=30 per lane; saturation stop",
                    n_retrieved="see discovery log",
                    n_screened="see discovery log",
                    n_included=str(n_tbl),
                    discovery_log_ref=f"methodology/discovery_logs/{log_names.get(lane, lane + '.md')}",
                    note=f"{len(cands)} candidates included by the {lane} lane before queue deduplication; per-table count uses exact table tags. Registration date is distinct from search date.",
                )
                print(f"  SRCH {table} {process:12s} ({lane}) n_included={n_tbl}")
    # ledger
    for process, status in ledger_status.items():
        process_tables = {
            table
            for lane, xs in candidates.items()
            for x in xs
            if (x.get("process") or ("grey" if lane == "grey" else "updated_lit"))
            == process
            for table in (x.get("tables") or "T3|T6").split("|")
        }
        for table in sorted(process_tables):
            for stage in ("searched", "screened"):
                ledger.mark(
                    args.nbs_id,
                    table,
                    process,
                    stage,
                    status,
                    family="",
                    run_id=run_prefix,
                    by="orchestrator",
                    note=f"synthesis-first round {args.date}; see SRCH {run_prefix}_* rows + discovery logs",
                )
    print(f"  ledger: {ledger_status} on {table_list}")
    # tracked discovery logs
    LOGS.mkdir(exist_ok=True)
    for lane, txt in tracked_reports.items():
        name = log_names[lane]
        atomic_write(LOGS / name, txt.encode("utf-8"))
        print(f"  log → methodology/discovery_logs/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
