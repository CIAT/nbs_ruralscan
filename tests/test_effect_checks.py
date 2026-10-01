"""Deterministic effect-claim checks (ruleset v1.6.0): context keys, bands, crosswalk, account."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from nbs_ruralscan.schema_tools import (
    check_account,
    check_bands,
    check_context,
    check_xw,
)

BANDS = [
    {
        "metric": "smd_hedges_g",
        "strength_class": "slight",
        "abs_min": "0",
        "abs_max": "0.2",
    },
    {
        "metric": "smd_hedges_g",
        "strength_class": "moderate",
        "abs_min": "0.2",
        "abs_max": "0.5",
    },
    {
        "metric": "smd_hedges_g",
        "strength_class": "strong",
        "abs_min": "0.5",
        "abs_max": "",
    },
    {
        "metric": "pct_change",
        "strength_class": "slight",
        "abs_min": "0",
        "abs_max": "10",
    },
]


def _row(
    eid="ev_x", role="nbs_effect", variable="erosion_hazard", ctx=None, rel=None, **kw
):
    r = {
        "evidence_id": eid,
        "use_role": role,
        "variable": variable,
        "context": json.dumps(ctx or {}),
        "relationship": json.dumps(rel or {}),
        "quote": kw.get("quote", "erosion fell by 40 % (n = 12)"),
        "review_state": kw.get("review_state", ""),
    }
    return r


def _write_ev(tmp_path: Path, rows: list[dict]) -> Path:
    p = tmp_path / "EV.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return p


def test_context_check_flags_sprawl_vocab_and_missing_income(tmp_path):
    aez, fs = {"semi_arid"}, {"cropping_rainfed"}
    ok = _row(
        ctx={"country": ["KEN"], "aez": "semi_arid", "income_group": "lower_middle"}
    )
    assert check_context.check_unit(ok, aez, fs) == []
    bad = _row(
        eid="ev_bad",
        ctx={
            "study_region": "Sahel",
            "country": "Kenya",
            "aez": "sahel",
            "farming_system": "millet",
        },
    )
    sigs = sorted(f["signal"] for f in check_context.check_unit(bad, aez, fs))
    assert sigs == [
        "bad_vocab",
        "bad_vocab",
        "bad_vocab",
        "missing_income_group",
        "unknown_context_key",
    ]
    av = _row(eid="ev_av", role="asset_vulnerability", ctx={"income_group": "low"})
    assert [f["signal"] for f in check_context.check_unit(av, aez, fs)] == [
        "missing_hazard_type"
    ]
    # T4 units and dropped units are ignored by check()
    p = _write_ev(
        tmp_path,
        [
            bad,
            _row(eid="ev_t4", role="structural_suitability", ctx={"foo": 1}),
            _row(eid="ev_dr", ctx={"foo": 1}, review_state="dropped"),
        ],
    )
    flags = check_context.check(p, tmp_path / "no_t7.csv")
    assert {f["evidence_id"] for f in flags} == {"ev_bad"}


def test_bands_check_flags_mismatch_and_adjective_strength():
    ok = _row(
        rel={"metric": "smd_hedges_g", "magnitude": 1.16, "strength_class": "strong"}
    )
    assert check_bands.check_unit(ok, BANDS) == []
    mism = _row(
        eid="ev_m",
        rel={"metric": "smd_hedges_g", "magnitude": 0.3, "strength_class": "strong"},
    )
    assert [f["signal"] for f in check_bands.check_unit(mism, BANDS)] == [
        "band_mismatch"
    ]
    adj = _row(
        eid="ev_a",
        rel={
            "metric": "narrative",
            "strength_class": "strong",
            "direction": "negative",
        },
    )
    assert [f["signal"] for f in check_bands.check_unit(adj, BANDS)] == [
        "adjective_strength"
    ]
    unsp = _row(
        eid="ev_u", rel={"metric": "narrative", "strength_class": "unspecified"}
    )
    assert check_bands.check_unit(unsp, BANDS) == []
    bad_metric = _row(eid="ev_bm", rel={"metric": "cohens_d", "magnitude": 1})
    assert [f["signal"] for f in check_bands.check_unit(bad_metric, BANDS)] == [
        "unknown_metric"
    ]
    # ordinal ratings are never adjective flags (their class comes from the adapter)
    ordn = _row(
        eid="ev_o", rel={"metric": "ordinal_rating", "strength_class": "strong"}
    )
    assert check_bands.check_unit(ordn, BANDS) == []


def test_xw_check_reports_no_vont_and_unmapped(tmp_path):
    ev = _write_ev(
        tmp_path,
        [
            _row(eid="e1", variable="erosion_hazard"),
            _row(eid="e2", variable="ecosystem_service"),
            _row(eid="e3", variable="ecosystem_service"),
            _row(eid="e4", variable="mystery_var"),
            _row(eid="e5", role="asset_vulnerability", variable="seedling_mortality"),
            _row(eid="e6", role="structural_suitability", variable="mystery_var"),
        ],
    )
    vont = tmp_path / "VONT.csv"
    vont.write_text(
        "canonical_variable_id\nerosion_hazard\necosystem_service\nseedling_mortality\n",
        encoding="utf-8",
    )
    xw = tmp_path / "XW.csv"
    xw.write_text(
        "ev_variable,target_table,target_key\nerosion_hazard,T6,soil_erosion_risk\n",
        encoding="utf-8",
    )
    flags = check_xw.check(ev, vont, xw)
    assert flags == [
        {"signal": "unmapped", "variable": "ecosystem_service", "n_units": 2},
        {"signal": "no_vont_id", "variable": "mystery_var", "n_units": 1},
    ]


def test_account_check_catches_foreign_numbers_and_ids(tmp_path):
    ev = _write_ev(
        tmp_path,
        [
            _row(
                eid="ev_a",
                quote="erosion fell by 40 % (n = 12)",
                rel={"magnitude": 40, "metric": "pct_change"},
            ),
            _row(eid="ev_b", quote="sediment retention of 60 to 90 %"),
            _row(eid="ev_dropped", quote="x", review_state="dropped"),
        ],
    )
    good = {
        "record_id": "r1",
        "evidence_ids": ["ev_a", "ev_b"],
        "n_sources": 2,
        "applicability": {"n_sources_in_scope": 2, "weight_share_in_context": 0.62},
        "justification": {
            "statement": "riparian_buffer strongly increases soil_erosion_risk benefit (limited evidence, high agreement → medium confidence)",
            "evidence_summary": [
                "ev_a · pct_change=40 percent",
                "ev_b · 60 to 90 % [ev_b]",
            ],
            "agreement_note": "weighted sign agreement 0.62: positive 2 [ev_a, ev_b]; negative 0 []; null 0 []",
            "agreement": 0.62,
        },
    }
    assert check_account.check_row(good, check_account._load_ev(ev)) == []
    bad = json.loads(json.dumps(good))
    bad["record_id"] = "r2"
    bad["evidence_ids"] = ["ev_a", "ev_dropped", "ev_nope"]
    bad["justification"]["statement"] = "reduces erosion by 55 % according to ev_zzz"
    bad["justification"]["evidence_summary"] = []  # isolate the four intended flags
    bad["justification"]["agreement_note"] = ""
    sigs = sorted(
        f["signal"] for f in check_account.check_row(bad, check_account._load_ev(ev))
    )
    assert sigs == [
        "cited_id_not_used",
        "evidence_id_dropped",
        "evidence_id_unknown",
        "number_not_in_evidence",
    ]
    rows = tmp_path / "rows.json"
    rows.write_text(json.dumps([good, bad]), encoding="utf-8")
    assert len(check_account.check(rows, ev)) == 4


def test_account_check_ignores_identifier_digits(tmp_path):
    ev = _write_ev(tmp_path, [_row(eid="ev_a", quote="removal of 40 %")])
    row = {
        "record_id": "r",
        "evidence_ids": ["ev_a"],
        "justification": {
            "evidence_summary": [
                "lee_2004 · smd_hedges_g=40 percent · (SWE; high) [ev_a]"
            ],
            "statement": "riparian_buffer increases soil_erosion_risk (limited evidence)",
        },
    }
    assert check_account.check_row(row, check_account._load_ev(ev)) == []
