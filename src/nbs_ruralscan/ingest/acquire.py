"""Deterministic source acquisition — fetch once, cache immutably.

Fetches a URL, saves the raw artifact under ``corpus_dir``, and writes an
accompanying ``{source_id}.meta.json`` provenance sidecar.  No LLM tokens
consumed.  Fail-hard on empty bodies, bad status codes, or content-type
mismatches so a 0-byte artefact is never silently accepted downstream.

CLI::

    python -m nbs_ruralscan.ingest.acquire <source_id> <url> --kind website
    python -m nbs_ruralscan.ingest.acquire SRC_001 https://example.org/paper.pdf --kind pdf
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import requests

# Corpus cache root — parallel to the docindex cache (.cache/ingest)
DEFAULT_CORPUS_DIR = ".cache/corpus"

# Request settings
_TIMEOUT = (10, 60)  # (connect, read) seconds
_USER_AGENT = (
    "nbs-ruralscan/0.1 (evidence pipeline; https://github.com/ciat/nbs_ruralscan)"
)

# Accepted content-type fragments per kind
_CONTENT_TYPE_MAP: dict[str, tuple[str, ...]] = {
    "pdf": ("application/pdf", "application/octet-stream", "binary/octet-stream"),
    "website": ("text/html", "application/xhtml", "text/plain", "text/"),
    "markdown": ("text/markdown", "text/plain", "text/x-markdown", "text/"),
}

# File extension per kind
_EXT_MAP: dict[str, str] = {
    "pdf": ".pdf",
    "website": ".html",
    "markdown": ".md",
}

_VALID_KINDS = frozenset(_EXT_MAP)


class AcquireError(RuntimeError):
    """Raised when acquisition fails for a non-retriable reason."""


@dataclass
class AcquireResult:
    """Outcome of a single :func:`acquire` call."""

    ok: bool
    source_id: str
    artifact_path: Path | None
    meta_path: Path | None
    reason: str | None = None  # populated when ok=False


def _sha1_hex(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def _detect_kind_from_content_type(ct: str) -> str | None:
    ct_lower = ct.lower()
    if "pdf" in ct_lower:
        return "pdf"
    if "html" in ct_lower or "xhtml" in ct_lower:
        return "website"
    if "markdown" in ct_lower:
        return "markdown"
    return None


def _check_content_type(kind: str, content_type: str) -> None:
    """Raise AcquireError if content-type contradicts ``kind``."""
    accepted = _CONTENT_TYPE_MAP[kind]
    ct_lower = content_type.lower()
    if not any(ct_lower.startswith(a) or a in ct_lower for a in accepted):
        raise AcquireError(
            f"Content-type mismatch for kind={kind!r}: "
            f"server returned {content_type!r}. "
            f"Expected one of {accepted}."
        )


def acquire(
    source_id: str,
    url: str,
    *,
    kind: str,
    corpus_dir: str | Path = DEFAULT_CORPUS_DIR,
    commit_sha: str | None = None,
    overwrite: bool = False,
) -> AcquireResult:
    """Fetch ``url`` and cache an immutable artifact + provenance sidecar.

    Parameters
    ----------
    source_id:
        Identifier matching ``SRC_source_register`` (e.g. ``"SRC_001"``).
    url:
        Remote URL to fetch.
    kind:
        ``"pdf"`` | ``"website"`` | ``"markdown"``.
    corpus_dir:
        Root directory for cached artifacts (default ``.cache/corpus``).
    commit_sha:
        Optional VCS pin to record in the sidecar (``null`` when omitted).
    overwrite:
        Re-fetch even if the artifact already exists.

    Returns
    -------
    AcquireResult
        Always returned; ``ok=False`` when a non-raising path was taken
        (currently unused — method raises on all failure modes).

    Raises
    ------
    AcquireError
        Non-200 HTTP status, empty response body, or content-type mismatch.
    ValueError
        Unknown ``kind``.
    """
    if kind not in _VALID_KINDS:
        raise ValueError(f"Unknown kind {kind!r}. Valid values: {sorted(_VALID_KINDS)}")

    corpus_path = Path(corpus_dir)
    corpus_path.mkdir(parents=True, exist_ok=True)

    ext = _EXT_MAP[kind]
    artifact_path = corpus_path / f"{source_id}{ext}"
    meta_path = corpus_path / f"{source_id}.meta.json"

    if artifact_path.exists() and not overwrite:
        # Already cached — load existing meta
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        return AcquireResult(
            ok=True,
            source_id=source_id,
            artifact_path=artifact_path,
            meta_path=meta_path if meta_path.exists() else None,
            reason="already_cached",
        )

    # --- Fetch -----------------------------------------------------------
    headers = {"User-Agent": _USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=_TIMEOUT, stream=True)
    except requests.exceptions.RequestException as exc:
        raise AcquireError(f"Network error fetching {url!r}: {exc}") from exc

    if response.status_code != 200:
        raise AcquireError(
            f"HTTP {response.status_code} fetching {source_id!r} from {url!r}"
        )

    content_type = response.headers.get("Content-Type", "")
    _check_content_type(kind, content_type)

    body = response.content
    if not body:
        raise AcquireError(
            f"Empty response body for {source_id!r} from {url!r}. "
            "Refusing to write a 0-byte artifact."
        )

    # --- Write artifact (atomic-ish: write then rename) ------------------
    tmp = artifact_path.with_suffix(".tmp")
    try:
        tmp.write_bytes(body)
        tmp.rename(artifact_path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise

    # --- Write sidecar ---------------------------------------------------
    meta: dict = {
        "source_id": source_id,
        "url": url,
        "kind": kind,
        "fetched_at": datetime.now(tz=timezone.utc).isoformat(),
        "sha1": _sha1_hex(body),
        "http_status": response.status_code,
        "content_type": content_type,
        "bytes": len(body),
        "commit_sha": commit_sha,
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    return AcquireResult(
        ok=True,
        source_id=source_id,
        artifact_path=artifact_path,
        meta_path=meta_path,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Fetch a source URL and cache an immutable artifact + sidecar.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    ap.add_argument("source_id", help="Source identifier (e.g. SRC_001)")
    ap.add_argument("url", help="URL to fetch")
    ap.add_argument(
        "--kind",
        choices=sorted(_VALID_KINDS),
        required=True,
        help="Artifact kind",
    )
    ap.add_argument(
        "--corpus-dir",
        default=DEFAULT_CORPUS_DIR,
        help="Corpus cache root directory",
    )
    ap.add_argument(
        "--commit-sha",
        default=None,
        help="Optional VCS pin to record in the sidecar",
    )
    ap.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-fetch even if the artifact already exists",
    )
    args = ap.parse_args()

    try:
        result = acquire(
            args.source_id,
            args.url,
            kind=args.kind,
            corpus_dir=args.corpus_dir,
            commit_sha=args.commit_sha,
            overwrite=args.overwrite,
        )
    except AcquireError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if result.reason == "already_cached":
        print(f"cached  {result.source_id} → {result.artifact_path}")
    else:
        meta = json.loads(result.meta_path.read_text())  # ty: ignore[unresolved-attribute]
        print(
            f"fetched {result.source_id} → {result.artifact_path} "
            f"({meta['bytes']} bytes, sha1={meta['sha1'][:12]})"
        )


if __name__ == "__main__":
    main()
