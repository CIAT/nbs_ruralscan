"""Adversarial contract checks against reviewed corpus and existing numeric executor."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from nbs_ruralscan.recipe import developer_contract as dc
from nbs_ruralscan.runtime.binding import Binding
from nbs_ruralscan.runtime.numeric import evaluate_numeric

ROOT = Path(__file__).resolve().parents[1]
SLOPE = "agroforestry__planted_silvoarable__slope"
NDVI = "agroforestry__cross_family__ndvi"


@pytest.fixture(scope="module")
def baseline():
    return dc.build_contract(ROOT, country="HTI")


def indexed(result):
    return {r["rule_id"]: r for r in result["contract"]["rows"]}


def selection(result, rule=NDVI, **overrides):
    row = indexed(result)[rule]
    option = row["function_options"][0]
    return {
        "contract_version": dc.VERSION,
        "selections": {
            rule: {
                "function_id": option["function_id"],
                "function_fingerprint": option["fingerprint"],
                "target_system": "agroforestry__planted_silvoarable",
                "applicability_country": "HTI",
                "applicability_note": "Explicit scoping transfer scenario for test",
                "decision_reference": "test-decision-001",
                **overrides,
            }
        },
    }


def score(option, xs):
    return evaluate_numeric(
        {
            "relationship_type": "piecewise",
            "relationship_params": {
                "profiles": [
                    {
                        "profile_id": option["function_id"],
                        "intervals": option["intervals"],
                    }
                ]
            },
        },
        xs,
        profile_id=option["function_id"],
    )


def test_target_country_does_not_filter_evidence_or_select_profiles(baseline):
    india_target = dc.build_contract(ROOT, country="IND")
    for rid, row in indexed(baseline).items():
        assert row["function_options"] == indexed(india_target)[rid]["function_options"]
        if row["role"] == "suitability_score":
            assert row["function_id"] is None
    assert not baseline["contract"]["run_contract"]["execution_ready"]


def test_study_country_filter_preserves_designs_and_separate_unknowns(baseline):
    filtered = dc.build_contract(ROOT, country="HTI", evidence_countries=["India"])
    for row in indexed(filtered).values():
        if row["role"] == "suitability_score":
            assert all(
                dc.country_match(o["context"], ["India"])
                for o in row["function_options"]
            )
        elif row["role"] == "eligibility_gate":
            assert (
                row["function_options"]
                == indexed(baseline)[row["rule_id"]]["function_options"]
            )
    congo = indexed(filtered)["agroforestry__cross_family__elevation"]
    assert congo["function_options"] == []
    assert congo["status"] == "blocked"
    assert any(not e["matches_evidence_country"] for e in filtered["evidence"])
    coded = dc.build_contract(ROOT, evidence_countries=["IND"])
    assert indexed(coded)[NDVI]["function_options"] == []
    assert indexed(filtered)[NDVI]["function_options"]
    with pytest.raises(ValueError, match="Unknown evidence-country"):
        dc.build_contract(ROOT, evidence_countries=["Not a recorded country"])
    assert not dc.country_match({"study_country": "India"}, ["Ind"])
    assert not dc.country_match({}, ["India"])


def test_slope_binary_and_pool_are_distinct_and_match_existing_executor(baseline):
    row = indexed(baseline)[SLOPE]
    options = {o["kind"]: o for o in row["function_options"]}
    xs = [2, 7, 12, 17, 30, 45, np.nan]
    np.testing.assert_allclose(
        score(options["numeric_threshold"], xs),
        [1, 1, 1, 1, 0, 0, np.nan],
        equal_nan=True,
    )
    np.testing.assert_allclose(
        score(options["harmonized_pool"], xs),
        [0.9, 0.75, 0.5, 0.25, np.nan, 0.25, np.nan],
        equal_nan=True,
    )
    assert row["function_id"] is None
    ndvi = indexed(baseline)[NDVI]["function_options"][0]
    np.testing.assert_allclose(
        score(ndvi, [0.1, 0.2, 0.5, 0.6, np.nan]),
        [0.25, 0.5, 0.5, 0.75, np.nan],
        equal_nan=True,
    )


def test_filtered_pool_recomputed_from_retained_members_not_cached_cells():
    raw = next(
        r
        for r in dc.read_csv(
            ROOT / "schema/recipes/agroforestry/T4_suitability_mappings.csv"
        )
        if r["mapping_id"] == SLOPE
    )
    params = json.loads(raw["relationship_params"])
    # Fixture intervention: make Nath a different study country while leaving the
    # precompiled two-paper pool intact. Filter must recompute from Ahmad alone.
    next(p for p in params["profiles"] if p["source_id"] == "nath_2021")["context"][
        "study_country"
    ] = "Ethiopia"
    raw["relationship_params"] = json.dumps(params)
    ev = {
        r["evidence_id"]: r
        for r in dc.read_csv(ROOT / "schema/registers/EV_evidence_register.csv")
    }
    src = {
        r["source_id"]: r
        for r in dc.read_csv(ROOT / "schema/registers/SRC_source_register.csv")
    }
    opts = dc._options(raw, ev, src, ["India"])
    pool = next(o for o in opts if o["kind"] == "harmonized_pool")
    assert pool["source_ids"] == ["ahmad_2018"]
    np.testing.assert_allclose(score(pool, [2, 7, 30]), [0.75, 0.5, 0.25])


@pytest.mark.parametrize(
    "change,match",
    [
        ({"function_fingerprint": "stale"}, "stale function"),
        ({"applicability_country": "IND"}, "matching target country"),
        ({"decision_reference": ""}, "decision reference"),
        ({"target_system": "agroforestry__cross_family"}, "Invalid target system"),
        ({"runtime_weight": -0.1}, "Invalid runtime weight"),
        ({"runtime_weight": True}, "Invalid runtime weight"),
        ({"runtime_weight": float("nan")}, "Invalid runtime weight"),
    ],
)
def test_invalid_selection_metadata_refused(baseline, change, match):
    with pytest.raises(ValueError, match=match):
        dc.build_contract(ROOT, country="HTI", selection=selection(baseline, **change))


def test_selected_profile_records_decision_without_claiming_execution_ready(baseline):
    built = dc.build_contract(
        ROOT, country="HTI", selection=selection(baseline, runtime_weight=1.0)
    )
    row = indexed(built)[NDVI]
    assert row["function_id"].startswith("profile:")
    assert row["weight"]["runtime_weight"] == 1
    assert row["target_system"] == "agroforestry__planted_silvoarable"
    assert not built["contract"]["run_contract"]["execution_ready"]


def test_unapproved_links_rejected_even_if_upstream_payload_is_corrupted(monkeypatch):
    original = dc.rebuild

    def corrupt(root, nbs):
        payload = original(root, nbs)
        next(
            r
            for r in payload["evidence"]
            if r["evidence_id"] == "ev_T4_canopy_ahmad2018_1"
        )["reviewer_ok"] = "false"
        return payload

    monkeypatch.setattr(dc, "rebuild", corrupt)
    with pytest.raises(ValueError, match="unapproved, dropped or missing"):
        dc.build_contract(ROOT)


def test_bind_upload_fallback_keeps_band_and_categorical_mismatch_visible():
    bindings = [
        Binding(
            "local",
            "land_cover",
            "admin_country",
            "HTI",
            "",
            1,
            "requires_upload",
            "local survey needed",
        ),
        Binding(
            "global",
            "land_cover",
            "global",
            "",
            "alternate_codes",
            1,
            "catalogued",
            band="classes",
        ),
    ]
    result = dc._binding(
        "land_cover",
        "esa_worldcover_2021",
        bindings,
        {"alternate_codes": {}},
        {},
        {"HTI"},
    )
    assert result["needs_upload"]
    assert result["dataset_id"] == "alternate_codes"
    assert result["band"] == "classes"
    assert result["preferred_binding_id"] == "local"
    assert result["binding_differs_from_recipe"]


def test_package_reproducible_and_every_output_hash_valid(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    a = dc.write_package(ROOT, first, country="HTI")
    b = dc.write_package(ROOT, second, country="HTI")
    assert a == b
    assert {p.name: p.read_bytes() for p in first.iterdir()} == {
        p.name: p.read_bytes() for p in second.iterdir()
    }
    for name, sha in a["output_sha256"].items():
        assert hashlib.sha256((first / name).read_bytes()).hexdigest() == sha
    with pytest.raises(ValueError, match="must be empty"):
        dc.write_package(ROOT, first)
    with pytest.raises(ValueError, match="authoritative inputs"):
        dc.write_package(ROOT, ROOT / "schema" / "never_write_here")


@pytest.mark.parametrize("weights", [(1.1,), (0.5,)])
def test_runtime_weights_must_be_normalized_within_selected_system(baseline, weights):
    with pytest.raises(ValueError, match="weight|Weight"):
        dc.build_contract(
            ROOT,
            country="HTI",
            selection=selection(baseline, runtime_weight=weights[0]),
        )


def test_duplicate_selected_system_criterion_refused(baseline):
    picks = selection(baseline, rule=SLOPE)
    duplicate = selection(baseline, rule="agroforestry__cross_family__slope")
    picks["selections"].update(duplicate["selections"])
    with pytest.raises(ValueError, match="[Dd]uplicate|one function"):
        dc.build_contract(ROOT, country="HTI", selection=picks)


def test_mixed_missing_and_supplied_selected_weights_refused(baseline):
    picks = selection(baseline, runtime_weight=1.0)
    picks["selections"].update(selection(baseline, rule=SLOPE)["selections"])
    with pytest.raises(ValueError, match="weight|Weight"):
        dc.build_contract(ROOT, country="HTI", selection=picks)


def test_input_mutation_during_package_build_rejected(tmp_path, baseline, monkeypatch):
    import shutil
    from types import SimpleNamespace

    checkout = tmp_path / "source"
    files = set(baseline["inputs"]) | {
        "methodology/T4_developer_contract.md",
        "handoff/agroforestry-t4/IMPLEMENTATION.md",
        "handoff/agroforestry-t4/START_HERE.md",
        "scripts/build-t4-developer.py",
        "pyproject.toml",
        "uv.lock",
    }
    files |= {
        str(p.relative_to(ROOT))
        for folder in ("src/nbs_ruralscan/recipe", "src/nbs_ruralscan/runtime")
        for p in (ROOT / folder).glob("*.py")
    }
    for name in files:
        dest = checkout / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
    original = dc._write_csv
    changed = False

    def mutate_after_compile(path, rows):
        nonlocal changed
        original(path, rows)
        if not changed:
            changed = True
            source = checkout / "schema/T1_data_registry.csv"
            source.write_bytes(source.read_bytes() + b"\n")

    monkeypatch.setattr(dc, "_write_csv", mutate_after_compile)
    monkeypatch.setattr(
        dc.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(stdout="test-commit"),
    )
    with pytest.raises(
        (ValueError, RuntimeError), match="[Ii]nputs?.*chang|[Cc]hang.*input"
    ):
        dc.write_package(checkout, tmp_path / "output", country="HTI")


def test_complete_selected_weight_vector_keeps_masks_outside_denominator(baseline):
    picks = selection(baseline, runtime_weight=0.4)
    picks["selections"].update(
        selection(baseline, rule=SLOPE, runtime_weight=0.6)["selections"]
    )
    result = dc.build_contract(ROOT, country="HTI", selection=picks)
    rows = indexed(result)
    assert rows[NDVI]["weight"]["runtime_weight"] == 0.4
    assert rows[SLOPE]["weight"]["runtime_weight"] == 0.6
    assert all(
        r["weight"]["runtime_weight"] is None
        for r in rows.values()
        if r["role"] == "eligibility_gate"
    )
    assert result["contract"]["run_contract"]["execution_ready"] is False


def test_gate_conformance_preserves_host_presence_absence_and_unknown(baseline):
    fixtures = [f for f in baseline["fixtures"] if "host_masks" in f]
    assert len(fixtures) == 21  # seven gates, three host states each
    coffee = {
        f["case"]: f for f in fixtures if f["rule_id"] == "agro_shaded_coffee_host_gate"
    }
    assert set(coffee) == {"host_present", "host_absent", "host_unknown"}
    expected = {"host_present": 1.0, "host_absent": 0.0, "host_unknown": None}
    for case, fixture in coffee.items():
        lookup = dict(zip(fixture["input"], fixture["expected"], strict=True))
        assert lookup[10] == expected[case]
        assert lookup[40] == expected[case]
        assert lookup[50] == 0  # built-up is excluded even with unknown host data
        assert lookup[80] == 0
        assert lookup[None] is None
        assert lookup[81] is None  # unlisted code is unknown, not unsuitable
        assert fixture["dataset_id"] == "esa_worldcover_2021"
        assert (
            fixture["mask_metadata"]["coffee_host_fraction"]["unit"]
            == "fraction_of_pixel"
        )


def test_package_verifier_detects_payload_and_pinned_input_tampering(tmp_path):
    import shutil

    output = tmp_path / "package"
    manifest = dc.write_package(ROOT, output, country="HTI")
    assert dc.verify_package(ROOT, output) == manifest
    assert manifest["package_version"] == dc.PACKAGE_VERSION
    assert manifest["contract_version"] == dc.VERSION
    assert f"developer-v{dc.PACKAGE_VERSION}" in (output / "VERSION").read_text()
    assert f"contract_version={dc.VERSION}" in (output / "VERSION").read_text()
    assert (
        "[developer_contract.json](developer_contract.json)"
        in (output / "START_HERE.md").read_text()
    )
    assert (
        "[the implementation task brief](START_HERE.md)"
        in (output / "IMPLEMENTATION.md").read_text()
    )
    payload = output / "function_intervals.csv"
    original = payload.read_bytes()
    payload.write_bytes(original + b"tampered\n")
    with pytest.raises(
        ValueError, match="hash verification failed: function_intervals.csv"
    ):
        dc.verify_package(ROOT, output)
    payload.write_bytes(original)
    snapshot = tmp_path / "pinned-inputs"
    for name in manifest["input_sha256"]:
        target = snapshot / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    # Verification is content-pinned; a different checkout location/HEAD is valid.
    assert dc.verify_package(snapshot, output) == manifest
    for name in (
        "src/nbs_ruralscan/recipe/developer_contract.py",
        "schema/T1_data_registry.csv",
    ):
        target = snapshot / name
        saved = target.read_bytes()
        target.write_bytes(saved + b"\nchanged\n")
        with pytest.raises(ValueError, match="hash verification failed"):
            dc.verify_package(snapshot, output)
        target.write_bytes(saved)
    payload.unlink()
    with pytest.raises(
        ValueError, match="hash verification failed: function_intervals.csv"
    ):
        dc.verify_package(snapshot, output)
