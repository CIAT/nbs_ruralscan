"""Hydrate selected corpus from read-only records, library copies and source adapters.

Prepare privately, publish coordinated outputs, preserve established routing and
source bytes. This is caught-error recovery under stable inputs and one writer,
not crash durability, a global lock, or remote synchronization.
"""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import csv
from dataclasses import dataclass
import hashlib
import io
import os
from pathlib import Path
import re
import urllib.parse
import urllib.request

from .acquisition_queue import _acquisition_workspace
from .integrity import copy_immutable, validate_source_id
from .source_publication import SourceSnapshot
from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths
from nbs_ruralscan.schema_tools.publication import (
    PublicationRecoveryError,
    _state,
    staged_publish,
)

_SNAPSHOT_EXTS = (".pdf", ".txt", ".html", ".md")
_BUNDLE_EXTS = (*_SNAPSHOT_EXTS, ".source.json", ".meta.json")


def library_root() -> Path | None:
    """Resolve the local OneDrive mirror of the SharePoint .../1_Projects/ folder."""
    env = os.environ.get("NBS_LIBRARY_ROOT")
    if env:
        return Path(env).expanduser()
    default = (
        Path.home()
        / "Library/CloudStorage/OneDrive-CGIAR/ClimateActionNetZero/1_Projects"
    )
    return default if default.exists() else None


def _github_raw(url: str) -> str | None:
    """github.com/<o>/<r>/blob/<ref>/<path> -> raw.githubusercontent.com/<o>/<r>/<ref>/<path>."""
    m = re.match(
        r"^https://github\.com/([^/]+)/([^/]+)/blob/(.+)$", (url or "").strip()
    )
    return (
        f"https://raw.githubusercontent.com/{m.group(1)}/{m.group(2)}/{m.group(3)}"
        if m
        else None
    )


def _fetch(url: str) -> bytes | None:
    """Fetch a URL (4 MB cap); None on any failure."""
    # paths copied from a browser may carry raw spaces ("R shiny app … .R"); encode them
    url = urllib.parse.quote(url, safe=":/?&=%#+@,;~")
    req = urllib.request.Request(url, headers={"User-Agent": "nbs-ruralscan-hydrate"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status != 200:
                return None
            return resp.read(4_000_000)
    except Exception:  # noqa: BLE001
        return None


def _cached(cache: Path, sid: str) -> bool:
    return any((cache / (sid + ext)).exists() for ext in _SNAPSHOT_EXTS)


def library_file(root: Path, relative: str) -> Path:
    if Path(relative).is_absolute() or ".." in relative.split("/") or "\\" in relative:
        raise ValueError("Library path must be relative without traversal")
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Library path escapes the selected library root")
    return path


@dataclass(frozen=True)
class HydrationPaths:
    sources: Path
    queue: Path
    corpus: Path
    archives: Path
    library: Path | None = None

    def __post_init__(self):
        for name in ("sources", "queue", "corpus", "archives", "library"):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, Path(os.path.abspath(value)))

    @classmethod
    def from_root(cls, root, *, corpus=None, archives=None, library=None):
        root = Path(os.path.abspath(root))
        return cls(
            root / "schema/registers/SRC_source_register.csv",
            root / "pipeline/acquisition_queue.csv",
            corpus if corpus is not None else root / ".cache/corpus",
            archives if archives is not None else root / "methodology/audits",
            library,
        )


@dataclass(frozen=True)
class HydrationResult:
    report: str
    changed: tuple[Path, ...]


def _rows(raw: bytes):
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
    cols = reader.fieldnames or []
    if "source_id" not in cols or len(cols) != len(set(cols)):
        raise ValueError("Hydration records have missing/duplicate columns")
    rows = list(reader)
    seen = set()
    for row in rows:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("Malformed hydration record")
        sid = row["source_id"].strip()
        if sid and sid in seen:
            raise ValueError(f"Duplicate hydration source_id: {sid}")
        seen.add(sid)
    return rows


def _prepare_queue(rows, root, nbs, cache, fetch, copy_input):
    copied = already = 0
    missing: list[str] = []
    pending: list[tuple[str, str]] = []
    for r in rows:
        sid = (r.get("source_id") or "").strip()
        status = (r.get("status") or "").strip().lower()
        if not sid or status == "duplicate":
            continue
        if status != "acquired":  # pending / unacquired — not in the library yet
            pending.append((sid, (r.get("blocker") or "not acquired").strip()))
            continue
        if _cached(cache, sid):
            already += 1
            continue
        lib_path = (r.get("target_library_path") or "").strip()
        url = (r.get("url") or "").strip()
        if not lib_path and url:
            # a code / web source (e.g. a tool's commit-pinned GitHub file) has no
            # library PDF: snapshot it as the SRC pass does — /blob/ -> raw .txt
            raw = _github_raw(url)
            data = fetch(raw or url)
            if data:
                (cache / (sid + (".txt" if raw else ".html"))).write_bytes(data)
                copied += 1
            else:
                missing.append(f"{sid} (fetch failed: {url})")
            continue
        if root is None or not lib_path:
            missing.append(f"{sid} (set NBS_LIBRARY_ROOT)" if root is None else sid)
            continue
        src_pdf = library_file(root, lib_path)
        if not src_pdf.exists():
            missing.append(sid)
            continue
        try:
            copy_input(src_pdf, cache / (sid + ".pdf"))
            copied += 1
        except Exception as e:  # noqa: BLE001
            print(f"  ! failed to copy {sid}: {e}")
            missing.append(sid)

    scope = nbs or "all NbS"
    print("")
    print(f"acquisition queue ({scope})")
    print(f"queue copied/fetched: {copied}")
    print(f"queue already cached: {already}")
    for sid, blocker in pending:
        print(f"SKIP {sid} - not acquired ({blocker})")
    if missing:
        print(f"queue MISSING from library: {len(missing)}")
        for sid in missing:
            print(f"  - {sid}")


def _prepare_sources(rows, paths, cache, fetch, copy_input, run_adapter):
    root = paths.library
    pdf_copied = pdf_already = code_fetched = code_already = skipped = 0
    pdf_missing: list[str] = []
    code_failed: list[str] = []

    for r in rows:
        sid = (r.get("source_id") or "").strip()
        if not sid:
            continue
        lib_path = (r.get("library_path") or "").strip()
        url = (r.get("url") or "").strip()
        kind = (r.get("source_kind") or "").strip().lower()
        cat = (r.get("source_category") or "").strip().lower()

        if lib_path:  # PDF from the SharePoint/OneDrive library
            if (cache / (sid + ".pdf")).exists():
                pdf_already += 1
                continue
            if root is None:
                pdf_missing.append(f"{sid} (set NBS_LIBRARY_ROOT)")
                continue
            src_pdf = library_file(root, lib_path)
            if not src_pdf.exists():
                pdf_missing.append(sid)
                continue
            try:
                copy_input(src_pdf, cache / (sid + ".pdf"))
                pdf_copied += 1
            except Exception as e:  # noqa: BLE001
                print(f"  ! failed to copy {sid}: {e}")
                pdf_missing.append(sid)
        elif re.fullmatch(r"wocat_[a-z0-9_]+_approach_\d+", sid):
            # Approach narratives are not technology impact questionnaires. Generic
            # HTML hydration loses the embedded narrative and cannot supply locators.
            if (cache / f"{sid}.md").exists():
                code_already += 1
                continue
            # Prefer the reviewed, tracked snapshot: a fresh clone should not depend
            # on the publisher continuing to serve the same selected version.
            expected = r.get("artifact_sha1", "")
            archived = next(
                (
                    path
                    for path in sorted(paths.archives.glob(f"*/{sid}.md"))
                    if expected
                    and hashlib.sha1(path.read_bytes()).hexdigest() == expected
                ),
                None,
            )
            if archived is not None:
                copy_input(archived, cache / f"{sid}.md")
                code_fetched += 1
                continue
            from nbs_ruralscan.ingest import wocat_approach

            try:
                run_adapter(
                    wocat_approach.acquire,
                    sid,
                    expected_sha1=r.get("artifact_sha1", ""),
                )
                code_fetched += 1
            except PublicationRecoveryError:
                raise
            except Exception as exc:
                print(f"  ! approach hydration failed {sid}: {exc}")
                code_failed.append(sid)
        elif url and (
            cat == "tool" or kind in ("website", "github")
        ):  # code/web snapshot
            if _cached(cache, sid):
                code_already += 1
                continue
            raw = _github_raw(url)
            data = fetch(raw or url)
            if not data:
                code_failed.append(sid)
                continue
            (cache / (sid + (".txt" if raw else ".html"))).write_bytes(data)
            code_fetched += 1
        else:
            skipped += (
                1  # no artifact source (e.g. a PDF not yet uploaded to the library)
            )

    # WOCAT transcripts: section-locator evidence verifies against `<sid>.md`, which the
    # adapter renders from the questionnaire JSON (never in the SharePoint library) —
    # re-acquire any that are missing (needs network; 2026-10-06)
    wocat_fetched = wocat_failed = 0
    wocat_ids = sorted(
        {
            r["source_id"]
            for r in rows
            if r["source_id"].startswith("wocat_")
            and re.match(r"wocat_\d+_", r["source_id"])
            and not (cache / f"{r['source_id']}.md").exists()
        }
    )
    if wocat_ids:
        from nbs_ruralscan.ingest import wocat as _wocat

        for sid in wocat_ids:
            try:
                run_adapter(_wocat.acquire, sid)
                wocat_fetched += 1
            except PublicationRecoveryError:
                raise
            except Exception:  # noqa: BLE001
                wocat_failed += 1

    print(f"library root       : {root}")
    print(f"PDF copied         : {pdf_copied}")
    print(f"WOCAT transcripts   : {wocat_fetched} fetched, {wocat_failed} failed")
    print(f"PDF already cached  : {pdf_already}")
    print(f"code/web fetched    : {code_fetched}")
    print(f"code/web cached     : {code_already}")
    print(f"no artifact source  : {skipped}")
    if pdf_missing:
        print(f"PDF missing from library: {len(pdf_missing)}")
        for sid in pdf_missing:
            print(f"  - {sid}")
    if code_failed:
        print(
            f"code/web fetch FAILED: {len(code_failed)} (check the SRC.url / network)"
        )
        for sid in code_failed:
            print(f"  - {sid}")


def run_hydration(
    paths: HydrationPaths,
    *,
    include_queue=False,
    queue_only=False,
    nbs=None,
    dry_run=False,
    fetch=None,
) -> HydrationResult:
    """Hydrate only selected corpus files; records/library/archives stay read-only."""
    fetch = fetch or _fetch
    if not queue_only and not paths.sources.exists():
        return HydrationResult(f"SRC register not found: {paths.sources}\n", ())
    raw_sources = paths.sources.read_bytes() if not queue_only else None
    raw_queue = (
        paths.queue.read_bytes()
        if (include_queue or queue_only) and paths.queue.exists()
        else None
    )
    sources = _rows(raw_sources) if raw_sources is not None else []
    queues = _rows(raw_queue) if raw_queue is not None else []
    # Historical --nbs behavior is exact whole-cell matching on queue only.
    queues = [r for r in queues if not nbs or (r.get("nbs_id") or "").strip() == nbs]
    acquired = [
        r for r in queues if (r.get("status") or "").strip().lower() == "acquired"
    ]
    ids = sorted(
        {
            r["source_id"].strip()
            for r in [*sources, *acquired]
            if r["source_id"].strip()
        }
    )
    for sid in ids:
        validate_source_id(sid)
    targets = [paths.corpus / (sid + ext) for sid in ids for ext in _BUNDLE_EXTS]
    context = SchemaBuildPaths(paths.corpus / "schema")
    context.preflight(targets)
    names = [str(p.resolve()).casefold() for p in targets]
    if len(names) != len(set(names)):
        raise ValueError("Hydration corpus destinations alias")
    corpus_key = str(paths.corpus.resolve()).casefold().rstrip(os.sep)
    for root in (paths.library, paths.archives):
        if root is not None:
            key = str(root.resolve()).casefold().rstrip(os.sep)
            if (
                key == corpus_key
                or key.startswith(corpus_key + os.sep)
                or corpus_key.startswith(key + os.sep)
            ):
                raise ValueError(
                    "Hydration corpus overlaps read-only library/archive root"
                )
    inputs = [paths.sources] if not queue_only else []
    if include_queue or queue_only:
        inputs.append(paths.queue)
    for r in sources:
        sid = r["source_id"].strip()
        if not sid:
            continue
        lib = (r.get("library_path") or "").strip()
        if (
            lib
            and paths.library is not None
            and not (paths.corpus / (sid + ".pdf")).exists()
        ):
            inputs.append(library_file(paths.library, lib))
    for r in acquired:
        sid = r["source_id"].strip()
        lib = (r.get("target_library_path") or "").strip()
        if sid and lib and paths.library is not None and not _cached(paths.corpus, sid):
            inputs.append(library_file(paths.library, lib))
    approach_ids = [
        r["source_id"].strip()
        for r in sources
        if re.fullmatch(r"wocat_[a-z0-9_]+_approach_\d+", r["source_id"].strip())
        and not (r.get("library_path") or "").strip()
        and not (paths.corpus / (r["source_id"].strip() + ".md")).exists()
    ]

    def archive_listing():
        return tuple(
            sorted(
                {p for sid in approach_ids for p in paths.archives.glob(f"*/{sid}.md")}
            )
        )

    archived = archive_listing()
    inputs.extend(archived)
    inputs = list(dict.fromkeys(inputs))
    for path in inputs:
        key = str(path.resolve()).casefold()
        if key == corpus_key or key.startswith(corpus_key + os.sep):
            raise ValueError("Hydration output overlaps read-only input")
    before = {p: _state(p) for p in [*targets, *inputs]}
    for path, raw in ((paths.sources, raw_sources), (paths.queue, raw_queue)):
        if raw is not None:
            state = before[path]
            if state is None or state[0] != hashlib.sha256(raw).hexdigest():
                raise ValueError(f"Hydration records changed while reading: {path}")

    def unchanged():
        context.preflight(targets)
        if archive_listing() != archived:
            raise ValueError("Hydration archive selection changed during preparation")
        for path, state in before.items():
            if _state(path) != state:
                raise ValueError(
                    f"Hydration input/output changed during preparation: {path}"
                )

    with _acquisition_workspace() as workspace:
        cache = workspace / "corpus"
        cache.mkdir()
        refresh = set()
        for path in targets:
            previous = before[path]
            if previous is not None:
                # Existing snapshots are only existence markers in the routing
                # pass. Avoid copying every cached PDF just to skip it. Adapter
                # sidecars can be read/replaced during missing-transcript repair.
                private = cache / path.name
                if path.name.endswith((".source.json", ".meta.json")):
                    private.write_bytes(path.read_bytes())
                    if hashlib.sha256(private.read_bytes()).hexdigest() != previous[0]:
                        raise ValueError(
                            f"Hydration input changed while copying: {path}"
                        )
                else:
                    private.touch()
        unchanged()

        def copy_input(source, destination):
            source = Path(source)
            if source not in before or _state(source) != before[source]:
                raise ValueError(f"Unstable or undeclared hydration input: {source}")
            copy_immutable(source, destination)
            state = before[source]
            if (
                state is None
                or hashlib.sha256(destination.read_bytes()).hexdigest() != state[0]
            ):
                raise ValueError(f"Hydration input changed while copying: {source}")

        def run_adapter(adapter, sid, **kwargs):
            # A failed/incomplete adapter must not leave partial output for the
            # enclosing batch to publish. Keep its work in an owned sub-workspace.
            with _acquisition_workspace() as adapter_cache:
                names = [sid + ext for ext in (".source.json", ".md", ".meta.json")]
                for name in names:
                    if (cache / name).exists():
                        (adapter_cache / name).write_bytes((cache / name).read_bytes())
                adapter(sid, adapter_cache, **kwargs)
                if {p.name for p in adapter_cache.iterdir()} != set(names):
                    raise ValueError(
                        f"Hydration adapter returned an incomplete bundle: {sid}"
                    )
                bodies = {
                    cache / name: (adapter_cache / name).read_bytes() for name in names
                }

                def validate_adapter_copy(stage):
                    if any(
                        (stage / path.name).read_bytes() != body
                        for path, body in bodies.items()
                    ):
                        raise ValueError("Hydration adapter copy differs")

                SourceSnapshot.capture(bodies).publish(bodies, validate_adapter_copy)
                refresh.update(paths.corpus / name for name in names)
            return cache / (sid + ".md")

        report = io.StringIO()
        with redirect_stdout(report):
            if not queue_only:
                _prepare_sources(sources, paths, cache, fetch, copy_input, run_adapter)
            if include_queue or queue_only:
                if raw_queue is None:
                    print(f"acquisition queue not found: {paths.queue}")
                else:
                    _prepare_queue(queues, paths.library, nbs, cache, fetch, copy_input)
        unchanged()
        if {p.name for p in cache.iterdir()} - {p.name for p in targets}:
            raise ValueError("Hydration adapter produced undeclared artifacts")
        outputs = []
        hashes = {}
        for path in targets:
            private = cache / path.name
            previous = before[path]
            if not private.exists() or (previous is not None and path not in refresh):
                continue
            digest = hashlib.sha256(private.read_bytes()).hexdigest()
            if previous is None or digest != previous[0]:
                outputs.append(path)
                hashes[path] = digest

        def validate(path):
            original = paths.corpus / path.name
            body = path.read_bytes()
            if hashlib.sha256(body).hexdigest() != hashes[original]:
                raise ValueError(f"Hydration publication bytes differ: {original}")
            if original == outputs[-1]:
                unchanged()  # Recheck read-only inputs after the whole render.

        def render(staged):
            unchanged()
            assert staged.output_root is not None
            for original in outputs:
                (staged.output_root / original.name).write_bytes(
                    (cache / original.name).read_bytes()
                )
            return []

        changed = (
            staged_publish(
                context,
                outputs,
                render,
                artifact_validators={p: validate for p in outputs},
                create_only_destinations=tuple(p for p in outputs if p not in refresh),
                dry_run=dry_run,
            )
            if outputs
            else []
        )
        if dry_run:
            report.write("DRY RUN: hydration validated; no selected files published\n")
        return HydrationResult(report.getvalue(), tuple(changed))


def main(argv=None, *, paths: HydrationPaths, fetch=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--queue", action="store_true", help="also hydrate acquired queue rows"
    )
    ap.add_argument("--nbs", help="restrict queue pass to one exact nbs_id cell")
    ap.add_argument("--root", type=Path, help="selected source-data root")
    ap.add_argument("--corpus-dir", type=Path)
    ap.add_argument("--archive-dir", type=Path)
    ap.add_argument(
        "--library-root",
        type=Path,
        help="root containing stored relative library paths",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="fetch/check privately without publishing corpus files",
    )
    args = ap.parse_args(argv)
    if args.root is not None:
        paths = HydrationPaths.from_root(args.root, library=paths.library)
    paths = HydrationPaths(
        paths.sources,
        paths.queue,
        args.corpus_dir or paths.corpus,
        args.archive_dir or paths.archives,
        args.library_root or paths.library,
    )
    result = run_hydration(
        paths, include_queue=args.queue, nbs=args.nbs, dry_run=args.dry_run, fetch=fetch
    )
    print(result.report, end="")
    return 0
