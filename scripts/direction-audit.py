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
import csv
import json
import re
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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


def _recodes() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for p in sorted(DIR.glob("out_*.json")):
        for r in json.loads(p.read_text(encoding="utf-8")):
            out[r["evidence_id"]] = r
    return out


def _ev() -> tuple[list[str], list[dict]]:
    with EV.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        return list(rd.fieldnames or []), list(rd)


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


def compare() -> int:
    rec = _recodes()
    _, rows = _ev()
    dis, c = [], Counter()
    seen = 0
    for r in rows:
        x = rec.get(r["evidence_id"])
        if not x:
            continue
        seen += 1
        rel = json.loads(r.get("relationship") or "{}")
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
    (DIR / "disagreements.json").write_text(
        json.dumps(dis, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"recoded {seen} unit(s): {dict(c)}; ids not in register: {len(missing)}")
    return 0


def apply(dry: bool) -> int:
    rec = _recodes()
    adj = {
        a["evidence_id"]: a
        for p in sorted(DIR.glob("adj_*.json"))
        for a in json.loads(p.read_text(encoding="utf-8"))
    }
    cols, rows = _ev()
    today = date.today().isoformat()
    log_rows, c = [], Counter()
    with LOG.open(newline="", encoding="utf-8") as f:
        logged = {
            r["evidence_id"]
            for r in csv.DictReader(f)
            if r.get("verdict") == "direction_audit"
        }
    for r in rows:
        eid = r["evidence_id"]
        x, a0 = rec.get(eid), adj.get(eid)
        if not x and not a0:
            continue
        a: dict = a0 or {}
        rel = json.loads(r.get("relationship") or "{}")
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
    if dry:
        return 0
    with EV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    if log_rows:
        with LOG.open("a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(log_rows[0]), lineterminator="\n")
            w.writerows(log_rows)
    new = not METRICS.exists()
    with METRICS.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        if new:
            w.writerow(["date", "metric", "value"])
        for k, v in sorted(c.items()):
            w.writerow([today, k, v])
    print("now: python3 src/nbs_ruralscan/schema_tools/generate.py schema")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("cmd", choices=["compare", "apply"])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    return compare() if a.cmd == "compare" else apply(a.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
