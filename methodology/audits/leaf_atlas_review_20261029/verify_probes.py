"""Isolated probes of pinned LEAF code; never import or run Delft3D setup."""

import ast
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / ".cache/corpus/dunlopt_leaf_main_v_2_1_14bd98b4249f.txt"
assert (
    hashlib.sha1(SOURCE.read_bytes()).hexdigest()
    == "434fcd3236d82d251b7da29a9d13ba8a722c1e6d"
)
tree = ast.parse(SOURCE.read_text())


def run(node, env):
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE), "exec"), env)


def conditional(name):
    return next(
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.If)
        and isinstance(n.test, ast.Compare)
        and isinstance(n.test.left, ast.Name)
        and n.test.left.id == name
    )


def main():
    out = {}
    env = {
        "np": np,
        "math": math,
        "b": 0,
        "j": 0,
        "erocrit": "balke2015",
        "vegtrkht": np.array([[0.1]]),
    }
    run(conditional("erocrit"), env)
    cm = 3.5058 * math.log(10) - 5.0584
    assert math.isclose(env["ecrit"] / (cm / 100), 10000)
    out["erosion_conversion"] = {
        "height_m": 0.1,
        "implemented_m": env["ecrit"],
        "cm_converted_to_m": cm / 100,
        "ratio": 10000,
    }
    env["vegtrkht"][0, 0] = 0.001
    previous = env["ecrit"]
    run(conditional("erocrit"), env)
    assert env["ecrit"] == previous
    out["erosion_stale_local"] = True
    env.update(taucrit="balke2015", vegtrkrt=np.array([[0.1]]))
    run(conditional("taucrit"), env)
    previous = env["taudisl"]
    env["vegtrkrt"][0, 0] = 0
    run(conditional("taucrit"), env)
    assert env["taudisl"] == previous
    out["shear_stale_local"] = True

    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    env = {"np": np, "datetime": datetime, "seedwinrep": "Y"}
    for name in [
        "date_within_range",
        "neighbourveg",
        "calculate_percentile",
        "calculate_min_water_levels",
    ]:
        run(funcs[name], env)
    env.update(
        x_coord=np.array([0.0, 1.0]),
        y_coord=np.array([0.0, 0.0]),
        vegtrkadult=np.array([1, 0]),
    )
    snapshot = next(
        n
        for n in tree.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "vegexist" for t in n.targets)
    )
    run(snapshot, env)
    before = env["neighbourveg"](1, 2)
    env["vegtrkadult"][0] = 0
    after = env["neighbourveg"](1, 2)
    assert before and after
    out["neighbour_snapshot"] = {
        "before_adult_death": before,
        "after_adult_death": after,
        "current_adult_flags": env["vegtrkadult"].tolist(),
    }
    result = env["calculate_percentile"](
        np.array([[10.0, 10.0], [20.0, 20.0]]), 50, np.zeros(2)
    )
    assert np.allclose(result, [15, 11.5])
    out["unused_percentile_helper"] = {
        "actual": result.tolist(),
        "independent_medians": [15, 15],
    }
    mins = env["calculate_min_water_levels"](np.array([[0, 2], [43200, 4]]), 43200, 3)
    assert mins[0, 1] == 2 and mins[1, 1] == 4 and np.isnan(mins[2, 1])
    out["water_level_intervals"] = [
        "start inclusive/end exclusive",
        "missing interval gives NaN",
    ]
    assert env["date_within_range"](
        datetime(2025, 1, 10), datetime(2017, 12, 15), datetime(2018, 1, 15)
    )
    out["year_wrap_window"] = "passes January in December-to-January recurring window"

    # Execute the original WoO1 conditional with a six-hour requirement and a
    # twelve-hour step, forcing chance=1 solely to isolate its eligibility gate.
    setup = {
        "np": np,
        "b": 0,
        "j": 0,
        "i": 0,
        "vegtrk": np.zeros((1, 1)),
        "maxwd": np.array([1.0]),
        "epshu": 0.01,
        "c_woo1": np.zeros((1, 1)),
        "inundfreestep": int(6 * 3600 / 43200),
        "estchance": 1,
        "vegtrktime": np.zeros((1, 1)),
        "vegtrkbed": np.zeros((1, 1)),
        "blh": np.array([0.0]),
        "date_within_range": env["date_within_range"],
        "currenttime": datetime(2025, 2, 1),
        "seedwinstart": datetime(2017, 1, 15),
        "seedwinend": datetime(2017, 3, 15),
    }
    woo = next(n for n in ast.walk(tree) if isinstance(n, ast.If) and n.lineno == 736)
    run(woo, setup)
    assert setup["vegtrk"][0, 0] == 1
    out["substep_window"] = {
        "required_hours": 6,
        "step_hours": 12,
        "floored_steps": 0,
        "wet_cell_anchored": True,
        "chance_override_for_probe": 1,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
