#!/usr/bin/env python3
"""Publish generated T4 panels for the existing evidence dashboard (no new page)."""

import argparse
from pathlib import Path
from nbs_ruralscan.recipe.t4_dashboard import build_dashboard
from nbs_ruralscan.recipe.developer_contract import stable_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--nbs", default="agroforestry")
    args = parser.parse_args()
    name = (
        "t4_analysis.json"
        if args.nbs == "agroforestry"
        else f"t4_analysis_{args.nbs}.json"
    )
    text = stable_json(build_dashboard(args.root, nbs=args.nbs))
    path = args.root / "docs" / name
    if args.check:
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            raise SystemExit(
                "T4 dashboard snapshot differs; rebuild with scripts/build-t4-dashboard.py"
            )
        print("T4 dashboard snapshot matches corpus and compiler")
    else:
        path.write_text(text, encoding="utf-8")
        print("Published panels: dashboard.html#t4/global")


if __name__ == "__main__":
    main()
