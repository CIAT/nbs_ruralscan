"""Data models for the structure-aware document index.

A `DocIndex` is the vectorless, page-tagged representation of one source PDF that
the T4 extraction step reads from (see ``methodology/T4_generation_method.md`` §5.1).
It is cached once and reused across every variable / NbS / run.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class TableBlock:
    """A table extracted from a page, with its nearest caption."""

    page: int
    rows: list[list[str]]
    caption: str | None = None
    label: str | None = None  # e.g. "Table 3"


@dataclass
class Caption:
    """A figure or table caption located on a page."""

    page: int
    label: str  # e.g. "Figure 2", "Table 3"
    text: str
    kind: str  # "figure" | "table"


@dataclass
class Section:
    """A detected section heading, page-tagged."""

    page: int
    title: str


@dataclass
class Passage:
    """A retrieved snippet with provenance (used by the retriever)."""

    page: int
    text: str
    kind: str  # "body" | "table" | "caption" | "section"
    label: str | None = None
    score: float = 0.0


@dataclass
class DocIndex:
    """Structure-aware index of one document.

    ``pages`` is 0-indexed text; page numbers reported elsewhere are 1-based.
    """

    source_id: str
    path: str
    sha1: str
    n_pages: int
    pages: list[str] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)
    tables: list[TableBlock] = field(default_factory=list)
    captions: list[Caption] = field(default_factory=list)
    needs_ocr_pages: list[int] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> DocIndex:
        return cls(
            source_id=d["source_id"],
            path=d["path"],
            sha1=d["sha1"],
            n_pages=d["n_pages"],
            pages=list(d.get("pages", [])),
            sections=[Section(**s) for s in d.get("sections", [])],
            tables=[TableBlock(**t) for t in d.get("tables", [])],
            captions=[Caption(**c) for c in d.get("captions", [])],
            needs_ocr_pages=list(d.get("needs_ocr_pages", [])),
        )
