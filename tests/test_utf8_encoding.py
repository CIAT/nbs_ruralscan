"""Guard against the Windows cp1252 'charmap' bug (issue #90).

On Windows the default text encoding is cp1252, not UTF-8 — so any `open()` /
`read_text()` / `write_text()` without an explicit `encoding="utf-8"` crashes with a
charmap error when the file carries non-ASCII (the register has °, em-dashes, and
multilingual quotes). The QA "Apply decisions & rebuild" path (review_server → generate)
hit exactly this. This test fails if any unencoded text I/O reappears in the package.
"""

import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "nbs_ruralscan"

# text I/O calls that MUST carry encoding="utf-8" (binary rb/wb + pdf libs are exempt)
_PATTERNS = [
    re.compile(r"\.open\(\s*newline="),  # csv reads/writes
    re.compile(r"\.read_text\("),
    re.compile(r"\.write_text\("),
    re.compile(r"[^.\w]open\([^)]*['\"][rwa]\+?['\"]"),  # open(path, "w"/"r"/"a")
]
_BINARY = re.compile(r"['\"](rb|wb|ab)['\"]")


def _calls_missing_encoding(text: str) -> list[str]:
    """Return source lines with a text-I/O call that lacks encoding= (paren-matched)."""
    bad = []
    for pat in _PATTERNS:
        for m in pat.finditer(text):
            # paren-match from the opening "(" of this call
            op = text.index("(", m.start())
            depth, j = 1, op + 1
            while j < len(text) and depth:
                depth += {"(": 1, ")": -1}.get(text[j], 0)
                j += 1
            span = text[m.start() : j]
            if "encoding=" in span or _BINARY.search(span):
                continue
            bad.append(span.replace("\n", " ").strip()[:90])
    return bad


def test_all_text_io_declares_utf8():
    offenders = {}
    for py in SRC.rglob("*.py"):
        miss = _calls_missing_encoding(py.read_text(encoding="utf-8"))
        if miss:
            offenders[str(py.relative_to(SRC))] = miss
    assert not offenders, (
        "text I/O without encoding='utf-8' (Windows cp1252 charmap risk, issue #90):\n"
        + "\n".join(f"  {f}: {v}" for f, v in offenders.items())
    )
