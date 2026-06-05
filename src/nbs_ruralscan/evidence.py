"""Evidence Register units — the structured output of T4 extraction.

One `EvidenceUnit` = one atomic claim pulled from a source, with full provenance
(quote + page) and the four orthogonal tags (`use_role`, `evidence_type`,
`claim_basis`, `claim_scope`). Mirrors the EV table in ``schema/spec.md``. The
extraction command (`.claude/commands/extract-evidence.md`) emits these; `validate`
enforces the hard rules before they're trusted.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .ingest.models import DocIndex
from .ingest.retrieve import retrieve

USE_ROLE = {
    "structural_suitability",
    "climate_risk",
    "priority_need",
    "nbs_effect",
    "dataset",
}
EVIDENCE_TYPE = {
    "literature_relationship",
    "ml_importance",
    "scoping_candidate",
    "expert",
}
CLAIM_BASIS = {
    "primary_measured",
    "modelled",
    "cited_secondary",
    "expert_assertion",
    "table",
    "figure_read",
}
CLAIM_SCOPE = {"practice_technology", "species_specific", "crop_specific"}
CONFIDENCE = {"high", "medium", "low"}

# evidence_types allowed to carry shape-bearing relationship params
_SHAPE_OK = {"literature_relationship", "expert"}


@dataclass
class EvidenceUnit:
    evidence_id: str
    source_id: str
    nbs_id: str
    suitability_family_id: str
    variable: str
    use_role: str
    evidence_type: str
    claim_basis: str
    claim_scope: str
    extraction_confidence: str
    quote: str
    page: int
    relationship: dict[str, Any] | None = (
        None  # e.g. {"opt_low":0,"opt_high":10,"abs_max":44,"unit":"deg"}
    )
    context: dict[str, Any] | None = None  # e.g. {"aez":"humid_tropics"}
    taxon: str | None = None
    lineage_of: str | None = None
    reviewer_ok: bool = False
    # ── paper-first sweep (v0.2.5) — all optional, backwards compatible ──
    raw_name: str | None = None  # surface name from paper before harmonisation
    observed_dataset: str | None = None  # which dataset the paper actually used
    # Namita's attribution requirement: who the paper cites + the paper's own rationale
    attribution: str | None = None  # free-text citation pointer (e.g. "Harrison 2016")
    justification_quote: str | None = (
        None  # second verbatim quote — paper's rationale for the threshold
    )
    justification_page: int | None = None
    selection_justification: str | None = (
        None  # why the paper selected the variable at all
    )
    selection_justification_page: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_SHAPE_KEYS = {
    "opt_low",
    "opt_high",
    "abs_min",
    "abs_max",
    "mean",
    "sigma",
    "threshold",
    "midpoint",
    "slope",
}


def validate(unit: EvidenceUnit) -> list[str]:
    """Return a list of rule violations for one unit (empty = valid)."""
    errs: list[str] = []
    req = [
        "evidence_id",
        "source_id",
        "nbs_id",
        "suitability_family_id",
        "variable",
        "use_role",
        "evidence_type",
        "claim_basis",
        "claim_scope",
        "extraction_confidence",
        "quote",
        "page",
    ]
    for f in req:
        if getattr(unit, f) in (None, ""):
            errs.append(f"missing required field: {f}")
    for fname, allowed in [
        ("use_role", USE_ROLE),
        ("evidence_type", EVIDENCE_TYPE),
        ("claim_basis", CLAIM_BASIS),
        ("claim_scope", CLAIM_SCOPE),
        ("extraction_confidence", CONFIDENCE),
    ]:
        v = getattr(unit, fname)
        if v and v not in allowed:
            errs.append(f"{fname}={v!r} not in {sorted(allowed)}")
    if isinstance(unit.page, int) and unit.page < 1:
        errs.append("page must be >= 1")
    if not (unit.quote or "").strip():
        errs.append("quote must be a verbatim, non-empty string (provenance)")
    # only literature/expert may carry shape params
    if unit.relationship and unit.evidence_type not in _SHAPE_OK:
        if _SHAPE_KEYS & set(unit.relationship):
            errs.append(
                f"evidence_type={unit.evidence_type} may not carry shape params (selection-only)"
            )
    # species/crop claims must name the taxon
    if (
        unit.claim_scope in {"species_specific", "crop_specific"}
        and not (unit.taxon or "").strip()
    ):
        errs.append(f"claim_scope={unit.claim_scope} requires a `taxon`")
    return errs


def validate_units(units: list[EvidenceUnit]) -> dict[str, list[str]]:
    """Validate many; return {evidence_id: errors} for units with violations."""
    out: dict[str, list[str]] = {}
    seen: set[str] = set()
    for u in units:
        e = validate(u)
        if u.evidence_id in seen:
            e.append("duplicate evidence_id")
        seen.add(u.evidence_id)
        if e:
            out[u.evidence_id or "<no id>"] = e
    return out


def package_for_extraction(
    index: DocIndex,
    variable: str,
    aliases: list[str] | None = None,
    *,
    max_passages: int = 12,
) -> dict[str, Any]:
    """Deterministic half of extraction: retrieve the passages an LLM should read.

    Returns a compact bundle (variable + page-stamped passages) to hand to the
    extraction command. The LLM produces `EvidenceUnit`s from this; nothing here
    invents thresholds.
    """
    terms = [variable, *(aliases or [])]
    passages = retrieve(index, terms, max_passages=max_passages)
    return {
        "source_id": index.source_id,
        "variable": variable,
        "terms": terms,
        "needs_ocr_pages": index.needs_ocr_pages,
        "passages": [
            {
                "page": p.page,
                "kind": p.kind,
                "label": p.label,
                "score": round(p.score, 2),
                "text": p.text,
            }
            for p in passages
        ],
    }


def save_units(units: list[EvidenceUnit], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([u.to_dict() for u in units], ensure_ascii=False, indent=2)
    )
    return path
