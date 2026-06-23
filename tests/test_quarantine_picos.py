"""Tests for the PICOS wrong-practice check + auto-quarantine guard (2026-06-23)."""

import csv
import json

from nbs_ruralscan.schema_tools import check_picos, quarantine

_FIELDS = [
    "evidence_id",
    "nbs_id",
    "use_role",
    "quote",
    "reviewer_ok",
    "review_state",
    "attribution",
]


def _write_ev(tmp_path, rows):
    reg = tmp_path / "registers"
    reg.mkdir(parents=True, exist_ok=True)
    with (reg / "EV_evidence_register.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        w = csv.DictWriter(f, fieldnames=_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in _FIELDS})
    return reg / "EV_evidence_register.csv"


def test_picos_flags_reforestation_but_not_agroforestry(tmp_path):
    ev = _write_ev(
        tmp_path,
        [
            {
                "evidence_id": "e1",
                "nbs_id": "agroforestry",
                "use_role": "structural_suitability",
                "quote": "Reforestation on steep slopes above 30% was prioritised.",
            },
            {
                "evidence_id": "e2",  # mentions reforestation BUT also agroforestry -> not flagged
                "nbs_id": "agroforestry",
                "use_role": "structural_suitability",
                "quote": "Unlike reforestation, agroforestry suits slopes up to 30%.",
            },
            {
                "evidence_id": "e3",  # genuine AF claim -> not flagged
                "nbs_id": "agroforestry",
                "use_role": "structural_suitability",
                "quote": "Alley cropping is suitable where slope is below 15%.",
            },
        ],
    )
    flags = {f["evidence_id"] for f in check_picos.check(ev)}
    assert flags == {"e1"}


def test_picos_skips_reviewed_and_non_structural(tmp_path):
    ev = _write_ev(
        tmp_path,
        [
            {
                "evidence_id": "ok1",
                "nbs_id": "agroforestry",
                "use_role": "structural_suitability",
                "quote": "Afforestation programme details.",
                "reviewer_ok": "true",
            },
            {
                "evidence_id": "t6",
                "nbs_id": "agroforestry",
                "use_role": "nbs_effect",
                "quote": "Afforestation programme details.",
            },
        ],
    )
    assert check_picos.check(ev) == []


def test_quarantine_excludes_human_touched(tmp_path):
    schema = tmp_path / "schema"
    _write_ev(
        schema,
        [
            {
                "evidence_id": "junk1",
                "nbs_id": "agroforestry",
                "use_role": "structural_suitability",
                "quote": "The study site is located in northern Kenya.",  # off_scope
            },
            {
                "evidence_id": "human1",
                "nbs_id": "agroforestry",
                "use_role": "structural_suitability",
                "quote": "Reforestation across the catchment.",  # wrong_practice
            },
        ],
    )
    # human already decided on human1 -> must be excluded from auto-quarantine
    (tmp_path / "pipeline" / "review").mkdir(parents=True)
    (tmp_path / "pipeline" / "review" / "decisions.json").write_text(
        json.dumps({"human1": {"peetmate": {"decision": "ok"}}})
    )
    cands = {c["evidence_id"] for c in quarantine.candidates(schema)}
    assert "junk1" in cands
    assert "human1" not in cands

    applied = quarantine.apply(schema)
    assert [a["evidence_id"] for a in applied] == ["junk1"]
    rows = list(
        csv.DictReader((schema / "registers" / "EV_evidence_register.csv").open())
    )
    by = {r["evidence_id"]: r for r in rows}
    assert by["junk1"]["review_state"] == "dropped"
    assert "[AUTO-QUARANTINE" in by["junk1"]["attribution"]
    assert by["human1"]["review_state"] == ""
    # idempotent: a second apply changes nothing more
    assert quarantine.apply(schema) == []
