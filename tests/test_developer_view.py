"""Presentation checks for the T4 consumer handoff; no analytical inference."""

from copy import deepcopy
from html.parser import HTMLParser

from nbs_ruralscan.recipe.developer_view import render_developer_view


class Elements(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.elements = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


def contract():
    return {
        "version": "test",
        "nbs": "agroforestry",
        "target_country": "HTI",
        "rows": [
            {
                "rule_id": "rule1",
                "system": "agroforestry__cross_family",
                "theme": "biophysical",
                "variable_group": "land_cover_vegetation",
                "variable": "ndvi",
                "unit": "unitless",
                "module": "M1",
                "role": "suitability_score",
                "function_id": None,
                "function_type": "selection_required",
                "function_options": [
                    {
                        "function_id": "source1",
                        "kind": "source_profile",
                        "label": "ahmad_2018",
                        "unit": "unitless",
                        "intervals": [
                            {
                                "lower": None,
                                "upper": 0.2,
                                "upper_inclusive": False,
                                "score": 0.25,
                            },
                            {
                                "lower": 0.2,
                                "upper": 0.5,
                                "lower_inclusive": True,
                                "upper_inclusive": True,
                                "score": 0.5,
                            },
                            {"lower": 0.5, "upper": 0.7, "score": None},
                            {
                                "lower": 0.7,
                                "upper": None,
                                "lower_inclusive": False,
                                "score": 0.75,
                            },
                        ],
                        "parameters": {"interpolation": "none"},
                    }
                ],
                "dataset": {
                    "dataset_id": "mod13q1_ndvi",
                    "asset": "MODIS/061/MOD13Q1",
                    "canonical_unit": "unitless",
                },
                "weight": {"configured_default": 0.2, "runtime_weight": None},
                "status": "blocked",
                "blockers": ["Choose source"],
                "host_inputs": {},
            }
        ],
    }


def test_no_selection_is_inferred_and_contract_is_unchanged():
    data = contract()
    before = deepcopy(data)
    page = render_developer_view(data)
    assert data == before
    assert "No selected function" in page
    assert "Preview only: first available option, not a recommendation." in page
    assert "Selected function</p>" not in page
    assert "Shared evidence — system not assigned" in page
    assert "Vegetation greenness (NDVI)" in page
    assert "Response selection required" in page
    assert "Runtime: Not assigned" in page


def test_plot_preserves_unknown_gap_and_exact_endpoint_marks():
    page = render_developer_view(contract())
    elements = Elements(page).elements
    segments = [a for t, a in elements if t == "path" and a.get("stroke-width") == "3"]
    assert len(segments) == 3  # Null-scored interval produces no fabricated segment.
    assert all("H" in a["d"] and "V" not in a["d"] for a in segments)
    circles = [a for t, a in elements if t == "circle"]
    assert {a["fill"] for a in circles} == {"white", "#087d72"}
    assert "[0.2, 0.5]" in page
    assert "Unknown</td>" in page


def test_host_upload_requirements_and_parameters_are_readable():
    data = contract()
    data["rows"][0]["host_inputs"] = {
        "farmland_context": {
            "spec": {
                "operation": "supplied_mask",
                "note": "Validated agricultural context required.",
            },
            "inputs": {
                "farmland_context": {
                    "dataset_id": None,
                    "needs_upload": True,
                    "prompt": "Supply local validated mask.",
                }
            },
        }
    }
    page = render_developer_view(data)
    assert "Host conditions and required inputs" in page
    assert "Farmland context — local input required" in page
    assert "Supply local validated mask." in page
    assert "Required function units" in page
    assert "<dt>Asset / location</dt><dd>MODIS/061/MOD13Q1</dd>" in page


def test_untrusted_text_is_escaped_and_comparisons_start_collapsed():
    data = contract()
    row = data["rows"][0]
    row["blockers"] = ['<script>alert("x")</script>']
    second = deepcopy(row["function_options"][0])
    second.update(function_id="source2", label="<img onerror=bad>")
    row["function_options"].append(second)
    page = render_developer_view(data)
    assert "<script>alert" not in page
    assert "&lt;script&gt;" in page
    assert "<img onerror=bad>" not in page
    assert "<details><summary>Compare all 2 options side by side</summary>" in page
    assert all(
        "open" not in attrs
        for tag, attrs in Elements(page).elements
        if tag == "details"
    )


def test_filter_sort_controls_and_downloads_exist():
    elements = Elements(render_developer_view(contract())).elements
    ids = {attrs.get("id") for _, attrs in elements}
    assert {"find", "module", "status", "rules", "count"} <= ids
    assert len([a for t, a in elements if t == "button" and "data-column" in a]) == 8
    hrefs = {attrs.get("href") for tag, attrs in elements if tag == "a"}
    assert {
        "developer_table.csv",
        "developer_contract.json",
        "inclusion.csv",
        "source_importance.json",
    } <= hrefs
