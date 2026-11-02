"""T3/T6 AOI row selection + flat view (runtime/effect_rows.py)."""

from __future__ import annotations

from pathlib import Path

from nbs_ruralscan.runtime import effect_rows as E

ROOT = Path(__file__).resolve().parents[1]


def _t3(rid, fs="all", st="", sid="", tc="adjacent", groups=None, fam=""):
    r = {
        "record_id": rid,
        "nbs_id": "nbs",
        "hazard_type": "drought",
        "farming_system": fs,
        "risk_role": "livelihood_mitigation",
        "applicability": {
            "transfer_class": tc,
            "income_groups": groups or {"low": 2},
            "n_sources_in_scope": 2,
        },
    }
    if st:
        r["scope_type"], r["scope_id"] = st, sid
    if fam:
        r["suitability_family_id"] = fam
    return r


def _rid(r):
    assert r.row is not None
    return r.row["record_id"]


ROWS = [
    _t3("g_all", tc="adjacent", groups={"low": 1, "high": 3}),
    _t3("g_ap", fs="agro_pastoral", tc="in_context"),
    _t3("hic_all", st="income_group", sid="high", tc="in_context", groups={"high": 2}),
    _t3("fam_all", fam="nbs__f1", tc="in_context"),
]


def test_farming_system_row_beats_all():
    r = E.resolve(
        ROWS,
        "nbs",
        {"income_group": "low", "farming_system": "agro_pastoral"},
        hazard_type="drought",
    )
    assert r.status == "ok" and _rid(r) == "g_ap"


def test_unmatched_farming_system_falls_back_to_all():
    r = E.resolve(
        ROWS,
        "nbs",
        {"income_group": "low", "farming_system": "tree_perennial"},
        hazard_type="drought",
    )
    assert _rid(r) == "g_all" and r.transfer_basis == "stored"


def test_income_scope_row_wins_for_matching_band():
    r = E.resolve(ROWS, "nbs", {"income_group": "high"}, hazard_type="drought")
    assert _rid(r) == "hic_all" and r.scope_matched == "income_group-high"


def test_global_row_recomputed_for_non_target_band():
    # 1 low + 3 high sources, AOI upper_middle: low→1, high→2 → 0.75 far → out_of_context
    rows = [_t3("g_all", groups={"low": 1, "high": 3})]
    r = E.resolve(rows, "nbs", {"income_group": "upper_middle"}, hazard_type="drought")
    assert r.transfer_basis == "source_counts"
    assert r.status == "no_applicable_evidence" and _rid(r) == "g_all"


def test_global_out_of_context_is_a_gap():
    rows = [_t3("g_all", tc="out_of_context", groups={"high": 2})]
    r = E.resolve(rows, "nbs", {"income_group": "low"}, hazard_type="drought")
    assert r.status == "no_applicable_evidence" and "high 2" in r.note


def test_family_and_missing_cell():
    r = E.resolve(
        ROWS, "nbs", {"income_group": "low"}, hazard_type="drought", family="nbs__f1"
    )
    assert _rid(r) == "fam_all"
    assert E.resolve(ROWS, "nbs", {}, hazard_type="flood").status == "no_row"


def test_flat_view_covers_every_row():
    text = E.build_flat(ROOT / "schema")
    n = sum(len(E.load_rows(ROOT / "schema", t)) for t in E.TABLES)
    assert text.count("\n") == n + 1
    assert text.splitlines()[0].split(",") == E.FLAT_COLUMNS
