#!/usr/bin/env python3
"""Regenerate evidence-derived T4 and export a reproducible developer contract."""

import argparse
import json
from pathlib import Path

from nbs_ruralscan.recipe.developer_contract import (
    build_contract,
    write_package,
    verify_package,
)

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--nbs", default="agroforestry")
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--verify",
        type=Path,
        help="Verify existing package hashes against this checkout without rebuilding",
    )
    parser.add_argument(
        "--country",
        help="Target three-letter country identifier for BIND, e.g. HTI; does not filter studies",
    )
    parser.add_argument(
        "--context",
        action="append",
        default=[],
        help="Additional T7/BIND context identifier",
    )
    parser.add_argument(
        "--evidence-country",
        action="append",
        default=[],
        help="Exact recorded study-country name, e.g. India; repeat for OR",
    )
    parser.add_argument(
        "--selection",
        type=Path,
        help="Explicit response selection document; never supplies new scores",
    )
    parser.add_argument("--list-evidence-countries", action="store_true")
    args = parser.parse_args()
    if args.verify:
        verify_package(args.root, args.verify)
        print("Package inputs and outputs verified")
        return
    if args.list_evidence_countries:
        print(
            "\n".join(
                build_contract(args.root, nbs=args.nbs)["contract"][
                    "available_evidence_countries"
                ]
            )
        )
        return
    if not args.output:
        parser.error("--output is required")
    manifest = write_package(
        args.root,
        args.output,
        nbs=args.nbs,
        country=args.country,
        contexts=args.context,
        evidence_countries=args.evidence_country,
        selection=json.loads(args.selection.read_text(encoding="utf-8"))
        if args.selection
        else None,
    )
    print(json.dumps(manifest["summary"], indent=2))
    print(f"Developer package: {args.output / 'index.html'}")


if __name__ == "__main__":
    main()
