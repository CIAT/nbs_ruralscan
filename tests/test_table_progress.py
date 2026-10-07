"""T3/T6 pipeline-position report (docs/table_progress.json)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from nbs_ruralscan.schema_tools import table_progress as tp

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema"
COMMITTED = ROOT / "docs" / "table_progress.json"


def _walk_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _walk_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_keys(v)


def test_build_is_deterministic_and_unstamped():
    a, b = tp.build(SCHEMA), tp.build(SCHEMA)
    assert a == b
    assert "build" not in a
    keys = set(_walk_keys(a["cells"]))
    assert "timestamp" not in keys and "git_commit" not in keys


def test_shape():
    out = tp.build(SCHEMA)
    assert out["meta"]["stages"] == tp.STAGES
    assert set(out["meta"]["rules"]) == set(tp.STAGES)
    assert sorted(out["cells"]) == sorted(tp.NBS)
    for nbs in tp.NBS:
        assert sorted(out["cells"][nbs]) == ["T3", "T6"]
        for tbl in tp.TABLES:
            cell = out["cells"][nbs][tbl]
            assert list(cell["stages"]) == tp.STAGES
            for s in tp.STAGES:
                assert cell["stages"][s]["status"] in tp.STATUSES
            assert 0 <= cell["completion"]["pct"] <= 100
            for reason in cell["blockers"]["pending_by_reason"]:
                assert reason in out["meta"]["blocker_reasons"]


def test_wetland_has_no_outputs_yet():
    cell = tp.build(SCHEMA)["cells"]["wetland_management"]["T3"]
    syn = cell["stages"]["synthesised"]
    assert syn["status"] == "not_started" and syn["rows"] == 0
    assert "no T3/T6 outputs yet" in cell["blockers"]["warnings"]


def test_status_helpers():
    assert tp.status_acquired({"discovered": 4, "pending": 0, "acquired": 4}) == "done"
    assert tp.status_acquired({"discovered": 0, "pending": 0}) == "not_started"
    assert tp.status_acquired({"discovered": 4, "pending": 1}) == "in_progress"
    assert tp.status_prose({"with_prose": 3, "total": 5}) == "in_progress"
    assert tp.status_prose({"with_prose": 5, "total": 5}) == "done"
    assert tp.status_prose({"with_prose": 0, "total": 5}) == "not_started"
    assert tp.status_benchmarked({"seed": True, "benchmark_md": False}) == "in_progress"
    assert tp.status_benchmarked({"seed": True, "benchmark_md": True}) == "done"
    assert (
        tp.status_benchmarked({"seed": False, "benchmark_md": False}) == "not_started"
    )
    assert tp.status_searched(list(tp.CATEGORIES), True) == "done"
    assert tp.status_searched(["stock"], True) == "in_progress"
    assert tp.status_searched([], False) == "not_started"
    syn = {
        "rows": 5,
        "report_stale": False,
        "unmapped_variables": [],
        "parked_families": [],
    }
    assert tp.status_synthesised(syn) == "done"
    assert tp.status_synthesised({**syn, "report_stale": True}) == "in_progress"
    assert tp.status_synthesised({**syn, "rows": 0}) == "not_started"


def test_completion():
    assert tp.completion(["done"] * 7)["pct"] == 100
    c = tp.completion(["done"] * 3 + ["in_progress"] * 2 + ["not_started"] * 2)
    assert c == {"pct": 57, "n_done": 3, "n_in_progress": 2}


def test_blocker_reason():
    assert tp.blocker_reason({"blocker": "webfetch_403_bot_block"}) == "needs_human"
    assert tp.blocker_reason({"blocker": "paywalled (Springer)"}) == "paywalled"
    assert (
        tp.blocker_reason({"blocker": "", "access_status": "paywalled"}) == "paywalled"
    )
    assert (
        tp.blocker_reason({"blocker": "no candidate URL yielded a PDF"})
        == "tool_failed"
    )
    assert (
        tp.blocker_reason({"blocker": "", "access_status": "oa", "status": "pending"})
        == "oa_not_fetched"
    )
    assert tp.blocker_reason({"blocker": "", "access_status": ""}) == "other"


def test_iter_queue(tmp_path):
    q = tmp_path / "queue.csv"
    q.write_text(
        "source_id,nbs_id,tables,status\n"
        "a,agroforestry|riparian_buffer,T3|T6,pending\n"
        "b,agroforestry,T6,acquired\n"
        "a,wetland_management,T4,acquired\n"
        ",agroforestry,T3,pending\n",
        encoding="utf-8",
    )
    rows = tp.iter_queue(q)
    assert [r["source_id"] for r, _, _ in rows] == ["a", "b"]
    _, nbs_ids, tables = rows[0]
    assert nbs_ids == {"agroforestry", "riparian_buffer"}
    assert tables == {"T3", "T6"}


def test_write_check_ignores_build_stamp(tmp_path):
    dest = tmp_path / "table_progress.json"
    shutil.copy(COMMITTED, dest)
    data = json.loads(dest.read_text(encoding="utf-8"))
    data["build"] = {"timestamp": "1970-01-01T00:00:00+00:00", "git_commit": "x"}
    dest.write_text(json.dumps(data), encoding="utf-8")
    assert tp.write(SCHEMA, check=True, dest=dest) == []
    assert tp.write(SCHEMA, check=False, dest=dest) == []  # no stamp refresh churn
    data["cells"]["agroforestry"]["T3"]["completion"]["pct"] = -1
    dest.write_text(json.dumps(data), encoding="utf-8")
    assert tp.write(SCHEMA, check=True, dest=dest) == [dest]
