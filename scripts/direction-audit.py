#!/usr/bin/env python3
"""Blind direction audit of effect evidence (ruleset v1.6.17, catalogue #37).

    python3 scripts/direction-audit.py compare            # recode vs register → disagreements
    python3 scripts/direction-audit.py apply [--dry-run]  # adjudicated corrections + cue back-fill

Coders re-read every active effect unit WITHOUT seeing its coded direction
(`pipeline/staging/direction_recode/in_N.json` → `out_N.json`: direction, framing, verbatim
cue). `compare` sets their answer against the register and writes
`pipeline/staging/direction_recode/disagreements.json` for adjudication, plus a summary.
Adjudication writes `adj_*.json` (one per adjudicator, plus `adj_auto.json` for disagreements
that only reflect a register convention): `[{evidence_id, outcome: keep|correct|ambiguous,
direction, framing, cue, why}]`.

`apply` then, in the EV register only:
* `correct` → sets `relationship.direction` (and `framing` when it changed), stamps the cue,
  and logs a review_log row (verdict direction_audit, reason accepted_correction);
* `keep` / agreement → back-fills `relationship.direction_cue` when the cue is verbatim;
* `correct` to `none` because a result is not significant → keeps the sign and stamps
  `significance = ns` instead (the engine down-weights ns units; erasing the sign would
  change the method, not fix an error);
* `ambiguous` → logs a `flag` row for human review, changes nothing.
A cue is written only when it is a verbatim slice of the quote. Quote, page, variable and
every other field are untouched. Metrics land in pipeline/metrics/direction_audit.csv.
"""

from __future__ import annotations

import argparse
import sys
import json
import re
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.schema_tools.record_publication import edit_records  # noqa: E402
from nbs_ruralscan.schema_tools.review_inputs import ReviewInputs  # noqa: E402
from nbs_ruralscan.schema_tools.specialist_records import (  # noqa: E402
    REVIEW_COLUMNS,
    append_history,
    evidence,
    json_field,
    keyed_records,
    read_table,
    rebuild_command,
    write_table,
)

EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
LOG = ROOT / "pipeline" / "metrics" / "review_log.csv"
DIR = ROOT / "pipeline" / "staging" / "direction_recode"
METRICS = ROOT / "pipeline" / "metrics" / "direction_audit.csv"
SIGNS = {"positive", "negative"}
_NS_WHY = re.compile(r"signific|\bns\b|p\s*[=<>]|letter|overlap", re.I)


def _norm(s: str) -> str:
    """Compare text the way a reader would: NFKC glyphs (ligatures, minus signs), a word
    hyphen-split across a line break re-joined, whitespace collapsed, case folded."""
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"(\w)-\s+(\w)", r"\1\2", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def _records(files, *, adjudicated: bool = False) -> dict[str, dict]:
    records = {}
    for path in files:
        for eid, item in keyed_records(path, array=True).items():
            if eid in records:
                raise ValueError(
                    f"Duplicate evidence_id across direction inputs: {eid}"
                )
            if any(
                item.get(k) is not None and not isinstance(item[k], str)
                for k in ("direction", "framing", "cue", "why", "outcome")
            ):
                raise ValueError(f"Malformed direction annotation for {eid}")
            outcome = item.get("outcome")
            if adjudicated and outcome not in {"keep", "correct", "ambiguous"}:
                raise ValueError(f"Invalid adjudication outcome for {eid}")
            direction = item.get("direction")
            if not adjudicated and direction not in SIGNS | {"none", "ambiguous"}:
                raise ValueError(f"Invalid recoded direction for {eid}")
            if (
                adjudicated
                and outcome == "correct"
                and "direction" in item
                and direction not in SIGNS | {"none"}
            ):
                raise ValueError(f"Invalid corrected direction for {eid}")
            if item.get("framing") not in (None, "", "presence", "loss"):
                raise ValueError(f"Invalid framing for {eid}")
            records[eid] = item
    return records


def _selection(directory: Path, apply: bool):
    def members():
        return (
            tuple(sorted(directory.glob("out_*.json"))),
            tuple(sorted(directory.glob("adj_*.json"))) if apply else (),
        )

    recodes, adjudications = members()
    if not recodes and not adjudications:
        raise ValueError(f"No direction annotations in {directory}")

    def verify():
        if members() != (recodes, adjudications):
            raise ValueError(f"Direction annotation file set changed: {directory}")

    return recodes, adjudications, verify


def classify(coded: str, framing: str, rec: dict) -> str:
    d = rec.get("direction", "")
    if d == "ambiguous":
        return "recode_ambiguous"
    if d == coded:
        return (
            "agree"
            if (rec.get("framing") or "presence") == (framing or "presence")
            else "framing_differs"
        )
    if d in SIGNS and coded in SIGNS:
        return "opposite_sign"
    return "none_vs_sign"


def _compare(ev: Path, recodes, output: Path) -> int:
    rec = _records(recodes)
    _, rows = evidence(ev, "variable", "use_role", "relationship", "quote")
    dis, c = [], Counter()
    seen = 0
    for r in rows:
        x = rec.get(r["evidence_id"])
        if not x:
            continue
        seen += 1
        rel = json_field(r, "relationship")
        coded, framing = str(rel.get("direction") or ""), str(rel.get("framing") or "")
        k = classify(coded, framing, x)
        c[k] += 1
        if k != "agree":
            dis.append(
                {
                    "evidence_id": r["evidence_id"],
                    "kind": k,
                    "nbs_id": r.get("nbs_id", ""),
                    "variable": r["variable"],
                    "use_role": r["use_role"],
                    "coded": {"direction": coded, "framing": framing or "presence"},
                    "recode": x,
                    "outcome_raw": rel.get("outcome_raw", ""),
                    "quote": r["quote"],
                }
            )
    missing = sorted(set(rec) - {r["evidence_id"] for r in rows})
    output.write_text(json.dumps(dis, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"recoded {seen} unit(s): {dict(c)}; ids not in register: {len(missing)}")
    return 0


def compare(
    *, root: Path = ROOT, directory: Path | None = None, dry: bool = False
) -> int:
    root = root.resolve()
    directory = (
        directory.resolve() if directory is not None else root / DIR.relative_to(ROOT)
    )
    ev = root / EV.relative_to(ROOT)
    recodes, _, verify = _selection(directory, False)
    output = directory / "disagreements.json"
    return edit_records(
        [output],
        lambda files: _compare(ev, recodes, files[output]),
        inputs=ReviewInputs([ev, *recodes]),
        verify=verify,
        dry_run=dry,
    )


def _apply(ev: Path, log: Path, metrics: Path, recodes, adjudications) -> int:
    rec = _records(recodes)
    adj = _records(adjudications, adjudicated=True)
    cols, rows = evidence(ev, "relationship", "quote")
    today = date.today().isoformat()
    log_rows, c = [], Counter()
    history_cols, history = read_table(log, REVIEW_COLUMNS)
    metric_cols = ["date", "metric", "value"]
    if metrics.exists():
        metric_cols, _ = read_table(metrics, metric_cols)
    logged = {r["evidence_id"] for r in history if r["verdict"] == "direction_audit"}
    for r in rows:
        eid = r["evidence_id"]
        x, a0 = rec.get(eid), adj.get(eid)
        if not x and not a0:
            continue
        a: dict = a0 or {}
        rel = json_field(r, "relationship")
        coded, framing = str(rel.get("direction") or ""), str(rel.get("framing") or "")
        kind = classify(coded, framing, x) if x else "adjudicated_only"
        c[kind] += 1
        cue = (a.get("cue") or (x or {}).get("cue") or "").strip()
        cue_ok = bool(cue) and _norm(cue) in _norm(r.get("quote", ""))
        outcome = a.get("outcome") if a else ("keep" if kind == "agree" else "")
        if (
            outcome == "correct"
            and a.get("direction") == "none"
            and coded in SIGNS
            and _NS_WHY.search(a.get("why") or "")
        ):
            # the register keeps a non-significant point estimate's sign and down-weights
            # it through significance = ns (engine NS_FACTOR); "ns → none" is not a
            # direction error, so stamp ns instead of erasing the sign
            if rel.get("significance") != "ns":
                rel["significance"] = "ns"
                log_rows.append(
                    {
                        "date": today,
                        "evidence_id": eid,
                        "source_id": r["source_id"],
                        "verdict": "direction_audit",
                        "decision": "ok",
                        "reason": "accepted_correction",
                        "note": f"direction audit {today}: significance → ns (direction kept). {a.get('why', '')}".strip(),
                        "reviewer": "ai_direction_audit",
                    }
                )
                c["significance_set_ns"] += 1
            else:
                c["ns_already_kept_sign"] += 1
            outcome = "keep"
        if (
            outcome == "correct"
            and a.get("direction", coded) == coded
            and (a.get("framing") or framing or "presence") == (framing or "presence")
        ):
            outcome = "keep"  # already applied: re-running apply is a no-op
        if outcome == "correct":
            new_d = a.get("direction", coded)
            new_f = a.get("framing") or framing or "presence"
            note = f"direction audit {today}: {coded or '∅'}→{new_d}"
            if new_f != (framing or "presence"):
                note += f", framing {framing or 'presence'}→{new_f}"
                rel["framing"] = new_f
            rel["direction"] = new_d
            if cue_ok:
                rel["direction_cue"] = cue
            log_rows.append(
                {
                    "date": today,
                    "evidence_id": eid,
                    "source_id": r["source_id"],
                    "verdict": "direction_audit",
                    "decision": "ok",
                    "reason": "accepted_correction",
                    "note": f"{note}. {a.get('why', '')}".strip(),
                    "reviewer": "ai_direction_audit",
                }
            )
            c["corrected"] += 1
        elif outcome == "keep":
            if cue_ok and not rel.get("direction_cue"):
                rel["direction_cue"] = cue
                c["cue_backfilled"] += 1
        elif outcome == "ambiguous" and eid in logged:
            pass
        elif outcome == "ambiguous":
            log_rows.append(
                {
                    "date": today,
                    "evidence_id": eid,
                    "source_id": r["source_id"],
                    "verdict": "direction_audit",
                    "decision": "flag",
                    "reason": "other",
                    "note": f"direction audit {today}: direction unclear from the quote, needs a human. {a.get('why', '')}".strip(),
                    "reviewer": "ai_direction_audit",
                }
            )
            c["flagged"] += 1
        if cue and not cue_ok:
            c["cue_not_verbatim_skipped"] += 1
        r["relationship"] = json.dumps(rel, ensure_ascii=False)
    print(dict(c))
    if c:
        write_table(ev, cols, rows)
    append_history(log, history_cols, log_rows)
    # Each completed invocation records its observed counts. A second completed
    # audit can observe agreement after the first one changed a sign.
    observations = [
        {"date": today, "metric": k, "value": v} for k, v in sorted(c.items())
    ]
    if not metrics.exists():
        write_table(metrics, metric_cols, observations)
    else:
        append_history(metrics, metric_cols, observations)
    return 0


def apply(dry: bool, *, root: Path = ROOT, directory: Path | None = None) -> int:
    root = root.resolve()
    directory = (
        directory.resolve() if directory is not None else root / DIR.relative_to(ROOT)
    )
    recodes, adjudications, verify = _selection(directory, True)
    ev, log, metrics = (root / p.relative_to(ROOT) for p in (EV, LOG, METRICS))
    result = edit_records(
        [ev, log, metrics],
        lambda files: _apply(
            files[ev], files[log], files[metrics], recodes, adjudications
        ),
        inputs=ReviewInputs([*recodes, *adjudications]),
        verify=verify,
        dry_run=dry,
    )
    if not dry:
        print(f"now: {rebuild_command(root)}")
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("cmd", choices=["compare", "apply"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--root", type=Path, default=ROOT, help="Selected data root")
    ap.add_argument(
        "--recode-dir", type=Path, help="Directory of coder and adjudicator JSON files"
    )
    a = ap.parse_args(argv)
    return (
        compare(root=a.root, directory=a.recode_dir, dry=a.dry_run)
        if a.cmd == "compare"
        else apply(a.dry_run, root=a.root, directory=a.recode_dir)
    )


if __name__ == "__main__":
    raise SystemExit(main())
