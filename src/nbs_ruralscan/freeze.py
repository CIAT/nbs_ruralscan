"""Corpus versioning and snapshotting.

Enables reproducible runs by freezing/verifying registers and document index caches.

CLI:
    # Snapshot corpus:
    uv run python -m nbs_ruralscan.freeze --zip-path schema/run_snapshot.zip

    # Verify existing manifest:
    uv run python -m nbs_ruralscan.freeze --verify
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile


def get_sha256(path: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def get_git_commit() -> str:
    """Retrieve the current git commit SHA."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        return "unknown"


def find_files(
    registers_dir: Path = Path("schema/registers"),
    cache_dir: Path = Path(".cache/ingest"),
) -> list[Path]:
    """Find all register JSON files and cached document index JSON files."""
    files: list[Path] = []

    # Target all register JSONs
    if registers_dir.exists():
        files.extend(sorted(registers_dir.glob("*.json")))

    # Target cached ingest JSONs
    if cache_dir.exists():
        files.extend(sorted(cache_dir.glob("*.json")))

    return files


def create_manifest_and_snapshot(
    manifest_path: str | Path = "schema/run_manifest.json",
    zip_path: str | Path | None = "schema/run_snapshot.zip",
    registers_dir: str | Path = "schema/registers",
    cache_dir: str | Path = ".cache/ingest",
) -> int:
    """Calculate checksums, write the run manifest, and package files into a ZIP."""
    manifest_path = Path(manifest_path)
    registers_dir = Path(registers_dir)
    cache_dir = Path(cache_dir)

    files = find_files(registers_dir, cache_dir)
    if not files:
        print("Warning: No files found to snapshot under registers or ingest cache.")

    file_hashes: dict[str, str] = {}
    for f in files:
        # Keep relative paths for portability
        try:
            rel_path = f.relative_to(Path.cwd())
        except ValueError:
            rel_path = f
        file_hashes[str(rel_path)] = get_sha256(f)

    git_commit = get_git_commit()
    timestamp = datetime.now(timezone.utc).isoformat()

    manifest_data = {
        "timestamp": timestamp,
        "git_commit": git_commit,
        "files": file_hashes,
    }

    # Ensure manifest parent directory exists
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    with open(manifest_path, "w", encoding="utf-8") as f_out:
        json.dump(manifest_data, f_out, indent=2)
    print(f"Created manifest: {manifest_path}")

    if zip_path:
        zip_path = Path(zip_path)
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                try:
                    rel_path = f.relative_to(Path.cwd())
                except ValueError:
                    rel_path = f
                zf.write(f, rel_path)
        print(f"Created snapshot ZIP: {zip_path} ({len(files)} files archived)")

    return 0


def verify_manifest(
    manifest_path: str | Path = "schema/run_manifest.json",
) -> int:
    """Verify that files match the manifest checksums and exist."""
    manifest_path = Path(manifest_path)
    if not manifest_path.exists():
        print(f"Error: Manifest file '{manifest_path}' does not exist.")
        return 1

    with open(manifest_path, "r", encoding="utf-8") as f_in:
        try:
            manifest_data = json.load(f_in)
        except json.JSONDecodeError as e:
            print(f"Error: Manifest file '{manifest_path}' is not valid JSON. {e}")
            return 1

    files_to_verify = manifest_data.get("files", {})
    if not files_to_verify:
        print("Warning: No files listed in manifest for verification.")
        return 0

    mismatches: list[str] = []
    missing: list[str] = []
    success_count = 0

    for rel_path_str, expected_hash in files_to_verify.items():
        f = Path(rel_path_str)
        if not f.exists():
            missing.append(rel_path_str)
            continue

        current_hash = get_sha256(f)
        if current_hash != expected_hash:
            mismatches.append(
                f"{rel_path_str} (expected {expected_hash[:8]}, got {current_hash[:8]})"
            )
        else:
            success_count += 1

    if missing or mismatches:
        print("\nVerification Failed!")
        if missing:
            print("\nMissing files:")
            for m in missing:
                print(f"  - {m}")
        if mismatches:
            print("\nChecksum mismatches:")
            for mm in mismatches:
                print(f"  - {mm}")
        return 1

    print(
        f"Verification Successful: {success_count} files verified against manifest (Commit {manifest_data.get('git_commit', 'unknown')[:8]})."
    )
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Snapshot and verify registers and ingest cache files for reproducibility."
    )
    ap.add_argument(
        "--manifest",
        default="schema/run_manifest.json",
        help="Path to manifest file (default: schema/run_manifest.json)",
    )
    ap.add_argument(
        "--zip-path",
        default="schema/run_snapshot.zip",
        help="Path to create snapshot ZIP (default: schema/run_snapshot.zip). Use 'none' to skip.",
    )
    ap.add_argument(
        "--verify",
        action="store_true",
        help="Verify the files listed in the manifest instead of snapshotting.",
    )
    ap.add_argument(
        "--registers-dir",
        default="schema/registers",
        help="Path to registers directory (default: schema/registers)",
    )
    ap.add_argument(
        "--cache-dir",
        default=".cache/ingest",
        help="Path to ingest cache directory (default: .cache/ingest)",
    )
    args = ap.parse_args()

    if args.verify:
        sys.exit(verify_manifest(args.manifest))
    else:
        zip_p = None if args.zip_path.lower() == "none" else args.zip_path
        sys.exit(
            create_manifest_and_snapshot(
                manifest_path=args.manifest,
                zip_path=zip_p,
                registers_dir=args.registers_dir,
                cache_dir=args.cache_dir,
            )
        )


if __name__ == "__main__":
    main()
