#!/usr/bin/env python3
"""Compare a local recipe release through the reference and independently installed runtime readers."""

from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

TABLES = ("T3", "T4", "T6", "T6E")
EFFECT_REPORT = "T3T6_synthesis_report.json"
READINESS = "T4_readiness.json"


def json_digest(value) -> str:
    data = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return sha256(data.encode("utf-8")).hexdigest()


def summarize(release, settings, get_report, provenance):
    """Summarize values returned by the reader. Preserve row order and JSON scalar types."""
    artifacts = {"provenance.json": json_digest(provenance)}
    practices = {}
    for name in release.practices:
        counts = {}
        calibration_holds = matching_input_holds = 0
        for table in TABLES:
            rows = release.table(name, table)
            artifacts[f"{name}/{table}"] = json_digest(rows)
            counts[table] = len(rows)
            if table == "T4":
                for row in rows:
                    adaptation = row.get("relationship_params", {}).get(
                        "reviewed_adaptation", {}
                    )
                    if (
                        adaptation.get("numerical_calibration", {}).get("status")
                        == "held"
                    ):
                        calibration_holds += 1
                    if (
                        adaptation.get("dataset_binding", {}).get("status")
                        == "requires_matching_input"
                    ):
                        matching_input_holds += 1
        for leaf in settings[name]:
            artifacts[f"{name}/settings/{leaf}"] = sha256(
                release.setting(name, leaf)
            ).hexdigest()
        readiness = get_report(name, READINESS)
        artifacts[f"{name}/{READINESS}"] = json_digest(readiness)
        artifacts[f"{name}/{EFFECT_REPORT}"] = json_digest(
            get_report(name, EFFECT_REPORT)
        )
        practices[name] = {
            "rows": counts,
            "calibration_holds": calibration_holds,
            "matching_input_holds": matching_input_holds,
            "execution_ready": readiness["execution_ready"],
        }
    return {
        "release_id": release.release_id,
        "source_revision": provenance["source_revision"],
        "practices": practices,
        "artifacts": artifacts,
    }


def check_legacy(upstream, release):
    from nbs_runtime.contract import fingerprint_holds, load_package

    package = load_package(Path(upstream))
    name = package.contract["nbs"]
    report = release.report(name, READINESS)
    ready = {row["rule_id"]: row for row in report["rows"]}
    policies = {}
    for previous in package.run_contract["approved_policies"]:
        policy = package.policy(previous["policy_id"])
        if policy.policy_id not in report["approved_policy_ids"]:
            raise ValueError(
                f"Legacy policy missing from recipe readiness: {policy.policy_id}"
            )
        holds = fingerprint_holds(package, policy)
        if holds:
            raise ValueError(f"Legacy policy fingerprint check failed: {holds}")
        for criterion in policy.criteria:
            row = ready[criterion.rule_id]
            if (
                row["functions"].get(criterion.function_id) != criterion.fingerprint
                or row["readiness"]["effective_function_id"] != criterion.function_id
                or row["readiness"]["effective_function_fingerprint"]
                != criterion.fingerprint
            ):
                raise ValueError(
                    f"Legacy policy criterion differs in recipe release: {criterion.rule_id}"
                )
        policies[policy.policy_id] = len(policy.criteria)
    if not policies:
        raise ValueError("Legacy package has no policy to compare")
    return {
        "package_version": package.version,
        "source_ref": package.pin["ref"],
        "matched_criteria": policies,
    }


def runtime_probe():
    """Run in the isolated interpreter. Only the runtime distribution supplies a reader."""
    if not sys.flags.isolated or importlib.util.find_spec("nbs_ruralscan") is not None:
        raise ValueError(
            "Use an isolated runtime environment without nbs_ruralscan installed"
        )

    def offline(event, _args):
        if event.startswith("socket."):
            raise RuntimeError(
                f"Network unavailable during the offline handoff check: {event}"
            )

    sys.addaudithook(offline)
    from nbs_runtime.recipe_release import load_recipe_release

    request = json.load(sys.stdin)
    release = load_recipe_release(Path(request["store"]))
    if release.release_id != request["release_id"]:
        raise ValueError(
            f"Runtime default pin selects {release.release_id}, expected {request['release_id']}"
        )
    compared = summarize(
        release, request["settings"], release.report, release.provenance
    )
    if request["legacy_upstream"]:
        compared["legacy"] = check_legacy(request["legacy_upstream"], release)
    print(json.dumps(compared, allow_nan=False))


def main():
    from nbs_ruralscan.runtime.schema_loader import (
        BOOT_FILE,
        PROVENANCE_FILE,
        load_recipe_release,
        report_path,
    )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--store", required=True, type=Path, help="Local immutable recipe store"
    )
    parser.add_argument(
        "--release-id",
        required=True,
        help="Expected default pin of the installed runtime",
    )
    parser.add_argument(
        "--runtime-python",
        required=True,
        type=Path,
        help="Python executable in the independent runtime environment",
    )
    parser.add_argument(
        "--legacy-upstream",
        type=Path,
        help="Also compare the original runtime package at this upstream directory",
    )
    args = parser.parse_args()
    reference = load_recipe_release(args.store, args.release_id)
    boot = json.loads(reference.read_bytes(BOOT_FILE))
    settings = {
        name: [Path(member).name for member in definition["settings"]]
        for name, definition in boot["practices"].items()
    }
    expected = summarize(
        reference,
        settings,
        lambda n, r: json.loads(reference.read_bytes(report_path(n, r))),
        json.loads(reference.read_bytes(PROVENANCE_FILE)),
    )
    request = {
        "store": str(args.store.resolve()),
        "release_id": args.release_id,
        "settings": settings,
        "legacy_upstream": str(args.legacy_upstream.resolve())
        if args.legacy_upstream
        else None,
    }
    # Retain the venv executable's symlink: resolving it would select the base installation.
    with TemporaryDirectory(prefix="ruralscan-handoff-") as directory:
        child = subprocess.run(
            [
                str(args.runtime_python.absolute()),
                "-I",
                str(Path(__file__).resolve()),
                "--runtime-probe",
            ],
            cwd=directory,
            input=json.dumps(request),
            text=True,
            capture_output=True,
        )
    if child.returncode:
        raise ValueError(f"Runtime validation failed:\n{child.stderr.strip()}")
    actual = json.loads(child.stdout)
    legacy = actual.pop("legacy", None)
    verified = expected.pop("artifacts")
    consumed = actual.pop("artifacts")
    differences = [
        key
        for key in sorted(verified.keys() | consumed.keys())
        if verified.get(key) != consumed.get(key)
    ]
    if differences:
        raise ValueError("Reader outputs differ: " + ", ".join(differences))
    if expected != actual:
        raise ValueError(
            "Runtime release identity, practice inventory or counts differ from reference"
        )
    expected["compared_values"] = len(verified)
    expected["comparison_sha256"] = json_digest(verified)
    expected["total_rows"] = sum(
        sum(p["rows"].values()) for p in expected["practices"].values()
    )
    if legacy is not None:
        expected["legacy"] = legacy
    print(json.dumps(expected, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        if sys.argv[1:] == ["--runtime-probe"]:
            runtime_probe()
        else:
            main()
    except (ImportError, KeyError, OSError, TypeError, ValueError, RuntimeError) as exc:
        sys.exit(str(exc))
