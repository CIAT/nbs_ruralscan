"""Verify local pinned artifacts and reproduce the reviewed ProGreen classifier probes.

Run from repository root with the project Python environment. This executes only
one inspected numerical function from the pinned artifact, with synthetic arrays;
it does not import or run the upstream geospatial applications.
"""

import ast
import hashlib
import json
import re
from pathlib import Path

import numpy as np

AUDIT = Path(__file__).parent
files = json.loads((AUDIT / "artifact_checks.json").read_text())
claims = json.loads((AUDIT / "claims.json").read_text())
artifacts = {f["source_id"]: f for f in files}
for file in files:
    content = Path(file["cached"]).read_bytes()
    assert hashlib.sha1(content).hexdigest() == file["sha1"]
    meta = json.loads(Path(file["cached"]).with_suffix(".meta.json").read_text())
    assert all(meta[key] == file[key] for key in ("repo", "commit", "path", "sha1"))
for claim in claims:
    artifact = artifacts[claim["source_id"]]
    start, end = map(int, re.search(r":L(\d+)-L(\d+)$", claim["locator"]).groups())
    lines = Path(artifact["cached"]).read_text().splitlines()
    assert claim["quote"] == "\n".join(lines[start - 1 : end])
    assert claim["commit"] == artifact["commit"]

source = Path(artifacts["tool_forest_progreen_suitability"]["cached"]).read_text()
function = next(
    node
    for node in ast.parse(source).body
    if isinstance(node, ast.FunctionDef) and node.name == "re_classify"
)
namespace = {"np": np}
exec(
    compile(
        ast.Module(body=[function], type_ignores=[]), "<pinned classifier>", "exec"
    ),
    namespace,
)
classify = namespace["re_classify"]
expected = json.loads((AUDIT / "behavior_probes.json").read_text())
assert (
    classify(
        np.array([224.0, 225.0, 314.0, 315.0, 359.0, 360.0]),
        {
            "min_val": None,
            "max_val": None,
            "ranges": [225, 315, 360],
            "range_definition": [100, 0, 100],
            "classifier": "ranges",
        },
        None,
    ).tolist()
    == expected["aspect_upper_edge"]
)
assert (
    classify(
        np.array([-10.0, 0.0, 60.0]),
        {"min_val": 0, "max_val": 60, "classifier": "linear-descending"},
        None,
    ).tolist()
    == expected["zero_min_ignored"]
)
assert (
    classify(
        np.array([62.0, 63.0, 100.0, 125.0, 156.0, 187.0, 249.0, 250.0, 251.0]),
        {
            "min_val": None,
            "max_val": 250,
            "ranges": [63, 100, 125, 156, 187, 250],
            "range_definition": [1, 5, 10, 50, 75, 100],
            "classifier": "ranges",
        },
        None,
    ).tolist()
    == expected["degradation_upper_edge"]
)
for case in expected["tracker_counterexamples"]:
    slope, rain, moisture = case["slope"], case["precipitation"], case["moisture"]
    assert (slope < 15 and rain >= 200 and moisture >= 0.2) == case["raster_expression"]
    assert (slope <= 15 and (rain >= 200 or moisture >= 0.2)) == case[
        "scalar_expression"
    ]
print(
    f"Verified {len(files)} artifact hashes, {len(claims)} exact quote locators and numerical probes."
)
