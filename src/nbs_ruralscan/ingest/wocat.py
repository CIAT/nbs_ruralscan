"""WOCAT SLM Technologies — acquisition adapter + rule-based effect extraction.

The PDF export of a WOCAT technology sheet loses the questionnaire's ratings (the tick
position on the "decreased … increased" scale is graphical; the text layer keeps only the
endpoint labels). The QCAT web page embeds the structured questionnaire
(``/api/database/technologies/<id>/``) as a SvelteKit-fetched JSON block, so the adapter:

1. ACQUIRE — fetch ``https://qcat.wocat.net/en/wocat/technologies/view/technologies_<id>/``,
   pull the embedded JSON and cache it as ``.cache/corpus/<source_id>.source.json`` (raw,
   never the quote artefact) with a ``<source_id>.meta.json`` sidecar (url · fetched_at · sha1).
2. RENDER — write a DETERMINISTIC markdown transcript ``.cache/corpus/<source_id>.md``: one
   section per questionnaire group, one line per rated field (``field: value +3 (comment)``).
   This is the artefact of record for section-locator evidence: every quote is a line of it,
   verified by ``validate_sources`` like any other snapshot. The PDF (page locators, T4 units)
   stays the artefact for page evidence — a source may carry both.
3. EMIT — rule-based evidence units, no LLM: QT 6.1 / 6.2 impact ratings become
   ``nbs_effect`` units (``metric = ordinal_rating``, ``unit = wocat_impact``,
   ``source_scale_value = "+3"``; variable + right-label from
   ``schema/lookups/wocat_impact_map.csv``); QT 6.3 disaster-coping ratings become
   ``asset_vulnerability`` units (hazard from ``schema/lookups/wocat_hazard_map.csv``;
   strength from the BANDS ``wocat_tol_*`` rows). Compiler comments ride along in
   ``outcome_raw``; nothing is inferred from them (PICOS: no hazard from prose).

    python -m nbs_ruralscan.ingest.wocat acquire wocat_959_2010 ...
    python -m nbs_ruralscan.ingest.wocat emit --nbs water_harvesting_conservation \
        --out pipeline/staging/wh_wocat_effects.json wocat_959_2010 ...
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / ".cache" / "corpus"
LOOKUPS = ROOT / "schema" / "lookups"
EV_CSV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
PAGE_URL = "https://qcat.wocat.net/en/wocat/technologies/view/technologies_{id}/"
_BLOCK = re.compile(
    r'<script type="application/json" data-sveltekit-fetched data-url="([^"]+)"[^>]*>(.*?)</script>',
    re.S,
)
_IMPACT_GROUPS = (
    "impacts_socio_economic_production",
    "impacts_socio_economic_water",
    "impacts_socio_economic_income",
    "impacts_socio_economic_other",
    "impacts_socio_cultural",
    "impacts_ecological_water",
    "impacts_ecological_soil",
    "impacts_ecological_biodiversity",
    "impacts_ecological_climate",
    "impacts_ecological_other",
    "impacts_offsite",
)
_COPING_GROUPS = (
    "gradual_climate_change",
    "meteorological_disaster_coping",
    "climatological_disaster_coping",
    "hydrological_disaster_coping",
    "biological_disaster_coping",
    "other_disaster_coping",
    "other_climate_consequences_coping",
)
_COPE_SCALE = {
    "NOT_WELL_AT_ALL": "not well at all",
    "NOT_WELL": "not well",
    "MODERATELY": "moderately",
    "WELL": "well",
    "VERY_WELL": "very well",
}
#: coping → asset-damage direction: tolerates "very well" = no damage (direction none)
_COPE_DIRECTION = {
    "not well at all": "positive",
    "not well": "positive",
    "moderately": "positive",
    "well": "positive",
    "very well": "none",
}


def tech_id(source_id: str) -> int:
    m = re.match(r"wocat_(\d+)_", source_id)
    if not m:
        raise ValueError(f"not a WOCAT source id: {source_id}")
    return int(m.group(1))


def _en(v: Any) -> str:
    """English text of a translated field, whitespace-collapsed to ONE line (a comment
    with a newline would otherwise split the transcript line the quote must equal)."""
    if isinstance(v, dict):
        v = v.get("en") or next(iter(v.values()), "") or ""
    return " ".join(str(v or "").split())


# ── 1. acquire ────────────────────────────────────────────────────────────────────────


def fetch_payload(tid: int, timeout: int = 40) -> dict[str, Any]:
    url = PAGE_URL.format(id=tid)
    req = urllib.request.Request(
        url, headers={"User-Agent": "nbs-ruralscan/wocat-adapter"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310
        page = r.read().decode("utf-8", errors="replace")
    key = f"/api/database/technologies/{tid}/"
    for data_url, block in _BLOCK.findall(page):
        if data_url != key:
            continue
        outer = json.loads(html.unescape(block))
        body = outer.get("body") if isinstance(outer, dict) else None
        if isinstance(body, str):
            body = json.loads(body)
        if isinstance(body, dict) and "selected_version" in body:
            return body
    raise ValueError(
        f"technology {tid}: embedded questionnaire JSON not found at {url}"
    )


def acquire(source_id: str, corpus: Path = CORPUS) -> Path:
    tid = tech_id(source_id)
    payload = fetch_payload(tid)
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=1)
    corpus.mkdir(parents=True, exist_ok=True)
    (corpus / f"{source_id}.source.json").write_text(raw, encoding="utf-8")
    md = render(payload, source_id)
    (corpus / f"{source_id}.md").write_text(md, encoding="utf-8")
    meta = {
        "source_id": source_id,
        "adapter": "ingest/wocat.py",
        "url": PAGE_URL.format(id=tid),
        "api_path": f"/api/database/technologies/{tid}/",
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_sha1": hashlib.sha1(raw.encode("utf-8")).hexdigest(),
        "render_sha1": hashlib.sha1(md.encode("utf-8")).hexdigest(),
        "selected_version_id": (payload.get("selected_version") or {}).get("id"),
    }
    (corpus / f"{source_id}.meta.json").write_text(
        json.dumps(meta, indent=1), encoding="utf-8"
    )
    return corpus / f"{source_id}.md"


# ── 2. render (deterministic transcript) ─────────────────────────────────────────────


def _fmt_value(v: Any) -> str:
    try:
        n = int(v)
    except (TypeError, ValueError):
        return str(v)
    return f"{n:+d}" if n else "0"


def render(payload: dict[str, Any], source_id: str) -> str:
    sv = payload.get("selected_version") or {}
    lines = [
        f"# WOCAT technology {payload.get('id')} — {_en(sv.get('name'))}",
        "",
        f"source_id: {source_id}",
        f"country: {sv.get('country') or ''}",
        f"compiler: {_en(sv.get('compiler'))}",
        f"date_documentation: {sv.get('date_documentation') or ''}",
        f"slm_group: {', '.join(sv.get('slm_group') or [])}",
        "",
    ]
    for group in _IMPACT_GROUPS:
        g = sv.get(group)
        if not isinstance(g, dict):
            continue
        lines.append(f"## {group}")
        for field in sorted(k for k in g if k != "other"):
            item = g[field]
            if not isinstance(item, dict) or item.get("value") is None:
                continue
            line = f"- {field}: value {_fmt_value(item['value'])}"
            c = _en(item.get("comment"))
            if c:
                line += f" — comment: {c}"
            lines.append(line)
        for item in g.get("other") or []:
            if not isinstance(item, dict) or item.get("value") is None:
                continue
            line = (
                f"- other [{_en(item.get('name'))}]: value {_fmt_value(item['value'])}"
                f" (scale {_en(item.get('label_left'))} … {_en(item.get('label_right'))})"
            )
            c = _en(item.get("comment"))
            if c:
                line += f" — comment: {c}"
            lines.append(line)
        lines.append("")
    for group in _COPING_GROUPS:
        g = sv.get(group)
        if not g:
            continue
        lines.append(f"## {group}")
        if group == "gradual_climate_change":
            for key in sorted(g):
                v = g[key]
                items = v if isinstance(v, list) else [v]
                for it in items:
                    if not isinstance(it, dict) or not it.get("cope"):
                        continue
                    tag = f"{key}" + (f" ({it['season']})" if it.get("season") else "")
                    line = f"- {tag} [trend {it.get('trend') or '?'}]: copes {_COPE_SCALE.get(it['cope'], it['cope'])}"
                    spec = _en(it.get("other_specify"))
                    if spec:
                        line += f" — {spec}"
                    lines.append(line)
        else:
            for key in sorted(g):
                lines.append(
                    f"- {key}: copes {_COPE_SCALE.get(str(g[key]), str(g[key]))}"
                )
        lines.append("")
    for key in (
        "onsite_impacts_comments",
        "impacts_offsite_comments",
        "climate_change_comments",
        "costbenefit_comments",
    ):
        c = _en(sv.get(key))
        if c:
            lines += [f"## {key}", c, ""]
    for key in (
        "strengths_compiler",
        "weaknesses_compiler",
        "strengths_landuser",
        "weaknesses_landuser",
    ):
        items = sv.get(key) or []
        if items:
            lines.append(f"## {key}")
            for it in items:
                t = _en(it.get("text") if isinstance(it, dict) else it)
                if t:
                    lines.append(f"- {t}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# ── 3. emit (rule-based units) ──────────────────────────────────────────────────────


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _family_of(source_id: str, ev_csv: Path = EV_CSV) -> str:
    """Modal `suitability_family_id` of the source's existing EV rows (T4 sweep), else ''."""
    from collections import Counter

    c: Counter[str] = Counter()
    if ev_csv.exists():
        for r in _load_csv(ev_csv):
            if r["source_id"] == source_id and r.get("suitability_family_id"):
                c[r["suitability_family_id"]] += 1
    return c.most_common(1)[0][0] if c else ""


_INCREASE_LABELS = {"increased", "improved", "strengthened", "enhanced"}


def emit_units(
    source_id: str,
    payload: dict[str, Any],
    md: str,
    nbs_id: str,
    family: str,
    impact_map: list[dict[str, str]],
    hazard_map: list[dict[str, str]],
    bands: list[dict[str, Any]],
    ruleset_version: str = "v1.6.2",
) -> list[dict[str, Any]]:
    from nbs_ruralscan.recipe.cell_synthesis import classify_magnitude

    sv = payload.get("selected_version") or {}
    md_lines = set(md.splitlines())
    # WOCAT stores ISO2; the context vocabulary is ISO3 + WB income group (lookup)
    iso2 = str(sv.get("country") or "").upper()
    base_ctx: dict[str, Any] = {}
    for r in _load_csv(LOOKUPS / "wb_income_groups.csv"):
        if r["iso2"] == iso2 or r["iso3"] == iso2:
            base_ctx = {"country": [r["iso3"]], "income_group": r["income_group"]}
            break
    units: list[dict[str, Any]] = []
    n = 0

    def _mk(
        eid: str,
        variable: str,
        role: str,
        quote: str,
        locator: str,
        rel: dict[str, Any],
        ctx: dict[str, Any],
    ) -> dict[str, Any]:
        assert quote in md_lines, (
            f"render drift: quote not a line of the transcript: {quote}"
        )
        return {
            "evidence_id": eid,
            "source_id": source_id,
            "nbs_id": nbs_id,
            "suitability_family_id": family,
            "variable": variable,
            "use_role": role,
            "evidence_type": "literature_relationship",
            "claim_basis": "expert_assertion",
            "claim_scope": "practice_technology",
            "extraction_confidence": "high",
            "quote": quote,
            "locator_type": "section",
            "locator": locator,
            "page": "",
            "relationship": rel,
            "context": ctx,
            "ruleset_version": ruleset_version,
            "attribution": "ingest/wocat.py (rule-based, no LLM)",
        }

    # 6.1 / 6.2 impact ratings
    imap = {(r["wocat_group"], r["wocat_field"]): r for r in impact_map}
    for group in _IMPACT_GROUPS:
        g = sv.get(group)
        if not isinstance(g, dict):
            continue
        for field in sorted(k for k in g if k != "other"):
            m = imap.get((group, field))
            item = g[field]
            if m is None or not isinstance(item, dict) or item.get("value") is None:
                continue
            v = int(item["value"])
            line = f"- {field}: value {_fmt_value(v)}"
            comment = _en(item.get("comment"))
            if comment:
                line += f" — comment: {comment}"
            right_up = m["right_label"].strip().lower() in _INCREASE_LABELS
            # value sign is towards the right label; direction is on the QUANTITY
            quantity_up = (v > 0) == right_up
            direction = (
                "none" if v == 0 else ("positive" if quantity_up else "negative")
            )
            note = m.get("note") or ""
            if "direction inverted on emit" in note and v != 0:
                direction = "negative" if direction == "positive" else "positive"
            scale = _fmt_value(v)
            cls = (
                "unspecified"
                if v == 0
                else classify_magnitude(
                    "ordinal_rating",
                    None,
                    bands,
                    source_scale_value=scale,
                    unit="wocat_impact",
                )
            )
            n += 1
            units.append(
                _mk(
                    # locator-based id: stable across re-emits (a sequential counter
                    # shifted when UNKNOWN coping rows were skipped → duplicates, 2026-10-06)
                    f"ev_{m['canonical_variable_id']}_{source_id}_{field}",
                    m["canonical_variable_id"],
                    m["use_role"],
                    line,
                    f"{group}/{field}",
                    {
                        "direction": direction,
                        "metric": "ordinal_rating",
                        "source_scale_value": scale,
                        "unit": "wocat_impact",
                        "strength_class": cls,
                        "design": "practitioner_rating",
                        "significance": "not_reported",
                        "outcome_raw": f"WOCAT {group}.{field} rated {scale} on the −3…+3 scale (right label '{m['right_label']}')"
                        + (f"; compiler: {comment}" if comment else ""),
                        "note": f"compiler rating, QT 6.{'2' if group == 'impacts_offsite' else '1'}; label mapping per schema/lookups/wocat_impact_map.csv",
                    },
                    dict(base_ctx),
                )
            )
    # 6.3 coping with climate-related extremes → asset vulnerability
    hmap = {(r["wocat_group"], r["wocat_key"]): r["hazard_type"] for r in hazard_map}
    for group in _COPING_GROUPS:
        g = sv.get(group)
        if not isinstance(g, dict) or group == "gradual_climate_change":
            continue
        for key in sorted(g):
            hz = hmap.get((group, key))
            if not hz or str(g[key]) not in _COPE_SCALE:
                # UNKNOWN / null coping is not a rating (T3 prose review 2026-10-06:
                # four "copes UNKNOWN" units had entered as threats)
                continue
            cope = _COPE_SCALE[str(g[key])]
            line = f"- {key}: copes {cope}"
            cls = classify_magnitude(
                "ordinal_rating", None, bands, source_scale_value=cope
            )
            n += 1
            units.append(
                _mk(
                    f"ev_asset_{hz}_{source_id}_{key}",
                    "climate_shock",
                    "asset_vulnerability",
                    line,
                    f"{group}/{key}",
                    {
                        "direction": _COPE_DIRECTION.get(cope, "positive"),
                        "metric": "ordinal_rating",
                        "source_scale_value": cope,
                        "strength_class": cls,
                        "design": "practitioner_rating",
                        "significance": "not_reported",
                        "outcome_raw": f"WOCAT QT 6.3: the Technology copes {cope} with {key.replace('_', ' ')}",
                        "note": "compiler tolerance rating; hazard per schema/lookups/wocat_hazard_map.csv; BANDS wocat_tol_* → asset_sensitivity",
                    },
                    dict(base_ctx, hazard_type=hz),
                )
            )
    return units


# ── CLI ───────────────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("acquire")
    a.add_argument("source_ids", nargs="+")
    e = sub.add_parser("emit")
    e.add_argument("source_ids", nargs="+")
    e.add_argument("--nbs", required=True)
    e.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    if args.cmd == "acquire":
        for sid in args.source_ids:
            try:
                p = acquire(sid)
                print(f"  acquired {sid} → {p.name}")
            except Exception as ex:  # noqa: BLE001
                print(f"  FAILED {sid}: {ex}", file=sys.stderr)
        return 0
    from nbs_ruralscan.recipe.cell_synthesis import load_bands

    bands = load_bands(ROOT / "schema" / "registers" / "BANDS_magnitude_bands.csv")
    imap = _load_csv(LOOKUPS / "wocat_impact_map.csv")
    hmap = _load_csv(LOOKUPS / "wocat_hazard_map.csv")
    fam_nbs = {
        r["suitability_family_id"]: r["nbs_id"]
        for r in _load_csv(ROOT / "schema" / "registers" / "FAM_family_registry.csv")
    }
    out: list[dict[str, Any]] = []
    for sid in args.source_ids:
        src = CORPUS / f"{sid}.source.json"
        md = CORPUS / f"{sid}.md"
        if not src.exists() or not md.exists():
            print(f"  skip {sid}: not acquired", file=sys.stderr)
            continue
        payload = json.loads(src.read_text(encoding="utf-8"))
        family = _family_of(sid)
        # PICOS: the practice is the one the sheet's T4 family already names; a sheet
        # filed under another NbS (an ANR entry in the WH queue) emits under THAT NbS
        nbs = fam_nbs.get(family, args.nbs) if family else args.nbs
        if nbs != args.nbs:
            print(
                f"  note {sid}: family {family} → emitted under {nbs}, not {args.nbs}"
            )
        units = emit_units(
            sid,
            payload,
            md.read_text(encoding="utf-8"),
            nbs,
            family,
            imap,
            hmap,
            bands,
        )
        print(f"  {sid}: {len(units)} unit(s), family {family or '(none)'}")
        out += units
    Path(args.out).write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(f"{len(out)} unit(s) → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
