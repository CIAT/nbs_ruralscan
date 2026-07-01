"""Verify each source's open-access / licensing status via Unpaywall (issue #53).

Before anything ships publicly we must know each source's access status: short verbatim
quotes are defensible fair-use, but redistributing paywalled full-text PDFs is not.
DOI-prefix inference is unreliable, so this verifies against the **Unpaywall** API (by DOI)
and writes the result to SRC: ``access_status`` (open_access | paywalled | unknown) +
``license`` (cc-by, etc., where Unpaywall reports it).

`.cache/corpus/` stays gitignored regardless — this just records what's legally shareable.

CLI:
  uv run python3 -m nbs_ruralscan.schema_tools.access_status schema            # fill unknowns
  uv run python3 -m nbs_ruralscan.schema_tools.access_status schema --refresh  # re-verify all
"""

from __future__ import annotations

import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

EMAIL = "p.steward@cgiar.org"  # Unpaywall requires a contact email
_API = "https://api.unpaywall.org/v2/"


def lookup(doi: str, email: str = EMAIL, timeout: float = 20.0) -> dict | None:
    """Query Unpaywall for one DOI → {access_status, license, oa_status} (None on failure)."""
    doi = (doi or "").strip().removeprefix("https://doi.org/").removeprefix("doi:")
    if not doi:
        return None
    url = _API + urllib.parse.quote(doi) + "?email=" + urllib.parse.quote(email)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            d = json.load(r)
    except Exception:  # noqa: BLE001 — network/404/parse → leave unknown
        return None
    is_oa = bool(d.get("is_oa"))
    loc = d.get("best_oa_location") or {}
    return {
        "access_status": "open_access" if is_oa else "paywalled",
        "license": (loc.get("license") or "") if is_oa else "",
        "oa_status": d.get("oa_status") or "",
    }


def update(
    schema_root: str | Path = "schema", *, email: str = EMAIL, refresh: bool = False
) -> list[dict]:
    """Verify + write access_status/license for SRC rows with a DOI. Returns changes."""
    src = Path(schema_root) / "registers" / "SRC_source_register.csv"
    with src.open(newline="", encoding="utf-8") as f:
        fields = list(csv.DictReader(f).fieldnames or [])
        f.seek(0)
        rows = list(csv.DictReader(f))
    if "license" not in fields:
        fields.append("license")
    changed: list[dict] = []
    for r in rows:
        doi = (r.get("doi") or "").strip()
        if not doi:
            continue
        if not refresh and (r.get("access_status") or "unknown") != "unknown":
            continue
        res = lookup(doi, email)
        if not res:
            continue
        before = (r.get("access_status"), r.get("license"))
        r["access_status"] = res["access_status"]
        r["license"] = res["license"]
        if (r.get("access_status"), r.get("license")) != before:
            changed.append(
                {
                    "source_id": r.get("source_id", ""),
                    "doi": doi,
                    "access_status": res["access_status"],
                    "license": res["license"],
                    "oa_status": res["oa_status"],
                }
            )
        time.sleep(0.3)  # be polite to the API
    with src.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    return changed


def main(argv: list[str] | None = None) -> int:
    import sys

    argv = argv if argv is not None else sys.argv[1:]
    root = next((a for a in argv if not a.startswith("-")), "schema")
    changed = update(root, refresh="--refresh" in argv)
    print(f"access_status: verified {len(changed)} source(s) via Unpaywall:")
    for c in changed:
        lic = f" · {c['license']}" if c["license"] else ""
        print(f"  {c['source_id']:34} {c['access_status']:12} ({c['oa_status']}){lic}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
