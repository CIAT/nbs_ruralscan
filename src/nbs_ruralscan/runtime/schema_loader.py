"""Read all tables of a hash-pinned, reconciled recipe generation."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
import csv
from dataclasses import dataclass
import io
import json
from pathlib import Path
import re
from typing import TYPE_CHECKING, Any

from nbs_ruralscan.recipe.run_policy import compile_policies
from nbs_ruralscan.recipe.table_fields import TABLE_FIELDS
from nbs_ruralscan.schema_tools.generate import _coerce
from nbs_ruralscan.schema_tools.specialist_records import parse_json

if TYPE_CHECKING:
    from nbs_ruralscan.recipe.release_store import PinnedRelease


BOOT_FILE = "recipe-release.json"
PROVENANCE_FILE = "provenance.json"
TABLE_STEMS = {
    "T3": "T3_nbs_hazard_farming",
    "T4": "T4_suitability_mappings",
    "T6": "T6_nbs_scorecard",
    "T6E": "T6E_economic_profile",
}
REPORT_FILES = ("T3T6_synthesis_report.json", "T4_readiness.json")
_REGISTRY = "T0_nbs_registry.csv"
_T4_SETTINGS = "T4_settings.json"
_AUTHORED_SETTINGS = {
    "authored_mappings.csv",
    "mapping_settings.csv",
    "review_holds.csv",
}
_SETTING_FLAGS = {"run_policy": "T4_run_policy.csv", "effect_prose": "T3T6_prose.json"}


def table_path(practice: str, table: str, suffix: str) -> str:
    if suffix not in (".csv", ".json"):
        raise ValueError(f"Unknown recipe table extension: {suffix}")
    return f"tables/{practice}/{TABLE_STEMS[table]}{suffix}"


def report_path(practice: str, filename: str) -> str:
    if filename not in REPORT_FILES:
        raise ValueError(f"Unknown recipe report: {filename}")
    return f"tables/{practice}/{filename}"


def setting_path(practice: str, filename: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*\.(?:json|csv)", filename):
        raise ValueError(f"Invalid recipe setting filename: {filename}")
    return f"settings/{practice}/{filename}"


def _json(members, name):
    value = members.get(name)
    if not isinstance(value, bytes):
        raise ValueError(f"Missing recipe member: {name}")
    return parse_json(value.decode("utf-8"))


def _csv(members, name, required, *, frozen_order=False):
    value = members.get(name)
    if not isinstance(value, bytes):
        raise ValueError(f"Missing recipe member: {name}")
    with io.StringIO(value.decode("utf-8"), newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        headers = reader.fieldnames or []
        if (
            not headers
            or any(not key.strip() for key in headers)
            or len(set(headers)) != len(headers)
            or set(required) - set(headers)
            or frozen_order
            and headers != required
        ):
            raise ValueError(f"Invalid recipe columns: {name}")
        rows = list(reader)
    if any(None in row or None in row.values() for row in rows):
        raise ValueError(f"Invalid recipe record width: {name}")
    return rows


def _unique_strings(value, name):
    if (
        not isinstance(value, list)
        or any(not isinstance(s, str) or not s for s in value)
        or len({s.casefold() for s in value}) != len(value)
    ):
        raise ValueError(f"Invalid or duplicate recipe members in {name}")
    return set(value)


def _validate_settings(members, practice, declared):
    names = _unique_strings(declared, practice)
    t0 = setting_path(practice, _REGISTRY)
    setting = setting_path(practice, _T4_SETTINGS)
    settings = _json(members, setting)
    if not isinstance(settings, dict) or settings.get("nbs_id") != practice:
        raise ValueError(f"Wrong practice in {setting}")
    authored = _unique_strings(settings.get("files"), setting)
    if not authored.issubset(_AUTHORED_SETTINGS):
        raise ValueError(f"Unknown authored setting in {setting}")
    required = {t0, setting} | {setting_path(practice, f) for f in authored}
    for flag, filename in _SETTING_FLAGS.items():
        if not isinstance(settings.get(flag), bool):
            raise ValueError(f"Missing or invalid {flag} in {setting}")
        if settings[flag]:
            required.add(setting_path(practice, filename))
    if names != required:
        raise ValueError(f"Incomplete or unexpected recipe settings for {practice}")
    records = _csv(members, t0, ["nbs_id"])
    if len(records) != 1 or records[0]["nbs_id"] != practice:
        raise ValueError(f"Expected one {practice} registry row: {t0}")
    for name in names - {t0, setting}:
        if name.endswith(".csv"):
            rows = _csv(members, name, ["nbs_id"])
            if any(r["nbs_id"] != practice for r in rows):
                raise ValueError(f"Wrong practice in {name}")
        else:
            _json(members, name)
    return names


def _validate_table(members, practice, table, seen):
    csv_name = table_path(practice, table, ".csv")
    json_name = table_path(practice, table, ".json")
    key = "mapping_id" if table == "T4" else "record_id"
    records = _csv(members, csv_name, TABLE_FIELDS[table], frozen_order=True)
    typed = []
    for row in records:
        identifier = row[key]
        if (
            not identifier.strip()
            or not isinstance(_coerce(identifier), str)
            or identifier in seen
            or row["nbs_id"] != practice
        ):
            raise ValueError(
                f"Missing, duplicate or misplaced recipe row: {csv_name}, {identifier!r}"
            )
        seen.add(identifier)
        converted = {k: _coerce(v) for k, v in row.items()}
        typed.append({k: v for k, v in converted.items() if v is not None})
    document = _json(members, json_name)
    # Compare JSON types as well as values. Python treats True and 1 as equal.
    if json.dumps(typed, sort_keys=True, allow_nan=False) != json.dumps(
        document, sort_keys=True, allow_nan=False
    ):
        raise ValueError(f"Recipe CSV and typed JSON differ: {json_name}")
    return {row[key] for row in records}


def _validate_policies(members, practice, report):
    declared = report.get("approved_policy_ids")
    if "approved_policies" in report or not isinstance(declared, list):
        raise ValueError("Readiness must declare approved_policy_ids only")
    name = setting_path(practice, "T4_run_policy.csv")
    if name not in members:
        if declared:
            raise ValueError("Approved policy IDs have no authored T4 run policy")
        return
    records = _csv(
        members,
        name,
        [
            "policy_row_id",
            "policy_id",
            "nbs_id",
            "system",
            "output_label",
            "variable_group",
            "rule_id",
            "function_id",
            "function_fingerprint",
            "group_weight",
            "criterion_weight",
            "aggregation",
            "sensitivity_aggregation",
            "missing_values",
            "gate_policy",
            "applicability",
            "decision_reference",
        ],
    )
    _unique_strings([row["policy_row_id"] for row in records], name)
    for row in records:
        if (
            not row["policy_id"].strip()
            or not row["function_id"].strip()
            or not re.fullmatch(r"[0-9a-f]{64}", row["function_fingerprint"])
        ):
            raise ValueError(f"Invalid policy identity or function in {name}")
    # The policy compiler needs the projected options and gate/criterion roles.
    # It records a changed approved fingerprint as a hold during development.
    rules = [
        {
            "rule_id": row["rule_id"],
            "role": row["role"],
            "system": row["system"],
            "variable_group": row["variable_group"],
            "function_options": [
                {"function_id": key, "fingerprint": value}
                for key, value in row["functions"].items()
            ],
        }
        for row in report["rows"]
    ]
    policies = compile_policies(records, rules)
    if any(p["status"] == "blocked_function_changed" for p in policies):
        raise ValueError(
            f"Stale approved policy function in {name}; reconcile before release"
        )
    if declared != sorted(p["policy_id"] for p in policies):
        raise ValueError(f"Approved policy IDs disagree with {name}")


def _validate_reports(members, practice, ids):
    effect, readiness = (report_path(practice, name) for name in REPORT_FILES)
    report = _json(members, effect)
    if not isinstance(report, dict) or report.get("nbs_id") != practice:
        raise ValueError(f"Wrong practice in {effect}")
    for table in ("T3", "T6", "T6E"):
        count = report.get(table.lower() + "_rows")
        if type(count) is not int or count != len(ids[table]):
            raise ValueError(f"{table} row count disagrees with {effect}")

    reviewed = _json(members, readiness)
    if not isinstance(reviewed, dict) or reviewed.get("nbs_id") != practice:
        raise ValueError(f"Wrong practice in {readiness}")
    if reviewed.get("contract_version") != "0.2.0":
        raise ValueError(f"Unsupported T4 readiness contract version: {readiness}")
    if reviewed.get("execution_ready") is not False or not isinstance(
        reviewed.get("rows"), list
    ):
        raise ValueError(f"Malformed reconciled readiness report: {readiness}")
    states = Counter()
    rules = set()
    for row in reviewed["rows"]:
        if not isinstance(row, dict) or not isinstance(row.get("readiness"), dict):
            raise ValueError(f"Invalid readiness row in {readiness}")
        key = row.get("rule_id")
        state = row["readiness"].get("state")
        functions = row.get("functions")
        if (
            not isinstance(key, str)
            or not key.strip()
            or key in rules
            or any(
                not isinstance(row.get(k), str) or not row[k].strip()
                for k in ("system", "variable_group")
            )
            or row.get("role")
            not in (
                "suitability_score",
                "operational_scenario",
                "eligibility_gate",
                "hard_exclusion",
                "reference_only",
            )
            or (row["role"] == "reference_only") != (state == "reference_only")
            or state not in ("defined", "provisional", "blocked", "reference_only")
            or (key not in ids["T4"] and state != "reference_only")
            or row["readiness"].get("execution_ready") is not False
            or not isinstance(functions, dict)
            or any(
                not k.strip()
                or not isinstance(v, str)
                or not re.fullmatch(r"[0-9a-f]{64}", v)
                for k, v in functions.items()
            )
        ):
            raise ValueError(
                f"Invalid or misplaced T4 readiness rule {key}: {readiness}"
            )
        selected = row["readiness"].get("effective_function_id")
        fingerprint = row["readiness"].get("effective_function_fingerprint")
        if (
            selected is not None
            and (not isinstance(selected, str) or selected not in functions)
            or fingerprint != functions.get(selected)
        ):
            raise ValueError(f"Invalid selected function fingerprint for {key}")
        rules.add(key)
        states[state] += 1
    summary = reviewed.get("implementation_readiness")
    if (
        not ids["T4"].issubset(rules)
        or not isinstance(summary, dict)
        or any(type(value) is not int for value in summary.values())
        or dict(states) != summary
    ):
        raise ValueError(
            f"Mismatch between T4 mappings and readiness report: {readiness}"
        )
    _validate_policies(members, practice, reviewed)
    return effect, readiness


def validate_recipe_members(members: Mapping[str, bytes]) -> None:
    """Validate the complete logical inventory before publication and on open."""
    boot = _json(members, BOOT_FILE)
    if (
        not isinstance(boot, dict)
        or set(boot) != {"format_version", "kind", "practices"}
        or type(boot["format_version"]) is not int
        or boot["format_version"] != 1
        or boot["kind"] != "reconciled_recipe"
    ):
        raise ValueError("Unsupported recipe release kind or format version")
    practices = boot["practices"]
    if not isinstance(practices, dict) or not practices:
        raise ValueError("A recipe release must declare its practices")
    provenance = _json(members, PROVENANCE_FILE)
    if not isinstance(provenance, dict) or any(
        not isinstance(provenance.get(k), str) or not provenance[k].strip()
        for k in ("source_revision", "schema_version")
    ):
        raise ValueError("Invalid recipe release provenance")
    if provenance["schema_version"] != "0.4.0-structure-frozen":
        raise ValueError(
            f"Unsupported recipe schema version: {provenance['schema_version']}"
        )
    for name in ("inputs_sha256", "compiler_sha256"):
        hashes = provenance.get(name)
        if (
            not isinstance(hashes, dict)
            or not hashes
            or any(
                not key.strip()
                or not isinstance(digest, str)
                or not re.fullmatch(r"[0-9a-f]{64}", digest)
                for key, digest in hashes.items()
            )
        ):
            raise ValueError(f"Invalid {name} in recipe release provenance")
    expected = {BOOT_FILE, PROVENANCE_FILE}
    seen = {table: set() for table in TABLE_STEMS}
    for practice, details in practices.items():
        if (
            not re.fullmatch(r"[a-z][a-z0-9_]*", practice)
            or not isinstance(details, dict)
            or set(details) != {"settings"}
        ):
            raise ValueError(f"Invalid recipe practice declaration: {practice}")
        expected.update(_validate_settings(members, practice, details["settings"]))
        ids = {}
        for table in TABLE_STEMS:
            ids[table] = _validate_table(members, practice, table, seen[table])
            expected.update(
                table_path(practice, table, suffix) for suffix in (".csv", ".json")
            )
        expected.update(_validate_reports(members, practice, ids))
    if set(members) != expected:
        raise ValueError(
            "Recipe release contains missing or undeclared logical members"
        )


@dataclass(frozen=True)
class RecipeRelease:
    """One resolved generation. Later store updates do not change this selection."""

    _pin: PinnedRelease
    practices: tuple[str, ...]

    @property
    def release_id(self) -> str:
        return self._pin.release_id

    def read_bytes(self, name: str) -> bytes:
        return self._pin.read_bytes(name)

    def table(self, practice: str, table: str) -> list[dict[str, Any]]:
        if practice not in self.practices or table not in TABLE_STEMS:
            raise KeyError((practice, table))
        return parse_json(
            self.read_bytes(table_path(practice, table, ".json")).decode("utf-8")
        )

    def setting(self, practice: str, filename: str) -> bytes:
        if practice not in self.practices:
            raise KeyError(practice)
        return self.read_bytes(setting_path(practice, filename))


def load_recipe_release(store: Path, release_id: str | None = None) -> RecipeRelease:
    """Pin once, then verify every file and the shared generation contract."""
    from nbs_ruralscan.recipe.release_store import open_release

    pin = open_release(store, release_id)
    members = {name: pin.read_bytes(name) for name in pin.files}
    validate_recipe_members(members)
    return RecipeRelease(pin, tuple(sorted(_json(members, BOOT_FILE)["practices"])))


open_recipe_release = load_recipe_release
