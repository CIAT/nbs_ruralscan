"""Variable *support* — literature prevalence of a variable, with hierarchy roll-up.

`paper_support_pct(V)` = share of the family's screened corpus that yields ≥1 evidence
unit for variable V. A *selection* signal (which variables matter), the provenanced,
per-family successor to the stocktake's variable-frequency heatmap — complements ML
importance. It is a **prevalence**, not a truth: a common variable may be convention
(citation echo), a rare one may be locally decisive. So it informs inclusion with a
**soft floor that flags for decision**, never a hard auto-filter (method §6).

Roll-up is **set-union over members**, not a sum: a paper using both slope and elevation
counts once toward "Topographic" prevalence.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from .evidence import EvidenceUnit


@dataclass
class Support:
    key: str  # variable id or group id
    n_sources: int  # distinct sources with ≥1 unit
    corpus_n: int  # denominator: sources screened for the family
    pct: float  # 100 * n_sources / corpus_n
    members: list[str] = field(default_factory=list)  # group members (group-level only)


def _pct(n: int, d: int) -> float:
    return round(100.0 * n / d, 1) if d else 0.0


def variable_support(units: list[EvidenceUnit], corpus_n: int) -> dict[str, Support]:
    """Distinct-source prevalence per canonical variable."""
    srcs: dict[str, set[str]] = defaultdict(set)
    for u in units:
        srcs[u.variable].add(u.source_id)
    return {
        v: Support(
            key=v, n_sources=len(s), corpus_n=corpus_n, pct=_pct(len(s), corpus_n)
        )
        for v, s in sorted(srcs.items(), key=lambda kv: -len(kv[1]))
    }


def group_support(
    units: list[EvidenceUnit], group_map: dict[str, str], corpus_n: int
) -> dict[str, Support]:
    """Roll variable prevalence up to its group (set-union over members)."""
    srcs: dict[str, set[str]] = defaultdict(set)
    members: dict[str, set[str]] = defaultdict(set)
    for u in units:
        g = group_map.get(u.variable, "ungrouped")
        srcs[g].add(u.source_id)
        members[g].add(u.variable)
    return {
        g: Support(
            key=g,
            n_sources=len(s),
            corpus_n=corpus_n,
            pct=_pct(len(s), corpus_n),
            members=sorted(members[g]),
        )
        for g, s in sorted(srcs.items(), key=lambda kv: -len(kv[1]))
    }


@dataclass
class SelectionRow:
    variable: str
    support_pct: float
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
        if s.pct >= floor_pct:
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
