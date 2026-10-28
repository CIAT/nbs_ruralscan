"""Small, shared integrity checks for acquisition and source promotion."""

from __future__ import annotations

import re
import tempfile
from pathlib import Path


def validate_source_id(source_id: str) -> None:
    """Source IDs become filenames; reject paths instead of silently sanitising them."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", source_id):
        raise ValueError(
            f"Invalid source_id: {source_id!r}; expected a filename-safe ID"
        )


def identity_error(row: dict | None) -> str | None:
    """Offline identity gate. Verification stamps live in the acquisition queue."""
    if row is None:
        return "source has no acquisition-queue identity record"
    if str(row.get("doi") or "").strip():
        if row.get("doi_verified") != "true":
            return "DOI is not verified; run verify_metadata verify before extraction"
    elif row.get("title_verified") != "true":
        return (
            "DOI-less source title is not verified; run verify_metadata verify-titles"
        )
    return None


def validate_body(body: bytes, kind: str) -> None:
    """Reject empty downloads and obvious error pages labelled as PDFs.

    A PDF header is not proof of a readable document or of source identity. PDF
    parsing and title/DOI checks remain separate gates.
    """
    if not body:
        raise ValueError("Empty artifact (0-byte body)")
    if kind == "pdf" and not body.lstrip().startswith(b"%PDF-"):
        raise ValueError("PDF signature missing; response may be an HTML error page")


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
        tmp = Path(f.name)
        try:
            f.write(data)
            f.close()
            tmp.replace(path)
        finally:
            tmp.unlink(missing_ok=True)


def source_identity_differs(source: dict, verified: dict) -> bool:
    """Ignore author-list formatting; require the same DOI and citation title."""
    from nbs_ruralscan.schema_tools.verify_metadata import _title_of

    def doi(row):
        return (
            str(row.get("doi") or "")
            .strip()
            .casefold()
            .removeprefix("https://doi.org/")
        )

    def title(row):
        return " ".join(_title_of(row.get("citation") or "").casefold().split())

    return doi(source) != doi(verified) or title(source) != title(verified)
