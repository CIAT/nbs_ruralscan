"""Review batch images, batches and their index publish from one selected data set."""

import csv
import importlib.util
import json
from pathlib import Path

import fitz
import pytest

from nbs_ruralscan.schema_tools import publication


ROOT = Path(__file__).resolve().parents[1]


def script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


units = script("build-review-batch")
rows = script("build-row-review-batch")
apply_rows = script("apply-row-review-export")


def write_csv(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


@pytest.fixture
def example(tmp_path):
    data = tmp_path / "data"
    schema = data / "schema"
    registers = schema / "registers"
    lookups = schema / "lookups"
    corpus = tmp_path / "external corpus"
    output = tmp_path / "workbook/review"
    items = tmp_path / "items.csv"
    write_csv(items, [dict(evidence_id="ev_local", question="Check the passage")])
    write_csv(
        registers / "EV_evidence_register.csv",
        [
            dict(
                evidence_id="ev_local",
                source_id="local",
                nbs_id="practice",
                use_role="nbs_effect",
                variable="x",
                page="1",
                quote="Restoration increased survival.",
                relationship='{"direction":"positive"}',
                context="{}",
            )
        ],
    )
    write_csv(
        registers / "SRC_source_register.csv",
        [dict(source_id="local", citation="Selected citation")],
    )
    write_csv(
        registers / "BANDS_magnitude_bands.csv",
        [dict(metric="other", unit="none", band_id="fixture")],
    )
    write_csv(
        registers / "VONT_variable_ontology.csv",
        [dict(canonical_variable_id="x", label="Indicator from selected data")],
    )
    write_csv(
        lookups / "variable_direction_sense.csv",
        [
            dict(
                variable="x",
                high_is="good",
                positive_means="selected sense",
                negative_means="selected decrease",
            )
        ],
    )
    write_csv(
        lookups / "display_vocab.csv",
        [dict(field="fixture", code="word", label="selected vocabulary")],
    )
    write_csv(
        lookups / "design_weights.csv",
        [dict(design="observational", weight_factor="0.85")],
    )
    write_csv(
        schema / "recipes/practice/T6_nbs_scorecard.csv",
        [
            dict(
                record_id="local_row",
                nbs_id="practice",
                variable_id="x",
                effect_direction="moderate",
                effect_confidence="high",
                evidence_ids='["ev_local"]',
            )
        ],
    )
    corpus.mkdir()
    with fitz.open() as doc:
        doc.new_page().insert_text((60, 60), "Restoration increased survival.")
        doc.save(corpus / "local.pdf")
    output.mkdir(parents=True)
    (output / "index.json").write_text(
        json.dumps(
            {
                "batches": [{"id": "retained", "file": "review/retained.json", "n": 3}],
                "redirects": {"legacy": "retained"},
            }
        ),
        encoding="utf-8",
    )
    common = [
        "test_batch",
        "--root",
        str(data),
        "--out-dir",
        str(output),
        "--title",
        "Selected batch",
    ]
    return (
        data,
        corpus,
        output,
        items,
        [*common, "--items", str(items), "--corpus-dir", str(corpus)],
        [*common, "--nbs", "practice", "--all-rollups"],
    )


def inventory(root):
    return {
        str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()
    }


def test_both_commands_render_selected_inputs_and_preserve_navigation(example):
    data, corpus, out, _, unit_args, row_args = example
    inputs = inventory(data), inventory(corpus)
    assert units.main(unit_args) == 0
    payload = json.loads((out / "test_batch.json").read_bytes())
    unit = payload["units"][0]
    assert (
        unit["citation"] == "Selected citation"
        and "selected sense" in unit["plain"]["direction_reads"]
    )
    assert unit["crop"] == "review/img/ev_local.png" and (
        out / "img/ev_local.png"
    ).read_bytes().startswith(b"\x89PNG")
    assert rows.main(row_args) == 0
    payload = json.loads((out / "test_batch.json").read_bytes())
    assert payload["vocab"]["fixture"]["word"]["label"] == "selected vocabulary"
    assert "selected sense" in payload["rows"][0]["evidence"][0]["direction_reads"]
    assert payload["rows"][0]["record_id"] == "local_row"
    index = json.loads((out / "index.json").read_bytes())
    assert index["redirects"] == {"legacy": "retained"} and [
        x["id"] for x in index["batches"]
    ] == ["retained", "test_batch"]
    assert (
        index["batches"][-1]["file"] == "review/test_batch.json"
        and index["batches"][-1]["kind"] == "rows"
    )
    assert (inventory(data), inventory(corpus)) == inputs


@pytest.mark.parametrize("kind", ["unit", "row"])
def test_failed_index_replacement_restores_whole_batch(example, monkeypatch, kind):
    _, _, out, _, unit_args, row_args = example
    before = inventory(out)
    replace = publication.os.replace
    failed = False

    def fail(src, dest):
        nonlocal failed
        replace(src, dest)
        if Path(dest) == out / "index.json" and not failed:
            failed = True
            raise OSError("simulated index failure")

    monkeypatch.setattr(publication.os, "replace", fail)
    with pytest.raises(OSError, match="index failure"):
        (units.main(unit_args) if kind == "unit" else rows.main(row_args))
    assert failed and inventory(out) == before


def test_drift_during_render_rejects_batch_and_retains_external_edit(
    example, monkeypatch
):
    _, _, out, items, args, _ = example
    before = inventory(out)
    render = units.render_crop

    def edit(*args):
        result = render(*args)
        items.write_text("evidence_id,question\nev_local,Changed\n", encoding="utf-8")
        return result

    monkeypatch.setattr(units, "render_crop", edit)
    with pytest.raises(ValueError, match="input changed"):
        units.main(args)
    assert inventory(out) == before and "Changed" in items.read_text()


def test_dry_runs_render_without_installing(example):
    _, _, out, _, ua, ra = example
    before = inventory(out)
    assert units.main([*ua, "--dry-run"]) == 0 and rows.main([*ra, "--dry-run"]) == 0
    assert inventory(out) == before


@pytest.mark.parametrize("batch_id", ["../escape", "index", "DECISIONS"])
def test_unsafe_or_reserved_batch_names_refused(example, batch_id):
    _, _, out, _, args, _ = example
    before = inventory(out)
    with pytest.raises(ValueError):
        units.main([batch_id, *args[1:]])
    assert inventory(out) == before


def test_existing_unrelated_json_and_case_alias_are_protected(example):
    _, _, out, _, args, _ = example
    other = out / "other.json"
    other.write_text('{"keep": true}', encoding="utf-8")
    before = inventory(out)
    with pytest.raises(ValueError, match="not this review batch"):
        units.main(["other", *args[1:]])
    with pytest.raises(ValueError, match="collides"):
        units.main(["RETAINED", *args[1:]])
    assert inventory(out) == before


def test_missing_pdf_page_keeps_reviewable_unit_without_broken_crop(example):
    data, _, out, _, args, _ = example
    ev = data / "schema/registers/EV_evidence_register.csv"
    with ev.open(encoding="utf-8", newline="") as stream:
        r = next(csv.DictReader(stream))
    write_csv(ev, [dict(r, page="20")])
    assert units.main(args) == 0
    u = json.loads((out / "test_batch.json").read_bytes())["units"][0]
    assert u["crop"] is None and u["crop_note"] == "page out of range"
    assert not (out / "img/ev_local.png").exists()


def test_row_import_rejects_export_alias_and_recovers_history(tmp_path, monkeypatch):
    data = tmp_path / "selected"
    log = data / "pipeline/metrics/row_review_log.csv"
    exp = tmp_path / "export.csv"
    old = dict(
        date="old",
        record_id="history",
        nbs_id="practice",
        table="T6",
        decision="approve",
        reason="",
        note="historical",
        reviewer="one",
    )
    write_csv(log, [old])
    before = log.read_bytes().rstrip(b"\r\n")
    log.write_bytes(before)
    write_csv(exp, [dict(old, date="new", record_id="current", reviewer="two")])
    original = exp.read_bytes()
    with pytest.raises(ValueError, match="alias"):
        apply_rows.apply_export(exp, exp)
    assert exp.read_bytes() == original
    replace = publication.os.replace
    failed = False

    def fail(src, dest):
        nonlocal failed
        replace(src, dest)
        if Path(dest) == log and not failed:
            failed = True
            raise OSError("simulated log failure")

    with monkeypatch.context() as patch:
        patch.setattr(publication.os, "replace", fail)
        with pytest.raises(OSError, match="log failure"):
            apply_rows.main([str(exp), "--root", str(data)])
    assert log.read_bytes() == before and exp.read_bytes() == original
    assert apply_rows.main([str(exp), "--root", str(data)]) == 0
    assert log.read_bytes().startswith(before + b"\r\n")
    with log.open(encoding="utf-8", newline="") as stream:
        assert [r["record_id"] for r in csv.DictReader(stream)] == [
            "history",
            "current",
        ]
    assert apply_rows.apply_export(exp, log)["appended"] == 0
