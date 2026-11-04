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
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

from nbs_ruralscan.schema_tools.generate import generate
from nbs_ruralscan.schema_tools.review import apply_decisions

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / "pipeline" / "review" / "decisions.json"


def _load_store() -> dict:
    if not STORE.exists():
        return {}
    raw = STORE.read_bytes()
    try:
        return json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError:
        return json.loads(raw.decode("cp1252"))  # tolerate a stray Windows byte


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


def main() -> int:
    from nbs_ruralscan.schema_tools.clarifications import publish

    clarification_count = publish(ROOT)
    print(f"submit_review: replayed {clarification_count} clarification events")
    store = _load_store()
    decisions, conflicts = consensus_decisions(store)
    if not decisions:
        if clarification_count:
            generate(ROOT / "schema")
        print("submit_review: no agreed decisions to apply (nothing to do).")
        if conflicts:
            print(
                f"  ({len(conflicts)} conflicted, left pending: {', '.join(conflicts)})"
            )
        return 0
    res = apply_decisions(decisions, "consensus")
    generate(ROOT / "schema")
    print(f"submit_review: applied {res}")
    if conflicts:
        print(f"  conflicts skipped (left pending): {', '.join(conflicts)}")
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
        for name in ("decisions.json", "clarifications.json"):
            source = root / "pipeline" / "review" / name
            if source.exists():
                target = checkout / "pipeline" / "review" / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
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
        changed = run(
            ["git", "diff", "--name-only", "--", *SHIP_FILES], checkout
        ).splitlines()
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
    args = parser.parse_args()
    try:
        return ship(args.ship, args.title, args.auto) if args.ship else main()
    except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"Submit failed: {exc}. Local decisions remain saved.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(cli())
