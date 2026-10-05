"""T3 / T6 cell synthesis — pooled effect-claim evidence units → generated table rows.

Implements ``.agents/skills/_versions/v1.6.0/contracts/T3_T6_synthesis_contract.md``
(normative source: ``methodology/T3_T6_generation_method.md`` §2, §5, §7, §8).

The unit of output is a table CELL (T3: nbs × hazard × farming_system; T6: nbs × T5 priority
or economic indicator), not a paper. Every unit that an ``XW`` crosswalk row routes to the
cell is pooled and reconciled deterministically:

    gather → lineage dedupe → polarity + ordinal rank → weight (tier × claim_basis × grey ×
    transferability × XW factor × ns) → modal-sign weighted median → IPCC evidence ×
    agreement → confidence → scope rows → applicability envelope → gated numbers → prose.

Sign convention: generated rows are in the BENEFIT frame (positive = the NbS improves the
priority / reduces the hazard impact); `XW.polarity` converts each outcome-as-measured
direction into it (see `unit_rank`).

Weights, lineage dedupe, weighted median and the report object are IMPORTED from the T4
engine (``recipe.synthesis``); ``synthesise_t4_row`` is untouched. Confidence is derived,
never authored. Same register in → byte-identical rows out.
"""

from __future__ import annotations

import re

import csv
import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .evidence import EvidenceUnit
from .synthesis import (
    _DEFAULT_GREY_DISCOUNT,
    BASIS_W,
    GREY_DISCOUNT,
    TIER_W,
    SynthesisReport,
    _dedupe_lineage,
    _weighted_median,
)

# ── constants (defaults; tune per RFC — mirrors TIER_W / BASIS_W) ─────────────────────

EFFECT_ROLES = {"nbs_effect", "asset_vulnerability"}

#: transferability weight by context distance (method §5.2)
TRANSFER_W = {0: 1.0, 1: 0.7, 2: 0.3}
#: non-significant results count toward direction only, at half weight (method §3.2)
NS_FACTOR = 0.5
#: XW proximity defaults (method §4)
PROXIMITY_W = {"direct": 1.0, "proxy": 0.7, "component": 0.7}

STRENGTH_RANK = {"slight": 1, "moderate": 2, "strong": 3}
INCOME_BAND = {
    "low": "lic_lmic",
    "lower_middle": "lic_lmic",
    "lic_lmic": "lic_lmic",
    "upper_middle": "upper_middle",
    "high": "high",
}
#: farming-system adjacency (method §5.2 table)
_FS_ADJACENT = {
    frozenset({"cropping_rainfed", "mixed_crop_livestock"}),
    frozenset({"agro_pastoral", "pastoral_rangeland"}),
    frozenset({"tree_perennial", "mixed_crop_livestock"}),
}
#: T7 aez → coarse climate zone, used when the two sides share no exact AEZ
AEZ_CLIMATE_ZONE = {
    "humid_tropics": "tropical",
    "sub_humid_tropics": "tropical",
    "sub_humid_tropics_africa": "tropical",
    "highland_tropics": "tropical",
    "semi_arid": "dryland",
    "arid": "dryland",
    "dryland_mena": "dryland",
    "dryland_south_asia": "dryland",
    "east_africa_semiarid": "dryland",
    "temperate_europe": "temperate",
}
#: the WB-investable default target for global rows (method §5.3)
DEFAULT_TARGET = {"income_group": "lic_lmic"}

#: IPCC AR5 guidance-note matrix (Mastrandrea et al. 2010; AR5 WGII Fig 1.11) — the same
#: table ships as schema/lookups/ipcc_confidence_matrix.csv; this is the in-code fallback.
IPCC_MATRIX = {
    ("robust", "low"): "medium",
    ("robust", "medium"): "high",
    ("robust", "high"): "very_high",
    ("medium", "low"): "low",
    ("medium", "medium"): "medium",
    ("medium", "high"): "high",
    ("limited", "low"): "very_low",
    ("limited", "medium"): "low",
    ("limited", "high"): "medium",
}
CONFIDENCE_ORDER = ["very_low", "low", "medium", "high", "very_high"]

T3_HAZARDS = [
    "drought",
    "flood",
    "heat_stress",
    "fire",
    "wind_cyclone",
    "waterlogging",
    "frost",
]
ECON_UNITS = {
    "usd_per_ha",
    "usd_per_ha_yr",
    "usd_per_beneficiary",
    "usd_per_tco2e",
    "usd_per_farmer",
}
#: scope precedence at runtime (most specific first) — BIND's order + income_group
SCOPE_PRECEDENCE = [
    "admin_region",
    "admin_country",
    "hydrobasin",
    "farming_system",
    "aez",
    "income_group",
]
_LOW_BASIS = {"cited_secondary", "expert_assertion", "practitioner_rating"}
_PRIMARY_BASIS = {"primary_measured", "table"}

# grey discount for the new claim kind (method §7.8) — registered on the shared table
GREY_DISCOUNT.setdefault("asset_vulnerability", 0.6)


# ── small data holders ────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class XWRow:
    """One target-crosswalk row (schema XW)."""

    ev_variable: str
    target_table: str  # "T3" | "T6"
    target_key: str  # hazard_type | T5.variable_id | economic_indicator_type
    polarity: str = "same"  # "same" | "inverted"
    proximity: str = "direct"  # "direct" | "proxy" | "component"
    weight_factor: float | None = None

    @property
    def factor(self) -> float:
        if self.weight_factor is not None:
            return float(self.weight_factor)
        return PROXIMITY_W.get(self.proximity, 1.0)


@dataclass
class CellReport(SynthesisReport):
    """SynthesisReport + the cell-engine additions (contract §4)."""

    unmapped: list[tuple[str, int]] = field(default_factory=list)
    excluded_economics: list[tuple[str, str]] = field(default_factory=list)
    scope_rows_emitted: list[str] = field(default_factory=list)
    weights_incomplete: list[str] = field(default_factory=list)


@dataclass
class _Contrib:
    unit: EvidenceUnit
    sign: int  # -1 | 0 | +1 after polarity
    magnitude: int | None  # 1..3 or None (unspecified)
    weight: float
    distance: int  # 0 | 1 | 2 vs the row's target
    ctx: dict[str, Any]
    ns: bool
    has_direction: bool = (
        True  # False = magnitude/economics-only unit (never a null vote)
    )


# ── loaders (CSV registers / lookups; all optional — callers may pass Python objects) ──


def load_xw(path: str | Path) -> list[XWRow]:
    rows: list[XWRow] = []
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            wf = (r.get("weight_factor") or "").strip()
            rows.append(
                XWRow(
                    ev_variable=r["ev_variable"].strip(),
                    target_table=r["target_table"].strip(),
                    target_key=r["target_key"].strip(),
                    polarity=(r.get("polarity") or "same").strip(),
                    proximity=(r.get("proximity") or "direct").strip(),
                    weight_factor=float(wf) if wf else None,
                )
            )
    return rows


def load_bands(path: str | Path) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def load_income_lookup(path: str | Path) -> dict[str, str]:
    """ISO3 → income_group from schema/lookups/wb_income_groups.csv."""
    with open(path, encoding="utf-8", newline="") as f:
        return {r["iso3"]: r["income_group"] for r in csv.DictReader(f)}


def load_confidence_matrix(path: str | Path) -> dict[tuple[str, str], str]:
    with open(path, encoding="utf-8", newline="") as f:
        return {
            (r["evidence_level"], r["agreement_level"]): r["confidence"]
            for r in csv.DictReader(f)
        }


# ── BANDS: magnitude → strength class ─────────────────────────────────────────────────


def classify_magnitude(
    metric: str,
    magnitude: float | None,
    bands: list[dict[str, Any]],
    source_scale_value: str | None = None,
    unit: str | None = None,
    income_band: str | None = None,
) -> str:
    """Return the strength_class a magnitude falls in per the BANDS register.

    ``income_band`` (``lic_lmic`` · ``upper_middle`` · ``high``) selects context-relative
    rows: an absolute cost is "big or small" only relative to where it is spent (Pete
    2026-10-05). Rows pinning an ``income_band`` are tried before band-agnostic rows.

    ``abs_min`` inclusive, ``abs_max`` exclusive, on |magnitude - centre|. ``centre``
    defaults to 0; a RATIO metric sets ``centre = 1`` (a response ratio of 1.0 is "no
    effect", so RR 0.9 is a 10% reduction, not a 90% one).

    A band row may also pin a ``unit``: unit-specific rows are tried first, so
    ``metric = absolute`` with ``unit = response_ratio`` bands correctly while every other
    ``absolute`` unit (t/ha, USD/ha …) still falls through to ``unspecified``. This is why
    ratio-reporting meta-analyses do not need a new metric in the extraction contract.

    ``ordinal_rating`` rows match on ``source_scale_value``. No matching band →
    ``unspecified``.
    """
    unit_s = (unit or "").strip().lower()
    band_s = (income_band or "").strip().lower()

    def _rows(unit_specific: bool, band_specific: bool) -> list[dict[str, Any]]:
        out = []
        for b in bands:
            bu = (b.get("unit") or "").strip().lower()
            bb = (b.get("income_band") or "").strip().lower()
            if bool(bu) is not unit_specific or (unit_specific and bu != unit_s):
                continue
            if bool(bb) is not band_specific or (band_specific and bb != band_s):
                continue
            out.append(b)
        return out

    pools = []
    if unit_s and band_s:
        pools.append(_rows(True, True))
    if unit_s:
        pools.append(_rows(True, False))
    pools.append(_rows(False, False))
    for pool in pools:
        for b in pool:
            if (b.get("metric") or "") != metric:
                continue
            if metric == "ordinal_rating":
                if source_scale_value is not None and (
                    (b.get("source_scale_value") or "").strip().lower()
                    == source_scale_value.strip().lower()
                ):
                    return b.get("strength_class") or "unspecified"
                continue
            if magnitude is None:
                continue
            lo = b.get("abs_min")
            hi = b.get("abs_max")
            lo_f = float(lo) if lo not in (None, "") else None
            hi_f = float(hi) if hi not in (None, "") else None
            centre = b.get("centre")
            c = float(centre) if centre not in (None, "") else 0.0
            v = abs(float(magnitude) - c)
            if (lo_f is None or v >= lo_f) and (hi_f is None or v < hi_f):
                return b.get("strength_class") or "unspecified"
    return "unspecified"


# ── context normalisation + distance (method §3.3, §5.2) ─────────────────────────────


def _as_list(v: Any) -> list[str]:
    if v is None or v == "":
        return []
    if isinstance(v, str):
        return [s.strip() for s in v.replace("|", ",").split(",") if s.strip()]
    return [str(x) for x in v]


_ISO3 = re.compile(r"^[A-Z]{3}$")
# names the WB lookup spells differently (or does not carry); extend as sources demand
COUNTRY_ALIASES = {
    "usa": "USA",
    "us": "USA",
    "united states of america": "USA",
    "uk": "GBR",
    "drc": "COD",
    "dr congo": "COD",
    "democratic republic of the congo": "COD",
    "congo, dem. rep.": "COD",
    "syria": "SYR",
    "iran": "IRN",
    "egypt": "EGY",
    "vietnam": "VNM",
    "laos": "LAO",
    "russia": "RUS",
    "south korea": "KOR",
    "bolivia": "BOL",
    "venezuela": "VEN",
    "tanzania": "TZA",
    "ivory coast": "CIV",
    "cote d'ivoire": "CIV",
    "côte d'ivoire": "CIV",
    "the gambia": "GMB",
    "gambia": "GMB",
    "cabo verde": "CPV",
    "cape verde": "CPV",
    "eswatini": "SWZ",
    "swaziland": "SWZ",
    "czech republic": "CZE",
    "slovakia": "SVK",
    "türkiye": "TUR",
    "turkey": "TUR",
}


def normalise_countries(
    raw: Any, name_to_iso3: dict[str, str] | None = None
) -> tuple[list[str], list[str]]:
    """Free-text / list country field → (ISO3 list, unresolved tokens).

    Splits on ';' ',' '/' and '&'; accepts ISO3 as-is; resolves names via the WB lookup's
    ``country_name`` (case-insensitive) and ``COUNTRY_ALIASES``. "Global"/"multiple" and
    unknown names are returned as unresolved and never enter the envelope.
    """
    names = {k.lower(): v for k, v in (name_to_iso3 or {}).items()}
    toks: list[str] = []
    for x in _as_list(raw):
        toks += [s.strip() for s in re.split(r"[;,/&]| and ", str(x)) if s.strip()]
    out: list[str] = []
    bad: list[str] = []
    valid = set(names.values())
    for tok in toks:
        key = tok.lower()
        if key in COUNTRY_ALIASES:
            code = COUNTRY_ALIASES[key]
        elif _ISO3.match(tok) and (not valid or tok in valid):
            code = tok
        else:
            code = names.get(key) or ""
        if code and code not in out:
            out.append(code)
        elif not code and key not in {
            "global",
            "multiple",
            "various",
            "worldwide",
            "n/a",
        }:
            bad.append(tok)
    return out, bad


def unit_context(
    unit: EvidenceUnit,
    src_context: dict[str, Any] | None = None,
    income_lookup: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Fixed-key context for a unit: unit.context overrides the SRC defaults.

    Fills ``income_group`` from ``country`` via the WB lookup when absent, and
    ``climate_zone`` from ``aez`` when absent. Free-text keys are ignored here (they are
    ``check_context``'s business), so the engine only ever sees the fixed vocabulary.
    """
    src = src_context or {}
    uc = unit.context or {}
    out: dict[str, Any] = {}
    countries = _as_list(uc.get("country")) or [
        c
        for c in _as_list(src.get("country") or src.get("study_country"))
        # the SRC fallback is free text ("Brazil; Colombia; Mexico", "Global"): only ISO3
        # tokens may enter the envelope — the loader normalises names first
        # (`normalise_countries`); anything left unresolved is dropped, not injected
        if _ISO3.match(str(c))
    ]
    if countries:
        out["country"] = countries
    for k in ("aez", "farming_system", "income_group", "climate_zone"):
        v = uc.get(k) or src.get(k) or src.get(f"study_{k}")
        if v:
            out[k] = str(v)
    if "income_group" not in out and countries and income_lookup:
        groups = {income_lookup[c] for c in countries if c in income_lookup}
        if len(groups) == 1:
            out["income_group"] = groups.pop()
        elif groups:
            # multi-country: take the band if they agree, else leave for the modal rule
            bands = {INCOME_BAND.get(g, g) for g in groups}
            if len(bands) == 1:
                out["income_group"] = bands.pop()
    if "climate_zone" not in out and out.get("aez") in AEZ_CLIMATE_ZONE:
        out["climate_zone"] = AEZ_CLIMATE_ZONE[out["aez"]]
    return out


def _income_distance(a: str, b: str) -> int:
    ba, bb = INCOME_BAND.get(a, a), INCOME_BAND.get(b, b)
    if ba == bb:
        return 0
    if "high" in (ba, bb):
        return 2
    return 1  # lic_lmic ↔ upper_middle


def _aez_distance(a: dict[str, Any], b: dict[str, Any]) -> int | None:
    aa, ab = a.get("aez"), b.get("aez")
    if aa and ab:
        if aa == ab:
            return 0
        za, zb = AEZ_CLIMATE_ZONE.get(aa), AEZ_CLIMATE_ZONE.get(ab)
        if za and zb:
            return 1 if za == zb else 2
        return 2
    za, zb = a.get("climate_zone"), b.get("climate_zone")
    if za and zb:
        return 0 if za == zb else 2
    return None


def _fs_distance(a: str, b: str) -> int:
    if a == b:
        return 0
    return 1 if frozenset({a, b}) in _FS_ADJACENT else 2


def context_distance(unit_ctx: dict[str, Any], target_ctx: dict[str, Any]) -> int:
    """0 same · 1 adjacent · 2 far — max over dimensions populated on BOTH sides."""
    ds: list[int] = []
    if unit_ctx.get("income_group") and target_ctx.get("income_group"):
        ds.append(
            _income_distance(unit_ctx["income_group"], target_ctx["income_group"])
        )
    d_aez = _aez_distance(unit_ctx, target_ctx)
    if d_aez is not None:
        ds.append(d_aez)
    if unit_ctx.get("farming_system") and target_ctx.get("farming_system"):
        ds.append(
            _fs_distance(unit_ctx["farming_system"], target_ctx["farming_system"])
        )
    return max(ds) if ds else 0


# ── per-unit rank + weight ────────────────────────────────────────────────────────────


def unit_rank(unit: EvidenceUnit, polarity: str = "same") -> tuple[int, int | None]:
    """(sign, magnitude) on the shared −3..+3 scale, in the BENEFIT frame.

    The unit's `direction` is on the outcome AS MEASURED (erosion `negative` = erosion
    went down). T3 `mitigation_potential` and T6 `effect_direction` are in the BENEFIT
    frame: positive = the NbS improves the priority concern. `XW.polarity` is the
    converter: `inverted` for `high_is_bad` outcomes (erosion, hazards, costs),
    `same` for `low_is_bad` outcomes (yield, income, carbon, biodiversity).
    """
    rel = unit.relationship or {}
    d = str(rel.get("direction") or "").lower()
    sign = {"positive": 1, "negative": -1, "none": 0}.get(d, 0)
    # `framing = "loss"`: the source measured what happens when the vegetation / practice is
    # LOST or absent (dose-response to vegetation loss, deforestation → floods). The sign is
    # then that of the loss, so flip it to the intervention-present frame before polarity.
    if str(rel.get("framing") or "presence").lower() == "loss":
        sign = -sign
    if polarity == "inverted":
        sign = -sign
    mag = STRENGTH_RANK.get(str(rel.get("strength_class") or "").lower())
    if sign == 0:
        mag = None
    return sign, mag


def unit_weight(
    unit: EvidenceUnit,
    tier: str,
    category: str,
    distance: int,
    xw_factor: float = 1.0,
) -> float:
    w = TIER_W.get((tier or "").lower(), 0.5) * BASIS_W.get(unit.claim_basis, 0.5)
    if (category or "").lower() == "grey":
        w *= GREY_DISCOUNT.get(unit.use_role, _DEFAULT_GREY_DISCOUNT)
    w *= TRANSFER_W.get(distance, TRANSFER_W[2]) * xw_factor
    if str((unit.relationship or {}).get("significance") or "").lower() == "ns":
        w *= NS_FACTOR
    return w


# ── reconciliation (method §7.2–§7.4) ─────────────────────────────────────────────────


def _reconcile_rank(contribs: list[_Contrib]) -> tuple[int, float, int]:
    """(cell rank, sign agreement A, modal sign) over the contributing units.

    Units with no `direction` (magnitude / economics-only) are excluded here — a missing
    direction is not a null finding — but stay in the envelope, n_sources and the gated
    number summaries."""
    contribs = [c for c in contribs if c.has_direction]
    if not contribs:
        return 0, 0.0, 0
    pos = sum(c.weight for c in contribs if c.sign > 0)
    neg = sum(c.weight for c in contribs if c.sign < 0)
    zero = sum(c.weight for c in contribs if c.sign == 0)
    total = pos + neg + zero
    if total <= 0:
        return 0, 0.0, 0
    if pos == 0 and neg == 0:
        return 0, 1.0, 0
    modal = 1 if pos >= neg else -1
    agreement = ((pos if modal > 0 else neg) + zero / 2) / total
    pairs = [
        (float(c.sign * c.magnitude), c.weight)
        for c in contribs
        if c.sign == modal and c.magnitude is not None
    ]
    pairs += [(0.0, c.weight) for c in contribs if c.sign == 0]
    if not pairs:  # direction known, strength never stated → weakest class of that sign
        return modal * 1, agreement, modal
    med = _weighted_median(pairs)
    rank = int(round(med if med is not None else modal))
    if rank == 0:
        rank = modal  # modal sign exists; zeros cannot flip a stated direction to null
    return max(-3, min(3, rank)), agreement, modal


def independent_sources(items: list[Any]) -> int:
    """Independent evidence count behind a set of units or contributions.

    A primary study counts 1 per distinct ``source_id``. A **meta-analysis unit** pools
    ``n`` independent studies, so it counts ``n`` (the largest ``n`` any of that source's
    units states) when ``relationship.design == "meta_analysis"`` and ``n >= 2``. Without
    this, a pooled estimate over 12 studies counted as one source and could never satisfy
    the "≥ 2 independent sources" gates on `magnitude_summary` / `economic_value_range`
    (method §7.7; agreed with Pete 2026-10-05). Lineage dedupe has already run upstream,
    so re-cited primaries are not double-counted here.
    """
    per_source: dict[str, int] = {}
    for it in items:
        u = getattr(it, "unit", it)
        rel = u.relationship or {}
        n = rel.get("n")
        k = 1
        if str(rel.get("design") or "") == "meta_analysis" and isinstance(
            n, (int, float)
        ):
            k = max(1, int(n)) if n >= 2 else 1
        per_source[u.source_id] = max(per_source.get(u.source_id, 0), k)
    return sum(per_source.values())


def evidence_level(units: list[EvidenceUnit], tiers: dict[str, str]) -> str:
    n = independent_sources(units)
    bases = [u.claim_basis for u in units]
    if n <= 2 or all(b in _LOW_BASIS for b in bases):
        return "limited"
    n_primary = sum(1 for b in bases if b in _PRIMARY_BASIS)
    has_high_ma = any(
        (tiers.get(u.source_id, "") or "").lower() == "high"
        and str((u.relationship or {}).get("design") or "") == "meta_analysis"
        for u in units
    )
    if n >= 5 and (n_primary >= 2 or has_high_ma):
        return "robust"
    return "medium"


def agreement_level(agreement: float) -> str:
    if agreement >= 0.8:
        return "high"
    if agreement >= 0.6:
        return "medium"
    return "low"


def confidence(
    ev_level: str,
    ag_level: str,
    matrix: dict[tuple[str, str], str] | None = None,
) -> str:
    return (matrix or IPCC_MATRIX).get((ev_level, ag_level), "very_low")


def _conf_at_least(c: str, floor: str) -> bool:
    return CONFIDENCE_ORDER.index(c) >= CONFIDENCE_ORDER.index(floor)


def t6_effect_direction(rank: int) -> str:
    names = {1: "slight", 2: "moderate", 3: "strong"}
    if rank == 0:
        return "no_relationship"
    return f"{names[abs(rank)]}_{'positive' if rank > 0 else 'negative'}"


def t3_mitigation_potential(rank: int, conf: str) -> str:
    if rank == 0:
        return "none"
    if rank < 0:
        return "very_negative" if rank <= -3 else "negative"
    if rank == 1:
        return "low"
    if rank == 2:
        return "moderate"
    return "very_high" if _conf_at_least(conf, "high") else "high"


def asset_sensitivity(rank: int, conf: str) -> str:
    r = max(0, rank)  # damage direction only
    if r == 0:
        return "none"
    if r == 1:
        return "low"
    if r == 2:
        return "moderate"
    return "very_high" if _conf_at_least(conf, "high") else "high"


# ── applicability envelope (method §5.4) ──────────────────────────────────────────────


def _count_by(contribs: list[_Contrib], key: str) -> dict[str, int]:
    seen: dict[str, set[str]] = defaultdict(set)
    for c in contribs:
        v = c.ctx.get(key) or "unknown"
        seen[str(v)].add(c.unit.source_id)
    return {k: len(v) for k, v in sorted(seen.items())}


def transfer_class_from_shares(share0: float, share_le1: float, share2: float) -> str:
    """Strict majorities: an even split between in- and out-of-context evidence is `mixed`,
    never `in_context` (method §5.4, corrected 2026-10-02)."""
    if share0 > 0.5:
        return "in_context"
    if share2 > 0.5:
        return "out_of_context"
    if share_le1 > 0.5:
        return "adjacent"
    return "mixed"


def _pre_transfer_weight(c: _Contrib) -> float:
    """The contribution's weight WITHOUT the transferability factor. The share that decides
    `transfer_class` must not be measured on weights that already down-weight out-of-context
    units — that made one LMIC unit + one HIC unit read as 0.95 in-context (agroforestry
    prose review, 2026-10-02)."""
    return c.weight / TRANSFER_W.get(c.distance, TRANSFER_W[2])


def build_applicability(
    contribs: list[_Contrib], target_ctx: dict[str, Any]
) -> dict[str, Any]:
    total = sum(_pre_transfer_weight(c) for c in contribs) or 1.0
    s0 = sum(_pre_transfer_weight(c) for c in contribs if c.distance == 0) / total
    s1 = sum(_pre_transfer_weight(c) for c in contribs if c.distance <= 1) / total
    s2 = sum(_pre_transfer_weight(c) for c in contribs if c.distance == 2) / total
    countries = sorted({c for x in contribs for c in x.ctx.get("country", [])})
    return {
        "income_groups": _count_by(contribs, "income_group"),
        "aezs": _count_by(contribs, "aez"),
        "farming_systems": _count_by(contribs, "farming_system"),
        "countries": countries,
        "n_sources_in_scope": len({c.unit.source_id for c in contribs}),
        "weight_share_in_context": round(s0, 3),
        "target": dict(target_ctx),
        "transfer_class": transfer_class_from_shares(s0, s1, s2),
    }


def recompute_transfer_class(
    row: dict[str, Any],
    contribs_ctx: list[tuple[dict[str, Any], float]],
    aoi_ctx: dict[str, Any],
) -> str:
    """Transfer class of an emitted row against an AOI (runtime, method §5.5)."""
    total = sum(w for _, w in contribs_ctx) or 1.0
    ds = [(context_distance(c, aoi_ctx), w) for c, w in contribs_ctx]
    s0 = sum(w for d, w in ds if d == 0) / total
    s1 = sum(w for d, w in ds if d <= 1) / total
    s2 = sum(w for d, w in ds if d == 2) / total
    return transfer_class_from_shares(s0, s1, s2)


# ── gated numbers (method §7.6–§7.7) ──────────────────────────────────────────────────


_DEFAULT_BANDS_PATH = (
    Path(__file__).resolve().parents[3]
    / "schema"
    / "registers"
    / "BANDS_magnitude_bands.csv"
)


def _default_bands() -> list[dict[str, Any]]:
    return load_bands(_DEFAULT_BANDS_PATH) if _DEFAULT_BANDS_PATH.exists() else []


def magnitude_summary(
    contribs: list[_Contrib],
    bands: list[dict[str, Any]] | None = None,
    target_band: str = "",
) -> dict[str, Any] | None:
    """Best same-metric/same-unit pooled magnitude, plus its ORDINAL class.

    ``class`` is the BANDS class of the weighted median, taken relative to the row's
    income band for absolute costs — the scoping answer "big or small given the context"
    (Pete 2026-10-05). Numbers stay as transparency; the class is what consumers read.
    """
    bands = bands if bands is not None else _default_bands()
    by_key: dict[tuple[str, str], list[_Contrib]] = defaultdict(list)
    for c in contribs:
        rel = c.unit.relationship or {}
        m, u, v = rel.get("metric"), rel.get("unit"), rel.get("magnitude")
        if m and u and isinstance(v, (int, float)) and m not in ("narrative",):
            by_key[(str(m), str(u).lower())].append(c)
    best: dict[str, Any] | None = None
    for (metric, unit), group in sorted(by_key.items()):
        if independent_sources(group) < 2:
            continue
        vals = [
            (float((c.unit.relationship or {})["magnitude"]), c.weight) for c in group
        ]
        med = _weighted_median(vals)
        cand: dict[str, Any] = {
            "metric": metric,
            "unit": unit,
            "median": med,
            "low": min(v for v, _ in vals),
            "high": max(v for v, _ in vals),
            "n": independent_sources(group),
            "income_groups": _count_by(group, "income_group"),
            "class": classify_magnitude(
                metric, med, bands, unit=unit, income_band=target_band
            ),
            "class_context": target_band or "any",
        }
        if best is None or int(cand["n"]) > int(best["n"]):
            best = cand
    return best


def economic_value_range(
    contribs: list[_Contrib],
    target_ctx: dict[str, Any],
    report: CellReport,
) -> dict[str, Any] | None:
    """Emit a range only under ALL the §7.7 gates; log every excluded unit + gate."""
    target_band = INCOME_BAND.get(str(target_ctx.get("income_group") or ""), "")
    by_unit: dict[str, list[_Contrib]] = defaultdict(list)
    for c in contribs:
        rel = c.unit.relationship or {}
        v = rel.get("magnitude")
        unit = str(rel.get("unit") or "").lower()
        band = INCOME_BAND.get(str(c.ctx.get("income_group") or ""), "")
        lo, hi = rel.get("magnitude_low"), rel.get("magnitude_high")
        if not isinstance(v, (int, float)) and not (
            isinstance(lo, (int, float)) and isinstance(hi, (int, float))
        ):
            report.excluded_economics.append(
                (c.unit.evidence_id, "no numeric magnitude")
            )
            continue
        if unit not in ECON_UNITS:
            report.excluded_economics.append(
                (
                    c.unit.evidence_id,
                    f"unit '{unit or '?'}' has no per-unit denominator",
                )
            )
            continue
        if not band:
            report.excluded_economics.append(
                (c.unit.evidence_id, "income group unknown")
            )
            continue
        if target_band and band != target_band:
            gate = (
                "HIC figure excluded from LIC/LMIC or global row"
                if band == "high"
                else f"income band {band} ≠ row band {target_band}"
            )
            report.excluded_economics.append((c.unit.evidence_id, gate))
            continue
        by_unit[unit].append(c)
    for unit, group in sorted(by_unit.items()):
        if independent_sources(group) < 2:
            for c in group:
                report.excluded_economics.append(
                    (c.unit.evidence_id, f"only 1 independent source in {unit}")
                )
            continue
        vals: list[float] = []
        for c in group:
            r = c.unit.relationship or {}
            if isinstance(r.get("magnitude"), (int, float)):
                vals.append(float(r["magnitude"]))
            else:  # range-only unit: both bounds enter the observed extremes
                vals += [float(r["magnitude_low"]), float(r["magnitude_high"])]
        notes = []
        for c in group:
            yr = (c.unit.relationship or {}).get("currency_year") or "year n/a"
            iso = ",".join(c.ctx.get("country", [])) or "country n/a"
            notes.append(f"{c.unit.source_id} ({iso}, {yr})")
        return {
            "low": min(vals),
            "high": max(vals),
            "unit": unit,
            "source_note": "; ".join(notes) + f"; n={len(group)}; band={target_band}",
        }
    return None


def asset_risk_weights(
    rows: list[dict[str, Any]], nbs_id: str, report: CellReport | None = None
) -> dict[str, float] | None:
    """rank_h / Σ rank over the NbS's asset_threat rows; None unless all 7 hazards present."""
    sens_rank = {"none": 0, "low": 1, "moderate": 2, "high": 3, "very_high": 3}
    global_rows = [
        r
        for r in rows
        if r.get("nbs_id") == nbs_id
        and r.get("risk_role") in ("asset_threat", "both")
        and not r.get("scope_type")
        and not r.get("suitability_family_id")
    ]
    by_h = {r["hazard_type"]: r for r in global_rows}
    if set(by_h) != set(T3_HAZARDS):
        if report is not None:
            report.weights_incomplete.append(nbs_id)
        return None
    ranks = {
        h: sens_rank.get(by_h[h].get("asset_sensitivity", "none"), 0) for h in by_h
    }
    tot = sum(ranks.values())
    if tot == 0:
        return {h: round(1 / len(T3_HAZARDS), 6) for h in T3_HAZARDS}
    return {h: round(ranks[h] / tot, 6) for h in T3_HAZARDS}


# ── the cell engine ───────────────────────────────────────────────────────────────────


def _record_id(
    nbs_id: str,
    cell: str,
    family: str | None,
    scope: tuple[str, str] | None,
) -> str:
    parts = [nbs_id]
    if family:
        # FAM ids already carry the NbS prefix (riparian_buffer__planted) — don't double it
        parts.append(
            family[len(nbs_id) + 2 :] if family.startswith(nbs_id + "__") else family
        )
    parts.append(cell)
    if scope:
        parts.append(f"{scope[0]}-{scope[1]}")
    return "__".join(parts)


def _contribs(
    units: list[EvidenceUnit],
    tiers: dict[str, str],
    categories: dict[str, str],
    xw: XWRow,
    target_ctx: dict[str, Any],
    src_contexts: dict[str, dict[str, Any]],
    income_lookup: dict[str, str] | None,
) -> list[_Contrib]:
    out: list[_Contrib] = []
    for u in units:
        ctx = unit_context(u, src_contexts.get(u.source_id), income_lookup)
        d = context_distance(ctx, target_ctx)
        sign, mag = unit_rank(u, xw.polarity)
        w = unit_weight(
            u,
            tiers.get(u.source_id, "medium"),
            categories.get(u.source_id, ""),
            d,
            xw.factor,
        )
        ns = str((u.relationship or {}).get("significance") or "").lower() == "ns"
        has_dir = str((u.relationship or {}).get("direction") or "").lower() in (
            "positive",
            "negative",
            "none",
        )
        out.append(_Contrib(u, sign, mag, w, d, ctx, ns, has_dir))
    return out


def _reconcile_group(
    contribs: list[_Contrib],
    tiers: dict[str, str],
    matrix: dict[tuple[str, str], str] | None,
    target_ctx: dict[str, Any],
) -> dict[str, Any]:
    rank, agreement, modal = _reconcile_rank(contribs)
    strength_stated = any(
        c.has_direction and c.sign == modal and c.magnitude is not None
        for c in contribs
    )
    units = [c.unit for c in contribs]
    ev_l = evidence_level(units, tiers)
    ag_l = agreement_level(agreement)
    conf = confidence(ev_l, ag_l, matrix)
    return {
        "rank": rank,
        "agreement": round(agreement, 3),
        "modal_sign": modal,
        "evidence_level": ev_l,
        "agreement_level": ag_l,
        "confidence": conf,
        "applicability": build_applicability(contribs, target_ctx),
        "n_sources": len({c.unit.source_id for c in contribs}),
        "evidence_ids": [c.unit.evidence_id for c in contribs],
        "sources": sorted({c.unit.source_id for c in contribs}),
        "source_mix": _source_mix(contribs),
        # direction_only = every modal-sign unit states a direction but no strength; the
        # weakest class is emitted and the statement says the strength is unquantified
        "strength_basis": "quantified" if strength_stated else "direction_only",
    }


def _source_mix(contribs: list[_Contrib]) -> dict[str, Any]:
    mix = {"peer_reviewed": 0, "grey": 0, "expert": 0}
    for c in contribs:
        if c.unit.evidence_type == "expert":
            mix["expert"] += 1
        elif (
            str((c.unit.relationship or {}).get("design") or "")
            == "practitioner_rating"
        ):
            mix["grey"] += 1
        else:
            mix["peer_reviewed"] += 1
    if contribs and mix["expert"] == len(contribs):
        mix["expert_only"] = True
    return mix


# T3/T6 rows are in the BENEFIT frame (positive = the NbS helps). The statement verb has to
# read in the frame of the TARGET: for a risk / hazard / gap / deficit target a benefit
# REDUCES it; for a stock / potential target a benefit INCREASES it. Caught by the riparian
# prose review (2026-10-01): "buffer increases soil_erosion_risk" meant the opposite.
_CONCERN_TARGET = re.compile(
    r"(_hazard|_risk|_gap|_stress|_poverty|_inequity|_dependency|_exposure)$"
)


def _benefit_verbs(table: str, key: str) -> tuple[str, str]:
    """(verb for a positive benefit rank, verb for a negative rank)."""
    if table == "T3" or key.endswith("_hazard"):
        # T6 hazard rows (variable_type climate_hazard_mitigation) are about livelihood
        # resilience to the hazard, not a smaller hazard
        return "reduces the impact of", "worsens the impact of"
    if _CONCERN_TARGET.search(key):
        return "reduces", "increases"
    return "increases", "decreases"


def _statement(
    table: str,
    nbs_id: str,
    key: str,
    rank: int,
    ev_l: str,
    ag_l: str,
    conf: str,
    envelope: dict[str, Any],
    role: str,
    strength_basis: str = "quantified",
) -> str:
    """Calibrated-language statement; levels inserted by the engine (contract §5)."""
    # name the AEZs only when they cover at least half of the pooled units; a single
    # tagged unit must not label the whole cell (riparian prose review, 2026-10-01)
    aezs = envelope.get("aezs", {}) or {}
    known = {k: n for k, n in aezs.items() if k != "unknown"}
    total = sum(aezs.values()) or 1
    if known and sum(known.values()) * 2 >= total:
        where = ", ".join(sorted(known))
    else:
        where = (
            ", ".join(envelope.get("countries", [])) or "the pooled evidence contexts"
        )
    if role == "asset_vulnerability":
        verb = {
            0: "is not damaged by",
            1: "is slightly damaged by",
            2: "is moderately damaged by",
            3: "is severely damaged by",
        }[max(0, min(3, rank))]
        core = f"{nbs_id} {verb} {key}"
    else:
        strength = {1: "slightly", 2: "moderately", 3: "strongly"}
        if strength_basis == "direction_only":
            strength = {1: "", 2: "", 3: ""}
        if key in _ECON_KEYS:
            # a cost indicator has no direction of benefit (manifest v0.4.1): describe the
            # pooled cost evidence instead of an effect
            core = f"{nbs_id} {key}: pooled cost evidence"
            return (
                f"{core} from {where} ({ev_l} evidence, {ag_l} agreement → {conf} confidence; "
                f"transfer: {envelope.get('transfer_class')}; value range only when the "
                "contract gates pass)."
            )
        up, down = _benefit_verbs(table, key)
        if rank == 0:
            core = f"{nbs_id} shows no effect on {key}"
        elif rank > 0:
            core = f"{nbs_id} {strength[rank]} {up} {key}".replace("  ", " ")
        else:
            core = f"{nbs_id} {strength[-rank]} {down} {key}".replace("  ", " ")
        if strength_basis == "direction_only":
            core += " (strength not quantified in the evidence)"
    return (
        f"{core} in {where} ({ev_l} evidence, {ag_l} agreement → {conf} confidence; "
        f"transfer: {envelope.get('transfer_class')})."
    )


def rec_statement(rec: dict[str, Any], table: str, key: str, role: str) -> str:
    """The calibrated statement for a reconciled record (used as the mechanism placeholder)."""
    return _statement(
        table,
        str(rec.get("nbs_id") or ""),
        key,
        rec["rank"],
        rec["evidence_level"],
        rec["agreement_level"],
        rec["confidence"],
        rec["applicability"],
        role,
        rec.get("strength_basis", "quantified"),
    )


def traceable_account(
    table: str,
    nbs_id: str,
    key: str,
    role: str,
    rec: dict[str, Any],
    contribs: list[_Contrib],
    proxies: list[str],
) -> dict[str, Any]:
    """Deterministic traceable account (contract §5). The optional AI prose writer may
    later REPLACE `evidence_summary`/`agreement_note`/`mechanism` text but never the levels,
    the statement template, or the id lists."""
    env = rec["applicability"]
    top = sorted(contribs, key=lambda c: c.weight, reverse=True)[:5]
    summary = []
    for c in sorted(contribs, key=lambda c: c.weight, reverse=True):
        rel = c.unit.relationship or {}
        bits = [c.unit.source_id]
        if rel.get("design"):
            bits.append(str(rel["design"]))
        if rel.get("outcome_raw"):
            bits.append(str(rel["outcome_raw"]))
        d = rel.get("direction")
        if d:
            bits.append(
                f"{d}{'/' + str(rel['strength_class']) if rel.get('strength_class') else ''}"
            )
        if isinstance(rel.get("magnitude"), (int, float)):
            m = f"{rel.get('metric', 'magnitude')}={rel['magnitude']}"
            if isinstance(rel.get("magnitude_low"), (int, float)) and isinstance(
                rel.get("magnitude_high"), (int, float)
            ):
                m += f" [{rel['magnitude_low']}, {rel['magnitude_high']}]"
            if rel.get("unit"):
                m += f" {rel['unit']}"
            bits.append(m)
        if c.ns:
            bits.append("ns")
        ctx_bits = [
            str(c.ctx[k])
            for k in ("income_group", "aez", "farming_system")
            if c.ctx.get(k)
        ]
        if c.ctx.get("country"):
            ctx_bits.insert(0, ",".join(c.ctx["country"]))
        if ctx_bits:
            bits.append("(" + "; ".join(ctx_bits) + ")")
        bits.append(f"[{c.unit.evidence_id}]")
        summary.append(" · ".join(bits))
    pos = [c.unit.evidence_id for c in contribs if c.sign > 0]
    neg = [c.unit.evidence_id for c in contribs if c.sign < 0]
    zero = [c.unit.evidence_id for c in contribs if c.sign == 0]
    agreement_note = (
        f"weighted sign agreement {rec['agreement']}: positive {len(pos)} {pos}; "
        f"negative {len(neg)} {neg}; null {len(zero)} {zero}."
    )
    return {
        "statement": _statement(
            table,
            nbs_id,
            key,
            rec["rank"],
            rec["evidence_level"],
            rec["agreement_level"],
            rec["confidence"],
            env,
            role,
            rec.get("strength_basis", "quantified"),
        ),
        "strength_basis": rec.get("strength_basis", "quantified"),
        "evidence_summary": summary,
        "agreement_note": agreement_note,
        "proxies": proxies,
        "key_evidence_ids": [c.unit.evidence_id for c in top],
        "source_mix": rec["source_mix"],
        "prose_pending": True,  # mechanism / conditionality await the (gated) prose writer
    }


def synthesise_cell(
    units: list[EvidenceUnit],
    tiers: dict[str, str],
    *,
    table: str,
    nbs_id: str,
    target_key: str,
    xw_rows: list[XWRow],
    role: str = "nbs_effect",
    farming_system: str = "all",
    family: str | None = None,
    categories: dict[str, str] | None = None,
    src_contexts: dict[str, dict[str, Any]] | None = None,
    income_lookup: dict[str, str] | None = None,
    matrix: dict[tuple[str, str], str] | None = None,
    target_ctx: dict[str, Any] | None = None,
    allow_crop_scope: bool = False,
    emit_scope_rows: bool = True,
    min_scope_sources: int = 2,
) -> tuple[list[dict[str, Any]], CellReport]:
    """Reconcile all units routed to ONE cell into its global row (+ scope rows).

    `units` may be the whole register slice for the NbS: the XW rows select what reaches
    the cell. `role` = `nbs_effect` (T3 mitigation / T6) or `asset_vulnerability` (T3
    asset threat; XW is bypassed — the unit's `context.hazard_type` selects the cell).
    Returns ([] , report) when nothing survives.
    """
    categories = categories or {}
    src_contexts = src_contexts or {}
    target_ctx = dict(target_ctx or DEFAULT_TARGET)
    rep = CellReport()

    # 1) gather via XW (or hazard key for asset vulnerability) + scope filter
    routed: list[tuple[EvidenceUnit, XWRow]] = []
    for u in units:
        if getattr(u, "review_state", "") == "dropped" or u.use_role != role:
            continue
        if u.nbs_id != nbs_id or (family and u.suitability_family_id != family):
            continue
        if u.claim_scope == "species_specific" or (
            u.claim_scope == "crop_specific" and not allow_crop_scope
        ):
            rep.dropped.append((u.evidence_id, f"claim_scope={u.claim_scope}"))
            continue
        if role == "asset_vulnerability":
            if str((u.context or {}).get("hazard_type") or "") == target_key:
                routed.append((u, XWRow(u.variable, "T3", target_key)))
            continue
        hits = [
            x
            for x in xw_rows
            if x.ev_variable == u.variable
            and x.target_table == table
            and x.target_key == target_key
        ]
        if not hits:
            continue
        if table == "T3":
            fs = str((u.context or {}).get("farming_system") or "all")
            if farming_system != "all" and fs not in (farming_system, "all"):
                continue
            # A unit that STATES its hazard only speaks to that hazard's cell. Without
            # this, any variable routed to several hazards (microclimate_buffering →
            # heat_stress AND frost) put every one of its units into every one of those
            # cells — the frost cell inherited 12 sources of daytime-shade evidence
            # (caught 2026-10-04). Blank = unstated = applies, exactly like farming_system.
            hz = str((u.context or {}).get("hazard_type") or "")
            if hz and hz != target_key:
                rep.dropped.append(
                    (u.evidence_id, f"hazard_type={hz} ≠ cell {target_key}")
                )
                continue
        if (
            table == "T6"
            and target_key in _ECON_KEYS
            and not _unit_fits_econ_cell(u, target_key)
        ):
            rep.dropped.append(
                (
                    u.evidence_id,
                    f"unit {(u.relationship or {}).get('unit')} does not fit the {target_key} denominator",
                )
            )
            continue
        for x in hits:
            routed.append((u, x))
    if not routed:
        return [], rep

    # 2) lineage dedupe (anti pseudo-consensus) — on the unit set
    kept_units = _dedupe_lineage([u for u, _ in routed], tiers, rep, categories)
    xw_by_unit = {u.evidence_id: x for u, x in routed}
    rep.used = [u.evidence_id for u in kept_units]

    # 3–5) contributions against the GLOBAL target
    contribs: list[_Contrib] = []
    for u in kept_units:
        x = xw_by_unit[u.evidence_id]
        contribs += _contribs(
            [u], tiers, categories, x, target_ctx, src_contexts, income_lookup
        )
    proxies = sorted(
        {
            f"{c.unit.variable}→{target_key} ({xw_by_unit[c.unit.evidence_id].proximity})"
            for c in contribs
            if xw_by_unit[c.unit.evidence_id].proximity != "direct"
        }
    )
    g = _reconcile_group(contribs, tiers, matrix, target_ctx)
    if table == "T6":
        cell = target_key
    elif role == "asset_vulnerability":
        cell = f"asset_threat__{target_key}"  # distinct from the mitigation cell of the same hazard
    else:
        cell = f"{target_key}__{farming_system}"
    rows: list[dict[str, Any]] = []

    def _row(rec: dict[str, Any], scope: tuple[str, str] | None, cs: list[_Contrib]):
        rec = dict(rec, nbs_id=nbs_id)
        r: dict[str, Any] = {
            "record_id": _record_id(nbs_id, cell, family, scope),
            "nbs_id": nbs_id,
            "suitability_family_id": family or "",
            "scope_type": scope[0] if scope else "",
            "scope_id": scope[1] if scope else "",
            "evidence_level": rec["evidence_level"],
            "agreement_level": rec["agreement_level"],
            "context_dependent": False,
            "family_spread": False,
            "applicability": rec["applicability"],
            "n_sources": rec["n_sources"],
            "evidence_ids": rec["evidence_ids"],
            "references": rec["sources"],
            "justification": traceable_account(
                table, nbs_id, target_key, role, rec, cs, proxies
            ),
        }
        if table == "T3":
            r.update(
                {
                    "hazard_type": target_key,
                    "farming_system": farming_system,
                    "confidence": rec["confidence"],
                    "timescale_of_effect": _modal_ctx(cs, "timescale_of_effect"),
                    "landscape_scale_only": _any_ctx_true(cs, "landscape_scale_only"),
                    # prose is written by the gated prose writer (contract §5); until it runs
                    # the field points at the traceable account instead of standing empty
                    "mitigation_mechanism": "[prose pending] "
                    + rec_statement(rec, table, target_key, role),
                    "caveats": "",
                }
            )
            if role == "asset_vulnerability":
                r["risk_role"] = "asset_threat"
                r["asset_sensitivity"] = asset_sensitivity(
                    rec["rank"], rec["confidence"]
                )
                r["mitigation_potential"] = ""
                r["asset_risk_weight"] = None
            else:
                r["risk_role"] = "livelihood_mitigation"
                r["mitigation_potential"] = t3_mitigation_potential(
                    rec["rank"], rec["confidence"]
                )
                r["asset_sensitivity"] = ""
        else:
            is_econ = target_key not in _T5_LIKE and target_key in _ECON_KEYS
            r.update(
                {
                    "variable_id": target_key,
                    "variable_type": (
                        "economic_indicator"
                        if is_econ
                        else (
                            "climate_hazard_mitigation"
                            if target_key.endswith("_hazard")
                            else "opportunity_space_variable"
                        )
                    ),
                    # a cost indicator has no "direction of benefit": the rank from the
                    # cost-sign votes is meaningless there, so economic rows leave it blank
                    # (manifest: conditional, required unless variable_type=economic_indicator)
                    "effect_direction": (
                        "" if is_econ else t6_effect_direction(rec["rank"])
                    ),
                    "effect_confidence": rec["confidence"],
                    "timescale_of_effect": _modal_ctx(cs, "timescale_of_effect"),
                    "effect_mechanism": "[prose pending] "
                    + rec_statement(rec, table, target_key, role),
                    "conditionality": "",
                    "magnitude_summary": magnitude_summary(
                        cs,
                        target_band=INCOME_BAND.get(
                            str(
                                rec["applicability"]["target"].get("income_group") or ""
                            ),
                            "",
                        ),
                    ),
                }
            )
            if is_econ:
                ms = r.get("magnitude_summary") or {}
                if ms.get("class") and ms["class"] != "unspecified":
                    size = {
                        "slight": "small",
                        "moderate": "moderate",
                        "strong": "large",
                    }[ms["class"]]
                    r["justification"]["statement"] += (
                        f" Cost class: {size} ({ms['unit']}, {ms['class_context']} context)."
                    )
                r["economic_indicator_type"] = target_key
                r["economic_value_range"] = economic_value_range(
                    cs, rec["applicability"]["target"], rep
                )
        return r

    global_row = _row(g, None, contribs)
    rows.append(global_row)

    # 7) scope rows — per context dimension, re-run against the group's own scope
    if emit_scope_rows:
        scope_dims = ["aez", "income_group"] + (
            ["farming_system"] if table == "T6" else []
        )
        differing: list[tuple[int, int]] = []
        for dim in scope_dims:
            groups: dict[str, list[EvidenceUnit]] = defaultdict(list)
            for c in contribs:
                v = c.ctx.get(dim)
                if v:
                    groups[
                        INCOME_BAND.get(v, v) if dim == "income_group" else str(v)
                    ].append(c.unit)
            for sid, gunits in sorted(groups.items()):
                if len({u.source_id for u in gunits}) < min_scope_sources:
                    continue
                # a scope row is reconciled against ITS scope alone (method §5.3): a
                # temperate_europe row applies to temperate Europe, whatever the income
                s_target: dict[str, Any] = {dim: sid}
                s_contribs: list[_Contrib] = []
                for u in gunits:
                    s_contribs += _contribs(
                        [u],
                        tiers,
                        categories,
                        xw_by_unit[u.evidence_id],
                        s_target,
                        src_contexts,
                        income_lookup,
                    )
                s_rec = _reconcile_group(s_contribs, tiers, matrix, s_target)
                g_class_for_scope = recompute_transfer_class(
                    global_row, [(c.ctx, c.weight) for c in contribs], s_target
                )
                if (
                    abs(s_rec["rank"] - g["rank"]) >= 1
                    or g_class_for_scope == "out_of_context"
                    or g["agreement_level"] == "low"
                ):
                    rows.append(_row(s_rec, (dim, sid), s_contribs))
                    rep.scope_rows_emitted.append(rows[-1]["record_id"])
                    differing.append((s_rec["modal_sign"], s_rec["rank"]))
        if g["agreement_level"] in ("low", "medium") and len(differing) >= 2:
            signs = {s for s, _ in differing}
            ranks = {r for _, r in differing}
            if len(signs) > 1 or len(ranks) > 1:
                global_row["context_dependent"] = True

    rep.notes.append(
        f"{table} {nbs_id}/{cell}: rank {g['rank']} A={g['agreement']} "
        f"{g['evidence_level']}×{g['agreement_level']}→{g['confidence']}; "
        f"{len(rows) - 1} scope row(s); transfer {g['applicability']['transfer_class']}"
    )
    return rows, rep


# Economic T6 cells are DENOMINATOR-SPECIFIC. A unit may reach a cost cell only if its
# `relationship.unit` matches the cell's denominator (or is a relative measure, which
# carries direction but never a value). Without this, XW routed every `project_cost`
# unit everywhere: a USD/tCO2e figure ended up as the magnitude of the per-hectare
# establishment-cost cell (caught 2026-10-05).
_ECON_UNITS: dict[str, set[str]] = {
    "establishment_cost": {
        "usd_per_ha",
        "usd_per_household",
        "usd_per_farmer",
        "usd_per_beneficiary",
    },
    "recurrent_cost": {"usd_per_ha_yr", "usd_per_household_yr", "usd_per_farmer_yr"},
    "cost_per_hectare_restored": {"usd_per_ha"},
    "cost_per_beneficiary": {
        "usd_per_beneficiary",
        "usd_per_household",
        "usd_per_household_yr",
    },
    "cost_per_farmer_reached": {"usd_per_farmer", "usd_per_farmer_yr"},
    "cost_per_tco2e_avoided": {"usd_per_tco2e"},
    "income_potential": {
        "usd_per_ha_yr",
        "usd_per_household_yr",
        "usd_per_farmer_yr",
        "usd_per_ha",
    },
    "carbon_revenue": {"usd_per_ha_yr", "usd_per_tco2e"},
}
#: relative metrics carry no denominator; they may vote direction in a cost cell but
#: never set a value, so they pass the unit filter and fail the value gates by construction
_RELATIVE_METRICS = {"ln_response_ratio", "pct_change", "smd_hedges_g", "narrative"}


def _unit_fits_econ_cell(unit: EvidenceUnit, target_key: str) -> bool:
    allowed = _ECON_UNITS.get(target_key)
    if allowed is None:
        return True  # unconstrained cell (cost_reduction, market_access, subsidy_dependency)
    rel = unit.relationship or {}
    if str(rel.get("metric") or "") in _RELATIVE_METRICS:
        return True
    return str(rel.get("unit") or "").strip().lower() in allowed


# T6 keys that are economic indicators (schema enum) vs T5-like priority ids
_ECON_KEYS = {
    "establishment_cost",
    "recurrent_cost",
    "income_potential",
    "cost_reduction",
    "market_access",
    "carbon_revenue",
    "subsidy_dependency",
    "cost_per_beneficiary",
    "cost_per_hectare_restored",
    "cost_per_tco2e_avoided",
    "cost_per_farmer_reached",
}
_T5_LIKE: set[str] = (
    set()
)  # reserved: callers may register T5 ids that collide with econ names


def _modal_ctx(contribs: list[_Contrib], key: str) -> str:
    counts: dict[str, float] = defaultdict(float)
    for c in contribs:
        v = (c.unit.context or {}).get(key)
        if v:
            counts[str(v)] += c.weight
    return max(counts, key=lambda k: counts[k]) if counts else ""


def _any_ctx_true(contribs: list[_Contrib], key: str) -> bool:
    return any(
        str((c.unit.context or {}).get(key)).lower() in ("true", "1") for c in contribs
    )


# ── family rows + NbS roll-up (method §2.2) ───────────────────────────────────────────


def synthesise_cell_with_families(
    units: list[EvidenceUnit],
    tiers: dict[str, str],
    *,
    families: list[str] | None = None,
    min_family_sources: int = 2,
    **kw: Any,
) -> tuple[list[dict[str, Any]], CellReport]:
    """NbS roll-up row(s) (always, pooled) + family rows where ≥ 2 independent sources.
    Sets `family_spread` on the roll-up global row when family ranks differ by ≥ 2."""
    rows, rep = synthesise_cell(units, tiers, family=None, **kw)
    if not rows:
        return rows, rep
    fams = families or sorted(
        {u.suitability_family_id for u in units if u.suitability_family_id}
    )
    fam_ranks: list[int] = []
    for fam in fams:
        fam_units = [u for u in units if u.suitability_family_id == fam]
        if len({u.source_id for u in fam_units}) < min_family_sources:
            continue
        frows, frep = synthesise_cell(
            fam_units, tiers, family=fam, emit_scope_rows=False, **kw
        )
        if frows:
            rows += frows
            fam_ranks.append(_rank_of(frows[0]))
            rep.notes += frep.notes
    if len(fam_ranks) >= 2 and max(fam_ranks) - min(fam_ranks) >= 2:
        rows[0]["family_spread"] = True
    return rows, rep


_DIR_RANK = {
    "strong_negative": -3,
    "moderate_negative": -2,
    "slight_negative": -1,
    "no_relationship": 0,
    "slight_positive": 1,
    "moderate_positive": 2,
    "strong_positive": 3,
    "very_negative": -3,
    "negative": -2,
    "none": 0,
    "low": 1,
    "moderate": 2,
    "high": 3,
    "very_high": 3,
}


def _rank_of(row: dict[str, Any]) -> int:
    v = (
        row.get("effect_direction")
        or row.get("mitigation_potential")
        or row.get("asset_sensitivity")
    )
    return _DIR_RANK.get(str(v), 0)


# ── runtime resolution (method §5.5) ──────────────────────────────────────────────────


def resolve_for_aoi(
    rows: list[dict[str, Any]],
    aoi_ctx: dict[str, Any],
    contrib_ctx_by_row: dict[str, list[tuple[dict[str, Any], float]]] | None = None,
) -> tuple[dict[str, Any] | None, str]:
    """Pick the most specific matching row for an AOI; return (row, status).

    status ∈ {"ok", "no_applicable_evidence", "no_rows"}. A global row whose transfer class
    against the AOI is `out_of_context` yields `no_applicable_evidence` (row attached for
    display, greyed), never a class as if it applied. `contrib_ctx_by_row` (record_id →
    [(unit_ctx, weight)]) enables the recompute; without it the stored class is used.
    """
    if not rows:
        return None, "no_rows"
    aoi_band = INCOME_BAND.get(str(aoi_ctx.get("income_group") or ""), "")
    for st in SCOPE_PRECEDENCE:
        want = aoi_band if st == "income_group" else aoi_ctx.get(st)
        if not want:
            continue
        for r in rows:
            if r.get("scope_type") == st and r.get("scope_id") == want:
                return r, "ok"
    glob = [r for r in rows if not r.get("scope_type")]
    if not glob:
        return None, "no_rows"
    row = glob[0]
    if contrib_ctx_by_row and row["record_id"] in contrib_ctx_by_row:
        tc = recompute_transfer_class(
            row, contrib_ctx_by_row[row["record_id"]], aoi_ctx
        )
    else:
        tc = (row.get("applicability") or {}).get("transfer_class", "mixed")
    if tc == "out_of_context":
        return row, "no_applicable_evidence"
    return row, "ok"


def save_rows(rows: list[dict[str, Any]], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path
