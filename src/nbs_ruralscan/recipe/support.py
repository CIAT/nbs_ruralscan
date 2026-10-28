"""Variable *support* — literature prevalence of a variable, with hierarchy roll-up.

`paper_support_pct(V)` = share of the family's screened corpus that yields ≥1 evidence
unit for variable V. A *selection* signal (which variables matter), the provenanced,
per-family successor to the stocktake's variable-frequency heatmap — complements ML
importance. It is a **prevalence**, not a truth: a common variable may be convention
(citation echo), a rare one may be locally decisive. So it informs inclusion with a
**soft floor that flags for decision**, never a hard auto-filter (method §6).

Roll-up is **set-union over members**, not a sum: a paper using both slope and elevation
counts once toward "Topographic" prevalence. Headline counts are unweighted. A separate
quality-weighted diagnostic requires explicit screened IDs and known tiers for all of them.
Callers must reconcile duplicate source identities before supplying the screened cohort;
this API counts source IDs and cannot establish bibliographic independence itself.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from .evidence import EvidenceUnit


@dataclass
class Support:
    key: str  # variable id or group id
    n_sources: int  # distinct sources with ≥1 unit
    corpus_n: int | None  # denominator: sources screened for the family
    pct: float | None  # 100 * n_sources / corpus_n
    members: list[str] = field(default_factory=list)  # group members (group-level only)
    quality_weighted_pct: float | None = (
        None  # diagnostic only; never selection/runtime weight
    )


TIER_W = {"high": 1.0, "medium": 0.6, "low": 0.35}


def _quality_weights(corpus_n, tiers):
    """No cohort membership or unknown tier means no weighted diagnostic."""
    if not isinstance(corpus_n, set) or not corpus_n or not tiers:
        return None
    weights = {}
    for source_id in corpus_n:
        tier = tiers.get(source_id)
        if not isinstance(tier, str) or tier.strip().lower() not in TIER_W:
            return None
        weights[source_id] = TIER_W[tier.strip().lower()]
    return weights


def _summarize_support(srcs, corpus_n, tiers, members=None):
    """Use one unweighted source vote; expose quality only as a named diagnostic."""
    if isinstance(corpus_n, set):
        missing = set().union(*srcs.values()) - corpus_n
        if missing:
            raise ValueError(
                f"Evidence sources absent from screened corpus: {sorted(missing)}"
            )
    n_den = len(corpus_n) if isinstance(corpus_n, set) else corpus_n
    weights = _quality_weights(corpus_n, tiers)
    weight_total = sum(weights.values()) if weights else None
    result = {}
    for key, sources in sorted(srcs.items(), key=lambda item: (-len(item[1]), item[0])):
        result[key] = Support(
            key=key,
            n_sources=len(sources),
            corpus_n=n_den,
            pct=round(100 * len(sources) / n_den, 1) if n_den else None,
            members=sorted((members or {}).get(key, [])),
            quality_weighted_pct=(
                round(100 * sum(weights[sid] for sid in sources) / weight_total, 1)
                if weights and weight_total
                else None
            ),
        )
    return result


def _validate_corpus_count(units, corpus_n):
    """A supplied denominator cannot be smaller than its observed membership."""
    if corpus_n is None or isinstance(corpus_n, set):
        return
    if type(corpus_n) is not int or corpus_n < 0:
        raise ValueError(
            "Screened corpus count must be a nonnegative integer or source set"
        )
    if len({u.source_id for u in units}) > corpus_n:
        raise ValueError("Evidence source count exceeds screened corpus count")


def variable_support(
    units: list[EvidenceUnit],
    corpus_n: int | set[str] | None,
    tiers: dict[str, str] | None = None,
) -> dict[str, Support]:
    """Unweighted source-ID prevalence per variable, with separate quality diagnostic."""
    _validate_corpus_count(units, corpus_n)
    srcs: dict[str, set[str]] = defaultdict(set)
    for u in units:
        srcs[u.variable].add(u.source_id)
    return _summarize_support(srcs, corpus_n, tiers)


def group_support(
    units: list[EvidenceUnit],
    group_map: dict[str, str],
    corpus_n: int | set[str] | None,
    tiers: dict[str, str] | None = None,
) -> dict[str, Support]:
    """Roll up source-ID sets, never add variable counts or source weights twice."""
    _validate_corpus_count(units, corpus_n)
    srcs: dict[str, set[str]] = defaultdict(set)
    members: dict[str, set[str]] = defaultdict(set)
    for u in units:
        group = group_map.get(u.variable, "ungrouped")
        srcs[group].add(u.source_id)
        members[group].add(u.variable)
    return _summarize_support(srcs, corpus_n, tiers, members)


@dataclass
class SelectionRow:
    variable: str
    support_pct: float | None
    n_sources: int
    ml_important: bool
    decision: str  # "include" | "review_low_support" | "include_ml_override"
    note: str = ""


def selection_table(
    var_support: dict[str, Support],
    *,
    floor_pct: float = 20.0,
    ml_important: set[str] | None = None,
) -> list[SelectionRow]:
    """Rank candidate variables and *flag* (don't drop) low-prevalence ones.

    A variable below ``floor_pct`` is flagged ``review_low_support`` for a recorded
    inclusion decision — unless ML importance rescues it (``include_ml_override``),
    which guards against discarding locally-decisive-but-rarely-published variables.
    """
    ml_important = ml_important or set()
    rows: list[SelectionRow] = []
    for v, s in var_support.items():
        if s.pct is None:
            rows.append(
                SelectionRow(
                    v,
                    None,
                    s.n_sources,
                    v in ml_important,
                    "review_unknown_support",
                    "Screened source membership unavailable; prevalence and floor cannot be evaluated",
                )
            )
        elif s.pct >= floor_pct:
            rows.append(
                SelectionRow(v, s.pct, s.n_sources, v in ml_important, "include")
            )
        elif v in ml_important:
            rows.append(
                SelectionRow(
                    v,
                    s.pct,
                    s.n_sources,
                    True,
                    "include_ml_override",
                    "low prevalence but ML-important — keep & flag",
                )
            )
        else:
            rows.append(
                SelectionRow(
                    v,
                    s.pct,
                    s.n_sources,
                    False,
                    "review_low_support",
                    f"below {floor_pct:.0f}% floor — decide & record",
                )
            )
    return rows


def attach_support(row: dict, var_support: dict[str, Support]) -> dict:
    """Add paper_support_pct / n_sources / corpus_n to a T4 row (in place)."""
    v = row.get("variable")
    s = var_support.get(v) if v else None
    if s:
        row["paper_support_pct"] = s.pct
        row["n_sources"] = s.n_sources
        row["corpus_n"] = s.corpus_n
    return row
