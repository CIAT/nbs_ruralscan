"""Tests for the GitHub/tool-code interrogation adapter (scan + slug — no network)."""

from nbs_ruralscan.ingest import github


def test_scan_flags_param_kinds():
    code = "\n".join(
        [
            "// Alley Cropping",
            "var weightWaterErosion = 5;",
            "var weightWindErosion = 5;",
            "var slopeThreshold = 15;",
            "var CDLcrops = cropLandcover.lte(61).or(cropLandcover.gte(205));",
            "var buf = feature.buffer({'distance':-10});",
            "var maxDistance:30;",
            "var suit = img.remap([1,2],[0,1]);",
            "var label = 'just a comment, no number';",
        ]
    )
    cands = github.scan_candidates(code, path="gee_script/Map")
    kinds = {c["kind"] for c in cands}
    assert {"weight", "threshold", "mask", "buffer", "reclassify"} <= kinds
    # line numbers are 1-based, usable as a locator
    weights = [c for c in cands if c["kind"] == "weight"]
    assert weights and weights[0]["line"] == 2
    assert all(c["path"] == "gee_script/Map" for c in cands)
    # a plain comment line is not flagged
    assert not any("just a comment" in c["text"] for c in cands)


def test_scan_ignores_prose():
    text = "Agroforestry can reduce erosion in many landscapes worldwide."
    assert github.scan_candidates(text) == []


def test_slug_is_stable_snake_case():
    assert (
        github._slug(
            "saraheb3/AgroforestrySuitability_GEE",
            "gee_script/Agroforestry-Suitability-Map",
        )
        == "saraheb3_agroforestry_suitability_map"
    )


def test_default_ignore_skips_species_scripts():
    import re

    ig = [re.compile(p) for p in github.DEFAULT_IGNORE]
    assert any(rx.search("gee_script/Apple-Tree-Growth-Suitability") for rx in ig)
    assert not any(rx.search("gee_script/Agroforestry-Suitability-Map") for rx in ig)
