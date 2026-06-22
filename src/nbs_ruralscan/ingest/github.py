"""GitHub / tool-code interrogation — acquire a repo's source at a pinned commit and
scan it for hardcoded analytical parameters (candidate EV claims).

Automates the manual fetch+grep that produced the saraheb3 tool EV (2026-06-22). It does
the two SAFE-to-automate halves of tool interrogation:

  1. ACQUIRE — fetch each source file at a fixed ``commit`` and cache it to
     ``.cache/corpus/<source_id>.txt`` with a ``{source_id}.meta.json`` provenance sidecar
     (repo · commit · path · sha1). Commit-pinned so ``locator_type=file_line`` EV is immutable.
  2. SCAN — heuristically flag lines that look like hardcoded parameters (weight/threshold
     assignments, reclassify tables, ``.lt/.gt`` masks, buffer distances, land-cover gates),
     each with its ``file:line`` so an EvidenceUnit's ``locator`` is auto-derivable.

What it does NOT do: decide which candidate maps to which canonical variable / family —
that is the PICOS / claim_scope judgement call and stays human/LLM-driven, then passes the
central guardrail (verbatim + ``check_numbers``, which already handle ``file_line`` locators).
Blind auto-emission would re-make the mis-mapping mistakes at scale.

CLI::

    python -m nbs_ruralscan.ingest.github CIAT/repo <commit> --subdir gee_script
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_CORPUS_DIR = ".cache/corpus"

# Files to skip by default: per-species envelope scripts are species-specific (claim_scope),
# not practice-level rules. Callers can extend/override.
DEFAULT_IGNORE = [r"(?i)tree-growth", r"(?i)per[-_]?species"]

# Heuristic signals of a hardcoded analytical parameter (a candidate EV claim).
_PARAM_PATTERNS: dict[str, re.Pattern] = {
    # keyword anywhere in the identifier (camelCase: weightWaterErosion, slopeThreshold)
    "weight": re.compile(r"\w*weight\w*\s*=\s*-?\d", re.I),
    "threshold": re.compile(r"\w*(threshold|thresh|cutoff|score)\w*\s*=\s*-?\d", re.I),
    "mask": re.compile(r"\.(lt|lte|gt|gte|eq|neq)\(\s*-?\d"),
    "buffer": re.compile(
        r"(buffer\(\s*\{?\s*['\"]?distance['\"]?\s*:\s*-?\d|maxDistance\s*:\s*-?\d)",
        re.I,
    ),
    "reclassify": re.compile(r"\b(remap|reclassify|classify)\s*\(", re.I),
}


class GithubIngestError(RuntimeError):
    pass


@dataclass
class AcquiredFile:
    source_id: str
    repo: str
    commit: str
    path: str
    sha1: str
    n_lines: int
    cached: str


def _gh(args: list[str]) -> str:
    """Run a `gh api` call; raise GithubIngestError on failure (gh handles auth)."""
    p = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise GithubIngestError(f"gh api {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout


def _slug(repo: str, path: str) -> str:
    """Stable snake_case source_id from repo owner + file stem."""
    owner = repo.split("/")[0].lower()
    stem = re.sub(r"\W+", "_", Path(path).stem.lower()).strip("_")
    return f"{owner}_{stem}"


def list_repo_files(
    repo: str, commit: str, subdir: str = "", ignore: list[str] | None = None
) -> list[str]:
    """List source-file paths under ``subdir`` of ``repo`` at ``commit`` (one level)."""
    ig = [re.compile(p) for p in (ignore if ignore is not None else DEFAULT_IGNORE)]
    items = json.loads(_gh([f"/repos/{repo}/contents/{subdir}?ref={commit}"]))
    out = []
    for it in items if isinstance(items, list) else []:
        if it.get("type") != "file":
            continue
        path = it["path"]
        if any(rx.search(path) for rx in ig):
            continue
        out.append(path)
    return out


def acquire_file(
    repo: str,
    commit: str,
    path: str,
    corpus_dir: str | Path = DEFAULT_CORPUS_DIR,
    source_id: str | None = None,
) -> AcquiredFile:
    """Fetch one repo file at ``commit`` → cache as text + provenance sidecar."""
    sid = source_id or _slug(repo, path)
    content = base64.b64decode(
        _gh([f"/repos/{repo}/contents/{path}?ref={commit}", "-q", ".content"])
    )
    if not content:
        raise GithubIngestError(f"empty content for {repo}:{path}@{commit}")
    corpus = Path(corpus_dir)
    corpus.mkdir(parents=True, exist_ok=True)
    dest = corpus / f"{sid}.txt"
    dest.write_bytes(content)
    sha1 = hashlib.sha1(content).hexdigest()
    meta = {
        "source_id": sid,
        "kind": "github_code",
        "repo": repo,
        "commit": commit,
        "path": path,
        "url": f"https://github.com/{repo}/blob/{commit}/{path}",
        "sha1": sha1,
        "fetched_at": datetime.now(tz=timezone.utc).isoformat(),
    }
    (corpus / f"{sid}.meta.json").write_text(json.dumps(meta, indent=2))
    return AcquiredFile(
        source_id=sid,
        repo=repo,
        commit=commit,
        path=path,
        sha1=sha1,
        n_lines=len(content.decode(errors="replace").splitlines()),
        cached=str(dest),
    )


def scan_candidates(text: str, path: str = "") -> list[dict]:
    """Flag lines that look like hardcoded parameters (candidate EV claims).

    Returns ``[{path, line, kind, text}]`` — one per matched line (first matching kind).
    ``line`` is 1-based so a unit's ``locator`` is ``f"{path}:L{line}"``.
    """
    out: list[dict] = []
    for i, line in enumerate(text.splitlines(), 1):
        for kind, pat in _PARAM_PATTERNS.items():
            if pat.search(line):
                out.append(
                    {"path": path, "line": i, "kind": kind, "text": line.strip()[:200]}
                )
                break
    return out


def interrogate(
    repo: str,
    commit: str,
    subdir: str = "",
    ignore: list[str] | None = None,
    corpus_dir: str | Path = DEFAULT_CORPUS_DIR,
) -> dict:
    """Acquire every (non-ignored) file under ``subdir`` and scan each for candidates."""
    files = list_repo_files(repo, commit, subdir, ignore)
    acquired, candidates = [], []
    for path in files:
        af = acquire_file(repo, commit, path, corpus_dir)
        acquired.append(asdict(af))
        text = Path(af.cached).read_text(errors="replace")
        for c in scan_candidates(text, path):
            c["source_id"] = af.source_id
            c["commit"] = commit
            candidates.append(c)
    return {"acquired": acquired, "candidates": candidates}


def main(argv: list[str] | None = None) -> int:
    import argparse
    import sys

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "repo", help="owner/name, e.g. saraheb3/AgroforestrySuitability_GEE"
    )
    ap.add_argument("commit", help="commit SHA to pin (immutable provenance)")
    ap.add_argument("--subdir", default="", help="restrict to a sub-directory")
    ap.add_argument(
        "--ignore", nargs="*", default=None, help="regex(es) of paths to skip"
    )
    args = ap.parse_args(argv if argv is not None else sys.argv[1:])

    res = interrogate(args.repo, args.commit, args.subdir, args.ignore)
    print(f"acquired {len(res['acquired'])} file(s) @ {args.commit[:8]}:")
    for a in res["acquired"]:
        print(f"  {a['source_id']:36} {a['path']} ({a['n_lines']}L)")
    print(f"\n{len(res['candidates'])} parameter candidate(s) for judged extraction:")
    for c in res["candidates"]:
        print(f"  [{c['kind']:10}] {c['source_id']}:L{c['line']}  {c['text'][:90]}")
    print(
        "\nNext: emit EvidenceUnits from candidates (judge variable + family per PICOS), "
        "locator=file_line + commit_sha auto from above, then validate + central guardrail."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
