"""Distinguish retired CIAT working copies from stand-alone replay directories."""

from pathlib import Path
import subprocess

QUEUE = "https://ruralscan.github.io/method/#review-queue"
DESTINATION = "https://github.com/RuralScan/evidence"
NOTICE = f"CIAT evidence writes are retired. Submit findings at {QUEUE} or use {DESTINATION}."


def retired(root: Path) -> bool:
    if (root / ".ciat-evidence-readonly").is_file():
        return True
    # Also protect older worktrees served with the updated review server.
    if not (root / ".git").exists():
        return False
    remotes = subprocess.run(
        ["git", "-C", str(root), "remote", "-v"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return any(
        url.lower()
        .removesuffix(".git")
        .rstrip("/")
        .endswith(("/ciat/nbs_ruralscan", ":ciat/nbs_ruralscan"))
        for line in remotes.splitlines()
        for url in line.split()[1:2]
    )


def require_writable(root: Path) -> None:
    if retired(root):
        raise ValueError(NOTICE)
