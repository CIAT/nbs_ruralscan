"""Tests for check_species — the 2026-07 species-envelope mis-tag guard."""

from __future__ import annotations

import csv

from nbs_ruralscan.schema_tools import check_species

_FIELDS = [
    "evidence_id",
    "source_id",
    "variable",
    "use_role",
    "claim_scope",
    "quote",
    "review_state",
    "reviewer_ok",
]


def _write(tmp_path, rows, citations=None):
    ev = tmp_path / "EV.csv"
    with ev.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in _FIELDS})
    # point the module's SRC at a temp citations file
    src = tmp_path / "SRC.csv"
    with src.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["source_id", "citation"])
        w.writeheader()
        for sid, cit in (citations or {}).items():
            w.writerow({"source_id": sid, "citation": cit})
    check_species.SRC = src
    return ev


def _row(eid, quote, claim_scope="practice_technology", **kw):
    return {
        "evidence_id": eid,
        "source_id": kw.get("source_id", "s1"),
        "variable": "annual_precipitation",
        "use_role": "structural_suitability",
        "claim_scope": claim_scope,
        "quote": quote,
        "review_state": kw.get("review_state", ""),
        "reviewer_ok": kw.get("reviewer_ok", ""),
    }


def _sig(flags, eid):
    return next((f["signal"] for f in flags if f["evidence_id"] == eid), None)


def test_binomial_in_quote_flags_mistag(tmp_path):
    ev = _write(
        tmp_path,
        [_row("ev_faid", "Faidherbia albida tolerates 300-1200 mm annual rainfall.")],
    )
    assert _sig(check_species.check(ev), "ev_faid") == "species_mistag"


def test_taxon_marker_in_quote_flags(tmp_path):
    ev = _write(tmp_path, [_row("ev_sp", "Morus spp. prefer well-drained soils.")])
    assert _sig(check_species.check(ev), "ev_sp") == "species_mistag"


def test_citation_taxon_flags_hint(tmp_path):
    ev = _write(
        tmp_path,
        [_row("ev_hint", "Rainfall of 300-1200 mm is suitable.", source_id="s9")],
        citations={"s9": "Growth of Gliricidia sepium under alley cropping (2021)"},
    )
    assert _sig(check_species.check(ev), "ev_hint") == "species_hint_citation"


def test_correctly_tagged_species_row_skipped(tmp_path):
    ev = _write(
        tmp_path,
        [
            _row(
                "ev_ok",
                "Faidherbia albida tolerates drought.",
                claim_scope="species_specific",
            )
        ],
    )
    assert check_species.check(ev) == []


def test_plain_practice_quote_not_flagged(tmp_path):
    ev = _write(
        tmp_path,
        [_row("ev_practice", "Alley cropping is suitable on slopes below 15 percent.")],
        citations={"s1": "Suitability mapping for agroforestry systems"},
    )
    assert check_species.check(ev) == []


def test_dropped_and_resolved_skipped(tmp_path):
    ev = _write(
        tmp_path,
        [
            _row("ev_d", "Acacia senegal range.", review_state="dropped"),
            _row("ev_r", "Acacia senegal range.", reviewer_ok="true"),
        ],
    )
    assert check_species.check(ev) == []
