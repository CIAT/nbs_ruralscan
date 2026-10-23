#!/usr/bin/env python3
"""Log the ORIGINAL studies behind second-hand effect evidence, for later acquisition.

    python3 scripts/log-cited-originals.py [--out pipeline/cited_originals.csv]

A `cited_secondary` unit is a paper repeating someone else's finding (Patil 2025 quoting
Beer et al. 1998). Until the original is acquired and read, the claim is credited to the
paper that repeats it, and two reviews citing the same original count twice. This script
lists every original, so it can be queued, acquired and verified; the weighting is
revisited once the originals are in hand (Pete 2026-10-23).

Per original (author + year key) it records: the label as cited, the full reference
text found in the host paper's reference list (auto-located in the cached PDF — check
before queueing), the units and host sources that cite it, a registered source with the
same author + year (a CANDIDATE: confirm by title), whether the acquisition queue already
holds it, and a status:

  linked               lineage_of already points at a registered source / evidence id
  registered_candidate a source we hold has the same first author + year (confirm by title)
  in_queue             the acquisition queue already lists it
  reference_found      full reference located in the host PDF; ready to verify + queue
  citation_only        only the in-text label is known (no reference text found)
  unattributed         the unit names no original at all (lineage blank, none in the quote)

Per-unit companion: scripts/log-primary-references.py (one row per second-hand unit and
how many generated rows it feeds). This file is one row per ORIGINAL, with `rows_fed` =
generated T3/T6 rows that its citing units sit in, so the acquisition round starts where
it changes most.

Read-only: never edits registers or the queue. Effect roles only (nbs_effect,
asset_vulnerability).
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
SRC = ROOT / "schema" / "registers" / "SRC_source_register.csv"
QUEUE = ROOT / "pipeline" / "acquisition_queue.csv"
CORPUS = ROOT / ".cache" / "corpus"
OUT = ROOT / "pipeline" / "cited_originals.csv"
EFFECT_ROLES = {"nbs_effect", "asset_vulnerability"}
RECIPES = ROOT / "schema" / "recipes"


def rows_fed_by_unit() -> dict[str, int]:
    c: dict[str, int] = defaultdict(int)
    for f in sorted(RECIPES.glob("*/T[36]_*.csv")):
        with f.open(newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                try:
                    for eid in json.loads(r.get("evidence_ids") or "[]"):
                        c[eid] += 1
                except json.JSONDecodeError:
                    continue
    return c


_YEAR = r"(1[89]\d{2}|20\d{2})[a-z]?"
_CITE = re.compile(
    r"([A-Z][A-Za-zÀ-ſ'\-]+(?:[ -][A-Z][A-Za-zÀ-ſ'\-]+)?)"
    r"(?:\s+et\s+al\.?|\s+(?:and|&|y|et)\s+[A-Z][A-Za-zÀ-ſ'\-]+)?,?\s*\(?" + _YEAR
)
_NUMREF = re.compile(r"\[(\d{1,3})\]")
_REF_HEAD = re.compile(
    r"\n\s*(references|literature cited|bibliography|références|bibliographie|"
    r"referencias|bibliografía|referências)\s*\n",
    re.I,
)
_STOP = {"The", "In", "This", "For", "Table", "Figure", "Fig", "See", "However", "And"}


def keys_in(text: str) -> list[tuple[str, str, str]]:
    """[(key, surname, year)] for in-text citations like 'Beer et al., 1998'."""
    out, seen = [], set()
    for m in _CITE.finditer(text or ""):
        name, year = m.group(1).strip(), m.group(2)
        first = name.split()[0]
        if first in _STOP:
            continue
        key = f"{first.lower()}_{year}"
        if key not in seen:
            seen.add(key)
            out.append((key, first, year))
    return out


_PDF_TEXT: dict[str, str] = {}


def _refs_text(source_id: str) -> str:
    if source_id in _PDF_TEXT:
        return _PDF_TEXT[source_id]
    txt = ""
    pdf = CORPUS / f"{source_id}.pdf"
    if pdf.exists():
        try:
            import fitz

            with fitz.open(pdf) as doc:
                full = "\n".join(p.get_text() for p in doc)
            heads = list(_REF_HEAD.finditer(full))
            txt = full[heads[-1].end() :] if heads else full[int(len(full) * 0.6) :]
        except Exception:
            txt = ""
    _PDF_TEXT[source_id] = txt
    return txt


def find_reference(source_id: str, surname: str, year: str, num: str = "") -> str:
    refs = _refs_text(source_id)
    if not refs:
        return ""
    if num:
        m = re.search(
            rf"(?:^|\n)\s*\[?{num}[\].]\s+(.{{20,400}}?)(?=\n\s*\[?\d{{1,3}}[\].]\s|\Z)",
            refs,
            re.S,
        )
        return " ".join(m.group(1).split())[:400] if m else ""
    for m in re.finditer(rf"(?:^|\n)\s*{re.escape(surname)}\b", refs):
        chunk = refs[m.start() : m.start() + 450]
        if year in chunk[:120]:
            nxt = re.search(r"\n[A-Z][A-Za-zÀ-ſ'\-]+,\s+[A-Z]", chunk[40:])
            chunk = chunk[: 40 + nxt.start()] if nxt else chunk
            ref = " ".join(chunk.split())[:400]
            if sum(c.isdigit() for c in ref) > 0.25 * len(ref):
                continue  # a table row, not a reference entry
            return ref
    return ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    with EV.open(newline="", encoding="utf-8") as f:
        ev = list(csv.DictReader(f))
    with SRC.open(newline="", encoding="utf-8") as f:
        src = list(csv.DictReader(f))
    with QUEUE.open(newline="", encoding="utf-8") as f:
        queue = list(csv.DictReader(f))
    ev_ids = {r["evidence_id"] for r in ev}
    src_ids = {s["source_id"] for s in src}
    reg_by_key: dict[str, list[str]] = defaultdict(list)
    for s in src:
        for k, _, _ in keys_in(s.get("citation", ""))[:1]:
            reg_by_key[k].append(s["source_id"])
    q_by_key: dict[str, list[str]] = defaultdict(list)
    for q in queue:
        for k, _, _ in keys_in(q.get("citation", ""))[:1]:
            q_by_key[k].append(q["source_id"])

    log: dict[str, dict] = {}

    def entry(key: str, label: str) -> dict:
        return log.setdefault(
            key,
            {
                "origin_key": key,
                "cited_as": label,
                "reference_text": "",
                "reference_found_in": "",
                "cited_by_units": set(),
                "host_sources": set(),
                "nbs_ids": set(),
                "status": "",
                "registered_candidate": "",
                "in_queue": "",
            },
        )

    for r in ev:
        if (
            r.get("review_state") == "dropped"
            or r.get("use_role") not in EFFECT_ROLES
            or r.get("claim_basis") != "cited_secondary"
        ):
            continue
        lin = (r.get("lineage_of") or "").strip()
        host, eid = r["source_id"], r["evidence_id"]
        if lin in ev_ids or lin in src_ids:
            e = entry(f"linked:{lin}", lin)
            e["status"] = "linked"
        else:
            found = keys_in(lin) or keys_in(r.get("quote", ""))
            nums = _NUMREF.findall(lin) if not found else []
            if not found and not nums:
                e = entry(f"unattributed:{eid}", "")
                e["status"] = "unattributed"
                e["cited_by_units"].add(eid)
                e["host_sources"].add(host)
                e["nbs_ids"].add(r.get("nbs_id", ""))
                continue
            targets = [(k, f"{s} {y}", s, y, "") for k, s, y in found] + [
                (f"{host}#ref{n}", f"[{n}] in {host}", "", "", n) for n in nums
            ]
            for key, label, surname, year, num in targets:
                e = entry(key, label)
                if not e["reference_text"]:
                    ref = find_reference(host, surname, year, num)
                    if ref:
                        e["reference_text"], e["reference_found_in"] = ref, host
                e["cited_by_units"].add(eid)
                e["host_sources"].add(host)
                e["nbs_ids"].add(r.get("nbs_id", ""))
            continue
        e["cited_by_units"].add(eid)
        e["host_sources"].add(host)
        e["nbs_ids"].add(r.get("nbs_id", ""))

    for key, e in log.items():
        if e["status"]:
            continue
        reg = [s for s in reg_by_key.get(key, []) if s not in e["host_sources"]]
        e["registered_candidate"] = "|".join(reg)
        e["in_queue"] = "|".join(q_by_key.get(key, []))
        e["status"] = (
            "registered_candidate"
            if reg
            else "in_queue"
            if e["in_queue"]
            else "reference_found"
            if e["reference_text"]
            else "citation_only"
        )

    reach = rows_fed_by_unit()
    rows: list[dict[str, Any]] = []
    for e in log.values():
        rows.append(
            {
                **e,
                "rows_fed": sum(reach.get(u, 0) for u in e["cited_by_units"]),
                "n_host_sources": len(e["host_sources"]),
                "n_units": len(e["cited_by_units"]),
                "cited_by_units": "|".join(sorted(e["cited_by_units"])),
                "host_sources": "|".join(sorted(e["host_sources"])),
                "nbs_ids": "|".join(sorted(e["nbs_ids"])),
            }
        )
    order = [
        "registered_candidate",
        "in_queue",
        "reference_found",
        "citation_only",
        "linked",
        "unattributed",
    ]
    rows.sort(
        key=lambda x: (
            order.index(x["status"]),
            -x["rows_fed"],
            -x["n_host_sources"],
            -x["n_units"],
            x["origin_key"],
        )
    )
    cols = [
        "origin_key",
        "status",
        "cited_as",
        "rows_fed",
        "n_host_sources",
        "n_units",
        "reference_text",
        "reference_found_in",
        "registered_candidate",
        "in_queue",
        "host_sources",
        "nbs_ids",
        "cited_by_units",
    ]
    out = Path(a.out)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    by: dict[str, int] = defaultdict(int)
    for x in rows:
        by[x["status"]] += 1
    multi = sum(
        1
        for x in rows
        if x["n_host_sources"] > 1
        and not x["origin_key"].startswith(("linked:", "unattributed:"))
    )
    print(f"{len(rows)} rows -> {out}: {dict(by)}; originals cited by >1 host: {multi}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
