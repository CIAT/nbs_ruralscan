"""Rebuild developer inputs from reviewed evidence without changing source tables.

The live recipe is an audited baseline and the source of authored design gates.
A mismatch is an error, not permission to publish new analytical rules silently.
"""

from __future__ import annotations

import csv
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import tempfile

from . import t4_build


def compiler_paths() -> dict[str, Path]:
    """Project compiler sources from the executing installation, not the data copy.

    This is a source-tree fingerprint, not an environment/dependency lock or a
    claim that every listed module was called. Keep those identities separate.
    """
    package = Path(__file__).resolve().parents[1]
    paths = {
        "src/nbs_ruralscan/" + path.relative_to(package).as_posix(): path
        for folder in ("recipe", "runtime")
        for path in sorted((package / folder).glob("*.py"))
    }
    paths["src/nbs_ruralscan/schema_tools/generate.py"] = (
        package / "schema_tools/generate.py"
    )
    return paths


def verify_compiler_snapshot(root: Path) -> None:
    """Refuse a package whose copied-code provenance differs from its compiler."""
    mismatches = [
        name
        for name, path in compiler_paths().items()
        if not (root / name).is_file()
        or (root / name).read_bytes() != path.read_bytes()
    ]
    if mismatches:
        raise ValueError(
            "Compiler snapshot differs from executing installation: "
            + ", ".join(mismatches)
            + ". Use a matching compiler checkout before publishing a package."
        )


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _semantic(row: dict[str, str]) -> dict:
    result = dict(row)
    for key in ("relationship_params", "evidence_ids", "context_overrides"):
        result[key] = json.loads(row.get(key) or "null")
    return result


def _index(rows):
    indexed = {r["mapping_id"]: _semantic(r) for r in rows}
    if len(indexed) != len(rows):
        raise ValueError("Duplicate T4 mapping_id; reconcile the live recipe first")
    return indexed


def rebuild(root: Path, nbs: str) -> dict:
    """Compile approved corpus, check audited parity and return complete dispositions.

    All generated outputs go into a temporary directory. Country selection belongs
    to the downstream compiler; this function never trims source evidence.
    """
    root = Path(root).resolve()
    if not nbs or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_" for c in nbs):
        raise ValueError("nbs must be a canonical lowercase identifier")
    recipe = f"schema/recipes/{nbs}/T4_suitability_mappings.csv"
    build_inputs = t4_build.T4BuildInputs.from_root(root, nbs)
    inputs = [path.relative_to(root).as_posix() for path in build_inputs.paths()]
    before = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in inputs
    }
    code_paths = compiler_paths()
    compiler_before = {
        name: hashlib.sha256(path.read_bytes()).hexdigest()
        for name, path in code_paths.items()
    }
    evidence = [r for r in _read(build_inputs.evidence) if r["nbs_id"] == nbs]
    sources = _read(build_inputs.sources)
    live = _read(root / recipe)
    results = t4_build.synthesise(nbs, inputs=build_inputs, approved_only=True)
    with tempfile.TemporaryDirectory(prefix="t4-developer-corpus-") as directory:
        t4_build.write_recipe(
            nbs,
            results,
            _read(build_inputs.ontology),
            inputs=build_inputs,
            output_dir=Path(directory),
        )
        rows = _read(Path(directory) / "T4_suitability_mappings.csv")
    after = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in inputs
    }
    compiler_after = {
        name: hashlib.sha256(path.read_bytes()).hexdigest()
        for name, path in compiler_paths().items()
    }
    if before != after or compiler_before != compiler_after:
        raise RuntimeError(
            "T4 inputs changed during rebuild; rerun against a stable checkout"
        )
    expected, rebuilt = _index(live), _index(rows)
    mismatches = sorted(
        k for k in expected.keys() | rebuilt.keys() if expected.get(k) != rebuilt.get(k)
    )
    if mismatches:
        raise ValueError(
            "Reviewed corpus does not reproduce the audited live T4 recipe: "
            + ", ".join(mismatches)
            + f". Run scripts/synthesise-recipe.py {nbs} --output-dir <trial-directory>, "
            "review the changes, regenerate the audited recipe and its JSON, then rebuild the developer package."
        )
    dispositions = {}
    for result in results.values():
        dispositions.update(result.dispositions)
    accounted = []
    for unit in evidence:
        if unit["use_role"] not in {"structural_suitability", "operational_risk"}:
            continue
        decision = dispositions.get(unit["evidence_id"])
        accounted.append(
            {
                "evidence_id": unit["evidence_id"],
                "source_id": unit["source_id"],
                "variable": unit["variable"],
                "suitability_family_id": unit["suitability_family_id"],
                "use_role": unit["use_role"],
                "reviewer_ok": unit["reviewer_ok"],
                "review_state": unit["review_state"],
                "disposition": decision["status"]
                if decision
                else "no_suitability_family",
                "compiled_mapping_ids": [
                    r["mapping_id"]
                    for r in rows
                    if unit["evidence_id"] in json.loads(r["evidence_ids"] or "[]")
                ],
            }
        )
    report = {
        "review_mode": "approved_with_authorized_source_completions"
        if any(d.get("admission_basis") for d in dispositions.values())
        else "approved_only",
        "audited_recipe_matches": True,
        "input_sha256": before,
        "compiler_source_sha256": compiler_before,
        "families": {family: asdict(result) for family, result in results.items()},
        "evidence_dispositions": accounted,
        "coverage": {
            "relevant_records": len(accounted),
            "accounted_records": len(accounted),
        },
    }
    return {
        "rows": rows,
        "evidence": evidence,
        "sources": sources,
        "inputs": inputs,
        "synthesis_report": report,
    }
