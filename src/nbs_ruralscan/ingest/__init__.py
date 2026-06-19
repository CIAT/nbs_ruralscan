"""Vectorless, structure-aware document ingestion for T4 evidence extraction.

Pipeline: PDF/HTML → `build_index` → page-tagged text + sections + tables +
captions (cached, gitignored) → `retrieve` relevant passages by
keyword/structure for a target variable.  Sources are fetched and cached by
``acquire`` before indexing.  See ``methodology/T4_generation_method.md`` §5.1.
"""

from __future__ import annotations

from .acquire import AcquireError, AcquireResult, acquire
from .build import build_cache
from .cache import load_index, save_index
from .html import build_html_index
from .models import Caption, DocIndex, Passage, Section, TableBlock
from .pdf import build_index
from .retrieve import retrieve

__all__ = [
    "AcquireError",
    "AcquireResult",
    "Caption",
    "DocIndex",
    "Passage",
    "Section",
    "TableBlock",
    "acquire",
    "build_cache",
    "build_html_index",
    "build_index",
    "load_index",
    "retrieve",
    "save_index",
]
