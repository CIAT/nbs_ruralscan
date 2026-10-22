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
    assert {c["table"] for c in cards} <= {"T3", "T6"}


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
