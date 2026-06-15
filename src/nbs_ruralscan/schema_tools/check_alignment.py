import csv
import re
import sys
from pathlib import Path


def parse_markdown_inclusions(log_path: Path) -> set[str]:
    """Extracts all source_ids listed in tables under inclusion sections in the discovery log."""
    content = log_path.read_text(encoding="utf-8")
    source_ids = set()

    # We look for tables or lists containing source_ids
    # Source IDs follow pattern: word_word_year or word_year or wocat_slm_database
    # E.g., tscharntke_shade_2011, quandt_resilience_2017, brandt_2015
    pattern = re.compile(
        r"`([a-z0-9_]+_[a-z0-9_]+_[0-9]{4})`|`([a-z0-9_]+_[0-9]{4})`|`(wocat_slm_database)`|`(wocat_studer_2013)`|`(wri_2025)`"
    )

    # Let's also look for them in tables directly: e.g. | source_id | or | `source_id` |
    # Standard format has | `source_id` | or | source_id | as the first column in the inclusions tables
    lines = content.splitlines()
    in_inclusions_section = False

    for line in lines:
        if line.startswith("## ") or line.startswith("### "):
            header = line.lower()
            if (
                "inclusion" in header
                or "sources" in header
                or "peer-reviewed" in header
                or "grey literature" in header
                or "tools" in header
            ):
                in_inclusions_section = True
            elif "exclusion" in header or "boundary" in header or "retro" in header:
                in_inclusions_section = False

        if in_inclusions_section and "|" in line:
            # Match code blocks or raw names in columns
            matches = pattern.findall(line)
            for m in matches:
                # findall returns a tuple of groups; grab the non-empty one
                for g in m:
                    if g:
                        source_ids.add(g)

            # Also extract plain text source IDs from the table columns
            parts = [p.strip().replace("`", "") for p in line.split("|")]
            for part in parts:
                if (
                    re.match(r"^[a-z0-9_]+_[0-9]{4}$", part)
                    or re.match(r"^[a-z0-9_]+_[a-z0-9_]+_[0-9]{4}$", part)
                    or part in ["wocat_slm_database", "wri_2025"]
                ):
                    source_ids.add(part)

    return source_ids


def main():
    repo_root = Path(__file__).resolve().parents[3]
    src_csv_path = repo_root / "schema" / "registers" / "SRC_source_register.csv"
    ev_csv_path = repo_root / "schema" / "registers" / "EV_evidence_register.csv"
    logs_dir = repo_root / "methodology" / "discovery_logs"

    errors = 0

    # =========================================================================
    # 1. Load Source Register
    # =========================================================================
    src_vars = {}
    with open(src_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row["source_id"]
            vars_str = row["vars_extracted"]
            vars_list = [v.strip() for v in vars_str.split(";") if v.strip()]
            src_vars[sid] = set(vars_list)

    # =========================================================================
    # 2. Load Evidence Register
    # =========================================================================
    ev_vars = {}
    with open(ev_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row["source_id"]
            var = row["variable"]
            if sid not in ev_vars:
                ev_vars[sid] = set()
            ev_vars[sid].add(var)

    # =========================================================================
    # 3. Check Source-Evidence Variable Agreement
    # =========================================================================
    print("Checking Source-Evidence Variable Agreement...")
    for sid, declared in src_vars.items():
        actual = ev_vars.get(sid, set())

        # Check for variables declared in SRC but missing in EV
        over_declared = declared - actual
        if over_declared:
            print(
                f"ERROR: Source '{sid}' declares variables {list(over_declared)} in SRC but has no matching rows in EV."
            )
            errors += 1

        # Check for variables present in EV but missing in SRC declaration
        under_declared = actual - declared
        if under_declared:
            print(
                f"ERROR: Source '{sid}' has evidence rows in EV for variables {list(under_declared)} but does not list them in SRC."
            )
            errors += 1

    # =========================================================================
    # 4. Check Discovery Log Inclusions vs. Source Register
    # =========================================================================
    print("\nChecking Discovery Log Inclusions against Source Register...")
    if logs_dir.exists():
        for log_path in sorted(logs_dir.glob("*.md")):
            if log_path.name == "README.md":
                continue

            inclusions = parse_markdown_inclusions(log_path)
            print(f"Log '{log_path.name}': parsed {len(inclusions)} inclusions.")
            for sid in inclusions:
                if sid not in src_vars:
                    # Ignore standard baseline or external papers if not registered, but verify general ones
                    print(
                        f"WARNING: Log inclusion '{sid}' is not registered in SRC_source_register.csv"
                    )
                    # We treat this as warning, but could be error depending on design

    print(f"\nAlignment check complete. Errors found: {errors}")
    if errors > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
