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
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from nbs_ruralscan.schema_tools import ledger, search_log

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
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f, fieldnames=cols, lineterminator="\n", extrasaction="ignore"
        )
        w.writeheader()
        w.writerows(rows)


def _load_candidates(p: Path) -> list[dict[str, Any]]:
    d = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(d, dict):
        d = d.get("candidates") or d.get("items") or []
    return list(d)


def _norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()[:70]


def _sections(
    report: str, pattern: str, stop: str = r"^## |^### ", maxlen: int = 7000
) -> str:
    """Concatenate every report section whose heading matches ``pattern`` (verbatim queries)."""
    out: list[str] = []
    for m in re.finditer(pattern, report, flags=re.M | re.I):
        rest = report[m.end() :]
        n = re.search(stop, rest, flags=re.M)
        out.append(re.sub(r"[ \t]+", " ", rest[: n.start()] if n else rest).strip())
    return (" || ".join(out))[:maxlen]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("nbs_id")
    ap.add_argument("--date", required=True)
    ap.add_argument("--ruleset", default="v1.6.0")
    ap.add_argument("--candidates", nargs="+", required=True, metavar="LANE=PATH")
    ap.add_argument("--reports", nargs="+", default=[], metavar="LANE=PATH")
    ap.add_argument("--log-names", nargs="+", default=[], metavar="LANE=NAME.md")
    ap.add_argument("--ledger", nargs="+", default=[], metavar="PROCESS=STATUS")
    ap.add_argument("--assigned", default="Namita-J")
    ap.add_argument("--run-prefix", default="")
    args = ap.parse_args(argv)
    kv = lambda items: dict(x.split("=", 1) for x in items)  # noqa: E731
    cand_files, reports, log_names = (
        kv(args.candidates),
        kv(args.reports),
        kv(args.log_names),
    )
    ledger_status = kv(args.ledger)
    run_prefix = (
        args.run_prefix or f"{args.nbs_id.split('_')[0]}_synthesis_first_{args.date}"
    )

    fam_rows = _rd(FAM)
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

    q = _rd(QUEUE)
    qcols = list(q[0].keys())
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
        for x in _load_candidates(Path(path)):
            sid = x["candidate_id"]
            doi = (x.get("doi") or "").strip()
            if doi and doi.lower() in known_doi:
                dropped.append((lane, sid, "duplicate DOI"))
                continue
            if _norm_title(x.get("citation", "")) in known_title:
                dropped.append((lane, sid, "duplicate title"))
                continue
            if sid in ids:
                dropped.append((lane, sid, "source_id collision"))
                continue
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
                blocker = "paywalled (verified: Unpaywall + web search found no copy) → institutional"
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
                    access_status="oa"
                    if not oa.startswith("paywalled")
                    else "paywalled",
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
    added_ids = {s for _, s in added}
    tables: set[str] = set()
    for lane, path in cand_files.items():
        for x in _load_candidates(Path(path)):
            if x["candidate_id"] in added_ids:
                tables |= set((x.get("tables") or "T3|T6").split("|"))
    table_list = sorted(tables)
    for lane, path in cand_files.items():
        cands = [
            x
            for x in _load_candidates(Path(path))
            if any(s == x["candidate_id"] for ln, s in added if ln == lane)
        ]
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
                    and table in (x.get("table_list") or "T3|T6")
                )
                if n_tbl == 0:
                    continue
                search_log.log_search(
                    nbs=args.nbs_id,
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
                    note=f"{len(cands)} candidates queued from the {lane} lane; per-table count counts candidates tagged for {table}.",
                )
                print(f"  SRCH {table} {process:12s} ({lane}) n_included={n_tbl}")
    # ledger
    for process, status in ledger_status.items():
        for table in table_list:
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
    for lane, path in reports.items():
        name = log_names.get(lane)
        if not name:
            continue
        txt = Path(path).read_text(encoding="utf-8")
        first = txt.index("\n") if "\n" in txt else len(txt)
        hdr = (
            f"\n> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). "
            f"Run `{run_prefix}_{lane}`, ruleset **{args.ruleset}**, synthesis-first rule (Pete 2026-10-01). "
            f"Registered by `scripts/register-discovery.py` on {args.date}: candidates → `pipeline/acquisition_queue.csv` (status `pending`), "
            f"SRCH rows `{run_prefix}_{lane}`, ledger per `--ledger`.\n\n"
        )
        (LOGS / name).write_text(
            txt[: first + 1] + hdr + txt[first + 1 :], encoding="utf-8"
        )
        print(f"  log → methodology/discovery_logs/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
