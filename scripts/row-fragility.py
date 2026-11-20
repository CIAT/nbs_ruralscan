#!/usr/bin/env python3
"""Retired automatic effect-sensitivity entrypoint; scientific synthesis now lives in RuralScan/evidence."""

import sys


def main(argv=None):
    print(
        "Automatic T3/T6 scoring is retired. Use the AI synthesis skill and "
        "workflows/synthesis/run.py in RuralScan/evidence. Code validates and "
        "packages scientifically accepted outputs; it does not assign ratings.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
