"""Bounded discovery registration with explicit paths and staged publication."""

from __future__ import annotations

import argparse
import csv
import json
import io
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, fields, replace
from pathlib import Path
from typing import Any

from nbs_ruralscan.schema_tools import ledger, search_log
from nbs_ruralscan.schema_tools.verify_metadata import _title_of
from nbs_ruralscan.ingest.integrity import atomic_write, validate_source_id
from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths
from nbs_ruralscan.schema_tools.publication import staged_publish

STEPS = "frame · source_type · relevance · credibility_six_axis · saturation_stop"
ROUTE_OA = "OA — browser/repository download (no institutional access needed)"


@dataclass(frozen=True)
class DiscoveryRegistrationPaths:
    """Sources/families are read-only; other paths hold registration outputs."""

    queue: Path
    sources: Path
    families: Path
    searches: Path
    ledger: Path
    logs: Path

    def __post_init__(self):
        for field in fields(self):
            object.__setattr__(
                self, field.name, Path(os.path.abspath(getattr(self, field.name)))
            )

    @classmethod
    def from_root(cls, root: Path) -> DiscoveryRegistrationPaths:
        root = Path(root).resolve()
        return cls(
            root / "pipeline/acquisition_queue.csv",
            root / "schema/registers/SRC_source_register.csv",
            root / "schema/registers/FAM_family_registry.csv",
            root / "schema/registers/SRCH_search_register.csv",
            root / "pipeline/progress_ledger.csv",
            root / "methodology/discovery_logs",
        )


def _kv(ap: argparse.ArgumentParser, items: list[str]) -> dict[str, str]:
    result = {}
    for item in items:
        key, separator, value = item.partition("=")
        if not separator or not key or not value or key in result:
            ap.error(f"invalid or duplicate keyed argument: {item!r}")
        result[key] = value
    return result


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


def _parser() -> argparse.ArgumentParser:
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
    ap.add_argument(
        "--family", default="", help="Actual targeted family; blank is generic"
    )
    ap.add_argument(
        "--reuse-log",
        help="New JSON filename under discovery_logs for explicit canonical-source reuse tasks",
    )
    ap.add_argument("--searched-by", default="discovery-agent / orchestrator")
    ap.add_argument(
        "--protocols",
        nargs="+",
        default=[],
        metavar="LANE=PATH",
        help="Actual per-table/process protocol JSON, required for targeted searches",
    )
    ap.add_argument(
        "--root",
        type=Path,
        help="Data root to validate and update (default: this checkout)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Render and validate the complete batch without publishing",
    )
    return ap


def _apply(
    args: argparse.Namespace,
    ap: argparse.ArgumentParser,
    paths: DiscoveryRegistrationPaths,
) -> list[str]:
    """Existing registration rules, operating only on selected/staged paths."""
    messages: list[str] = []

    def report(message: str) -> None:
        messages.append(message)

    cand_files, reports, log_names = (
        _kv(ap, args.candidates),
        _kv(ap, args.reports),
        _kv(ap, args.log_names),
    )
    ledger_status = _kv(ap, args.ledger)
    protocol_files = _kv(ap, args.protocols)
    if args.family and not protocol_files:
        ap.error("targeted family searches require --protocols")
    if protocol_files and set(protocol_files) != set(cand_files):
        ap.error("protocols must name exactly the candidate lanes")
    protocols: dict[tuple[str, str, str], dict[str, Any]] = {}
    for lane, path in protocol_files.items():
        items = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(items, list) or not items:
            ap.error(f"{lane}: protocols must be a nonempty list")
        for item in items:
            if not isinstance(item, dict):
                ap.error(f"{lane}: protocol must be an object")
            key = (item.get("table"), item.get("category"))
            if key[0] not in search_log.TABLES or key[1] not in search_log.CATEGORIES:
                ap.error(f"{lane}: invalid protocol table/category")
            if (lane, *key) in protocols:
                ap.error(f"{lane}: duplicate protocol table/category")
            for field in ("search_terms", "inclusion_criteria", "limits"):
                if not isinstance(item.get(field), str) or not item[field].strip():
                    ap.error(f"{lane}: protocol requires {field}")
            for field in ("n_retrieved", "n_screened", "n_included"):
                value = item.get(field)
                if value is not None and (type(value) is not int or value < 0):
                    ap.error(f"{lane}: {field} must be a nonnegative integer or null")
            if item.get("n_included") is None:
                ap.error(f"{lane}: n_included must be known")
            counts = [item.get(k) for k in ("n_retrieved", "n_screened", "n_included")]
            known = [n for n in counts if n is not None]
            if known != sorted(known, reverse=True):
                ap.error(
                    f"{lane}: protocol counts must satisfy retrieved >= screened >= included"
                )
            protocols[(lane, *key)] = item
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
        if not xs and not protocol_files:
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
    for lane, xs in candidates.items():
        if not protocol_files:
            continue
        observed = Counter(
            (table, x.get("process") or ("grey" if lane == "grey" else "updated_lit"))
            for x in xs
            for table in (x.get("tables") or "T3|T6").split("|")
        )
        for key, count in observed.items():
            if (lane, *key) not in protocols:
                ap.error(f"{lane}: missing protocol for {key}")
        for (scope_lane, table, process), item in protocols.items():
            if scope_lane == lane and item["n_included"] != observed[(table, process)]:
                ap.error(
                    f"{lane}: protocol included count differs from candidate membership"
                )
    searched_processes = {
        x.get("process") or ("grey" if lane == "grey" else "updated_lit")
        for lane, xs in candidates.items()
        for x in xs
    }
    searched_processes |= {process for _, _, process in protocols}
    if not set(ledger_status) <= searched_processes:
        ap.error("--ledger cannot claim a process absent from this batch")
    fam_rows = [r for r in _rd(paths.families) if r["nbs_id"] == args.nbs_id]
    if not fam_rows:
        ap.error(f"unknown NbS {args.nbs_id!r}; no registered suitability families")
    fams = {r["suitability_family_id"] for r in fam_rows}
    if args.family and args.family not in fams:
        ap.error("--family is not registered for this NbS")
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
            valid, bad = famlist(x.get("families"))
            if args.family and args.family not in valid:
                ap.error(f"{lane}: candidate does not declare targeted family")
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
            f"Run `{run_prefix}_{lane}`, ruleset **{args.ruleset}**, actual family `{args.family or 'generic'}`. "
            f"Registered by `scripts/register-discovery.py` on {args.date}: candidates → `pipeline/acquisition_queue.csv` (status `pending`), "
            f"SRCH rows `{run_prefix}_{lane}`, ledger per `--ledger`.\n\n"
        )
        tracked_reports[lane] = txt[: first + 1] + hdr + txt[first + 1 :]
        destination = paths.logs / log_names[lane]
        if (
            destination.exists()
            and destination.read_text(encoding="utf-8") != tracked_reports[lane]
        ):
            ap.error(
                f"tracked discovery log differs: {destination}; use a new run/log name to preserve search history"
            )
    # Explicit protocols retain measured counts and targeted scope. Legacy callers keep
    # their report-based generic route; no family-targeted search may use that fallback.
    if not protocol_files:
        for lane, cands in candidates.items():
            terms = _sections(
                report_text[lane], r"^#{2,3} .*(verbatim|queries|channel \d).*$"
            )
            counts = Counter(
                (
                    table,
                    x.get("process") or ("grey" if lane == "grey" else "updated_lit"),
                )
                for x in cands
                for table in (x.get("tables") or "T3|T6").split("|")
            )
            for (table, process), count in counts.items():
                protocols[(lane, table, process)] = dict(
                    search_terms=terms,
                    inclusion_criteria="See tracked discovery report; practice must be explicit (PICOS).",
                    limits="See tracked discovery report",
                    n_retrieved=None,
                    n_screened=None,
                    n_included=count,
                )
    existing_searches = search_log.rows(paths.searches)
    for (lane, table, process), protocol in protocols.items():
        identity = dict(
            nbs_id=args.nbs_id,
            suitability_family_id=args.family,
            table=table,
            category=process,
            search_date=args.date,
            run_id=f"{run_prefix}_{lane}",
        )
        expected = dict(
            identity,
            ruleset_version=args.ruleset,
            searched_by=args.searched_by,
            screening_steps=STEPS,
            discovery_log_ref=f"methodology/discovery_logs/{log_names[lane]}",
        )
        for field in (
            "search_terms",
            "inclusion_criteria",
            "limits",
            "n_retrieved",
            "n_screened",
            "n_included",
        ):
            value = protocol[field]
            expected[field] = "" if value is None else str(value)
        for previous in existing_searches:
            if all(
                previous.get(k, "") == value for k, value in identity.items()
            ) and any(previous.get(k, "") != value for k, value in expected.items()):
                ap.error(
                    "existing search protocol differs; use a new run ID to preserve history"
                )
    with paths.queue.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        qcols = list(reader.fieldnames or [])
        q = list(reader)
    required_queue = {"source_id", "citation", "doi"}
    if not required_queue <= set(qcols) or len(qcols) != len(set(qcols)):
        ap.error(
            "queue needs unique column names including source_id, citation and doi"
        )
    sources = _rd(paths.sources)
    # A known identity is not necessarily an already-covered NbS/table. Dropping
    # cross-scope candidates would lose future extraction work while SRCH still
    # records their inclusion. Reuse requires an explicit canonical-source route.
    reuse_tasks = []
    if args.reuse_log and (
        Path(args.reuse_log).name != args.reuse_log
        or not args.reuse_log.endswith(".json")
    ):
        ap.error("--reuse-log must be a JSON filename")
    seen_sources = q + sources
    for lane, xs in candidates.items():
        for candidate in xs:
            candidate_doi = (candidate.get("doi") or "").strip().casefold()
            candidate_title = _norm_title(_title_of(candidate["citation"]))
            matches = [
                row
                for row in seen_sources
                if (
                    candidate_doi
                    and candidate_doi == (row.get("doi") or "").strip().casefold()
                )
                or candidate_title == _norm_title(_title_of(row.get("citation", "")))
            ]
            reuse_id = candidate.get("reuse_source_id")
            if reuse_id and reuse_id not in {row["source_id"] for row in matches}:
                ap.error(
                    f"{lane}: reuse_source_id does not match verified candidate identity"
                )
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
            if reuse_id:
                if (
                    not args.reuse_log
                    or not str(candidate.get("reuse_reason") or "").strip()
                ):
                    ap.error(
                        f"{lane}: explicit reuse needs --reuse-log and reuse_reason"
                    )
                reuse_tasks.append(
                    dict(
                        source_id=reuse_id,
                        candidate_id=candidate["candidate_id"],
                        lane=lane,
                        nbs_id=args.nbs_id,
                        tables=sorted(requested_tables),
                        families=requested_families,
                        reason=candidate["reuse_reason"],
                        status="pending_scope_review",
                        run_id=f"{run_prefix}_{lane}",
                        search_date=args.date,
                    )
                )
                continue
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
    reuse_text = json.dumps(reuse_tasks, indent=2, ensure_ascii=False) + "\n"
    if args.reuse_log:
        reuse_path = paths.logs / args.reuse_log
        if reuse_path.exists() and reuse_path.read_text(encoding="utf-8") != reuse_text:
            ap.error("reuse log differs; use a new run/log name to preserve history")
    known_doi = {(r["doi"] or "").lower() for r in q} | {
        (r.get("doi") or "").lower() for r in sources
    }
    known_title = {_norm_title(_title_of(r["citation"])) for r in q} | {
        _norm_title(_title_of(r["citation"])) for r in sources
    }
    ids = {r["source_id"] for r in q} | {r["source_id"] for r in sources}

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
            if _norm_title(_title_of(x.get("citation", ""))) in known_title:
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
                f"{run_prefix} (ruleset {args.ruleset}, discovery). process={process}; "
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
            known_title.add(_norm_title(_title_of(x["citation"])))
            added.append((lane, sid))
    if args.reuse_log:
        paths.logs.mkdir(parents=True, exist_ok=True)
        atomic_write(paths.logs / args.reuse_log, reuse_text.encode("utf-8"))
    _wr(paths.queue, q, qcols)
    report(
        f"queue +{len(added)}; explicit reuse tasks {len(reuse_tasks)} (deduplicated {len(dropped)}: {Counter(d for _, _, d in dropped)})"
    )
    if bad_fams:
        report(f"  family tags not in FAM (dropped from `family`): {dict(bad_fams)}")

    table_list = sorted({table for _, table, _ in protocols})
    for (lane, table, process), protocol in protocols.items():
        search_log.log_search(
            nbs=args.nbs_id,
            path=paths.searches,
            search_date=args.date,
            table=table,
            category=process,
            family=args.family,
            ruleset_version=args.ruleset,
            run_id=f"{run_prefix}_{lane}",
            searched_by=args.searched_by,
            screening_steps=STEPS,
            search_terms=protocol["search_terms"],
            inclusion_criteria=protocol["inclusion_criteria"],
            limits=protocol["limits"],
            n_retrieved=""
            if protocol["n_retrieved"] is None
            else str(protocol["n_retrieved"]),
            n_screened=""
            if protocol["n_screened"] is None
            else str(protocol["n_screened"]),
            n_included=str(protocol["n_included"]),
            discovery_log_ref=f"methodology/discovery_logs/{log_names[lane]}",
            note="Counts describe the reported bounded search set before queue deduplication; unknown totals remain blank. See report for reuse, exclusions and unavailable channels.",
        )
        report(
            f"  SRCH {table} {process:12s} ({lane}) n_included={protocol['n_included']}"
        )
    # ledger
    for process, status in ledger_status.items():
        process_tables = {
            table for _, table, category in protocols if category == process
        }
        for table in sorted(process_tables):
            for stage in ("searched", "screened"):
                ledger.mark(
                    args.nbs_id,
                    table,
                    process,
                    stage,
                    status,
                    family=args.family,
                    run_id=run_prefix,
                    by="orchestrator",
                    path=paths.ledger,
                    note=f"discovery round {args.date}; see SRCH {run_prefix}_* rows + discovery logs",
                )
    report(f"  ledger: {ledger_status} on {table_list}")
    # tracked discovery logs
    paths.logs.mkdir(parents=True, exist_ok=True)
    for lane, txt in tracked_reports.items():
        name = log_names[lane]
        atomic_write(paths.logs / name, txt.encode("utf-8"))
        report(f"  log → methodology/discovery_logs/{name}")
    return messages


def main(argv: list[str] | None = None, *, paths: DiscoveryRegistrationPaths) -> int:
    """Run one complete registration against explicit data locations.

    Validation, history checks and all writes run on private output copies.
    Stable inputs and one writer are required. The publication helper provides
    rollback on caught failures, not crash safety or simultaneous reader visibility.
    """
    ap = _parser()
    args = ap.parse_args(argv)
    if args.root is not None:
        paths = DiscoveryRegistrationPaths.from_root(args.root)
    if not args.dry_run:
        from nbs_ruralscan.schema_tools.evidence_authority import require_writable

        require_writable(paths.queue.parent.parent)
    logs = _kv(ap, args.log_names)
    for name in logs.values():
        if Path(name).name != name or not name.endswith(".md"):
            ap.error("log name must be a Markdown filename")
    if args.reuse_log and (
        Path(args.reuse_log).name != args.reuse_log
        or not args.reuse_log.endswith(".json")
    ):
        ap.error("--reuse-log must be a JSON filename")
    reports = [paths.logs / name for name in logs.values()]
    destinations = [paths.queue, paths.searches, *reports]
    if args.ledger:
        destinations.append(paths.ledger)
    if args.reuse_log:
        destinations.append(paths.logs / args.reuse_log)
    # Refuse case-only collisions on every platform, including fresh destinations.
    if len({str(p.resolve()).casefold() for p in destinations}) != len(destinations):
        raise ValueError("Registration destinations must be distinct (including case)")
    inputs = [paths.sources, paths.families]
    for selected in (args.candidates, args.reports, args.protocols):
        inputs.extend(Path(p).absolute() for p in _kv(ap, selected).values())
    for path in [paths.queue, *inputs]:
        if not path.is_file():
            raise FileNotFoundError(f"Missing discovery input: {path}")
    protected = {str(p.resolve()).casefold() for p in inputs}
    if any(str(p.resolve()).casefold() in protected for p in destinations):
        raise ValueError("Registration destination overlaps a read-only input")
    # An unrequested existing ledger must never become a report/queue destination.
    if not args.ledger and any(
        str(p.resolve()).casefold() == str(paths.ledger.resolve()).casefold()
        for p in destinations
    ):
        raise ValueError("Registration destination overlaps the unrequested ledger")
    root = Path(os.path.commonpath([p.parent for p in destinations]))
    messages: list[str] = []

    def render(staged: SchemaBuildPaths) -> list[Path]:
        assert staged.output_root is not None
        target = staged.output_root
        selected = replace(
            paths,
            queue=target / paths.queue.relative_to(root),
            searches=target / paths.searches.relative_to(root),
            ledger=target / paths.ledger.relative_to(root)
            if args.ledger
            else paths.ledger,
            logs=target / paths.logs.relative_to(root)
            if reports or args.reuse_log
            else paths.logs,
        )
        messages.extend(_apply(args, ap, selected))
        return []

    staged_publish(
        SchemaBuildPaths(root / "schema"),
        destinations,
        render,
        markdown_destinations=tuple(reports),
        dry_run=args.dry_run,
    )
    if args.dry_run:
        print("DRY RUN: complete registration batch validated; nothing published")
    for message in messages:
        print(message)
    return 0
