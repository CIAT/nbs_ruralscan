#!/usr/bin/env python3
"""Key-level 3-way merge driver for register-style CSVs (one row per key, first column).

git calls:  git-merge-keycsv.py %O %A %B %P   (result written to %A)

Per key: unchanged on one side -> take the other side's row; added on one side -> keep it;
deleted on one side and unchanged on the other -> delete; changed differently on both sides
-> a real conflict: keep OURS for that row, list the key on stderr and exit 1 so git marks
the file conflicted. Row order: ours first, then rows only theirs added (append-only
registers stay append-only). Column set: ours (structure changes go through the manifest).
"""

from __future__ import annotations

import csv
import io
import sys


def _read(path: str) -> tuple[list[str], dict[str, dict], list[str]]:
    with open(path, newline="", encoding="utf-8") as f:
        text = f.read()
    if not text.strip():
        return [], {}, []
    rd = csv.DictReader(io.StringIO(text))
    cols = list(rd.fieldnames or [])
    rows: dict[str, dict] = {}
    order: list[str] = []
    for r in rd:
        k = r[cols[0]]
        if k not in rows:
            order.append(k)
        rows[k] = r
    return cols, rows, order


def merge(base_p: str, ours_p: str, theirs_p: str) -> tuple[str, list[str]]:
    _, base, _ = _read(base_p)
    cols, ours, ours_order = _read(ours_p)
    tcols, theirs, theirs_order = _read(theirs_p)
    cols = cols or tcols
    out: dict[str, dict] = {}
    conflicts: list[str] = []
    for k in ours_order + [k for k in theirs_order if k not in ours]:
        b, o, t = base.get(k), ours.get(k), theirs.get(k)
        if o == t:
            row = o
        elif o == b:
            row = t
        elif t == b:
            row = o
        else:
            row = o
            conflicts.append(k)
        if row is not None:
            out[k] = row
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    for r in out.values():
        w.writerow({c: r.get(c, "") for c in cols})
    return buf.getvalue(), conflicts


def main(argv: list[str]) -> int:
    base_p, ours_p, theirs_p = argv[1:4]
    path = argv[4] if len(argv) > 4 else ours_p
    text, conflicts = merge(base_p, ours_p, theirs_p)
    with open(ours_p, "w", newline="", encoding="utf-8") as f:
        f.write(text)
    if conflicts:
        sys.stderr.write(
            f"keycsv: {path}: {len(conflicts)} row(s) changed on both sides, kept ours: "
            + ", ".join(conflicts[:20])
            + "\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
