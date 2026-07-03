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
                                    [--sharepoint-nonoa]

    --scope flagged      (default) only render EV rows whose attribution carries a
                         [VERIFY-FLAG marker.
    --scope all          render every EV row.
    --dry-run            do everything EXCEPT writing images / manifest (counts +
                         gate assertion only).
    --sharepoint-nonoa   (default OFF) ALSO render a crop for NON-open-access sources
                         into the OneDrive/SharePoint library `crops/` folder — NEVER
                         into docs/. Copyright-safe: same access control as the PDFs.
                         Only their library-relative path is recorded in the public
                         manifest (never the image bytes). No-op if the library root
                         can't be resolved.

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


def library_crops_reldir(src: dict) -> str | None:
    """Library-relative crops dir for a source, from the first two segments of its
    library_path (e.g. `D591_.../2_Technical_&_Data/Stocktake Review/x.pdf`
    → `D591_.../2_Technical_&_Data/crops`). None if library_path is empty/too shallow.
    """
    lib_path = (src.get("library_path") or "").strip().replace("\\", "/")
    if not lib_path:
        return None
    segs = [s for s in lib_path.split("/") if s]
    if len(segs) < 2:
        return None
    return "/".join(segs[:2]) + "/crops"


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


def _render_nonoa_library_crop(
    r: dict,
    eid: str,
    sid: str,
    src: dict,
    lib_root: Path | None,
    dry_run: bool,
    sharepoint_map: dict[str, str],
    sharepoint_sids: dict[str, str],
    sp_nopdf: list[str],
    sp_norender: list[str],
    sp_noreldir: list[str],
) -> None:
    """Render a non-OA source's crop into the library mirror's crops/ dir (never docs/).

    Records the library-relative path in sharepoint_map so the dashboard can build a
    SharePoint URL. Only the path string is public — the image bytes stay in the
    access-controlled library.
    """
    reldir = library_crops_reldir(src)
    if reldir is None:
        sp_noreldir.append(eid)
        return
    pdf = resolve_pdf(sid, src, lib_root)
    if pdf is None:
        sp_nopdf.append(eid)
        return
    page = int(r["page"]) if (r.get("page") or "").strip().isdigit() else None
    png = render_region_png(pdf, r.get("quote") or "", page)
    if png is None:
        sp_norender.append(eid)
        return
    jpeg = png_to_jpeg(png)
    if jpeg is None:
        sp_norender.append(eid)
        return
    rel_path = f"{reldir}/{eid}.jpg"
    sharepoint_map[eid] = rel_path
    sharepoint_sids[eid] = sid
    if not dry_run:
        assert lib_root is not None  # sp_nonoa_active guarantees this
        abs_dir = lib_root / reldir
        abs_dir.mkdir(parents=True, exist_ok=True)
        (abs_dir / f"{eid}.jpg").write_bytes(jpeg)


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
    ap.add_argument(
        "--sharepoint-nonoa",
        action="store_true",
        help="also render non-OA crops into the OneDrive library crops/ dir (never docs/)",
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

    # non-OA→library rendering is only active when the flag is set AND we can resolve
    # the local library mirror (else there is nowhere copyright-safe to write).
    sp_nonoa_active = args.sharepoint_nonoa and lib_root is not None

    print(f"scope           : {args.scope}")
    print(f"in-scope EV rows: {len(ev_rows)}")
    print(f"library root    : {lib_root if lib_root else '(none / not found)'}")
    print(f"dry-run         : {args.dry_run}")
    print(f"sharepoint-nonoa: {args.sharepoint_nonoa} (active: {sp_nonoa_active})")
    if args.sharepoint_nonoa and lib_root is None:
        print(
            "  ! --sharepoint-nonoa requested but library root not found "
            "(set NBS_LIBRARY_ROOT) — skipping non-OA library crops."
        )

    rendered: list[str] = []
    rendered_sids: dict[str, str] = {}  # eid -> sid, for the gate assertion
    skipped_nonoa: dict[str, str] = {}  # eid -> sid
    skipped_nopdf: list[str] = []
    skipped_norender: list[str] = []
    produced_banned: list[
        str
    ] = []  # eids for banned sids that produced a crop (must stay empty)

    # non-OA → library crops (copyright-gated: bytes go ONLY to the library mirror)
    sharepoint_map: dict[str, str] = {}  # eid -> library-relative "<reldir>/<eid>.jpg"
    sharepoint_sids: dict[str, str] = {}  # eid -> sid, for the gate assertion
    sp_nopdf: list[str] = []
    sp_norender: list[str] = []
    sp_noreldir: list[str] = []

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
            # non-OA sources get a crop ONLY inside the access-controlled library
            # mirror — NEVER under docs/. Gated behind --sharepoint-nonoa + a
            # resolvable library root.
            if sp_nonoa_active:
                _render_nonoa_library_crop(
                    r,
                    eid,
                    sid,
                    src,
                    lib_root,
                    args.dry_run,
                    sharepoint_map,
                    sharepoint_sids,
                    sp_nopdf,
                    sp_norender,
                    sp_noreldir,
                )
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
    # non-OA library crops: publish ONLY the library-relative path (never the bytes),
    # so the dashboard can build a SharePoint link for reviewers with library access.
    if sp_nonoa_active and sharepoint_map:
        manifest["sharepoint"] = {
            eid: sharepoint_map[eid] for eid in sorted(sharepoint_map)
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

    if sp_nonoa_active:
        target_dirs = sorted({p.rsplit("/", 1)[0] for p in sharepoint_map.values()})
        print(
            f"\nnon-OA crops written to library: {len(sharepoint_map)}"
            + (" (would be, dry-run)" if args.dry_run else "")
        )
        if target_dirs:
            for d in target_dirs:
                print(f"  target library dir: {lib_root / d}")
        sp_sids = sorted(set(sharepoint_sids.values()))
        if sp_sids:
            print(f"  non-OA library sids: {', '.join(sp_sids)}")
        print(f"  non-OA skipped no-pdf   : {len(sp_nopdf)}")
        print(f"  non-OA skipped no-render: {len(sp_norender)}")
        print(f"  non-OA skipped no-reldir: {len(sp_noreldir)}")

    # gate assertion: none of the known-banned sids produced a PUBLIC (docs/) crop
    banned_in_rendered = [
        eid for eid in rendered if rendered_sids.get(eid) in KNOWN_NONPUBLISHABLE
    ]
    gate_ok = not produced_banned and not banned_in_rendered
    print(
        f"\nGATE (no PUBLIC crop for {sorted(KNOWN_NONPUBLISHABLE)}): "
        + ("PASS" if gate_ok else "FAIL")
    )
    if not gate_ok:
        print(f"  ! banned crops produced: {produced_banned + banned_in_rendered}")
        return 2

    # sharepoint gate: every eid in the sharepoint map must belong to a
    # NON-publishable source, and NONE may also appear in the public docs/ set.
    if args.sharepoint_nonoa:
        sp_bad_publishable = [
            eid
            for eid, s in sharepoint_sids.items()
            if is_publishable(src_by_id.get(s, {})) and s not in KNOWN_NONPUBLISHABLE
        ]
        sp_in_docs = [eid for eid in sharepoint_map if eid in set(rendered)]
        # every mapped eid must belong to a known non-OA sid (the 3 known ones)
        sp_sids_seen = set(sharepoint_sids.values())
        sp_unknown_sids = sorted(sp_sids_seen - KNOWN_NONPUBLISHABLE)
        sp_gate_ok = (
            not sp_bad_publishable
            and not sp_in_docs
            and sp_sids_seen.issubset(KNOWN_NONPUBLISHABLE)
        )
        print(
            f"SHAREPOINT GATE (map ⊆ {sorted(KNOWN_NONPUBLISHABLE)}, none in docs/): "
            + ("PASS" if sp_gate_ok else "FAIL")
        )
        if not sp_gate_ok:
            if sp_bad_publishable:
                print(f"  ! publishable sids in sharepoint map: {sp_bad_publishable}")
            if sp_in_docs:
                print(f"  ! sharepoint eids also in docs/: {sp_in_docs}")
            if sp_unknown_sids:
                print(f"  ! unexpected non-OA sids in map: {sp_unknown_sids}")
            return 3

    if args.dry_run:
        print("(dry-run: no images or manifest written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
