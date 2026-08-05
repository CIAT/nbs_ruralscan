"""Guard against the Windows `python3` Store-alias bug (issue #212).

A Windows venv contains `python.exe` only — no `python3.exe` (POSIX venvs add that as a
symlink). So `uv run python3 …` cannot resolve `python3` inside the environment, falls
through to PATH, and hits the Microsoft Store App-Execution-Alias stub, which prints
"Python was not found; run without arguments to install from the Microsoft Store" and
exits non-zero. That broke the QA "Apply & submit to main" flow for a Windows reviewer
(review_server → /api/submit → scripts/submit-review.sh) while passing on macOS/Linux/CI.

These shell scripts are executed by the review server and the git merge driver, so they
must invoke `python`, never `python3`. A bare `python3` outside uv is unsafe for the same
reason — `command -v python3` *finds* the stub, so a fallback must verify the interpreter
actually runs rather than trust that it exists.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# `python3` as an EXECUTED command. `command -v python3` / `which python3` are probes, not
# invocations — a fallback may legitimately test for python3, it just may not assume it.
_UV_RUN_PYTHON3 = re.compile(r"\buv\s+run\s+python3\b")
_PYTHON3_COMMAND = re.compile(r"(?:^|[;&|(]|\$\()\s*python3\b")
_PROBE = re.compile(r"(?:command\s+-v|which|type)\s+python3\b")


def _offending_lines(text: str) -> list[str]:
    bad = []
    for i, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0]  # ignore comments
        if _PROBE.search(line):
            continue
        if _UV_RUN_PYTHON3.search(line) or _PYTHON3_COMMAND.search(line):
            bad.append(f"L{i}: {raw.strip()[:90]}")
    return bad


def test_shell_scripts_do_not_invoke_python3():
    offenders = {}
    for sh in sorted(ROOT.rglob("*.sh")):
        if ".venv" in sh.parts:
            continue
        miss = _offending_lines(sh.read_text(encoding="utf-8"))
        if miss:
            offenders[str(sh.relative_to(ROOT))] = miss
    assert not offenders, (
        "shell scripts must invoke `python`, not `python3` — `python3` is unresolvable in "
        "a Windows venv and hits the MS Store alias stub (issue #212):\n"
        + "\n".join(f"  {f}: {v}" for f, v in offenders.items())
    )
