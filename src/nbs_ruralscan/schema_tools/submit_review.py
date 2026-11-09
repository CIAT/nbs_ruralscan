"""Headless apply of the local QA decisions — the non-UI half of the dashboard's
"Apply decisions & rebuild", for scripts/submit-review.sh.

Reads the per-reviewer decision store (pipeline/review/decisions.json), reduces it to
CONSENSUS decisions (a flag is applied only when every reviewer who decided it agrees; a
disagreement is left as a conflict and skipped), applies them to the CURRENT registers via
`apply_decisions`, and regenerates the JSON. Because it runs against whatever EV rows exist
*now*, it applies surgically — so a reviewer whose local branch drifted from main never
reverts other people's rows (the recurring pain that buried tiny review edits in 50k-line
generated-JSON churn + stale-branch reverts).

CLI: uv run python -m nbs_ruralscan.schema_tools.submit_review [--ship HANDLE --auto]

For a local snapshot, --root PATH replays and rebuilds there. The replay(root) API
only applies review/clarification records; it never builds artifacts or submits Git
changes. Replay stages its three records and rolls back caught installation
failures. Artifact rebuilding remains separate; use an independent copy.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path

from nbs_ruralscan.schema_tools.review_local import read_decisions, review_pair_lock
from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths
from nbs_ruralscan.schema_tools.generate import generate
from nbs_ruralscan.schema_tools.publication import staged_publish
from nbs_ruralscan.schema_tools.review import (
    ReviewFiles,
    apply_decisions,
    check_review_destinations,
)

ROOT = Path(__file__).resolve().parents[3]


def _load_store(path: Path) -> dict:
    return read_decisions(path)[0]


def consensus_decisions(store: dict) -> tuple[dict, list[str]]:
    """Reduce the (evidence_id × reviewer) store to a flat {evidence_id: {...}} of AGREED
    decisions + a list of conflicted evidence_ids. Mirrors the dashboard /api/apply logic."""
    decisions: dict = {}
    conflicts: list[str] = []
    for eid, byrev in store.items():
        decs = {rv: v for rv, v in byrev.items() if (v.get("decision") or "").strip()}
        if not decs:
            continue
        vals = {v["decision"] for v in decs.values()}
        if len(vals) == 1:
            entry = {
                "decision": next(iter(vals)),
                "reason": ";".join(
                    sorted(
                        {v.get("reason", "") for v in decs.values() if v.get("reason")}
                    )
                ),
                "note": " | ".join(
                    v.get("note", "") for v in decs.values() if v.get("note")
                ),
                "reviewer": ",".join(sorted(decs.keys())),
            }
            # a `reclassify` decision carries the target claim_scope + taxon — preserve them
            # through the consensus reduction so apply_decisions can retag the row.
            _tax = next((v.get("taxon") for v in decs.values() if v.get("taxon")), "")
            _cs = next(
                (v.get("claim_scope") for v in decs.values() if v.get("claim_scope")),
                "",
            )
            if _tax:
                entry["taxon"] = _tax
            if _cs:
                entry["claim_scope"] = _cs
            decisions[eid] = entry
        else:
            conflicts.append(eid)
    return decisions, conflicts


@dataclass(frozen=True)
class ReplayResult:
    clarification_count: int
    applied: dict | None
    conflicts: tuple[str, ...]

    @property
    def needs_rebuild(self) -> bool:
        return self.applied is not None or self.clarification_count > 0


def replay(root: Path) -> ReplayResult:
    """Apply local decisions/events to this snapshot, without generation or Git.

    The source stores remain unchanged. Consensus, soft deletion, reclassification
    and event deduplication use the same implementation as the existing workflow.
    Prepare all three records privately, then install with rollback for caught
    failures. Incomplete rollback retains recovery copies. This is not crash-safe
    or atomically visible to readers; use a stable snapshot and one writer.
    """
    from nbs_ruralscan.schema_tools.review_inputs import ReviewInputs
    from nbs_ruralscan.schema_tools.clarifications import (
        LOCK,
        merge_history,
        read_events,
        serialize_events,
    )

    root = Path(root).resolve(strict=True)
    files = ReviewFiles.from_root(root)
    decision_path = root / "pipeline/review/decisions.json"
    pending_path = root / "pipeline/review/clarifications.json"
    with LOCK, review_pair_lock():
        inputs = ReviewInputs((decision_path, pending_path))
        store = _load_store(decision_path)
        local_events = read_events(pending_path)
        inputs.verify()
    decisions, conflicts = consensus_decisions(store)
    check_review_destinations(
        files.evidence,
        files.log,
        root / "pipeline/metrics/clarification_log.json",
        root / "pipeline/metrics/clarification_log.tmp",
    )
    # A missing evidence snapshot must not leave clarification history partly applied.
    if decisions and not files.evidence.is_file():
        raise ValueError(f"Evidence register missing: {files.evidence}")
    destinations = (
        files.evidence,
        files.log,
        root / "pipeline/metrics/clarification_log.json",
    )
    result = None

    def render(staged: SchemaBuildPaths) -> list[Path]:
        nonlocal result
        assert staged.output_root is not None
        staged_files = ReviewFiles.from_root(staged.output_root)
        inputs.verify()
        staged_history = staged.output_root / "pipeline/metrics/clarification_log.json"
        events, clarification_count = merge_history(
            read_events(staged_history), local_events
        )
        if clarification_count:
            staged_history.parent.mkdir(parents=True, exist_ok=True)
            staged_history.write_bytes(serialize_events(events))
        applied = (
            apply_decisions(decisions, "consensus", files=staged_files)
            if decisions
            else None
        )
        if applied and applied["reasons"] and not staged_files.log.is_file():
            raise ValueError("Review decisions produced no audit log")
        result = ReplayResult(clarification_count, applied, tuple(conflicts))
        inputs.verify()
        return []

    # Optional files can remain absent on no-op/unknown-ID/clarification-only runs.
    # Existing files are always required; no deletion is permitted by publication.
    staged_publish(
        SchemaBuildPaths(root / "schema"),
        list(destinations),
        render,
        optional_destinations=destinations,
        artifact_validators={path: lambda _: inputs.verify() for path in destinations},
    )
    assert result is not None
    return result


def main(*, root: Path | None = None) -> int:
    """Compatibility wrapper: replay records, then run the existing full generator."""
    root = Path(root if root is not None else ROOT).resolve()
    result = replay(root)
    print(f"submit_review: replayed {result.clarification_count} clarification events")
    if result.needs_rebuild:
        try:
            generate(root / "schema")
        except BaseException:
            print(
                "Review replay completed, but artifact rebuilding failed. "
                f"Retry generation explicitly for {root / 'schema'}; "
                "replaying clarification-only events may not trigger another rebuild. "
                "Keep any reported publication recovery copies before retrying.",
                file=sys.stderr,
            )
            raise
    if result.applied is None:
        print("submit_review: no agreed decisions to apply (nothing to do).")
        if result.conflicts:
            print(
                f"  ({len(result.conflicts)} conflicted, left pending: {', '.join(result.conflicts)})"
            )
        return 0
    print(f"submit_review: applied {result.applied}")
    if result.conflicts:
        print(f"  conflicts skipped (left pending): {', '.join(result.conflicts)}")
    return 0


# Exact allowlist: generated neighbours may change, application code never ships here.
SHIP_FILES = (
    "schema/registers/EV_evidence_register.csv",
    "schema/registers/EV_evidence_register.json",
    "pipeline/metrics/review_log.csv",
    "pipeline/metrics/clarification_log.json",
    "docs/dashboard_data.json",
    "docs/progress.json",
    "docs/table_progress.json",
    "docs/scorecard.json",
)


def _submission_stores(root: Path) -> dict[str, bytes]:
    """Copy the declared pair from one observed local review state."""
    from nbs_ruralscan.schema_tools.review_inputs import ReviewInputs
    from nbs_ruralscan.schema_tools.clarifications import LOCK, read_events

    review = root / "pipeline/review"
    pending = review / "clarifications.json"
    paths = (review / "decisions.json", pending)
    with LOCK, review_pair_lock():
        selected = ReviewInputs(paths)
        read_events(pending)
        bodies = {path.name: path.read_bytes() for path in paths if path.exists()}
        selected.verify()
        for path, state in selected.states.items():
            body = bodies.get(path.name)
            expected = state[0] if state is not None else None
            actual = hashlib.sha256(body).hexdigest() if body is not None else None
            if expected != actual:
                raise ValueError(f"Review store changed while reading: {path}")
        return bodies


def ship(
    reviewer: str, title: str | None = None, auto: bool = False, *, root: Path = ROOT
) -> int:
    """Replay a snapshot on latest main in an isolated checkout; preserve the live checkout.

    Failure retains the checkout for diagnosis. No force-push, branch reset, stash or
    reviewer-store mutation. Auto-merge still requires repository checks and approvals.
    """
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}", reviewer):
        raise ValueError(
            "Reviewer must be a GitHub handle (letters, digits, dot, dash or underscore)."
        )
    if not (root / ".cache" / "corpus").is_dir():
        raise ValueError(
            "Source cache missing. Run uv run python scripts/hydrate-corpus.py before submitting"
        )
    title = title or f"qaqc: review decisions ({reviewer})"
    if not title.startswith("qaqc:"):
        raise ValueError("Review submission titles must start with 'qaqc:'.")
    env = {
        **os.environ,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_ASKPASS": "",
        "SSH_ASKPASS": "",
        "GCM_INTERACTIVE": "Never",
        "GH_PROMPT_DISABLED": "1",
    }

    def run(args: list[str], cwd: Path = root) -> str:
        result = subprocess.run(
            args,
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            stdin=subprocess.DEVNULL,
            timeout=600,
        )
        if result.returncode:
            raise RuntimeError(
                result.stderr.strip() or result.stdout.strip() or str(args)
            )
        return result.stdout.strip()

    # Check tools/auth before creating any review checkout.
    run(["git", "--version"])
    run(["gh", "auth", "status"])
    lock = root / ".cache" / "review-submit.lock"
    lock.parent.mkdir(exist_ok=True)
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError(
            "Another submission is running. Decisions remain saved locally."
        ) from exc
    os.close(fd)
    checkout = None
    success = False
    try:
        run(["git", "fetch", "origin", "main"])
        branch = f"codex/review-{reviewer}-{uuid.uuid4().hex[:12]}"
        checkout = Path(tempfile.mkdtemp(prefix="nbs-review-")) / "checkout"
        run(["git", "worktree", "add", "-b", branch, str(checkout), "origin/main"])
        print(f"Review checkout: {checkout}", flush=True)
        for name, body in _submission_stores(root).items():
            target = checkout / "pipeline" / "review" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
        corpus = root / ".cache" / "corpus"
        target_corpus = checkout / ".cache" / "corpus"
        target_corpus.parent.mkdir(exist_ok=True)
        if corpus.exists():
            try:
                target_corpus.symlink_to(corpus, target_is_directory=True)
            except OSError:
                # Windows without symlink privilege: hardlinks where possible, copy otherwise.
                def link_or_copy(src: str, dst: str) -> str:
                    try:
                        os.link(src, dst)
                        return dst
                    except OSError:
                        return shutil.copy2(src, dst)

                shutil.copytree(corpus, target_corpus, copy_function=link_or_copy)
        env["PYTHONPATH"] = str(checkout / "src")
        print(
            run(
                [sys.executable, "-m", "nbs_ruralscan.schema_tools.submit_review"],
                checkout,
            ),
            flush=True,
        )
        tracked = run(["git", "diff", "--name-only", "--", *SHIP_FILES], checkout)
        # The first clarification-only submission can create the history file.
        created = run(
            ["git", "ls-files", "--others", "--exclude-standard", "--", *SHIP_FILES],
            checkout,
        )
        changed = sorted(set(tracked.splitlines()) | set(created.splitlines()))
        meaningful = {
            "schema/registers/EV_evidence_register.csv",
            "pipeline/metrics/review_log.csv",
            "pipeline/metrics/clarification_log.json",
        }
        if not meaningful.intersection(changed):
            print("No agreed review changes to submit. Local decisions preserved.")
            success = True
            return 0
        run(["git", "add", "--", *changed], checkout)
        staged = set(
            run(["git", "diff", "--cached", "--name-only"], checkout).splitlines()
        )
        if not staged.issubset(SHIP_FILES):
            raise RuntimeError(
                "Submission stopped: staged files exceed the review allowlist."
            )
        run(["git", "commit", "-m", title], checkout)
        run(["git", "push", "-u", "origin", branch], checkout)
        body = checkout / ".cache" / "review-pr-body.md"
        body.write_text(
            f"QA review decisions by **{reviewer}**, replayed onto latest main. "
            "Consensus decisions and clarification history only; no stale-branch reverts. "
            "Clarification acceptance does not approve extraction. "
            "Required checks and approvals still apply.\n",
            encoding="utf-8",
        )
        url = run(
            [
                "gh",
                "pr",
                "create",
                "--base",
                "main",
                "--head",
                branch,
                "--title",
                title,
                "--body-file",
                str(body),
            ],
            checkout,
        )
        print(url, flush=True)
        if auto:
            try:
                print(run(["gh", "pr", "merge", url, "--squash", "--auto"], checkout))
                print(
                    "Auto-merge requested; required checks and approvals still apply."
                )
            except RuntimeError as exc:
                print(f"PR created; auto-merge unavailable. Review it on GitHub: {exc}")
        success = True
        return 0
    finally:
        lock.unlink(missing_ok=True)
        if checkout is not None:
            if success:
                run(["git", "worktree", "remove", "--force", str(checkout)])
                checkout.parent.rmdir()
            else:
                print(
                    f"Submission stopped. Recovery checkout retained: {checkout}",
                    flush=True,
                )


def cli() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ship", metavar="REVIEWER")
    parser.add_argument("--title")
    parser.add_argument("--auto", action="store_true")
    parser.add_argument(
        "--root",
        type=Path,
        help="Replay and rebuild a local snapshot (not with --ship).",
    )
    args = parser.parse_args()
    if args.ship and args.root is not None:
        parser.error("--root is for local replay only; it cannot be used with --ship.")
    try:
        return (
            ship(args.ship, args.title, args.auto)
            if args.ship
            else main(root=args.root)
        )
    except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"Submit failed: {exc}. Local decisions remain saved.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(cli())
