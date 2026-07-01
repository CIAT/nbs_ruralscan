"""Categorical code-list decoding — turn numeric class codes into readable names.

Class-coded evidence (a CDL crop mask, HWSD soil-quality classes 1–7, FAO LCCS classes
1–4) stores bare integers that a reviewer can't interpret ("land_cover: 61, 205…" — QA
flag, issue #102). This resolver decodes them against a legend (`schema/codelists/<scheme>.csv`)
so the readable names show **by default** wherever the evidence is surfaced.

General API:
  * ``load(scheme)``            → {code: label}
  * ``decode(scheme, codes)``   → [(code, label), …]
  * ``scheme_for(variable, dataset)`` → the codelist scheme to use (default routing)

CDL masks (GEE expressions like ``cropLandcover.lte(61).or(cropLandcover.gte(205)...)``)
need their code set computed first: ``codes_from_cdl_mask(expr)`` parses the lte/gte/eq/neq
/and/or pattern into the included set, and ``summarise_cdl_mask(expr)`` returns the
included class names + the explicitly-excluded ones (the saraheb3 "annual crops, not tree
crops" rule). Anything richer than this expression family should be decoded from an
explicit code list, not parsed heuristically.
"""

from __future__ import annotations

import csv
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CODELISTS = ROOT / "schema" / "codelists"

# default routing: which scheme decodes a given variable / dataset. Extend as schemes land.
_SCHEME_BY_DATASET = {
    "usda_cdl": "cdl",
    "cropscape": "cdl",
    "gaez_v4_aez33": "gaez_aez33",
    "hwsd": "hwsd_soil_quality",
}
_SCHEME_BY_VARIABLE: dict[str, str] = {}  # e.g. {"land_cover": "cdl"} once unambiguous


@lru_cache(maxsize=None)
def load(scheme: str) -> dict[int, str]:
    """Load a code→label legend from schema/codelists/<scheme>.csv."""
    path = CODELISTS / f"{scheme}.csv"
    if not path.exists():
        return {}
    out: dict[int, str] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            code = (r.get("code") or "").strip()
            if code.lstrip("-").isdigit():
                out[int(code)] = (r.get("label") or "").strip()
    return out


def scheme_for(variable: str | None = None, dataset: str | None = None) -> str | None:
    """Pick the codelist scheme for a variable/dataset (default-decoding routing)."""
    if dataset and dataset.lower() in _SCHEME_BY_DATASET:
        return _SCHEME_BY_DATASET[dataset.lower()]
    if variable and variable in _SCHEME_BY_VARIABLE:
        return _SCHEME_BY_VARIABLE[variable]
    return None


def decode(scheme: str, codes: list[int]) -> list[tuple[int, str]]:
    """Decode codes → [(code, label)] (label '' if unknown), preserving order."""
    legend = load(scheme)
    return [(c, legend.get(c, "")) for c in codes]


def expand_codes(spec: str) -> list[int]:
    """Parse a class spec like "1-4", "5-7", "1,2,3", "1-3,5" → sorted [ints]."""
    out: set[int] = set()
    for part in str(spec or "").replace(" ", "").split(","):
        if not part:
            continue
        if "-" in part.lstrip("-"):  # a range "a-b" (not a lone negative)
            a, _, b = part.partition("-")
            if a.lstrip("-").isdigit() and b.isdigit():
                out.update(range(int(a), int(b) + 1))
        elif part.lstrip("-").isdigit():
            out.add(int(part))
    return sorted(out)


def summarise_class_ranges(scheme: str, suitable: str, not_suitable: str = "") -> dict:
    """Decode `classes_suitable` / `classes_not_suitable` range specs against a legend.

    For relationship-coded class evidence (e.g. HWSD soil-quality "classes_suitable": "1-4").
    """
    legend = load(scheme)
    inc = expand_codes(suitable)
    exc = expand_codes(not_suitable)
    return {
        "scheme": scheme,
        "n_included": len(inc),
        "included": [(c, legend.get(c, "")) for c in inc],
        "excluded": [(c, legend.get(c, "")) for c in exc],
    }


# ── CDL GEE-mask parsing ─────────────────────────────────────────────────────
_NEQ = re.compile(r"\.neq\(\s*(\d+)\s*\)")
_OP = {"lte": "<=", "gte": ">=", "eq": "==", "neq": "!="}
# the transformed predicate must contain ONLY these chars before we eval it (safety)
_SAFE = re.compile(r"^[c0-9<>=!()&|orandt \.]*$")


def _mask_predicate(expr: str) -> str:
    """Translate a GEE band mask (``band.lte(61).or(band.gte(205).and(...))``) into a
    Python boolean expression over a single code variable ``c`` — evaluated per code, so
    operator precedence/chaining is handled exactly rather than guessed with regex."""
    # strip JS wrapping that EV quotes carry: `var X = …`, `//comments`, trailing `;`
    expr = re.sub(r"//[^\n]*", " ", expr)
    expr = re.sub(r"\bvar\s+\w+\s*=\s*", "", expr)
    expr = expr.replace(";", " ")
    # band.OP(n)  →  (c OP n)
    pred = re.sub(
        r"\w+\.(lte|gte|eq|neq)\(\s*(\d+)\s*\)",
        lambda m: f"(c {_OP[m.group(1)]} {m.group(2)})",
        expr,
    )
    pred = pred.replace(".or(", " or (").replace(".and(", " and (")
    return pred


def codes_from_cdl_mask(expr: str, legend_codes: set[int] | None = None) -> set[int]:
    """Compute the exact set of legend codes a CDL inclusion mask selects.

    Evaluates the translated predicate against every legend code. Robust for any
    lte/gte/eq/neq + and/or mask (no range-guessing). Restricted to legend codes so phantom
    ints never appear; rejects anything that doesn't translate to a safe arithmetic predicate.
    """
    universe = legend_codes if legend_codes is not None else set(load("cdl"))
    pred = _mask_predicate(expr)
    if not _SAFE.match(
        pred
    ):  # un-translatable token → refuse rather than eval-injecting
        raise ValueError(f"unsafe/unparseable CDL mask predicate: {pred[:80]!r}")
    return {c for c in universe if eval(pred, {"__builtins__": {}}, {"c": c})}  # noqa: S307


def summarise_cdl_mask(expr: str) -> dict:
    """Readable summary of a CDL inclusion mask: included names + excluded names."""
    legend = load("cdl")
    included = codes_from_cdl_mask(expr, set(legend))
    excluded = {int(k) for k in _NEQ.findall(expr)}
    return {
        "scheme": "cdl",
        "n_included": len(included),
        "included": sorted((c, legend.get(c, "")) for c in included),
        "excluded": sorted((c, legend.get(c, "")) for c in excluded),
    }


def main() -> int:
    import sys

    # CLI: decode a CDL mask expression (or fall back to the saraheb3 default).
    expr = (
        " ".join(sys.argv[1:])
        or "cropLandcover.lte(61).or(cropLandcover.gte(205).and(cropLandcover.lte(209)))"
        ".or((cropLandcover.gte(213)).and((cropLandcover.neq(215)).and(cropLandcover.neq(217))"
        ".and(cropLandcover.neq(218)).and(cropLandcover.neq(220)).and(cropLandcover.neq(223))))"
    )
    s = summarise_cdl_mask(expr)
    print(f"CDL mask → {s['n_included']} included classes")
    print("  INCLUDED:", ", ".join(f"{c} {lbl}" for c, lbl in s["included"]))
    print("  EXCLUDED:", ", ".join(f"{c} {lbl}" for c, lbl in s["excluded"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
