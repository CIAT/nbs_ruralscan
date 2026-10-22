"""schema/lookups/display_vocab.csv — the controlled DISPLAY vocabulary (labels + provenance)."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pytest

from nbs_ruralscan.schema_tools import check_context

ROOT = Path(__file__).resolve().parents[1]
VOCAB = ROOT / "schema" / "lookups" / "display_vocab.csv"
MANIFEST = ROOT / "schema" / "structure" / "columns.json"
COLS = [
    "field",
    "code",
    "label",
    "ttl_label",
    "definition",
    "source_type",
    "source_ref",
    "source_url",
    "ratified_by",
    "ratified_date",
]
SOURCE_TYPES = {"ipcc", "standard_ontology", "project_ruling", "spec"}
BLOB = "https://github.com/CIAT/nbs_ruralscan/blob/main/"
#: (manifest table, column) → display_vocab field
MANIFEST_FIELDS = {
    ("T3", "risk_role"): "risk_role",
    ("T3", "mitigation_potential"): "mitigation_potential",
    ("T3", "asset_sensitivity"): "asset_sensitivity",
    ("T3", "confidence"): "confidence",
    ("T3", "evidence_level"): "evidence_level",
    ("T3", "agreement_level"): "agreement_level",
    ("T6", "effect_direction"): "effect_direction",
    ("T6", "effect_confidence"): "confidence",
    ("T6", "evidence_level"): "evidence_level",
    ("T6", "agreement_level"): "agreement_level",
}
#: EV.context vocabularies enforced by check_context → display_vocab field
CONTEXT_FIELDS = {
    "comparator": check_context.COMPARATOR,
    "attribution": check_context.ATTRIBUTION,
    "beneficiary": check_context.BENEFICIARY,
    "cost_nature": check_context.COST_NATURE,
}
#: engine / review-page states not in the manifest enums
EXTRA = {
    "transfer_class": {"in_context", "adjacent", "out_of_context", "mixed"},
    "row_state": {"data_deficient"},
    "mitigation_potential": {"conflicting_evidence"},
    "effect_direction": {"conflicting_evidence"},
    "claim_basis_bucket": {
        "measured",
        "cited_secondary",
        "practitioner_rating",
        "modelled",
        "expert",
    },
}


def _rows() -> list[dict]:
    with VOCAB.open(newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        assert rdr.fieldnames == COLS
        return list(rdr)


def _codes() -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for r in _rows():
        out.setdefault(r["field"], set()).add(r["code"])
    return out


def test_manifest_enums_covered():
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    have = _codes()
    for (table, col), field in MANIFEST_FIELDS.items():
        enum = m["tables"][table]["enum_values"][col]
        missing = set(enum) - have.get(field, set())
        assert not missing, (
            f"{table}.{col} → {field}: no vocab row for {sorted(missing)}"
        )


@pytest.mark.parametrize("field", sorted(CONTEXT_FIELDS))
def test_context_vocab_covered(field):
    missing = set(CONTEXT_FIELDS[field]) - _codes().get(field, set())
    assert not missing, f"context.{field}: no vocab row for {sorted(missing)}"


def test_engine_states_covered():
    from nbs_ruralscan.recipe import cell_synthesis as cs

    have = _codes()
    for field, codes in EXTRA.items():
        assert codes <= have.get(field, set()), (field, codes - have.get(field, set()))
    engine = {
        cs.transfer_class_from_shares(*s)
        for s in [(1, 1, 0), (0, 0, 1), (0, 1, 0), (0.5, 0.5, 0.5)]
    }
    assert engine <= have["transfer_class"]


def test_unique_keys():
    keys = [(r["field"], r["code"]) for r in _rows()]
    assert len(keys) == len(set(keys))


def test_rows_have_label_and_definition():
    for r in _rows():
        assert r["label"].strip(), r
        assert r["definition"].strip(), r


def test_source_type_valid():
    for r in _rows():
        assert r["source_type"] in SOURCE_TYPES, r


def test_source_url_blank_or_https():
    for r in _rows():
        u = r["source_url"].strip()
        assert not u or u.startswith("https://"), r


def test_repo_blob_urls_point_to_existing_files():
    for r in _rows():
        u = r["source_url"].strip()
        if not u.startswith(BLOB):
            continue
        path = u[len(BLOB) :].split("#", 1)[0]
        assert (ROOT / path).is_file(), f"{r['field']}.{r['code']}: {path} not found"


def _slug(heading: str) -> str:
    """GitHub's heading anchor: lowercase, drop punctuation, spaces → hyphens."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def test_repo_blob_anchors_exist():
    for r in _rows():
        u = r["source_url"].strip()
        if not u.startswith(BLOB) or "#" not in u:
            continue
        path, anchor = u[len(BLOB) :].split("#", 1)
        heads = [
            _slug(re.sub(r"^#+\s*", "", ln))
            for ln in (ROOT / path).read_text(encoding="utf-8").splitlines()
            if ln.startswith("#")
        ]
        assert anchor in heads, (
            f"{r['field']}.{r['code']}: #{anchor} not a heading of {path}"
        )


def test_project_rulings_are_dated():
    for r in _rows():
        if r["source_type"] == "project_ruling":
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["ratified_date"]), r
        if r["ratified_by"] == "pete":
            assert r["source_type"] == "project_ruling", r


def test_hazard_placeholder_on_risk_role():
    rr = {r["code"]: r for r in _rows() if r["field"] == "risk_role"}
    assert rr["livelihood_mitigation"]["ttl_label"] == "Protects farmers from <hazard>"
    assert rr["asset_threat"]["ttl_label"] == "Threat to the works from <hazard>"
