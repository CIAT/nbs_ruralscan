"""Pipeline progress tracker — a one-glance view of how far the evidence pipeline has got.

Run: `uv run python3 src/nbs_ruralscan/schema_tools/status.py`

Reports the funnel: candidates discovered -> PDFs cached -> sources registered ->
units staged (extracted, not yet merged) -> units in the EV register (verified) ->
flagged for review. No side effects; read-only.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _read_csv(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with p.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _bar(done: int, total: int, width: int = 24) -> str:
    if total <= 0:
        return "[" + " " * width + "] n/a"
    filled = round(width * done / total)
    return f"[{'#' * filled}{'.' * (width - filled)}] {done}/{total} ({100 * done // total}%)"


def main() -> int:
    reg = ROOT / "schema" / "registers"
    corpus = ROOT / ".cache" / "corpus"
    staging = ROOT / "pipeline" / "staging"
    inbox = ROOT / "pipeline" / "inbox"

    src = _read_csv(reg / "SRC_source_register.csv")
    ev = _read_csv(reg / "EV_evidence_register.csv")
    cand = _read_csv(inbox / "candidates.csv")

    pdfs = (
        [p for p in corpus.glob("*.pdf") if p.stat().st_size > 0]
        if corpus.exists()
        else []
    )

    # staging units not yet in EV register
    ev_ids = {r["evidence_id"] for r in ev}
    staged_units = 0
    staged_unmerged = 0
    staged_sources: set[str] = set()
    if staging.exists():
        for f in staging.glob("*.json"):
            try:
                rows = json.loads(f.read_text())
            except Exception:
                continue
            staged_units += len(rows)
            for u in rows:
                staged_sources.add(u.get("source_id", f.stem))
                if u.get("evidence_id") not in ev_ids:
                    staged_unmerged += 1

    print("\n=== NbS Rural Scan — evidence pipeline status ===\n")

    print("DISCOVERY")
    if cand:
        pr = Counter(c.get("priority", "?") for c in cand)
        print(
            f"  candidates listed : {len(cand)}  (priority {dict(sorted(pr.items()))})"
        )
    print(f"  PDFs cached       : {len(pdfs)}")

    print("\nSOURCES (SRC register)")
    print(f"  registered        : {len(src)}")
    print(
        f"    by kind         : {dict(Counter(s.get('source_kind', '?') for s in src))}"
    )
    print(
        f"    by access_status: {dict(Counter(s.get('access_status', '?') for s in src))}"
    )
    print(
        f"    by extraction   : {dict(Counter(s.get('extraction_status', '?') for s in src))}"
    )

    print("\nEXTRACTION (staging — not yet merged)")
    print(f"  staged units total: {staged_units}")
    print(f"  awaiting merge    : {staged_unmerged}")
    print(f"  sources staged    : {len(staged_sources)}")

    print("\nREGISTER (EV — verbatim-verified)")
    print(f"  units             : {len(ev)}")
    if ev:
        role = Counter(r.get("use_role", "?") for r in ev)
        print(f"    by use_role     : {dict(role)}")
        flagged = sum(1 for r in ev if "[VERIFY-FLAG" in (r.get("attribution") or ""))
        low = sum(1 for r in ev if r.get("extraction_confidence") == "low")
        rel = sum(1 for r in ev if (r.get("relationship") or "").strip())
        print(f"    numeric (rel)   : {rel}")
        print(f"    flagged review  : {flagged}")
        print(f"    low confidence  : {low}")
        top = Counter(r.get("source_id", "?") for r in ev).most_common(5)
        print(f"    top sources     : {top}")

    # funnel: registered sources that have >=1 EV row vs pending
    ev_srcs = {r["source_id"] for r in ev}
    extracted = sum(1 for s in src if s["source_id"] in ev_srcs)
    print("\nFUNNEL")
    print(f"  sources extracted : {_bar(extracted, len(src))}")
    if cand:
        p1 = [c for c in cand if c.get("priority") == "1"]
        p1_done = sum(
            1
            for c in p1
            if c["source_id"] in staged_sources or c["source_id"] in ev_srcs
        )
        print(f"  priority-1 swept  : {_bar(p1_done, len(p1))}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
