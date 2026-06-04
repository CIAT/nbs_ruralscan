"""Tests for context-aware dataset resolution (BIND registry runtime)."""

from __future__ import annotations

import pytest

from nbs_ruralscan.binding import Binding, resolve_all, resolve_binding

# A minimal in-memory registry: global MapSPAM + an SLE upload-required override.
BINDINGS = [
    Binding("slope__global", "slope", "global", "", "srtm_dem_30m", 1, "catalogued"),
    Binding(
        "cocoa__global",
        "cocoa_distribution",
        "global",
        "",
        "mapspam_cocoa_2020",
        2,
        "catalogued",
    ),
    Binding(
        "cocoa__sle",
        "cocoa_distribution",
        "admin_country",
        "sle",
        "",
        1,
        "requires_upload",
        "National EO cocoa map known to exist",
    ),
    Binding(
        "cocoa__humid",
        "cocoa_distribution",
        "aez",
        "humid_tropics",
        "eo_cocoa_humid",
        1,
        "community",
    ),
]


def test_global_default_when_no_context_match():
    r = resolve_binding(BINDINGS, "cocoa_distribution", {"temperate_europe"})
    assert r.dataset_id == "mapspam_cocoa_2020"
    assert r.needs_upload is False


def test_most_specific_context_wins():
    # admin_country (sle) beats aez (humid_tropics) even though both match.
    r = resolve_binding(BINDINGS, "cocoa_distribution", {"sle", "humid_tropics"})
    assert r.winning_binding.binding_id == "cocoa__sle"


def test_requires_upload_flags_and_falls_back():
    r = resolve_binding(BINDINGS, "cocoa_distribution", {"sle", "humid_tropics"})
    assert r.needs_upload is True
    assert (
        r.dataset_id == "eo_cocoa_humid"
    )  # best catalogued/community fallback among matches
    assert r.fell_back_to is not None
    assert r.prompt and "upload" in r.prompt.lower()


def test_aez_override_used_when_catalogued():
    # No SLE; humid_tropics community dataset should win over the global default.
    r = resolve_binding(BINDINGS, "cocoa_distribution", {"humid_tropics"})
    assert r.dataset_id == "eo_cocoa_humid"
    assert r.needs_upload is False


def test_resolve_all_collects_prompts():
    res, prompts = resolve_all(
        BINDINGS, ["slope", "cocoa_distribution"], {"sle", "humid_tropics"}
    )
    assert res["slope"].dataset_id == "srtm_dem_30m"
    assert len(prompts) == 1


def test_missing_variable_raises():
    with pytest.raises(KeyError):
        resolve_binding(BINDINGS, "nonexistent", {"sle"})
