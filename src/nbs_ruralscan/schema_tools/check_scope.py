"""Deterministic SECTION-SCOPE check (the dominant 2026-06-18 QA defect).

The verbatim guardrail proves a quote is real; `check_numbers` proves its numbers come
from the quote. Neither proves the quote is a SUITABILITY CLAIM. Human QA on 2026-06-18
dropped 12/15 reviewed units as `off_scope` — values lifted from sections that are NOT
suitability reasoning: study-site/characteristics tables, methods/study-area text,
carbon·CO2·biomass accounting, and generic problem statements. (See review_log notes.)

This flags the same class deterministically, every build, no model tokens: an EV quote
whose text signals one of those off-scope section types is flagged for review. Signals
are PROXIES — a real suitability claim can mention carbon — so this is ADVISORY (flags,
never fails the build). Use it to triage before an LLM verify pass and to stop
regressions; the `off_scope` rate must trend DOWN sweep-over-sweep.

Two 2026-07 additions (from the sweep-retro triage of the July QA `other`/`constrained_aoi`
buckets): `land_capability` catches AOI-constraining land-capability/land-use-capacity
schemes (residual/"marginal land" framing — catalogue #14 `constrained_aoi`), and
`land_cover_no_classes` catches a land_cover/LULC quote that names no in/out classes
(unactionable — catalogue #13). Both advisory, same as the section signals.

Already-resolved rows (reviewer_ok) and quarantined rows (review_state=dropped) are
skipped — they've had their human call.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"

# off-scope section signals (case-insensitive), grouped by the defect they catch
_SIGNALS: dict[str, re.Pattern] = {
    "study_site": re.compile(
        r"study (site|area)|site characteristic|experimental (site|plot|design)"
        r"|the sites? (are|were|comprise)|located (in|within|at)|study region",
        re.I,
    ),
    "carbon_biomass": re.compile(
        r"\bCO2\b|\bCO₂\b|carbon (stock|sequestr|removal|dioxide|storage)"
        r"|sequestr|\bbiomass\b|\bPg ?C\b|tCO2|\bMg ?C\b|aboveground (carbon|biomass)",
        re.I,
    ),
    "problem_intro": re.compile(
        r"problem statement|in recent decades|globally,|is a (growing|major) (concern|problem)"
        r"|threatens? (food|livelihood)",
        re.I,
    ),
    # results/output description: describing a produced map/zones, not a suitability RULE
    # ("mapped suitability for an area", "zones being described") — added 2026-06-22 from review.
    "results_description": re.compile(
        r"(map|maps|mapped|classified|delineated|categori[sz]ed) (the |as |into )?"
        r"(suitab|priority|potential|zones?|areas?)"
        r"|suitability map (shows|indicates|reveals|identif)"
        r"|the (resulting )?map (shows|reveals|identif)"
        r"|(zones?|areas?|regions?) (were|are|was|is) "
        r"(classified|identified|delineated|mapped|categori[sz]ed)"
        r"|potential (zones?|areas?) for (agroforestry|implementation)",
        re.I,
    ),
    # allocation/area-share OUTPUT of an MCDA/AHP run ("X% of the land unit was allocated to
    # agroforestry", "distribution ratio ... for ... agroforestry") — a produced result, not a
    # per-pixel suitability criterion. Added 2026-06-23 (seja2022 land_cover; AHP allocation).
    "allocation_result": re.compile(
        r"land[- ]use allocation|allocat(ed|ion) (to|of)"
        r"|(distribution|coverage|allocation) ratio"
        r"|produced the ratio|ratio of [\d.,%\s]+for",
        re.I,
    ),
    # trend/distribution description: a global/temporal trend, not a per-pixel suitability rule
    # ("biomass distribution", "tree cover global trend") — added 2026-06-22 from review.
    "trend_description": re.compile(
        r"global trend|over the (past|last) (few )?(decades?|years?|century)"
        r"|(tree cover|forest cover|biomass|vegetation) (has |have )?"
        r"(increased|declined|decreased|changed|expanded)"
        r"|distribution of (tree|forest|biomass|carbon)|(historical|temporal) (trend|change)",
        re.I,
    ),
    # speculation/assumption, not measured/used evidence ("may still deter", "reflection and
    # assumption", "hand-wavy assumed causation") — added 2026-06-22 from review.
    "speculation": re.compile(
        r"\bwe assume\b|\bassumption\b|\bassumed\b"
        r"|may (still )?(deter|help|improve|reduce|increase|affect|enhance)"
        r"|could (potentially|possibly|help|improve|enhance)"
        r"|might (be|help|deter|affect|improve)|it is (likely|possible) that"
        r"|we (believe|expect|hypothesi)|is (a )?reflection|hand-?wavy|speculat",
        re.I,
    ),
    # AOI-CONSTRAINING classification (2026-06-24 `constrained_aoi`, catalogue #14): a
    # land-capability / land-use-capacity scheme (USDA-LCC-style, e.g. INAB Guatemala) that
    # files agroforestry into a residual / "marginal land" bucket UNDERSTATES where the NbS is
    # feasible — its class thresholds describe where it was *allocated*, not where it *can go*.
    # A FRAMING bias of an on-topic source: never use to set the AOI/extent or a global
    # threshold. Existing INAB rows are already dropped (skipped below); this stops regressions.
    "land_capability": re.compile(
        r"land[- ]?(use[- ]?)?capabilit|capability class(es|ification)?"
        r"|land[- ]?use[- ]?capacit|capacidad de uso|clase[s]? agrol[oó]gic"
        r"|clases de capacidad|marginal land|residual land|tierras marginales"
        r"|USDA[- ]?LCC|\bINAB\b",
        re.I,
    ),
}

# land_cover / LULC variables (2026-06-24, catalogue #13): a bare "land cover is a variable"
# claim with NO enumerated in/out classes is unreviewable ("which classes are in or out?").
# Flag a land_cover EV whose quote names none of the usual class terms.
_LC_VARS = ("land_cover", "landcover", "lulc", "land_use")
_LC_CLASS = re.compile(
    r"\b(forest|woodland|cropland|crop ?land|agricultur|pasture|grass ?land|range ?land"
    r"|shrub|savanna|wetland|\bwater\b|urban|built[- ]?up|bare|barren|mangrove|plantation"
    r"|orchard|fallow|settlement|grazing|scrub|tree ?cover|canopy|paddy|arable"
    r"|deciduous|evergreen|coniferous|meadow|bush)\b",
    re.I,
)

# ---------------------------------------------------------------------------
# site_context (2026-07, catalogue #16): a structural_suitability quote that describes the
# STUDY'S OWN SITE / a figure / a region — NOT a generalising suitability RULE. A single
# study saying "our site is 900 mm, 28 °C, 30 trees/ha" is n=1 CONTEXT (answers "where did
# you work?"), not a criterion ("where does the practice work?"). The recurring #1 defect
# Pete flags: study context extracted as biophysical suitability. Net for the classes the
# pure-quote `study_site` signal above misses — the AI's own `direction` tell (site_envelope
# / fmnr_occurs_on…), figure captions, and region-extent context. GATE: FRAME (or site-
# occurrence direction) AND NOT a suitability CRITERION AND NOT a distributional
# GENERALisation — because "FMNR occurs ACROSS the 100–950 mm band" (a review envelope) and
# "suitable where…" ARE rules and must be kept. Tuned to 6/6 of Pete's 2026-07 FMNR site-
# context drops with 0 genuine-rule false-positives. Advisory, like the signals above.
_SITE_FRAME = re.compile(
    r"study\s+(area|site|sites|region|plots?)"
    r"|\bis\s+located\s+in\b|\blocated\s+in\s+the\b|characteri[sz]ed\s+by"
    r"|(extended\s+)?fig(ure|\.)\s*\d|\btable\s*\d+\s*[:.]"
    r"|couvre\s+[\d\s]+\s*km|du\s+territoire|correspond\s+à\s+des\s+écosyst"
    r"|covers?\s+[\d,\s]+\s*(km|ha|hectares)\b|% of the (national )?territory"
    r"|our\s+(study|site|plots?|field)|the\s+region\s+(is|has|over\s+which)"
    r"|study\s+(area\s+)?was\s+(conducted|carried|situated)"
    r"|used\s+\w*\s*fmnr\s+to\s+restore|restored?\s+[\d,]+\s*(ha|hectares)",
    re.I,
)
_SITE_OCC_DIR = re.compile(
    r"site_envelope|observed_.*_where_fmnr|fmnr_occurs_on|_at_site\b", re.I
)
_SITE_CRITERION = re.compile(
    r"suitab|optim|\brequire|\bneeds?\b|grows?\s+(best|well)|thriv|toleran|prefer"
    r"|best\s+(for|suited)|ideal\s+for|establishment\s+requires|gated|enabl|favou?r",
    re.I,
)
_SITE_GENERAL = re.compile(
    r"\bacross\b|throughout|many\s+(types|soils|kinds)|generally|broadly|band|zones?\s+of"
    r"|wherever|(wide\s+)?range\s+of|various\s+soils|confined\s+to|gradient|isohyet"
    r"|agroecological\s+context",
    re.I,
)
_DIRECTION = re.compile(r'"direction"\s*:\s*"([^"]*)"')


def _is_site_context(quote: str, relationship: str) -> bool:
    """True when a structural_suitability quote is single-study CONTEXT, not a rule."""
    m = _DIRECTION.search(relationship or "")
    direction = m.group(1) if m else ""
    if _SITE_CRITERION.search(quote) or _SITE_CRITERION.search(direction):
        return False
    if _SITE_GENERAL.search(quote) or _SITE_GENERAL.search(direction):
        return False
    return bool(_SITE_FRAME.search(quote) or _SITE_OCC_DIR.search(direction))


def check(ev_path: str | Path | None = None) -> list[dict]:
    """Return advisory off-scope flags: [{evidence_id, signal, snippet}]."""
    path = Path(ev_path) if ev_path else EV
    flags: list[dict] = []
    if not path.exists():
        return flags
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r.get("review_state") or "") == "dropped":
                continue
            if (r.get("reviewer_ok") or "").lower() == "true":
                continue
            # off-scope here means "not a SUITABILITY claim" -> only T4 structural rows.
            # carbon/biomass is legitimate for T6 (nbs_effect) and fuel/biomass for T3
            # (hazard), so this check is scoped to structural_suitability only.
            if r.get("use_role") != "structural_suitability":
                continue
            quote = r.get("quote") or ""
            matched = False
            for name, pat in _SIGNALS.items():
                m = pat.search(quote)
                if m:
                    s = max(0, m.start() - 20)
                    flags.append(
                        {
                            "evidence_id": r["evidence_id"],
                            "signal": name,
                            "snippet": quote[s : m.end() + 20].strip(),
                        }
                    )
                    matched = True
                    break  # one section-signal flag per row is enough for triage
            if matched:
                continue
            # land_cover with no enumerated classes → unactionable (catalogue #13)
            var = (r.get("variable") or "").lower()
            if any(k in var for k in _LC_VARS) and not _LC_CLASS.search(quote):
                flags.append(
                    {
                        "evidence_id": r["evidence_id"],
                        "signal": "land_cover_no_classes",
                        "snippet": quote[:60].strip(),
                    }
                )
                continue
            # study-site / figure / region CONTEXT extracted as suitability (catalogue #16)
            if _is_site_context(quote, r.get("relationship") or ""):
                flags.append(
                    {
                        "evidence_id": r["evidence_id"],
                        "signal": "site_context",
                        "snippet": quote[:60].strip(),
                    }
                )
    return flags


def main(argv: list[str] | None = None) -> int:

    flags = check(argv[0] if argv else None)
    if not flags:
        print("SCOPE CHECK: no off-scope signals in active, unreviewed units.")
        return 0
    from collections import Counter

    by = Counter(f["signal"] for f in flags)
    print(
        f"SCOPE CHECK (advisory): {len(flags)} unit(s) with off-scope signals — review:"
    )
    for sig, n in by.most_common():
        print(f"  {n}  {sig}")
    for f in flags:
        print(f"  [{f['signal']}] {f['evidence_id']}: …{f['snippet']}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
