"""SRCH search-protocol register + the ledger gate (search must be logged, not claimed)."""

import csv

import pytest

from nbs_ruralscan.schema_tools import ledger as L
from nbs_ruralscan.schema_tools import search_log as S


def test_has_search_family_resolution(tmp_path):
    p = tmp_path / "SRCH.csv"
    S.log_search(
        nbs="agroforestry",
        table="T4",
        category="grey",
        search_terms="x",
        ruleset_version="v1.0",
        path=p,  # family='' = table-level
    )
    # table-level row covers any family + the empty case
    assert S.has_search("agroforestry", "T4", "grey", "", path=p)
    assert S.has_search(
        "agroforestry", "T4", "grey", "agroforestry__silvopastoral", path=p
    )
    # different table/category not covered
    assert not S.has_search("agroforestry", "T3", "grey", "", path=p)


def test_log_search_validates(tmp_path):
    p = tmp_path / "SRCH.csv"
    with pytest.raises(ValueError):
        S.log_search(
            nbs="a",
            table="BAD",
            category="grey",
            search_terms="x",
            ruleset_version="v1.0",
            path=p,
        )
    with pytest.raises(ValueError):
        S.log_search(
            nbs="a",
            table="T4",
            category="grey",
            search_terms="",
            ruleset_version="v1.0",
            path=p,
        )
    with pytest.raises(ValueError):  # ruleset_version required
        S.log_search(
            nbs="a",
            table="T4",
            category="grey",
            search_terms="x",
            ruleset_version="",
            path=p,
        )
    row = S.log_search(
        nbs="agroforestry",
        table="T4",
        category="grey",
        search_terms="FMNR suitability",
        ruleset_version="v1.0",
        family="agroforestry__regeneration_farmland",
        path=p,
    )
    assert row["search_id"].endswith(row["search_date"])
    assert "regeneration_farmland" in row["search_id"]


def _mini_schema(tmp_path):
    reg = tmp_path / "registers"
    reg.mkdir(parents=True)
    with (reg / "EV_evidence_register.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(
            [
                "evidence_id",
                "nbs_id",
                "use_role",
                "source_id",
                "review_state",
                "suitability_family_id",
                "reviewer_ok",
            ]
        )
        w.writerow(
            [
                "e1",
                "agroforestry",
                "structural_suitability",
                "s1",
                "",
                "agroforestry__planted_silvoarable",
                "",
            ]
        )
    with (reg / "SRC_source_register.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["source_id", "source_category"])
        w.writerow(["s1", "stock"])
    return tmp_path


def test_ledger_gate_requires_srch(tmp_path, monkeypatch):
    schema = _mini_schema(tmp_path)
    monkeypatch.setattr(L, "LEDGER", tmp_path / "ledger.csv")
    L.mark(
        "agroforestry", "T4", "stock", "searched", "done"
    )  # claim a search, no SRCH yet
    errs = L.check(schema)
    assert any("no SRCH" in e for e in errs)  # gate fires

    # log the protocol → gate clears
    S.log_search(
        nbs="agroforestry",
        table="T4",
        category="stock",
        search_terms="agroforestry suitability stocktake",
        ruleset_version="v1.0",
        path=schema / "registers" / "SRCH_search_register.csv",
    )
    assert not any("no SRCH" in e for e in L.check(schema))
