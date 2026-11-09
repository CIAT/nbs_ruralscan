"""Migration parity: data snapshots must not select code or leak across roots."""

from dataclasses import asdict, fields
import hashlib
import json
from pathlib import Path
import runpy
import shutil

import pytest

from nbs_ruralscan.recipe import developer_corpus, t4_build
from nbs_ruralscan.recipe.developer_contract import write_package

ROOT = Path(__file__).resolve().parents[1]
NBS = "agroforestry"


def snapshot_files(root):
    return {
        path.relative_to(root): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


@pytest.fixture
def relocated(tmp_path):
    target = tmp_path / "data snapshot"
    for path in t4_build.T4BuildInputs.from_root(ROOT, NBS).paths():
        dest = target / path.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
    return target


def test_data_only_snapshot_rebuilds_from_unrelated_working_directory(
    relocated, tmp_path, monkeypatch
):
    expected = developer_corpus.rebuild(ROOT, NBS)
    before = snapshot_files(relocated)
    monkeypatch.chdir(tmp_path)
    actual = developer_corpus.rebuild(relocated, NBS)
    assert actual == expected
    assert snapshot_files(relocated) == before
    assert not (relocated / "src").exists()
    assert not (relocated / "scripts").exists()


def test_explicit_input_files_need_no_repository_layout(relocated, tmp_path):
    normal = t4_build.T4BuildInputs.from_root(relocated, NBS)
    isolated = {}
    for field in fields(normal):
        if getattr(normal, field.name) is None:
            continue
        dest = tmp_path / (field.name + ".csv")
        shutil.copyfile(getattr(normal, field.name), dest)
        isolated[field.name] = dest
    inputs = t4_build.T4BuildInputs(**isolated)
    expected = t4_build.synthesise(NBS, inputs=normal)
    actual = t4_build.synthesise(NBS, inputs=inputs)
    assert {k: asdict(v) for k, v in actual.items()} == {
        k: asdict(v) for k, v in expected.items()
    }
    before = {path: path.read_bytes() for path in inputs.paths()}
    t4_build.write_recipe(
        NBS,
        actual,
        t4_build._rd(inputs.ontology),
        inputs=inputs,
        output_dir=tmp_path / "trial",
    )
    assert (tmp_path / "trial/T4_suitability_mappings.csv").read_bytes() == (
        inputs.audited_recipe.read_bytes()
    )
    assert before == {path: path.read_bytes() for path in inputs.paths()}


def test_copied_script_is_not_executed_or_claimed_as_compiler(relocated):
    script = relocated / "scripts/synthesise-recipe.py"
    script.parent.mkdir()
    script.write_text('raise RuntimeError("wrong compiler")\n')
    result = developer_corpus.rebuild(relocated, NBS)
    report = result["synthesis_report"]
    assert "scripts/synthesise-recipe.py" not in report["input_sha256"]
    actual = Path(t4_build.__file__)
    assert (
        report["compiler_source_sha256"]["src/nbs_ruralscan/recipe/t4_build.py"]
        == hashlib.sha256(actual.read_bytes()).hexdigest()
    )


def test_failed_alternate_root_does_not_change_inputs_or_next_build(relocated):
    expected = developer_corpus.rebuild(ROOT, NBS)
    policy = relocated / "schema/lookups/crop_scope_policy.csv"
    policy.unlink()
    before = snapshot_files(relocated)
    with pytest.raises(FileNotFoundError):
        developer_corpus.rebuild(relocated, NBS)
    assert snapshot_files(relocated) == before
    assert developer_corpus.rebuild(ROOT, NBS) == expected


def test_cli_explicit_source_root_preserves_data_and_trial_bytes(
    relocated, tmp_path, monkeypatch, capsys
):
    runner = runpy.run_path(str(ROOT / "scripts/synthesise-recipe.py"))
    before = snapshot_files(relocated)
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "trial"
    assert (
        runner["main"](
            [NBS, "--source-root", str(relocated), "--output-dir", str(output)]
        )
        == 0
    )
    assert snapshot_files(relocated) == before
    assert (output / "T4_suitability_mappings.csv").read_bytes() == (
        relocated / "schema/recipes/agroforestry/T4_suitability_mappings.csv"
    ).read_bytes()
    report = json.loads((output / "T4_synthesis_report.json").read_text())
    assert report["review_mode"] == "approved_only"
    assert "schema/registers/EV_evidence_register.csv" in report["input_sha256"]
    capsys.readouterr()


@pytest.mark.parametrize("installed", [False, True])
def test_unreviewed_cli_protects_both_input_and_compiler_roots(
    relocated, installed, capsys
):
    runner = runpy.run_path(str(ROOT / "scripts/synthesise-recipe.py"))
    target = (ROOT if installed else relocated) / "docs"
    before = snapshot_files(relocated)
    with pytest.raises(SystemExit) as exc:
        runner["main"](
            [
                NBS,
                "--source-root",
                str(relocated),
                "--include-unreviewed",
                "--output-dir",
                str(target),
            ]
        )
    assert exc.value.code == 2
    assert snapshot_files(relocated) == before
    capsys.readouterr()


def test_publication_refuses_code_snapshot_different_from_executing_compiler(
    relocated, tmp_path
):
    for name, source in developer_corpus.compiler_paths().items():
        dest = relocated / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
    changed = relocated / "src/nbs_ruralscan/recipe/t4_build.py"
    changed.write_bytes(changed.read_bytes() + b"\n# other compiler revision\n")
    before = snapshot_files(relocated)
    output = tmp_path / "package"
    with pytest.raises(ValueError, match="Compiler snapshot differs.*t4_build.py"):
        write_package(relocated, output)
    assert not output.exists()
    assert snapshot_files(relocated) == before


@pytest.mark.parametrize("target_option", ["--output-dir", "--report"])
def test_relocated_wrapper_protects_separate_compiler_checkout(
    relocated, tmp_path, monkeypatch, target_option, capsys
):
    wrapper = tmp_path / "wrapper/scripts/synthesise-recipe.py"
    wrapper.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "scripts/synthesise-recipe.py", wrapper)
    runner = runpy.run_path(str(wrapper))

    def must_not_compile(*args, **kwargs):
        raise AssertionError("Path validation must happen before compilation")

    monkeypatch.setitem(runner["main"].__globals__, "synthesise", must_not_compile)
    args = [
        NBS,
        "--source-root",
        str(relocated),
        "--include-unreviewed",
        "--output-dir",
        str(tmp_path / "safe-draft"),
        target_option,
        str(ROOT / "docs/must-not-write"),
    ]
    with pytest.raises(SystemExit) as exc:
        runner["main"](args)
    assert exc.value.code == 2
    assert not (tmp_path / "safe-draft").exists()
    capsys.readouterr()
