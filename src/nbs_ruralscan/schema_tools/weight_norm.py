"""Cross-source weight normalisation (the `uninterpretable_weight` synthesis half).

Extracted weights come in incompatible encodings: AHP priority shares (0–1, Σ=1),
random-forest relative importance (0–1, Σ=1), raw RF importance (unbounded), and tool
slider intensities (0–N, NOT Σ=1). A bare "5" or "0.24" is not comparable across sources
until put on a common footing. This module does that deterministically.

KEY SEMANTIC — two bases that must NOT be averaged together:
  * SHARE     — a fraction of a source's total importance (Σ=1 across that source's vars).
                AHP/RF weights are shares. Comparable as "what fraction of importance".
  * INTENSITY — a value on its own fixed scale (e.g. a 0–10 slider), independent per var,
                NOT a share. Tool defaults are intensities → normalised = value / scale_max.

So a tool weight of 5/10 (intensity 0.5) is NOT the same thing as an AHP weight of 0.5
(half of all importance). `compare()` groups by variable and reports each source's value
WITH its basis so a reader never conflates the two. This is an EVIDENCE-comparison view —
our MCDA still computes its own weights at runtime (CRITIC/Entropy/AHP); literature
weights are benchmark, never injected as MCDA inputs.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

# weight-key → (basis, is_share). Order = precedence when a row carries several.
_WEIGHT_KEYS: list[tuple[str, str, bool]] = [
    ("ahp_weight", "ahp_priority_share", True),
    ("relative_weight", "rf_relative_share", True),
    ("variable_importance", "rf_importance_raw", False),  # → normalised ÷ source sum
    ("weight", "tool_slider_intensity", False),  # → normalised ÷ scale_max
]
# tool slider scale ceilings by criterion (saraheb3 app: erosion/SOC 0–10, others 0–5).
_TOOL_SCALE_MAX = {
    "water_erosion": 10,
    "wind_erosion": 10,
    "soil_carbon_(soc)": 10,
}
_DEFAULT_TOOL_MAX = 10


def _rows(schema_root: Path) -> list[dict]:
    ev = schema_root / "registers" / "EV_evidence_register.csv"
    if not ev.exists():
        return []
    with ev.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def extract(schema_root: str | Path = "schema") -> list[dict]:
    """Pull every weight-bearing active EV row → {source_id, variable, kind, basis, raw}."""
    out: list[dict] = []
    for r in _rows(Path(schema_root)):
        if (r.get("review_state") or "") == "dropped":
            continue
        rel = (r.get("relationship") or "").strip()
        if not rel:
            continue
        try:
            d = json.loads(rel)
        except (json.JSONDecodeError, TypeError):
            continue
        for key, basis, is_share in _WEIGHT_KEYS:
            if key in d and isinstance(d[key], (int, float)):
                out.append(
                    {
                        "source_id": r.get("source_id", ""),
                        "variable": r.get("variable", ""),
                        "kind": key,
                        "basis": basis,
                        "is_share": is_share,
                        "raw": float(d[key]),
                        "criterion": str(d.get("criterion", "")).lower(),
                    }
                )
                break  # one weight kind per row
    return out


def normalise(schema_root: str | Path = "schema") -> list[dict]:
    """Add a 0–1 `normalised` value to each weight, per its basis (never mixing bases)."""
    items = extract(schema_root)
    # raw RF importance → share within its source (÷ that source's total raw importance)
    src_imp_sum: dict[str, float] = defaultdict(float)
    for it in items:
        if it["kind"] == "variable_importance":
            src_imp_sum[it["source_id"]] += it["raw"]
    for it in items:
        k = it["kind"]
        if k in ("ahp_weight", "relative_weight"):
            it["normalised"] = round(it["raw"], 4)  # already a 0–1 share
        elif k == "variable_importance":
            tot = src_imp_sum.get(it["source_id"], 0.0)
            it["normalised"] = round(it["raw"] / tot, 4) if tot > 0 else None
            it["basis"] = "rf_importance_share"  # now a share after ÷sum
            it["is_share"] = True
        elif k == "weight":
            mx = _TOOL_SCALE_MAX.get(it["criterion"], _DEFAULT_TOOL_MAX)
            it["normalised"] = round(it["raw"] / mx, 4)
            it["scale_max"] = mx
    return items


def compare(schema_root: str | Path = "schema") -> dict[str, list[dict]]:
    """Group normalised weights by variable for cross-source comparison."""
    by_var: dict[str, list[dict]] = defaultdict(list)
    for it in normalise(schema_root):
        by_var[it["variable"]].append(it)
    return dict(sorted(by_var.items()))


def main() -> int:
    import sys

    root = sys.argv[1] if len(sys.argv) > 1 else "schema"
    cmp = compare(root)
    if not cmp:
        print("WEIGHT-NORM: no weight-bearing evidence found.")
        return 0
    print(
        "CROSS-SOURCE WEIGHT COMPARISON (normalised 0–1; SHARE vs INTENSITY not mixed):"
    )
    for var, items in cmp.items():
        print(f"\n  {var}")
        for it in items:
            n = it.get("normalised")
            tag = "share" if it["is_share"] else "intensity"
            print(
                f"    {it['source_id']:24} {it['kind']:20} raw={it['raw']:<7} "
                f"→ {n} ({tag})"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
