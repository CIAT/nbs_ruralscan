"""Verify pinned artifacts/quotes and reproduce bounded code-behavior probes.

Run from repository root in the project environment. Only inspected numerical
functions execute. Erosion cell lookup is stubbed to two synthetic cells. R and
MATLAB checks evaluate translated expressions, not those complete applications.
"""

import ast
import json
from pathlib import Path
import numpy as np
import pandas as pd
from numpy.random import default_rng
import hashlib
import re

AUDIT = Path(__file__).parent
files = json.loads((AUDIT / "artifact_checks.json").read_text())
lookup = {f["source_id"]: f for f in files}
for f in files:
    artifact = Path(f["cached"])
    assert hashlib.sha1(artifact.read_bytes()).hexdigest() == f["sha1"]
    meta = json.loads(artifact.with_suffix(".meta.json").read_text())
    assert all(meta[k] == f[k] for k in ["repo", "commit", "path", "sha1"])
for c in json.loads((AUDIT / "claims.json").read_text()):
    start, end = map(int, re.search(r":L(\d+)-L(\d+)$", c["locator"]).groups())
    f = lookup[c["source_id"]]
    assert c["quote"] == "\n".join(
        Path(f["cached"]).read_text().splitlines()[start - 1 : end]
    )
    assert c["commit"] == f["commit"]
p = Path(".cache/corpus/smbeselly_d3d_mangro_seeds_650bb67c04e2.txt")
tree = ast.parse(p.read_text())
ns = {"np": np, "pd": pd, "default_rng": default_rng}
for name in ["reduce_seeds_vect", "elim_seeds_ced"]:
    f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[f], type_ignores=[]), "<pinned helper>", "exec"), ns)
results = {"environment": {"numpy": np.__version__, "pandas": pd.__version__}}
results["seed_reduction"] = [
    {
        "source_score": v,
        "input_count": 30,
        "retained_count": len(
            ns["reduce_seeds_vect"](v, pd.DataFrame({"x": range(30)}))
        ),
    }
    for v in [0.1, 0.3, 0.31, 0.5, 0.51, 0.7, 0.71, 1.0]
]
# Stub only cell lookup; execute original erosion function unchanged.
ns["subsetting_cellCdveg"] = lambda grid, cells, row, data: data[
    data.cell == row
].copy()
data = pd.DataFrame(
    {
        "cell": [0] * 4 + [1] * 4,
        "Species": ["Avicennia_marina"] * 4 + ["Rhizopora_apiculata"] * 4,
    }
)
for label, levels in [
    ("one_eroding_cell", [[0, -0.06], [0, 0]]),
    ("both_eroding_cells", [[0, -0.06], [0, -0.06]]),
    ("neither_eroding", [[0, 0], [0, 0]]),
]:
    out = ns["elim_seeds_ced"](np.array(levels), None, [0, 1], [1, 1], data.copy())
    results[label] = {
        "retained_indices": out.index.tolist(),
        "retained_by_cell": {
            str(k): int(v) for k, v in out.groupby("cell").size().items()
        },
        "retained_species": out.Species.value_counts().to_dict(),
    }
p = Path(".cache/corpus/smbeselly_d3d_meso_mangro_a013df599af5.txt")
f = next(
    n
    for n in ast.parse(p.read_text()).body
    if isinstance(n, ast.FunctionDef) and n.name == "calc_woo_avc_rzp_hs"
)
exec(compile(ast.Module(body=[f], type_ignores=[]), "<pinned WoO helper>", "exec"), ns)


class Model:
    def __init__(self, bed):
        self.bed = np.array(bed)

    def get_var(self, name):
        assert name == "bl"
        return self.bed


results["woo_probes"] = {}
for label, depth, bed in [
    ("dry_5days", [[0] * 5], [0]),
    ("dry_10days", [[0] * 10], [0]),
    ("one_cm_5days", [[0.01] * 5], [0]),
    ("above_one_cm", [[0.011] * 5], [0]),
    ("below_zero_bed", [[0] * 5], [-0.01]),
]:
    results["woo_probes"][label] = ns["calc_woo_avc_rzp_hs"](
        np.array(depth), Model(bed)
    ).tolist()
results["mini_buoy_boundaries"] = [
    {
        "minutes_per_day": x,
        "suitability_warning": "not suitable"
        if x < 100 or x > 800
        else "generally suitable",
    }
    for x in [99, 100, 800, 801]
]
results["mvm_normalization"] = {
    "flooded_samples": 20,
    "total_samples": 100,
    "scenario_max_flooded_samples": [40, 100],
    "relative_values": [20 / 40, 20 / 100],
    "colonization_at_tau_0_1": [False, True],
    "note": "Same absolute inundation fraction0.2; code P<0.5 changes with spatial maximum. Expression-level probe, not MATLAB execution.",
}
expected = json.loads((AUDIT / "behavior_probes.json").read_text())
assert {k: v for k, v in results.items() if k != "environment"} == {
    k: v for k, v in expected.items() if k != "environment"
}
print("Pinned function probes reproduced; runtime environment:", results["environment"])
