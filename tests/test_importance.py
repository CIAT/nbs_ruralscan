import copy
import pytest
from nbs_ruralscan.recipe.importance import compare_importance


def leaf(name, w, scope="general"):
    return dict(id=name, variable=name, scope=scope, weight=w)


def group(name, w, children):
    return dict(id=name, weight=w, children_complete=True, children=children)


def model(children):
    return dict(
        additive=True, weight_scale="nonnegative_ratio", tree=group("root", 1, children)
    )


def variable(result, name):
    return next(r for r in result["variables"] if r["variable"] == name)


def test_flat_four():
    r = compare_importance(
        model([leaf("rain", 40), leaf("ph", 30), leaf("slope", 20), leaf("temp", 10)])
    )
    assert variable(r, "ph")["hierarchy_adjusted_ratio"] == pytest.approx(1.2)
    assert variable(r, "ph")["flat_variable_ratio"] == pytest.approx(1.2)


def test_flat_fifty():
    r = compare_importance(
        model([leaf("ph", 5)] + [leaf(str(i), 95 / 49) for i in range(49)])
    )
    assert variable(r, "ph")["hierarchy_adjusted_ratio"] == pytest.approx(2.5)


def nested():
    return model(
        [
            group("climate", 60, [leaf("rain", 50), leaf("temp", 50)]),
            group(
                "soil",
                40,
                [
                    leaf("ph", 50),
                    leaf("depth", 20),
                    leaf("texture", 20),
                    leaf("drainage", 10),
                ],
            ),
        ]
    )


def test_hierarchy_and_scale_invariance():
    m = nested()
    r = compare_importance(m)
    p = variable(r, "ph")
    assert p["whole_model_share"] == pytest.approx(0.2)
    assert p["within_group_ratios"] == pytest.approx([2])
    assert p["flat_variable_ratio"] == pytest.approx(1.2)
    assert p["hierarchy_adjusted_ratio"] == pytest.approx(1.6)
    for n in m["tree"]["children"][1]["children"]:
        n["weight"] *= 7
    assert variable(compare_importance(m), "ph") == p


@pytest.mark.parametrize(
    "mutation",
    [
        "incomplete",
        "missing",
        "negative",
        "nan",
        "zero",
        "ordinal",
        "nonadditive",
        "duplicate",
    ],
)
def test_invalid_models_hold(mutation):
    m = model([leaf("a", 1), leaf("b", 2)])
    if mutation == "incomplete":
        m["tree"]["children_complete"] = False
    elif mutation == "ordinal":
        m["weight_scale"] = "ranks"
    elif mutation == "nonadditive":
        m["additive"] = False
    elif mutation == "duplicate":
        m["tree"]["children"][1]["id"] = "a"
    elif mutation == "zero":
        for n in m["tree"]["children"]:
            n["weight"] = 0
    else:
        m["tree"]["children"][0]["weight"] = {
            "missing": None,
            "negative": -1,
            "nan": float("nan"),
        }[mutation]
    assert compare_importance(m)["status"] == "held"


def test_additive_branches_aggregate_but_scopes_stay_distinct():
    a = leaf("ph_a", 50)
    a["variable"] = "ph"
    b = leaf("ph_b", 50)
    b["variable"] = "ph"
    m = model(
        [
            group("nutrients", 50, [a, leaf("n", 50)]),
            group("rooting", 50, [b, leaf("density", 50)]),
        ]
    )
    p = variable(compare_importance(m), "ph")
    assert p["branch_count"] == 2
    assert p["whole_model_share"] == pytest.approx(0.5)
    assert p["hierarchy_adjusted_ratio"] == pytest.approx(1)
    assert p["flat_variable_ratio"] == pytest.approx(1.5)
    other = copy.deepcopy(m)
    other["tree"]["children"][1]["children"][0]["scope"] = "species"
    assert (
        len(
            [r for r in compare_importance(other)["variables"] if r["variable"] == "ph"]
        )
        == 2
    )


def test_real_source_inventories():
    from pathlib import Path
    from nbs_ruralscan.recipe.importance import load_weight_models

    path = (
        Path(__file__).resolve().parents[1]
        / "pipeline/t4_audit/agroforestry/importance_2026-10-21/source_weight_trees.csv"
    )
    models = load_weight_models(path)
    results = {m["model_id"]: compare_importance(m) for m in models}
    assert len(models) == 5
    assert len({m["source_id"] for m in models}) == 3
    for result in results.values():
        assert result["status"] == "calculated"
        assert sum(
            v["whole_model_share"] for v in result["variables"]
        ) == pytest.approx(1)
        assert sum(
            v["equal_hierarchy_share"] for v in result["variables"]
        ) == pytest.approx(1)
    singh = results["singh_2026_relative_weights"]
    assert singh["source_sibling_sums"]["root"] == 99
    assert variable(singh, "soil_ph")["hierarchy_adjusted_ratio"] == pytest.approx(
        3 / 99 * 15
    )
    nath = results["nath_2021_table2"]
    assert nath["leaf_count"] == 26
    assert nath["distinct_variable_scope_count"] == 24
    assert variable(nath, "soil_ph")["branch_count"] == 2
    assert variable(nath, "soil_ph")["hierarchy_adjusted_ratio"] == pytest.approx(1)
    assert variable(nath, "slope")["hierarchy_adjusted_ratio"] == pytest.approx(1.5)
    assert variable(results["haile_2024_table3"], "soil_ph")[
        "hierarchy_adjusted_ratio"
    ] == pytest.approx(1.75)
    assert variable(results["haile_2024_table5"], "soil_ph")[
        "hierarchy_adjusted_ratio"
    ] == pytest.approx(34.5 / 99.9 * 0.2 / 0.04)


@pytest.mark.parametrize(
    "bad_rows",
    [
        [("root", "", ""), ("a", "missing", "1")],
        [("root", "", ""), ("a", "b", "1"), ("b", "a", "1")],
        [("root", "", ""), ("a", "root", "1"), ("a", "root", "2")],
    ],
)
def test_loader_rejects_invalid_graph(tmp_path, bad_rows):
    import csv
    from nbs_ruralscan.recipe.importance import load_weight_models

    path = tmp_path / "bad.csv"
    fields = [
        "model_id",
        "node_id",
        "parent_id",
        "weight",
        "variable",
        "scope",
        "children_complete",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fields)
        writer.writeheader()
        for identity, parent, weight in bad_rows:
            writer.writerow(
                dict(
                    model_id="bad",
                    node_id=identity,
                    parent_id=parent,
                    weight=weight,
                    variable=identity,
                    scope="general",
                    children_complete="true" if identity == "root" else "",
                )
            )
    with pytest.raises(ValueError):
        load_weight_models(path)
