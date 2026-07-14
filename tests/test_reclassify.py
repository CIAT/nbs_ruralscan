"""apply_decisions must handle the 2026-07 `reclassify` decision: retag a species/crop
claim (claim_scope + taxon) and KEEP it active — never drop. Also un-drops a previously
dropped row so wrongly-dropped species evidence is recovered + banked for reuse."""

import csv

from nbs_ruralscan.schema_tools import review


def _setup(tmp_path, monkeypatch):
    ev = tmp_path / "EV.csv"
    ev.write_text(
        "evidence_id,source_id,claim_scope,taxon,attribution,review_state,reviewer_ok\n"
        "e_active,s1,practice_technology,,note,,\n"
        "e_dropped,s2,practice_technology,,[dropped 2026-07 by x; reason:species_envelope] old,dropped,\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(review, "EV", ev)
    monkeypatch.setattr(review, "LOG", tmp_path / "review_log.csv")
    return ev


def test_reclassify_retags_and_keeps(tmp_path, monkeypatch):
    ev = _setup(tmp_path, monkeypatch)
    res = review.apply_decisions(
        {
            "e_active": {
                "decision": "reclassify",
                "reason": "species_envelope",
                "claim_scope": "species_specific",
                "taxon": "Faidherbia albida",
            }
        },
        reviewer="tester",
    )
    assert res["reclassified"] == 1
    by = {r["evidence_id"]: r for r in csv.DictReader(ev.open(encoding="utf-8"))}
    row = by["e_active"]
    assert row["claim_scope"] == "species_specific"
    assert row["taxon"] == "Faidherbia albida"
    assert row["review_state"] == ""  # kept active, NOT dropped
    assert row["reviewer_ok"] == "true"


def test_reclassify_undrops_wrongly_dropped_species(tmp_path, monkeypatch):
    ev = _setup(tmp_path, monkeypatch)
    review.apply_decisions(
        {
            "e_dropped": {
                "decision": "reclassify",
                "claim_scope": "crop_specific",
                "taxon": "Coffea arabica",
            }
        },
        reviewer="tester",
    )
    by = {r["evidence_id"]: r for r in csv.DictReader(ev.open(encoding="utf-8"))}
    row = by["e_dropped"]
    assert row["review_state"] == ""  # un-dropped → back in the register (species lane)
    assert row["claim_scope"] == "crop_specific"
    assert row["taxon"] == "Coffea arabica"
