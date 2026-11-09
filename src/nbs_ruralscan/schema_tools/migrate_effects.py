"""Migrate archived T3/T6 evidence units into the v1.6.0 effect-claim shape (PR4).

Method: ``methodology/T3_T6_generation_method.md`` §10. Only units from sources found by a
**T3/T6-targeted** search re-enter (Pete, 2026-09-30: T4-net effect rows are incidental, not
evidence-targeted). Everything here is DETERMINISTIC — no model call. Where the archived unit
carries an authored class (``mitigation_potential``, ``effect_direction``) it is reduced to
the direction it implies; the class itself is never trusted (defect E1/E3) — it is kept in
``context.note`` for audit and the engine re-derives strength from BANDS or leaves it
``unspecified``.

Quote / page / source are untouched: the verbatim guardrail re-verifies them on the live
register. The archive file is left intact (it is the restorable record); the ids
selected in each completed import are listed in ``schema/registers/_deferred/migrated_<date>.txt``.
The receipt includes matching existing rows; the separate appended count measures new EV rows.
The first migration date stays in each existing EV context. Unhashed historical receipt headings
are recognised for the pinned September 2026 archive; other archive bytes or names use SHA-256.

Rules (per unit)
----------------
role        climate_risk → nbs_effect (→ asset_vulnerability when the archived
            risk_role was asset_threat); nbs_effect unchanged.
direction   1) relationship.direction if valid; 2) sign of the authored effect_direction
            (inverted for high_is_bad outcome variables); 3) an authored
            mitigation_potential on a hazard outcome → 'negative' (hazard impact reduced),
            'none' → 'none'; 4) economic_return with a positive return figure → 'positive';
            5) otherwise ABSENT (the engine excludes the unit from direction/strength and
            keeps it for magnitude / economics only).
metric      hedges g → smd_hedges_g (central, ci → magnitude/_low/_high, p → significance);
            pct_increase → pct_change; recognised money / rate keys → absolute with the
            archived unit; else narrative (direction only) or absolute without magnitude.
strength    BANDS from metric+magnitude, else 'unspecified'.
context     fixed keys only: country (ISO3 via the WB lookup names), income_group (lookup;
            Castle SR = LMIC scope → lic_lmic), aez / farming_system (unit, else SRC, T7 only),
            hazard_type (enum only — 'erosion' is not a hazard), timescale_of_effect (enum
            only), landscape_scale_only; everything else → note.
stamp       ruleset_version = v1.6.0; review_state / reviewer_ok preserved.
"""

from __future__ import annotations

import csv
import hashlib
import json
import io
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from nbs_ruralscan.ingest.integrity import atomic_write
from nbs_ruralscan.recipe.cell_synthesis import classify_magnitude, load_bands
from nbs_ruralscan.schema_tools.record_publication import edit_records
from nbs_ruralscan.schema_tools.review_inputs import ReviewInputs
from nbs_ruralscan.schema_tools.specialist_records import read_table, write_table

ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "schema"
DEFERRED = SCHEMA / "registers" / "_deferred" / "EV_T3_T6_deferred_2026-09.json"
EV_CSV = SCHEMA / "registers" / "EV_evidence_register.csv"
SRC_CSV = SCHEMA / "registers" / "SRC_source_register.csv"
T7_CSV = SCHEMA / "T7_geographic_context.csv"
BANDS_CSV = SCHEMA / "registers" / "BANDS_magnitude_bands.csv"
INCOME_CSV = SCHEMA / "lookups" / "wb_income_groups.csv"

RULESET = "v1.6.0"
# The September 2026 archive predates digest-bearing migration receipts.
_LEGACY_ARCHIVE_SHA256 = (
    "40ef18a44c1d4afedcd182a0c3be18db7b85d0ece1ccc997e8d1685338bc16a2"
)

#: sources whose units came in via a T3/T6-targeted search (method §10 table)
TARGETED_SOURCES = {
    "batcheler_silvopasture_2024",
    "castle_sr_2021",
    "quandt_resilience_2017",
    "wb_fsrp_2022",
    "wb_kcsap_2016",
}
HAZARDS = {
    "drought",
    "flood",
    "heat_stress",
    "fire",
    "wind_cyclone",
    "waterlogging",
    "frost",
}
TIMESCALES = {
    "immediate",
    "short_term_1_3yr",
    "medium_term_3_7yr",
    "long_term_7yr_plus",
}
#: outcome variables where "more" is worse — an authored effect_direction on them is in the
#: benefit frame and must be inverted back to the outcome-as-measured frame
HIGH_IS_BAD = {
    "erosion_hazard",
    "drought_hazard",
    "flood_hazard",
    "fire_hazard",
    "climate_shock",
    "project_cost",
    "economic_cost",
}
#: hazard-IMPACT outcomes: an authored "mitigates" class ⇒ the outcome goes DOWN (negative)
HAZARD_IMPACT_OUTCOMES = {
    "drought_hazard",
    "flood_hazard",
    "fire_hazard",
    "erosion_hazard",
    "climate_shock",
}
#: PROTECTIVE-service outcomes: "mitigates" ⇒ the service goes UP (positive)
PROTECTIVE_OUTCOMES = {
    "soil_water_retention",
    "microclimate_buffering",
    "windbreak_protection",
}
HAZARD_OUTCOMES = HAZARD_IMPACT_OUTCOMES | PROTECTIVE_OUTCOMES
#: directional variable names whose recorded direction is that of the underlying hazard →
#: resolve to the hazard variable (VONT alias level; raw_name keeps the original)
VARIABLE_ALIASES = {"wildfire_mitigation": "fire_hazard"}
ECON_RETURN_VARS = {"economic_return"}
_COUNTRY_ALIASES = {
    "united states": "USA",
    "usa": "USA",
    "u.s.": "USA",
    "us": "USA",
    "kenya": "KEN",
    "ethiopia": "ETH",
    "madagascar": "MDG",
    "malawi": "MWI",
    "niger": "NER",
    "tanzania": "TZA",
    "brazil": "BRA",
    "india": "IND",
    "burkina faso": "BFA",
    "italy": "ITA",
    "sweden": "SWE",
}
_NON_COUNTRY = {
    "global",
    "regional",
    "multi",
    "lmics",
    "ssa",
    "sub-saharan africa",
    "eastern and southern africa (mpa)",
}


# ── lookups ──────────────────────────────────────────────────────────────────────────


def _obj(v: Any) -> dict[str, Any]:
    if isinstance(v, dict):
        return v
    if not v:
        return {}
    try:
        o = json.loads(v)
    except Exception:
        return {}
    return o if isinstance(o, dict) else {}


def load_income(path: Path = INCOME_CSV) -> tuple[dict[str, str], dict[str, str]]:
    """(iso3 → income_group, lower-cased country name → iso3)."""
    iso_inc: dict[str, str] = {}
    name_iso: dict[str, str] = {}
    if path.exists():
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                iso_inc[r["iso3"]] = r["income_group"]
                name_iso[r["country_name"].strip().lower()] = r["iso3"]
    name_iso.update({k: v for k, v in _COUNTRY_ALIASES.items()})
    return iso_inc, name_iso


def load_t7(path: Path = T7_CSV) -> tuple[set[str], set[str]]:
    aez: set[str] = set()
    fs: set[str] = set()
    if path.exists():
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                (
                    aez
                    if r.get("context_type") == "aez"
                    else fs
                    if r.get("context_type") == "farming_system"
                    else set()
                ).add(r["context_id"])
    return aez, fs


def load_src(path: Path = SRC_CSV) -> dict[str, dict[str, str]]:
    _, sources = _register(Path(path), "source_id")
    return sources


def countries_from_text(text: str | None, name_iso: dict[str, str]) -> list[str]:
    """ISO3 codes named in a free-text country / region string (deterministic substring
    match on WB country names + aliases). 'Global' / 'Regional' → []."""
    if not text:
        return []
    t = str(text).strip().lower()
    if t in _NON_COUNTRY:
        return []
    if re.fullmatch(r"[A-Z]{3}", str(text).strip()):
        return [str(text).strip()]
    hits: list[tuple[int, str]] = []
    for name, iso in name_iso.items():
        if len(name) < 4:
            continue
        mt = re.search(r"\b" + re.escape(name) + r"\b", t)
        if mt and iso not in {i for _, i in hits}:
            hits.append((mt.start(), iso))
    return [iso for _, iso in sorted(hits)]  # text order → deterministic


# ── per-unit transform ───────────────────────────────────────────────────────────────


_SIGN = {"positive": "positive", "negative": "negative", "none": "none"}


def _dir_from_effect_direction(ed: str, variable: str) -> str | None:
    ed = (ed or "").lower()
    if ed == "no_relationship":
        return "none"
    if ed.endswith("_positive"):
        s = "positive"
    elif ed.endswith("_negative"):
        s = "negative"
    else:
        return None
    if (
        variable in HIGH_IS_BAD
    ):  # authored class was in the benefit frame → outcome frame
        s = "negative" if s == "positive" else "positive"
    return s


def _significance(p: Any) -> str:
    if p is None or p == "":
        return "not_reported"
    if isinstance(p, str):
        s = p.strip()
        if s.startswith("<"):
            try:
                return "sig" if float(s[1:]) <= 0.05 else "ns"
            except ValueError:
                return "not_reported"
        try:
            p = float(s)
        except ValueError:
            return "not_reported"
    return "sig" if float(p) <= 0.05 else "ns"


def _first_numeric(rel: dict[str, Any], keys: list[str]) -> tuple[str, float] | None:
    for k in keys:
        v = rel.get(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return k, float(v)
    return None


def build_relationship(
    unit: dict[str, Any], bands: list[dict[str, Any]]
) -> dict[str, Any]:
    rel = _obj(unit.get("relationship"))
    ctx = _obj(unit.get("context"))
    variable = unit.get("variable", "")
    out: dict[str, Any] = {}

    # direction
    d = str(rel.get("direction") or "").lower()
    direction = _SIGN.get(d)
    if direction is None and ctx.get("effect_direction"):
        direction = _dir_from_effect_direction(str(ctx["effect_direction"]), variable)
    if (
        direction is None
        and ctx.get("mitigation_potential")
        and variable in HAZARD_OUTCOMES
    ):
        mp = str(ctx["mitigation_potential"]).lower()
        worsens = mp in {"very_negative", "negative"}
        if mp == "none":
            direction = "none"
        elif variable in PROTECTIVE_OUTCOMES:
            direction = "negative" if worsens else "positive"  # service up = mitigation
        else:
            direction = "positive" if worsens else "negative"  # hazard impact down

    # metric / magnitude
    metric: str | None = None
    unit_s: str | None = str(rel.get("unit")) if rel.get("unit") else None
    est = str(rel.get("effect_size_type") or "").lower()
    if "hedges" in est or "standardized_mean_difference" in est:
        metric = "smd_hedges_g"
        unit_s = "unitless"
        if isinstance(rel.get("central"), (int, float)):
            out["magnitude"] = float(rel["central"])
        for k_in, k_out in (("ci_low", "magnitude_low"), ("ci_high", "magnitude_high")):
            if isinstance(rel.get(k_in), (int, float)):
                out[k_out] = float(rel[k_in])
        out["significance"] = _significance(rel.get("p_value"))
        if direction is None and "magnitude" in out:
            direction = (
                "positive"
                if out["magnitude"] > 0
                else "negative"
                if out["magnitude"] < 0
                else "none"
            )
    elif isinstance(rel.get("pct_increase"), (int, float)):
        metric = "pct_change"
        unit_s = "percent"
        out["magnitude"] = float(rel["pct_increase"])
        out["significance"] = _significance(rel.get("p_value"))
        if direction is None:
            direction = "positive" if out["magnitude"] > 0 else "negative"
    else:
        hit = _first_numeric(
            rel,
            [
                "npv_incremental_usd_per_acre",
                "annual_net_benefit_usd_per_acre",
                "eirr_percent",
                "threshold",
                "opt_low",
                "npv_usd_million",
                "total_project_cost_usd_million",
                "component1_upscaling_csa_usd_million",
                "total_cofinancing_usd_million",
                "low",
                "central",
                "value",
            ],
        )
        if hit:
            metric = "absolute"
            key, val = hit
            out["magnitude"] = val
            if key == "opt_low" and isinstance(rel.get("opt_high"), (int, float)):
                out["magnitude_low"] = val
                out["magnitude_high"] = float(rel["opt_high"])
            if key == "low" and isinstance(rel.get("high"), (int, float)):
                out["magnitude_low"] = val
                out["magnitude_high"] = float(rel["high"])
            if (
                key == "npv_incremental_usd_per_acre"
                or key == "annual_net_benefit_usd_per_acre"
            ):
                unit_s = "usd_per_acre"
            elif key in ("eirr_percent", "threshold") or (
                key == "opt_low" and "eirr" in str(unit_s)
            ):
                unit_s = "percent_eirr"
            elif key.endswith("usd_million") or unit_s == "usd_million":
                unit_s = "usd_million"
            if direction is None and variable in ECON_RETURN_VARS:
                direction = "positive" if val > 0 else "negative" if val < 0 else "none"
        elif direction is not None:
            metric = "narrative"
    if metric is None:
        metric = "absolute"  # no number, no direction — catalogued only

    if direction is not None:
        out["direction"] = direction
    out["metric"] = metric
    if unit_s:
        out["unit"] = unit_s
    if "significance" not in out and rel.get("p_value") is not None:
        out["significance"] = _significance(rel.get("p_value"))
    out["strength_class"] = (
        classify_magnitude(
            metric, out.get("magnitude"), bands, unit=str(out.get("unit") or "")
        )
        if "magnitude" in out
        else "unspecified"
    )
    note = (
        str(ctx.get("claim_basis_note") or "").lower()
        + " "
        + str(rel.get("model") or "").lower()
    )
    if "meta" in note or "random_effects" in note:
        out["design"] = "meta_analysis"
    raw = unit.get("raw_name") or rel.get("outcome") or rel.get("qualifier")
    if raw:
        out["outcome_raw"] = str(raw)[:200]
    if rel:
        out["legacy"] = (
            rel  # archived shape kept verbatim for audit (numbers already quote-checked)
        )
    return out


def _migration_stamp(day: date) -> str:
    return f"migrated v1.5.0→{RULESET} {day.isoformat()} (deterministic re-shape, method §10)"


def build_context(
    unit: dict[str, Any],
    src: dict[str, str],
    iso_inc: dict[str, str],
    name_iso: dict[str, str],
    aez_ids: set[str],
    fs_ids: set[str],
    run_day: date | None = None,
) -> dict[str, Any]:
    ctx = _obj(unit.get("context"))
    out: dict[str, Any] = {}
    leftovers: list[str] = []

    # country
    countries: list[str] = []
    for k in (
        "country",
        "countries",
        "country_context",
        "study_country",
        "location",
        "study_region",
        "context_location",
    ):
        if ctx.get(k):
            for iso in countries_from_text(str(ctx[k]), name_iso):
                if iso not in countries:
                    countries.append(iso)
    if not countries:
        countries = countries_from_text(src.get("study_country"), name_iso)
    if countries:
        out["country"] = countries
    # income group
    groups = {iso_inc[c] for c in countries if c in iso_inc}
    if len(groups) == 1:
        out["income_group"] = groups.pop()
    elif groups and groups <= {"low", "lower_middle"}:
        out["income_group"] = "lic_lmic"
    elif (src.get("region") or "").strip().lower() == "lmics":
        out["income_group"] = (
            "lic_lmic"  # e.g. Castle 2021: SR scoped to LMICs by title
        )
    # aez / farming system (T7 vocab only)
    for k, ids, extra in (("aez", aez_ids, set()), ("farming_system", fs_ids, {"all"})):
        v = str(ctx.get(k) or "").strip() or str(src.get(k) or "").strip()
        if v and v in ids | extra:
            out[k] = v
        elif v:
            leftovers.append(f"{k}={v}")
    # hazard keys
    hz = str(ctx.get("hazard_type") or "").strip()
    if hz in HAZARDS:
        out["hazard_type"] = hz
    elif hz:
        leftovers.append(f"hazard_type={hz} (not a T3 hazard; routed by XW)")
    ts = str(ctx.get("timescale_of_effect") or ctx.get("timescale") or "").strip()
    if ts in TIMESCALES:
        out["timescale_of_effect"] = ts
    elif ts:
        leftovers.append(f"timescale={ts}")
    ls = ctx.get("landscape_scale_only", ctx.get("landscape_scale"))
    if isinstance(ls, bool) or str(ls).lower() in ("true", "false"):
        out["landscape_scale_only"] = str(ls).lower() == "true"
    # everything else → note (authored classes kept for audit, never trusted)
    consumed = {
        "country",
        "countries",
        "country_context",
        "study_country",
        "location",
        "study_region",
        "context_location",
        "aez",
        "farming_system",
        "hazard_type",
        "timescale_of_effect",
        "timescale",
        "landscape_scale_only",
        "landscape_scale",
    }
    for k, v in ctx.items():
        if k in consumed or v in (None, ""):
            continue
        leftovers.append(
            f"{k}={json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v}"
        )
    stamp = _migration_stamp(run_day or date.today())
    out["note"] = "; ".join([stamp] + leftovers)[:1500]
    return out


def migrate_unit(
    unit: dict[str, Any],
    src: dict[str, str],
    bands: list[dict[str, Any]],
    iso_inc: dict[str, str],
    name_iso: dict[str, str],
    aez_ids: set[str],
    fs_ids: set[str],
    run_day: date | None = None,
) -> dict[str, Any]:
    ctx_old = _obj(unit.get("context"))
    role = unit.get("use_role", "")
    if role == "climate_risk":
        role = (
            "asset_vulnerability"
            if str(ctx_old.get("risk_role") or "") == "asset_threat"
            else "nbs_effect"
        )
    new = dict(unit)
    new["use_role"] = role
    if unit.get("variable") in VARIABLE_ALIASES:
        new["raw_name"] = unit.get("raw_name") or unit.get("variable")
        new["variable"] = VARIABLE_ALIASES[unit["variable"]]
        unit = dict(unit, variable=new["variable"])
    new["relationship"] = build_relationship(unit, bands)
    new["context"] = build_context(
        unit, src, iso_inc, name_iso, aez_ids, fs_ids, run_day
    )
    new["ruleset_version"] = RULESET
    return new


# ── register I/O ─────────────────────────────────────────────────────────────────────


def _cell(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False, allow_nan=False)
    return str(v)


def _register(path: Path, key: str) -> tuple[list[str], dict[str, dict[str, str]]]:
    columns, rows = read_table(path, [key])
    records = {}
    for row in rows:
        value = row[key]
        if not value.strip() or value in records:
            raise ValueError(f"existing register has blank/duplicate {key}: {value!r}")
        records[value] = row
    return columns, records


def _with_first_migration_date(existing, generated):
    """Reproduce the exact archived stamp; every other note character and field still compares."""
    prior_note = existing.get("note") if isinstance(existing, dict) else None
    if not isinstance(prior_note, str):
        return generated
    first_stamp = prior_note.partition("; ")[0]
    match = re.search(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", first_stamp)
    if not match:
        return generated
    try:
        first_day = date.fromisoformat(match.group())
    except ValueError:
        return generated
    if first_stamp != _migration_stamp(first_day):
        return generated
    _, separator, remainder = generated["note"].partition("; ")
    return dict(generated, note=first_stamp + separator + remainder)


def _append(rows, ev_csv: Path, *, historical_replay: bool = False) -> int:
    cols, existing = _register(ev_csv, "evidence_id")
    seen: set[str] = set()
    for row in rows:
        eid = row["evidence_id"]
        if not isinstance(eid, str) or not eid.strip() or "\n" in eid or "\r" in eid:
            raise ValueError("evidence_id must be nonempty text on one line")
        if eid in seen:
            raise ValueError(f"duplicate evidence_id in batch: {eid}")
        seen.add(eid)
        previous = existing.get(eid)
        if previous is None:
            continue
        for key, value in row.items():
            # Review ownership stays with the review workflow, including on reruns.
            if key in {"reviewer_ok", "review_state"} or key not in cols:
                continue
            old, new_value = previous.get(key) or "", _cell(value)
            if key in {"context", "relationship"}:
                old = json.loads(old) if old else None
                new_value = json.loads(new_value) if new_value else None
                if historical_replay and key == "context" and old != new_value:
                    new_value = _with_first_migration_date(old, new_value)
                    if new_value == old:
                        row[key] = new_value
            if old != new_value:
                raise ValueError(
                    f"{eid}: existing evidence differs in {key}; use an audited correction, not append"
                )
    new = [r for r in rows if r["evidence_id"] not in existing]
    # Render the entire batch before touching disk. A malformed later row must not
    # leave earlier rows silently appended, even on a dry run.
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=cols, lineterminator="\n")
    for row in new:
        writer.writerow({c: _cell(row.get(c)) for c in cols})
    if new:
        previous_bytes = ev_csv.read_bytes()
        separator = b"" if previous_bytes.endswith(b"\n") else b"\n"
        atomic_write(
            ev_csv, previous_bytes + separator + buffer.getvalue().encode("utf-8")
        )
    return len(new)


def append_to_register(
    rows: list[dict[str, Any]], ev_csv: Path = EV_CSV, *, dry_run: bool = False
) -> int:
    ev_csv = Path(ev_csv)
    return edit_records(
        [ev_csv], lambda stage: _append(rows, stage[ev_csv]), dry_run=dry_run
    )


def stamp_extracted(
    source_ids: set[str],
    run_id: str,
    extractor: str,
    day: str,
    src_csv: Path = SRC_CSV,
) -> list[str]:
    """Stamp a fresh ingest while preserving each source's first extraction run."""
    src_csv = Path(src_csv)
    return edit_records(
        [src_csv],
        lambda stage: _stamp(source_ids, run_id, extractor, day, stage[src_csv]),
    )


def _stamp(
    source_ids: set[str],
    run_id: str,
    extractor: str,
    day: str,
    src_csv: Path,
) -> list[str]:
    """Mark sources whose units were just ingested as `swept` with this run's id.

    Promotion leaves a source `pending` (2026-10-28 hardening); only a real ingest moves it.
    A source already `swept` / `signed_off` keeps its status and first run id.
    """
    cols, sources = _register(src_csv, "source_id")
    rows = sources.values()
    stamped: list[str] = []
    for r in rows:
        if r["source_id"] in source_ids and (r.get("extraction_status") or "") in {
            "",
            "pending",
        }:
            r.update(
                extraction_status="swept",
                extraction_date=day,
                extraction_run_id=run_id,
                extractor=extractor,
            )
            stamped.append(r["source_id"])
    if stamped:
        write_table(src_csv, cols, rows)
    return sorted(stamped)


def resync_vars_extracted(
    source_ids: set[str], src_csv: Path = SRC_CSV, ev_csv: Path = EV_CSV
) -> dict[str, str]:
    """SRC.vars_extracted = distinct active EV variables per source (all live roles)."""
    src_csv, ev_csv = Path(src_csv), Path(ev_csv)
    return edit_records(
        [src_csv],
        lambda stage: _resync(source_ids, stage[src_csv], ev_csv),
        inputs=ReviewInputs([ev_csv]),
    )


def _resync(source_ids, src_csv: Path, ev_csv: Path) -> dict[str, str]:
    by_src: dict[str, set[str]] = defaultdict(set)
    _, evidence = _register(ev_csv, "evidence_id")
    for r in evidence.values():
        if (r.get("review_state") or "") == "dropped" or r.get("use_role") == "dataset":
            continue
        if r["source_id"] in source_ids:
            by_src[r["source_id"]].add(r["variable"])
    cols, sources = _register(src_csv, "source_id")
    rows = sources.values()
    changed: dict[str, str] = {}
    for r in rows:
        if r["source_id"] in source_ids:
            new = "|".join(sorted(by_src.get(r["source_id"], set())))
            if new != (r.get("vars_extracted") or ""):
                changed[r["source_id"]] = new
                r["vars_extracted"] = new
    for extra in ("study_income_group", "venue_type"):
        if extra not in cols:
            cols.append(extra)  # manifest-optional columns the CSV never carried
    write_table(src_csv, cols, rows)
    return changed


def backfill_src_context(
    source_ids: set[str], src_csv: Path = SRC_CSV, income_csv: Path = INCOME_CSV
) -> dict[str, dict[str, str]]:
    """Deterministic SRC back-fill: study_income_group from study_country; venue_type from
    source_kind; benchmark_tier lower-cased. Returns {source_id: {field: new}}."""
    src_csv, income_csv = Path(src_csv), Path(income_csv)
    return edit_records(
        [src_csv],
        lambda stage: _backfill(source_ids, stage[src_csv], income_csv),
        inputs=ReviewInputs([income_csv]),
    )


def _backfill(source_ids, src_csv: Path, income_csv: Path) -> dict[str, dict[str, str]]:
    iso_inc, name_iso = load_income(income_csv)
    cols, sources = _register(src_csv, "source_id")
    rows = sources.values()
    changed: dict[str, dict[str, str]] = {}
    for r in rows:
        if r["source_id"] not in source_ids:
            continue
        ch: dict[str, str] = {}
        if not r.get("study_income_group"):
            isos = countries_from_text(r.get("study_country"), name_iso)
            groups = {iso_inc[c] for c in isos if c in iso_inc}
            if len(groups) == 1:
                ch["study_income_group"] = groups.pop()
        if not r.get("venue_type"):
            kind = r.get("source_kind", "")
            if kind == "paper":
                ch["venue_type"] = "peer_reviewed_journal"
            elif kind == "grey_lit":
                ch["venue_type"] = "institutional_report"
        tier = r.get("benchmark_tier", "")
        if tier and tier != tier.lower():
            ch["benchmark_tier"] = tier.lower()
        if ch:
            r.update(ch)
            changed[r["source_id"]] = ch
    for extra in ("study_income_group", "venue_type"):
        if extra not in cols:
            cols.append(extra)  # manifest-optional columns the CSV never carried
    write_table(src_csv, cols, rows)
    return changed


def _transform(
    sources, deferred, archive_bytes, bands_csv, income_csv, t7_csv, src_csv, run_day
):
    units = json.loads(archive_bytes.decode("utf-8"))
    if not isinstance(units, list) or not all(isinstance(unit, dict) for unit in units):
        raise ValueError(f"{deferred.name}: expected a list of archived evidence units")
    sel = [u for u in units if u.get("source_id") in sources]
    bands = load_bands(bands_csv)
    iso_inc, name_iso = load_income(income_csv)
    aez_ids, fs_ids = load_t7(t7_csv)
    src = load_src(src_csv)
    missing = sorted({unit["source_id"] for unit in sel} - src.keys())
    if missing:
        raise ValueError(
            f"Archived evidence references missing source IDs: {', '.join(missing)}"
        )
    migrated = [
        migrate_unit(
            u, src[u["source_id"]], bands, iso_inc, name_iso, aez_ids, fs_ids, run_day
        )
        for u in sel
    ]
    summary: dict[str, Any] = {
        "selected": len(sel),
        "by_role": dict(_count(m["use_role"] for m in migrated)),
        "with_direction": sum(1 for m in migrated if "direction" in m["relationship"]),
        "with_magnitude": sum(1 for m in migrated if "magnitude" in m["relationship"]),
        "by_metric": dict(_count(m["relationship"]["metric"] for m in migrated)),
        "with_income_group": sum(
            1 for m in migrated if m["context"].get("income_group")
        ),
        "with_country": sum(1 for m in migrated if m["context"].get("country")),
        "dropped_state_preserved": sum(
            1 for m in migrated if m.get("review_state") == "dropped"
        ),
    }
    summary["units"] = migrated
    return summary


def _manifest_heading(archive: Path, archive_bytes: bytes) -> str:
    digest = hashlib.sha256(archive_bytes).hexdigest()
    label = archive.stem
    if archive.name != DEFERRED.name or digest != _LEGACY_ARCHIVE_SHA256:
        label += f" [sha256={digest}]"
    return (
        f"# evidence_ids migrated from {label} into the live register "
        f"under ruleset {RULESET} (method §10; only T3/T6-targeted sources)"
    )


def _merge_manifest(path: Path, heading: str, evidence_ids: list[str]) -> str:
    prior_ids = []
    if path.exists():
        previous = path.read_text(encoding="utf-8")
        header, separator, body = previous.partition("\n")
        if header != heading or not separator or not body.endswith("\n"):
            raise ValueError(
                f"{path.name}: existing migration manifest has a different archive or "
                "an incomplete record. Reconcile the dated manifest before retrying."
            )
        prior_ids = body[:-1].split("\n") if body != "\n" else []
        if any(not eid.strip() for eid in prior_ids) or len(prior_ids) != len(
            set(prior_ids)
        ):
            raise ValueError(
                f"{path.name}: reconcile blank or duplicate IDs before retrying"
            )
    all_ids = list(dict.fromkeys([*prior_ids, *evidence_ids]))
    return heading + "\n" + "\n".join(all_ids) + "\n"


def run(
    sources: set[str] = TARGETED_SOURCES,
    *,
    root: Path = ROOT,
    deferred: Path | None = None,
    write: bool = True,
) -> dict[str, Any]:
    """Transform the selected archive. A write publishes EV, SRC and the dated ID list together."""
    root = Path(root).resolve()
    registers = root / "schema/registers"
    archive = (
        Path(deferred)
        if deferred is not None
        else registers / "_deferred" / DEFERRED.name
    )
    bands = registers / BANDS_CSV.name
    income = root / "schema/lookups" / INCOME_CSV.name
    t7 = root / "schema" / T7_CSV.name
    ev, src = registers / EV_CSV.name, registers / SRC_CSV.name
    inputs = ReviewInputs([archive, bands, income, t7])
    archive_bytes = archive.read_bytes()
    run_day = date.today()
    if not write:
        inputs.include([src])
        summary = _transform(
            sources, archive, archive_bytes, bands, income, t7, src, run_day
        )
        inputs.verify()
        return summary

    manifest = registers / "_deferred" / f"migrated_{run_day.isoformat()}.txt"
    manifest_text = ""

    def apply(stage):
        nonlocal manifest_text
        summary = _transform(
            sources, archive, archive_bytes, bands, income, t7, stage[src], run_day
        )
        migrated = summary["units"]
        summary["appended"] = _append(migrated, stage[ev], historical_replay=True)
        summary["src_backfill"] = _backfill(sources, stage[src], income)
        summary["vars_extracted_changed"] = _resync(sources, stage[src], stage[ev])
        manifest_text = _merge_manifest(
            stage[manifest],
            _manifest_heading(archive, archive_bytes),
            [m["evidence_id"] for m in migrated],
        )
        stage[manifest].write_text(manifest_text, encoding="utf-8")
        summary["manifest"] = str(manifest.relative_to(root))
        return summary

    def validate_manifest(path):
        if path.read_text(encoding="utf-8") != manifest_text:
            raise ValueError("Staged manifest differs from migrated evidence IDs")

    return edit_records(
        [ev, src, manifest],
        apply,
        inputs=inputs,
        validators={manifest: validate_manifest},
    )


def _count(it):
    from collections import Counter

    return Counter(it)


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument(
        "--dry-run", action="store_true", help="transform + summarise, write nothing"
    )
    ap.add_argument("--source", action="append", help="restrict to these source_ids")
    ap.add_argument(
        "--root",
        "--data-root",
        type=Path,
        default=ROOT,
        help="Checkout containing the selected schema and registers",
    )
    ap.add_argument(
        "--deferred",
        type=Path,
        help="Archived evidence JSON (default: the selected root’s September 2026 archive)",
    )
    args = ap.parse_args(argv)
    sources = set(args.source) if args.source else TARGETED_SOURCES
    s = run(sources, root=args.root, deferred=args.deferred, write=not args.dry_run)
    units = s.pop("units")
    print(json.dumps(s, indent=2, ensure_ascii=False))
    if args.dry_run:
        for m in units[:5]:
            print(
                json.dumps(
                    {
                        k: m[k]
                        for k in ("evidence_id", "use_role", "relationship", "context")
                    },
                    indent=1,
                    ensure_ascii=False,
                )[:900]
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
