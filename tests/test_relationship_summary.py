from nbs_ruralscan.recipe.relationship_summary import reading, comparison


def row(direction, variable="slope", **kwargs):
    return {"variable": variable, "relationship": {"direction": direction}, **kwargs}


def test_directions_are_plain_language_not_invented_curves():
    kind, headline, _ = reading(row("decreasing"))
    assert kind == "down"
    assert headline == "Higher slope → lower suitability"
    assert reading(row("unclear"))[0] == "unknown"


def test_opposite_directions_remain_disagreement():
    assert "Opposite directions" in comparison([row("increasing"), row("decreasing")])
    assert "transferable agreement" in comparison([row("increasing"), row("unclear")])


def test_class_codes_context_and_enabling_factors_are_not_numeric_responses():
    assert reading(row("positive", "soil_quality_class"))[0] == "classes"
    assert reading(row("negative", "protected_area_status"))[0] == "classes"
    assert (
        reading(row("increasing", compilation_disposition="observed_presence"))[0]
        == "context"
    )
    assert reading(row("increasing", "rootstock_presence"))[0] == "enabling"
    assert reading(row("inverse", "production_gap"))[0] == "context"
