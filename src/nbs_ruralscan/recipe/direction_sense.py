"""What a coded `relationship.direction` means for each outcome variable.

`direction` is always on the variable AS NAMED (extraction contract §2.2 rule 1):
`erosion_hazard` + `negative` = erosion went down, which is a benefit. Shown raw, that reads
as "bad". This module turns (variable, direction, use_role, framing) into words a reviewer
cannot misread, from `schema/lookups/variable_direction_sense.csv`.
"""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

SENSE_CSV = (
    Path(__file__).resolve().parents[3]
    / "schema"
    / "lookups"
    / "variable_direction_sense.csv"
)
ASSET_ROLE = "asset_vulnerability"


@lru_cache(maxsize=1)
def load_sense(path: str | Path = SENSE_CSV) -> dict[str, dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as f:
        return {r["variable"]: r for r in csv.DictReader(f)}


def verdict(
    variable: str, direction: str, use_role: str = "nbs_effect", framing: str = ""
) -> str:
    """benefit | harm | no_effect | context | unknown, in the practice-PRESENT frame."""
    if direction == "none":
        return "no_effect"
    if direction not in ("positive", "negative"):
        return "unknown"
    up = direction == "positive"
    if framing == "loss":
        up = not up  # measured on losing the practice: its presence does the reverse
    if use_role == ASSET_ROLE:
        return "harm" if up else "benefit"
    hi = (load_sense().get(variable) or {}).get("high_is", "")
    if hi == "good":
        return "benefit" if up else "harm"
    if hi == "bad":
        return "harm" if up else "benefit"
    return "context" if hi == "context" else "unknown"


def reads(
    variable: str, direction: str, use_role: str = "nbs_effect", framing: str = ""
) -> dict[str, str]:
    """{'arrow', 'words', 'verdict', 'text'} for display, e.g. '↓ less erosion · benefit'."""
    s = load_sense().get(variable) or {}
    v = verdict(variable, direction, use_role, framing)
    if direction == "positive":
        arrow = "↑"
        words = (
            "the hazard damages the NbS (how much: the strength class)"
            if use_role == ASSET_ROLE
            else s.get("positive_means", "")
        )
    elif direction == "negative":
        arrow = "↓"
        words = (
            "the NbS is not damaged"
            if use_role == ASSET_ROLE
            else s.get("negative_means", "")
        )
    elif direction == "none":
        arrow, words = "○", "no clear effect"
    else:
        arrow, words = "?", "direction not coded"
    label = {
        "benefit": "benefit",
        "harm": "harm",
        "no_effect": "",
        "context": "good or bad depends on context",
        "unknown": "",
    }[v]
    text = f"{arrow} {words}".strip()
    if framing == "loss" and direction in ("positive", "negative"):
        text += " when the practice is LOST"
    if label and use_role == ASSET_ROLE:
        text += " · " + ("damage to the NbS" if v == "harm" else "the NbS holds up")
    elif label:
        text += f" · {label} of the practice"
    return {"arrow": arrow, "words": words, "verdict": v, "text": text}
