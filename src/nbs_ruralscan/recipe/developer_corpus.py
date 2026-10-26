"""Rebuild developer inputs from reviewed evidence without changing source tables.

The live recipe is an audited baseline and the source of authored design gates.
A mismatch is an error, not permission to publish new analytical rules silently.
"""

from __future__ import annotations

import csv
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile


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
    inputs = [
        "scripts/synthesise-recipe.py",
        "schema/registers/EV_evidence_register.csv",
        "schema/registers/SRC_source_register.csv",
        "schema/registers/VONT_variable_ontology.csv",
        "schema/lookups/crop_scope_policy.csv",
        "schema/lookups/t4_numeric_compilation_policy.csv",
        recipe,
    ]
    inputs += [
        str(p.relative_to(root))
        for p in sorted((root / "src/nbs_ruralscan/recipe").glob("*.py"))
    ]
    inputs += ["src/nbs_ruralscan/schema_tools/generate.py"]
    before = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in inputs
    }
    spec = importlib.util.spec_from_file_location(
        "_developer_t4_synthesis", root / "scripts/synthesise-recipe.py"
    )
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load the T4 synthesis entrypoint")
    synthesis = importlib.util.module_from_spec(spec)
    # Execute source directly so importlib does not create a __pycache__ beside
    # the caller's synthesis script. Analytical inputs remain strictly read-only.
    exec(
        compile(
            (root / "scripts/synthesise-recipe.py").read_bytes(),
            str(spec.origin),
            "exec",
        ),
        synthesis.__dict__,
    )
    setattr(synthesis, "ROOT", root)
    setattr(synthesis, "REG", root / "schema/registers")
    # The typed CSV reader omits empty fields, but EvidenceUnit requires a family
    # argument. Preserve an explicitly unassigned family for disposition coverage;
    # synthesise() already excludes empty families from compiled configurations.
    typed_reader = synthesis._csv_to_rows

    def typed_rows(path):
        rows = typed_reader(path)
        for row in rows:
            row.setdefault("suitability_family_id", "")
        return rows

    setattr(synthesis, "_csv_to_rows", typed_rows)
    evidence = [
        r
        for r in _read(synthesis.REG / "EV_evidence_register.csv")
        if r["nbs_id"] == nbs
    ]
    sources = _read(synthesis.REG / "SRC_source_register.csv")
    live = _read(root / recipe)
    results = synthesis.synthesise(nbs, approved_only=True)
    with tempfile.TemporaryDirectory(prefix="t4-developer-corpus-") as directory:
        synthesis.write_recipe(
            nbs,
            results,
            _read(synthesis.REG / "VONT_variable_ontology.csv"),
            output_dir=Path(directory),
        )
        rows = _read(Path(directory) / "T4_suitability_mappings.csv")
    after = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in inputs
    }
    if before != after:
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
        "review_mode": "approved_only",
        "audited_recipe_matches": True,
        "input_sha256": before,
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
