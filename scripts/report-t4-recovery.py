#!/usr/bin/env python3
"""Build a compact review of the October T4 evidence recovery."""

import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows(path):
    return list(csv.DictReader((ROOT / path).open()))


def profiles(path):
    return {
        p["profile_id"]: p
        for r in rows(path)
        for p in json.loads(r["relationship_params"]).get("profiles", [])
    }


def bands(profile):
    if not profile:
        return "Not in live T4 — human review pending."
    result = []
    for b in profile["intervals"]:
        low, high = b["lower"], b["upper"]
        if low is None:
            interval = f"{'≤' if b['upper_inclusive'] else '<'} {high:.2f}"
        elif high is None:
            interval = f"{'≥' if b['lower_inclusive'] else '>'} {low:.2f}"
        else:
            interval = f"{'[' if b['lower_inclusive'] else '('}{low:.2f}, {high:.2f}{']' if b['upper_inclusive'] else ')'}"
        result.append(
            html.escape(
                f"{interval} {profile['unit']}: {b['label'].replace('_', ' ')} → {b['score']:g}"
            )
        )
    return "<br>".join(result)


def main():
    live = profiles("schema/recipes/agroforestry/T4_suitability_mappings.csv")
    draft = profiles(
        "pipeline/t4_audit/agroforestry/final_audit/draft/T4_suitability_mappings.csv"
    )
    comparisons = [
        (
            "Chuma 2021 · slope",
            "ev_T4_slope_chuma21_1",
            "Live: existing human approval preserved. Source slope percentages converted to degrees. Regional response retained; no unsupported transfer to every agroforestry system.",
        ),
        (
            "Haile 2024 · soil organic carbon",
            "ev_T4_soc_haile2024_1",
            "Review: confirm continuation belongs to SOC and inherited % unit. Two missing classes on p6 join p5 as one source profile; they do not add a second paper vote. Display converted to g/kg.",
        ),
        (
            "Chuma 2021 · elevation",
            "ev_T4_elevation_chuma2021_recovery",
            "Review: confirm five source classes and regional scope. No global elevation limit inferred.",
        ),
    ]
    table = "".join(
        f"<tr><th>{html.escape(label)}</th><td>{bands(live.get(eid))}</td><td>{bands(draft.get(eid))}</td><td>{html.escape(note)}</td></tr>"
        for label, eid, note in comparisons
    )
    pending = [
        r
        for r in rows("schema/registers/EV_evidence_register.csv")
        if r["nbs_id"] == "agroforestry" and r["ruleset_version"] == "v1.6.14"
    ]
    pending_html = "".join(
        f"<tr><td>{html.escape(r['source_id'])}</td><td>{html.escape(r['variable'])}</td><td>{html.escape(r['page'])}</td><td><code>{html.escape(r['evidence_id'])}</code></td></tr>"
        for r in pending
    )
    coverage = rows("pipeline/t4_audit/agroforestry/stocktake_coverage_2026-10-20.csv")
    coverage_html = "".join(
        f"<tr><td>{html.escape(r['source_id'])}</td><td>{html.escape(r['finding'])}</td><td>{html.escape(r['source_locator'])}</td></tr>"
        for r in coverage
    )
    page = f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>T4 evidence recovery</title>
<style>body{{font:17px/1.5 system-ui;color:#163d32;background:#f5f8f6;margin:32px auto;max-width:1500px;padding:0 24px}}table{{border-collapse:collapse;width:100%;background:white;margin:20px 0}}th,td{{text-align:left;vertical-align:top;padding:16px;border:1px solid #ceddd5}}th{{background:#edf4ef}}code{{font-size:13px;overflow-wrap:anywhere}}summary{{cursor:pointer;font-weight:600}}h1{{margin-bottom:8px}}a{{color:#096b50}}</style>
<h1>T4: recovered evidence</h1><p>One approved numeric profile recovered into live T4. Eight new evidence records await human review. All 23 scoping-review papers now accounted for in the source register.</p>
<p><a href="t4-categorical-tables.html">Full live T4</a> · <a href="t4-harmonization-results.html">Cross-paper comparisons</a></p>
<table><thead><tr><th>Study / variable</th><th>Live T4 now</th><th>With pending evidence</th><th>Meaning / review needed</th></tr></thead><tbody>{table}</tbody></table>
<p><strong>Reading ranges:</strong> source endpoint conventions remain in machine-readable profiles. Overlapping boundary values stay unknown. Scores are shared ordinal conventions, not probabilities.</p>
<details><summary>Inspect Chuma’s original class table (p6)</summary><img src="img/chuma2021_table_recovery.png" alt="Chuma Table 3" style="max-width:100%"></details><details><summary>Inspect Haile’s continuation (p6)</summary><img src="img/haile2024_continuation_recovery.png" alt="Haile SOC continuation" style="max-width:100%"></details><h2>Other recovered evidence</h2><p><strong>Ahmad 2020:</strong> Table 2 supplies model weights: temperature, rainfall and aridity 11.11% each; NDVI and slope 16.66% each. Combined soil-condition weight 33.33% stays unallocated among soil variables. These document variable importance within this paper; they do not set T4 thresholds or default weights. Five new records await image-reading review.</p>
<details><summary>Inspect Ahmad’s original Table 2</summary><img src="img/ahmad2020_table2_recovery.png" alt="Original Ahmad Table 2 page" style="max-width:100%"></details>
<p><strong>Baldwin 2022:</strong> agricultural/open-land statement retained but quarantined by the scope guardrail (speculative wording). Review whether it supports a host rule, then transfer to agroforestry systems and dataset classes before executing a new mask.</p>
<p><strong>Still ambiguous:</strong> Ahmad’s scaled aridity and response interpolation; Haile SOC attribution/unit; Baldwin’s class crosswalk; regional transfer of Chuma elevation. Existing holds remain visible in full T4 review. Castle’s companion code contains species envelopes and environmental-priority weights: neither becomes a general agroforestry threshold.</p>
<details><summary>Eight new records for human review</summary><table><tr><th>Source</th><th>Variable</th><th>PDF page</th><th>Review ID</th></tr>{pending_html}</table></details>
<details><summary>All 23 scoping papers: disposition and locator</summary><table><tr><th>Source</th><th>Disposition</th><th>Locator</th></tr>{coverage_html}</table></details>
<h2>Why evidence was missed</h2><p>QA reviewed extracted records, but did not reconcile every paper or every table class. Chuma’s approved numeric fields fell through an unsupported encoding; Haile’s table continued onto another page; Ahmad’s weights were image-only. Five shared PDFs never reached the source register.</p>
<p>New CI checks reconcile source coverage, inventoried class counts, live approval boundaries, exact reviewer follow-up notes and figure checksums. Compiler tests reject incompatible or overlapping table fragments. These checks protect documented coverage; they cannot prove an unseen PDF contains no further evidence.</p></html>"""
    (ROOT / "docs/review/t4-evidence-recovery.html").write_text(page)
    (ROOT / "docs/review/t4-evidence-coverage.html").write_text(page)


if __name__ == "__main__":
    main()
