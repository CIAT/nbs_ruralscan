"""Compile complete practice recipes against a stable CIAT snapshot and publish one local release."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections.abc import Sequence
from pathlib import Path
import tempfile

from nbs_ruralscan.recipe import (
    developer_contract,
    developer_corpus,
    t3t6_build,
    t4_build,
)
from nbs_ruralscan.recipe.release_store import PinnedRelease, publish_release
from nbs_ruralscan.runtime import schema_loader as layout
from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths, source_revision
from nbs_ruralscan.schema_tools.generate import _csv_to_rows
from nbs_ruralscan.schema_tools.review_inputs import ReviewInputs
from nbs_ruralscan.schema_tools.specialist_records import parse_json

FAMILIES = Path("schema/registers/FAM_family_registry.csv")
STRUCTURE = Path("schema/structure/columns.json")
T4_INDEX = Path("schema/recipe_inputs/t4/practices.csv")
IDENTITY = "T0_nbs_registry.csv"
POLICY = "T4_run_policy.csv"
PROSE = "T3T6_prose.json"
SETTINGS = "T4_settings.json"


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        + "\n"
    ).encode()


def _compiler_sources() -> dict[str, Path]:
    paths = developer_corpus.compiler_paths()
    source = Path(__file__).resolve().parents[2]
    for module in (
        "schema_tools/build_paths.py",
        "schema_tools/publication.py",
        "schema_tools/review_inputs.py",
        "schema_tools/specialist_records.py",
        "ingest/integrity.py",
    ):
        paths["src/nbs_ruralscan/" + module] = source / "nbs_ruralscan" / module
    return paths


def _practices(root: Path, selected: Sequence[str] | None) -> list[str]:
    with (root / FAMILIES).open(encoding="utf-8", newline="") as f:
        known = {row["nbs_id"] for row in csv.DictReader(f)}
    if selected is None:
        with (root / T4_INDEX).open(encoding="utf-8", newline="") as index:
            declared = {row["nbs_id"] for row in csv.DictReader(index)}
        directories = {
            child.name
            for child in (root / "schema/recipes").iterdir()
            if child.is_dir() and not child.name.startswith(".")
        }
        inventories = {
            "family registry": known,
            "settings index": declared,
            "recipe folders": directories,
        }
        all_names = known | declared | directories
        if any(names != all_names for names in inventories.values()):
            missing = [
                f"{label} missing {', '.join(sorted(all_names - names))}"
                for label, names in inventories.items()
                if names != all_names
            ]
            raise ValueError("Incomplete practice inventory: " + "; ".join(missing))
    names = sorted(known if selected is None else selected)
    if not names or len(names) != len(set(names)):
        raise ValueError("Select at least one practice and list each practice once")
    for name in names:
        t3t6_build.check_nbs_id(name)
        if name not in known:
            raise ValueError(f"Unknown practice in family registry: {name}")
    return names


def _sources(root: Path, name: str) -> set[Path]:
    recipe = root / "schema/recipes" / name
    inputs = developer_contract.contract_input_paths(root, name)
    inputs.update(
        t4_build.T4BuildInputs.from_root(root, name, require_authored=True).paths()
    )
    inputs.update(t3t6_build.T3T6BuildInputs.from_root(root, name).paths())
    inputs.update(
        recipe / item for item in (IDENTITY, POLICY, "T3T6_synthesis_report.json")
    )
    inputs.update((recipe / item).with_suffix(".json") for item in (IDENTITY, POLICY))
    for stem in layout.TABLE_STEMS.values():
        inputs.update(recipe / (stem + ext) for ext in (".csv", ".json"))
    return inputs


def _require_synced_csv(source: Path) -> list[dict]:
    """Verify the checkout’s typed companion matches its CSV, including types and order."""
    rows = _csv_to_rows(source)
    typed = source.with_suffix(".json")
    if _json_bytes(rows) != _json_bytes(parse_json(typed.read_text(encoding="utf-8"))):
        raise ValueError(f"Stale generated {typed.name}; rebuild it from {source.name}")
    return rows


def _compile(root: Path, work: Path, name: str) -> tuple[dict[str, bytes], list[str]]:
    recipe = root / "schema/recipes" / name
    if not (recipe / IDENTITY).is_file():
        raise ValueError(f"Missing practice definition {IDENTITY}")
    t4 = t4_build.T4BuildInputs.from_root(root, name, require_authored=True)
    _require_synced_csv(recipe / IDENTITY)
    availability = t4.release_settings(name)
    for flag, filename in (("run_policy", POLICY), ("effect_prose", PROSE)):
        if (recipe / filename).is_file() != availability[flag]:
            raise ValueError(f"Recipe settings declaration disagrees with {filename}")
    if availability["run_policy"]:
        if not _require_synced_csv(recipe / POLICY):
            raise ValueError(f"Declared run policy is empty: {POLICY}")
    elif (recipe / POLICY).with_suffix(".json").exists():
        raise ValueError(f"Generated run policy has no authored {POLICY}")
    settings = t4.authored_paths()[1:]
    files = {
        layout.setting_path(name, SETTINGS): _json_bytes(
            {"nbs_id": name, "files": sorted(p.name for p in settings), **availability}
        )
    }
    for path in (recipe / IDENTITY, *settings, recipe / POLICY, recipe / PROSE):
        if path.exists():
            files[layout.setting_path(name, path.name)] = path.read_bytes()
    setting_names = sorted(files)

    # Includes the complete T4 rebuild, audited-baseline comparison, per-rule
    # readiness and approved run-policy fingerprint checks. Never filter evidence.
    built = developer_contract.build_contract(root, nbs=name)
    contract = built["contract"]
    policies = contract["run_contract"]["approved_policies"]
    stale_policies = [
        p["policy_id"] for p in policies if p["status"] == "blocked_function_changed"
    ]
    if stale_policies:
        raise ValueError(
            f"Approved T4 function fingerprint changed: {', '.join(stale_policies)}"
        )
    files[layout.report_path(name, "T4_readiness.json")] = _json_bytes(
        {
            "nbs_id": name,
            "contract_version": contract["version"],
            "execution_ready": contract["run_contract"]["execution_ready"],
            "implementation_readiness": contract["summary"]["implementation_readiness"],
            "approved_policy_ids": sorted(p["policy_id"] for p in policies),
            "rows": [
                {
                    "rule_id": row["rule_id"],
                    "role": row["role"],
                    "system": row["system"],
                    "variable_group": row["variable_group"],
                    "readiness": row["readiness"],
                    "functions": {
                        option["function_id"]: option["fingerprint"]
                        for option in row["function_options"]
                    },
                }
                for row in contract["rows"]
            ],
        }
    )

    effects = t3t6_build.T3T6BuildInputs.from_root(root, name)
    result = t3t6_build.synthesise(
        name, t3t6_build.load_inputs(name, [], inputs=effects)
    )
    t3t6_build.write_recipe(
        name, result, inputs=effects, output_dir=work, dry_run=False
    )
    for table, stem in layout.TABLE_STEMS.items():
        audited = recipe / (stem + ".csv")
        expected = _require_synced_csv(audited)
        compiled = audited if table == "T4" else work / audited.name
        if table != "T4" and _json_bytes(_csv_to_rows(compiled)) != _json_bytes(
            expected
        ):
            raise ValueError(f"Full-corpus rebuild differs from audited {audited.name}")
        files[layout.table_path(name, table, ".csv")] = compiled.read_bytes()
        files[layout.table_path(name, table, ".json")] = audited.with_suffix(
            ".json"
        ).read_bytes()
    report = "T3T6_synthesis_report.json"
    generated = parse_json((work / report).read_text(encoding="utf-8"))
    if _json_bytes(generated) != _json_bytes(
        parse_json((recipe / report).read_text(encoding="utf-8"))
    ):
        raise ValueError(f"Full-corpus rebuild differs from audited {report}")
    files[layout.report_path(name, report)] = _json_bytes(generated)
    return files, setting_names


def _prepare_and_publish(
    root: Path, selected: Sequence[str] | None, store: Path | None
) -> PinnedRelease | None:
    root = Path(root).resolve()
    if store is not None:
        # Protect the data and compiler checkouts from a misplaced release store.
        SchemaBuildPaths(root / "schema", Path(store)).preflight([])
    compiler = _compiler_sources()
    code_guard = ReviewInputs(compiler.values())
    guard = ReviewInputs([root / FAMILIES, root / STRUCTURE, root / T4_INDEX])
    revision = source_revision(root)
    names = _practices(root, selected)
    paths = {root / FAMILIES, root / STRUCTURE, root / T4_INDEX}
    for name in names:
        paths.update(_sources(root, name))
    guard.include(paths)

    def verify() -> None:
        guard.verify()
        code_guard.verify()
        if compiler != _compiler_sources():
            raise ValueError("Compiler file set changed during recipe build")
        if _practices(root, selected) != names:
            raise ValueError("Practice inventory changed during recipe build")
        for name in names:
            # Check newly introduced optional paths, including undeclared T4 files.
            t4_build.T4BuildInputs.from_root(root, name, require_authored=True)
        if source_revision(root) != revision:
            raise ValueError("Source checkout revision changed during recipe build")

    with tempfile.TemporaryDirectory(prefix="ruralscan-recipe-build-") as directory:
        private = Path(directory).resolve()
        snapshot = private / "snapshot"
        hashes = {}
        for path in sorted(paths):
            state = guard.states[path]
            if state is None:
                continue
            relative = path.relative_to(root)
            data = path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            if digest != state[0]:
                raise ValueError(f"Recipe input changed while copying: {relative}")
            copy = snapshot / relative
            copy.parent.mkdir(parents=True, exist_ok=True)
            copy.write_bytes(data)
            hashes[relative.as_posix()] = digest
        verify()
        _require_synced_csv(snapshot / "schema/registers/EV_evidence_register.csv")
        members: dict[str, bytes] = {}
        inventory = {}
        holds = []
        for name in names:
            try:
                files, settings = _compile(snapshot, private / "compiled" / name, name)
            except (ValueError, FileNotFoundError) as exc:
                holds.append(f"{name}: {exc}")
                continue
            members.update(files)
            inventory[name] = {"settings": settings}
        if holds:
            raise ValueError(
                "Cannot publish requested recipe set:\n" + "\n".join(holds)
            )
        members[layout.BOOT_FILE] = _json_bytes(
            {"format_version": 1, "kind": "reconciled_recipe", "practices": inventory}
        )
        members[layout.PROVENANCE_FILE] = _json_bytes(
            {
                "source_revision": revision,
                "schema_version": json.loads((snapshot / STRUCTURE).read_bytes())[
                    "manifest_version"
                ],
                "compiler_sha256": {
                    key: hashlib.sha256(path.read_bytes()).hexdigest()
                    for key, path in compiler.items()
                },
                "inputs_sha256": hashes,
            }
        )
        layout.validate_recipe_members(members)
        verify()
        if store is None:
            return None
        return publish_release(Path(store), members, verify_inputs=verify)


def publish_recipes(
    root: Path, store: Path, *, practices: Sequence[str] | None = None
) -> PinnedRelease:
    """Publish every requested practice together after full-corpus reconciliation."""
    release = _prepare_and_publish(root, practices, store)
    assert release is not None
    return release


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    for name in ("check", "publish"):
        sub = commands.add_parser(name)
        sub.add_argument(
            "--source-root",
            "--root",
            type=Path,
            required=True,
            help="Selected CIAT data checkout",
        )
        sub.add_argument(
            "--nbs",
            action="append",
            help="Practice to include; repeat for more. Default: every registered practice.",
        )
        if name == "publish":
            sub.add_argument(
                "--store",
                type=Path,
                required=True,
                help="Local release directory outside the data and compiler checkouts",
            )
    inspect = commands.add_parser("inspect")
    inspect.add_argument("--store", type=Path, required=True)
    inspect.add_argument("--release-id", help="Open an earlier release by its ID")
    args = parser.parse_args(argv)
    try:
        if args.action == "inspect":
            bundle = layout.load_recipe_release(args.store, args.release_id)
            print(bundle.release_id)
            for practice in bundle.practices:
                print(
                    practice,
                    " ".join(
                        f"{t}={len(bundle.table(practice, t))}"
                        for t in layout.TABLE_STEMS
                    ),
                )
        elif args.action == "check":
            _prepare_and_publish(args.source_root, args.nbs, None)
            print("All requested recipes reconciled.")
        else:
            print(
                publish_recipes(
                    args.source_root, args.store, practices=args.nbs
                ).release_id
            )
    except (ValueError, OSError) as exc:
        parser.exit(1, f"{exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
