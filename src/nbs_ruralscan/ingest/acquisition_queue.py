"""Prepare and publish a selected PDF acquisition batch with explicit paths.

Stable inputs and one writer are required. Caught local failures roll back owned
outputs; this is not crash-safe, reader-atomic or a remote library transaction.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import hashlib
from contextlib import contextmanager
import json
import io
import os
import pathlib
import re
import shutil
import time
import tempfile

from nbs_ruralscan.ingest.acquire import AcquireError, acquire
from nbs_ruralscan.ingest.artifact_publication import PairSnapshot, publish_pair
from nbs_ruralscan.ingest.integrity import (
    atomic_write,
    copy_immutable,
    pdf_title_error,
    validate_source_id,
    validate_body,
)
from urllib.parse import urljoin
from nbs_ruralscan.schema_tools.publication import (
    PublicationRecoveryError,
    staged_publish,
    _state,
)
from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths

import requests

UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh) nbs-ruralscan evidence pipeline (p.steward@cgiar.org)"
}


@contextmanager
def _acquisition_workspace():
    # Resolve only this owned system-temp path (e.g. /var -> /private on macOS).
    directory = pathlib.Path(
        tempfile.mkdtemp(prefix="ruralscan-acquisition-")
    ).resolve()
    retain = False
    try:
        yield directory
    except PublicationRecoveryError as exc:
        retain = True
        exc.add_note(f"Temporary acquisition files retained at {directory}")
        raise
    finally:
        if not retain:
            try:
                shutil.rmtree(directory)
            except Exception as exc:
                raise PublicationRecoveryError(
                    directory, [f"Temporary acquisition cleanup failed: {exc}"]
                ) from exc


def _acquire(
    sid: str,
    url: str,
    dest: pathlib.Path,
    citation: str | None = None,
    identity_holds: list[str] | None = None,
    *,
    acquire_fn=None,
    publish_fn=None,
    workspace_fn=None,
    title_check=None,
) -> bool:
    # A failed retry must never destroy an existing source. Acquire into an isolated
    # directory and validate with the PDF parser before promoting the artifact.
    import fitz

    acquire_fn = acquire_fn or acquire
    publish_fn = publish_fn or publish_pair
    workspace_fn = workspace_fn or _acquisition_workspace
    title_check = title_check or pdf_title_error

    def identity_matches(path: pathlib.Path) -> bool:
        problem = title_check(path, citation) if citation is not None else None
        if problem and identity_holds is not None:
            identity_holds.append(f"{url}: {problem}")
        return problem is None

    try:
        validate_source_id(sid)
        snapshot = PairSnapshot.capture(dest, dest.with_suffix(".meta.json"))
        if snapshot.sidecar_state is not None and snapshot.artifact_state is None:
            raise AcquireError("Existing provenance without requested PDF artifact")
        if dest.exists():
            if not identity_matches(dest):
                return False
            acquire_fn(sid, url, kind="pdf", corpus_dir=dest.parent)
            with fitz.open(dest) as doc:
                readable = doc.page_count > 0
            snapshot.assert_unchanged()
            return readable
        with workspace_fn() as tmp:
            result = acquire_fn(sid, url, kind="pdf", corpus_dir=tmp)
            if result.artifact_path is None or result.meta_path is None:
                return False
            with fitz.open(result.artifact_path) as doc:
                if doc.page_count == 0:
                    return False
            if not identity_matches(result.artifact_path):
                return False
            publish_fn(
                snapshot,
                result.artifact_path.read_bytes(),
                result.meta_path.read_bytes(),
                source_id=sid,
                url=url,
                kind="pdf",
            )
        return True
    except PublicationRecoveryError:
        raise  # Recovery requires intervention; never continue to another URL.
    except (AcquireError, ValueError, RuntimeError, OSError):
        return False


def _candidates(r: dict, wayback: dict, *, headers=None, request_get=None) -> list[str]:
    headers = headers if headers is not None else UA
    request_get = request_get or requests.get
    out: list[str] = []
    if r["source_id"] in wayback:
        out.append(wayback[r["source_id"]])
    if r.get("doi") and r.get("doi_verified") == "true":
        try:
            u = request_get(
                f"https://api.unpaywall.org/v2/{r['doi']}?email=p.steward@cgiar.org",
                timeout=30,
            ).json()
            locs = (
                [u.get("best_oa_location")] if u.get("best_oa_location") else []
            ) + (u.get("oa_locations") or [])
            for loc in locs:
                if loc and loc.get("url_for_pdf") and loc["url_for_pdf"] not in out:
                    out.append(loc["url_for_pdf"])
        except Exception:
            pass
    for url in [r.get("url", "")] + list(out):
        if not url or url.lower().endswith(".pdf"):
            continue
        try:
            h = request_get(url, headers=headers, timeout=40, allow_redirects=True)
            if "html" not in h.headers.get("content-type", ""):
                continue
            m = re.search(
                r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)',
                h.text,
                re.I,
            ) or re.search(
                r'content=["\']([^"\']+)["\'][^>]+name=["\']citation_pdf_url["\']',
                h.text,
                re.I,
            )
            links = (
                [m.group(1)]
                if m
                else re.findall(r'href=["\']([^"\']+\.pdf[^"\']*)', h.text, re.I)[:3]
            )
            for link in links:
                full = urljoin(h.url, link)
                if full not in out:
                    out.append(full)
        except Exception:
            pass
    return out


def _prepare_rows(
    rows,
    cols,
    a,
    *,
    queue_path,
    corpus,
    mirror,
    original_mirror,
    library_prefix,
    wayback,
    acquire_candidate,
    candidates,
    copy_library,
    write_queue,
):
    import fitz  # noqa: WPS433

    log: list[tuple[str, str, str]] = []
    acquired_urls = {}
    for r in rows:
        if (
            (r["date_added"] != a.date and not a.all_dates)
            or r["status"] != "pending"
            or a.nbs not in {token.strip() for token in r["nbs_id"].split("|")}
        ):
            continue
        sid = r["source_id"]
        try:
            validate_source_id(sid)
        except ValueError as exc:
            log.append((sid, "fail", str(exc)))
            continue
        if "HUMAN CHECK" in (r["blocker"] or "") or "paywalled (verified" in (
            r["blocker"] or ""
        ):
            log.append((sid, "skip", "human / verified paywalled"))
            continue
        dest = corpus / f"{sid}.pdf"
        url = (r["url"] or "").strip()
        got = None
        identity_holds: list[str] = []
        citation = r.get("citation", "")
        if url and not (
            url.startswith("https://doi.org/") and "researchgate" not in url
        ):
            if acquire_candidate(sid, url, dest, citation, identity_holds):
                got = url
        if not got:
            for cand in candidates(r, wayback):
                if acquire_candidate(sid, cand, dest, citation, identity_holds):
                    got = cand
                    break
                time.sleep(0.5)
        if not got:
            if identity_holds:
                r["blocker"] = "document identity hold — " + "; ".join(
                    dict.fromkeys(identity_holds)
                )
                log.append((sid, "fail", r["blocker"]))
                continue
            reason = (
                "no URL/DOI route"
                if not (url or r.get("doi"))
                else "no candidate URL yielded a PDF (landing page / 403 / no Unpaywall copy)"
            )
            r["blocker"] = (
                r["blocker"]
                or f"tool acquisition failed — {reason}; human browser download / OA web-search recovery"
            )
            log.append((sid, "fail", reason))
            continue
        acquired_urls[sid] = got
        identity_problem = pdf_title_error(dest, r.get("citation", ""))
        if identity_problem:
            r["blocker"] = f"document identity hold — {identity_problem}"
            log.append((sid, "fail", r["blocker"]))
            continue
        try:
            with fitz.open(dest) as d:
                txt = "".join(d[i].get_text() for i in range(min(3, len(d))))
                npages = len(d)
        except Exception as e:  # noqa: BLE001
            log.append((sid, "fail", f"unreadable PDF: {e}"))
            continue
        ocr = len(txt.strip()) < 200
        try:
            copy_library(dest, mirror / f"{sid}.pdf")
        except OSError as exc:
            r["blocker"] = "library copy held — " + str(exc).replace(
                str(mirror / f"{sid}.pdf"), str(original_mirror / f"{sid}.pdf")
            )
            log.append((sid, "fail", r["blocker"]))
            continue
        r["status"] = "acquired"
        r["target_library_path"] = "/".join(
            p for p in (library_prefix, a.library_subdir, f"{sid}.pdf") if p
        )
        r["url"] = got
        if ocr:
            r["blocker"] = "needs_ocr (scanned PDF, no text layer)"
        r["note"] = (
            r["note"]
            + f"; acquired {a.date} by acquire-queue.py ({npages} pp{', NO TEXT LAYER' if ocr else ''}) → cache + SharePoint mirror"
        ).strip("; ")
        log.append((sid, "ok", f"{npages} pp{' OCR' if ocr else ''}"))
        time.sleep(1.0)
    buffer = io.StringIO(newline="")
    w = csv.DictWriter(buffer, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    write_queue(queue_path, buffer.getvalue().encode("utf-8"))
    return log, acquired_urls


def _relative_label(value: str, label: str) -> str:
    if (
        "\\" in value
        or pathlib.PurePosixPath(value).is_absolute()
        or ".." in value.split("/")
    ):
        raise ValueError(f"{label} must be a relative path without '..' or backslashes")
    return value.strip("/")


@dataclass(frozen=True)
class AcquisitionPaths:
    queue: pathlib.Path
    corpus: pathlib.Path
    library: pathlib.Path
    library_prefix: str

    def __post_init__(self):
        for name in ("queue", "corpus", "library"):
            object.__setattr__(
                self, name, pathlib.Path(os.path.abspath(getattr(self, name)))
            )
        object.__setattr__(
            self,
            "library_prefix",
            _relative_label(self.library_prefix, "library prefix"),
        )

    @classmethod
    def from_root(cls, root, *, library, library_prefix, corpus=None):
        root = pathlib.Path(root).resolve()
        return cls(
            root / "pipeline/acquisition_queue.csv",
            corpus if corpus is not None else root / ".cache/corpus",
            library,
            library_prefix,
        )

    def mirror(self, subdir):
        subdir = _relative_label(subdir, "library subdirectory")
        mirror = self.library / subdir
        if not mirror.resolve().is_relative_to(self.library.resolve()):
            raise ValueError("library subdirectory escapes the team library")
        if not mirror.is_dir():
            raise ValueError(f"library mirror missing: {mirror}")
        return mirror


@dataclass(frozen=True)
class AcquisitionResult:
    log: tuple[tuple[str, str, str], ...]
    changed: tuple[pathlib.Path, ...]


def _queue_rows(raw):
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
    cols = list(reader.fieldnames or [])
    required = {
        "source_id",
        "date_added",
        "status",
        "nbs_id",
        "url",
        "blocker",
        "note",
        "target_library_path",
    }
    if len(cols) != len(set(cols)) or not required.issubset(cols):
        raise ValueError("Acquisition queue has duplicate/missing required columns")
    rows = list(reader)
    seen = set()
    for row in rows:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("Acquisition queue has a malformed row")
        sid = row["source_id"]
        if not sid.strip() or sid in seen:
            raise ValueError(
                f"Acquisition queue has a blank/duplicate source_id: {sid!r}"
            )
        seen.add(sid)
    return rows, cols


def run_acquisition(
    paths: AcquisitionPaths,
    *,
    date: str,
    nbs: str,
    library_subdir: str,
    all_dates: bool = False,
    wayback_path=None,
    dry_run: bool = False,
    acquire_candidate=None,
    candidates=None,
    copy_library=None,
    write_queue=None,
) -> AcquisitionResult:
    """Prepare privately, then publish cache/library files and finally the queue.

    Valid per-row holds are recorded together with any valid cache they acquired.
    Observed input/output drift aborts publication. Local rollback does not undo
    remote synchronization and is not a crash-safe transaction or writer lock.
    """
    from types import SimpleNamespace

    acquire_candidate = acquire_candidate or _acquire
    candidates = candidates or _candidates
    copy_library = copy_library or copy_immutable
    write_queue = write_queue or atomic_write
    mirror = paths.mirror(library_subdir)
    library_subdir = _relative_label(library_subdir, "library subdirectory")
    raw_queue = paths.queue.read_bytes()
    rows, cols = _queue_rows(raw_queue)
    wayback_file = pathlib.Path(os.path.abspath(wayback_path)) if wayback_path else None
    raw_wayback = wayback_file.read_bytes() if wayback_file else None
    wayback = json.loads(raw_wayback.decode("utf-8")) if raw_wayback is not None else {}
    if not isinstance(wayback, dict) or any(
        not isinstance(k, str) or not isinstance(v, str) for k, v in wayback.items()
    ):
        raise ValueError("Wayback input must map source IDs to URL strings")
    selected = {}
    for row in rows:
        if (
            (row["date_added"] != date and not all_dates)
            or row["status"] != "pending"
            or nbs not in {part.strip() for part in row["nbs_id"].split("|")}
            or "HUMAN CHECK" in row["blocker"]
            or "paywalled (verified" in row["blocker"]
        ):
            continue
        try:
            validate_source_id(row["source_id"])
        except ValueError:
            continue  # Original row-level failure; untouched historical IDs survive.
        selected[row["source_id"]] = row
    targets = [paths.queue]
    for sid in selected:
        targets.extend(
            [
                paths.corpus / f"{sid}.pdf",
                paths.corpus / f"{sid}.meta.json",
                mirror / f"{sid}.pdf",
            ]
        )
    root = pathlib.Path(os.path.commonpath([p.parent for p in targets]))
    context = SchemaBuildPaths(root / "schema")
    context.preflight(targets)
    canonical = [str(p.resolve()).casefold() for p in targets]
    if len(canonical) != len(set(canonical)):
        raise ValueError("Acquisition destinations alias each other")
    corpus_key, library_key = (
        str(p.resolve()).casefold().rstrip(os.sep)
        for p in (paths.corpus, paths.library)
    )
    if (
        corpus_key == library_key
        or corpus_key.startswith(library_key + os.sep)
        or library_key.startswith(corpus_key + os.sep)
    ):
        raise ValueError("Acquisition corpus and library roots overlap")
    queue_key = str(paths.queue.resolve()).casefold()
    if any(
        queue_key == k or queue_key.startswith(k + os.sep)
        for k in (corpus_key, library_key)
    ):
        raise ValueError("Acquisition queue overlaps corpus/library")
    if wayback_file and str(wayback_file.resolve()).casefold() in canonical:
        raise ValueError("Acquisition destination overlaps Wayback input")
    guarded = [*targets, *([wayback_file] if wayback_file else [])]
    before = {p: _state(p) for p in guarded}
    queue_state = before[paths.queue]
    if queue_state is None or queue_state[0] != hashlib.sha256(raw_queue).hexdigest():
        raise ValueError("Acquisition queue changed while reading")
    if wayback_file is not None and raw_wayback is not None:
        wayback_state = before[wayback_file]
        if (
            wayback_state is None
            or wayback_state[0] != hashlib.sha256(raw_wayback).hexdigest()
        ):
            raise ValueError("Wayback input changed while reading")

    def unchanged():
        context.preflight(targets)
        for path, state in before.items():
            if _state(path) != state:
                raise ValueError(
                    f"Acquisition input/output changed during preparation: {path}"
                )

    with _acquisition_workspace() as workspace:
        working = {paths.queue: workspace / "queue.csv"}
        for sid in selected:
            working[paths.corpus / f"{sid}.pdf"] = workspace / "cache" / f"{sid}.pdf"
            working[paths.corpus / f"{sid}.meta.json"] = (
                workspace / "cache" / f"{sid}.meta.json"
            )
            working[mirror / f"{sid}.pdf"] = workspace / "library" / f"{sid}.pdf"
        for original, private in working.items():
            private.parent.mkdir(parents=True, exist_ok=True)
            original_state = before[original]
            if original_state is not None:
                shutil.copy2(original, private)
                if (
                    hashlib.sha256(private.read_bytes()).hexdigest()
                    != original_state[0]
                ):
                    raise ValueError(
                        f"Acquisition input changed while copying: {original}"
                    )
        unchanged()
        a = SimpleNamespace(
            date=date, nbs=nbs, all_dates=all_dates, library_subdir=library_subdir
        )
        log, acquired_urls = _prepare_rows(
            rows,
            cols,
            a,
            queue_path=working[paths.queue],
            corpus=workspace / "cache",
            mirror=workspace / "library",
            original_mirror=mirror,
            library_prefix=paths.library_prefix,
            wayback=wayback,
            acquire_candidate=acquire_candidate,
            candidates=candidates,
            copy_library=copy_library,
            write_queue=write_queue,
        )
        unchanged()
        # Held malformed originals are unchanged inputs, never republished outputs.
        outputs = []
        for path in targets:
            previous = before[path]
            if (
                path != paths.queue
                and working[path].exists()
                and (
                    previous is None
                    or hashlib.sha256(working[path].read_bytes()).hexdigest()
                    != previous[0]
                )
            ):
                outputs.append(path)
        outputs.append(paths.queue)  # Queue visibility follows every artifact install.
        output_set = set(outputs)

        def staged_file(original, stage):
            return (
                stage / original.relative_to(root)
                if original in output_set
                else working[original]
            )

        def check_cache(sid, stage):
            body = staged_file(paths.corpus / f"{sid}.pdf", stage).read_bytes()
            validate_body(body, "pdf")
            record = json.loads(
                staged_file(paths.corpus / f"{sid}.meta.json", stage).read_text(
                    encoding="utf-8"
                )
            )
            expected = {
                "source_id": sid,
                "url": acquired_urls.get(sid),
                "kind": "pdf",
                "sha1": hashlib.sha1(body).hexdigest(),
                "bytes": len(body),
                "commit_sha": None,
            }
            if (
                not acquired_urls.get(sid)
                or not isinstance(record, dict)
                or any(record.get(k) != v for k, v in expected.items())
            ):
                raise ValueError(f"Acquired artifact/provenance mismatch: {sid}")
            problem = pdf_title_error(
                staged_file(paths.corpus / f"{sid}.pdf", stage),
                selected[sid].get("citation", ""),
            )
            if problem:
                raise ValueError(f"Acquired document identity hold: {sid}: {problem}")

        validators = {}
        for sid in selected:
            for original in (
                paths.corpus / f"{sid}.pdf",
                paths.corpus / f"{sid}.meta.json",
                mirror / f"{sid}.pdf",
            ):
                if original not in output_set:
                    continue

                def validate(path, *, sid=sid, original=original):
                    stage = path
                    for _ in original.relative_to(root).parts:
                        stage = stage.parent
                    check_cache(sid, stage)
                    if (
                        original.parent == mirror
                        and path.read_bytes()
                        != staged_file(paths.corpus / f"{sid}.pdf", stage).read_bytes()
                    ):
                        raise ValueError(
                            f"Library copy differs from cached artifact: {sid}"
                        )

                validators[original] = validate

        def render(staged):
            unchanged()  # Do not adopt changes made before the publisher's snapshot.
            assert staged.output_root is not None
            for original in outputs:
                target = staged.output_root / original.relative_to(root)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(working[original], target)
            return []

        changed = staged_publish(
            context,
            outputs,
            render,
            artifact_validators=validators,
            create_only_destinations=tuple(p for p in outputs if p != paths.queue),
            dry_run=dry_run,
        )
        return AcquisitionResult(tuple(log), tuple(changed))


def main(
    argv=None,
    *,
    paths: AcquisitionPaths,
    acquire_candidate=None,
    candidates=None,
    copy_library=None,
    write_queue=None,
) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--date", required=True)
    ap.add_argument("--nbs", required=True)
    ap.add_argument("--library-subdir", required=True)
    ap.add_argument("--wayback", default="")
    ap.add_argument("--all-dates", action="store_true")
    ap.add_argument("--root", type=pathlib.Path)
    ap.add_argument("--corpus-dir", type=pathlib.Path)
    ap.add_argument(
        "--library-dir",
        type=pathlib.Path,
        help="Physical team library root, independent of stored prefix",
    )
    ap.add_argument(
        "--library-prefix", help="Relative prefix recorded in target_library_path"
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Run downloads/checks privately without publishing selected files",
    )
    a = ap.parse_args(argv)
    paths = AcquisitionPaths(
        a.root / "pipeline/acquisition_queue.csv"
        if a.root is not None
        else paths.queue,
        a.corpus_dir
        if a.corpus_dir is not None
        else (a.root / ".cache/corpus" if a.root is not None else paths.corpus),
        a.library_dir if a.library_dir is not None else paths.library,
        a.library_prefix if a.library_prefix is not None else paths.library_prefix,
    )
    try:
        paths.mirror(a.library_subdir)
    except ValueError as exc:
        ap.error(str(exc))
    try:
        result = run_acquisition(
            paths,
            date=a.date,
            nbs=a.nbs,
            library_subdir=a.library_subdir,
            all_dates=a.all_dates,
            wayback_path=a.wayback or None,
            dry_run=a.dry_run,
            acquire_candidate=acquire_candidate,
            candidates=candidates,
            copy_library=copy_library,
            write_queue=write_queue,
        )
    except (OSError, ValueError) as exc:
        print(f"ACQUISITION FAILED: {exc}")
        return 1
    from collections import Counter

    if a.dry_run:
        print("DRY RUN: acquisition batch validated; no selected files published")
    print(Counter(s for _, s, _ in result.log))
    for sid, status, message in result.log:
        if status != "ok":
            print(f"  [{status}] {sid}: {message}")
    return 0
