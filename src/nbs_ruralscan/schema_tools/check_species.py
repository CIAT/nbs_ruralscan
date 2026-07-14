"""Deterministic SPECIES-ENVELOPE MIS-TAG check (2026-07 sweep-retro).

`species_envelope` is the 3rd-biggest recurring QA reason (29 in the July batch) and — unlike
off_scope / wrong_practice / smuggled-numbers — had NO deterministic catch. The schema
already models the right thing: a per-species claim carries `claim_scope=species_specific`
(or `crop_specific`) + a `taxon`, and `synthesis.py` routes those OUT of the practice-level
T4 suitability surface while KEEPING them in the register for reuse. The defect is an
extractor MIS-TAG: a species claim left as `claim_scope=practice_technology`, so it leaks
into the practice suitability instead of the species lane. 12 of the 29 July drops were
exactly this (tagged practice_technology).

This flags that mis-tag deterministically, every build (advisory — never fatal). Three
layers (the first is the strongest; the other two from Pete's 2026-07 note that "the article
title/abstract often indicates species-specificity"):

* field-level (`species_mistag_taxon_set`): a `taxon` is FILLED but claim_scope is still
  practice_technology. The spec requires taxon only when claim_scope ≠ practice_technology, so
  this is a definitional mis-tag — list-independent (catches any genus, e.g. Artocarpus).
* evidence-level (`species_mistag`): the QUOTE names a taxon but claim_scope=practice_technology
* source-level  (`species_hint_citation`): the SRC CITATION (carries the title) names a taxon
  and claim_scope=practice_technology, even if this particular quote doesn't

The right FIX for a flag is to **retag** (`claim_scope=species_specific` + `taxon`) and KEEP —
never drop; the evidence is banked for a future species-level layer. Resolved (reviewer_ok)
and dropped rows are skipped.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
SRC = ROOT / "schema" / "registers" / "SRC_source_register.csv"

# Curated genera that recur in agroforestry / crop suitability sources (trees, shade/crop
# species, staples). A `Genus epithet` hit here is a strong species-envelope signal; the
# curated list keeps false positives down vs a bare "Capitalised word + lowercase word".
_GENERA = (
    "faidherbia|gliricidia|acacia|grevillea|leucaena|calliandra|senna|moringa|prosopis"
    "|eucalyptus|morus|falcataria|carica|oryza|zea|triticum|glycine|arachis|coffea"
    "|theobroma|cocos|musa|mangifera|persea|citrus|vitis|olea|juglans|populus|salix"
    "|pinus|tectona|khaya|azadirachta|jatropha|sesbania|cajanus|vigna|sorghum|manihot"
    "|hordeum|helianthus|gossypium|saccharum|elaeis|hevea|cedrela|swietenia|paulownia"
    "|albizia|inga|erythrina|paraserianthes|tamarindus|anacardium|psidium|annona"
)
# a curated genus followed by a lowercase species epithet, e.g. "Faidherbia albida"
_BINOMIAL = re.compile(rf"\b(?:{_GENERA})\s+[a-z]{{3,}}\b", re.I)
# botanical rank / open-nomenclature markers: "sp.", "spp.", "var.", "cv.", "subsp.", cultivar
_TAXON_MARKER = re.compile(
    r"\b(?:spp?\.|var\.|subsp\.|cv\.|cultivars?)\b|\bssp\b", re.I
)


def _has_taxon(text: str) -> bool:
    return bool(_BINOMIAL.search(text) or _TAXON_MARKER.search(text))


def _citations() -> dict[str, str]:
    if not SRC.exists():
        return {}
    with SRC.open(newline="", encoding="utf-8") as f:
        return {r["source_id"]: (r.get("citation") or "") for r in csv.DictReader(f)}


def check(ev_path: str | Path | None = None) -> list[dict]:
    """Return advisory species-mis-tag flags: [{evidence_id, signal, snippet}].

    Only structural_suitability rows tagged practice_technology are candidates — a row already
    tagged species_specific/crop_specific is handled correctly and skipped.
    """
    path = Path(ev_path) if ev_path else EV
    flags: list[dict] = []
    if not path.exists():
        return flags
    cites = _citations()
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r.get("review_state") or "") == "dropped":
                continue
            if (r.get("reviewer_ok") or "").lower() == "true":
                continue
            if r.get("use_role") != "structural_suitability":
                continue
            if (r.get("claim_scope") or "practice_technology") != "practice_technology":
                continue  # already scoped to a species/crop lane — correct
            # Strongest, list-independent signal: a `taxon` is filled but claim_scope is still
            # practice_technology. The spec requires taxon ONLY when claim_scope ≠ practice_tech,
            # so a taxon on a practice-scoped row is definitionally a mis-tag — regardless of
            # whether the genus is in our curated list (catches e.g. Artocarpus, Intsia).
            if (r.get("taxon") or "").strip():
                flags.append(
                    {
                        "evidence_id": r["evidence_id"],
                        "signal": "species_mistag_taxon_set",
                        "snippet": f"taxon={r['taxon']} but claim_scope=practice_technology",
                    }
                )
                continue
            quote = r.get("quote") or ""
            m = _BINOMIAL.search(quote) or _TAXON_MARKER.search(quote)
            if m:
                s = max(0, m.start() - 20)
                flags.append(
                    {
                        "evidence_id": r["evidence_id"],
                        "signal": "species_mistag",
                        "snippet": quote[s : m.end() + 20].strip(),
                    }
                )
                continue
            cit = cites.get(r.get("source_id") or "", "")
            if _has_taxon(cit):
                flags.append(
                    {
                        "evidence_id": r["evidence_id"],
                        "signal": "species_hint_citation",
                        "snippet": cit[:80].strip(),
                    }
                )
    return flags


def main(argv: list[str] | None = None) -> int:
    flags = check(argv[0] if argv else None)
    if not flags:
        print("SPECIES CHECK: no species mis-tag signals in active, unreviewed units.")
        return 0
    from collections import Counter

    by = Counter(f["signal"] for f in flags)
    print(
        f"SPECIES CHECK (advisory): {len(flags)} practice-tagged unit(s) that look "
        "species-specific — retag claim_scope=species_specific + taxon (keep, don't drop):"
    )
    for sig, n in by.most_common():
        print(f"  {n}  {sig}")
    for f in flags:
        print(f"  [{f['signal']}] {f['evidence_id']}: …{f['snippet']}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
