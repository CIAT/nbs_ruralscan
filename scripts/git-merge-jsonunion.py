#!/usr/bin/env python3
"""Key-union merge driver for hand-maintained JSON objects keyed by id
(e.g. pipeline/t4_audit/*/review_followups.json). Never "take theirs" here: that silently
drops the other side's entries.

Per key: same logic as git-merge-keycsv.py (one side unchanged -> the other; both changed
differently -> keep ours and exit 1). Output: indent=2, ensure_ascii=False, trailing newline.
"""

from __future__ import annotations

import json
import sys


def _load(p: str) -> dict:
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f) or {}
    except (OSError, json.JSONDecodeError):
        return {}


def main(argv: list[str]) -> int:
    base, ours, theirs = (_load(p) for p in argv[1:4])
    out: dict = {}
    conflicts = []
    for k in list(ours) + [k for k in theirs if k not in ours]:
        b, o, t = base.get(k), ours.get(k), theirs.get(k)
        if o == t:
            v = o
        elif o == b:
            v = t
        elif t == b:
            v = o
        else:
            v = o
            conflicts.append(k)
        if v is not None:
            out[k] = v
    with open(argv[2], "w", encoding="utf-8") as f:
        f.write(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    if conflicts:
        sys.stderr.write(
            f"jsonunion: {len(conflicts)} key(s) changed on both sides, kept ours\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
