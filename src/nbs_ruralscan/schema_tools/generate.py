"""Generate the schema JSON files from their CSV source-of-truth.

CSVs are the human-editable form; the JSONs are typed artefacts the code reads
(``binding.py``, ``structure.py``, Colab notebooks). Editing both by hand is a
recipe for drift, so JSON is **generated** from CSV — never edited directly.

Conversion rule, per cell: try ``json.loads`` — succeeds → typed value (numbers,
booleans, ``null``, nested ``[...]``/``{...}``); fails → kept as the raw string.
Empty cells are dropped (the structure validator treats missing == empty).

The set of tables is driven by the frozen manifest (``schema/structure/columns.json``)
so working CSVs not in the manifest (e.g. the ``CV_*`` lit-review sheets) are left alone.

Usage::

    python3 src/nbs_ruralscan/schema_tools/generate.py schema           # (re)write all JSONs
    python3 src/nbs_ruralscan/schema_tools/generate.py schema --check    # CI: fail if any JSON is stale

Stdlib only.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import hashlib
import re
import sys
from pathlib import Path
from typing import Any

from nbs_ruralscan.schema_tools.build_paths import SchemaBuildPaths, source_revision


def _coerce(value: str):
    """Typed value for a CSV cell; raw string if it isn't valid JSON."""
    if value == "":
        return None  # signals "drop this key"
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def _csv_to_rows(path: Path) -> list[dict]:
    try:
        with path.open(newline="", encoding="utf-8") as fh:
            rows = []
            for raw in csv.DictReader(fh):
                row = {k: _coerce(v) for k, v in raw.items() if v is not None}
                rows.append({k: v for k, v in row.items() if v is not None})
            return rows
    except UnicodeDecodeError as e:
        # name the offending file (issue: Namita's opaque "utf-8 codec can't decode byte
        # 0xe7" popup gave no filename). A stray non-UTF-8 byte usually means a local cp1252
        # write — re-save the file as UTF-8 or `git restore` it (the committed copy is clean).
        raise ValueError(
            f"{path} is not valid UTF-8 (byte 0x{e.object[e.start]:02x} at position "
            f"{e.start}). Re-save it as UTF-8 or `git restore {path}` (committed copy is clean)."
        ) from e


def _csv_files(schema_root: Path, location: str) -> list[Path]:
    """Resolve a manifest ``location`` to existing CSV source files."""
    stem = location.split(".")[0]
    glob = stem.replace("<nbs_id>", "*")
    return sorted(schema_root.glob(glob + ".csv"))


def generate_progress_report(
    schema_root: Path, check: bool = False, *, dest: Path | None = None
) -> list[Path]:
    """Generates docs/progress.json summarizing literature registers status."""
    src_csv = schema_root / "registers" / "SRC_source_register.csv"
    if not src_csv.exists():
        return []

    from collections import Counter

    git_commit = source_revision(schema_root.parent)

    nbs_stats: dict[str, dict[str, Any]] = {}
    with src_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("source_id"):
                continue
            # register list fields are "|"-separated (";" tolerated from older rows)
            nbs_ids = [
                n.strip()
                for n in re.split(r"[|;]", row.get("nbs_ids", ""))
                if n.strip()
            ]
            status = row.get("extraction_status", "pending") or "pending"
            tier = row.get("benchmark_tier", "low") or "low"
            method = row.get("method_type", "empirical") or "empirical"
            country = row.get("study_country", "") or ""
            vars_list = [
                v.strip()
                for v in re.split(r"[|;]", row.get("vars_extracted", ""))
                if v.strip()
            ]

            for nbs in nbs_ids:
                if nbs not in nbs_stats:
                    nbs_stats[nbs] = {
                        "total_sources": 0,
                        "status_counts": Counter(),
                        "benchmark_tiers": Counter(),
                        "method_types": Counter(),
                        "variables_extracted": set(),
                        "countries": set(),
                    }
                s = nbs_stats[nbs]
                s["total_sources"] += 1
                s["status_counts"][status] += 1
                s["benchmark_tiers"][tier] += 1
                s["method_types"][method] += 1
                for v in vars_list:
                    s["variables_extracted"].add(v)
                if country:
                    s["countries"].add(country)

    formatted_stats = {}
    for nbs, s in nbs_stats.items():
        formatted_stats[nbs] = {
            "total_sources": s["total_sources"],
            "status_counts": dict(s["status_counts"]),
            "benchmark_tiers": dict(s["benchmark_tiers"]),
            "method_types": dict(s["method_types"]),
            "variables_extracted": sorted(list(s["variables_extracted"])),
            "countries": sorted(list(s["countries"])),
        }

    report_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit,
        "nbs_progress": formatted_stats,
    }

    dest_path = (
        dest if dest is not None else schema_root.parent / "docs" / "progress.json"
    )

    current_data = None
    if dest_path.exists():
        try:
            current_data = json.loads(dest_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    if check and current_data:
        if current_data.get("nbs_progress") == report_data.get("nbs_progress"):
            return []

    if (
        current_data
        and current_data.get("git_commit") == git_commit
        and current_data.get("nbs_progress") == formatted_stats
    ):
        report_data["timestamp"] = current_data["timestamp"]

    text = json.dumps(report_data, ensure_ascii=False, indent=2) + "\n"
    current = dest_path.read_text(encoding="utf-8") if dest_path.exists() else None

    if text == current:
        return []

    changed = [dest_path]
    if not check:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(text, encoding="utf-8", newline="\n")
    return changed


def _parse_discovery_logs(schema_root: Path) -> dict[str, dict]:
    """Parses all PRISMA markdown logs under methodology/discovery_logs/ into structured objects."""
    logs_dir = schema_root.parent / "methodology" / "discovery_logs"
    parsed_logs = {}
    if not logs_dir.exists():
        return parsed_logs

    for item in sorted(logs_dir.iterdir()):
        if item.is_file() and item.suffix == ".md" and item.name != "README.md":
            log_id = item.stem
            try:
                content = item.read_text(encoding="utf-8")
                lines = content.splitlines()

                title = ""
                date_str = ""
                authors_str = ""
                seed_rule = ""

                for line in lines:
                    if line.startswith("# "):
                        title = line[2:].strip()
                    elif line.startswith("**Date(s):**"):
                        date_str = line.split("**Date(s):**")[1].strip()
                    elif line.startswith("**Author(s):**"):
                        authors_str = line.split("**Author(s):**")[1].strip()
                    elif line.startswith("**Seed-set rule:**"):
                        seed_rule = line.split("**Seed-set rule:**")[1].strip()

                # Extract sections split by ## headings
                sections = {}
                current_section = None
                current_lines = []

                for line in lines:
                    if line.startswith("## "):
                        if current_section:
                            sections[current_section] = "\n".join(current_lines).strip()
                        current_section = line[3:].strip()
                        current_lines = []
                    elif current_section is not None:
                        current_lines.append(line)

                if current_section and current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()

                parsed_logs[log_id] = {
                    "id": log_id,
                    "title": title,
                    "date": date_str,
                    "authors": authors_str,
                    "seed_rule": seed_rule,
                    "sections": sections,
                    "raw_markdown": content,
                }
            except Exception as e:
                print(f"Error parsing discovery log {item.name}: {e}")

    return parsed_logs


def generate_dashboard_data(
    schema_root: Path, check: bool = False, *, dest: Path | None = None
) -> list[Path]:
    """Generates docs/dashboard_data.json aggregating all registers and recipe data."""
    registers = [
        "SRC_source_register",
        "EV_evidence_register",
        "FAM_family_registry",
        "VONT_variable_ontology",
        "BIND_dataset_binding",
        "TOOL_tool_registry",
        "SRCH_search_register",
        "XW_target_crosswalk",
    ]
    global_tables = [
        "T1_data_registry",
        "T2_climate_risk",
        "T5_opportunity_space",
        "T7_geographic_context",
    ]

    git_commit = source_revision(schema_root.parent)

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit,
        "registers": {},
        "global_tables": {},
        "recipes": {},
        "discovery_logs": _parse_discovery_logs(schema_root),
        "progress_ledger": [],
        "qaqc_stats": {},
        "review_log": [],
    }

    # Presentation annotations only: never consumed by synthesis or used to change evidence.
    presentation_csv = schema_root.parent / "docs" / "dashboard-family-presentation.csv"
    data["family_presentation"] = {
        row["suitability_family_id"]: row
        for row in (_csv_to_rows(presentation_csv) if presentation_csv.exists() else [])
    }
    status_csv = schema_root.parent / "docs" / "dashboard-family-status.csv"
    data["family_display_status"] = {
        row["suitability_family_id"]: row
        for row in (_csv_to_rows(status_csv) if status_csv.exists() else [])
    }
    rollup_csv = schema_root / "lookups" / "family_rollup_policy.csv"
    for row in _csv_to_rows(rollup_csv) if rollup_csv.exists() else []:
        if str(row.get("rollup_included", "")).lower() == "false":
            data["family_display_status"].setdefault(
                row["suitability_family_id"],
                {
                    "status": "separate_comparison",
                    "label": "Separate comparison",
                    "reason": row["rationale"],
                    "reference": "schema/lookups/family_rollup_policy.csv",
                },
            )

    ledger_csv = schema_root.parent / "pipeline" / "progress_ledger.csv"
    if ledger_csv.exists():
        data["progress_ledger"] = _csv_to_rows(ledger_csv)

    # All authorised tables are live; source identity and search-event counts remain distinct.
    queue_csv = schema_root.parent / "pipeline" / "acquisition_queue.csv"
    queue = _csv_to_rows(queue_csv) if queue_csv.exists() else []

    from nbs_ruralscan.schema_tools import qaqc_stats as _qaqc

    data["qaqc_stats"] = _qaqc.compute(
        schema_root.parent / "pipeline" / "metrics" / "review_log.csv"
    )

    review_log_csv = schema_root.parent / "pipeline" / "metrics" / "review_log.csv"
    data["review_log"] = _csv_to_rows(review_log_csv) if review_log_csv.exists() else []

    # Bounded source audits supplement the existing evidence cards, never decisions.
    from nbs_ruralscan.schema_tools.review_notes import load_review_notes

    data["t4_review_notes"] = load_review_notes(schema_root.parent)

    from nbs_ruralscan.schema_tools.review_priorities import load_review_priorities

    data["review_priorities"] = load_review_priorities(schema_root.parent)

    # Reported evidence gaps (missing variables / figures a reviewer flagged) — see /api/gap.
    gaps_csv = schema_root.parent / "pipeline" / "metrics" / "gaps.csv"
    data["gaps"] = _csv_to_rows(gaps_csv) if gaps_csv.exists() else []

    # Stocktake (pre-repo OpenAlex + C/I/D benchmark) — trimmed display set; full CSV in
    # reference/stocktake/. Distinct from the in-repo discovery logs.
    data["stocktake"] = {"peer_reviewed": [], "grey_lit": []}
    _stk_dir = schema_root.parent / "reference" / "stocktake"
    _stk_cols = [
        "oa_title",
        "NbS_Practice",
        "NbS_Cluster",
        "NbS_Subpractice",
        "Final_Benchmark",
        "cited_by_count",
        "journal_name",
        "citations_per_year",
        "doi_extracted",
        "Input_Variables",
        "Spatial_Method",
        "Method_Validation",
        "Tool",
        "Geographic_Scope",
        "Output",
        "Combined_Score",
    ]
    _pr = _stk_dir / "peer_reviewed_benchmarked.csv"
    if _pr.exists():
        import csv as _stkcsv

        with _pr.open(newline="", encoding="utf-8") as f:
            data["stocktake"]["peer_reviewed"] = [
                {k: (r.get(k, "") or "") for k in _stk_cols}
                for r in _stkcsv.DictReader(f)
            ]

    # Read registers
    for reg in registers:
        csv_path = schema_root / "registers" / f"{reg}.csv"
        if csv_path.exists():
            data["registers"][reg] = _csv_to_rows(csv_path)

    # Read global tables
    for tbl in global_tables:
        csv_path = schema_root / f"{tbl}.csv"
        if csv_path.exists():
            data["global_tables"][tbl] = _csv_to_rows(csv_path)

    # Decode categorical class codes by default (issue #102): for any EV whose quote
    # carries a CDL-style band mask, attach the readable included/excluded class names so
    # the dashboard never shows bare "61, 205…". Generalises as more schemes are routed.
    from nbs_ruralscan.runtime import codelist as _codelist

    data["decoded_classes"] = {}
    _mask_re = re.compile(r"\w+\.(lte|gte)\(\s*\d+\s*\)")
    for ev in data["registers"].get("EV_evidence_register", []):
        quote = ev.get("quote") or ""
        rel = ev.get("relationship")
        ctx = ev.get("context")
        summary = None
        # (a) GEE band mask in the quote → CDL-style decode
        if _mask_re.search(quote):
            try:
                summary = _codelist.summarise_cdl_mask(
                    quote, codelists=schema_root / "codelists"
                )
            except Exception:  # noqa: BLE001 — never break the build on a mask
                summary = None
        # (b) relationship class-range spec (e.g. HWSD "classes_suitable": "1-4") → decode
        #     against the scheme routed from the row's dataset hint (context.dataset).
        elif isinstance(rel, dict) and rel.get("classes_suitable"):
            dataset = (ctx or {}).get("dataset") if isinstance(ctx, dict) else None
            scheme = _codelist.scheme_for(variable=ev.get("variable"), dataset=dataset)
            if scheme and _codelist.load(scheme, codelists=schema_root / "codelists"):
                summary = _codelist.summarise_class_ranges(
                    scheme,
                    rel.get("classes_suitable", ""),
                    rel.get("classes_not_suitable", ""),
                    codelists=schema_root / "codelists",
                )
        if summary and summary["n_included"]:
            data["decoded_classes"][ev["evidence_id"]] = summary

    # Discover recipes
    recipes_dir = schema_root / "recipes"
    if recipes_dir.exists():
        for item in sorted(recipes_dir.iterdir()):
            if item.is_dir():
                if any(
                    (item / (table + ".csv")).exists()
                    for table in (
                        "T0_nbs_registry",
                        "T4_suitability_mappings",
                        "T3_nbs_hazard_farming",
                        "T6_nbs_scorecard",
                    )
                ):
                    nbs_id = item.name
                    data["recipes"][nbs_id] = {}
                    for tbl in [
                        "T0_nbs_registry",
                        "T4_suitability_mappings",
                        "T3_nbs_hazard_farming",
                        "T6_nbs_scorecard",
                    ]:
                        csv_path = item / f"{tbl}.csv"
                        if csv_path.exists():
                            data["recipes"][nbs_id][tbl] = _csv_to_rows(csv_path)

    from nbs_ruralscan.schema_tools.dashboard_progress import build_progress
    from nbs_ruralscan.schema_tools.dashboard_relationships import build_relationships

    data["progress_overview"] = build_progress(data, queue)
    data["relationships"] = build_relationships(data, schema_root.parent)
    releases_path = schema_root.parent / "docs" / "dashboard-releases.csv"
    releases = _csv_to_rows(releases_path) if releases_path.exists() else []
    release = (
        releases[-1]
        if releases
        else {"version": "unversioned", "count_definition_version": "1"}
    )
    data["dashboard_releases"] = releases
    docs = schema_root.parent / "docs"
    ui_files = (
        "dashboard.html",
        "t4_analysis.js",
        "dashboard-progress.js",
        "dashboard-progress.css",
        "dashboard-shell.js",
        "dashboard-shell.css",
        "dashboard-priority.js",
        "dashboard-relationships.js",
        "dashboard-relationships.css",
        "dashboard-feedback.js",
        "dashboard-feedback.css",
        "dashboard-releases.csv",
    )
    ui_hash = hashlib.sha256()
    for name in ui_files:
        path = docs / name
        if path.exists():
            ui_hash.update(name.encode() + b"\0" + path.read_bytes())
    ui_id = ui_hash.hexdigest()[:12]
    # Exclude volatile provenance fields: identical data produces the same snapshot identity.
    content = {k: v for k, v in data.items() if k not in {"timestamp", "git_commit"}}
    data_id = hashlib.sha256(
        json.dumps(content, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()[:12]

    dest_path = (
        dest
        if dest is not None
        else schema_root.parent / "docs" / "dashboard_data.json"
    )

    # A first relocated publication retains the selected snapshot's build history.
    # Later builds use their own destination history. Neither path changes inputs.
    history_path = (
        dest_path
        if dest_path.exists()
        else schema_root.parent / "docs/dashboard_data.json"
    )
    current_data = None
    if history_path.exists():
        try:
            parsed = json.loads(history_path.read_text(encoding="utf-8"))
            current_data = parsed if isinstance(parsed, dict) else None
        except Exception:
            pass

    previous_build = (current_data or {}).get("build", {})
    if not isinstance(previous_build, dict):
        previous_build = {}
    unchanged_build = (
        previous_build.get("ui_id") == ui_id
        and previous_build.get("data_id") == data_id
    )
    if unchanged_build and current_data is not None:
        data["timestamp"] = current_data.get("timestamp", data["timestamp"])
        data["git_commit"] = current_data.get("git_commit", git_commit)
    build_entry = {
        "release": release["version"],
        "ui_id": ui_id,
        "data_id": data_id,
        "count_definition_version": str(release.get("count_definition_version", "1")),
        "built_at": data["timestamp"],
        "source_commit": data["git_commit"],
    }
    history = list(previous_build.get("history", []))
    if not unchanged_build:
        history.append(build_entry.copy())
    data["build"] = {**build_entry, "history": history[-50:]}
    # Compare every generated section, not just five legacy sections. New progress,
    # bibliography, scope annotations and build IDs must participate in stale detection.
    if check and current_data and dest_path.exists():
        # Stored IDs are claims, not proof: also compare the regenerated payload.
        # Otherwise edited totals or recipes can pass --check with old hashes intact.
        normalised = json.loads(json.dumps(data, ensure_ascii=False))
        return [] if current_data == normalised else [dest_path]

    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    current = dest_path.read_text(encoding="utf-8") if dest_path.exists() else None

    if text == current:
        return []

    changed = [dest_path]
    if not check:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(text, encoding="utf-8", newline="\n")
    return changed


def _safe_console() -> None:
    """Never crash on printing: the build notes use arrows and symbols (→, ✓, ⓘ) that a
    Windows cp1252 console cannot encode, and the dashboard's submit path calls generate()
    without UTF-8 mode, so one arrow aborted a QA/QC submission (2026-10-19). Switch the
    streams to UTF-8, falling back to replacing unencodable characters."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            try:
                reconfigure(errors="replace")
            except (OSError, ValueError):
                pass


def refresh_review_state(schema_root: str | Path) -> None:
    """Refresh review-only UI artifacts; full source validation still runs on Apply.

    Reopening changes review metadata, not source claims. Avoid re-reading every PDF
    before returning the editable card to the reviewer.
    """
    schema_root = Path(schema_root)
    path = schema_root / "registers/EV_evidence_register.csv"
    path.with_suffix(".json").write_text(
        json.dumps(_csv_to_rows(path), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    generate_dashboard_data(schema_root)
    generate_progress_report(schema_root)


def validate_inputs(paths: SchemaBuildPaths) -> None:
    """Run existing hard gates and advisory checks without changing any inputs/outputs."""
    _safe_console()
    schema_root = paths.schema
    root = paths.source_root

    # Run the strict source and quote validation guardrails first
    from nbs_ruralscan.schema_tools.validate_sources import validate_all_sources

    validate_all_sources(schema_root, corpus_root=paths.corpus)

    # Enforce the progress ledger: its stage claims must reconcile with the register
    # (no unproven "done", no evidence for an unstamped stage, valid stage order).
    from nbs_ruralscan.schema_tools.ledger import check as _ledger_check

    _ledger_errs = _ledger_check(
        schema_root, ledger_path=root / "pipeline/progress_ledger.csv"
    )
    if _ledger_errs:
        raise ValueError(
            "PROGRESS LEDGER FAILED: stage claims do not reconcile with the register:\n"
            + "\n".join(f"  - {e}" for e in _ledger_errs)
        )

    # Acquisition-queue metadata gate: no pending row may carry a DOI that hasn't been
    # round-trip-verified against its citation (a wrong DOI fetches the wrong PDF ->
    # contamination). Offline (reads the doi_verified stamp; run verify_metadata.py verify
    # to (re)stamp). Build note, not fatal — extraction is the hard refusal point.
    try:
        from nbs_ruralscan.schema_tools.verify_metadata import check as _meta_check

        if (
            _meta_check(
                queue_path=root / "pipeline/acquisition_queue.csv",
                sources_path=schema_root / "registers/SRC_source_register.csv",
            )
            != 0
        ):
            print(
                "  METADATA NOTE: acquisition-queue rows carry an UNVERIFIED DOI — run "
                "`verify_metadata.py verify`, or blank the DOI and acquire by title. "
                "Extraction MUST refuse doi_verified != true (title-only otherwise)."
            )
    except Exception as _e:  # never block the build on the advisory gate
        print(f"  METADATA NOTE: metadata check skipped ({_e}).")

    # Advisory (never fatal): off-scope extraction signals + unincorporated review feedback.
    from nbs_ruralscan.schema_tools.check_scope import check as _scope_check
    from nbs_ruralscan.schema_tools.learnings import coverage_note as _learn_note

    _scope_flags = _scope_check(
        schema_root / "registers" / "EV_evidence_register.csv",
        policy_path=schema_root / "lookups/m2b_variable_policy.csv",
    )
    if _scope_flags:
        print(
            f"  SCOPE NOTES ({len(_scope_flags)} active unit(s) with off-scope signals — "
            "run check_scope.py; the dominant QA defect)"
        )
    from nbs_ruralscan.schema_tools.check_quote import check as _quote_check

    _quote_flags = _quote_check(schema_root / "registers" / "EV_evidence_register.csv")
    if _quote_flags:
        print(
            f"  QUOTE NOTES ({len(_quote_flags)} active unit(s) with too-narrow quotes — "
            "run check_quote.py; re-extract with full context)"
        )
    from nbs_ruralscan.schema_tools.check_picos import check as _picos_check

    _picos_flags = _picos_check(schema_root / "registers" / "EV_evidence_register.csv")
    if _picos_flags:
        print(
            f"  PICOS NOTES ({len(_picos_flags)} active AF unit(s) with wrong-practice "
            "signals — run check_picos.py; the practice must be evidenced in the source)"
        )
    from nbs_ruralscan.schema_tools.check_species import check as _species_check

    _species_flags = _species_check(
        schema_root / "registers" / "EV_evidence_register.csv",
        sources_path=schema_root / "registers/SRC_source_register.csv",
    )
    if _species_flags:
        print(
            f"  SPECIES NOTES ({len(_species_flags)} practice-tagged unit(s) that look "
            "species-specific — run check_species.py; retag claim_scope=species_specific "
            "+ taxon and KEEP, don't drop)"
        )
    # Effect-claim gates (ruleset v1.6.0, T3/T6 generation method) — advisory. They only
    # see use_role = nbs_effect / asset_vulnerability units, so they print nothing until
    # the migrated / re-extracted effect units land (PR4+).
    from nbs_ruralscan.schema_tools.check_bands import check as _bands_check
    from nbs_ruralscan.schema_tools.check_context import check as _context_check
    from nbs_ruralscan.schema_tools.check_xw import check as _xw_check

    _ev_csv = schema_root / "registers" / "EV_evidence_register.csv"
    _ctx_flags = _context_check(_ev_csv, schema_root / "T7_geographic_context.csv")
    if _ctx_flags:
        print(
            f"  CONTEXT NOTES ({len(_ctx_flags)} fixed-key violation(s) on active effect "
            "units — run check_context.py; contract §2.3 keys only)"
        )
    _band_flags = _bands_check(
        _ev_csv, schema_root / "registers" / "BANDS_magnitude_bands.csv"
    )
    if _band_flags:
        print(
            f"  BANDS NOTES ({len(_band_flags)} strength-class/magnitude disagreement(s) "
            "— run check_bands.py; classes come from BANDS, never adjectives)"
        )
    from nbs_ruralscan.schema_tools.check_direction import check as _dir_check
    from nbs_ruralscan.schema_tools.check_direction import (
        check_structure as _dir_structure,
    )

    _dir_errs = _dir_structure(
        _ev_csv,
        schema_root / "registers" / "XW_target_crosswalk.csv",
        schema_root / "lookups" / "variable_direction_sense.csv",
    )
    if _dir_errs:
        raise ValueError(
            "DIRECTION SENSE FAILED: every effect variable needs a row in "
            "lookups/variable_direction_sense.csv and XW polarity must agree with it:\n"
            + "\n".join(f"  - {e['signal']}: {e['detail']}" for e in _dir_errs)
        )
    _dir_flags = _dir_check(
        _ev_csv,
        sense_path=schema_root / "lookups/variable_direction_sense.csv",
        exceptions_path=schema_root / "lookups/direction_cue_exceptions.csv",
    )
    if _dir_flags:
        print(
            f"  DIRECTION NOTES ({len(_dir_flags)} cue problem(s) on active effect units "
            "— run check_direction.py; direction is on the variable AS NAMED)"
        )
    _xw_flags = _xw_check(
        _ev_csv,
        schema_root / "registers" / "VONT_variable_ontology.csv",
        schema_root / "registers" / "XW_target_crosswalk.csv",
    )
    if _xw_flags:
        print(
            f"  XW NOTES ({len(_xw_flags)} effect variable(s) with no VONT id or no "
            "crosswalk route — run check_xw.py; unmapped feeds no cell)"
        )
    # Advisory: a quote that swallows a whole table hides the claim and lets number
    # provenance pass on numbers from other rows (Pete 2026-10-12 review theme).
    from nbs_ruralscan.schema_tools import check_quote as _cq

    _wide = [f for f in _cq.check(_ev_csv) if "whole table" in f["why"]]
    if _wide:
        print(
            f"  QUOTE WIDTH: {len(_wide)} active unit(s) quote a whole table/page "
            "(run check_quote.py; quote the table ROW + header instead)"
        )
    _ln = _learn_note(
        review_log=root / "pipeline/metrics/review_log.csv",
        learnings_log=root / "pipeline/metrics/learnings_log.csv",
    )
    if _ln:
        print(f"  LEARNING-LOOP NOTE: {_ln}")


def quarantine_inputs(paths: SchemaBuildPaths) -> list[dict]:
    """Explicit legacy register mutation; callers must validate first."""
    if paths.output_root is not None:
        raise ValueError(
            "A separate-output build cannot quarantine its source snapshot"
        )
    from nbs_ruralscan.schema_tools.quarantine import apply

    quarantined = apply(paths.schema)
    if quarantined:
        print(
            f"  AUTO-QUARANTINE: soft-dropped {len(quarantined)} off-scope/wrong-practice "
            "unit(s) (review_state=dropped, reversible via the QA dashboard)"
        )
    return quarantined


def _table_outputs(paths: SchemaBuildPaths) -> list[tuple[Path, Path]]:
    schema_root = paths.schema
    manifest = json.loads(
        (schema_root / "structure" / "columns.json").read_text(encoding="utf-8")
    )
    return [
        (
            csv_path,
            paths.schema_output
            / csv_path.relative_to(schema_root).with_suffix(".json"),
        )
        for spec in manifest["tables"].values()
        for csv_path in _csv_files(schema_root, spec["location"])
    ]


def _destinations(paths: SchemaBuildPaths) -> list[Path]:
    return [
        *(dest for _, dest in _table_outputs(paths)),
        *(
            [paths.docs_output / "progress.json"]
            if (paths.schema / "registers/SRC_source_register.csv").exists()
            else []
        ),
        *(
            paths.docs_output / name
            for name in (
                "dashboard_data.json",
                "review/decisions.json",
                "table_progress.json",
                "scorecard.json",
                "effect_rows_flat.csv",
            )
        ),
    ]


def _preflight(paths: SchemaBuildPaths) -> None:
    paths.preflight(_destinations(paths))


def publish_outputs(paths: SchemaBuildPaths, *, check: bool = False) -> list[Path]:
    """Stage a complete build before replacing derived files; no quarantine.

    Validate before calling. Checks remain read-only. Writes have rollback for
    caught failures, not whole-build reader atomicity or crash durability.
    """
    _preflight(paths)
    if check:
        return _render_outputs(paths, check=True)
    from nbs_ruralscan.schema_tools.publication import staged_publish

    return staged_publish(paths, _destinations(paths), _render_outputs)


def _render_outputs(paths: SchemaBuildPaths, *, check: bool = False) -> list[Path]:
    """Compile into the supplied destination (private staging for write builds)."""
    schema_root, docs = paths.schema, paths.docs_output
    changed: list[Path] = []
    for csv_path, json_path in _table_outputs(paths):
        text = json.dumps(_csv_to_rows(csv_path), ensure_ascii=False, indent=2) + "\n"
        current = json_path.read_text(encoding="utf-8") if json_path.exists() else None
        if text == current:
            continue
        changed.append(json_path)
        if not check:
            json_path.parent.mkdir(parents=True, exist_ok=True)
            json_path.write_text(text, encoding="utf-8", newline="\n")

    # Compile the progress.json report
    changed.extend(
        generate_progress_report(schema_root, check=check, dest=docs / "progress.json")
    )
    # Compile the dashboard_data.json payload
    changed.extend(
        generate_dashboard_data(
            schema_root, check=check, dest=docs / "dashboard_data.json"
        )
    )
    # Compile the per NbS × T3/T6 pipeline-position report (docs/table_progress.json)
    from nbs_ruralscan.schema_tools import review_exports, table_progress

    # committed review-page exports → docs/review/decisions.json (shared decision view)
    changed.extend(
        review_exports.write_decisions(
            check=check,
            dest=docs / "review/decisions.json",
            exports_dir=paths.source_root / "docs/review/exports",
            batch_dir=paths.source_root / "docs/review",
        )
    )

    changed.extend(
        table_progress.write(
            schema_root, check=check, dest=docs / "table_progress.json"
        )
    )
    # NbS comparison scorecard (decisions D3–D7) → docs/scorecard.json
    from nbs_ruralscan.runtime import scorecard

    changed.extend(
        scorecard.write(schema_root, check=check, dest=docs / "scorecard.json")
    )
    # flat, filterable view of every T3/T6/T6E row → docs/effect_rows_flat.csv
    from nbs_ruralscan.runtime import effect_rows

    changed.extend(
        effect_rows.write_flat(
            schema_root, check=check, dest=docs / "effect_rows_flat.csv", from_csv=True
        )
    )
    return changed


def build(paths: SchemaBuildPaths, *, check: bool = False) -> list[Path]:
    """Validate and publish a reconciled snapshot without changing its inputs."""
    if paths.schema.name != "schema":
        raise ValueError(
            "Snapshot builds currently require a CIAT-layout schema/ directory"
        )
    _preflight(paths)
    validate_inputs(paths)
    from nbs_ruralscan.schema_tools.quarantine import candidates

    pending = candidates(paths.schema)
    if pending:
        raise ValueError(
            f"Snapshot has {len(pending)} pending automatic quarantine candidate(s); "
            "reconcile explicitly before building without input changes: "
            + ", ".join(row["evidence_id"] for row in pending)
        )
    return publish_outputs(paths, check=check)


def generate(schema_root: str | Path, *, check: bool = False) -> list[Path]:
    """Compatibility flow: validate, quarantine on writes, then publish in place."""
    paths = SchemaBuildPaths(Path(schema_root))
    _preflight(paths)
    validate_inputs(paths)
    if not check:
        quarantine_inputs(paths)
    return publish_outputs(paths, check=check)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "schema_root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[3] / "schema",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare generated artifacts without creating files or folders",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--validate-only",
        action="store_true",
        help="run existing source/ledger/policy checks without publication or quarantine",
    )
    mode.add_argument(
        "--build-only",
        action="store_true",
        help="validate and publish a reconciled snapshot without quarantine",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        help="separate derived schema/ and docs/ destination; requires --build-only",
    )
    parser.add_argument(
        "--corpus-dir",
        type=Path,
        help="explicit existing source corpus; missing/empty artifacts still fail validation",
    )
    args = parser.parse_args(argv)
    if args.output_root is not None and not args.build_only:
        parser.error("--output-root requires --build-only")
    if args.validate_only and args.check:
        parser.error("--validate-only and --check are separate operations")
    paths = SchemaBuildPaths(args.schema_root, args.output_root, args.corpus_dir)
    if args.validate_only:
        validate_inputs(paths)
        print("Validation complete; no files written.")
        return 0
    if args.build_only:
        changed = build(paths, check=args.check)
    else:
        _preflight(paths)
        validate_inputs(paths)
        if not args.check:
            quarantine_inputs(paths)
        changed = publish_outputs(paths, check=args.check)
    if args.check and changed:
        print("Stale generated artifacts:")
        for path in changed:
            print(f"  {path}")
        return 1
    print(f"{'stale' if args.check else 'wrote'}: {len(changed)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
