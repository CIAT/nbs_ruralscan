# Source access & public-sharing policy

*Issue #53. What may appear in the public repo / dashboard, by each source's verified `SRC.access_status`.*

Every source's access status is **verified against Unpaywall by DOI** (not inferred from the DOI prefix) and written to `SRC.access_status` (`open_access` | `paywalled` | `unknown`) + `SRC.license` (e.g. `cc-by`). Tool: `schema_tools/access_status.py`.

## What can be shared

| access_status | Short verbatim quotes (dashboard / EV) | Full-text PDF / large excerpts |
|---|---|---|
| **open_access** (CC-BY / CC-BY-* ) | ✅ yes — with attribution | ✅ permitted by licence (still kept out of git by default) |
| **open_access (NC/ND, green, other-oa)** | ✅ yes (fair-use citation) | ⚠️ no redistribution — quote only |
| **paywalled** | ✅ short quotes only (fair-use citation) | ❌ **never** commit or redistribute the PDF |
| **unknown / no DOI** | ✅ short quotes only | ❌ treat as paywalled until manually verified |

## Standing rules
- **`.cache/corpus/` stays gitignored** — source PDFs/snapshots are never committed, regardless of access status.
- The public dashboard surfaces **short verbatim quotes** (the EV provenance anchor) — defensible as fair-use citation across all licences. Do not expose full-text or large multi-paragraph excerpts.
- **Paywalled / unknown sources** (current: `mushtaq_2023` paywalled; `wb_fsrp_2022`, `wb_kcsap_2016` unknown; the no-DOI grey/tool sources `inab_landcap_guatemala`, `crs_fmnr_niger_2025`, `saraheb3_*`) — quotes only; verify manually before sharing anything larger.
- Re-verify after adding sources: `uv run python3 -m nbs_ruralscan.schema_tools.access_status schema` (fills `unknown`; `--refresh` re-checks all).

## Status (2026-06-25, verified via Unpaywall)
36 open_access · 1 paywalled · 2 unknown (WB project DOIs not in Unpaywall) · 4 no-DOI (grey/tool — manual). Most carry CC-BY; a few CC-BY-NC-ND / green-OA (quote-only for redistribution).
