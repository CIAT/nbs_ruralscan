"""check_bands.explain_unit — the band rule shown to a reviewer (review theme 4)."""

from __future__ import annotations

import json
from pathlib import Path

from nbs_ruralscan.recipe.cell_synthesis import load_bands
from nbs_ruralscan.schema_tools import check_bands as cb

ROOT = Path(__file__).resolve().parents[1]
BANDS = load_bands(ROOT / "schema" / "registers" / "BANDS_magnitude_bands.csv")


def _row(rel: dict, ctx: dict | None = None) -> dict:
    return {
        "evidence_id": "ev_x",
        "use_role": "nbs_effect",
        "relationship": json.dumps(rel),
        "context": json.dumps(ctx or {}),
    }


def test_pct_change_names_the_threshold():
    out = cb.explain_unit(
        _row({"metric": "pct_change", "magnitude": 5.1, "strength_class": "slight"}),
        BANDS,
    )
    assert out["verdict"] == "rule"
    assert out["class_by_rule"] == "slight"
    assert "10" in out["rule"]
    assert "5.1" in out["value"]


def test_contrast_is_explained_as_a_ratio():
    out = cb.explain_unit(
        _row(
            {
                "metric": "contrast",
                "value_with": 505,
                "value_without": 247,
                "unit": "kg_per_ha",
                "strength_class": "strong",
            }
        ),
        BANDS,
    )
    assert out["verdict"] == "rule"
    assert "ratio" in out["value"]
    assert out["band_id"] == "response_ratio_strong"


def test_mismatch_is_reported_like_check_unit():
    rel = {
        "metric": "pct_change",
        "magnitude": 5.1,
        "strength_class": "strong",
    }
    out = cb.explain_unit(_row(rel), BANDS)
    assert out["verdict"] == "mismatch"
    assert out["class_by_rule"] == "slight"
    assert {f["signal"] for f in cb.check_unit(_row(rel), BANDS)} == {"band_mismatch"}


def test_complete_contrast_is_strong_by_definition():
    out = cb.explain_unit(
        _row({"metric": "complete_contrast", "strength_class": "strong"}), BANDS
    )
    assert out["verdict"] == "rule"
    assert "definition" in out["rule"]


def test_no_size_says_so_instead_of_inventing_a_rule():
    out = cb.explain_unit(
        _row({"metric": "narrative", "strength_class": "unspecified"}), BANDS
    )
    assert out["verdict"] == "no_size"
    assert "no band applies" in out["rule"]


def test_ordinal_rating_quotes_the_scale_row():
    out = cb.explain_unit(
        _row(
            {
                "metric": "ordinal_rating",
                "unit": "wocat_impact",
                "source_scale_value": "+3",
                "strength_class": "strong",
            }
        ),
        BANDS,
    )
    assert out["verdict"] == "rule"
    assert "+3" in out["rule"]


def test_changelog_notes_are_not_shown_as_rules():
    out = cb.explain_unit(
        _row(
            {
                "metric": "contrast",
                "value_with": 2,
                "value_without": 1,
                "strength_class": "strong",
            }
        ),
        BANDS,
    )
    assert "sweep" not in out["rule"]
