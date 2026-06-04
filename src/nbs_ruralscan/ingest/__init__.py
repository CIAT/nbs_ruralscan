"""Vectorless, structure-aware document ingestion for T4 evidence extraction.

Pipeline: PDF → `build_index` → page-tagged text + sections + tables + captions
(cached, gitignored) → `retrieve` relevant passages by keyword/structure for a
target variable. See ``methodology/T4_generation_method.md`` §5.1.
"""

from __future__ import annotations

from .build import build_cache
from .cache import load_index, save_index
from .models import Caption, DocIndex, Passage, Section, TableBlock
from .pdf import build_index
from .retrieve import retrieve

__all__ = [
    "Caption",
    "DocIndex",
    "Passage",
    "Section",
    "TableBlock",
    "build_cache",
    "build_index",
    "load_index",
    "retrieve",
    "save_index",
]
