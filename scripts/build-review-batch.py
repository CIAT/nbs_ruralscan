#!/usr/bin/env python3
"""Build a review batch for the simple review page (docs/review.html).

    python3 scripts/build-review-batch.py <batch_id> --title "..." --items items.csv [--notes "..."]

`items.csv` columns: evidence_id, question (why this unit needs a human look), and optionally
ai_decision / ai_reason (what the AI proposed; a reviewer who agrees with an AI reject can
press Reject without picking the reason again). Writes
`docs/review/<batch_id>.json` (the units with their fields + the quote), renders a page crop
per unit to `docs/review/img/<evidence_id>.png` (quote highlighted; whole page at low DPI
when the quote cannot be located), and updates `docs/review/index.json`. Reads only the
register + the cached PDF; never edits evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
import sys
from datetime import date
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.recipe.cell_synthesis import load_bands  # noqa: E402
from nbs_ruralscan.recipe.direction_sense import load_sense, read_sense  # noqa: E402
from nbs_ruralscan.recipe.direction_sense import reads as direction_reads  # noqa: E402
from nbs_ruralscan.schema_tools import check_bands  # noqa: E402
from nbs_ruralscan.schema_tools.review import REASON_CODES  # noqa: E402
from nbs_ruralscan.schema_tools.review_inputs import ReviewInputs  # noqa: E402
from nbs_ruralscan.schema_tools.review_batches import (  # noqa: E402
    batch_directory,
    publish_batch,
)
from nbs_ruralscan.ingest.integrity import validate_source_id  # noqa: E402

EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
SRC = ROOT / "schema" / "registers" / "SRC_source_register.csv"
CORPUS = ROOT / ".cache" / "corpus"
BANDS = ROOT / "schema" / "registers" / "BANDS_magnitude_bands.csv"
OUT = ROOT / "docs" / "review"
IMG = OUT / "img"
DPI = 110
#: same base the dashboard uses (vfSharePointUrl) — team-openable link built from SRC.library_path
SP_BASE = (
    "https://cgiar.sharepoint.com/sites/Alliance-ClimateActionNetZero/Shared%20Documents/"
    "ClimateActionNetZero/1_Projects/"
)


def sharepoint_url(library_path: str, page: int | None = None) -> str | None:
    from urllib.parse import quote

    if not library_path:
        return None
    url = SP_BASE + "/".join(quote(part) for part in library_path.split("/"))
    return f"{url}#page={page}" if page else url


MARGIN = 28  # pt around the quote block


def _j(s: str) -> dict:
    try:
        return json.loads(s) if s else {}
    except json.JSONDecodeError:
        return {}


VONT = ROOT / "schema" / "registers" / "VONT_variable_ontology.csv"
_STRENGTH = {
    "slight": "by a small amount",
    "moderate": "by a moderate amount",
    "strong": "by a large amount",
}
_DESIGN = {
    "meta_analysis": "a pooled result across many studies (meta-analysis)",
    "systematic_review": "a systematic review of other studies",
    "review": "a review citing other studies",
    "rct": "a randomised trial",
    "quasi_experimental": "a controlled comparison (not randomised)",
    "observational": "an observational study (measured, no experimental control)",
    "case_study": "a single case study",
    "model": "a modelled (simulated) result",
    "expert": "an expert statement",
    "practitioner_rating": "a practitioner's rating on a fixed scale (WOCAT compiler)",
}
_SIG = {
    "sig": "statistically significant",
    "ns": "NOT statistically significant",
    "not_reported": "significance not reported",
}
_BASIS = {
    "primary_measured": "measured by the authors themselves",
    "primary_measurement": "measured by the authors themselves",
    "table": "read from a table in the paper",
    "figure_read": "read off a figure",
    "cited_secondary": "cited by the authors from another study (not their own measurement)",
    "expert_assertion": "asserted by the authors without a measurement",
    "modelled": "produced by a model, not measured",
}
_SCOPE = {
    "practice_technology": "about the practice in general",
    "species_specific": "about one species only",
    "crop_specific": "about one crop only",
}
_ROLE = {
    "nbs_effect": "an EFFECT of the practice on people or land (routed to relevant effect tables by the variable crosswalk)",
    "asset_vulnerability": "DAMAGE to the works themselves by a hazard (asset threat)",
    "operational_risk": "an enabling / implementation factor (next-steps guidance, not an effect)",
    "structural_suitability": "a condition for where the practice can be established (suitability table)",
}
_INCOME = {
    "low": "low-income",
    "lower_middle": "lower-middle-income",
    "upper_middle": "upper-middle-income",
    "high": "high-income",
    "lic_lmic": "low / lower-middle-income",
    "mixed": "mixed-income",
}


FAM = ROOT / "schema" / "registers" / "FAM_family_registry.csv"


def _families(path: Path = FAM) -> dict[str, str]:
    """family id → 'name; name' of its sub-practices (what the practice actually is)."""
    out: dict[str, list[str]] = {}
    try:
        for r in csv.DictReader(path.open(encoding="utf-8")):
            fid = (r.get("suitability_family_id") or "").strip()
            if fid and r.get("name"):
                out.setdefault(fid, []).append(r["name"].strip())
    except OSError:
        pass
    return {k: "; ".join(v) for k, v in out.items()}


def _labels(path: Path = VONT) -> dict[str, str]:
    try:
        return {
            r["canonical_variable_id"]: r["label"]
            for r in csv.DictReader(path.open(encoding="utf-8"))
        }
    except OSError:
        return {}


def _num(rel: dict) -> str:
    unit = str(rel.get("unit") or "").replace("_per_", " per ").replace("_", " ")
    m = rel.get("magnitude")
    lo, hi = rel.get("magnitude_low"), rel.get("magnitude_high")
    met = str(rel.get("metric") or "")
    if met == "contrast" and rel.get("value_with") is not None:
        return f"{rel.get('value_with')} with the practice vs {rel.get('value_without')} without ({unit})".strip()
    if met == "complete_contrast":
        return "an all-or-nothing contrast (e.g. a harvest only with the practice)"
    if met == "ordinal_rating":
        v = rel.get("source_scale_value")
        return (
            f"rated {v} on the compiler's −3…+3 scale"
            if v is not None
            else "a compiler rating"
        )
    if met == "pct_change" and m is not None:
        return f"a change of {m} %"
    if m is not None:
        return f"{m} {unit}".strip()
    if lo is not None or hi is not None:
        return f"{lo}–{hi} {unit}".strip()
    if met == "narrative":
        return "stated in words only, no number"
    return ""


XW = ROOT / "schema" / "registers" / "XW_target_crosswalk.csv"
T5 = ROOT / "schema" / "T5_opportunity_space.csv"
_PROX = {
    "direct": "direct",
    "proxy": "as a proxy, weight ×0.7",
    "component": "as a component, weight ×0.7",
}


def _routes(path: Path = XW) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    try:
        for r in csv.DictReader(path.open(encoding="utf-8")):
            out.setdefault(r["ev_variable"], []).append(r)
    except OSError:
        pass
    return out


def _t5_labels(path: Path = T5) -> dict[str, str]:
    try:
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        lab = next(
            (
                c
                for c in ("ttl_priority_label", "label", "name")
                if rows and c in rows[0]
            ),
            None,
        )
        return (
            {r["variable_id"]: (r.get(lab) or r["variable_id"]) for r in rows}
            if lab
            else {}
        )
    except (OSError, KeyError):
        return {}


#: PICOS (locked, AGENTS "the NbS practice must be EVIDENCED in the source"): practice
#: keywords per NbS, used for an ADVISORY "is the practice named in the quote?" test. A
#: miss is not proof of a wrong tag (the practice may be named elsewhere in the paper) —
#: it tells the reviewer to look.
_PRACTICE_WORDS = {
    "agroforestry": r"agro-?forest|agro-?silvo|silvo-?(pastor|arable|cultur)|parkland|shade tree|shaded (coffee|cocoa)|live fence|windbreak|shelterbelt|alley crop|home-?garden|farmer[- ]managed natural regeneration|\bFMNR\b|scattered tree|tree[s]? on farm|intercrop",
    "water_harvesting_conservation": r"water harvest|rain-?water|\bza[iï]\b|tassa|demi-?lune|bund|terrac|check dam|farm pond|percolation|sand dam|subsurface dam|cistern|tank|runoff|run-?on|mulch|conservation agricultur|no-?till|minimum tillage|reduced tillage|tied ridg|contour|trench|banquette|jessour|spate",
    "forest_restoration": r"restorat|reforest|afforest|regenerat|\bANR\b|tree planting|planted forest|enrichment planting|community forest|forest protect|exclosure|rewild",
    "mangrove_restoration": r"mangrove|\bEMR\b|tidal re-?establish|hydrological restoration|avicennia|rhizophora|sonneratia",
    "riparian_buffer": r"riparian|buffer strip|vegetat(ed|ive) (filter|buffer)|streamside|stream-?bank|filter strip",
    "wetland_management": r"wetland|peat-?land|re-?wetting|marsh|floodplain|drainage block|re-?flood|constructed wetland",
}


def _practice_named(r: dict, rel: dict, ctx: dict, fams: dict[str, str]) -> bool | None:
    pat = _PRACTICE_WORDS.get(r["nbs_id"])
    hay = " ".join(
        str(x or "")
        for x in (
            r.get("quote"),
            r.get("raw_name"),
            rel.get("outcome_raw"),
            ctx.get("note"),
        )
    )
    fam_words = [
        w
        for w in re.split(
            r"[^A-Za-z]+", fams.get(r.get("suitability_family_id") or "", "")
        )
        if len(w) > 5
    ]
    if pat and re.search(pat, hay, re.I):
        return True
    if fam_words and any(re.search(re.escape(w), hay, re.I) for w in fam_words):
        return True
    return False if pat else None


def _named_note(named: bool | None) -> str:
    if named:
        return "the practice is named in the quote"
    if named is False:
        return "the practice is NOT named in the quoted text — check the source before keeping this tag"
    return ""


def picos(
    r: dict,
    rel: dict,
    ctx: dict,
    labels: dict[str, str],
    fams: dict[str, str],
    src: dict,
) -> dict:
    """The five PICOS elements spelled out for the reviewer, with the gaps named.

    Locked discipline: the practice (Intervention) must be evidenced IN the source, and a
    comparator must be identifiable — an effect with nothing to compare against is not an
    effect. Each element can be flagged by the reviewer on the page."""
    role = r["use_role"]
    # P — population / setting
    pop = []
    c = ctx.get("country")
    if c:
        pop.append(", ".join(c) if isinstance(c, list) else str(c))
    elif src.get("study_country"):
        pop.append(
            str(src["study_country"]).replace("|", ", ")
            + " (from the source record, not the quote)"
        )
    if ctx.get("income_group") in _INCOME:
        pop.append(_INCOME[ctx["income_group"]])
    if ctx.get("farming_system"):
        pop.append(str(ctx["farming_system"]).replace("_", " ") + " farming")
    if r.get("claim_scope") == "species_specific":
        pop.append(f"ONE SPECIES only: {r.get('taxon') or 'unnamed'}")
    elif r.get("claim_scope") == "crop_specific":
        pop.append(f"ONE CROP only: {r.get('taxon') or 'unnamed'}")
    # I — intervention
    fid = r.get("suitability_family_id") or ""
    inter = r["nbs_id"].replace("_", " ")
    if fid and not fid.endswith("__cross_family"):
        inter += " → " + fid.split("__", 1)[-1].replace("_", " ")
        if fams.get(fid):
            inter += f" ({fams[fid]})"
    else:
        inter += " (no sub-practice stated — pooled across the NbS)"
    named = _practice_named(r, rel, ctx, fams)
    described = str(ctx.get("practice_as_described") or "").strip()
    if described:
        inter += f" — the source calls it: “{described}”"
    # C — comparator
    comp = []
    if rel.get("value_without") is not None:
        comp.append(
            f"without the practice: {rel.get('value_without')} {str(rel.get('unit') or '').replace('_', ' ')}".strip()
        )
    if ctx.get("comparator") == "existing_forest":
        comp.append("EXISTING forest / forest loss, not a restoration")
    if ctx.get("comparator") == "existing_wetland":
        comp.append("EXISTING wetlands, not a restoration")
    raw = str(rel.get("outcome_raw") or "")
    if not comp and re.search(
        r"\bvs\.?\b|versus|compared (with|to)|control", raw, re.I
    ):
        comp.append(raw)
    if not comp and re.search(
        r"\bvs\.?\b|versus|compared (with|to)|\bcontrol\b",
        str(r.get("quote") or ""),
        re.I,
    ):
        comp.append(
            "stated in the quote (see the words 'vs' / 'control') but not captured in the coded fields"
        )
    # O — outcome
    out = [labels.get(r["variable"], r["variable"].replace("_", " "))]
    if raw:
        out.append(raw)
    n = _num(rel)
    if n:
        out.append(n)
    if rel.get("significance") in _SIG:
        out.append(_SIG[rel["significance"]])
    # S — study design
    st = []
    if rel.get("design") in _DESIGN:
        st.append(_DESIGN[rel["design"]])
    if r.get("claim_basis") in _BASIS:
        st.append(_BASIS[r["claim_basis"]])
    if src.get("method_type"):
        st.append("source type: " + str(src["method_type"]).replace("_", " "))
    if src.get("benchmark_tier"):
        st.append(f"source tier: {src['benchmark_tier']}")
    gaps = []
    if not pop:
        gaps.append("P")
    if named is False:
        gaps.append("I")
    if not comp and role in ("nbs_effect", "asset_vulnerability"):
        gaps.append("C")
    if not raw:
        gaps.append("O")
    if not st:
        gaps.append("S")
    return {
        "P": "; ".join(pop) or "not recorded — where/for whom does this hold?",
        "I": inter,
        "I_named": named,
        "I_note": (
            _named_note(named)
            if described
            else (
                "the source's own description of the practice is NOT captured — judge the "
                "practice from the quote. " + _named_note(named)
            ).strip()
        ),
        "C": "; ".join(comp)
        or (
            "NOT recorded — an effect needs something to compare against; read the quote and say what the control was"
            if role in ("nbs_effect", "asset_vulnerability")
            else "not applicable to this kind of unit"
        ),
        "O": " — ".join(out),
        "S": "; ".join(st) or "not recorded",
        "gaps": gaps,
    }


RECIPES = ROOT / "schema" / "recipes"
COMPARATOR_POLICY = ROOT / "schema" / "lookups" / "comparator_policy.csv"
_T_FILE_LABEL = {
    "T3_nbs_hazard_farming": "T3 — hazard table",
    "T6_nbs_scorecard": "T6 — NbS scorecard",
    "T6E_economic_profile": "T6E — NbS economic profile",
}


def _pool_sentence(n_units: int, n_sources: int) -> str:
    """How big the row's pool is, in the engine's own terms (review theme 5)."""
    u = f"{n_units} unit{'s' if n_units != 1 else ''}"
    m = f"{n_sources} source{'s' if n_sources != 1 else ''}"
    tail = (
        " — the weighting counts sources, not units, so several findings from one paper "
        "do not multiply its say."
        if n_units > n_sources
        else "."
    )
    return f" That row draws on {u} from {m}{tail}"


def _placements(
    sources: dict[str, str] | None = None,
    *,
    recipe_dirs=None,
) -> dict[str, list[dict[str, str]]]:
    """evidence_id → the generated rows it is actually in. Ground truth beats a predicted
    route: a unit can route somewhere and still land nowhere (kept out of a roll-up by the
    comparator policy, or in a family row that needs two independent sources).

    Each placement also carries how big the row's pool is — units and distinct sources —
    because several data points from one paper are not several findings (review theme 5,
    Pete 2026-10-12); the engine weights by source, and the page has to say so."""
    sources = sources or {}
    out: dict[str, list[dict[str, str]]] = {}
    for d in sorted(RECIPES.glob("*")) if recipe_dirs is None else recipe_dirs:
        for stem, label in _T_FILE_LABEL.items():
            f = d / f"{stem}.csv"
            if not f.exists():
                continue
            with f.open(newline="", encoding="utf-8") as fh:
                for r in csv.DictReader(fh):
                    try:
                        ids = json.loads(r.get("evidence_ids") or "[]")
                    except json.JSONDecodeError:
                        continue
                    scope = (r.get("scope_id") or "").strip()
                    where = {
                        "table": label,
                        "record_id": r.get("record_id", ""),
                        "family": (r.get("suitability_family_id") or "").strip(),
                        "scope": scope,
                        "role": (r.get("risk_role") or "").strip(),
                        "pool": _pool_sentence(
                            len(ids), len({sources.get(i, i) for i in ids})
                        ),
                    }
                    for eid in ids:
                        out.setdefault(eid, []).append(where)
    return out


def _comparator_policy(
    path: Path = COMPARATOR_POLICY,
) -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = {}
    try:
        for r in csv.DictReader(path.open(encoding="utf-8")):
            out[(r["nbs_id"].strip(), r["comparator"].strip())] = r
    except OSError:
        pass
    return out


def placement_lines(
    r: dict,
    ctx: dict,
    places: list[dict[str, str]],
    pol: dict[tuple[str, str], dict[str, str]],
) -> tuple[list[str], str]:
    """(lines naming the rows this unit is in, reason when it is in none)."""
    lines = []
    for w in places:
        scope = f", {w['scope']} rows only" if w["scope"] else ""
        fam = (
            f"the {w['family'].split('__', 1)[-1].replace('_', ' ')} family row"
            if w["family"]
            else "the NbS roll-up row"
        )
        role = " (asset threat)" if w["role"] == "asset_threat" else ""
        pool = str(w.get("pool") or "")
        lines.append(f"{w['table']}: {w['record_id']} — {fam}{scope}{role}.{pool}")
    if lines:
        return lines, ""
    if (r.get("review_state") or "") == "dropped":
        return [], "It was dropped in review, so it sets no score."
    comp = str(ctx.get("comparator") or "")
    pr = pol.get((r["nbs_id"], comp)) if comp else None
    if pr and (pr.get("rollup_included") or "").strip().lower() != "true":
        home = (pr.get("home_family") or "").split("__", 1)[-1].replace("_", " ")
        return [], (
            f"It is '{comp.replace('_', ' ')}' evidence, so it is deliberately kept out of the NbS roll-up "
            f"and belongs only in the {home} family row — and that row is not generated yet, because a family "
            "row needs at least two independent sources. Right now this unit sets no score anywhere."
        )
    return [], (
        "It is not in any generated row yet — the cell it would join needs at least two independent "
        "sources, or a gate (stated hazard, income band, significance) kept it out."
    )


def _now(r, ctx, places, pol) -> dict:
    now, none_reason = placement_lines(r, ctx, places or [], pol or {})
    return {"now": now, "none_reason": none_reason}


def feeds_line(
    r: dict,
    ctx: dict,
    routes: dict[str, list[dict]],
    t5: dict[str, str],
    places: list[dict[str, str]] | None = None,
    pol: dict[tuple[str, str], dict[str, str]] | None = None,
) -> dict:
    """Which generated table(s) and cell(s) this unit lands in, and what question each
    one answers. A hazard finding legitimately feeds BOTH tables (method §4, 'many-to-many
    is allowed and expected': flood_hazard → T3 flood + T6 flood_hazard) because they are
    read by different modules at different granularity — they are never added together."""
    role, var = r["use_role"], r["variable"]
    hz = (ctx.get("hazard_type") or "").replace("_", " ")
    if role == "asset_vulnerability":
        return {
            "lead": "",
            **_now(r, ctx, places, pol),
            "items": [
                f"T3 — hazard table, asset-threat row for {hz or 'the hazard'}: can {hz or 'the hazard'} damage the works themselves? Read by the Module 2b project-risk screen, never by the livelihood cells."
            ],
        }
    if role == "operational_risk":
        return {
            "lead": "",
            **_now(r, ctx, places, pol),
            "items": [
                "No table cell. This is an enabling / implementation factor — it informs Module 6 next-steps and the Module 2b operational-risk filter, and never sets a score."
            ],
        }
    if role == "structural_suitability":
        return {
            "lead": "",
            **_now(r, ctx, places, pol),
            "items": [
                f"T4 — suitability table, variable '{var}' for the family above: where the practice can physically establish."
            ],
        }
    rs = routes.get(var) or []
    if not rs:
        return {
            "lead": "",
            **_now(r, ctx, places, pol),
            "items": [
                f"Nothing yet — '{var}' has no crosswalk route to T3 or T6, so this unit currently sets no score (routing / ontology decision pending)."
            ],
        }
    t3 = [x for x in rs if x["target_table"] == "T3"]
    t6 = [x for x in rs if x["target_table"] == "T6"]
    items: list[str] = []
    n_dest = 0
    # T3 — mirrors the engine's gate (cell_synthesis.gather): a stated hazard selects ONE
    # cell; with no stated hazard a single direct route still lands, several land nowhere.
    if t3:
        hz_key = (ctx.get("hazard_type") or "").strip()
        chosen = None
        if hz_key:
            m = [x for x in t3 if x["target_key"] == hz_key]
            chosen = (m[0], "the unit states that hazard") if m else None
            if not m:
                items.append(
                    f"T3 — no cell: the stated hazard '{hz_key.replace('_', ' ')}' has no route from '{var}'."
                )
        elif len(t3) == 1 and (t3[0].get("proximity") or "direct") == "direct":
            chosen = (t3[0], "the variable is itself a hazard variable")
        else:
            items.append(
                "T3 — no hazard cell: the unit names no hazard, so it is not hazard-year evidence."
            )
        if chosen:
            x, why = chosen
            key = x["target_key"].replace("_", " ")
            prox = x.get("proximity") or "direct"
            n_dest += 1
            items.append(
                f"T3 — hazard table, the {key} cell for this NbS and farming system: does the practice reduce the impact of {key} on rural livelihoods? "
                f"Counted {_PROX.get(prox, prox)}, because {why}. Read by Module 5 (NbS response) and the M2b screen."
            )
    for x in t6:
        key = t5.get(x["target_key"], x["target_key"]).strip()
        prox = x.get("proximity") or "direct"
        n_dest += 1
        items.append(
            f"T6 — NbS scorecard, the '{key}' priority: how this NbS scores for a Task Team Leader who prioritises {key.lower()}. "
            f"Counted {_PROX.get(prox, prox)}. Read by the Module 4 hotspot / NbS comparison, one row per NbS (no farming-system split)."
        )
    lead = (
        "The same finding answers two different questions, so it is used in both tables. They are never added together:"
        if n_dest > 1
        else ""
    )
    now, none_reason = placement_lines(r, ctx, places or [], pol or {})
    return {"lead": lead, "items": items, "now": now, "none_reason": none_reason}


def described_line(ctx: dict, role: str) -> str:
    """What the SOURCE says was done, in its own words (review theme 2, Pete 2026-10-12).

    Supplemental irrigation counted as water harvesting, a plantation counted as forest
    restoration and a protected area counted as restoration all got through because the
    practice test was inferred from our tag instead of read from the paper. The reviewer
    needs the paper's own description in front of them."""
    d = str(ctx.get("practice_as_described") or "").strip()
    if d:
        return f"The source describes what was done as: “{d}”."
    if role in ("nbs_effect", "asset_vulnerability"):
        return (
            "The source's own description of the practice was not captured for this unit "
            "(it is required from ruleset v1.6.9 on) — read the quote and say whether what "
            "was measured really is this practice."
        )
    return ""


def identity(
    r: dict,
    ctx: dict,
    labels: dict[str, str],
    fams: dict[str, str],
    routes: dict[str, list[dict]],
    t5: dict[str, str],
    placements: list[dict] | None = None,
) -> dict:
    """What a reviewer must see first (Pete 2026-10-26): the practice, the outcome variable and
    the table(s) the unit feeds — each a short label.

    Plain words (Pete 2026-11-09, "what does 'no table (dropped or unrouted)' mean?"): the
    labels name the rating, and an unused unit says WHY it is unused, in one sentence."""
    nbs = r["nbs_id"].replace("_", " ")
    fam = r.get("suitability_family_id") or ""
    fam_lbl = fam.split("__")[-1].replace("_", " ")
    practice = nbs + (
        f" → {fam_lbl}" if fam and not fam.endswith("cross_family") else ""
    )
    var = labels.get(r["variable"], r["variable"].replace("_", " "))
    role = r.get("use_role", "")
    hz = str(ctx.get("hazard_type") or "")
    hz_lbl = hz.replace("_", " ")
    tables: list[str] = []
    if role == "structural_suitability":
        tables = ["Where the practice can go (T4 suitability)"]
    elif role == "operational_risk":
        tables = ["Risk to the investment: enabling conditions (M2b)"]
    elif role == "asset_vulnerability":
        tables = [f"Risk to the investment from {hz_lbl or 'a hazard'} (T3)"]
    else:
        for x in routes.get(r["variable"], []):
            tag = "" if x.get("proximity") == "direct" else " (indirect measure)"
            if x.get("target_table") == "T6":
                key = t5.get(x["target_key"], x["target_key"].replace("_", " "))
                tables.append(f"Scorecard: {key} (T6){tag}")
            elif x.get("target_table") == "T3" and x.get("target_key") == hz:
                tables.append(f"Livelihood rating for {hz_lbl} (T3){tag}")
    tables = list(dict.fromkeys(tables))
    placed = bool(placements)
    reason = ""
    if (r.get("review_state") or "") == "dropped":
        reason = "Not used in any rating: it was removed in an earlier review."
    elif role in ("structural_suitability", "operational_risk"):
        reason = ""  # T4 / M2b are not built from generated T3/T6 rows
    elif not routes.get(r["variable"]):
        reason = (
            f"Not used in any rating: what it measures ({var}) is not yet linked "
            "to any scorecard or hazard row."
        )
    elif not tables:
        reason = (
            "Not used in any rating: what it measures only feeds hazard ratings, and "
            "the study does not name the hazard."
        )
    elif not placed:
        reason = (
            "Not used in a rating yet: it has a place to go but was held out "
            "(open 'Where this lands' below for the rule that kept it out)."
        )
    return {
        "practice": practice,
        "variable": var,
        "tables": tables if (placed or role != "nbs_effect") and not reason else [],
        "not_used_reason": reason,
        "as_of": date.today().isoformat(),
    }


def practice_line(r: dict, fams: dict[str, str]) -> str:
    nbs = r["nbs_id"].replace("_", " ")
    fid = r.get("suitability_family_id") or ""
    if not fid or fid.endswith("__cross_family"):
        return f"Practice: {nbs} (no sub-practice stated in the source — pooled across the whole NbS)."
    short = fid.split("__", 1)[-1].replace("_", " ")
    names = fams.get(fid)
    return f"Practice: {nbs} → {short}" + (f" ({names})" if names else "") + "."


def plain_words(
    r: dict,
    rel: dict,
    ctx: dict,
    labels: dict[str, str],
    fams: dict[str, str] | None = None,
    routes: dict[str, list[dict]] | None = None,
    t5: dict[str, str] | None = None,
    places: list[dict[str, str]] | None = None,
    pol: dict[tuple[str, str], dict[str, str]] | None = None,
    bands: list[dict] | None = None,
    sense: dict | None = None,
) -> dict:
    """Plain-English sentences for a reviewer: what the unit claims, how it was
    established, and in what context. The codes stay in the JSON for the record."""
    var = labels.get(r["variable"], r["variable"].replace("_", " "))
    practice = r["nbs_id"].replace("_", " ")
    d = str(rel.get("direction") or "")
    hazard_var = r["variable"].endswith("_hazard")
    sense = load_sense() if sense is None else sense
    high_is_bad = (sense.get(r["variable"]) or {}).get("high_is") == "bad"
    if r["use_role"] == "asset_vulnerability":
        hz = (ctx.get("hazard_type") or "the hazard").replace("_", " ")
        verb = {
            "positive": f"is damaged by {hz}",
            "negative": f"withstands {hz}",
            "none": f"is not clearly affected by {hz}",
        }.get(d, f"— {d}")
        claim = f"The works of {practice} {verb}"
    elif d in ("positive", "negative", "none"):
        if hazard_var:
            verb = {
                "negative": "REDUCES the impact of",
                "positive": "WORSENS the impact of",
                "none": "has NO clear effect on",
            }[d]
            obj = var.replace(" hazard", "").replace(" risk", "")
        elif high_is_bad:
            verb = {
                "negative": "REDUCES (a benefit)",
                "positive": "INCREASES (a harm)",
                "none": "has NO clear effect on",
            }[d]
            obj = var
        else:
            verb = {
                "positive": "INCREASES",
                "negative": "DECREASES",
                "none": "has NO clear effect on",
            }[d]
            obj = var
        if rel.get("framing") == "loss":
            verb = verb.replace(" (a benefit)", "").replace(" (a harm)", "")
            claim = (
                f"LOSING {practice} {verb} {obj} "
                "(so the practice's presence does the reverse)"
            )
        else:
            claim = f"{practice.capitalize()} {verb} {obj}"
    else:
        claim = d or "(no direction coded)"
    bits = []
    if d in ("positive", "negative") and rel.get("strength_class") in _STRENGTH:
        bits.append(_STRENGTH[rel["strength_class"]])
    elif d in ("positive", "negative"):
        bits.append("size not stated")
    n = _num(rel)
    if n:
        bits.append(n)
    if rel.get("significance") in _SIG:
        bits.append(_SIG[rel["significance"]])
    claim_sentence = claim + (" — " + "; ".join(bits) if bits else "") + "."
    how = []
    if rel.get("design") in _DESIGN:
        how.append(_DESIGN[rel["design"]])
    if r.get("claim_basis") in _BASIS:
        how.append(_BASIS[r["claim_basis"]])
    if r.get("claim_scope") in _SCOPE:
        how.append(
            _SCOPE[r["claim_scope"]]
            + (f" ({r.get('taxon')})" if r.get("taxon") else "")
        )
    how_sentence = ("This is " + "; ".join(how) + ".") if how else ""
    where = []
    if ctx.get("hazard_type"):
        hz = str(ctx["hazard_type"]).replace("_", " ")
        sev = ctx.get("hazard_severity")
        if sev and sev != "unspecified":
            where.append(
                f"under a {hz} the authors call {sev}"
                + (
                    f" (their words: “{ctx.get('severity_cue')}”)"
                    if ctx.get("severity_cue")
                    else ""
                )
            )
        else:
            where.append(f"under {hz} (intensity not characterised by the authors)")
    if ctx.get("country"):
        c = ctx["country"]
        where.append("in " + (", ".join(c) if isinstance(c, list) else str(c)))
    if ctx.get("income_group") in _INCOME:
        where.append(f"a {_INCOME[ctx['income_group']]} setting")
    if ctx.get("farming_system"):
        where.append(f"farming system: {str(ctx['farming_system']).replace('_', ' ')}")
    if ctx.get("comparator") == "existing_forest":
        where.append(
            "measured on EXISTING forest (or forest loss), not on a restoration"
        )
    if ctx.get("comparator") == "existing_wetland":
        where.append("measured on EXISTING wetlands, not on a restoration")
    where_sentence = ("Context: " + "; ".join(where) + ".") if where else ""
    compared = str(rel.get("outcome_raw") or "").strip()
    return {
        "direction_reads": direction_reads(
            r["variable"], d, r["use_role"], str(rel.get("framing") or ""), sense=sense
        )["text"],
        "practice": practice_line(r, fams or {}),
        "described": described_line(ctx, r["use_role"]),
        "band": check_bands.explain_unit(r, bands or []),
        "feeds": feeds_line(r, ctx, routes or {}, t5 or {}, places, pol),
        "compared": ("What the paper compared: " + compared + ".") if compared else "",
        "role": _ROLE.get(r["use_role"], r["use_role"]),
        "claim": claim_sentence,
        "how": how_sentence,
        "where": where_sentence,
    }


def _norm_word(w: str) -> str:
    # transliterate accents (très -> tres) before dropping non-alphanumerics, so native-language
    # quotes keep their letters
    w = unicodedata.normalize("NFKD", w).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^0-9a-z]", "", w.lower())


def _quote_word_rects(page, quote: str) -> list:
    """Rects of the page words that spell out the quote, in reading order; [] if not found."""
    words = page.get_text("words")  # (x0, y0, x1, y1, word, block, line, word_no)
    # match on the alphanumeric character stream: the words list and get_text() can split
    # tokens differently ("intensity≤35%" vs "intensity ≤35%"), characters agree
    stream, owner = [], []
    for i, w in enumerate(words):
        t = _norm_word(w[4])
        stream.append(t)
        owner.extend([i] * len(t))
    text = "".join(stream)
    target = _norm_word(quote)
    if len(target) < 20:  # too short to bind to one place on the page
        return []
    # highlight every occurrence: a repeated run (header, table value) is shown, not guessed
    hit: set[int] = set()
    at = text.find(target)
    while at >= 0:
        hit.update(owner[at : at + len(target)])
        at = text.find(target, at + 1)
    return [fitz.Rect(words[i][:4]) for i in sorted(hit)]


def render_crop(pdf: Path, page_no: int, quote: str, dest: Path) -> str:
    """Crop the cited page around the quote (highlighted); fall back to the whole page."""
    doc = fitz.open(pdf)
    if page_no < 1 or page_no > len(doc):
        return "page out of range"
    page = doc[page_no - 1]
    q = re.sub(r"\s+", " ", quote).strip()
    # Quotes are sliced from page.get_text(), so their words are the page's words in order:
    # highlight the whole matched word run. (The earlier probe search marked only the first
    # and last ~50 characters and could hit a repeated phrase elsewhere — Pete, 2026-11-03.)
    rects = _quote_word_rects(page, q)
    if not rects:
        for probe in (q[:50], q[-50:], q[:30]):
            if len(probe) < 12:
                continue
            hits = page.search_for(probe)
            if hits:
                rects += hits
                if len(rects) >= 2 or probe == q[:30]:
                    break
    note = "quote highlighted"
    if rects:
        r = rects[0]
        for x in rects[1:]:
            r |= x
        clip = fitz.Rect(
            max(page.rect.x0, r.x0 - MARGIN),
            max(page.rect.y0, r.y0 - MARGIN * 3),
            min(page.rect.x1, r.x1 + MARGIN),
            min(page.rect.y1, r.y1 + MARGIN * 3),
        )
        # widen to the full text width so the sentence context stays readable
        clip.x0, clip.x1 = page.rect.x0 + 20, page.rect.x1 - 20
        for h in rects:
            page.add_highlight_annot(h)
        pix = page.get_pixmap(dpi=DPI, clip=clip)
    else:
        note = "quote not located in the text layer — whole page shown"
        pix = page.get_pixmap(dpi=72)
    dest.parent.mkdir(parents=True, exist_ok=True)
    pix.save(dest)
    return note


def _section_probes(quote: str) -> list[str]:
    """Text to look for in the PDF version of a transcript-quoted source (WOCAT): the
    compiler's comment first (printed verbatim on the sheet), then the field label."""
    probes = []
    m = re.search(r"comment:\s*(.+)$", quote, re.S)
    if m:
        probes.append(m.group(1).strip())
    for line in quote.splitlines():
        lab = re.match(r"\s*-\s*([a-z0-9_]+)\s*:", line)
        if lab:
            probes.append(lab.group(1).replace("_", " "))
    probes.append(quote)
    return [x for x in probes if len(_norm_word(x)) >= 12]


def find_page_by_text(pdf: Path, quote: str) -> tuple[int, str]:
    """(1-based page, probe) where the PDF prints the quoted text; (0, "") if nowhere.
    For sources quoted from a transcript by section (no page number), so the reviewer
    still gets the printed page beside the claim (Pete 2026-11-09: "there is no image")."""
    doc = fitz.open(pdf)
    streams = [_norm_word(pg.get_text()) for pg in doc]
    for probe in _section_probes(quote):
        target = _norm_word(probe)[:80]
        for i, txt in enumerate(streams):
            if target and target in txt:
                return i + 1, probe
    return 0, ""


def _build_units(item_rows, ev, *, schema, corpus, image_dir, recipe_dirs):
    items = {r["evidence_id"]: (r.get("question") or "") for r in item_rows}
    # optional ai_decision / ai_reason columns: what the AI proposed, so a reviewer who
    # agrees can reject without re-picking the reason (Pete 2026-10-26)
    ai_of = {
        r["evidence_id"]: {
            "decision": (r.get("ai_decision") or "").strip(),
            "reason": (r.get("ai_reason") or "").strip(),
        }
        for r in item_rows
        if (r.get("ai_decision") or "").strip()
    }
    registers = schema / "registers"
    with (registers / SRC.name).open(encoding="utf-8") as stream:
        src = {r["source_id"]: r for r in csv.DictReader(stream)}
    units = []
    missing = []
    labels = _labels(registers / VONT.name)
    fams = _families(registers / FAM.name)
    routes = _routes(registers / XW.name)
    pol = _comparator_policy(schema / "lookups" / COMPARATOR_POLICY.name)
    t5 = _t5_labels(schema / T5.name)
    bands = load_bands(registers / BANDS.name)
    sense = read_sense(schema / "lookups/variable_direction_sense.csv")
    places = _placements(
        {k: v["source_id"] for k, v in ev.items()}, recipe_dirs=recipe_dirs
    )
    for eid, question in items.items():
        r = ev.get(eid)
        if not r:
            missing.append(eid)
            continue
        rel, ctx = _j(r.get("relationship", "")), _j(r.get("context", ""))
        s_rec = src.get(r["source_id"], {})
        crop, crop_note = None, "no cached PDF"
        pdf = corpus / f"{r['source_id']}.pdf"
        page = int(r["page"]) if (r.get("page") or "").isdigit() else 0
        if pdf.exists() and page:
            dest = image_dir / f"{eid}.png"
            crop_note = render_crop(pdf, page, r.get("quote", ""), dest)
            if crop_note != "page out of range":
                crop = f"review/img/{eid}.png"
        elif (r.get("locator_type") or "") == "section":
            crop_note = f"transcript section {r.get('locator')} (no page image)"
            if pdf.exists():
                found, probe = find_page_by_text(pdf, r.get("quote", ""))
                if found:
                    dest = image_dir / f"{eid}.png"
                    note = render_crop(pdf, found, probe, dest)
                    if note != "page out of range":
                        crop = f"review/img/{eid}.png"
                        page = found
                        crop_note = (
                            f"Page {found} of the source PDF. Highlighted: the text this "
                            "finding was coded from."
                            if note == "quote highlighted"
                            else f"Page {found} of the source PDF. {note}"
                        )
        units.append(
            {
                "evidence_id": eid,
                "source_id": r["source_id"],
                "citation": s_rec.get("citation", ""),
                "benchmark_tier": s_rec.get("benchmark_tier", ""),
                "nbs_id": r["nbs_id"],
                "use_role": r["use_role"],
                "variable": r["variable"],
                "suitability_family_id": r.get("suitability_family_id", ""),
                "claim_scope": r.get("claim_scope", ""),
                "claim_basis": r.get("claim_basis", ""),
                "page": page or r.get("page"),
                "locator": r.get("locator", ""),
                "quote": r.get("quote", ""),
                "relationship": {
                    k: rel.get(k)
                    for k in (
                        "direction",
                        "strength_class",
                        "metric",
                        "magnitude",
                        "magnitude_low",
                        "magnitude_high",
                        "value_with",
                        "value_without",
                        "unit",
                        "design",
                        "significance",
                        "outcome_raw",
                    )
                    if rel.get(k) not in (None, "")
                },
                "context": {
                    k: ctx.get(k)
                    for k in (
                        "hazard_type",
                        "hazard_severity",
                        "severity_cue",
                        "country",
                        "income_group",
                        "farming_system",
                        "comparator",
                        "practice_as_described",
                        "note",
                    )
                    if ctx.get(k) not in (None, "")
                },
                "question": question,
                "ai": ai_of.get(eid),
                "crop": crop,
                "crop_note": crop_note,
                "pdf_url": sharepoint_url(s_rec.get("library_path", ""), page or None),
                "plain": plain_words(
                    r,
                    rel,
                    ctx,
                    labels,
                    fams,
                    routes,
                    t5,
                    places.get(eid) or [],
                    pol,
                    bands,
                    sense,
                ),
                "picos": picos(r, rel, ctx, labels, fams, s_rec),
                "identity": identity(
                    r, ctx, labels, fams, routes, t5, places.get(eid) or []
                ),
                "library_path": s_rec.get("library_path", ""),
                "cited_original": (r.get("lineage_of") or "").strip()
                if r.get("claim_basis") == "cited_secondary"
                else "",
            }
        )
    return units, missing


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("batch_id")
    ap.add_argument("--title", required=True)
    ap.add_argument("--items", required=True, type=Path)
    ap.add_argument("--notes", default="")
    ap.add_argument("--root", type=Path, default=ROOT, help="Selected data root")
    ap.add_argument("--corpus-dir", type=Path)
    ap.add_argument("--out-dir", type=Path, help="Review output directory")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    schema = a.root / "schema"
    corpus = a.corpus_dir or a.root / ".cache/corpus"
    output = batch_directory(a.root, a.out_dir, corpus)
    recipe_dirs = sorted(p for p in (schema / "recipes").glob("*") if p.is_dir())
    ev_file = schema / "registers" / EV.name
    inputs = ReviewInputs(
        [
            a.items,
            ev_file,
            *(schema / "registers" / p.name for p in (SRC, VONT, FAM, XW, BANDS)),
            schema / T5.name,
            schema / "lookups" / COMPARATOR_POLICY.name,
            schema / "lookups/variable_direction_sense.csv",
            *(
                directory / (stem + ".csv")
                for directory in recipe_dirs
                for stem in _T_FILE_LABEL
            ),
        ]
    )
    with a.items.open(encoding="utf-8", newline="") as stream:
        item_rows = list(csv.DictReader(stream))
    with ev_file.open(encoding="utf-8", newline="") as stream:
        ev = {r["evidence_id"]: r for r in csv.DictReader(stream)}
    crop_ids = []
    for eid in dict.fromkeys(row["evidence_id"] for row in item_rows):
        row = ev.get(eid)
        if row is None:
            continue
        validate_source_id(row["source_id"])
        pdf = corpus / (row["source_id"] + ".pdf")
        inputs.include([pdf])
        if pdf.exists() and (row.get("page") or "").isdigit() and int(row["page"]):
            crop_ids.append(eid)
        elif (
            pdf.exists()
            and (row.get("locator_type") or "") == "section"
            and find_page_by_text(pdf, row.get("quote", ""))[0]
        ):
            crop_ids.append(eid)  # transcript quote: page found by text in the PDF
    n = 0
    missing = []

    def render(stage):
        nonlocal n, missing
        units, missing = _build_units(
            item_rows,
            ev,
            schema=schema,
            corpus=corpus,
            image_dir=stage / "img",
            recipe_dirs=recipe_dirs,
        )
        n = len(units)
        return {
            "batch": {
                "id": a.batch_id,
                "title": a.title,
                "date": date.today().isoformat(),
                "notes": a.notes,
                "n": n,
            },
            "reasons": REASON_CODES,
            "units": units,
        }

    result = publish_batch(
        output, a.batch_id, render, inputs=inputs, crop_ids=crop_ids, dry_run=a.dry_run
    )
    target = (
        str(result) if a.out_dir or a.root != ROOT else f"docs/review/{a.batch_id}.json"
    )
    print(
        f"{n} unit(s) → {target}; missing ids: {missing}"
        + (" (dry run)" if a.dry_run else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
