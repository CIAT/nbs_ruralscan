"""Cited-originals log: in-text citation parsing (scripts/log-cited-originals.py)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "log_cited_originals", ROOT / "scripts" / "log-cited-originals.py"
)
assert _spec and _spec.loader
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)


def test_keys_in_parses_author_year_forms():
    keys = [k for k, _, _ in L.keys_in("(Beer et al., 1998; Somarriba et al., 2013)")]
    assert keys == ["beer_1998", "somarriba_2013"]
    assert [k for k, _, _ in L.keys_in("Udawatta and Jose 2012")] == ["udawatta_2012"]
    assert [k for k, _, _ in L.keys_in("CONAF 2011")] == ["conaf_2011"]


def test_keys_in_skips_sentence_words():
    assert L.keys_in("In 2015 the project") == []
