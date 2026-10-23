"""Deterministic DIRECTION check for effect claims (ruleset v1.6.17, catalogue #37).

`relationship.direction` is on the outcome variable AS NAMED (contract §2.2 rule 1):
`erosion_hazard` + `negative` = erosion went DOWN (a benefit). Coders who think in
"good / bad" flip it, and the engine then scores a benefit as a harm. Meaning per variable
lives in `schema/lookups/variable_direction_sense.csv`.

Structural (fail the build):

* `no_sense`            — an effect variable or crosswalk variable with no sense row
* `polarity_mismatch`   — XW polarity disagrees with the sense table (a high-is-bad
                          outcome routed `same` to a benefit target, or the reverse)

Unit-level (advisory, active `nbs_effect` / `asset_vulnerability` units):

* `cue_not_verbatim`    — `relationship.direction_cue` is not a verbatim slice of the quote
* `missing_cue`         — unit stamped v1.6.17 or later with a direction but no cue
* `cue_word_conflict`   — the cue only has DOWN words and the
                          direction is positive, or only UP words and it is negative, when
                          the cue names the variable's own quantity, on a plainly-named one (not a `*_reduction` / retention / buffering
                          variable, not loss-framed, not a WOCAT rating)

    python3 src/nbs_ruralscan/schema_tools/check_direction.py [EV.csv]
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
import sys
from pathlib import Path

from nbs_ruralscan.recipe.direction_sense import load_sense as _cached_sense

ROOT = Path(__file__).resolve().parents[3]
_EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
_XW = ROOT / "schema" / "registers" / "XW_target_crosswalk.csv"
_SENSE = ROOT / "schema" / "lookups" / "variable_direction_sense.csv"
#: units whose cue wording cannot decide the direction but whose direction was confirmed
#: against the full quote — reviewed, so the lexical rule stays meaningful
_EXCEPTIONS = ROOT / "schema" / "lookups" / "direction_cue_exceptions.csv"


def _exceptions() -> set[str]:
    if not _EXCEPTIONS.exists():
        return set()
    with _EXCEPTIONS.open(newline="", encoding="utf-8") as f:
        return {r["evidence_id"] for r in csv.DictReader(f)}


EFFECT_ROLES = {"nbs_effect", "asset_vulnerability"}
CUE_FROM = (1, 6, 17)
#: targets that are themselves costs: a cost routed to a cost keeps its sign
_COST_TARGETS = re.compile(r"^(cost_|establishment_cost|recurrent_cost)")
#: variables NAMED as the benefit, where "reduced X" means the variable went UP
_BENEFIT_NAMED = re.compile(
    r"(_reduction|_retention|_buffering|_protection|_mitigation|_removal)$"
)
_DOWN = re.compile(
    r"\b(reduc\w*|decreas\w*|lower\w*|less|fewer|declin\w*|fell|drop\w*|diminish\w*|"
    r"mitigat\w*|prevent\w*|curb\w*|minimi[sz]\w*|attenuat\w*|avoid\w*|"
    r"réduit\w*|réduction|diminu\w*|reduj\w*|disminu\w*|menor\w*|menos)\b",
    re.I,
)
_UP = re.compile(
    r"\b(increas\w*|higher|more|greater|rais\w*|rose|ris\w*|boost\w*|enhanc\w*|"
    r"improv\w*|doubl\w*|tripl\w*|gain\w*|augment\w*|aument\w*|mayor\w*|más)\b",
    re.I,
)


#: nouns that reverse a movement word ("reducing yield LOSSES", "less DEFORESTATION")
_REVERSERS = re.compile(
    r"\b(loss\w*|failure\w*|deforest\w*|emission\w*|damage\w*|declin\w*|oscillat\w*|"
    r"deviation\w*|mortality|flux|purchas\w*|infestation|pests?|odds|adverse)\b",
    re.I,
)
_GENERIC = {
    "hazard",
    "outcome",
    "potential",
    "rate",
    "value",
    "risk",
    "index",
    "deficit",
    "productivity",
    "capacity",
    "effect",
    "provision",
    "named",
    "benefit",
    "with",
    "from",
    "more",
    "less",
    "the",
    "and",
    "per",
    "unit",
    "shortage",
    "impact",
}


def _keywords(variable: str) -> set[str]:
    """Words that name the variable's own quantity (id parts + sense `quantity`)."""
    sense = _cached_sense().get(variable) or {}
    words = re.findall(
        r"[a-z]{4,}", (variable + " " + sense.get("quantity", "")).lower()
    )
    return {w[:6] for w in words if w not in _GENERIC}


def _ver(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", v or "")[:3]) or (0,)


def _norm(s: str) -> str:
    """Compare text the way a reader would: NFKC glyphs (ligatures, minus signs), a word
    hyphen-split across a line break re-joined, whitespace collapsed, case folded."""
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"(\w)-\s+(\w)", r"\1\2", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def load_sense(path: Path = _SENSE) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return {r["variable"]: r for r in csv.DictReader(f)}


def check_structure(
    ev_path: Path = _EV, xw_path: Path = _XW, sense_path: Path = _SENSE
) -> list[dict]:
    sense = load_sense(sense_path)
    out: list[dict] = []
    seen: set[str] = set()
    with ev_path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("use_role") in EFFECT_ROLES and r.get("review_state") != "dropped":
                seen.add(r.get("variable", ""))
    with xw_path.open(newline="", encoding="utf-8") as f:
        xw = list(csv.DictReader(f))
    seen |= {x["ev_variable"] for x in xw}
    for v in sorted(seen - set(sense)):
        out.append({"signal": "no_sense", "evidence_id": "", "detail": v})
    for x in xw:
        hi = (sense.get(x["ev_variable"]) or {}).get("high_is")
        if hi not in ("good", "bad") or _COST_TARGETS.match(x["target_key"]):
            continue
        want = "inverted" if hi == "bad" else "same"
        if (x.get("polarity") or "same") != want:
            out.append(
                {
                    "signal": "polarity_mismatch",
                    "evidence_id": "",
                    "detail": f"{x['xw_id']}: polarity {x.get('polarity')} but "
                    f"{x['ev_variable']} high_is {hi} → expected {want}",
                }
            )
    return out


def check_unit(r: dict) -> list[dict]:
    try:
        rel = json.loads(r.get("relationship") or "{}")
    except json.JSONDecodeError:
        return []
    eid = r.get("evidence_id", "")
    d = str(rel.get("direction") or "")
    cue = str(rel.get("direction_cue") or "")
    quote = r.get("quote", "")
    out: list[dict] = []
    if cue and _norm(cue) not in _norm(quote):
        out.append({"signal": "cue_not_verbatim", "evidence_id": eid, "detail": cue})
    if (
        not cue
        and d in ("positive", "negative", "none")
        and _ver(r.get("ruleset_version", "")) >= CUE_FROM
    ):
        out.append({"signal": "missing_cue", "evidence_id": eid, "detail": d})
    var = r.get("variable", "")
    if (
        cue
        and any(k in _norm(cue) for k in _keywords(var))
        and d in ("positive", "negative")
        and r.get("use_role") == "nbs_effect"
        and rel.get("framing") != "loss"
        and not _BENEFIT_NAMED.search(var)
        and "wocat" not in (r.get("source_id") or "")
    ):
        text = cue
        own = _keywords(var)
        if any(m.group(0).lower()[:6] not in own for m in _REVERSERS.finditer(text)):
            return out  # a reversing noun that is not the variable itself: words can't tell
        down, up = bool(_DOWN.search(text)), bool(_UP.search(text))
        if (d == "positive" and down and not up) or (
            d == "negative" and up and not down
        ):
            out.append(
                {
                    "signal": "cue_word_conflict",
                    "evidence_id": eid,
                    "detail": f"{var} {d} but the {'cue' if cue else 'quote'} only says "
                    f"{'down' if down else 'up'}: " + " ".join(text.split())[:120],
                }
            )
    return out


def check(ev_path: str | Path | None = None) -> list[dict]:
    p = Path(ev_path) if ev_path else _EV
    if not p.exists():
        return []
    out: list[dict] = []
    skip = _exceptions()
    with p.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (
                r.get("review_state") == "dropped"
                or r.get("use_role") not in EFFECT_ROLES
            ):
                continue
            out += [
                x
                for x in check_unit(r)
                if not (x["signal"] == "cue_word_conflict" and r["evidence_id"] in skip)
            ]
    return out


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ev = Path(argv[0]) if argv else _EV
    hard = check_structure(ev)
    soft = check(ev)
    for f in hard + soft:
        print(f"{f['signal']:18s} {f['evidence_id']:45s} {f['detail']}")
    by: dict[str, int] = {}
    for f in soft:
        by[f["signal"]] = by.get(f["signal"], 0) + 1
    print(f"structural: {len(hard)} · advisory: {by or 0}")
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
