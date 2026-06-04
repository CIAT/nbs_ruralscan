"""Gitignored, process-once cache for `DocIndex` objects.

The cache holds extracted full text of copyrighted PDFs, so it lives **outside the
committed tree** (default ``<repo>/.cache/ingest`` — see ``.gitignore``). Only the
ingestion *code* and the downstream *structured evidence* (short quotes + page refs)
are committed, never this cache.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import DocIndex

DEFAULT_CACHE = Path(".cache/ingest")


def _slug(source_id: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in source_id)[:80]


def cache_path(source_id: str, cache_dir: Path | str = DEFAULT_CACHE) -> Path:
    return Path(cache_dir) / f"{_slug(source_id)}.json"


def save_index(index: DocIndex, cache_dir: Path | str = DEFAULT_CACHE) -> Path:
    p = cache_path(index.source_id, cache_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(index.to_dict(), ensure_ascii=False, indent=2))
    return p


def load_index(
    source_id: str, cache_dir: Path | str = DEFAULT_CACHE
) -> DocIndex | None:
    p = cache_path(source_id, cache_dir)
    if not p.exists():
        return None
    return DocIndex.from_dict(json.loads(p.read_text()))
