"""Strict evidence provenance guardrail.

Every row in ``EV_evidence_register.csv`` is a claim that MUST trace to a verbatim
quote on a specific page of a cached source artifact. This validator proves that —
or fails the build. It is the backstop that makes hand-authored / hallucinated
evidence impossible to commit (the failure mode that contaminated this register).

Rules enforced (no silent escapes — every referenced source is checked):
  1. Every ``source_id`` referenced by EV has a cached artifact in ``.cache/corpus/``
     — a PDF (``{sid}.pdf``) or a web snapshot (``{sid}.txt|.html|.md``). Artifacts
     must be non-empty and parseable.
  2. Every EV ``quote`` appears verbatim (whitespace/punctuation-normalised) in that
     artifact. Ellipsis-joined fragments are each checked. Non-English quotes stored
     as ``"<native> (English: <translation>)"`` are checked on the native text only.
  3. For PDF artifacts the quote must appear ON the cited ``page`` (page-level
     provenance), not merely somewhere in the document.

Only rows whose ``use_role`` is in ``EXEMPT_USE_ROLES`` (baseline map/mask layers
that carry no quotable claim) skip the quote check — and they are reported, never
silent.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None  # ty: ignore[invalid-assignment]

# Rows with these use_roles describe baseline dataset/mask layers, not a literature
# claim — they have no quotable source text. Reported explicitly, never silent.
EXEMPT_USE_ROLES = {"dataset"}

# Artifact extensions, in lookup priority.
_PDF_EXT = ".pdf"
_SNAPSHOT_EXT = (".txt", ".html", ".md")
# The complete set of artifact formats we know how to acquire, cache, and verify.
# A cached file with any other extension is an UNDEFINED FORMAT -> the build pauses
# until a handling rule (acquire adapter + locator semantics + QA/QC rule) is defined.
_KNOWN_EXT = {_PDF_EXT, *_SNAPSHOT_EXT}


def _norm(text: str) -> str:
    """Lower-case and strip everything but alphanumerics.

    Robust to PDF extraction artefacts (hyphenation, ligatures, irregular spacing)
    while still anchoring the quote to real source text.
    """
    return re.sub(r"\W+", "", text.lower())


def _native_part(quote: str) -> str:
    """Drop a bracketed English translation from a multilingual quote.

    AGENTS.md stores non-English quotes as ``"<native> (English: <translation>)"``.
    The translation is not in the source PDF, so verify the native text only.
    """
    m = re.search(r"\(english:.*\)\s*$", quote, flags=re.I | re.S)
    return quote[: m.start()].strip() if m else quote


def _fragments(quote: str) -> list[str]:
    """Split a quote on ellipsis into fragments that must each appear in the source."""
    parts = re.split(r"…|\.\.\.+", _native_part(quote))
    return [p for p in (_norm(x) for x in parts) if p]


def _strip_html(raw: str) -> str:
    return re.sub(r"<[^>]+>", " ", raw)


def _load_pdf_pages(path: Path) -> list[str]:
    """Return per-page normalised text (index 0 == page 1)."""
    if fitz is None:
        raise RuntimeError(
            "PyMuPDF (fitz) is missing — cannot verify PDF quotes. `uv add pymupdf`."
        )
    doc = fitz.open(str(path))
    try:
        return [_norm(page.get_text() or "") for page in doc]
    finally:
        doc.close()


def _find_artifact(corpus: Path, sid: str) -> tuple[Path, str] | None:
    pdf = corpus / f"{sid}{_PDF_EXT}"
    if pdf.exists():
        return pdf, "pdf"
    for ext in _SNAPSHOT_EXT:
        snap = corpus / f"{sid}{ext}"
        if snap.exists():
            return snap, "snapshot"
    return None


def validate_all_sources(schema_root: str | Path) -> None:
    """Verify every EV row; raise ``ValueError`` listing all violations on failure."""
    schema_root = Path(schema_root)
    src_csv = schema_root / "registers" / "SRC_source_register.csv"
    ev_csv = schema_root / "registers" / "EV_evidence_register.csv"
    corpus = schema_root.parent / ".cache" / "corpus"

    if not src_csv.exists() or not ev_csv.exists():
        print(f"Skipping verification: missing registers in {schema_root}")
        return

    with src_csv.open(newline="", encoding="utf-8") as f:
        src_by_id = {row["source_id"]: row for row in csv.DictReader(f)}
    src_ids = set(src_by_id)

    with ev_csv.open(newline="", encoding="utf-8") as f:
        ev_rows = list(csv.DictReader(f))

    if not ev_rows:
        print("VERIFICATION: EV register is empty — nothing to verify.")
        return

    errors: list[str] = []
    # Only sources backing a non-exempt claim need a verifiable artifact; a source
    # referenced solely by baseline-layer (exempt) rows carries no quotable claim.
    referenced = {
        r["source_id"] for r in ev_rows if r.get("use_role") not in EXEMPT_USE_ROLES
    }

    # 1. Referential integrity + artifact presence.
    artifacts: dict[str, tuple[Path, str]] = {}
    for sid in sorted(referenced):
        if sid not in src_ids:
            errors.append(f"[{sid}] EV references a source_id absent from SRC register")
            continue
        found = _find_artifact(corpus, sid)
        if found is None:
            errors.append(
                f"[{sid}] no cached artifact in {corpus} "
                f"(need {sid}.pdf or {sid}.txt/.html/.md) — cannot verify its quotes"
            )
            continue
        path, kind = found
        if path.stat().st_size == 0:
            errors.append(f"[{sid}] cached artifact is empty (0 bytes): {path.name}")
            continue
        artifacts[sid] = (path, kind)

    # 2/3. Quote + page verification.
    pdf_pages: dict[str, list[str]] = {}
    snap_text: dict[str, str] = {}
    n_verified = 0
    n_exempt = 0

    for ev in ev_rows:
        ev_id = ev["evidence_id"]
        sid = ev["source_id"]
        if ev.get("use_role") in EXEMPT_USE_ROLES:
            n_exempt += 1
            continue
        if sid not in artifacts:
            continue  # source-level error already recorded
        quote = ev.get("quote", "")
        frags = _fragments(quote)
        if not frags:
            errors.append(f"[{ev_id}] empty/blank quote — provenance is mandatory")
            continue

        path, kind = artifacts[sid]
        locator_type = (ev.get("locator_type") or "page").strip()

        # Page-level provenance: only for a PDF with a page locator.
        if kind == "pdf" and locator_type == "page":
            if sid not in pdf_pages:
                try:
                    pdf_pages[sid] = _load_pdf_pages(path)
                except Exception as e:  # noqa: BLE001
                    errors.append(f"[{sid}] failed to parse PDF {path.name}: {e}")
                    artifacts.pop(sid, None)
                    continue
            pages = pdf_pages[sid]
            page_raw = (ev.get("page") or "").strip()
            page_no = int(page_raw) if page_raw.isdigit() else None
            on_cited = (
                page_no is not None
                and 1 <= page_no <= len(pages)
                and all(fr in pages[page_no - 1] for fr in frags)
            )
            if on_cited:
                n_verified += 1
                continue
            full = "".join(pages)
            if all(fr in full for fr in frags):
                errors.append(
                    f"[{ev_id}] quote found in {path.name} but NOT on cited page "
                    f"{page_raw!r} — page provenance is wrong"
                )
            else:
                errors.append(
                    f"[{ev_id}] FABRICATED quote — not found verbatim in {path.name}:\n"
                    f'    "{quote[:160]}"'
                )
            continue

        # Non-page locator (section / char_span / file_line) or a snapshot artifact:
        # verify the quote is present verbatim in the artifact. Locator-precise
        # checking (a quote actually sitting under its cited section / at file:line)
        # lands with the HTML/code index adapters; today this proves it is not
        # fabricated and the locator is recorded. file_line additionally requires a
        # commit_sha (enforced in EvidenceUnit.validate — immutable code pin).
        if sid not in snap_text:
            if kind == "pdf":
                if sid not in pdf_pages:
                    try:
                        pdf_pages[sid] = _load_pdf_pages(path)
                    except Exception as e:  # noqa: BLE001
                        errors.append(f"[{sid}] failed to parse PDF {path.name}: {e}")
                        artifacts.pop(sid, None)
                        continue
                snap_text[sid] = "".join(pdf_pages[sid])
            else:
                raw = path.read_text(encoding="utf-8", errors="replace")
                snap_text[sid] = _norm(
                    _strip_html(raw) if path.suffix == ".html" else raw
                )
        if all(fr in snap_text[sid] for fr in frags):
            n_verified += 1
        else:
            errors.append(
                f"[{ev_id}] FABRICATED quote ({locator_type} locator "
                f"{(ev.get('locator') or ev.get('page') or '')!r}) — not found in "
                f'{path.name}:\n    "{quote[:160]}"'
            )

    # ---- Acquisition / cataloguing rule (locked process) ----------------------
    # PDFs discovered as evidence must be catalogued in the SharePoint library; web /
    # github evidence needs a url + a locator (where on the page); an unknown cached
    # format is a hard pause until its handling rule is defined.
    warnings: list[str] = []
    if corpus.exists():
        for p in sorted(corpus.glob("*")):
            if (
                p.is_file()
                and not p.name.startswith(".")
                and p.suffix.lower() not in _KNOWN_EXT
            ):
                errors.append(
                    f"[{p.name}] UNDEFINED ARTIFACT FORMAT '{p.suffix}' in .cache/corpus — "
                    "no handling rule exists. PAUSE: define an acquire adapter + locator "
                    "semantics + a QA/QC rule for this format before registering its evidence."
                )
    for sid, (path, kind) in artifacts.items():
        srow = src_by_id.get(sid, {})
        if kind == "pdf" and not (srow.get("library_path") or "").strip():
            warnings.append(
                f"[{sid}] PDF cached but library_path is empty — catalogue it in the "
                "SharePoint library (…/2_Technical_&_Data/library/<NbS>/) so the team can open it"
            )
        if kind == "snapshot":
            if not (srow.get("url") or "").strip():
                warnings.append(
                    f"[{sid}] web/github snapshot has no url — record the source URL"
                )
            miss = [
                e["evidence_id"]
                for e in ev_rows
                if e["source_id"] == sid
                and e.get("use_role") not in EXEMPT_USE_ROLES
                and not (e.get("locator") or "").strip()
            ]
            if miss:
                warnings.append(
                    f"[{sid}] {len(miss)} web/github evidence row(s) lack a locator "
                    f"(where on the page: section / anchor / selector) — e.g. {miss[0]}"
                )

    if errors:
        head = (
            f"GUARDRAIL FAILED: {len(errors)} evidence-provenance violation(s). "
            "Evidence must trace to a verbatim quote on the cited page of a cached "
            "source. Hand-authored / hallucinated rows are rejected.\n"
        )
        raise ValueError(head + "\n".join(f"  - {e}" for e in errors))

    print(
        f"VERIFICATION SUCCESSFUL: {n_verified} EV quote(s) verified verbatim "
        f"against {len(artifacts)} cached source(s); {n_exempt} exempt (baseline layers)."
    )
    if warnings:
        print(
            f"  PROVENANCE NOTES ({len(warnings)} — non-fatal cataloguing / locator gaps):"
        )
        for w in warnings:
            print(f"    · {w}")


if __name__ == "__main__":
    import sys

    try:
        validate_all_sources(Path("schema"))
        sys.exit(0)
    except Exception as e:  # noqa: BLE001
        print(e, file=sys.stderr)
        sys.exit(1)
