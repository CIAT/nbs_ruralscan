"""Use a complete, verified generation across T4 and the effect tables."""

import csv
import io
import json

import pytest

from nbs_ruralscan.recipe.release_store import publish_release
from nbs_ruralscan.recipe.table_fields import TABLE_FIELDS
from nbs_ruralscan.runtime import effect_rows
from nbs_ruralscan.runtime.schema_loader import (
    BOOT_FILE,
    PROVENANCE_FILE,
    TABLE_STEMS,
    load_recipe_release,
    report_path,
    setting_path,
    table_path,
    validate_recipe_members,
)


def encoded(value):
    return json.dumps(value).encode()


def csv_bytes(fields, rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode()


def example(practices=("forest", "wetland"), direction="positive"):
    files = {}
    details = {}
    for name in practices:
        settings = []
        for leaf, data in {
            "T0_nbs_registry.csv": csv_bytes(["nbs_id"], [{"nbs_id": name}]),
            "T4_settings.json": encoded(
                {
                    "nbs_id": name,
                    "files": ["mapping_settings.csv"],
                    "effect_prose": False,
                    "run_policy": False,
                }
            ),
            "mapping_settings.csv": csv_bytes(
                ["nbs_id", "weight"], [{"nbs_id": name, "weight": "0.4"}]
            ),
        }.items():
            member = setting_path(name, leaf)
            settings.append(member)
            files[member] = data
        details[name] = {"settings": settings}
        for table in TABLE_STEMS:
            key = "mapping_id" if table == "T4" else "record_id"
            row = {"nbs_id": name, key: f"{name}__{table}"}
            raw = dict(row)
            if table == "T3":
                raw["landscape_scale_only"] = "true"
                raw["caveats"] = "null"
                row["landscape_scale_only"] = True
            if table == "T6":
                raw.update(
                    {"effect_direction": direction, "evidence_ids": '["ev2","ev1"]'}
                )
                row.update(
                    {"effect_direction": direction, "evidence_ids": ["ev2", "ev1"]}
                )
            empty = name == "forest" and table == "T4"
            files[table_path(name, table, ".csv")] = csv_bytes(
                TABLE_FIELDS[table], [] if empty else [raw]
            )
            files[table_path(name, table, ".json")] = encoded([] if empty else [row])
        files[report_path(name, "T3T6_synthesis_report.json")] = encoded(
            {"nbs_id": name, "t3_rows": 1, "t6_rows": 1, "t6e_rows": 1}
        )
        files[report_path(name, "T4_readiness.json")] = encoded(
            dict(
                nbs_id=name,
                contract_version="0.2.0",
                approved_policy_ids=[],
                execution_ready=False,
                implementation_readiness=({} if name == "forest" else {"defined": 1}),
                rows=(
                    []
                    if name == "forest"
                    else [
                        dict(
                            rule_id=f"{name}__T4",
                            role="suitability_score",
                            system=name,
                            variable_group="soil",
                            functions={},
                            readiness=dict(state="defined", execution_ready=False),
                        )
                    ]
                ),
            )
        )
    files[BOOT_FILE] = encoded(
        dict(format_version=1, kind="reconciled_recipe", practices=details)
    )
    files[PROVENANCE_FILE] = encoded(
        dict(
            source_revision="snapshot",
            schema_version="0.4.0-structure-frozen",
            compiler_sha256={"compiler": "a" * 64},
            inputs_sha256={"input": "b" * 64},
        )
    )
    return files


def test_complete_reader_remains_pinned_across_publication_and_explicit_rollback(
    tmp_path,
):
    store = tmp_path / "store"
    old = publish_release(store, example()).release_id
    earlier = load_recipe_release(store)
    new = publish_release(store, example(direction="negative")).release_id
    current = load_recipe_release(store)
    assert old != new and current.release_id == new and earlier.release_id == old
    assert (
        earlier.practices == ("forest", "wetland")
        and earlier.table("forest", "T4") == []
    )
    assert earlier.table("wetland", "T4")[0]["mapping_id"] == "wetland__T4"
    assert earlier.setting("forest", "T0_nbs_registry.csv") == b"nbs_id\nforest\n"
    assert earlier.table("wetland", "T3")[0]["landscape_scale_only"] is True
    assert [
        row["effect_direction"] for row in effect_rows.load_rows(earlier, "T6")
    ] == ["positive", "positive"]
    assert current.table("wetland", "T6")[0]["effect_direction"] == "negative"
    assert current.table("wetland", "T6")[0]["evidence_ids"] == ["ev2", "ev1"]
    assert load_recipe_release(store, old).table("forest", "T6E") == earlier.table(
        "forest", "T6E"
    )
    with pytest.raises(KeyError):
        effect_rows.load_rows(earlier, "T4")
    with pytest.raises(KeyError):
        earlier.table("absent", "T6")


def test_mutable_checkout_and_pinned_loader_agree(tmp_path):
    files = example()
    root = tmp_path / "schema"
    for name in ("forest", "wetland"):
        for table in effect_rows.TABLES:
            path = root / "recipes" / name / effect_rows.TABLES[table]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(files[table_path(name, table, ".json")])
    store = tmp_path / "store"
    publish_release(store, files)
    release = load_recipe_release(store)
    for table in effect_rows.TABLES:
        assert effect_rows.load_rows(release, table) == effect_rows.load_rows(
            root, table
        )


@pytest.mark.parametrize(
    "problem",
    [
        "missing",
        "extra",
        "csv_types",
        "empty_header",
        "reordered_columns",
        "duplicate_id",
        "wrong_practice",
        "unlisted_setting",
        "stray_setting",
        "registry",
        "unknown_version",
        "flag_ready",
        "missing_policy",
        "undeclared_prose",
        "wrong_effect_count",
        "unknown_t4_rule",
        "unsupported_schema",
        "unsupported_contract",
        "malformed_hash",
    ],
)
def test_invalid_bundles_refused_by_shared_validation_and_reader(tmp_path, problem):
    files = example(("forest",))

    def one(table, ext):
        return table_path("forest", table, ext)

    boot = json.loads(files[BOOT_FILE])
    if problem == "missing":
        del files[one("T6E", ".json")]
    elif problem == "extra":
        files["extra.csv"] = b"x\n"
    elif problem == "csv_types":
        records = json.loads(files[one("T3", ".json")])
        records[0]["landscape_scale_only"] = 1
        files[one("T3", ".json")] = encoded(records)
    elif problem == "empty_header":
        files[one("T4", ".csv")] = b"mapping_id,nbs_id\n"
    elif problem == "reordered_columns":
        files[one("T4", ".csv")] = csv_bytes(list(reversed(TABLE_FIELDS["T4"])), [])
    elif problem == "duplicate_id":
        csv_file = one("T6", ".csv")
        files[csv_file] += files[csv_file].splitlines(keepends=True)[1]
        path = one("T6", ".json")
        files[path] = encoded(json.loads(files[path]) * 2)
    elif problem == "wrong_practice":
        for ext in (".csv", ".json"):
            p = one("T6", ext)
            files[p] = files[p].replace(b"forest", b"other")
    elif problem == "unlisted_setting":
        boot["practices"]["forest"]["settings"].remove(
            setting_path("forest", "mapping_settings.csv")
        )
    elif problem == "stray_setting":
        key = setting_path("forest", "private_notes.csv")
        boot["practices"]["forest"]["settings"].append(key)
        files[key] = b"note\ninternal\n"
        files[setting_path("forest", "T4_settings.json")] = encoded(
            {"nbs_id": "forest", "files": ["mapping_settings.csv", "private_notes.csv"]}
        )
    elif problem == "registry":
        files[setting_path("forest", "T0_nbs_registry.csv")] = (
            b"nbs_id\nforest\nother\n"
        )
    elif problem == "unknown_version":
        boot["format_version"] = True
    elif problem == "wrong_effect_count":
        key = report_path("forest", "T3T6_synthesis_report.json")
        files[key] = encoded(dict(json.loads(files[key]), t6e_rows=0))
    elif problem == "missing_policy":
        key = setting_path("forest", "T4_settings.json")
        files[key] = encoded(dict(json.loads(files[key]), run_policy=True))
    elif problem == "undeclared_prose":
        key = setting_path("forest", "T3T6_prose.json")
        files[key] = encoded({})
        boot["practices"]["forest"]["settings"].append(key)
    elif problem == "unknown_t4_rule":
        key = report_path("forest", "T4_readiness.json")
        files[key] = encoded(
            dict(
                json.loads(files[key]),
                implementation_readiness={"defined": 1},
                rows=[
                    dict(
                        rule_id="other",
                        role="suitability_score",
                        system="forest",
                        variable_group="soil",
                        functions={},
                        readiness=dict(state="defined", execution_ready=False),
                    )
                ],
            )
        )
    elif problem == "unsupported_schema":
        files[PROVENANCE_FILE] = encoded(
            dict(json.loads(files[PROVENANCE_FILE]), schema_version="0.9")
        )
    elif problem == "unsupported_contract":
        key = report_path("forest", "T4_readiness.json")
        files[key] = encoded(dict(json.loads(files[key]), contract_version="2"))
    elif problem == "flag_ready":
        p = report_path("forest", "T4_readiness.json")
        files[p] = encoded(dict(json.loads(files[p]), execution_ready=True))
    elif problem == "malformed_hash":
        p = json.loads(files[PROVENANCE_FILE])
        p["compiler_sha256"] = {"source": "bogus"}
        files[PROVENANCE_FILE] = encoded(p)
    files[BOOT_FILE] = encoded(boot)
    with pytest.raises(ValueError):
        validate_recipe_members(files)
    store = tmp_path / "store"
    publish_release(store, files)
    with pytest.raises(ValueError):
        load_recipe_release(store)


def test_declared_prose_and_reference_only_rule(tmp_path):
    files = example(("forest",))
    key = setting_path("forest", "T4_settings.json")
    files[key] = encoded(
        dict(json.loads(files[key]), run_policy=False, effect_prose=True)
    )
    prose = setting_path("forest", "T3T6_prose.json")
    files[prose] = encoded({})
    boot = json.loads(files[BOOT_FILE])
    boot["practices"]["forest"]["settings"].append(prose)
    files[BOOT_FILE] = encoded(boot)
    ready = report_path("forest", "T4_readiness.json")
    files[ready] = encoded(
        dict(
            json.loads(files[ready]),
            implementation_readiness={"reference_only": 1},
            rows=[
                dict(
                    rule_id="reference__forest__tenure",
                    role="reference_only",
                    system="See evidence contexts",
                    variable_group="land",
                    functions={},
                    readiness=dict(state="reference_only", execution_ready=False),
                )
            ],
        )
    )
    store = tmp_path / "store"
    publish_release(store, files)
    loaded = load_recipe_release(store)
    assert loaded.table("forest", "T4") == []
    assert loaded.setting("forest", "T3T6_prose.json") == files[prose]


@pytest.fixture
def policy_bundle():
    """Exercise the historical v0.1.7 policy shape with independently authored rows."""
    from pathlib import Path
    from nbs_ruralscan.schema_tools.generate import _csv_to_rows

    name = "agroforestry"
    folder = (
        Path(__file__).resolve().parents[1] / "handoff/agroforestry-t4/developer-v0.1.7"
    )
    contract = json.loads((folder / "developer_contract.json").read_bytes())
    files = example((name,))
    path = folder / "T4_suitability_mappings.csv"
    files[table_path(name, "T4", ".csv")] = path.read_bytes()
    files[table_path(name, "T4", ".json")] = encoded(_csv_to_rows(path))
    settings = setting_path(name, "T4_settings.json")
    files[settings] = encoded(dict(json.loads(files[settings]), run_policy=True))
    policy_csv = setting_path(name, "T4_run_policy.csv")
    boot = json.loads(files[BOOT_FILE])
    boot["practices"][name]["settings"].append(policy_csv)
    files[BOOT_FILE] = encoded(boot)
    policies = contract["run_contract"]["approved_policies"]
    policy = policies[0]
    shared = {
        k: policy[k]
        for k in [
            "nbs_id",
            "system",
            "output_label",
            "aggregation",
            "sensitivity_aggregation",
            "missing_values",
            "gate_policy",
            "applicability",
            "decision_reference",
        ]
    }
    authored = []
    for c in policy["criteria"]:
        authored.append(
            dict(
                policy_row_id=policy["policy_id"] + "__" + c["rule_id"],
                policy_id=policy["policy_id"],
                **shared,
                rule_id=c["rule_id"],
                function_id=c["function_id"],
                function_fingerprint=c["function_fingerprint"],
                variable_group=c["variable_group"],
                criterion_weight=str(c["weight"]),
                group_weight=str(policy["group_budgets"][c["variable_group"]]),
            )
        )
    files[policy_csv] = csv_bytes(list(authored[0]), authored)
    report = report_path(name, "T4_readiness.json")
    files[report] = encoded(
        dict(
            nbs_id=name,
            contract_version="0.2.0",
            execution_ready=False,
            approved_policy_ids=sorted(p["policy_id"] for p in policies),
            implementation_readiness=contract["summary"]["implementation_readiness"],
            rows=[
                dict(
                    rule_id=r["rule_id"],
                    role=r["role"],
                    system=r["system"],
                    variable_group=r["variable_group"],
                    readiness=r["readiness"],
                    functions={
                        fn["function_id"]: fn["fingerprint"]
                        for fn in r["function_options"]
                    },
                )
                for r in contract["rows"]
            ],
        )
    )
    return files, report


def test_historical_policy_recompiles_and_changed_fingerprint_blocks_release(
    policy_bundle,
):
    files, key = policy_bundle
    validate_recipe_members(files)
    report = json.loads(files[key])
    policy_name = setting_path("agroforestry", "T4_run_policy.csv")
    criteria = list(csv.DictReader(io.StringIO(files[policy_name].decode())))
    # The compiler holds a stale approved option instead of raising. Publishing must fail closed.
    criteria[0]["function_fingerprint"] = "a" * 64
    files[policy_name] = csv_bytes(list(criteria[0]), criteria)
    assert report["approved_policy_ids"]
    with pytest.raises(ValueError, match="Stale approved policy"):
        validate_recipe_members(files)


@pytest.mark.parametrize(
    "problem",
    [
        "missing_list",
        "forged",
        "omitted",
        "duplicate",
        "legacy",
        "wrong_weight",
        "missing_gate",
        "unknown_rule",
    ],
)
def test_inconsistent_policy_ids_and_authored_inputs_are_refused(
    policy_bundle, problem
):
    files, key = policy_bundle
    report = json.loads(files[key])
    if problem == "missing_list":
        del report["approved_policy_ids"]
    elif problem == "forged":
        files = example(("agroforestry",))
        report = json.loads(files[key])
        report["approved_policy_ids"] = ["forged"]
    elif problem == "omitted":
        report["approved_policy_ids"] = []
    elif problem == "duplicate":
        report["approved_policy_ids"] *= 2
    elif problem == "legacy":
        report["approved_policies"] = []
    elif problem == "missing_gate":
        for rule in report["rows"]:
            if rule["role"] == "hard_exclusion":
                rule["role"] = "operational_scenario"
    else:
        path = setting_path("agroforestry", "T4_run_policy.csv")
        rows = list(csv.DictReader(io.StringIO(files[path].decode())))
        if problem == "wrong_weight":
            rows[0]["criterion_weight"] = "0"
        else:
            rows[0]["rule_id"] = "unknown"
        files[path] = csv_bytes(list(rows[0]), rows)
    files[key] = encoded(report)
    with pytest.raises(ValueError, match="(?i)polic|approv|criter|gate"):
        validate_recipe_members(files)
