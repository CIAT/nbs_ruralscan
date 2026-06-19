"""Deterministic SECTION-SCOPE check (the dominant 2026-06-18 QA defect).

The verbatim guardrail proves a quote is real; `check_numbers` proves its numbers come
from the quote. Neither proves the quote is a SUITABILITY CLAIM. Human QA on 2026-06-18
dropped 12/15 reviewed units as `off_scope` — values lifted from sections that are NOT
suitability reasoning: study-site/characteristics tables, methods/study-area text,
carbon·CO2·biomass accounting, and generic problem statements. (See review_log notes.)

This flags the same class deterministically, every build, no model tokens: an EV quote
whose text signals one of those off-scope section types is flagged for review. Signals
are PROXIES — a real suitability claim can mention carbon — so this is ADVISORY (flags,
never fails the build). Use it to triage before an LLM verify pass and to stop
regressions; the `off_scope` rate must trend DOWN sweep-over-sweep.

Already-resolved rows (reviewer_ok) and quarantined rows (review_state=dropped) are
skipped — they've had their human call.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"

# off-scope section signals (case-insensitive), grouped by the defect they catch
_SIGNALS: dict[str, re.Pattern] = {
    "study_site": re.compile(
        r"study (site|area)|site characteristic|experimental (site|plot|design)"
        r"|the sites? (are|were|comprise)|located (in|within|at)|study region",
        re.I,
    ),
    "carbon_biomass": re.compile(
        r"\bCO2\b|\bCO₂\b|carbon (stock|sequestr|removal|dioxide|storage)"
        r"|sequestr|\bbiomass\b|\bPg ?C\b|tCO2|\bMg ?C\b|aboveground (carbon|biomass)",
        re.I,
    ),
    "problem_intro": re.compile(
        r"problem statement|in recent decades|globally,|is a (growing|major) (concern|problem)"
        r"|threatens? (food|livelihood)",
        re.I,
    ),
}


def check(ev_path: str | Path | None = None) -> list[dict]:
    """Return advisory off-scope flags: [{evidence_id, signal, snippet}]."""
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
            # off-scope here means "not a SUITABILITY claim" -> only T4 structural rows.
            # carbon/biomass is legitimate for T6 (nbs_effect) and fuel/biomass for T3
            # (hazard), so this check is scoped to structural_suitability only.
            if r.get("use_role") != "structural_suitability":
                continue
            quote = r.get("quote") or ""
            for name, pat in _SIGNALS.items():
                m = pat.search(quote)
                if m:
                    s = max(0, m.start() - 20)
                    flags.append(
                        {
                            "evidence_id": r["evidence_id"],
                            "signal": name,
                            "snippet": quote[s : m.end() + 20].strip(),
                        }
                    )
                    break  # one flag per row is enough for triage
    return flags


def main(argv: list[str] | None = None) -> int:

    flags = check(argv[0] if argv else None)
    if not flags:
        print("SCOPE CHECK: no off-scope signals in active, unreviewed units.")
        return 0
    from collections import Counter

    by = Counter(f["signal"] for f in flags)
    print(
        f"SCOPE CHECK (advisory): {len(flags)} unit(s) with off-scope signals — review:"
    )
    for sig, n in by.most_common():
        print(f"  {n}  {sig}")
    for f in flags:
        print(f"  [{f['signal']}] {f['evidence_id']}: …{f['snippet']}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
