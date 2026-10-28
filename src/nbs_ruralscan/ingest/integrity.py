"""Small, shared integrity checks for acquisition and source promotion."""

from __future__ import annotations

import re
import os
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


def pdf_title_error(path: Path, citation: str) -> str | None:
    """Conservative document-binding gate, separate from DOI metadata verification.

    A resolved DOI verifies citation metadata, not arbitrary downloaded bytes.
    Scans and chapters lacking an opening-title match remain identity holds;
    callers must not mistake this for evidence of a paywall or source absence.
    """
    import fitz

    from nbs_ruralscan.schema_tools.verify_metadata import (
        TITLE_THRESH,
        _title_coverage,
        _title_of,
    )

    try:
        title = _title_of(citation)
        with fitz.open(path) as doc:
            head = " ".join(doc[i].get_text() for i in range(min(3, len(doc))))
        if _title_coverage(title, head) >= TITLE_THRESH:
            return None
    except (OSError, RuntimeError, ValueError) as exc:
        return f"unreadable PDF: {exc}"
    return (
        "downloaded PDF does not match the citation title on its opening pages; "
        "wrong documents, scans and chapters require document identity verification"
    )


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
        tmp = Path(f.name)
        try:
            f.write(data)
            f.close()
            tmp.replace(path)
        finally:
            tmp.unlink(missing_ok=True)


def copy_immutable(source: Path, destination: Path) -> None:
    """Publish a complete copy, refusing to replace a different existing artifact.

    A same-directory temporary file and exclusive hard-link creation avoid both
    partial reads and the check-then-overwrite race between acquisition workers.
    Existing identical content is an idempotent success.
    """
    data = source.read_bytes()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as f:
        tmp = Path(f.name)
        try:
            f.write(data)
            f.close()
            try:
                os.link(tmp, destination)
            except FileExistsError:
                if destination.read_bytes() != data:
                    raise FileExistsError(
                        f"Existing artifact differs: {destination}; reconcile before replacement"
                    ) from None
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
