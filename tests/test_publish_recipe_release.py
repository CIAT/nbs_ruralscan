"""Exercise the normal release command against an independent, synthetic data root."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import shutil

import pytest

from nbs_ruralscan.recipe import publish_release as publisher, t3t6_build, t4_build
from nbs_ruralscan.recipe.release_store import publish_release
from nbs_ruralscan.runtime.schema_loader import load_recipe_release
from nbs_ruralscan.schema_tools.generate import _csv_to_rows

ROOT = Path(__file__).resolve().parents[1]
NBS = "forest_restoration"


def sync(csv_file):
    csv_file.with_suffix(".json").write_text(
        json.dumps(_csv_to_rows(csv_file)), encoding="utf-8"
    )


def rows(path, records, fields=None):
    if fields is None:
        with path.open(newline="", encoding="utf-8") as handle:
            fields = next(csv.reader(handle))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


@pytest.fixture
def snapshot(tmp_path):
    """Make a small, independent reconciled recipe with real table/definition formats."""
    root = tmp_path / "data only"
    recipe = root / "schema/recipes" / NBS
    recipe.mkdir(parents=True)
    for src in publisher._sources(ROOT, NBS) | {ROOT / publisher.STRUCTURE}:
        if src.exists():
            dst = root / src.relative_to(ROOT)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
    effects = t3t6_build.T3T6BuildInputs.from_root(root, NBS)
    for file in (effects.evidence.with_suffix(".csv"), effects.sources):
        rows(file, [])
    sync(effects.evidence.with_suffix(".csv"))
    current = t4_build.T4BuildInputs.from_root(root, NBS, require_authored=True)
    # This fixture models an empty evidence corpus and its matching empty recipe.
    if current.authored_mappings:
        current.authored_mappings.unlink()
        with current.definition_index.open(newline="", encoding="utf-8") as file:
            declarations = list(csv.DictReader(file))
        next(r for r in declarations if r["nbs_id"] == NBS)["authored_mappings"] = (
            "false"
        )
        rows(current.definition_index, declarations)
    rows(current.audited_recipe, [])
    sync(current.audited_recipe)
    effects.prose.write_text("{}")
    # Reconcile a fresh effects baseline against the empty test corpus.
    compiled = t3t6_build.synthesise(
        NBS, t3t6_build.load_inputs(NBS, [], inputs=effects)
    )
    for candidate in t3t6_build.write_recipe(
        NBS,
        compiled,
        inputs=effects,
        output_dir=tmp_path / "effect-candidate",
        dry_run=False,
    ):
        copy = recipe / candidate.name
        shutil.copyfile(candidate, copy)
        if copy.suffix == ".csv":
            sync(copy)
    return root


def test_cli_publishes_and_pins_two_complete_generations(
    snapshot, tmp_path, monkeypatch, capsys
):
    store = tmp_path / "reader store"
    monkeypatch.chdir(tmp_path)
    args = ["publish", "--root", str(snapshot), "--store", str(store), "--nbs", NBS]
    assert publisher.main(args) == 0
    old = load_recipe_release(store)
    assert old.practices == (NBS,)
    assert old.table(NBS, "T4") == [] and old.table(NBS, "T6E") == []
    assert json.loads(old.setting(NBS, "T4_settings.json"))["files"] == []
    definition = snapshot / "schema/recipes" / NBS / publisher.IDENTITY
    with definition.open(newline="", encoding="utf-8") as f:
        records = list(csv.DictReader(f))
    records[0]["nbs_name"] = "Revised synthetic name"
    rows(definition, records)
    sync(definition)
    assert publisher.main(args) == 0
    second = load_recipe_release(store)
    assert second.release_id != old.release_id
    assert b"Revised synthetic name" in second.setting(NBS, publisher.IDENTITY)
    assert b"Revised synthetic name" not in old.setting(NBS, publisher.IDENTITY)
    assert (
        publisher.main(
            ["inspect", "--store", str(store), "--release-id", old.release_id]
        )
        == 0
    )
    assert old.release_id in capsys.readouterr().out
    assert load_recipe_release(store, old.release_id).table(NBS, "T6") == old.table(
        NBS, "T6"
    )


@pytest.mark.parametrize(
    "fault,expected",
    [
        ("typed evidence", "Stale generated EV"),
        ("typed economic", "Stale generated T6E"),
        ("missing identity", "Missing practice definition"),
        ("stale policy", "no authored T4_run_policy"),
        ("missing prose", "declaration disagrees"),
        ("empty declared policy", "Declared run policy is empty"),
        ("compiled effect", "Full-corpus rebuild differs"),
        ("undeclared recipe", "practices.csv"),
    ],
)
def test_failed_reconciliation_keeps_existing_pointer(
    snapshot, tmp_path, fault, expected
):
    store = tmp_path / "store"
    publish_release(store, {"prior.txt": b"prior selection"})
    previous = (store / "current.json").read_bytes()
    recipe = snapshot / "schema/recipes" / NBS
    if fault == "typed evidence":
        (snapshot / "schema/registers/EV_evidence_register.json").write_text(
            '[{"foreign":true}]'
        )
    elif fault == "typed economic":
        (recipe / "T6E_economic_profile.json").write_text("[{}]")
    elif fault == "missing identity":
        (recipe / publisher.IDENTITY).unlink()
    elif fault == "stale policy":
        (recipe / publisher.POLICY).with_suffix(".json").write_text("[]")
    elif fault == "missing prose":
        (recipe / publisher.PROSE).unlink()
    elif fault == "empty declared policy":
        index = snapshot / publisher.T4_INDEX
        with index.open(newline="", encoding="utf-8") as file:
            declarations = list(csv.DictReader(file))
        next(r for r in declarations if r["nbs_id"] == NBS)["run_policy"] = "true"
        rows(index, declarations)
        policy = recipe / publisher.POLICY
        rows(policy, [], ["nbs_id", "policy_id"])
        sync(policy)
    elif fault == "compiled effect":
        file = recipe / "T6_nbs_scorecard.csv"
        rows(file, [{"record_id": "invented", "nbs_id": NBS}])
        sync(file)
    else:
        (snapshot / publisher.T4_INDEX).unlink()
    with pytest.raises((ValueError, FileNotFoundError), match=expected):
        publisher.publish_recipes(snapshot, store, practices=[NBS])
    assert (store / "current.json").read_bytes() == previous


def test_writes_are_separate_and_source_edit_stops_publication(
    snapshot, tmp_path, monkeypatch
):
    with pytest.raises(ValueError, match="overlaps"):
        publisher.publish_recipes(snapshot, snapshot / "releases", practices=[NBS])
    assert not (snapshot / "releases").exists()
    real = publisher.publish_release

    def racing_publisher(store, members, *, verify_inputs):
        (snapshot / "schema/recipes" / NBS / publisher.PROSE).write_text('{"new":{}}')
        return real(store, members, verify_inputs=verify_inputs)

    monkeypatch.setattr(publisher, "publish_release", racing_publisher)
    store = tmp_path / "out"
    with pytest.raises(ValueError, match="changed"):
        publisher.publish_recipes(snapshot, store, practices=[NBS])
    assert not (store / "current.json").exists()


def test_default_selection_cannot_silently_drop_or_rename_practice(snapshot, tmp_path):
    registry = snapshot / publisher.FAMILIES
    with registry.open(encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle))
    rows(registry, [r for r in records if r["nbs_id"] == NBS])
    store = tmp_path / "store"
    publish_release(store, {"prior.txt": b"prior selection"})
    previous = (store / "current.json").read_bytes()
    with pytest.raises(ValueError, match="Incomplete practice inventory.*agroforestry"):
        publisher.publish_recipes(snapshot, store)
    assert (store / "current.json").read_bytes() == previous


def test_developer_contract_fingerprint_hold_stops_release(
    snapshot, tmp_path, monkeypatch
):
    # The existing developer view returns a readable hold for this condition.
    # A reconciled recipe publisher must decline to select it.
    original = publisher.developer_contract.build_contract

    def changed(*args, **kwargs):
        result = original(*args, **kwargs)
        result["contract"]["run_contract"]["approved_policies"] = [
            {"policy_id": "approved-first-pass", "status": "blocked_function_changed"}
        ]
        return result

    monkeypatch.setattr(publisher.developer_contract, "build_contract", changed)
    store = tmp_path / "store"
    with pytest.raises(ValueError, match="fingerprint changed: approved-first-pass"):
        publisher.publish_recipes(snapshot, store, practices=[NBS])
    assert not (store / "current.json").exists()
