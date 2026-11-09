"""Promote acquired sources using explicit paths and recoverable SRC publication."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date
import hashlib
import io
import json
import os
from pathlib import Path
import re
from types import SimpleNamespace

from nbs_ruralscan.ingest.integrity import (
    identity_error,
    pdf_title_error,
    validate_body,
    validate_source_id,
)
from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths
from nbs_ruralscan.schema_tools.publication import staged_publish


@dataclass(frozen=True)
class SourcePromotionPaths:
    queue: Path
    sources: Path
    corpus: Path

    def __post_init__(self):
        for name in ("queue", "sources", "corpus"):
            object.__setattr__(self, name, Path(os.path.abspath(getattr(self, name))))

    @classmethod
    def from_root(
        cls, root: Path, *, corpus: Path | None = None
    ) -> SourcePromotionPaths:
        root = Path(root).resolve()
        return cls(
            root / "pipeline/acquisition_queue.csv",
            root / "schema/registers/SRC_source_register.csv",
            corpus if corpus is not None else root / ".cache/corpus",
        )

    def preflight(self, protected_inputs: tuple[Path, ...] = ()) -> None:
        for path in (self.queue, self.sources, *protected_inputs):
            if not path.is_file():
                raise FileNotFoundError(f"Missing promotion input: {path}")
        SchemaBuildPaths(self.sources.parent / "schema").preflight([self.sources])
        target = str(self.sources.resolve()).casefold()
        readonly = {
            str(p.resolve()).casefold() for p in (self.queue, *protected_inputs)
        }
        corpus = str(self.corpus.resolve()).casefold().rstrip(os.sep)
        if target in readonly or target == corpus or target.startswith(corpus + os.sep):
            raise ValueError(
                "Source-register destination overlaps a read-only promotion input"
            )


@dataclass(frozen=True)
class PromotionResult:
    appended: int
    skipped: tuple[str, ...]
    messages: tuple[str, ...]


class PromotionGateError(ValueError):
    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__("; ".join(problems))


def _indexed_csv(path: Path) -> tuple[list[str], dict[str, dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        cols = list(reader.fieldnames or [])
        if "source_id" not in cols or len(cols) != len(set(cols)):
            raise ValueError(
                f"{path.name}: unique columns including source_id required"
            )
        rows = {}
        for row in reader:
            sid = row.get("source_id") or ""
            if not sid.strip() or sid in rows:
                raise ValueError(f"{path.name}: blank/duplicate source_id: {sid!r}")
            rows[sid] = row
    return cols, rows


_METHOD = {
    "review": "review",
    "systematic_review": "systematic_review",
    "meta_analysis": "meta_analysis",
    "synthesis_brief": "review",
    "case_study_synthesis": "review",
    "institutional_synthesis": "review",
    "programme_evaluation_synthesis": "review",
    "ppar": "mel_report",
    "icr": "mel_report",
    "evaluation_brief": "mel_report",
    "programme_evaluation": "mel_report",
    "programme_evaluation_survey": "mel_report",
    "impact_evaluation": "empirical",
    "quasi_experimental_impact_evaluation": "empirical",
    "field_assessment": "empirical",
    "review_plus_experiment": "empirical",
    "case_analysis_hydraulic": "empirical",
    "multi_site_evaluation": "empirical",
}
_ISO3 = re.compile(r"^[A-Z]{3}$")


def _tag(note: str, key: str) -> str:
    m = re.search(rf"{key}=(\[[^\]]*\]|[^;]+)", note)
    return m.group(1).strip() if m else ""


def _list(raw: str) -> list[str]:
    raw = raw.strip()
    if raw.startswith("["):
        try:
            return [str(x) for x in json.loads(raw.replace("'", '"'))]
        except json.JSONDecodeError:
            return []
    return [raw] if raw else []


def _sha1(p: Path) -> str:
    h = hashlib.sha1()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _ids(paths: list[str]) -> list[str]:
    out: list[str] = []
    for p in paths:
        pth = Path(p)
        if pth.suffix == ".json":
            for it in json.loads(pth.read_text(encoding="utf-8")):
                if isinstance(it, dict):
                    # a staging unit file keys the source as `source_id`; the older lane
                    # manifests used `sid` — accept either rather than failing on shape
                    out.append(str(it.get("source_id") or it.get("sid") or ""))
                else:
                    out.append(str(it))
        else:
            out += [
                ln.strip()
                for ln in pth.read_text(encoding="utf-8").splitlines()
                if ln.strip()
            ]
    return sorted({o for o in out if o})


def _scopes(row: dict, key: str) -> list[str]:
    return list(
        dict.fromkeys(x.strip() for x in (row.get(key) or "").split("|") if x.strip())
    )


def _web_snapshot(corpus: Path, source_id: str) -> Path | None:
    for ext in (".html", ".md", ".txt"):
        f = corpus / f"{source_id}{ext}"
        if f.exists():
            return f
    return None


def _snapshot_title_error(snapshot: Path, citation: str) -> str:
    """Identity check for a web snapshot: the citation's title words must appear near the
    top of the page text (same idea as the PDF opening-pages check)."""
    import re as _re

    from nbs_ruralscan.schema_tools.validate_sources import _strip_html

    raw = snapshot.read_text(encoding="utf-8", errors="ignore")
    text = _strip_html(raw) if snapshot.suffix == ".html" else raw
    if not text.strip():
        return f"{snapshot.name}: empty snapshot"
    m = _re.search(r"\)\.\s*(.+?)(?:\.\s|$)", citation)
    title = (m.group(1) if m else citation).lower()
    words = [w for w in _re.findall(r"[a-zà-ÿ]{5,}", title)][:8]
    head = text[:20000].lower()
    hits = sum(1 for w in words if w in head)
    if words and hits < max(3, len(words) * 2 // 3):
        return (
            f"{snapshot.name}: citation title words not found near the top of the page"
        )
    return ""


def build_row(q: dict, meta: dict, cols: list[str], a, *, corpus: Path) -> dict:
    validate_source_id(q["source_id"])
    scopes = _scopes(q, "nbs_id")
    if a.nbs not in scopes:
        raise ValueError(
            f"requested NbS {a.nbs!r} absent from queue-declared scopes {scopes}"
        )
    problem = identity_error(q)
    if problem:
        raise ValueError(problem)
    if not q.get("target_library_path"):
        raise ValueError("team library path missing; share the source before promotion")
    pdf = corpus / f"{q['source_id']}.pdf"
    snapshot = _web_snapshot(corpus, q["source_id"]) if not pdf.exists() else None
    if snapshot is not None:
        # web source (acquisition rule: url + saved snapshot + section locators)
        problem = _snapshot_title_error(snapshot, q.get("citation") or "")
    else:
        validate_body(pdf.read_bytes(), "pdf")
        problem = pdf_title_error(pdf, q.get("citation") or "")
    if problem:
        raise ValueError(f"source document identity hold: {problem}")
    if not meta.get("benchmark_tier") or not meta.get("venue_type"):
        raise ValueError(
            "--meta must supply benchmark_tier and venue_type from credibility assessment"
        )
    note = q["note"]
    proc = _tag(note, "process") or "updated_lit"
    sub = _tag(note, "method_subtype")
    method = meta.get("method_type") or _METHOD.get(sub)
    if not method:
        raise ValueError(
            "method_type is unknown; supply assessed --meta rather than defaulting to empirical"
        )
    scope = _list(_tag(note, "study_scope"))
    iso = [s for s in scope if _ISO3.match(s)]
    inc = _list(_tag(note, "income_groups_covered"))
    pdf = corpus / f"{q['source_id']}.pdf"
    row = {c: "" for c in cols}
    row.update(
        {
            "source_id": q["source_id"],
            "citation": q["citation"],
            "doi": q.get("doi") or "",
            "benchmark_tier": meta["benchmark_tier"],
            "study_country": meta.get("study_country", "; ".join(iso)),
            "region": meta.get("region", "" if iso else "; ".join(scope)),
            "method_type": method,
            "nbs_ids": "|".join(scopes),
            "vars_extracted": "",
            "extraction_status": "pending",
            "extraction_date": "",
            "extraction_run_id": "",
            "extractor": "",
            "source_kind": "website"
            if snapshot is not None
            else ("paper" if proc == "updated_lit" else "grey_lit"),
            "url": q["url"],
            "artifact_sha1": _sha1(pdf)
            if pdf.exists()
            else (_sha1(snapshot) if snapshot is not None else ""),
            "retrieved_at": a.date,
            "access_status": {
                "oa": "open_access",
                "open_access": "open_access",
                "paywalled": "paywalled",
            }.get(q.get("access_status") or "", "unknown"),
            "source_category": proc,
            "library_path": q["target_library_path"],
            "study_income_group": meta.get(
                "study_income_group", inc[0] if len(inc) == 1 else ""
            ),
            "venue_type": meta["venue_type"],
        }
    )
    return row


def promote(
    source_ids: list[str],
    metadata: dict,
    *,
    paths: SourcePromotionPaths,
    nbs: str,
    retrieved_at: str,
    dry_run: bool = False,
    protected_inputs: tuple[Path, ...] = (),
) -> PromotionResult:
    """Validate a complete batch, then publish only the selected source register.

    Stable inputs and one writer are required. Existing rows retain their bytes.
    Dry runs render and validate the same complete CSV without installation.
    Caught installation failures roll back; incomplete rollback retains recovery.
    """
    paths.preflight(protected_inputs)
    if not isinstance(metadata, dict):
        raise ValueError("Promotion metadata must be an object keyed by source_id")
    results: list[PromotionResult] = []

    def render(staged: SchemaBuildPaths) -> list[Path]:
        assert staged.output_root is not None
        target = staged.output_root / paths.sources.name
        _, queue = _indexed_csv(paths.queue)
        cols, existing = _indexed_csv(target)
        new: list[dict] = []
        errors: list[str] = []
        skipped: list[str] = []
        messages: list[str] = []
        options = SimpleNamespace(nbs=nbs, date=retrieved_at)
        for sid in sorted(set(source_ids)):
            q = queue.get(sid)
            scopes = _scopes(q or {}, "nbs_id")
            if nbs not in scopes:
                errors.append(
                    f"{sid}: requested NbS {nbs!r} absent from queue-declared scopes {scopes}"
                )
                continue
            if sid in existing:
                missing = set(scopes) - set(_scopes(existing[sid], "nbs_ids"))
                if missing:
                    errors.append(
                        f"{sid}: existing SRC lacks queue-declared scopes {sorted(missing)}; reconcile source reuse explicitly"
                    )
                else:
                    skipped.append(sid)
                    messages.append(f"  skip (in SRC, scopes preserved): {sid}")
                continue
            if q is None or q["status"] != "acquired":
                errors.append(f"{sid}: not acquired in queue")
                continue
            try:
                meta = metadata.get(sid, {})
                if not isinstance(meta, dict):
                    raise ValueError("assessed metadata for source must be an object")
                row = build_row(q, meta, cols, options, corpus=paths.corpus)
            except (ValueError, OSError) as exc:
                errors.append(f"{sid}: {exc}")
                continue
            if not row["artifact_sha1"]:
                skipped.append(sid)
                messages.append(f"  skip (no cached PDF): {sid}")
                continue
            new.append(row)
            messages.append(
                f"  + {sid:40} {row['benchmark_tier']:6} {row['method_type']:17} "
                f"{row['source_category']:11} {row['venue_type']:22} {row['study_country']:12} "
                f"{row['study_income_group']}"
            )
        if errors:
            raise PromotionGateError(errors)
        # Serialize every row before changing the private copy. This also catches
        # incompatible SRC headers in dry-run mode, with no partial append.
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=cols, lineterminator="\n")
        writer.writerows(new)
        if new:
            before = target.read_bytes()
            separator = b"" if before.endswith(b"\n") else b"\n"
            target.write_bytes(before + separator + buffer.getvalue().encode("utf-8"))
        messages.append(f"{len(new)} row(s) to append")
        results.append(PromotionResult(len(new), tuple(skipped), tuple(messages)))
        return []

    staged_publish(
        SchemaBuildPaths(paths.sources.parent / "schema"),
        [paths.sources],
        render,
        dry_run=dry_run,
    )
    return results[0]


def main(argv: list[str] | None = None, *, paths: SourcePromotionPaths) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--nbs", required=True)
    ap.add_argument("--sources", nargs="+", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--extractor", default="claude-opus-5 (gated pipeline)")
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--root",
        type=Path,
        help="Data root to validate and update (default: this checkout)",
    )
    ap.add_argument(
        "--corpus-dir",
        type=Path,
        help="Selected cached PDFs (default: selected root/.cache/corpus)",
    )
    args = ap.parse_args(argv)
    if args.root is not None:
        paths = SourcePromotionPaths.from_root(args.root, corpus=args.corpus_dir)
    elif args.corpus_dir is not None:
        paths = SourcePromotionPaths(paths.queue, paths.sources, args.corpus_dir)
    inputs = tuple(Path(p).absolute() for p in [args.meta, *args.sources])
    try:
        paths.preflight(inputs)
        metadata = json.loads(Path(args.meta).read_text(encoding="utf-8"))
        result = promote(
            _ids(args.sources),
            metadata,
            paths=paths,
            nbs=args.nbs,
            retrieved_at=args.date,
            dry_run=args.dry_run,
            protected_inputs=inputs,
        )
    except PromotionGateError as exc:
        print("PROMOTION FAILED — nothing written:\n  " + "\n  ".join(exc.problems))
        return 1
    except (ValueError, OSError) as exc:
        print(f"PROMOTION FAILED: {exc}")
        return 1
    if args.dry_run:
        print("DRY RUN: complete source-register update validated; nothing published")
    for message in result.messages:
        print(message)
    if result.appended and not args.dry_run:
        print(
            f"appended {result.appended} row(s) to {paths.sources}; now regenerate JSON"
        )
    return 0
