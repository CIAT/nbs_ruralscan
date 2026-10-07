"""Per NbS × table (T3, T6) pipeline-position report → ``docs/table_progress.json``.

A project-manager view of where each generated effect table sits in the seven-stage
pipeline (searched → acquired → extracted → reviewed → synthesised → prose → benchmarked).
It measures **pipeline position, not evidence quality**: every number is read from an
existing artefact (progress ledger, SRCH register, acquisition queue, EV register,
review log, the generated recipe CSVs and their synthesis report / prose files, the seed
benchmark), never hand-claimed.

``build()`` is pure and deterministic (no timestamp); ``write()`` adds the build stamp only
when the payload actually changed, so ``generate.py schema --check`` stays churn-free.

Usage::

    python3 -m nbs_ruralscan.schema_tools.table_progress           # (re)write
    python3 -m nbs_ruralscan.schema_tools.table_progress --check   # fail if stale

Stdlib only.
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nbs_ruralscan.schema_tools.ledger import CATEGORIES, tables_for, xw_routes

NBS = [
    "agroforestry",
    "forest_restoration",
    "riparian_buffer",
    "water_harvesting_conservation",
    "wetland_management",
]
TABLES = ("T3", "T6")
T_FILES = {"T3": "T3_nbs_hazard_farming.csv", "T6": "T6_nbs_scorecard.csv"}
CONF_COL = {"T3": "confidence", "T6": "effect_confidence"}
STAGES = [
    "searched",
    "acquired",
    "extracted",
    "reviewed",
    "synthesised",
    "prose",
    "benchmarked",
]
STATUSES = ("not_started", "in_progress", "done")
REVIEW_DONE_SHARE = 0.5

# EV.claim_basis → display bucket; anything unlisted (incl. blank) → "other".
BASIS_BUCKETS = {
    "primary_measured": "measured",
    "primary_measurement": "measured",
    "table": "measured",
    "figure_read": "measured",
    "cited_secondary": "cited",
    "expert_assertion": "expert",
    "modelled": "modelled",
}

# Ordered: first match wins. Matched (case-insensitive) against the queue row's
# `blocker` text; `access_status` is checked alongside where noted.
BLOCKER_REASONS: list[tuple[str, str]] = [
    (r"HUMAN|403|human browser|unverified|ResearchGate", "needs_human"),
    (r"paywall|closed", "paywalled"),
    (r"no candidate URL|landing page|fetch failed|tool", "tool_failed"),
]
_BLOCKER_ORDER = ["needs_human", "paywalled", "tool_failed", "oa_not_fetched", "other"]

# Review-log decisions that mean a human rejected the unit (it is then soft-dropped).
_REJECT_DECISIONS = {"drop", "reclassify"}

RULES = {
    "searched": "Done when all four discovery processes (stock, updated literature, grey, "
    "tool) are marked searched in the progress ledger for this table, at table level or "
    "for any sub-practice; not started when there is no ledger activity and no logged "
    "search.",
    "acquired": "Done when every source the acquisition queue lists for this table is in "
    "hand (none pending); not started when the queue lists no sources for it.",
    "extracted": "Done when evidence units exist and no acquired source is waiting to be "
    "read; not started when there are no active evidence units.",
    "reviewed": f"Done when at least {int(REVIEW_DONE_SHARE * 100)}% of evidence units have "
    "a human review decision (signed off, or rejected and dropped); not started when none "
    "have.",
    "synthesised": "Done when the generated table has rows, matches its synthesis report, "
    "and the report lists no unmapped variables (decision-parked families are shown but do "
    "not block); not started when the table has no rows.",
    "prose": "Done when every row has written prose; not started when none do.",
    "benchmarked": "Done when both the seed benchmark table and the benchmark write-up "
    "exist; in progress when only one does.",
}
COMPLETION_RULE = (
    "Completion = round(100 × (stages done + 0.5 × stages in progress) / 7). "
    "It measures pipeline position, not evidence quality."
)


# ---------------------------------------------------------------------------- readers
def _split(value: str | None) -> set[str]:
    return {t.strip() for t in re.split(r"[|;,]", value or "") if t.strip()}


def _read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def iter_queue(path: Path) -> list[tuple[dict, set[str], set[str]]]:
    """Acquisition-queue rows as ``(row, nbs_ids, tables)``.

    Rows without a ``source_id`` or ``nbs_id`` are skipped; the first row per
    ``source_id`` wins (later repeats are dropped). ``duplicate``-status rows are kept —
    callers filter them. ``nbs_id`` / ``tables`` are split on ``| ; ,``.
    """
    out: list[tuple[dict, set[str], set[str]]] = []
    seen: set[str] = set()
    for row in _read_csv(Path(path)):
        sid = (row.get("source_id") or "").strip()
        nbs = (row.get("nbs_id") or "").strip()
        if not sid or not nbs or sid in seen:
            continue
        seen.add(sid)
        out.append((row, _split(nbs), _split(row.get("tables"))))
    return out


def _json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _sorted(counter: Counter | dict) -> dict:
    return {k: counter[k] for k in sorted(counter)}


def _pct(num: int, den: int) -> int:
    return round(100 * num / den) if den else 0


def blocker_reason(row: dict) -> str:
    """Classify a pending queue row's blocker into one of ``_BLOCKER_ORDER``."""
    text = row.get("blocker") or ""
    access = (row.get("access_status") or "").strip().lower()
    status = (row.get("status") or "").strip()
    for pattern, reason in BLOCKER_REASONS:
        if re.search(pattern, text, re.I):
            return reason
        if reason == "paywalled" and access == "paywalled":
            return reason
    if access in ("oa", "open_access") and status == "pending":
        return "oa_not_fetched"
    return "other"


# ---------------------------------------------------------------------- status helpers
def status_searched(categories_done: list[str], any_activity: bool) -> str:
    if set(CATEGORIES) <= set(categories_done):
        return "done"
    return "in_progress" if any_activity else "not_started"


def status_acquired(m: dict) -> str:
    if not m["discovered"]:
        return "not_started"
    return "done" if m["pending"] == 0 else "in_progress"


def status_extracted(m: dict) -> str:
    if not m["units_active"]:
        return "not_started"
    return "done" if m["queue_in_hand_unextracted"] == 0 else "in_progress"


def status_reviewed(m: dict) -> str:
    if m["reviewed_ok"] + m["reviewed_rejected"] == 0:
        return "not_started"
    return "done" if m["pct_reviewed"] >= REVIEW_DONE_SHARE * 100 else "in_progress"


def status_synthesised(m: dict) -> str:
    if not m["rows"]:
        return "not_started"
    # decision-parked families (qualitative_only, e.g. rooftop, homegardens) are shown
    # but do not block "done" — they are parked by decision, not pending work
    clean = not m["report_stale"] and not m["unmapped_variables"]
    return "done" if clean else "in_progress"


def status_prose(m: dict) -> str:
    if not m["with_prose"]:
        return "not_started"
    return "done" if m["with_prose"] == m["total"] else "in_progress"


def status_benchmarked(m: dict) -> str:
    n = int(bool(m["seed"])) + int(bool(m["benchmark_md"]))
    return ("not_started", "in_progress", "done")[n]


def completion(statuses: list[str]) -> dict:
    n_done = statuses.count("done")
    n_prog = statuses.count("in_progress")
    return {
        "pct": round(100 * (n_done + 0.5 * n_prog) / len(STAGES)),
        "n_done": n_done,
        "n_in_progress": n_prog,
    }


# ------------------------------------------------------------------------------ stages
def _searched(nbs: str, tbl: str, ledger: list[dict], srch: list[dict]) -> dict:
    rank = {"": 0, "not_started": 0, "in_progress": 1, "done": 2}
    lrows = [r for r in ledger if r.get("nbs_id") == nbs and r.get("table") == tbl]
    srows = [r for r in srch if r.get("nbs_id") == nbs and r.get("table") == tbl]
    by_cat: dict[str, dict] = {}
    done: list[str] = []
    for cat in CATEGORIES:
        cl = [r for r in lrows if r.get("category") == cat]
        table_level = [r for r in cl if not (r.get("family") or "")]
        base = table_level[0] if table_level else {}
        if not base and cl:  # no table-level row: best status across sub-practice rows
            base = {
                s: max((r.get(s) or "" for r in cl), key=lambda v: rank.get(v, 0))
                for s in ("searched", "screened", "verified")
            }
        if any((r.get("searched") or "") == "done" for r in cl):
            done.append(cat)
        cs = [r for r in srows if r.get("category") == cat]

        def _n(field: str, rows: list[dict] = cs) -> int:
            tot = 0
            for r in rows:
                try:
                    tot += int(float(r.get(field) or 0))
                except ValueError:
                    pass
            return tot

        by_cat[cat] = {
            "ledger_searched": base.get("searched", "") or "",
            "ledger_screened": base.get("screened", "") or "",
            "ledger_verified": base.get("verified", "") or "",
            "srch_rows": len(cs),
            "n_retrieved": _n("n_retrieved"),
            "n_screened": _n("n_screened"),
            "n_included": _n("n_included"),
            "latest_search_date": max(
                (r.get("search_date") or "" for r in cs), default=""
            ),
        }
    activity = bool(srows) or any(
        (r.get(s) or "not_started") != "not_started"
        for r in lrows
        for s in ("searched", "screened", "verified")
    )
    families = sorted(
        {
            r["family"]
            for r in lrows
            if r.get("family") and (r.get("searched") or "") == "done"
        }
    )
    return {
        "status": status_searched(done, activity),
        "categories_done": done,
        "categories_missing": [c for c in CATEGORIES if c not in done],
        "by_category": by_cat,
        "families_searched": families,
    }


def _queue_cell(nbs: str, tbl: str, queue: list) -> list[dict]:
    return [row for row, n_ids, tbls in queue if nbs in n_ids and tbl in tbls]


def _acquired(rows: list[dict]) -> dict:
    c = Counter((r.get("status") or "").strip() for r in rows)
    discovered = len(rows) - c["duplicate"]
    m = {
        "discovered": discovered,
        "pending": c["pending"],
        "acquired": c["acquired"],
        "extracted": c["extracted"],
        "duplicate": c["duplicate"],
        "pct_in_hand": _pct(c["acquired"] + c["extracted"], discovered),
    }
    return {"status": status_acquired(m), **m}


def _extracted(units: list[dict], n_in_hand: int) -> dict:
    active = [u for u in units if (u.get("review_state") or "") != "dropped"]
    basis = Counter((u.get("claim_basis") or "") or "unknown" for u in active)
    buckets = Counter(
        BASIS_BUCKETS.get(u.get("claim_basis") or "", "other") for u in active
    )
    m = {
        "units_active": len(active),
        "units_dropped": len(units) - len(active),
        "sources": len({u.get("source_id") for u in active if u.get("source_id")}),
        "by_role": _sorted(Counter(u.get("use_role") or "" for u in active)),
        "by_basis_bucket": _sorted(buckets),
        "by_claim_basis": _sorted(basis),
        "queue_in_hand_unextracted": n_in_hand,
    }
    return {"status": status_extracted(m), **m}


def _reviewed(units: list[dict], rejected_ids: set[str]) -> dict:
    active = [u for u in units if (u.get("review_state") or "") != "dropped"]
    ok = sum(1 for u in active if (u.get("reviewer_ok") or "").lower() == "true")
    rejected = sum(
        1
        for u in units
        if (u.get("review_state") or "") == "dropped"
        and u.get("evidence_id") in rejected_ids
    )
    m = {
        "reviewed_ok": ok,
        "reviewed_rejected": rejected,
        "unreviewed": len(active) - ok,
        "pct_reviewed": _pct(ok + rejected, len(active) + rejected),
    }
    return {"status": status_reviewed(m), **m}


def _justification(row: dict) -> dict:
    try:
        j = json.loads(row.get("justification") or "{}")
    except json.JSONDecodeError:
        return {}
    return j if isinstance(j, dict) else {}


def _synthesised(tbl: str, rows: list[dict], report: dict | None) -> dict:
    report = report or {}
    fams = Counter((r.get("suitability_family_id") or "") or "_rollup" for r in rows)
    conf = Counter((r.get(CONF_COL[tbl]) or "") or "none" for r in rows)
    flags: dict[str, Any] = {
        "intensity_limited": 0,
        "maladaptation": 0,
        "modelled_capped": 0,
        "proxy_capped": 0,
        "landscape_scale_only": 0,
    }
    severe: Counter = Counter()
    for r in rows:
        j = _justification(r)
        for k in ("intensity_limited", "modelled_capped", "proxy_capped"):
            if j.get(k) is True:
                flags[k] += 1
        if j.get("maladaptation") is not None:
            flags["maladaptation"] += 1
        sc = j.get("severity_coverage")
        if isinstance(sc, dict) and sc.get("severe_end"):
            severe[str(sc["severe_end"])] += 1
        if (r.get("landscape_scale_only") or "").lower() == "true":
            flags["landscape_scale_only"] += 1
    flags["severe_end"] = _sorted(severe)
    report_rows = int(report.get(f"{tbl.lower()}_rows") or 0)
    m: dict[str, Any] = {
        "rows": len(rows),
        "report_rows": report_rows,
        "report_stale": bool(report) and len(rows) != report_rows,
        "n_units_pooled": int(report.get("n_units_pooled") or 0),
        "families": _sorted(fams),
        "confidence": _sorted(conf),
        "flags": flags,
        "synth_dropped": len(report.get("dropped") or []),
        "collapsed": len(report.get("collapsed") or []),
        "excluded_economics": len(report.get("excluded_economics") or []),
        "unmapped_variables": [list(x) for x in report.get("unmapped_variables") or []],
        "parked_families": sorted(report.get("parked_families") or []),
    }
    if tbl == "T3":
        m["risk_role"] = _sorted(Counter(r.get("risk_role") or "" for r in rows))
    else:
        m["effect_direction"] = _sorted(
            Counter(r.get("effect_direction") or "" for r in rows)
        )
    return {"status": status_synthesised(m), **m}


def _prose(rows: list[dict], prose: dict | None) -> dict:
    prose = prose if isinstance(prose, dict) else {}
    n = sum(
        1
        for r in rows
        if r.get("record_id") in prose
        and _justification(r).get("prose_pending") is not True
    )
    m = {"with_prose": n, "total": len(rows), "pct": _pct(n, len(rows))}
    return {"status": status_prose(m), **m}


def _benchmarked(schema_root: Path, nbs: str, tbl: str) -> dict:
    stem = Path(T_FILES[tbl]).stem
    m = {
        "seed": (
            schema_root / "design" / "seed_benchmark" / f"{nbs}_{stem}.seed.csv"
        ).exists(),
        "benchmark_md": (schema_root / "recipes" / nbs / "T3T6_BENCHMARK.md").exists(),
    }
    return {"status": status_benchmarked(m), **m}


# ------------------------------------------------------------------------------- build
def build(schema_root: str | Path) -> dict:
    """The table-progress payload (``meta`` + ``cells``) — pure, no timestamp."""
    schema_root = Path(schema_root)
    repo = schema_root.parent
    ledger = _read_csv(repo / "pipeline" / "progress_ledger.csv")
    srch = _read_csv(schema_root / "registers" / "SRCH_search_register.csv")
    queue = iter_queue(repo / "pipeline" / "acquisition_queue.csv")
    ev = _read_csv(schema_root / "registers" / "EV_evidence_register.csv")
    review_log = _read_csv(repo / "pipeline" / "metrics" / "review_log.csv")
    rejected_ids = {
        r.get("evidence_id", "")
        for r in review_log
        if (r.get("decision") or "") in _REJECT_DECISIONS
    }
    routes = xw_routes(schema_root)
    ev_tables = [
        (u, tables_for(u.get("use_role", ""), u.get("variable", ""), routes))
        for u in ev
    ]

    cells: dict[str, dict] = {}
    for nbs in NBS:
        rdir = schema_root / "recipes" / nbs
        report = _json(rdir / "T3T6_synthesis_report.json")
        prose = _json(rdir / "T3T6_prose.json")
        cells[nbs] = {}
        for tbl in TABLES:
            qrows = _queue_cell(nbs, tbl, queue)
            units = [u for u, t in ev_tables if u.get("nbs_id") == nbs and tbl in t]
            rows = _read_csv(rdir / T_FILES[tbl])
            acq = _acquired(qrows)
            stages = {
                "searched": _searched(nbs, tbl, ledger, srch),
                "acquired": acq,
                "extracted": _extracted(units, acq["acquired"]),
                "reviewed": _reviewed(units, rejected_ids),
                "synthesised": _synthesised(tbl, rows, report),
                "prose": _prose(rows, prose),
                "benchmarked": _benchmarked(schema_root, nbs, tbl),
            }
            cells[nbs][tbl] = {
                "completion": completion([stages[s]["status"] for s in STAGES]),
                "stages": stages,
                "blockers": _blockers(nbs, tbl, stages, qrows, report, ledger),
            }

    meta = {
        "nbs": NBS,
        "tables": list(TABLES),
        "stages": STAGES,
        "rules": RULES,
        "completion_rule": COMPLETION_RULE,
        "review_done_share": REVIEW_DONE_SHARE,
        "basis_buckets": BASIS_BUCKETS,
        "blocker_reasons": _BLOCKER_ORDER,
    }
    return {"meta": meta, "cells": cells, "decisions": load_decisions(schema_root)}


DECISION_STATUS = ("open", "parked", "decided")
DECISIONS_CSV = Path("methodology") / "decisions" / "open_decisions.csv"


def load_decisions(schema_root: str | Path) -> list[dict[str, str]]:
    """`methodology/decisions/open_decisions.csv` → rows for the page, open first, then
    parked, then decided (newest first within a status). Unknown statuses are kept and
    flagged in `_status_note` so a typo shows up rather than hides a decision."""
    path = Path(schema_root).parent / DECISIONS_CSV
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        rows = [dict(r) for r in csv.DictReader(f)]
    for r in rows:
        if r.get("status") not in DECISION_STATUS:
            r["_status_note"] = f"unknown status {r.get('status')!r}"
    order = {s: i for i, s in enumerate(DECISION_STATUS)}
    rows.sort(
        key=lambda r: (
            order.get(r.get("status") or "", 99),
            r.get("raised") or "",
            r.get("decision_id") or "",
        )
    )
    # newest first within a status
    out: list[dict[str, str]] = []
    for st in DECISION_STATUS + ("",):
        grp = [
            r
            for r in rows
            if (r.get("status") if r.get("status") in DECISION_STATUS else "") == st
        ]
        out += sorted(grp, key=lambda r: r.get("raised") or "", reverse=True)
    return out


def _blockers(
    nbs: str,
    tbl: str,
    stages: dict,
    qrows: list[dict],
    report: dict | None,
    ledger: list[dict],
) -> dict:
    pending = [r for r in qrows if (r.get("status") or "").strip() == "pending"]
    tagged = sorted(
        ((blocker_reason(r), (r.get("source_id") or "").strip(), r) for r in pending),
        key=lambda t: (_BLOCKER_ORDER.index(t[0]), t[1]),
    )
    top = [
        {
            "source_id": sid,
            "citation": (r.get("citation") or "")[:120],
            "reason": reason,
            "blocker": (r.get("blocker") or "")[:160],
        }
        for reason, sid, r in tagged[:10]
    ]
    notes = sorted(
        {
            (
                r.get("family") or "",
                r.get("note") or "",
                r.get("last_run_id") or "",
                r.get("updated") or "",
            )
            for r in ledger
            if r.get("nbs_id") == nbs and r.get("table") == tbl and r.get("note")
        }
    )
    syn = stages["synthesised"]
    warnings: list[str] = []
    if not syn["rows"]:
        warnings.append("no T3/T6 outputs yet")
    if syn["report_stale"]:
        warnings.append("synthesis report stale")
    if stages["extracted"]["units_active"] and not stages["acquired"]["discovered"]:
        warnings.append(
            "evidence exists but the acquisition queue lists no sources for this table "
            "(queue tagging incomplete)"
        )
    unlogged = [
        c for c in CATEGORIES if not stages["searched"]["by_category"][c]["srch_rows"]
    ]
    if unlogged:
        warnings.append("search not logged for: " + ", ".join(unlogged))
    return {
        "pending_by_reason": _sorted(Counter(t[0] for t in tagged)),
        "acquired_not_extracted": stages["acquired"]["acquired"],
        "top": top,
        "unmapped_variables": syn["unmapped_variables"],
        "parked_families": syn["parked_families"],
        "weights_incomplete": sorted((report or {}).get("weights_incomplete") or []),
        "ledger_notes": [
            {"family": f, "note": n, "last_run_id": rid, "updated": up}
            for f, n, rid, up in notes
        ],
        "warnings": warnings,
    }


# ------------------------------------------------------------------------------- write
def _git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:  # noqa: BLE001 — never break the build on a missing git
        return "unknown"


def write(
    schema_root: str | Path, check: bool = False, dest: Path | None = None
) -> list[Path]:
    """(Re)write ``docs/table_progress.json``; returns ``[dest]`` if it was/is stale.

    Unchanged ``meta`` + ``cells`` → ``[]`` in both modes (the build stamp is not
    refreshed, so regeneration is churn-free).
    """
    schema_root = Path(schema_root)
    dest = Path(dest) if dest else schema_root.parent / "docs" / "table_progress.json"
    payload = build(schema_root)
    current = _json(dest)
    if (
        isinstance(current, dict)
        and current.get("cells") == payload["cells"]
        and current.get("meta") == payload["meta"]
        and current.get("decisions", []) == payload["decisions"]
    ):
        return []
    out = {
        "build": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "git_commit": _git_commit(),
        },
        **payload,
    }
    if not check:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(
            json.dumps(out, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    return [dest]


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    check = "--check" in argv
    root = Path(__file__).resolve().parents[3] / "schema"
    changed = write(root, check=check)
    for p in changed:
        print(("stale: " if check else "wrote: ") + str(p))
    return 1 if (check and changed) else 0


if __name__ == "__main__":
    raise SystemExit(main())
