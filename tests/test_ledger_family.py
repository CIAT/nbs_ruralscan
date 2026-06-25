"""Ledger family (sub-practice) dimension — search status logged, not inferred (2026-06-25)."""

from nbs_ruralscan.schema_tools import ledger as L


def test_facts_for_aggregates_or_selects_family():
    facts = {
        ("agroforestry", "T3", "grey", "agroforestry__planted_silvoarable"): {
            "ev": 11,
            "reviewed": 0,
        },
        ("agroforestry", "T3", "grey", "agroforestry__silvopastoral"): {
            "ev": 3,
            "reviewed": 1,
        },
    }
    # specific family
    assert (
        L.facts_for(facts, "agroforestry", "T3", "grey", "agroforestry__silvopastoral")[
            "ev"
        ]
        == 3
    )
    # family='' sums over families
    assert L.facts_for(facts, "agroforestry", "T3", "grey", "")["ev"] == 14
    # a family never searched/extracted → zero (NOT inferred from a sibling family)
    assert (
        L.facts_for(
            facts, "agroforestry", "T3", "grey", "agroforestry__regeneration_farmland"
        )["ev"]
        == 0
    )


def test_mark_family_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(L, "LEDGER", tmp_path / "ledger.csv")
    # a sub-practice-targeted search status, distinct from the table-level row
    L.mark("agroforestry", "T3", "grey", "searched", "done")  # family='' (table-level)
    L.mark(
        "agroforestry",
        "T3",
        "grey",
        "searched",
        "not_started",
        family="agroforestry__regeneration_farmland",
        note="no FMNR-targeted T3 grey search yet",
    )
    rows = L._rows()
    assert len(rows) == 2
    tbl = {
        (r["nbs_id"], r["table"], r["category"], r.get("family", "")): r for r in rows
    }
    assert tbl[("agroforestry", "T3", "grey", "")]["searched"] == "done"
    fam = tbl[("agroforestry", "T3", "grey", "agroforestry__regeneration_farmland")]
    assert fam["searched"] == "not_started"  # logged source-of-truth, not inferred
    assert "FMNR" in fam["note"]
    assert "family" in L.FIELDS
