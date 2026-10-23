#!/usr/bin/env python3
"""Build a ROW-review batch (generated T3/T6 rows) for the review page (docs/review.html).

    python3 scripts/build-row-review-batch.py <batch_id> --nbs <nbs_id> --title "..." \
        [--rows rows.csv | --all-rollups] [--notes "..."]

`rows.csv` columns: record_id (required), question (optional: why this row needs a look).
`--all-rollups` takes every NbS roll-up row (no family, no scope) from both tables. Writes
`docs/review/<batch_id>.json` with ``"kind": "rows"`` (one card per generated row: class,
confidence, prose, statement, family vote, held-out units and the evidence it rests on, each
unit with its citation and a trimmed verbatim quote) and adds the batch to
`docs/review/index.json` with kind "rows". Reads the recipe tables + EV/SRC registers only;
never edits them. Decisions come back through scripts/apply-row-review-export.py.

Each card also carries an ``at_a_glance`` block for rapid triage, computed deterministically
from the same data (no new prose): headline, a one-line statement,
basis mix, top-source share, income mix, a one-line family vote and rule-based red flags.
The statement is built from the row's own fields, never the engine prose, so it always agrees
with the headline (a family-vote re-class included); its T3 lead takes the TTL wording of the
risk role from ``schema/lookups/display_vocab.csv`` (the controlled display vocabulary, also
copied into the batch as ``"vocab"`` so the page shows labels, definitions and provenance
instead of raw codes).
Optionally each card carries a ``priority`` block (``--fragility`` CSV from
scripts/row-fragility.py, ``--second-read`` JSON verdicts from an independent reader): a
score, a level (high / medium / low) and plain "why this needs you" lines, so a reviewer who
can only glance at most rows reads the least certain ones properly. Priority is triage only;
it never changes a row.
Weights there are a REVIEW APPROXIMATION of the engine's (tier × claim basis × design ×
grey discount, then one vote per source split across its units) — good for spotting a row
that leans on one paper or on ratings, not a replay of cell_synthesis.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.recipe.direction_sense import reads as direction_reads  # noqa: E402
from nbs_ruralscan.recipe.synthesis import (  # noqa: E402
    _DEFAULT_GREY_DISCOUNT,
    BASIS_W,
    GREY_DISCOUNT,
    TIER_W,
)

DESIGN_WEIGHTS = ROOT / "schema" / "lookups" / "design_weights.csv"
RECIPES = ROOT / "schema" / "recipes"
EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
SRC = ROOT / "schema" / "registers" / "SRC_source_register.csv"
OUT = ROOT / "docs" / "review"
VOCAB = ROOT / "schema" / "lookups" / "display_vocab.csv"
TABLES = {
    "T3": "T3_nbs_hazard_farming.csv",
    "T6": "T6_nbs_scorecard.csv",
    "T6E": "T6E_economic_profile.csv",
}
QUOTE_MAX = 400
#: row reject codes (the page carries the same list + gloss)
ROW_REASONS = [
    "wrong_class",
    "wrong_confidence",
    "prose_misleading",
    "evidence_misrouted",
    "should_be_split",
    "other",
]


def _j(s: str | None, default=None):
    if not s:
        return default
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return default


#: fields of display_vocab.csv copied into the batch for each code
VOCAB_KEYS = ("label", "ttl_label", "definition", "source_ref", "source_url")


def load_vocab(path: Path = VOCAB) -> dict[str, dict[str, dict[str, str]]]:
    """display_vocab.csv → {field: {code: {label, ttl_label, definition, source_ref, source_url}}}."""
    out: dict[str, dict[str, dict[str, str]]] = {}
    if not path.exists():
        return out
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.setdefault(r["field"], {})[r["code"]] = {
                k: (r.get(k) or "").strip() for k in VOCAB_KEYS
            }
    return out


_VOCAB = load_vocab()


def ttl(field: str, code: str, hazard: str = "", default: str = "") -> str:
    """The TTL wording for a code, `<hazard>` filled in; `default` when the vocab lacks it."""
    t = (_VOCAB.get(field, {}).get(code, {}).get("ttl_label") or default).strip()
    return t.replace("<hazard>", hazard)


def _lc_first(s: str) -> str:
    return s[:1].lower() + s[1:] if s else s


def _trim(q: str, n: int = QUOTE_MAX) -> str:
    q = " ".join((q or "").split())
    return q if len(q) <= n else q[: n - 1].rstrip() + "…"


def load_rows(nbs_id: str, recipes: Path = RECIPES) -> list[tuple[str, dict]]:
    out = []
    for table, fname in TABLES.items():
        p = recipes / nbs_id / fname
        if not p.exists():
            continue
        with p.open(newline="", encoding="utf-8") as f:
            out += [(table, r) for r in csv.DictReader(f)]
    return out


def _nbs_label(nbs_id: str, recipes: Path = RECIPES) -> str:
    p = recipes / nbs_id / "T0_nbs_registry.csv"
    if p.exists():
        with p.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("nbs_id") == nbs_id and (r.get("nbs_name") or "").strip():
                    return r["nbs_name"].strip()
    return nbs_id.replace("_", " ").capitalize()


def is_rollup(r: dict) -> bool:
    return (
        not (r.get("suitability_family_id") or "").strip()
        and not (r.get("scope_type") or "").strip()
    )


def _unit(eid: str, ev: dict, src: dict) -> dict:
    r = ev.get(eid)
    if not r:
        return {"evidence_id": eid, "missing": True}
    rel = _j(r.get("relationship"), {}) or {}
    ctx = _j(r.get("context"), {}) or {}
    s = src.get(r.get("source_id", ""), {})
    return {
        "evidence_id": eid,
        "source_id": r.get("source_id", ""),
        "citation": s.get("citation", ""),
        "variable": r.get("variable", ""),
        "direction": rel.get("direction", ""),
        "direction_reads": direction_reads(
            r.get("variable", ""),
            str(rel.get("direction") or ""),
            r.get("use_role", ""),
            str(rel.get("framing") or ""),
        )["text"],
        "strength": rel.get("strength_class", ""),
        "claim_basis": r.get("claim_basis", ""),
        "cited_original": (r.get("lineage_of") or "").strip()
        if r.get("claim_basis") == "cited_secondary"
        else "",
        "basis_bucket": _basis_bucket(
            r.get("claim_basis", ""), str(rel.get("design") or "")
        ),
        "comparator": str(ctx.get("comparator") or ""),
        "attribution": str(ctx.get("attribution") or ""),
        "beneficiary": str(ctx.get("beneficiary") or ""),
        "cost_nature": str(ctx.get("cost_nature") or ""),
        "suitability_family_id": r.get("suitability_family_id", ""),
        "page": r.get("page", ""),
        "review_state": r.get("review_state", ""),
        "quote": _trim(r.get("quote", "")),
    }


# ── at-a-glance (rapid triage; deterministic, no prose) ──────────────────────────────
_MEASURED = {"primary_measured", "primary_measurement", "table", "figure_read"}
BASIS_BUCKETS = [
    "measured",
    "cited_secondary",
    "practitioner_rating",
    "modelled",
    "expert",
]
INCOME_BUCKETS = ["LIC/LMIC", "UMIC", "HIC", "unknown"]
_FAM_SHORT = {
    "planted_silvoarable": "silvoarable",
    "linear_boundary": "boundary",
    "shaded_perennial": "shaded",
    "regeneration_farmland": "regeneration",
    "homegardens_proximity": "homegardens",
    "cross_family": "cross-family",
}
_LABEL_SYM = {
    "strong_positive": "+3",
    "moderate_positive": "+2",
    "slight_positive": "+1",
    "slight_negative": "−1",
    "moderate_negative": "−2",
    "strong_negative": "−3",
    "very_high": "+4",
    "high": "+3",
    "moderate": "+2",
    "low": "+1",
    "none": "0",
    "no_relationship": "0",
    "conflicting_evidence": "±",
    "data_deficient": "?",
}


def _design_weights(path: Path = DESIGN_WEIGHTS) -> dict[str, float]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as f:
        return {
            r["design"].strip(): float(r["weight_factor"])
            for r in csv.DictReader(f)
            if (r.get("weight_factor") or "").strip()
        }


_DW = _design_weights()


def _basis_bucket(claim_basis: str, design: str) -> str:
    if design == "practitioner_rating":
        return "practitioner_rating"
    if claim_basis == "cited_secondary":
        return "cited_secondary"
    if claim_basis == "modelled" or design == "model":
        return "modelled"
    if claim_basis in _MEASURED:
        return "measured"
    return "expert"


def _income_bucket(*vals: str) -> str:
    for v in vals:
        toks = {t for t in re.split(r"[|/_ ]+|,", (v or "").lower()) if t}
        toks -= {"mostly", "income"}
        if not toks:
            continue
        if toks <= {"low", "lower", "middle", "lic", "lmic"} and "upper" not in toks:
            return "LIC/LMIC"
        if toks <= {"upper", "middle"}:
            return "UMIC"
        if toks == {"high"}:
            return "HIC"
        return "unknown"  # mixed bands
    return "unknown"


def short_citation(citation: str, source_id: str = "") -> str:
    c = (citation or "").strip()
    if not c:
        return source_id
    first = re.split(r"[,(]", c, maxsplit=1)[0].strip()
    first = re.sub(r"\s+et al\.?$", "", first).rstrip(". ") or source_id
    yr = re.search(r"\b(19|20)\d{2}\b", c)
    head = c[: yr.start()] if yr else c[:150]
    many = " et al." if re.search(r"et al|&| and |;", head) else ""
    return f"{first}{many} {yr.group(0)}".strip() if yr else first + many


_CLASS_WORDS = {
    "strong_positive": "strongly positive",
    "moderate_positive": "moderately positive",
    "slight_positive": "slightly positive",
    "slight_negative": "slightly negative",
    "moderate_negative": "moderately negative",
    "strong_negative": "strongly negative",
    "no_relationship": "no clear effect",
    "very_high": "very high",
}


def _words(v: str) -> str:
    return (v or "").replace("_", " ").strip()


def class_words(cls_value: str, table: str = "T6", asset: bool = False) -> str:
    w = _CLASS_WORDS.get(cls_value, _words(cls_value))
    if table == "T3" and w and cls_value != "no_relationship":
        w += " sensitivity" if asset else " mitigation"
    return w


def build_statement(
    *,
    table: str,
    nbs_label: str,
    target: dict,
    cls_value: str,
    confidence: str,
    n_units: int,
    n_sources: int,
    measured_share: float,
    vote_line: str,
    data_deficient: bool,
    conflicting: bool,
    harm_sources: int,
) -> str:
    """One-line statement built ONLY from the row's own fields (never the engine prose),
    so it always agrees with the headline — a family-vote re-class included."""
    role = target.get("risk_role") or "livelihood_mitigation"
    asset = table == "T3" and role == "asset_threat"
    hz = _words(target.get("hazard", ""))
    if table in ("T6", "T6E"):
        lead = f"{nbs_label} → {_words(target.get('priority', ''))}"
    elif asset:
        lead = f"{nbs_label} — " + _lc_first(
            ttl("risk_role", role, hz, "Threat to the works from <hazard>")
        )
    else:
        fs = target.get("farming_system", "")
        fs = "all farming systems" if fs in ("", "all") else _words(fs)
        lead = f"{nbs_label} — " + _lc_first(
            ttl("risk_role", role, hz, "Protects farmers from <hazard>")
        )
        lead += f" ({fs})"
    src_s = f"{n_sources} source{'' if n_sources == 1 else 's'}"
    if data_deficient:
        meas = (
            "none measured"
            if measured_share <= 0
            else f"{round(100 * measured_share)}% measured"
        )
        body = f"not enough evidence to state a class ({src_s}, {meas})"
    elif conflicting:
        body = (
            f"evidence conflicts — sub-practices disagree ({vote_line})"
            if vote_line
            else "evidence conflicts (minority side ≥ 1/3 of the weight)"
        )
    elif asset and not cls_value:
        body = "not assessed"
    else:
        body = (
            f"{class_words(cls_value, table, asset) or 'no class'} "
            f"({_words(confidence) or 'unrated'} confidence; {n_units} unit{'' if n_units == 1 else 's'}, {src_s})"
        )
    out = f"{lead}: {body}"
    if harm_sources:
        out += f" · harm reported in {harm_sources} source{'' if harm_sources == 1 else 's'}"
    return out


def family_vote_line(fv: dict | None, nbs_id: str = "") -> str:
    if not fv or not fv.get("votes"):
        return ""
    out = []
    for v in fv["votes"]:
        fam = str(v.get("family") or "")
        if nbs_id and fam.startswith(nbs_id + "__"):
            fam = fam[len(nbs_id) + 2 :]
        fam = _FAM_SHORT.get(fam, fam.split("_")[0] if fam else "?")
        lab = str(v.get("label") or "")
        out.append(f"{fam} {_LABEL_SYM.get(lab, lab.replace('_', ' '))}")
    return " · ".join(out)


def _unit_weight(r: dict, s: dict) -> float:
    rel = _j(r.get("relationship"), {}) or {}
    w = TIER_W.get((s.get("benchmark_tier") or "").lower(), 0.5)
    w *= BASIS_W.get(r.get("claim_basis", ""), 0.5)
    w *= _DW.get(str(rel.get("design") or "").strip().lower(), 1.0)
    if (s.get("source_category") or "").lower() == "grey":
        w *= GREY_DISCOUNT.get(r.get("use_role", ""), _DEFAULT_GREY_DISCOUNT)
    return w


def at_a_glance(
    cls_value: str,
    confidence: str,
    j: dict,
    evidence_ids: list[str],
    ev: dict,
    src: dict,
    nbs_id: str = "",
    table: str = "T6",
    target: dict | None = None,
    nbs_label: str = "",
) -> dict:
    target = target or {}
    units = [
        ev[e]
        for e in evidence_ids
        if e in ev and (ev[e].get("review_state") or "") != "dropped"
    ]
    by_src: dict[str, list[dict]] = defaultdict(list)
    for r in units:
        by_src[r.get("source_id", "")].append(r)
    # one vote per source = its mean unit weight, split evenly across its units
    src_w = {
        sid: sum(_unit_weight(r, src.get(sid, {})) for r in rs) / len(rs)
        for sid, rs in by_src.items()
    }
    total = sum(src_w.values()) or 1.0
    counts = dict.fromkeys(BASIS_BUCKETS, 0)
    wshare = dict.fromkeys(BASIS_BUCKETS, 0.0)
    inc_n = dict.fromkeys(INCOME_BUCKETS, 0)
    for sid, rs in by_src.items():
        for r in rs:
            rel = _j(r.get("relationship"), {}) or {}
            ctx = _j(r.get("context"), {}) or {}
            b = _basis_bucket(r.get("claim_basis", ""), str(rel.get("design") or ""))
            counts[b] += 1
            wshare[b] += src_w[sid] / len(rs) / total
            inc = _income_bucket(
                str(ctx.get("income_group") or ""),
                src.get(sid, {}).get("study_income_group", ""),
            )
            inc_n[inc] += 1
    n = len(units)
    income_mix = {k: round(v / n, 3) if n else 0.0 for k, v in inc_n.items()}
    top_sid = max(src_w, key=lambda k: src_w[k]) if src_w else ""
    top_share = round(src_w[top_sid] / total, 3) if top_sid else 0.0
    dd = bool(j.get("data_deficient")) or cls_value == "data_deficient"
    conf = bool(j.get("conflicting")) or cls_value == "conflicting_evidence"
    headline = (
        "DATA DEFICIENT"
        if dd
        else "CONFLICTING"
        if conf
        else f"{_words(cls_value) or 'no class'} · {_words(confidence) or '—'}"
    )
    flags = []
    if len(by_src) == 1:
        flags.append("rests on 1 source")
    if top_share > 0.4 and len(by_src) > 1:
        flags.append("single source carries >40%")
    if wshare["cited_secondary"] > 0.5:
        flags.append("mostly second-hand")
    if wshare["practitioner_rating"] > 0.5:
        flags.append("mostly practitioner ratings")
    if income_mix["HIC"] > 0.5:
        flags.append("HIC-dominated")
    if n and inc_n["LIC/LMIC"] == 0:
        flags.append("no LIC/LMIC evidence")
    if (cls_value.startswith("slight") or cls_value == "low") and confidence in (
        "high",
        "very_high",
    ):
        flags.append("weak class but high confidence")
    mal = j.get("maladaptation")
    harm_sources = 0
    if mal and (not isinstance(mal, dict) or mal.get("n_units") or mal.get("ids")):
        flags.append("harm units present")
        harm_sources = int(mal.get("n_sources") or 1) if isinstance(mal, dict) else 1
    if conf:
        flags.append("conflicting")
    if dd:
        flags.append("data deficient")
    s_top = src.get(top_sid, {})
    vote_line = family_vote_line(j.get("family_vote"), nbs_id)
    statement = build_statement(
        table=table,
        nbs_label=nbs_label or _words(nbs_id).capitalize(),
        target=target,
        cls_value=cls_value,
        confidence=confidence,
        n_units=n,
        n_sources=len(by_src),
        measured_share=wshare["measured"],
        vote_line=vote_line,
        data_deficient=dd,
        conflicting=conf,
        harm_sources=harm_sources,
    )
    return {
        "headline": headline,
        "statement_short": statement,
        "basis": {
            "n_units": n,
            "n_sources": len(by_src),
            "counts": counts,
            "weight_share": {k: round(v, 3) for k, v in wshare.items()},
        },
        "top_source_share": {
            "share": top_share,
            "source_id": top_sid,
            "citation": short_citation(s_top.get("citation", ""), top_sid),
        },
        "income_mix": income_mix,
        "family_vote_line": vote_line,
        "red_flags": flags,
    }


def card(
    table: str,
    r: dict,
    ev: dict,
    src: dict,
    question: str = "",
    nbs_label: str = "",
) -> dict:
    j = _j(r.get("justification"), {}) or {}
    if table in ("T6", "T6E"):
        target = {"priority": r.get("variable_id", "")}
        target_label = r.get("variable_id", "")
        cls_field = "effect_direction"
        confidence = r.get("effect_confidence", "")
        mech_col, cond_col = "effect_mechanism", "conditionality"
    else:
        role = r.get("risk_role", "")
        target = {
            "hazard": r.get("hazard_type", ""),
            "farming_system": r.get("farming_system", ""),
            "risk_role": role,
        }
        target_label = f"{r.get('hazard_type', '')} × {r.get('farming_system', '')}"
        if role and role != "livelihood_mitigation":
            target_label += f" ({role})"
        cls_field = (
            "asset_sensitivity" if role == "asset_threat" else "mitigation_potential"
        )
        confidence = r.get("confidence", "")
        mech_col, cond_col = "mitigation_mechanism", "caveats"
    held = j.get("held_out_of_class") or {}
    ev_ids = _j(r.get("evidence_ids"), []) or []
    cls_value = r.get(cls_field, "") or ""
    return {
        "record_id": r.get("record_id", ""),
        "table": table,
        "nbs_id": r.get("nbs_id", ""),
        "suitability_family_id": r.get("suitability_family_id", ""),
        "scope": ":".join(
            x for x in (r.get("scope_type", ""), r.get("scope_id", "")) if x
        ),
        "target": target,
        "target_label": target_label,
        "class": {"field": cls_field, "value": r.get(cls_field, "")},
        "confidence": confidence,
        "evidence_level": r.get("evidence_level", ""),
        "agreement_level": r.get("agreement_level", ""),
        "data_deficient": bool(j.get("data_deficient")),
        "data_deficient_reason": j.get("data_deficient_reason", ""),
        "conflicting": bool(j.get("conflicting")),
        "mechanism": j.get("mechanism") or r.get(mech_col, ""),
        "conditionality": j.get("conditionality") or r.get(cond_col, ""),
        "statement": j.get("statement", ""),
        "pool_note": j.get("pool_note", ""),
        "family_vote": j.get("family_vote") or None,
        "held_out_of_class": [
            {"reason": k, "units": [_unit(e, ev, src) for e in (ids or [])]}
            for k, ids in held.items()
        ],
        "evidence": [_unit(e, ev, src) for e in ev_ids],
        "question": question,
        "at_a_glance": at_a_glance(
            cls_value,
            confidence,
            j,
            ev_ids,
            ev,
            src,
            r.get("nbs_id", ""),
            table=table,
            target=target,
            nbs_label=nbs_label,
        ),
    }


PRIORITY_HIGH = 9.0
PRIORITY_MEDIUM = 5.0


def load_fragility(path: Path | str | None) -> dict[str, dict]:
    """record_id -> {n_units, n_pivotal, pivotal: [(evidence_id, flips_to)]}."""
    if not path:
        return {}
    out: dict[str, dict] = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            piv = []
            for part in (r.get("pivotal_units") or "").split(";"):
                if "->" in part:
                    e, lab = part.split("->", 1)
                    piv.append((e.strip(), lab.strip()))
            out[r["record_id"]] = {
                "n_units": int(r.get("n_units") or 0),
                "n_pivotal": int(r.get("n_pivotal") or 0),
                "pivotal": piv,
            }
    return out


def load_second_read(paths: list[str] | None) -> dict[str, dict]:
    """record_id -> {verdict, severity, why} from one or more reader JSON files."""
    out: dict[str, dict] = {}
    for p in paths or []:
        for r in json.loads(Path(p).read_text(encoding="utf-8")):
            out[r["record_id"]] = {
                "verdict": r.get("verdict", ""),
                "severity": int(r.get("severity") or 0),
                "why": (r.get("why") or "").strip(),
            }
    return out


def _flip_words(lab: str) -> str:
    if lab == "row gone":
        return "the row disappears"
    if lab == "data_deficient":
        return "the row becomes data deficient"
    return f"the class becomes {_words(lab)}"


def priority(c: dict, frag: dict | None, second: dict | None) -> dict | None:
    """Review-priority score + plain reasons for one card (None without any input).

    Points: second-reader severity ×3 · a class held up by single units (+2, +0.5 per
    pivotal unit up to 4) — halved on data-deficient rows, where a flip changes little ·
    high/very-high confidence on a row a single unit can flip (+2) · red flags +0.5 each.
    """
    if frag is None and second is None:
        return None
    score, why = 0.0, []
    if second and second.get("verdict") == "concern":
        score += 3 * second.get("severity", 0)
        if second.get("why"):
            why.append(f"Second reader: {second['why']}")
    dd = c.get("data_deficient") or c["class"]["value"] == "data_deficient"
    if frag and frag.get("n_pivotal"):
        n, k = frag["n_units"], frag["n_pivotal"]
        pts = 2 + 0.5 * min(k, 4)
        score += pts / 2 if dd else pts
        cite = {u["evidence_id"]: u for u in c.get("evidence", [])}
        named = []
        for e, lab in frag["pivotal"][:3]:
            u = cite.get(e, {})
            who = short_citation(u.get("citation", ""), u.get("source_id", "")) or e
            named.append(f"{who} ({e}): {_flip_words(lab)}")
        if not dd:
            why.append(
                f"Fragile: {k} of {n} unit{'s' if n != 1 else ''} can each flip this row "
                f"on its own. Check these first — " + "; ".join(named) + "."
            )
        else:
            why.append("Rests on very little evidence: " + "; ".join(named) + ".")
        if (c.get("confidence") or "") in ("high", "very_high") and not dd:
            score += 2
            why.append(
                f"Stated at {_words(c['confidence'])} confidence, yet one unit can change it."
            )
    flags = (c.get("at_a_glance") or {}).get("red_flags") or []
    score += 0.5 * len(flags)
    if second and second.get("verdict") == "consistent" and not why:
        why.append(
            f"Second reader found it consistent: {second.get('why', '')}".strip()
        )
    level = (
        "high"
        if score >= PRIORITY_HIGH
        else "medium"
        if score >= PRIORITY_MEDIUM
        else "low"
    )
    return {
        "score": round(score, 2),
        "level": level,
        "why": why,
        "fragility": (
            {
                "n_units": frag["n_units"],
                "n_pivotal": frag["n_pivotal"],
                "pivotal": [
                    {"evidence_id": e, "flips_to": lab} for e, lab in frag["pivotal"]
                ],
            }
            if frag
            else None
        ),
        "second_read": second,
    }


def build_cards(
    nbs_id: str,
    wanted: dict[str, str] | None = None,
    all_rollups: bool = False,
    recipes: Path = RECIPES,
    ev_path: Path = EV,
    src_path: Path = SRC,
    fragility: dict[str, dict] | None = None,
    second_read: dict[str, dict] | None = None,
) -> tuple[list[dict], list[str]]:
    """Cards for the wanted record_ids ({id: question}) and/or every roll-up row."""
    wanted = wanted or {}
    with ev_path.open(newline="", encoding="utf-8") as f:
        ev = {r["evidence_id"]: r for r in csv.DictReader(f)}
    with src_path.open(newline="", encoding="utf-8") as f:
        src = {r["source_id"]: r for r in csv.DictReader(f)}
    cards, seen = [], set()
    label = _nbs_label(nbs_id, recipes)
    for table, r in load_rows(nbs_id, recipes):
        rid = r.get("record_id", "")
        if rid in wanted or (all_rollups and is_rollup(r)):
            c = card(table, r, ev, src, wanted.get(rid, ""), label)
            pr = priority(c, (fragility or {}).get(rid), (second_read or {}).get(rid))
            if pr is not None:
                c["priority"] = pr
            cards.append(c)
            seen.add(rid)
    return cards, [k for k in wanted if k not in seen]


def write_batch(
    batch_id: str,
    title: str,
    cards: list[dict],
    notes: str = "",
    out_dir: Path = OUT,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    p = out_dir / f"{batch_id}.json"
    p.write_text(
        json.dumps(
            {
                "kind": "rows",
                "batch": {
                    "id": batch_id,
                    "title": title,
                    "date": today,
                    "notes": notes,
                    "n": len(cards),
                    "kind": "rows",
                },
                "reasons": ROW_REASONS,
                "vocab": _VOCAB,
                "rows": cards,
            },
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    idx_p = out_dir / "index.json"
    idx = (
        json.loads(idx_p.read_text(encoding="utf-8"))
        if idx_p.exists()
        else {"batches": []}
    )
    idx["batches"] = [b for b in idx["batches"] if b["id"] != batch_id] + [
        {
            "id": batch_id,
            "title": title,
            "date": today,
            "n": len(cards),
            "file": f"review/{batch_id}.json",
            "kind": "rows",
        }
    ]
    idx_p.write_text(
        json.dumps(idx, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return p


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("batch_id")
    ap.add_argument("--nbs", required=True)
    ap.add_argument("--title", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--rows", help="CSV with record_id[,question]")
    g.add_argument("--all-rollups", action="store_true")
    ap.add_argument("--notes", default="")
    ap.add_argument("--fragility", help="CSV from scripts/row-fragility.py")
    ap.add_argument(
        "--second-read",
        nargs="*",
        default=[],
        help="JSON verdict file(s): [{record_id, verdict, severity, why}]",
    )
    a = ap.parse_args(argv)
    wanted: dict[str, str] = {}
    if a.rows:
        with open(a.rows, newline="", encoding="utf-8") as f:
            wanted = {
                r["record_id"].strip(): (r.get("question") or "").strip()
                for r in csv.DictReader(f)
                if (r.get("record_id") or "").strip()
            }
    cards, missing = build_cards(
        a.nbs,
        wanted,
        a.all_rollups,
        fragility=load_fragility(a.fragility),
        second_read=load_second_read(a.second_read),
    )
    write_batch(a.batch_id, a.title, cards, a.notes)
    print(
        f"{len(cards)} row card(s) → docs/review/{a.batch_id}.json; missing ids: {missing}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
