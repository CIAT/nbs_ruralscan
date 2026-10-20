#!/usr/bin/env python3
"""Package unchanged reviewed T4 tables, provenance and categorical runtime for Diego."""

import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "handoff/agroforestry-t4/agroforestry-t4-diego.zip"


def main():
    paths = [
        "handoff/agroforestry-t4/README.md",
        "schema/spec.md",
        "schema/structure/columns.json",
    ]
    tables = [
        "schema/recipes/agroforestry/T4_suitability_mappings",
        "schema/T1_data_registry",
        "schema/T7_geographic_context",
    ]
    tables += [
        "schema/registers/" + name
        for name in [
            "BIND_dataset_binding",
            "VONT_variable_ontology",
            "FAM_family_registry",
            "EV_evidence_register",
            "SRC_source_register",
        ]
    ]
    paths += [t + ext for t in tables for ext in [".csv", ".json"]]
    paths += ["src/nbs_ruralscan/__init__.py", "src/nbs_ruralscan/runtime/__init__.py"]
    paths += [
        "src/nbs_ruralscan/runtime/" + name + ".py"
        for name in ["categorical", "binding", "host_inputs"]
    ]
    paths += [
        "tests/" + name
        for name in ["test_categorical_runtime.py", "test_host_inputs.py"]
    ]
    base = "pipeline/t4_audit/agroforestry/final_audit/"
    paths += [
        base + name
        for name in [
            "README.md",
            "record_reconciliation.csv",
            "categorical_current_t4.csv",
            "categorical_source_classes.csv",
            "executable_categories/dataset_bindings.csv",
            "executable_categories/family_execution.csv",
        ]
    ]
    paths += [
        str(p.relative_to(ROOT))
        for p in (ROOT / "docs/review/exports").glob("review_agroforestry-t4-*.csv")
    ]
    paths = sorted(set(paths))
    manifest = {
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "scope": "Reviewed T4 handoff; no raster data or pilot test results",
        "files": {},
    }
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in paths:
            data = (ROOT / name).read_bytes()
            manifest["files"][name] = hashlib.sha256(data).hexdigest()
            archive.writestr(name, data)
        archive.writestr("MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
    with zipfile.ZipFile(OUT) as archive:
        assert archive.testzip() is None
        for name, digest in manifest["files"].items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest
    print(f"Verified {len(paths)} files: {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
