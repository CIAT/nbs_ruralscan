"""Effect compilation selects data, policies and prose independently of installed code."""

from dataclasses import fields, replace
import csv
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

import pytest

from nbs_ruralscan.recipe import cell_synthesis as cs, t3t6_build as build
from nbs_ruralscan.schema_tools import publication

ROOT = Path(__file__).resolve().parents[1]
NBS = "riparian_buffer"


def fingerprints(root):
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*")
        if p.is_file()
    }


@pytest.fixture
def selected(tmp_path):
    root = tmp_path / "data snapshot"
    original = build.T3T6BuildInputs.from_root(ROOT, NBS)
    for path in original.paths():
        if path.exists():
            destination = root / path.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
    return root


def poison(*args, **kwargs):
    raise AssertionError("Explicit compilation must not read compiler defaults")


def test_relocated_inputs_survive_interleaving_failure_and_poisoned_defaults(
    selected, tmp_path, monkeypatch
):
    inputs = build.T3T6BuildInputs.from_root(selected, NBS)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cs, "_default_bands", poison)
    monkeypatch.setattr(cs, "_default_design_weights", poison)
    before = fingerprints(selected)
    loaded = build.load_inputs(NBS, [], inputs=inputs)
    expected = build.synthesise(NBS, loaded)
    assert expected["T3"] and expected["T6"]
    # A second snapshot excludes every T6 route. It must not affect the first.
    other = tmp_path / "other"
    shutil.copytree(selected, other)
    alternate = build.T3T6BuildInputs.from_root(other, NBS)
    with alternate.route_policy.open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "nbs_id",
                "ev_variable",
                "target_table",
                "target_key",
                "included",
            ],
        )
        writer.writeheader()
        for route in loaded["xw"]:
            if route.target_table == "T6":
                writer.writerow(
                    dict(
                        nbs_id=NBS,
                        ev_variable=route.ev_variable,
                        target_table="T6",
                        target_key=route.target_key,
                        included="false",
                    )
                )
    different = build.synthesise(NBS, build.load_inputs(NBS, [], inputs=alternate))
    assert different["T6"] == [] and expected["T6"]
    alternate.design_weights.unlink()
    with pytest.raises(ValueError, match="design_weights"):
        build.load_inputs(NBS, [], inputs=alternate)
    assert build.synthesise(NBS, build.load_inputs(NBS, [], inputs=inputs)) == expected
    assert fingerprints(selected) == before
    assert not (selected / "src").exists() and not (selected / "scripts").exists()


def test_explicit_files_need_no_repository_layout(selected, tmp_path):
    normal = build.T3T6BuildInputs.from_root(selected, NBS)
    files = {}
    for field in fields(normal):
        source = getattr(normal, field.name)
        destination = tmp_path / "flat" / (field.name + source.suffix)
        destination.parent.mkdir(exist_ok=True)
        if source.exists():
            shutil.copyfile(source, destination)
        files[field.name] = destination
    isolated = build.T3T6BuildInputs(**files)
    assert build.synthesise(
        NBS, build.load_inputs(NBS, [], inputs=isolated)
    ) == build.synthesise(NBS, build.load_inputs(NBS, [], inputs=normal))


def test_selected_policy_values_captured_before_synthesis(selected, monkeypatch):
    inputs = build.T3T6BuildInputs.from_root(selected, NBS)
    loaded = build.load_inputs(NBS, [], inputs=inputs)
    expected = build.synthesise(NBS, loaded)
    # Synthesis consumes captured values; there are no late policy-file reads.
    monkeypatch.setattr(Path, "open", poison)
    assert build.synthesise(NBS, loaded) == expected


def test_prose_from_input_not_destination_and_repeat_publication(selected, tmp_path):
    inputs = build.T3T6BuildInputs.from_root(selected, NBS)
    out = build.synthesise(NBS, build.load_inputs(NBS, [], inputs=inputs))
    row = out["T6"][0]
    source_prose = {
        row["record_id"]: {
            "evidence_ids": row["evidence_ids"],
            "class": row["effect_direction"],
            "mechanism": "Selected snapshot prose",
            "conditionality": "Selected caveat",
        }
    }
    inputs.prose.parent.mkdir(parents=True, exist_ok=True)
    inputs.prose.write_text(json.dumps(source_prose))
    output = tmp_path / "candidate"
    output.mkdir()
    (output / "T3T6_prose.json").write_text(
        "invalid destination sidecar: must not be read"
    )
    before = fingerprints(selected)
    written = build.write_recipe(
        NBS, out, inputs=inputs, output_dir=output, dry_run=False
    )
    assert len(written) == 4
    with (output / "T6_nbs_scorecard.csv").open(newline="") as stream:
        actual = {r["record_id"]: r for r in csv.DictReader(stream)}
    assert actual[row["record_id"]]["effect_mechanism"] == "Selected snapshot prose"
    assert fingerprints(selected) == before
    states = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in written}
    assert (
        build.write_recipe(NBS, out, inputs=inputs, output_dir=output, dry_run=False)
        == written
    )
    assert states == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in written}
    assert (output / "T3T6_prose.json").read_text().startswith("invalid destination")
    source_prose[row["record_id"]]["evidence_ids"] = ["wrong-id"]
    inputs.prose.write_text(json.dumps(source_prose))
    fresh = build.synthesise(NBS, build.load_inputs(NBS, [], inputs=inputs))
    build.write_recipe(NBS, fresh, inputs=inputs, output_dir=output, dry_run=False)
    assert (
        "Selected snapshot prose" not in (output / "T6_nbs_scorecard.csv").read_text()
    )


def test_cli_preview_and_refused_staging_write_never_mutate(
    selected, tmp_path, monkeypatch
):
    cli = runpy.run_path(str(ROOT / "scripts/synthesise-t3t6.py"))
    monkeypatch.chdir(tmp_path)
    poison_script = selected / "scripts/synthesise-t3t6.py"
    poison_script.parent.mkdir()
    poison_script.write_text(
        'raise AssertionError("Input snapshot must not select compiler")'
    )
    before = fingerprints(selected)
    output = tmp_path / "candidate"
    staging = tmp_path / "staged.json"
    staging.write_text("[]")
    args = [NBS, "--source-root", str(selected), "--output-dir", str(output)]
    assert cli["main"](args + ["--dry-run", "--staging", str(staging)]) == 0
    assert not output.exists()
    assert cli["main"](args + ["--staging", str(staging)]) == 2
    assert not output.exists() and fingerprints(selected) == before
    with pytest.raises(SystemExit):
        cli["main"]([NBS, "--source-root", str(selected)])
    for invalid in ("../escape", "/escape", "name/child"):
        with pytest.raises(ValueError, match="identifier"):
            cli["main"]([invalid, "--source-root", str(selected), "--dry-run"])
    with pytest.raises(SystemExit):
        cli["main"](
            [
                NBS,
                "--source-root",
                str(selected),
                "--output-dir",
                str(selected / "trial"),
            ]
        )
    assert fingerprints(selected) == before
    assert cli["main"](args) == 0
    assert sorted(p.name for p in output.iterdir()) == [
        "T3T6_synthesis_report.json",
        "T3_nbs_hazard_farming.csv",
        "T6E_economic_profile.csv",
        "T6_nbs_scorecard.csv",
    ]
    assert fingerprints(selected) == before


@pytest.mark.parametrize(
    "field", [f.name for f in fields(build.T3T6BuildInputs) if f.name != "prose"]
)
def test_missing_explicit_inputs_fail_before_empty_build(selected, field):
    inputs = build.T3T6BuildInputs.from_root(selected, NBS)
    getattr(inputs, field).unlink()
    before = fingerprints(selected)
    with pytest.raises(ValueError, match=field):
        build.load_inputs(NBS, [], inputs=inputs)
    assert fingerprints(selected) == before


@pytest.mark.parametrize("failure", ["render", "second_install", "after_replace"])
def test_recipe_publication_failure_preserves_previous_set(
    selected, tmp_path, monkeypatch, failure
):
    inputs = build.T3T6BuildInputs.from_root(selected, NBS)
    out = build.synthesise(NBS, build.load_inputs(NBS, [], inputs=inputs))
    output = tmp_path / "candidate"
    output.mkdir()
    for name in (
        "T3_nbs_hazard_farming.csv",
        "T6_nbs_scorecard.csv",
        "T6E_economic_profile.csv",
    ):
        (output / name).write_text("old,content\nkeep,me\n")
    (output / "T3T6_synthesis_report.json").write_text('{"old":true}')
    before = fingerprints(output)
    original_write, original_replace = Path.write_text, publication.os.replace
    fired = False

    def fail_write(path, *args, **kwargs):
        if failure == "render" and path.name == "T3T6_synthesis_report.json":
            raise OSError("report rendering failed")
        return original_write(path, *args, **kwargs)

    def fail_replace(source, target):
        nonlocal fired
        if (
            failure != "render"
            and Path(target) == output / "T6_nbs_scorecard.csv"
            and not fired
        ):
            fired = True
            if failure == "after_replace":
                original_replace(source, target)
                raise KeyboardInterrupt()
            raise OSError("installation failed")
        return original_replace(source, target)

    monkeypatch.setattr(Path, "write_text", fail_write)
    monkeypatch.setattr(publication.os, "replace", fail_replace)
    with pytest.raises(KeyboardInterrupt if failure == "after_replace" else OSError):
        build.write_recipe(NBS, out, inputs=inputs, output_dir=output, dry_run=False)
    assert fingerprints(output) == before


def test_output_alias_and_redirect_refused_before_write(selected, tmp_path):
    inputs = build.T3T6BuildInputs.from_root(selected, NBS)
    out = build.synthesise(NBS, build.load_inputs(NBS, [], inputs=inputs))
    output = tmp_path / "candidate"
    output.mkdir()
    destination = output / "T3_nbs_hazard_farming.csv"
    destination.symlink_to(inputs.sources)
    before = fingerprints(selected)
    with pytest.raises(ValueError, match="symlink|overlap"):
        build.write_recipe(NBS, out, inputs=inputs, output_dir=output, dry_run=False)
    assert fingerprints(selected) == before
    destination.unlink()
    alias = replace(inputs, sources=destination)
    shutil.copyfile(inputs.sources, destination)
    with pytest.raises(ValueError, match="overlap"):
        build.write_recipe(NBS, out, inputs=alias, output_dir=output, dry_run=False)


def test_import_does_not_read_schema():
    script = """
from pathlib import Path
from builtins import open as original
import builtins, runpy
original_path = Path.open
def guard(path, *args, **kwargs):
    if "schema" in Path(path).parts:
        raise AssertionError("Import read schema: " + str(path))
    return original(path, *args, **kwargs)
def guard_path(path, *args, **kwargs):
    if "schema" in path.parts:
        raise AssertionError("Import read schema: " + str(path))
    return original_path(path, *args, **kwargs)
builtins.open = guard
Path.open = guard_path
runpy.run_path("scripts/synthesise-t3t6.py")
"""
    subprocess.run([sys.executable, "-c", script], cwd=ROOT, check=True)


def test_fragility_uses_selected_records_policies_and_preserves_inputs(
    selected, tmp_path, monkeypatch
):
    cli = runpy.run_path(str(ROOT / "scripts/row-fragility.py"))
    inputs = build.T3T6BuildInputs.from_root(selected, NBS)
    loaded = build.load_inputs(NBS, [], inputs=inputs)
    compiled = build.synthesise(NBS, loaded)
    recipe = selected / "schema/recipes" / NBS
    # Keep one real global row, so this exercises actual leave-one-out synthesis.
    compiled["T3"] = []
    compiled["T6E"] = []
    compiled["T6"] = [
        next(
            row
            for row in compiled["T6"]
            if not row.get("suitability_family_id") and not row.get("scope_type")
        )
    ]
    build.write_recipe(NBS, compiled, inputs=inputs, output_dir=recipe, dry_run=False)
    before = fingerprints(selected)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cs, "_default_bands", poison)
    monkeypatch.setattr(cs, "_default_design_weights", poison)
    output = tmp_path / "fragility.csv"
    assert cli["main"]([NBS, "--source-root", str(selected), "--out", str(output)]) == 0
    with output.open() as stream:
        rows = list(csv.DictReader(stream))
    assert [row["record_id"] for row in rows] == [compiled["T6"][0]["record_id"]]
    assert fingerprints(selected) == before
    # A captured policy set must also reach the independent cell runner unchanged.
    run = cli["_cell_runner"](NBS, loaded)
    monkeypatch.setattr(Path, "open", poison)
    assert isinstance(
        run(loaded["units"], "T6", compiled["T6"][0]["variable_id"], None, None), list
    )


@pytest.mark.parametrize("link", ["hard", "symbolic"])
def test_fragility_refuses_redirected_output(selected, tmp_path, link):
    cli = runpy.run_path(str(ROOT / "scripts/row-fragility.py"))
    inputs = build.T3T6BuildInputs.from_root(selected, NBS)
    output = tmp_path / "fragility.csv"
    if link == "hard":
        output.hardlink_to(inputs.sources)
    else:
        output.symlink_to(inputs.sources)
    before = fingerprints(selected)
    with pytest.raises((ValueError, SystemExit)):
        cli["main"]([NBS, "--source-root", str(selected), "--out", str(output)])
    assert fingerprints(selected) == before


def test_fragility_empty_tables_publish_header_only(selected, tmp_path):
    cli = runpy.run_path(str(ROOT / "scripts/row-fragility.py"))
    recipe = selected / "schema/recipes" / NBS
    recipe.mkdir(parents=True, exist_ok=True)
    for name in ("T3_nbs_hazard_farming", "T6_nbs_scorecard", "T6E_economic_profile"):
        (recipe / (name + ".csv")).write_text("record_id\n")
    output = tmp_path / "empty.csv"
    before = fingerprints(selected)
    assert cli["main"]([NBS, "--source-root", str(selected), "--out", str(output)]) == 0
    assert output.read_text() == "record_id,class,n_units,n_pivotal,pivotal_units\n"
    assert fingerprints(selected) == before
