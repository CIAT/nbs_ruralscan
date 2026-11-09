"""Independently authored T4 definitions reproduce the mixed historical snapshot."""

import csv
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import runpy
import shutil

import pytest

from nbs_ruralscan.recipe import developer_contract, developer_corpus, t4_build as t4

ROOT = Path(__file__).resolve().parents[1]
PRACTICES = [
    "agroforestry",
    "forest_restoration",
    "mangrove_restoration",
    "riparian_buffer",
    "water_harvesting_conservation",
    "wetland_management",
]


def compile_to(root, practice, inputs):
    results = t4.synthesise(practice, inputs=inputs)
    t4.write_recipe(
        practice, results, t4._rd(inputs.ontology), inputs=inputs, output_dir=root
    )
    return (
        {p.name: p.read_bytes() for p in root.iterdir()},
        {k: asdict(v) for k, v in results.items()},
    )


def copy_inputs(root, practice):
    for src in t4.T4BuildInputs.from_root(ROOT, practice).paths():
        dest = root / src.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
    return t4.T4BuildInputs.from_root(root, practice, require_authored=True)


def replace_record(path, edit):
    rows = t4._rd(path)
    edit(rows)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


@pytest.mark.parametrize("practice", PRACTICES)
def test_clean_build_reproduces_every_legacy_mapping_and_family_report(
    tmp_path, practice
):
    selected = copy_inputs(tmp_path / "source", practice)
    legacy = replace(
        selected,
        definition_index=None,
        authored_mappings=None,
        mapping_settings=None,
        review_holds=None,
        family_registry=None,
    )
    historical = compile_to(tmp_path / "legacy", practice, legacy)
    selected.audited_recipe.unlink()
    assert selected.audited_recipe not in selected.compilation_paths()
    assert selected.audited_recipe in selected.paths()
    assert compile_to(tmp_path / "clean", practice, selected) == historical
    assert selected.release_settings(practice) == dict(
        run_policy=practice == "agroforestry", effect_prose=True
    )


def test_setting_changes_new_output_and_blocks_stale_audited_package(tmp_path):
    root = tmp_path / "source"
    practice = "agroforestry"
    config = copy_inputs(root, practice)
    assert config.mapping_settings is not None
    mapping = t4._rd(config.mapping_settings)[0]["mapping_id"]
    replace_record(
        config.mapping_settings,
        lambda rows: rows[0].update(weight_default="0.07", weight_adjustable="false"),
    )
    compile_to(tmp_path / "changed", practice, config)
    candidates = {
        r["mapping_id"]: r
        for r in t4._rd(tmp_path / "changed" / "T4_suitability_mappings.csv")
    }
    assert candidates[mapping]["weight_default"] == "0.07"
    assert candidates[mapping]["weight_adjustable"] == "false"
    with pytest.raises(ValueError, match="does not reproduce"):
        developer_corpus.rebuild(root, practice)
    assert set(config.paths()).issubset(
        developer_contract.contract_input_paths(root, practice)
    )
    assert (
        root / "schema/recipes/agroforestry/T4_run_policy.csv"
        in developer_contract.contract_input_paths(root, practice)
    )


def test_missing_declaration_and_missing_hold_close_the_release(tmp_path):
    practice = "water_harvesting_conservation"
    root = tmp_path / "source"
    config = copy_inputs(root, practice)
    assert config.review_holds is not None
    config.review_holds.unlink()
    with pytest.raises(FileNotFoundError, match="Missing declared T4 input"):
        t4.T4BuildInputs.from_root(root, practice, require_authored=True)
    assert config.definition_index is not None
    config.definition_index.unlink()
    with pytest.raises(FileNotFoundError):
        t4.T4BuildInputs.from_root(root, practice)
    shutil.rmtree(root / "schema/recipe_inputs")
    legacy = t4.T4BuildInputs.from_root(root, practice)
    assert legacy.audited_recipe in legacy.compilation_paths()
    with pytest.raises(FileNotFoundError):
        t4.T4BuildInputs.from_root(root, practice, require_authored=True)


@pytest.mark.parametrize(
    "edits",
    [
        dict(weight_default="nan"),
        dict(weight_default="2"),
        dict(weight_adjustable="maybe"),
        dict(mapping_id="wrong_mapping"),
        dict(nbs_id="cross_practice"),
    ],
)
def test_refuse_malformed_or_misdirected_settings(tmp_path, edits):
    practice = "riparian_buffer"
    config = copy_inputs(tmp_path, practice)
    replace_record(config.mapping_settings, lambda rows: rows[0].update(edits))
    with pytest.raises(ValueError):
        t4.synthesise(practice, inputs=config)


@pytest.mark.parametrize("practice", PRACTICES)
def test_every_accepted_mapping_review_hold_is_declared(practice):
    inputs = t4.T4BuildInputs.from_root(ROOT, practice, require_authored=True)
    assert t4.accepted_hold_differences(inputs) == []


@pytest.mark.parametrize(
    "new_hold", [True, False], ids=["new-decision", "changed-decision"]
)
def test_in_place_build_protects_divergent_accepted_hold(tmp_path, new_hold):
    practice = "water_harvesting_conservation"
    root = tmp_path / "data"
    inputs = copy_inputs(root, practice)
    held = t4._rd(inputs.review_holds)[0]["mapping_id"]
    target = "synthetic_new_mapping" if new_hold else held

    if new_hold:
        # Add a synthetic newly accepted mapping before the reviewer places a hold.
        setting = next(
            r for r in t4._rd(inputs.mapping_settings) if r["variable"] == "slope"
        )

        def add_mapping(rows):
            record = dict.fromkeys(rows[0], "")
            record.update(setting, mapping_id=target)
            rows.append(record)

        replace_record(inputs.audited_recipe, add_mapping)

    def later_review(rows):
        row = next(r for r in rows if r["mapping_id"] == target)
        params = t4.binding_params(row)
        params.setdefault("reviewed_adaptation", {})["dataset_binding"] = {
            "status": "requires_matching_input",
            "reason": "Later approved review.",
        }
        row["relationship_params"] = json.dumps(params)

    replace_record(inputs.audited_recipe, later_review)
    accepted = inputs.audited_recipe
    report = accepted.parent / "T4_synthesis_report.json"
    report.write_text("previous report")
    before = {p.name: p.read_bytes() for p in accepted.parent.iterdir()}
    assert t4.accepted_hold_differences(inputs) == [target]
    cli = runpy.run_path(str(ROOT / "scripts/synthesise-recipe.py"))["main"]
    with pytest.raises(
        ValueError, match=f"Unreconciled accepted T4 review holds: {target}"
    ):
        cli([practice, "--source-root", str(root)])
    assert before == {p.name: p.read_bytes() for p in accepted.parent.iterdir()}
    with pytest.raises(ValueError, match="supplied SHA-256 differs"):
        cli([practice, "--source-root", str(root), "--supersede-holds-from", "0" * 64])
    assert before == {p.name: p.read_bytes() for p in accepted.parent.iterdir()}
    trial = tmp_path / "trial"
    assert cli([practice, "--source-root", str(root), "--output-dir", str(trial)]) == 0
    assert before == {p.name: p.read_bytes() for p in accepted.parent.iterdir()}

    if new_hold:
        # Explicitly retire the later synthetic decision against the reviewed baseline.
        digest = hashlib.sha256(accepted.read_bytes()).hexdigest()
        assert (
            cli(
                [practice, "--source-root", str(root), "--supersede-holds-from", digest]
            )
            == 0
        )
        assert accepted.read_bytes() == (trial / accepted.name).read_bytes()
    else:
        # Record the later decision in its authored file, then regenerate normally.
        replace_record(inputs.review_holds, later_review)
        assert cli([practice, "--source-root", str(root)]) == 0
        row = next(r for r in t4._rd(accepted) if r["mapping_id"] == target)
        assert t4.row_binding_requirement(row)["reason"] == "Later approved review."
    assert t4.accepted_hold_differences(inputs) == []


def test_wetland_full_corpus_checks_nested_types_and_ignores_object_key_order(tmp_path):
    practice = "wetland_management"
    config = copy_inputs(tmp_path, practice)

    def change(rows, false_bound):
        row = rows[0]
        params = t4.binding_params(row)
        interval = params["profiles"][0]["intervals"][0]
        assert interval["lower"] == 0
        if false_bound:
            interval["lower"] = False
        row["relationship_params"] = json.dumps(params, sort_keys=True)

    replace_record(config.audited_recipe, lambda rows: change(rows, False))
    assert developer_corpus.rebuild(tmp_path, practice)["synthesis_report"][
        "audited_recipe_matches"
    ]
    replace_record(config.audited_recipe, lambda rows: change(rows, True))
    with pytest.raises(
        ValueError,
        match="does not reproduce.*wetland_management__creation__distance_to_waterbody",
    ):
        developer_corpus.rebuild(tmp_path, practice)


@pytest.mark.parametrize(
    ("column", "content"),
    [
        ("relationship_params", '{"bounds":1,"bounds":2}'),
        ("context_overrides", '[{"weight":1e400}]'),
        ("evidence_ids", "[NaN]"),
        ("future_dataset_ids", '{"projection":Infinity}'),
    ],
)
def test_full_corpus_refuses_ambiguous_embedded_json(tmp_path, column, content):
    practice = "wetland_management"
    config = copy_inputs(tmp_path, practice)
    replace_record(
        config.audited_recipe, lambda rows: rows[0].update({column: content})
    )
    with pytest.raises(
        ValueError, match=f"Invalid {column} for wetland_management__creation"
    ):
        developer_corpus.rebuild(tmp_path, practice)


@pytest.mark.parametrize(
    ("practice", "kind"),
    [
        ("agroforestry", "authored_mappings"),
        ("water_harvesting_conservation", "review_holds"),
        ("riparian_buffer", "mapping_settings"),
    ],
)
@pytest.mark.parametrize("field", ["variable", "suitability_family_id"])
def test_authored_decisions_bind_to_declared_family_and_variable(
    tmp_path, practice, kind, field
):
    config = copy_inputs(tmp_path, practice)

    def change(rows):
        row = rows[0]
        row[field] = "typo_or_retired_identity"
        row["mapping_id"] = f"{row['suitability_family_id']}__{row['variable']}"

    replace_record(getattr(config, kind), change)
    with pytest.raises(ValueError, match="Unknown T4 family or variable"):
        developer_corpus.rebuild(tmp_path, practice)


@pytest.mark.parametrize("target", ["family", "audited", "hardlink"])
def test_report_cannot_replace_related_files(tmp_path, target):
    practice = "wetland_management"
    root = tmp_path / "data"
    inputs = copy_inputs(root, practice)
    output = tmp_path / "trial"
    output.mkdir()
    if target == "family":
        report = output / "T4_wetland_management__creation.json"
    elif target == "audited":
        report = inputs.audited_recipe
    else:
        report = output / "T4_synthesis_report.json"
        report.hardlink_to(inputs.audited_recipe)
    before = inputs.audited_recipe.read_bytes()
    cli = runpy.run_path(str(ROOT / "scripts/synthesise-recipe.py"))["main"]
    with pytest.raises(SystemExit, match="2"):
        cli(
            [
                practice,
                "--source-root",
                str(root),
                "--output-dir",
                str(output),
                "--report",
                str(report),
            ]
        )
    assert not (output / "T4_suitability_mappings.csv").exists()
    assert inputs.audited_recipe.read_bytes() == before
