"""Historical deferred migration and direct register edits on disposable roots."""

import csv
from datetime import date
import json
import os
from pathlib import Path

import pytest

from nbs_ruralscan.schema_tools import migrate_effects as m


def table(path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def seed(root):
    regs = root / "schema/registers"
    src = regs / m.SRC_CSV.name
    source = dict(
        source_id="castle_sr_2021",
        vars_extracted="old",
        source_kind="paper",
        study_country="Kenya",
        benchmark_tier="HIGH",
        extraction_status="pending",
        extraction_run_id="",
        extraction_date="",
        extractor="",
    )
    table(src, list(source), [source, dict(source, source_id="untouched")])
    unit = dict(
        evidence_id="u-one",
        source_id="castle_sr_2021",
        variable="yield",
        use_role="nbs_effect",
        nbs_id="agroforestry",
        relationship={"direction": "positive"},
        context={"country": "Kenya"},
        quote="Measured café yield",
        page=3,
        reviewer_ok="true",
        review_state="",
        ruleset_version="early",
    )
    ev = regs / m.EV_CSV.name
    table(
        ev,
        list(unit),
        [
            dict(
                unit,
                evidence_id="u-old",
                variable="slope",
                relationship="",
                context="",
                use_role="structural_suitability",
            )
        ],
    )
    archive = regs / "_deferred" / m.DEFERRED.name
    archive.parent.mkdir()
    archive.write_text(
        json.dumps(
            [
                unit,
                dict(
                    unit,
                    evidence_id="u-two",
                    variable="retired",
                    review_state="dropped",
                ),
                dict(unit, evidence_id="u-ignore", source_id="untouched"),
            ]
        )
    )
    table(
        regs / m.BANDS_CSV.name, ["metric", "strength_class", "abs_min", "abs_max"], []
    )
    table(
        root / "schema/lookups" / m.INCOME_CSV.name,
        ["iso3", "income_group", "country_name"],
        [dict(iso3="KEN", income_group="test_group", country_name="Kenya")],
    )
    table(root / "schema" / m.T7_CSV.name, ["context_type", "context_id"], [])
    return ev, src, archive


def read_table(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def data_bytes(root):
    return {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_relocated_dry_run_write_and_reviewed_rerun(tmp_path, capsys):
    ev, src, archive = seed(tmp_path)
    before = data_bytes(tmp_path)
    assert m.main(["--data-root", str(tmp_path), "--dry-run"]) == 0
    stdout = capsys.readouterr().out
    assert '"selected": 2' in stdout and '"evidence_id": "u-two"' in stdout
    assert data_bytes(tmp_path) == before
    result = m.run(root=tmp_path)
    assert result["appended"] == 2 and result["dropped_state_preserved"] == 1
    assert result["vars_extracted_changed"] == {"castle_sr_2021": "slope|yield"}
    assert result["src_backfill"] == {
        "castle_sr_2021": {
            "study_income_group": "test_group",
            "venue_type": "peer_reviewed_journal",
            "benchmark_tier": "high",
        }
    }
    manifest = tmp_path / result["manifest"]
    assert manifest.read_text().splitlines()[1:] == ["u-one", "u-two"]
    assert archive.read_bytes() == before[archive.relative_to(tmp_path)]
    rows = read_table(ev)
    rows[1]["reviewer_ok"] = "false"
    table(ev, list(rows[0]), rows)
    snapshot = data_bytes(tmp_path)
    assert m.run(root=tmp_path)["appended"] == 0
    assert data_bytes(tmp_path) == snapshot
    assert read_table(src)[0]["extraction_status"] == "pending"


@pytest.mark.parametrize("existing_manifest", [True, False])
def test_failure_after_installing_manifest_restores_both_registers(
    tmp_path, monkeypatch, existing_manifest
):
    ev, src, archive = seed(tmp_path)
    manifest = archive.with_name(f"migrated_{date.today().isoformat()}.txt")
    if existing_manifest:
        manifest.write_text(
            m._merge_manifest(
                manifest, m._manifest_heading(archive, archive.read_bytes()), ["u-old"]
            )
        )
    original = data_bytes(tmp_path)
    replace = os.replace
    observed = []

    def interrupt(a, b):
        replace(a, b)
        if Path(b) == manifest and not observed:
            observed.append((ev.read_bytes(), src.read_bytes()))
            raise OSError("simulated late manifest failure")

    monkeypatch.setattr(os, "replace", interrupt)
    with pytest.raises(OSError, match="late manifest failure"):
        m.run(root=tmp_path)
    assert observed and all(
        new != original[p.relative_to(tmp_path)]
        for new, p in zip(observed[0], (ev, src), strict=True)
    )
    assert data_bytes(tmp_path) == original


@pytest.mark.parametrize("write", [True, False])
def test_archive_changed_while_transforming_refuses_the_entire_run(
    tmp_path, monkeypatch, write
):
    ev, src, archive = seed(tmp_path)
    before = data_bytes(tmp_path)
    transform = m.migrate_unit

    def change(*args):
        result = transform(*args)
        archive.write_text("[]")
        return result

    monkeypatch.setattr(m, "migrate_unit", change)
    with pytest.raises(ValueError, match="changed"):
        m.run(root=tmp_path, write=write)
    before[archive.relative_to(tmp_path)] = b"[]"
    assert data_bytes(tmp_path) == before


def test_direct_resync_refuses_a_changed_evidence_input(tmp_path, monkeypatch):
    ev, src, _ = seed(tmp_path)
    src_before = src.read_bytes()
    write_sources = m.write_table

    def change(*args):
        write_sources(*args)
        ev.write_bytes(ev.read_bytes() + b"\n")

    monkeypatch.setattr(m, "write_table", change)
    with pytest.raises(ValueError, match="changed"):
        m.resync_vars_extracted({"castle_sr_2021"}, src, ev)
    assert src.read_bytes() == src_before


@pytest.mark.parametrize("action", ["backfill", "stamp", "resync"])
def test_direct_writers_preserve_malformed_sources(tmp_path, action):
    ev, src, _ = seed(tmp_path)
    src.write_bytes(src.read_bytes() + b"too,few\n")
    before = src.read_bytes()
    args = {"castle_sr_2021"}
    with pytest.raises(ValueError, match="Malformed CSV row"):
        if action == "backfill":
            m.backfill_src_context(
                args, src, tmp_path / "schema/lookups" / m.INCOME_CSV.name
            )
        elif action == "resync":
            m.resync_vars_extracted(args, src, ev)
        else:
            m.stamp_extracted(args, "run-id", "extractor", "2026-11-09", src)
    assert src.read_bytes() == before


def test_archive_cannot_alias_a_write_target(tmp_path):
    ev, _, _ = seed(tmp_path)
    before = data_bytes(tmp_path)
    with pytest.raises(ValueError, match="alias"):
        m.run(root=tmp_path, deferred=ev)
    assert before == data_bytes(tmp_path)


def test_bounded_runs_share_dated_manifest_without_overwriting_previous_ids(tmp_path):
    _, _, archive = seed(tmp_path)
    first = m.run(root=tmp_path)
    path = tmp_path / first["manifest"]
    assert m.run({"untouched"}, root=tmp_path)["appended"] == 1
    expected = path.read_bytes()
    assert path.read_text().splitlines()[1:] == ["u-one", "u-two", "u-ignore"]
    assert m.run(root=tmp_path)["appended"] == 0 and path.read_bytes() == expected
    other = tmp_path / "different.json"
    other.write_bytes(archive.read_bytes())
    before = data_bytes(tmp_path)
    with pytest.raises(ValueError, match="different archive"):
        m.run(root=tmp_path, deferred=other)
    assert data_bytes(tmp_path) == before


def test_reviewed_substantive_correction_blocks_historical_reimport(tmp_path):
    ev, _, _ = seed(tmp_path)
    m.run(root=tmp_path)
    rows = read_table(ev)
    rows[1].update(quote="Subsequent reviewed correction", reviewer_ok="true")
    table(ev, list(rows[0]), rows)
    before = data_bytes(tmp_path)
    with pytest.raises(ValueError, match="existing evidence differs in quote"):
        m.run(root=tmp_path)
    assert data_bytes(tmp_path) == before


@pytest.mark.parametrize("archived", [{}, {"units": []}, ["damaged"]])
def test_malformed_archive_cannot_be_reported_as_an_empty_migration(tmp_path, archived):
    _, _, archive = seed(tmp_path)
    archive.write_text(json.dumps(archived))
    before = data_bytes(tmp_path)
    with pytest.raises(ValueError, match="list of archived evidence units"):
        m.run(root=tmp_path)
    assert data_bytes(tmp_path) == before


def change_day(monkeypatch, day):
    class FixedDay(date):
        @classmethod
        def today(cls):
            return cls.fromisoformat(day)

    monkeypatch.setattr(m, "date", FixedDay)


def test_cross_day_retry_preserves_first_dates_and_reports_selected_ids(
    tmp_path, monkeypatch
):
    ev, src, archive = seed(tmp_path)
    change_day(monkeypatch, "2026-09-30")
    first = m.run(root=tmp_path)
    prior_receipt = tmp_path / first["manifest"]
    original_receipt = prior_receipt.read_bytes()
    original_ev, original_src = ev.read_bytes(), src.read_bytes()
    change_day(monkeypatch, "2026-11-09")
    second = m.run(root=tmp_path)
    assert second["appended"] == 0 and second["selected"] == 2
    assert second["units"] == first["units"]
    today = tmp_path / second["manifest"]
    assert today != prior_receipt and today.read_bytes() == original_receipt
    assert prior_receipt.read_bytes() == original_receipt
    assert ev.read_bytes() == original_ev and src.read_bytes() == original_src
    # A fresh source on the same day keeps the original rows' stamps and expands today's receipt.
    more = m.run({"castle_sr_2021", "untouched"}, root=tmp_path)
    assert more["appended"] == 1 and more["selected"] == 3
    assert [u["evidence_id"] for u in more["units"]] == ["u-one", "u-two", "u-ignore"]
    assert "2026-11-09" in more["units"][-1]["context"]["note"]
    assert more["units"][:2] == first["units"]
    assert today.read_text().splitlines()[1:] == ["u-one", "u-two", "u-ignore"]
    assert prior_receipt.read_bytes() == original_receipt
    assert archive.exists()


@pytest.mark.parametrize(
    "field", ["note", "country", "edited_stamp", "impossible_date"]
)
def test_cross_day_retry_refuses_reviewed_context_and_altered_stamp(
    tmp_path, monkeypatch, field
):
    ev, _, _ = seed(tmp_path)
    change_day(monkeypatch, "2026-09-30")
    m.run(root=tmp_path)
    rows = read_table(ev)
    recorded = json.loads(rows[1]["context"])
    if field == "note":
        recorded["note"] += "; reviewer recorded 2026-09-30"
    elif field == "country":
        recorded["country"] = ["ETH"]
    elif field == "edited_stamp":
        recorded["note"] = recorded["note"].replace(
            "method §10", "reviewer's method §10"
        )
    else:
        recorded["note"] = recorded["note"].replace("2026-09-30", "2026-09-31")
    rows[1]["context"] = json.dumps(recorded)
    table(ev, list(rows[0]), rows)
    before = data_bytes(tmp_path)
    change_day(monkeypatch, "2026-11-09")
    with pytest.raises(ValueError, match="existing evidence differs in context"):
        m.run(root=tmp_path)
    assert before == data_bytes(tmp_path)


def test_active_append_still_compares_migration_date_exactly(tmp_path, monkeypatch):
    ev, _, _ = seed(tmp_path)
    change_day(monkeypatch, "2026-09-30")
    first = m.run(root=tmp_path)
    change_day(monkeypatch, "2026-11-09")
    prospective = m.run(root=tmp_path, write=False)["units"]
    assert first["units"] != prospective
    before = ev.read_bytes()
    with pytest.raises(ValueError, match="existing evidence differs in context"):
        m.append_to_register(prospective, ev)
    assert ev.read_bytes() == before


@pytest.mark.parametrize("write", [False, True])
def test_selected_archived_evidence_needs_a_registered_source(tmp_path, write):
    _, src, _ = seed(tmp_path)
    rows = read_table(src)
    table(src, list(rows[0]), [rows[1]])
    before = data_bytes(tmp_path)
    with pytest.raises(ValueError, match="missing source IDs: castle_sr_2021"):
        m.run(root=tmp_path, write=write)
    assert before == data_bytes(tmp_path)


def test_same_named_changed_archive_and_unverified_legacy_heading_refused(tmp_path):
    _, _, archive = seed(tmp_path)
    result = m.run(root=tmp_path)
    receipt = tmp_path / result["manifest"]
    assert "[sha256=" in receipt.read_text().splitlines()[0]
    alternate = tmp_path / "sibling" / archive.name
    alternate.parent.mkdir()
    alternate.write_bytes(archive.read_bytes() + b" ")
    before = data_bytes(tmp_path)
    with pytest.raises(ValueError, match="different archive"):
        m.run(root=tmp_path, deferred=alternate)
    assert data_bytes(tmp_path) == before
    # A synthetic/changed archive at the "canonical" name cannot adopt a legacy receipt.
    heading, rows = receipt.read_text().split("\n", 1)
    receipt.write_text(
        heading.split(" [sha256=")[0] + heading.split("]", 1)[1] + "\n" + rows
    )
    before = data_bytes(tmp_path)
    with pytest.raises(ValueError, match="different archive"):
        m.run(root=tmp_path)
    assert data_bytes(tmp_path) == before
