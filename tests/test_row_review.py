"""Row-review batch builder + apply path (generated T3/T6 rows on docs/review.html)."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, fname: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / fname)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


builder = _load("build_row_review_batch", "build-row-review-batch.py")
applier = _load("apply_row_review_export", "apply-row-review-export.py")

AF_T6 = ROOT / "schema" / "recipes" / "agroforestry" / "T6_nbs_scorecard.csv"


def _af_rollup_id() -> str:
    if not AF_T6.exists():
        pytest.skip("agroforestry T6 not generated")
    with AF_T6.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if builder.is_rollup(r) and r.get("evidence_ids", "").strip() not in (
                "",
                "[]",
            ):
                return r["record_id"]
    pytest.skip("no agroforestry roll-up row with evidence")


def test_builder_one_agroforestry_rollup(tmp_path):
    rid = _af_rollup_id()
    cards, missing = builder.build_cards("agroforestry", {rid: "check the class"})
    assert missing == []
    assert len(cards) == 1
    c = cards[0]
    for k in (
        "record_id",
        "table",
        "nbs_id",
        "suitability_family_id",
        "scope",
        "target",
        "target_label",
        "class",
        "confidence",
        "evidence_level",
        "agreement_level",
        "data_deficient",
        "conflicting",
        "mechanism",
        "conditionality",
        "statement",
        "family_vote",
        "held_out_of_class",
        "evidence",
        "question",
    ):
        assert k in c, k
    assert (
        c["record_id"] == rid and c["table"] == "T6" and c["nbs_id"] == "agroforestry"
    )
    assert c["suitability_family_id"] == "" and c["scope"] == ""
    assert c["class"]["field"] == "effect_direction" and c["class"]["value"]
    assert "priority" in c["target"]
    assert isinstance(c["held_out_of_class"], list)
    assert c["evidence"], "roll-up row should list its evidence"
    for e in c["evidence"]:
        assert "evidence_id" in e
        if not e.get("missing"):
            for k in (
                "variable",
                "direction",
                "strength",
                "claim_basis",
                "citation",
                "quote",
            ):
                assert k in e, k
            assert len(e["quote"]) <= builder.QUOTE_MAX

    # write: valid JSON with kind "rows", and the index gains a kind-"rows" entry
    (tmp_path / "index.json").write_text(
        json.dumps(
            {
                "batches": [
                    {"id": "old", "title": "t", "n": 1, "file": "review/old.json"}
                ]
            }
        ),
        encoding="utf-8",
    )
    p = builder.write_batch("rows_test", "Rows test", cards, "n", out_dir=tmp_path)
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["kind"] == "rows"
    assert data["batch"]["id"] == "rows_test" and data["batch"]["n"] == 1
    assert data["reasons"] == builder.ROW_REASONS
    assert data["rows"][0]["record_id"] == rid
    idx = json.loads((tmp_path / "index.json").read_text(encoding="utf-8"))
    ids = [b["id"] for b in idx["batches"]]
    assert ids == ["old", "rows_test"]
    assert idx["batches"][-1]["kind"] == "rows"
    assert idx["batches"][-1]["file"] == "review/rows_test.json"


def test_all_rollups_only_takes_rollups():
    if not AF_T6.exists():
        pytest.skip("agroforestry T6 not generated")
    cards, _ = builder.build_cards("agroforestry", all_rollups=True)
    assert cards
    assert all(not c["suitability_family_id"] and not c["scope"] for c in cards)
    assert {c["table"] for c in cards} <= {"T3", "T6", "T6E"}


def _export(path: Path, rows: list[list[str]]) -> Path:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "batch",
                "record_id",
                "nbs_id",
                "table",
                "decision",
                "reason",
                "note",
                "reviewer",
                "date",
            ]
        )
        w.writerows(rows)
    return path


def test_apply_appends_to_temp_log(tmp_path):
    log = tmp_path / "metrics" / "row_review_log.csv"
    exp = _export(
        tmp_path / "export.csv",
        [
            [
                "b",
                "af__x",
                "agroforestry",
                "T6",
                "approve",
                "",
                "fine",
                "pete",
                "2026-10-22T10:00:00Z",
            ],
            [
                "b",
                "af__y",
                "agroforestry",
                "T3",
                "reject",
                "wrong_class",
                "too high",
                "pete",
                "2026-10-22T10:01:00Z",
            ],
            [
                "b",
                "af__z",
                "agroforestry",
                "T6",
                "hold",
                "",
                "ask Namita",
                "pete",
                "2026-10-22T10:02:00Z",
            ],
            [
                "b",
                "af__bad",
                "agroforestry",
                "T6",
                "reject",
                "smuggled_number",
                "",
                "pete",
                "2026-10-22T10:03:00Z",
            ],
        ],
    )
    out = applier.apply_export(exp, log)
    assert out["appended"] == 3
    assert [r[0] for r in out["skipped"]] == ["af__bad"]
    assert {r["record_id"] for r in out["todo"]} == {"af__y", "af__z"}
    with log.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        assert rd.fieldnames == applier.LOG_COLS
        logged = list(rd)
    assert [r["record_id"] for r in logged] == ["af__x", "af__y", "af__z"]
    assert logged[1]["reason"] == "wrong_class" and logged[1]["table"] == "T3"

    # re-applying the same export appends nothing; a new decision appends once, no new header
    assert applier.apply_export(exp, log)["appended"] == 0
    exp2 = _export(
        tmp_path / "export2.csv",
        [
            [
                "b",
                "af__z",
                "agroforestry",
                "T6",
                "approve",
                "",
                "",
                "namita",
                "2026-10-23T09:00:00Z",
            ]
        ],
    )
    assert applier.apply_export(exp2, log)["appended"] == 1
    text = log.read_text(encoding="utf-8")
    assert text.count("date,record_id") == 1
    assert len(text.strip().splitlines()) == 5


def test_apply_dry_run_writes_nothing(tmp_path):
    log = tmp_path / "row_review_log.csv"
    exp = _export(
        tmp_path / "e.csv",
        [["b", "af__x", "agroforestry", "T6", "approve", "", "", "pete", "2026-10-22"]],
    )
    out = applier.apply_export(exp, log, dry_run=True)
    assert out["would_append"] == 1 and out["appended"] == 0
    assert not log.exists()


# ── at-a-glance (rapid triage layer) ─────────────────────────────────────────────────


def test_at_a_glance_present_on_real_rollups():
    if not AF_T6.exists():
        pytest.skip("agroforestry T6 not generated")
    cards, _ = builder.build_cards("agroforestry", all_rollups=True)
    for c in cards:
        g = c["at_a_glance"]
        for k in (
            "headline",
            "statement_short",
            "basis",
            "top_source_share",
            "income_mix",
            "family_vote_line",
            "red_flags",
        ):
            assert k in g, (c["record_id"], k)
        assert "ev_" not in g["statement_short"]
        # header must never contradict itself
        if g["headline"] == "CONFLICTING":
            assert "evidence conflicts" in g["statement_short"]
        if g["headline"] == "DATA DEFICIENT":
            assert "not enough evidence" in g["statement_short"]
        assert isinstance(g["red_flags"], list)


def _ev(eid, sid, basis="primary_measured", design="observational", income="low"):
    return {
        "evidence_id": eid,
        "source_id": sid,
        "claim_basis": basis,
        "relationship": json.dumps({"direction": "positive", "design": design}),
        "context": json.dumps({"income_group": income}),
        "use_role": "nbs_effect",
        "review_state": "",
    }


def test_red_flags_fire_on_constructed_row():
    ev = {
        "ev_a": _ev("ev_a", "s1", basis="cited_secondary", income="high"),
        "ev_b": _ev("ev_b", "s1", basis="cited_secondary", income="high"),
        "ev_c": _ev("ev_c", "s1", basis="cited_secondary", income="high"),
    }
    src = {
        "s1": {
            "citation": "Smith, J. et al. (2020). A paper.",
            "benchmark_tier": "high",
        }
    }
    j = {
        "statement": "agroforestry slightly increases x [ev_a]. Second sentence.",
        "maladaptation": {"n_units": 1, "n_sources": 1, "ids": ["ev_a"]},
        "family_vote": {
            "votes": [
                {
                    "family": "agroforestry__regeneration_farmland",
                    "label": "strong_positive",
                },
                {
                    "family": "agroforestry__planted_silvoarable",
                    "label": "conflicting_evidence",
                },
            ]
        },
    }
    g = builder.at_a_glance(
        "slight_positive",
        "very_high",
        j,
        ["ev_a", "ev_b", "ev_c"],
        ev,
        src,
        "agroforestry",
    )
    for f in (
        "rests on 1 source",
        "mostly second-hand",
        "HIC-dominated",
        "no LIC/LMIC evidence",
        "weak class but high confidence",
        "harm units present",
    ):
        assert f in g["red_flags"], f
    assert (
        "single source carries >40%" not in g["red_flags"]
    )  # one source is its own flag
    assert g["headline"] == "slight positive · very high"
    assert g["top_source_share"]["share"] == 1.0
    assert g["top_source_share"]["citation"] == "Smith et al. 2020"
    assert g["family_vote_line"] == "regeneration +3 · silvoarable ±"
    assert g["basis"]["n_units"] == 3 and g["basis"]["n_sources"] == 1
    assert g["income_mix"]["HIC"] == 1.0

    # conflicting / data-deficient headlines + flags; two sources → top-share flag
    ev["ev_d"] = _ev("ev_d", "s2", design="practitioner_rating")
    src["s2"] = {
        "citation": "Doe (2019)",
        "benchmark_tier": "low",
        "source_category": "grey",
    }
    g2 = builder.at_a_glance(
        "conflicting_evidence",
        "medium",
        {"conflicting": True},
        ["ev_a", "ev_d"],
        ev,
        src,
    )
    assert g2["headline"] == "CONFLICTING" and "conflicting" in g2["red_flags"]
    assert "single source carries >40%" in g2["red_flags"]
    g3 = builder.at_a_glance("", "", {"data_deficient": True}, [], ev, src)
    assert g3["headline"] == "DATA DEFICIENT" and "data deficient" in g3["red_flags"]


def test_statement_agrees_with_headline_on_reclassed_row():
    """A row re-classed by the family vote: the engine statement still describes the
    POOLED class ("strongly reduces"); statement_short must follow the row's own class."""
    ev = {f"ev_{k}": _ev(f"ev_{k}", f"s{k}") for k in range(3)}
    src = {
        f"s{k}": {"citation": f"A{k} (2020)", "benchmark_tier": "high"}
        for k in range(3)
    }
    j = {
        "statement": "agroforestry strongly reduces production_gap in KEN, NER, MLI, BFA.",
        "conflicting": True,
        "maladaptation": {"n_units": 4, "n_sources": 2, "ids": ["ev_0"]},
        "family_vote": {
            "votes": [
                {
                    "family": "agroforestry__regeneration_farmland",
                    "label": "strong_positive",
                },
                {
                    "family": "agroforestry__silvopastoral",
                    "label": "conflicting_evidence",
                },
            ],
            "pooled_label": "strong_positive",
            "outcome": "conflicting_evidence",
        },
    }
    g = builder.at_a_glance(
        "conflicting_evidence",
        "high",
        j,
        list(ev),
        ev,
        src,
        "agroforestry",
        table="T6",
        target={"priority": "production_gap"},
        nbs_label="Agroforestry",
    )
    assert g["headline"] == "CONFLICTING"
    assert "strongly" not in g["statement_short"]
    assert g["statement_short"] == (
        "Agroforestry → production gap: evidence conflicts — sub-practices disagree "
        "(regeneration +3 · silvopastoral ±) · harm reported in 2 sources"
    )


def test_statement_templates():
    ev = {
        "ev_a": _ev("ev_a", "s1"),
        "ev_b": _ev("ev_b", "s2", basis="expert_assertion"),
    }
    src = {"s1": {"benchmark_tier": "high"}, "s2": {"benchmark_tier": "high"}}
    t6 = builder.at_a_glance(
        "moderate_positive",
        "high",
        {},
        ["ev_a", "ev_b"],
        ev,
        src,
        "agroforestry",
        table="T6",
        target={"priority": "biodiversity_priority"},
        nbs_label="Agroforestry",
    )
    assert t6["statement_short"] == (
        "Agroforestry → biodiversity priority: moderately positive "
        "(high confidence; 2 units, 2 sources)"
    )
    assert t6["headline"].startswith("moderate positive")
    t3 = builder.at_a_glance(
        "low",
        "high",
        {},
        ["ev_a"],
        ev,
        src,
        "agroforestry",
        table="T3",
        target={
            "hazard": "drought",
            "farming_system": "all",
            "risk_role": "livelihood_mitigation",
        },
        nbs_label="Agroforestry",
    )
    assert t3["statement_short"] == (
        "Agroforestry — protects farmers from drought (all farming systems): low mitigation "
        "(high confidence; 1 unit, 1 source)"
    )
    dd = builder.at_a_glance(
        "",
        "",
        {"data_deficient": True},
        ["ev_b"],
        ev,
        src,
        "agroforestry",
        table="T3",
        target={"hazard": "fire", "farming_system": "all", "risk_role": "asset_threat"},
        nbs_label="Agroforestry",
    )
    assert dd["headline"] == "DATA DEFICIENT"
    assert dd["statement_short"] == (
        "Agroforestry — threat to the works from fire: not enough evidence to state a class "
        "(1 source, none measured)"
    )
    na = builder.at_a_glance(
        "",
        "high",
        {},
        ["ev_a"],
        ev,
        src,
        "agroforestry",
        table="T3",
        target={
            "hazard": "flood",
            "farming_system": "all",
            "risk_role": "asset_threat",
        },
    )
    assert (
        na["statement_short"]
        == "Agroforestry — threat to the works from flood: not assessed"
    )


def test_batch_carries_display_vocab(tmp_path):
    """The batch ships the controlled display vocabulary the page renders labels from."""
    builder.write_batch("vocab_test", "t", [], out_dir=tmp_path)
    data = json.loads((tmp_path / "vocab_test.json").read_text(encoding="utf-8"))
    v = data["vocab"]
    rr = v["risk_role"]["livelihood_mitigation"]
    assert rr["ttl_label"] == "Protects farmers from <hazard>"
    assert set(rr) == {"label", "ttl_label", "definition", "source_ref", "source_url"}
    assert v["confidence"]["high"]["source_url"].startswith("https://")
    assert "data_deficient" in v["row_state"]


def _prio_card(cls="moderate", conf="high", dd=False, flags=()):
    return {
        "class": {"field": "effect_direction", "value": cls},
        "confidence": conf,
        "data_deficient": dd,
        "evidence": [
            {
                "evidence_id": "ev_a",
                "citation": "Smith, J. (2020). A paper.",
                "source_id": "smith20",
            }
        ],
        "at_a_glance": {"red_flags": list(flags)},
    }


def test_priority_none_without_inputs():
    assert builder.priority(_prio_card(), None, None) is None


def test_priority_fragile_confident_row_ranks_and_names_unit():
    frag = {"n_units": 5, "n_pivotal": 2, "pivotal": [("ev_a", "conflicting_evidence")]}
    p = builder.priority(_prio_card(), frag, None)
    assert p["level"] == "medium"
    sev = {"verdict": "concern", "severity": 2, "why": "Ratings only."}
    assert builder.priority(_prio_card(), frag, sev)["level"] == "high"
    assert any("ev_a" in w and "conflicting evidence" in w for w in p["why"])
    assert any("confidence" in w for w in p["why"])


def test_priority_second_reader_concern_dominates_and_consistent_is_low():
    sev = {"verdict": "concern", "severity": 3, "why": "Unit X is a bundle."}
    assert builder.priority(_prio_card(conf="low"), None, sev)["level"] == "high"
    ok = {"verdict": "consistent", "severity": 0, "why": "Signs agree."}
    p = builder.priority(_prio_card(conf="low"), None, ok)
    assert p["level"] == "low" and p["why"][0].startswith("Second reader found")


def test_priority_data_deficient_flip_counts_half():
    frag = {"n_units": 1, "n_pivotal": 1, "pivotal": [("ev_a", "row gone")]}
    dd = builder.priority(_prio_card(cls="data_deficient", dd=True), frag, None)
    full = builder.priority(_prio_card(conf="low"), frag, None)
    assert dd["score"] < full["score"]


def test_load_fragility_parses_pivots(tmp_path):
    p = tmp_path / "f.csv"
    p.write_text(
        "record_id,class,n_units,n_pivotal,pivotal_units\n"
        "r1,moderate,4,2,ev_a -> low; ev_b -> row gone\n",
        encoding="utf-8",
    )
    f = builder.load_fragility(p)
    assert f["r1"]["pivotal"] == [("ev_a", "low"), ("ev_b", "row gone")]
