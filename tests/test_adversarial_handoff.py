"""Boundary tests for cross-recipe exports and unreviewed diagnostic writes."""

import importlib.util
import json
from pathlib import Path

import pytest

from nbs_ruralscan.recipe import developer_contract as dc

ROOT = Path(__file__).resolve().parents[1]


def test_other_nbs_never_inherits_agroforestry_handoff():
    for nbs in ("forest_restoration", "mangrove_restoration"):
        docs = dc._package_docs(ROOT, nbs)
        assert len(docs) == 4
        assert all((ROOT / path).is_file() for path in docs.values())
        assert all("agroforestry" not in path for path in docs.values())
        inputs = dc._package_inputs(ROOT, nbs)
        assert set(docs.values()) <= inputs
        assert not any("agroforestry" in path for path in inputs)
    assert dc._package_docs(ROOT, "agroforestry")["START_HERE.md"] == (
        "handoff/agroforestry-t4/START_HERE.md"
    )


def test_recipe_notes_override_only_matching_template(tmp_path):
    note = tmp_path / "handoff/mangrove_restoration-t4/START_HERE.md"
    note.parent.mkdir(parents=True)
    note.write_text("Reviewed mangrove-specific instructions")
    docs = dc._package_docs(tmp_path, "mangrove_restoration")
    assert docs["START_HERE.md"] == str(note.relative_to(tmp_path))
    assert docs["IMPLEMENTATION.md"].startswith("methodology/templates/")
    with pytest.raises(ValueError, match="Invalid NbS"):
        dc._package_inputs(tmp_path, "../../elsewhere")


def test_neutral_handoff_links_resolve_inside_published_package(tmp_path, monkeypatch):
    docs = dc._package_docs(ROOT, "forest_restoration")
    monkeypatch.setattr(dc, "_package_docs", lambda root, nbs: docs)
    package = tmp_path / "package"
    dc.write_package(ROOT, package)
    for name in ("START_HERE.md", "IMPLEMENTATION.md", "DATASET_INPUTS.md"):
        text = (package / name).read_text()
        assert "/methodology/templates/t4_handoff/" not in text
    assert "(developer_contract.json)" in (package / "START_HERE.md").read_text()
    assert "(developer_table.csv)" in (package / "DATASET_INPUTS.md").read_text()
    manifest = dc.verify_package(ROOT, package)
    original_manifest = json.dumps(manifest)
    del manifest["input_sha256"]["schema/lookups/t4_numeric_compilation_policy.csv"]
    (package / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="Incomplete package manifest"):
        dc.verify_package(ROOT, package)
    manifest = json.loads(original_manifest)
    del manifest["output_sha256"]["function_options.csv"]
    (package / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="Incomplete package manifest"):
        dc.verify_package(ROOT, package)


@pytest.mark.parametrize(
    "manifest", [{}, {"input_sha256": {}, "output_sha256": {}}, []]
)
def test_empty_manifest_cannot_claim_verified_package(tmp_path, manifest):
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="Incomplete package manifest"):
        dc.verify_package(ROOT, tmp_path)


@pytest.fixture
def runner():
    spec = importlib.util.spec_from_file_location(
        "adversarial_runner", ROOT / "scripts/synthesise-recipe.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "target",
    [
        "schema/recipes/forest_restoration",
        "schema/recipes/agroforestry/nested",
        "docs",
        "src",
    ],
)
def test_unreviewed_cannot_publish_into_other_recipe_or_code(runner, target):
    with pytest.raises(SystemExit) as exc:
        runner.main(
            ["agroforestry", "--include-unreviewed", "--output-dir", str(ROOT / target)]
        )
    assert exc.value.code == 2


def test_dry_run_does_not_write_explicit_report(runner, tmp_path):
    report = tmp_path / "report.json"
    assert runner.main(["agroforestry", "--dry-run", "--report", str(report)]) == 0
    assert not report.exists()


def test_invalid_nbs_cannot_escape_recipe_directory(runner):
    with pytest.raises(SystemExit):
        runner.main(["../../outside", "--dry-run"])


def test_compiler_does_not_invent_missing_source_quality(runner, monkeypatch):
    from nbs_ruralscan.recipe.family import FamilyResult

    original = runner._rd
    missing_id = original(runner.REG / "SRC_source_register.csv")[0]["source_id"]

    def read(path):
        rows = original(path)
        if path.name == "SRC_source_register.csv":
            rows[0]["benchmark_tier"] = ""
        return rows

    seen = []

    def synthesize(units, tiers, **kwargs):
        seen.append(tiers)
        return FamilyResult(kwargs["family"], None)

    monkeypatch.setattr(runner, "_rd", read)
    monkeypatch.setattr(runner, "synthesise_family", synthesize)
    runner.synthesise("agroforestry")
    assert seen and all(missing_id not in tiers for tiers in seen)


@pytest.mark.parametrize(
    "target", ["AGENTS.md", "README.md", ".git/config", "handoff/release/report.json"]
)
def test_unreviewed_report_cannot_overwrite_root_or_handoff_files(runner, target):
    with pytest.raises(SystemExit):
        runner.main(
            [
                "agroforestry",
                "--include-unreviewed",
                "--dry-run",
                "--report",
                str(ROOT / target),
            ]
        )
