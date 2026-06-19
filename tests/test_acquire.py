"""Tests for deterministic source acquisition (acquire.py).

All HTTP calls are monkeypatched — no network access.
"""

from __future__ import annotations

import hashlib
import json
from unittest.mock import MagicMock, patch

import pytest

from nbs_ruralscan.ingest.acquire import AcquireError, acquire


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_response(
    *,
    status_code: int = 200,
    content: bytes = b"<html><body>Hello</body></html>",
    content_type: str = "text/html; charset=utf-8",
) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.content = content
    resp.headers = {"Content-Type": content_type}
    return resp


# ---------------------------------------------------------------------------
# Failure cases
# ---------------------------------------------------------------------------


def test_acquire_non200_raises(tmp_path):
    """Non-200 HTTP status must raise AcquireError, not silently fail."""
    resp = _mock_response(status_code=404, content=b"Not Found")
    with patch("nbs_ruralscan.ingest.acquire.requests.get", return_value=resp):
        with pytest.raises(AcquireError, match="HTTP 404"):
            acquire(
                "SRC_TEST",
                "https://example.com/page",
                kind="website",
                corpus_dir=tmp_path,
            )


def test_acquire_empty_body_raises(tmp_path):
    """A 200 response with an empty body must raise AcquireError."""
    resp = _mock_response(content=b"")
    with patch("nbs_ruralscan.ingest.acquire.requests.get", return_value=resp):
        with pytest.raises(AcquireError, match="[Ee]mpty|0-byte"):
            acquire(
                "SRC_TEST",
                "https://example.com/page",
                kind="website",
                corpus_dir=tmp_path,
            )


def test_acquire_content_type_mismatch_raises(tmp_path):
    """A response whose content-type contradicts ``kind`` must raise AcquireError."""
    resp = _mock_response(content_type="text/html; charset=utf-8")
    with patch("nbs_ruralscan.ingest.acquire.requests.get", return_value=resp):
        with pytest.raises(AcquireError, match="[Cc]ontent-type|mismatch"):
            acquire(
                "SRC_TEST",
                "https://example.com/paper.pdf",
                kind="pdf",
                corpus_dir=tmp_path,
            )


def test_acquire_unknown_kind_raises(tmp_path):
    """An unknown ``kind`` must raise ValueError before any network call."""
    with pytest.raises(ValueError, match="Unknown kind"):
        acquire("SRC_TEST", "https://example.com/", kind="docx", corpus_dir=tmp_path)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_acquire_writes_artifact_and_meta(tmp_path):
    """A successful fetch writes the artifact file and a valid meta.json sidecar."""
    body = b"<html><body>Hello world</body></html>"
    resp = _mock_response(content=body)
    with patch("nbs_ruralscan.ingest.acquire.requests.get", return_value=resp):
        result = acquire(
            "SRC_HAPPY",
            "https://example.com/page",
            kind="website",
            corpus_dir=tmp_path,
        )

    assert result.ok
    assert result.artifact_path is not None
    assert result.artifact_path.exists()
    assert result.artifact_path.suffix == ".html"
    assert result.artifact_path.read_bytes() == body

    assert result.meta_path is not None
    assert result.meta_path.exists()
    meta = json.loads(result.meta_path.read_text())
    assert meta["source_id"] == "SRC_HAPPY"
    assert meta["kind"] == "website"
    assert meta["http_status"] == 200
    assert meta["bytes"] == len(body)
    # sha1 must match the artifact
    expected_sha1 = hashlib.sha1(body).hexdigest()
    assert meta["sha1"] == expected_sha1


def test_acquire_meta_fields_present(tmp_path):
    """Meta sidecar must contain all required fields."""
    body = b"<html><body>test</body></html>"
    resp = _mock_response(content=body)
    required_fields = {
        "source_id",
        "url",
        "kind",
        "fetched_at",
        "sha1",
        "http_status",
        "content_type",
        "bytes",
        "commit_sha",
    }
    with patch("nbs_ruralscan.ingest.acquire.requests.get", return_value=resp):
        result = acquire(
            "SRC_META", "https://example.com/", kind="website", corpus_dir=tmp_path
        )

    meta = json.loads(result.meta_path.read_text())  # ty: ignore[unresolved-attribute]
    assert required_fields <= set(meta.keys()), (
        f"Missing fields: {required_fields - set(meta.keys())}"
    )


def test_acquire_pdf_kind(tmp_path):
    """PDF kind writes a .pdf artifact."""
    body = b"%PDF-1.4 fake pdf content"
    resp = _mock_response(content=body, content_type="application/pdf")
    with patch("nbs_ruralscan.ingest.acquire.requests.get", return_value=resp):
        result = acquire(
            "SRC_PDF", "https://example.com/paper.pdf", kind="pdf", corpus_dir=tmp_path
        )

    assert result.artifact_path is not None
    assert result.artifact_path.suffix == ".pdf"
    assert result.artifact_path.read_bytes() == body


def test_acquire_skips_if_already_cached(tmp_path):
    """Calling acquire twice without overwrite=True returns cached result without a new fetch."""
    body = b"<html>cached</html>"
    resp = _mock_response(content=body)
    with patch(
        "nbs_ruralscan.ingest.acquire.requests.get", return_value=resp
    ) as mock_get:
        acquire(
            "SRC_CACHE", "https://example.com/", kind="website", corpus_dir=tmp_path
        )
        result2 = acquire(
            "SRC_CACHE", "https://example.com/", kind="website", corpus_dir=tmp_path
        )

    # requests.get called exactly once
    assert mock_get.call_count == 1
    assert result2.reason == "already_cached"


def test_acquire_overwrite_refetches(tmp_path):
    """overwrite=True re-fetches even if artifact exists."""
    body = b"<html>fresh</html>"
    resp = _mock_response(content=body)
    with patch(
        "nbs_ruralscan.ingest.acquire.requests.get", return_value=resp
    ) as mock_get:
        acquire("SRC_OW", "https://example.com/", kind="website", corpus_dir=tmp_path)
        acquire(
            "SRC_OW",
            "https://example.com/",
            kind="website",
            corpus_dir=tmp_path,
            overwrite=True,
        )

    assert mock_get.call_count == 2


def test_acquire_commit_sha_recorded(tmp_path):
    """commit_sha is stored in the sidecar when supplied."""
    body = b"<html>versioned</html>"
    resp = _mock_response(content=body)
    with patch("nbs_ruralscan.ingest.acquire.requests.get", return_value=resp):
        result = acquire(
            "SRC_GIT",
            "https://example.com/",
            kind="website",
            corpus_dir=tmp_path,
            commit_sha="abc123def456",
        )
    meta = json.loads(result.meta_path.read_text())  # ty: ignore[unresolved-attribute]
    assert meta["commit_sha"] == "abc123def456"
