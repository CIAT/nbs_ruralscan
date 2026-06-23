"""Deterministic PICOS / wrong-practice check (the #2 QA defect, 2026-06-23).

`check_scope` proves a quote is a suitability claim about the right *section*; this proves
it is about the right *practice*. PICOS discipline (locked): the NbS practice must be
EVIDENCED in the source — a paper about **reforestation**, **afforestation**, **pure
forestry / plantation**, or the **climate-smart-agriculture (CSA) umbrella** is NOT
evidence for agroforestry suitability. 2026-06-23 human QA dropped these as `wrong_practice`
(e.g. fesenmyer25 reforestation, brandt2015 CSA umbrella) — the agent had borrowed the
agroforestry tag from sweep context, not from the source.

This flags the same class deterministically: an agroforestry `structural_suitability` row
whose quote signals a NON-agroforestry practice **and** carries NO agroforestry/silvo
signal. Signals are PROXIES (a paper can contrast AF *with* reforestation), so a row that
also mentions agroforestry is NOT flagged — advisory, used to feed auto-quarantine + triage.

Already-resolved (`reviewer_ok`) and quarantined (`review_state=dropped`) rows are skipped.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"

# A non-agroforestry practice presented as THE intervention (not agroforestry).
_WRONG_PRACTICE = re.compile(
    r"\breforestation\b|\bafforestation\b|\breforest(ing|ed)?\b"
    r"|climate[- ]smart agriculture|\bCSA\b"
    r"|pure forestry|plantation forest|forest plantation|monoculture plantation"
    r"|\bforest restoration\b|\bplantation(s)?\b",
    re.I,
)

# An agroforestry / silvo signal — its presence cancels the wrong-practice flag
# (the source genuinely concerns agroforestry, perhaps contrasting it with the above).
_AF_SIGNAL = re.compile(
    r"agro[- ]?forest|agro[- ]?silvo|silvo[- ]?(pastor|arable|culture)"
    r"|alley crop|shelterbelt|windbreak|parkland|hedgerow|home ?garden"
    r"|farmer[- ]managed natural regeneration|\bFMNR\b|fallow"
    r"|shaded (perennial|coffee|cocoa|cacao)|tree(s)? on farm|on[- ]farm tree"
    r"|intercrop\w* (with )?tree|scattered tree",
    re.I,
)


def check(ev_path: str | Path | None = None) -> list[dict]:
    """Return advisory wrong-practice flags: [{evidence_id, signal, snippet}]."""
    path = Path(ev_path) if ev_path else EV
    flags: list[dict] = []
    if not path.exists():
        return flags
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r.get("review_state") or "") == "dropped":
                continue
            if (r.get("reviewer_ok") or "").lower() == "true":
                continue
            # PICOS applies to the practice claim — only structural_suitability rows tag a
            # suitability_family_id / nbs_id that this catches mis-borrowing on.
            if r.get("use_role") != "structural_suitability":
                continue
            if (r.get("nbs_id") or "") != "agroforestry":
                continue
            quote = r.get("quote") or ""
            m = _WRONG_PRACTICE.search(quote)
            if not m:
                continue
            if _AF_SIGNAL.search(quote):
                continue  # source genuinely concerns agroforestry — not a mis-map
            s = max(0, m.start() - 20)
            flags.append(
                {
                    "evidence_id": r["evidence_id"],
                    "signal": "wrong_practice:" + m.group(0).lower(),
                    "snippet": quote[s : m.end() + 20].strip(),
                }
            )
    return flags


def main(argv: list[str] | None = None) -> int:
    flags = check(argv[0] if argv else None)
    if not flags:
        print("PICOS CHECK: no wrong-practice signals in active, unreviewed AF units.")
        return 0
    print(f"PICOS CHECK (advisory): {len(flags)} unit(s) with wrong-practice signals:")
    for f in flags:
        print(f"  [{f['signal']}] {f['evidence_id']}: …{f['snippet']}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
