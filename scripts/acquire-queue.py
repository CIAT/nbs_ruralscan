#!/usr/bin/env python3
"""Acquire pending PDF queue rows into selected cache and team library.

Existing commands/defaults remain available. Use --root, --corpus-dir,
--library-dir and --library-prefix to select independent records/storage;
--dry-run performs downloads privately without publishing selected files.
"""

from __future__ import annotations

import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from nbs_ruralscan.ingest import acquisition_queue as queue
from nbs_ruralscan.ingest.acquire import AcquireError as AcquireError, acquire
from nbs_ruralscan.ingest.artifact_publication import (
    PairSnapshot as PairSnapshot,
    publish_pair,
)
from nbs_ruralscan.ingest.integrity import (
    atomic_write,
    copy_immutable,
    pdf_title_error,
    validate_source_id as validate_source_id,
)
from nbs_ruralscan.schema_tools.publication import (
    PublicationRecoveryError as PublicationRecoveryError,
)

# Retain importable compatibility helpers and their existing injectable dependencies.
requests, time, tempfile, shutil = (
    queue.requests,
    queue.time,
    queue.tempfile,
    queue.shutil,
)
_acquisition_workspace = queue._acquisition_workspace
UA = queue.UA
ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache/corpus"
LIB_ROOT = pathlib.Path(
    os.environ.get("NBS_LIBRARY_ROOT")
    or pathlib.Path.home()
    / "Library/CloudStorage/OneDrive-CGIAR/ClimateActionNetZero/1_Projects"
)
LIB_REL = "D591_Rural-Scan_NBS/2_Technical_&_Data/library"


def _acquire(sid, url, dest, citation=None, identity_holds=None):
    return queue._acquire(
        sid,
        url,
        dest,
        citation,
        identity_holds,
        acquire_fn=acquire,
        publish_fn=publish_pair,
        workspace_fn=_acquisition_workspace,
        title_check=pdf_title_error,
    )


def _candidates(row, wayback):
    return queue._candidates(row, wayback, headers=UA, request_get=requests.get)


def main(argv=None):
    return queue.main(
        argv,
        paths=queue.AcquisitionPaths(
            ROOT / "pipeline/acquisition_queue.csv", CACHE, LIB_ROOT / LIB_REL, LIB_REL
        ),
        acquire_candidate=_acquire,
        candidates=_candidates,
        copy_library=copy_immutable,
        write_queue=atomic_write,
    )


if __name__ == "__main__":
    raise SystemExit(main())
