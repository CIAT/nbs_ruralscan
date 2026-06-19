"""Tests for the evidence-provenance guardrail.

The old validator was theatre — it verified ~10% of rows and silently passed the
rest (the failure mode that let hallucinated evidence into the register). These
tests pin the hardened behaviour: fabricated quotes, wrong cited pages, and
missing source artifacts must all fail loudly.
"""

from __future__ import annotations

import csv
from pathlib import Path

import fitz  # PyMuPDF — already a project dep
import pytest

from nbs_ruralscan.schema_tools.validate_sources import (
    _fragments,
    _native_part,
    _norm,
    validate_all_sources,
)

_EV_COLS = [
    "evidence_id",
    "source_id",
    "nbs_id",
    "suitability_family_id",
    "variable",
    "relationship",
    "context",
    "use_role",
    "evidence_type",
    "claim_basis",
    "claim_scope",
    "lineage_of",
    "extraction_confidence",
    "quote",
    "page",
    "locator_type",
    "locator",
    "commit_sha",
    "reviewer_ok",
    "raw_name",
    "taxon",
    "observed_dataset",
    "attribution",
]
_SRC_COLS = [
    "source_id",
    "citation",
    "doi",
    "benchmark_tier",
    "method_type",
    "source_kind",
]


def _make_pdf(path: Path, pages: list[str]) -> None:
    doc = fitz.open()
    for body in pages:
        page = doc.new_page()
        page.insert_text((72, 72), body)
    doc.save(str(path))
    doc.close()


def _write_schema(root: Path, ev_rows: list[dict], src_rows: list[dict]) -> Path:
    reg = root / "schema" / "registers"
    reg.mkdir(parents=True)
    for name, cols, rows in [
        ("EV_evidence_register", _EV_COLS, ev_rows),
        ("SRC_source_register", _SRC_COLS, src_rows),
    ]:
        with (reg / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in rows:
                w.writerow({c: r.get(c, "") for c in cols})
    return root / "schema"


def _ev(eid: str, sid: str, quote: str, page: int | str, **kw) -> dict:
    base = dict(
        evidence_id=eid,
        source_id=sid,
        nbs_id="agroforestry",
        suitability_family_id="F1",
        variable="slope",
        use_role="structural_suitability",
        evidence_type="literature_relationship",
        claim_basis="table",
        claim_scope="practice_technology",
        extraction_confidence="high",
        quote=quote,
        page=str(page),
        locator_type="page",
    )
    base.update(kw)
    return base


def test_norm_and_fragments():
    assert _norm("Slope: 0–5°!") == "slope05"
    assert _fragments("A B ... C D") == [_norm("A B"), _norm("C D")]
    # native-only check for multilingual quotes
    assert _native_part("Pente faible (English: gentle slope)") == "Pente faible"


def test_passes_real_quote_on_cited_page(tmp_path):
    schema = _write_schema(
        tmp_path,
        ev_rows=[_ev("ev1", "src1", "slopes below five degrees are most suitable", 2)],
        src_rows=[dict(source_id="src1", method_type="empirical")],
    )
    corpus = tmp_path / ".cache" / "corpus"
    corpus.mkdir(parents=True)
    _make_pdf(
        corpus / "src1.pdf",
        ["intro page one", "slopes below five degrees are most suitable here"],
    )
    validate_all_sources(schema)  # must not raise


def test_fabricated_quote_fails(tmp_path):
    schema = _write_schema(
        tmp_path,
        ev_rows=[_ev("evX", "src1", "this sentence was never in the paper", 1)],
        src_rows=[dict(source_id="src1", method_type="empirical")],
    )
    (tmp_path / ".cache" / "corpus").mkdir(parents=True)
    _make_pdf(
        tmp_path / ".cache" / "corpus" / "src1.pdf", ["completely different text"]
    )
    with pytest.raises(ValueError, match="FABRICATED"):
        validate_all_sources(schema)


def test_right_quote_wrong_page_fails(tmp_path):
    schema = _write_schema(
        tmp_path,
        ev_rows=[_ev("evP", "src1", "the threshold is ten percent", 1)],
        src_rows=[dict(source_id="src1", method_type="empirical")],
    )
    (tmp_path / ".cache" / "corpus").mkdir(parents=True)
    _make_pdf(
        tmp_path / ".cache" / "corpus" / "src1.pdf",
        [
            "page one has nothing",
            "the threshold is ten percent",
        ],  # quote on p.2, cited p.1
    )
    with pytest.raises(ValueError, match="NOT on cited page"):
        validate_all_sources(schema)


def test_missing_artifact_fails(tmp_path):
    schema = _write_schema(
        tmp_path,
        ev_rows=[_ev("evM", "ghost", "anything", 1)],
        src_rows=[dict(source_id="ghost", method_type="ahp")],
    )
    (tmp_path / ".cache" / "corpus").mkdir(parents=True)
    with pytest.raises(ValueError, match="no cached artifact"):
        validate_all_sources(schema)


def test_empty_register_passes(tmp_path):
    schema = _write_schema(tmp_path, ev_rows=[], src_rows=[])
    validate_all_sources(schema)  # must not raise


def test_section_locator_html_snapshot_passes(tmp_path):
    schema = _write_schema(
        tmp_path,
        ev_rows=[
            _ev(
                "evH",
                "web1",
                "agroforestry reduces surface runoff",
                "",
                locator_type="section",
                locator="3.2 Hydrology",
            )
        ],
        src_rows=[
            dict(source_id="web1", method_type="synthesis", source_kind="website")
        ],
    )
    corpus = tmp_path / ".cache" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "web1.html").write_text(
        "<html><body><h2>3.2 Hydrology</h2>"
        "<p>agroforestry reduces surface runoff markedly</p></body></html>",
        encoding="utf-8",
    )
    validate_all_sources(schema)  # must not raise


def test_section_locator_fabricated_fails(tmp_path):
    schema = _write_schema(
        tmp_path,
        ev_rows=[
            _ev(
                "evHf",
                "web1",
                "a claim never on the page",
                "",
                locator_type="section",
                locator="3.2 Hydrology",
            )
        ],
        src_rows=[
            dict(source_id="web1", method_type="synthesis", source_kind="website")
        ],
    )
    corpus = tmp_path / ".cache" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "web1.html").write_text(
        "<html><body><p>unrelated</p></body></html>", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="FABRICATED"):
        validate_all_sources(schema)


def test_dataset_role_is_exempt(tmp_path):
    schema = _write_schema(
        tmp_path,
        ev_rows=[_ev("evD", "maplayer", "n/a baseline", 1, use_role="dataset")],
        src_rows=[dict(source_id="maplayer", method_type="empirical")],
    )
    (tmp_path / ".cache" / "corpus").mkdir(parents=True)
    validate_all_sources(schema)  # baseline layer carries no quotable claim
