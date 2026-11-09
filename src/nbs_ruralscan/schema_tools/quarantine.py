"""Auto-quarantine off-scope / wrong-practice evidence (QA guard "B", 2026-06-23).

2026-06-23 human QA dropped 61/102 reviewed units (60%) — dominated by off-scope
extraction (study-site / problem-statement / biomass / mapped-result *descriptions*) and
wrong-practice mis-mapping (reforestation, CSA umbrella tagged as agroforestry). The
deterministic checks (`check_scope`, `check_picos`) already flag these; this module ACTS on
them — soft-deleting (`review_state=dropped`) so they stop polluting the live register and
the AI-flagged worklist, while staying fully reversible + auditable (the locked soft-delete
model). Chosen over a build-FAIL because the signals are regex proxies: the reviewer keeps
the final call (re-open restores the row); the guard just stops junk reaching them by default.

SAFETY — never re-quarantines a row a human has touched:
  * `reviewer_ok=true`           — already signed off
  * `review_state=dropped`       — already dropped/quarantined
  * evidence_id in `review_log`  — a human applied a decision (incl. a re-open)
  * evidence_id in `decisions.json` — a human has an in-progress decision

Each quarantined row is stamped `[AUTO-QUARANTINE <kind>:<signal>]` in `attribution`
(idempotent) so the dashboard's dropped view + git history show exactly why.

Run on the WRITE path of `generate.py` only (never on `--check`, which must not mutate).
CLI: `python -m nbs_ruralscan.schema_tools.quarantine schema [--apply]` (default = dry-run).
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from nbs_ruralscan.schema_tools import check_picos, check_scope
from nbs_ruralscan.schema_tools.record_publication import edit_records
from nbs_ruralscan.schema_tools.review_inputs import ReviewInputs
from nbs_ruralscan.schema_tools.review_local import read_decisions
from nbs_ruralscan.schema_tools.specialist_records import read_table, write_table

_MARKER = "[AUTO-QUARANTINE "


@dataclass(frozen=True)
class QuarantinePaths:
    evidence: Path
    sources: Path
    policy: Path
    review_log: Path
    decisions: Path

    def __post_init__(self):
        for name, path in vars(self).items():
            object.__setattr__(self, name, Path(path).absolute())
        if len({str(p.resolve()).casefold() for p in vars(self).values()}) != len(
            vars(self)
        ):
            raise ValueError("Quarantine paths must be distinct")

    @classmethod
    def from_schema(cls, schema_root):
        schema = Path(schema_root).resolve()
        return cls(
            schema / "registers/EV_evidence_register.csv",
            schema / "registers/SRC_source_register.csv",
            schema / "lookups/m2b_variable_policy.csv",
            schema.parent / "pipeline/metrics/review_log.csv",
            schema.parent / "pipeline/review/decisions.json",
        )


def _paths(schema_root):
    return (
        schema_root
        if isinstance(schema_root, QuarantinePaths)
        else QuarantinePaths.from_schema(schema_root)
    )


def _read_rows(path: Path, id_field: str, *required: str, unique: bool = False):
    fields, rows = read_table(path, [id_field, *required])
    ids = [row[id_field] for row in rows]
    if any(not value.strip() for value in ids):
        raise ValueError(f"Missing {id_field} in {path}")
    if unique and len(set(ids)) != len(ids):
        raise ValueError(f"Duplicate {id_field} in {path}")
    return fields, rows


def _read_evidence(paths: QuarantinePaths, ev: Path):
    # A source register makes the tool exemption available; its join key must
    # then also be present on EV. Older isolated EV fixtures have no SRC.
    source_key = ("source_id",) if paths.sources.exists() else ()
    return _read_rows(
        ev, "evidence_id", "reviewer_ok", "review_state", *source_key, unique=True
    )


def _human_touched(paths: QuarantinePaths) -> set[str]:
    """Existing decisions are read without repairing or re-encoding the local store."""
    decisions, _ = read_decisions(paths.decisions)
    touched = set(decisions)
    if paths.review_log.exists():
        _, log = _read_rows(paths.review_log, "evidence_id")
        touched.update(row["evidence_id"] for row in log)
    return touched


# check_scope signals that are REPORTED for reviewer triage but NOT auto-quarantined. The
# `site_context` boundary (study/figure/region context vs a distributional rule) is fuzzier
# than the tight section regexes, so auto-dropping it would wrongly quarantine borderline
# rules and erode trust in the register. The extraction spec (#16) stops it at source; the
# reviewer decides the residue from the advisory SCOPE-CHECK report.
# `span_bleed` = a section signal fired but the quote still carries the criterion; the span
# is the defect, not the claim, so it goes to the reviewer to RE-SLICE (retro 2026-09, FR).
# `m2b_flag` = feasibility-level detail in an operational unit (catalogue #50): the reviewer
# decides; only the `m2b_exclude` variables are dropped (2026-10-29 retro).
_ADVISORY_ONLY = {"site_context", "span_bleed", "m2b_flag"}


def _screen(paths: QuarantinePaths, ev: Path, rows: list[dict]) -> list[dict]:
    """Run the paper checks in their historical order, keeping the first signal per ID."""
    touched = _human_touched(paths)
    if paths.sources.exists():
        _, sources = _read_rows(
            paths.sources, "source_id", "source_category", unique=True
        )
        tools = {r["source_id"] for r in sources if r["source_category"] == "tool"}
        touched.update(
            row["evidence_id"] for row in rows if row.get("source_id") in tools
        )
    if paths.policy.exists():
        _, policy = _read_rows(
            paths.policy, "variable", "decision", "reason", unique=True
        )
        for row in policy:
            if row["decision"] not in {"exclude", "flag"}:
                raise ValueError(
                    f"Unknown M2b decision for {row['variable']}: {row['decision']!r} in {paths.policy}"
                )
    flags: dict[str, dict] = {}
    for f in check_scope.check(ev, policy_path=paths.policy):
        if f["signal"] in _ADVISORY_ONLY:
            continue  # advisory-only — surfaced for review, not auto-quarantined
        flags.setdefault(f["evidence_id"], {"kind": "off_scope", **f})
    for f in check_picos.check(ev):  # wrong-practice; don't overwrite an off_scope hit
        flags.setdefault(f["evidence_id"], {"kind": "wrong_practice", **f})
    out = []
    for eid, f in flags.items():
        if eid in touched:
            continue
        out.append(
            {
                "evidence_id": eid,
                "kind": f["kind"],
                "signal": f["signal"],
                "snippet": f.get("snippet", ""),
            }
        )
    return out


def candidates(schema_root: str | Path | QuarantinePaths = "schema") -> list[dict]:
    """Eligible rows in scope-check order. The dry run writes no files."""
    paths = _paths(schema_root)
    inputs = ReviewInputs(vars(paths).values())
    result = []
    if paths.evidence.exists():
        _, rows = _read_evidence(paths, paths.evidence)
        result = _screen(paths, paths.evidence, rows)
    inputs.verify()
    return result


def _apply_private(paths: QuarantinePaths, ev: Path) -> list[dict]:
    if not ev.exists():
        return []
    fields, rows = _read_evidence(paths, ev)
    cands = {c["evidence_id"]: c for c in _screen(paths, ev, rows)}
    if not cands:
        return []
    if not {"review_state", "attribution"}.issubset(fields):
        raise ValueError(
            "The evidence register needs review_state and attribution for a soft drop"
        )
    applied: list[dict] = []
    for r in rows:
        c = cands.get(r.get("evidence_id", ""))
        if not c:
            continue
        if (r.get("review_state") or "") == "dropped":
            continue
        r["review_state"] = "dropped"
        stamp = f"{_MARKER}{c['kind']}:{c['signal']}]"
        if _MARKER not in (r.get("attribution") or ""):
            r["attribution"] = (
                (r.get("attribution") or "").rstrip() + " " + stamp
            ).strip()
        applied.append(c)
    if applied:
        write_table(ev, fields, rows)
    return applied


def apply(schema_root: str | Path | QuarantinePaths = "schema") -> list[dict]:
    """Soft-drop eligible evidence in a private copy, then publish the selected EV."""
    paths = _paths(schema_root)
    dependencies = ReviewInputs(
        [paths.sources, paths.policy, paths.review_log, paths.decisions]
    )
    return edit_records(
        [paths.evidence],
        lambda private: _apply_private(paths, private[paths.evidence]),
        inputs=dependencies,
        optional=[paths.evidence],
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report or soft-drop automatic quarantine candidates."
    )
    parser.add_argument("schema", nargs="?", type=Path, default=Path("schema"))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument(
        "--dry-run", action="store_true", help="Report candidates (default)"
    )
    args = parser.parse_args(argv)
    if args.apply:
        applied = apply(args.schema)
        print(
            f"AUTO-QUARANTINE: dropped {len(applied)} off-scope/wrong-practice unit(s)."
        )
    else:
        applied = candidates(args.schema)
        print(f"AUTO-QUARANTINE (dry-run): {len(applied)} candidate(s) — pass --apply:")
    for c in applied:
        print(f"  [{c['kind']}/{c['signal']}] {c['evidence_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
