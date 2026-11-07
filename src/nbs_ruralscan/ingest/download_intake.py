"""File human downloads with explicit paths and recoverable local publication.

Cache, library and archive copies precede the queue. Download cleanup follows
successful publication and is reported separately; it is not rolled back.
Stable inputs and a single writer are required. No remote sync is implied.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date
import hashlib
import io
import os
from pathlib import Path
import shutil

from nbs_ruralscan.ingest.acquisition_queue import _acquisition_workspace
from nbs_ruralscan.ingest.integrity import (
    atomic_write,
    copy_immutable,
    validate_source_id,
)
from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths
from nbs_ruralscan.schema_tools.publication import _state, staged_publish
from nbs_ruralscan.schema_tools.verify_metadata import (
    TITLE_THRESH,
    _title_coverage,
    _title_of,
)


def title_check(pdf: Path, citation: str) -> tuple[bool, str]:
    """(ok, where): opening-page title match; body matches need identity review."""
    import fitz

    title = _title_of(citation)
    with fitz.open(pdf) as doc:
        head = " ".join(doc[i].get_text() for i in range(min(3, len(doc))))
        if _title_coverage(title, head) >= TITLE_THRESH:
            return True, "opening pages"
        prev = ""
        for i in range(min(len(doc), 500)):
            page = doc[i].get_text()
            if _title_coverage(title, prev + " " + page) >= TITLE_THRESH:
                return (
                    False,
                    f"title only in body (page {i + 1}); could be a cited reference; verify chapter identity manually",
                )
            prev = page
    return False, f"title not found: {title[:80]}"


@dataclass(frozen=True)
class DownloadIntakePaths:
    queue: Path
    corpus: Path
    downloads: Path
    library: Path | None

    def __post_init__(self):
        for name in ("queue", "corpus", "downloads", "library"):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, Path(os.path.abspath(value)))

    @classmethod
    def from_root(cls, root, *, downloads, library=None, corpus=None):
        root = Path(root).resolve()
        return cls(
            root / "pipeline/acquisition_queue.csv",
            root / ".cache/corpus" if corpus is None else Path(corpus),
            Path(downloads),
            Path(library) if library is not None else None,
        )


@dataclass(frozen=True)
class DownloadIntakeResult:
    done: tuple[str, ...]
    bad: tuple[str, ...]
    no_library: tuple[str, ...]
    changed: tuple[Path, ...]
    cleanup_pending: tuple[str, ...] = ()

    @property
    def returncode(self) -> int:
        return int(bool(self.bad or self.no_library or self.cleanup_pending))


def _rows(raw: bytes):
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""), strict=True)
    cols = list(reader.fieldnames or [])
    required = {
        "source_id",
        "citation",
        "status",
        "blocker",
        "note",
        "title_verified",
        "target_library_path",
    }
    if len(cols) != len(set(cols)) or not required.issubset(cols):
        raise ValueError("Download intake queue has duplicate/missing columns")
    rows = list(reader)
    seen = set()
    for row in rows:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("Download intake queue has a malformed row")
        sid = row["source_id"]
        if not sid.strip() or sid in seen:
            raise ValueError("Download intake queue has blank/duplicate source IDs")
        seen.add(sid)
    return rows, cols


def _key(path: Path) -> str:
    return str(path.resolve()).casefold().rstrip(os.sep)


def _overlaps(a: str, b: str) -> bool:
    return a == b or a.startswith(b + os.sep) or b.startswith(a + os.sep)


def run_intake(
    paths: DownloadIntakePaths,
    *,
    dry_run: bool = False,
    keep: bool = False,
    today: str | None = None,
    title_checker=None,
    copy_file=None,
    write_queue=None,
) -> DownloadIntakeResult:
    title_checker = title_checker or title_check
    copy_file = copy_file or copy_immutable
    write_queue = write_queue or atomic_write
    today = today or date.today().isoformat()
    raw_queue = paths.queue.read_bytes()
    rows, cols = _rows(raw_queue)
    by_id = {row["source_id"]: row for row in rows}
    sources = [p for p in sorted(paths.downloads.glob("*.pdf")) if p.stem in by_id]
    storage = [paths.corpus, paths.downloads]
    if paths.library is not None:
        storage.append(paths.library)
    keys = [_key(p) for p in storage]
    if any(_overlaps(a, b) for i, a in enumerate(keys) for b in keys[i + 1 :]):
        raise ValueError("Download, corpus and library roots overlap")
    if any(_overlaps(_key(paths.queue), key) for key in keys):
        raise ValueError("Download intake queue overlaps storage")

    planned, invalid = {}, {}
    targets = [paths.queue]
    for pdf in sources:
        validate_source_id(pdf.stem)
        row = by_id[pdf.stem]
        label = row.get("target_library_path", "").strip()
        if paths.library is None or not label:
            continue
        if (
            Path(label).is_absolute()
            or "\\" in label
            or ".." in label.split("/")
            or not (paths.library / label)
            .resolve()
            .is_relative_to(paths.library.resolve())
        ):
            invalid[pdf] = f"{pdf.name}: library path escapes library root"
            continue
        destinations = [paths.corpus / pdf.name, paths.library / label]
        if not keep:
            destinations.append(paths.downloads / "nbs_ingested" / pdf.name)
        planned[pdf] = destinations
        targets.extend(destinations)
    canonical = [_key(p) for p in [*targets, *sources]]
    if len(canonical) != len(set(canonical)):
        raise ValueError("Download intake paths alias each other")
    root = Path(os.path.commonpath([p.parent for p in [*targets, *sources]]))
    context = SchemaBuildPaths(root / "schema")
    context.preflight([*targets, *sources])
    before = {p: _state(p) for p in [*targets, *sources]}
    queue_state = before[paths.queue]
    if queue_state is None or queue_state[0] != hashlib.sha256(raw_queue).hexdigest():
        raise ValueError("Download intake queue changed while reading")

    def unchanged():
        context.preflight([*targets, *sources])
        for path, state in before.items():
            if _state(path) != state:
                raise ValueError(f"Download intake input/output changed: {path}")

    done, bad, no_lib = [], [], []
    completed = []
    outputs = []
    cleanup_pending = []
    changed = []
    with _acquisition_workspace() as workspace:
        private_sources = {}
        private_targets = {
            p: workspace / "outputs" / p.relative_to(root) for p in targets
        }
        for i, pdf in enumerate(sources):
            private = workspace / "downloads" / str(i) / pdf.name
            private.parent.mkdir(parents=True)
            shutil.copy2(pdf, private)
            previous = before[pdf]
            if (
                previous is None
                or hashlib.sha256(private.read_bytes()).hexdigest() != previous[0]
            ):
                raise ValueError(f"Download changed while copying: {pdf}")
            private_sources[pdf] = private
        for target in targets:
            private = private_targets[target]
            private.parent.mkdir(parents=True, exist_ok=True)
            previous = before[target]
            if previous is not None:
                shutil.copy2(target, private)
                if hashlib.sha256(private.read_bytes()).hexdigest() != previous[0]:
                    raise ValueError(f"Download output changed while copying: {target}")
        unchanged()
        for pdf in sources:
            row = by_id[pdf.stem]
            private = private_sources[pdf]
            try:
                ok, where = title_checker(private, row.get("citation", ""))
            except (OSError, RuntimeError, ValueError) as exc:
                message = str(exc).replace(str(private), str(pdf))
                bad.append(f"{pdf.name}: unreadable PDF: {message}")
                continue
            if not ok:
                bad.append(f"{pdf.name}: {where}")
                continue
            if pdf in invalid:
                bad.append(invalid[pdf])
                continue
            if pdf not in planned:
                no_lib.append(row["source_id"])
                continue
            digest = hashlib.sha256(private.read_bytes()).hexdigest()
            destinations = planned[pdf]
            if any(
                state is not None and state[0] != digest
                for state in (before[p] for p in destinations)
            ):
                bad.append(
                    f"{pdf.name}: existing cache/library artifact differs; reconcile identity before replacement"
                )
                continue
            try:
                for target in destinations:
                    copy_file(private, private_targets[target])
            except OSError as exc:
                message = str(exc).replace(str(private), str(pdf))
                for target in destinations:
                    message = message.replace(str(private_targets[target]), str(target))
                bad.append(f"{pdf.name}: filing held: {message}")
                continue
            done.append(f"{pdf.name}: title on {where}")
            row["status"] = "acquired"
            row["title_verified"] = "true"
            row["blocker"] = ""
            add = f"acquired {today} from a human/browser download; title verified ({where})"
            row["note"] = f"{row['note']} | {add}" if row.get("note") else add
            outputs.extend(destinations)
            completed.append(pdf)
        unchanged()
        if done:
            buffer = io.StringIO(newline="")
            writer = csv.DictWriter(buffer, fieldnames=cols, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            write_queue(private_targets[paths.queue], buffer.getvalue().encode("utf-8"))
            outputs.append(paths.queue)
            validators = {}
            for pdf in completed:
                for target in planned[pdf]:

                    def validate(staged, *, pdf=pdf):
                        if staged.read_bytes() != private_sources[pdf].read_bytes():
                            raise ValueError(
                                f"Filed PDF differs from checked download: {pdf.name}"
                            )
                        ok, why = title_checker(
                            staged, by_id[pdf.stem].get("citation", "")
                        )
                        if not ok:
                            raise ValueError(
                                f"Filed PDF identity changed: {pdf.name}: {why}"
                            )

                    validators[target] = validate

            # The queue is validated last, after every staged PDF/title check.
            # Read-only downloads are not publisher destinations, so check them
            # again here before any output can be installed.
            validators[paths.queue] = lambda _: unchanged()

            def render(staged):
                unchanged()
                assert staged.output_root is not None
                for target in outputs:
                    output = staged.output_root / target.relative_to(root)
                    output.parent.mkdir(parents=True, exist_ok=True)
                    # A private comparison may originate from a read-only existing file.
                    if output.exists():
                        output.chmod(output.stat().st_mode | 0o200)
                    shutil.copy2(private_targets[target], output)
                return []

            changed = staged_publish(
                context,
                outputs,
                render,
                create_only_destinations=tuple(p for p in outputs if p != paths.queue),
                artifact_validators=validators,
                dry_run=dry_run,
            )
            if not dry_run and not keep:
                # Publication is committed. Cleanup must not undo it or discard a
                # download changed since preparation, even when another cleanup fails.
                for pdf in completed:
                    try:
                        context.preflight([pdf])
                        if _state(pdf) != before[pdf]:
                            raise ValueError(
                                "download changed after preparation; preserved"
                            )
                        archive = paths.downloads / "nbs_ingested" / pdf.name
                        context.preflight([archive])
                        if archive.read_bytes() != private_sources[pdf].read_bytes():
                            raise ValueError(
                                "published archive changed; original preserved"
                            )
                        pdf.unlink()
                    except (OSError, ValueError) as exc:
                        cleanup_pending.append(f"{pdf}: {exc}")
    return DownloadIntakeResult(
        tuple(done), tuple(bad), tuple(no_lib), tuple(changed), tuple(cleanup_pending)
    )


def main(
    argv=None,
    *,
    paths: DownloadIntakePaths,
    title_checker=None,
    copy_file=None,
    write_queue=None,
    today=None,
) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--dir", type=Path, default=paths.downloads)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--keep", action="store_true", help="leave the downloads in place"
    )
    parser.add_argument("--root", type=Path)
    parser.add_argument("--queue-path", type=Path)
    parser.add_argument("--corpus-dir", type=Path)
    parser.add_argument("--library-root", type=Path)
    args = parser.parse_args(argv)
    selected = DownloadIntakePaths(
        args.queue_path
        if args.queue_path is not None
        else args.root / "pipeline/acquisition_queue.csv"
        if args.root is not None
        else paths.queue,
        args.corpus_dir
        if args.corpus_dir is not None
        else args.root / ".cache/corpus"
        if args.root is not None
        else paths.corpus,
        args.dir.expanduser(),
        args.library_root if args.library_root is not None else paths.library,
    )
    result = run_intake(
        selected,
        dry_run=args.dry_run,
        keep=args.keep,
        today=today,
        title_checker=title_checker,
        copy_file=copy_file,
        write_queue=write_queue,
    )
    print(f"filed {len(result.done)}" + (" (dry run)" if args.dry_run else ""))
    for line in result.done:
        print("  ok  ", line)
    for line in result.bad:
        print("  FAIL", line, "(left in place)")
    if result.no_library:
        print(
            "  library copy skipped (no library root / target path):",
            ", ".join(result.no_library),
        )
    if result.cleanup_pending:
        print(
            "  CLEANUP PENDING: files and queue are published; reconcile retained downloads:"
        )
        for line in result.cleanup_pending:
            print("  -", line)
    if result.done and not args.dry_run:
        print(
            "next: python3 src/nbs_ruralscan/schema_tools/verify_metadata.py verify  (DOI rows)"
        )
    return result.returncode
