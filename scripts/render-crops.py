#!/usr/bin/env python3
"""Pre-render highlighted PDF-region crops for OPEN-ACCESS evidence → docs/crops/.

The QA/QC dashboard's "show source region" normally renders a highlighted PDF crop
via the local review server's GET /api/crop, which needs the reviewer to have the PDF
locally. Most reviewers (and the public GitHub-Pages site) don't. This script runs on
the machine that HAS all the PDFs (via .cache/corpus or the OneDrive library mirror),
renders each crop once, and writes a committed JPEG per evidence_id so every reviewer
sees it with zero setup.

COPYRIGHT GATE (safety-critical): a crop is written ONLY for sources that are
open-access. Everything else is skipped and falls back to the SharePoint link in the
dashboard. Never publish a crop for a paywalled / unknown-licence source.

Usage:
    python3 scripts/render-crops.py [--scope flagged|all] [--dry-run]

    --scope flagged   (default) only render EV rows whose attribution carries a
                      [VERIFY-FLAG marker.
    --scope all       render every EV row.
    --dry-run         do everything EXCEPT writing images / manifest (counts + gate
                      assertion only).

The library root defaults to Pete's CGIAR OneDrive mount; override with NBS_LIBRARY_ROOT
(same resolution as scripts/hydrate-corpus.py).
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "corpus"
EV_CSV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
SRC_CSV = ROOT / "schema" / "registers" / "SRC_source_register.csv"
CROPS_DIR = ROOT / "docs" / "crops"

# import the shared render function from the review server
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.schema_tools.review_server import render_region_png  # noqa: E402

# sources we must NEVER publish a crop for (belt-and-braces on top of the gate)
KNOWN_NONPUBLISHABLE = {"wb_fsrp_2022", "wb_kcsap_2016", "mushtaq_2023"}


def library_root() -> Path | None:
    """Resolve the local OneDrive mirror of the SharePoint .../1_Projects/ folder.

    Same logic as scripts/hydrate-corpus.py (copied to avoid a hyphenated-module import).
    """
    env = os.environ.get("NBS_LIBRARY_ROOT")
    if env:
        return Path(env).expanduser()
    default = (
        Path.home()
        / "Library/CloudStorage/OneDrive-CGIAR/ClimateActionNetZero/1_Projects"
    )
    return default if default.exists() else None


def is_publishable(src: dict) -> bool:
    """Copyright gate: True iff the source is open-access and safe to publish a crop for."""
    lic = (src.get("license") or "").lower()
    acc = (src.get("access_status") or "").lower()
    return (
        lic.startswith("cc-")
        or lic in ("other-oa", "cc0", "public-domain")
        or acc in ("open_access", "open", "gold", "green", "hybrid", "oa")
    )


def resolve_pdf(sid: str, src: dict, lib_root: Path | None) -> Path | None:
    """Resolve a PDF for a source: .cache/corpus/<sid>.pdf first, else OneDrive library."""
    cached = CACHE / (sid + ".pdf")
    if cached.exists():
        return cached
    lib_path = (src.get("library_path") or "").strip()
    if not lib_path or lib_root is None:
        return None
    p = lib_root / lib_path
    return p if p.exists() else None


def png_to_jpeg(png: bytes) -> bytes | None:
    """PNG bytes → optimised JPEG bytes via Pillow. None on failure."""
    try:
        from PIL import Image
    except Exception:
        print(
            "  ! Pillow (PIL) not importable — cannot convert to JPEG", file=sys.stderr
        )
        return None
    try:
        im = Image.open(io.BytesIO(png)).convert("RGB")
        # committed crops are for reading a highlighted passage, not table zoom —
        # cap the long edge so the public asset set stays light (full-res render
        # is ~2600px). 1600px keeps text crisp at a fraction of the size.
        max_edge = 1600
        if max(im.size) > max_edge:
            im.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
        out = io.BytesIO()
        im.save(out, format="JPEG", quality=70, optimize=True)
        return out.getvalue()
    except Exception as e:  # noqa: BLE001
        print(f"  ! JPEG conversion failed: {e}", file=sys.stderr)
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--scope",
        choices=["flagged", "all"],
        default="flagged",
        help="which EV rows to render (default: flagged)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="count + gate-check only; write no images / manifest",
    )
    args = ap.parse_args()

    if not EV_CSV.exists() or not SRC_CSV.exists():
        print(f"missing register(s): {EV_CSV} / {SRC_CSV}")
        return 1

    # SRC index
    src_by_id: dict[str, dict] = {}
    with SRC_CSV.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            sid = (r.get("source_id") or "").strip()
            if sid:
                src_by_id[sid] = r

    lib_root = library_root()

    # in-scope EV rows
    ev_rows: list[dict] = []
    with EV_CSV.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            attr = r.get("attribution") or ""
            if args.scope == "flagged" and "[VERIFY-FLAG" not in attr:
                continue
            ev_rows.append(r)

    print(f"scope           : {args.scope}")
    print(f"in-scope EV rows: {len(ev_rows)}")
    print(f"library root    : {lib_root if lib_root else '(none / not found)'}")
    print(f"dry-run         : {args.dry_run}")

    rendered: list[str] = []
    rendered_sids: dict[str, str] = {}  # eid -> sid, for the gate assertion
    skipped_nonoa: dict[str, str] = {}  # eid -> sid
    skipped_nopdf: list[str] = []
    skipped_norender: list[str] = []
    produced_banned: list[
        str
    ] = []  # eids for banned sids that produced a crop (must stay empty)

    if not args.dry_run:
        CROPS_DIR.mkdir(parents=True, exist_ok=True)

    for r in ev_rows:
        eid = (r.get("evidence_id") or "").strip()
        sid = (r.get("source_id") or "").strip()
        if not eid:
            continue
        src = src_by_id.get(sid, {})

        # copyright gate FIRST
        if sid in KNOWN_NONPUBLISHABLE or not is_publishable(src):
            skipped_nonoa[eid] = sid
            continue

        pdf = resolve_pdf(sid, src, lib_root)
        if pdf is None:
            skipped_nopdf.append(eid)
            continue

        page = int(r["page"]) if (r.get("page") or "").strip().isdigit() else None
        png = render_region_png(pdf, r.get("quote") or "", page)
        if png is None:
            skipped_norender.append(eid)
            continue
        jpeg = png_to_jpeg(png)
        if jpeg is None:
            skipped_norender.append(eid)
            continue

        # extra guard: a banned sid must never reach here
        if sid in KNOWN_NONPUBLISHABLE:
            produced_banned.append(eid)
            continue

        rendered.append(eid)
        rendered_sids[eid] = sid
        if not args.dry_run:
            (CROPS_DIR / f"{eid}.jpg").write_bytes(jpeg)

    rendered.sort()

    # manifest
    manifest = {
        "generated_scope": args.scope,
        "n": len(rendered),
        "eids": rendered,
    }
    if not args.dry_run:
        (CROPS_DIR / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )

    # summary
    print("\n=== summary ===")
    print(f"rendered            : {len(rendered)}")
    print(f"skipped non-OA      : {len(skipped_nonoa)}")
    nonoa_sids = sorted(set(skipped_nonoa.values()))
    if nonoa_sids:
        print(f"  non-OA sids: {', '.join(nonoa_sids)}")
    print(f"skipped no-pdf      : {len(skipped_nopdf)}")
    print(f"skipped no-render   : {len(skipped_norender)}")

    # gate assertion: none of the known-banned sids produced a crop
    banned_in_rendered = [
        eid for eid in rendered if rendered_sids.get(eid) in KNOWN_NONPUBLISHABLE
    ]
    gate_ok = not produced_banned and not banned_in_rendered
    print(
        f"\nGATE (no crop for {sorted(KNOWN_NONPUBLISHABLE)}): "
        + ("PASS" if gate_ok else "FAIL")
    )
    if not gate_ok:
        print(f"  ! banned crops produced: {produced_banned + banned_in_rendered}")
        return 2
    if args.dry_run:
        print("(dry-run: no images or manifest written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
