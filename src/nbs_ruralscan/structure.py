"""Structure validator — checks the schema data files against the frozen column manifest.

The manifest (``schema/structure/columns.json``) is the locked v0.2 column set. This
module checks every T0-T7 + register data file (CSV or JSON) against it:

Two tiers:

* **STRUCTURE** (always fatal) — column drift: required columns missing, or unknown
  columns present. This is the frozen v0.2 contract; breaking it fails the build.
* **CONTENT** (advisory by default; fatal under ``--strict``) — empty required values,
  unresolved foreign keys, and out-of-vocabulary enum values (``enum_values`` in the
  manifest). Draft-0 example tables are *expected* to have content gaps until populated,
  so these are warnings unless you ask for ``--strict`` (used to prove a fully-populated
  slice, e.g. the F1×slope chain).

Stdlib only — runs with plain ``python3 -m nbs_ruralscan.structure <schema_root>`` even
without the package installed. Exit code is non-zero if any ERROR is found. Use it in
CI and as the team's "did I break the structure?" check.
"""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Finding:
    level: str  # "ERROR" | "WARN"
    table: str
    message: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    def error(self, table: str, msg: str) -> None:
        self.findings.append(Finding("ERROR", table, msg))

    def warn(self, table: str, msg: str) -> None:
        self.findings.append(Finding("WARN", table, msg))

    @property
    def n_errors(self) -> int:
        return sum(1 for f in self.findings if f.level == "ERROR")

    @property
    def n_warnings(self) -> int:
        return sum(1 for f in self.findings if f.level == "WARN")


def _load_manifest(schema_root: Path) -> dict:
    mpath = schema_root / "structure" / "columns.json"
    return json.loads(mpath.read_text())


def _find_files(schema_root: Path, location: str) -> list[Path]:
    """Resolve a manifest ``location`` pattern to concrete files (prefer JSON)."""
    stem = location.split(".")[0]  # drop the {csv,json} suffix marker
    if "<nbs_id>" in stem:
        glob = stem.replace("<nbs_id>", "*")
        cands = sorted(schema_root.glob(glob + ".json")) + sorted(
            schema_root.glob(glob + ".csv")
        )
    else:
        cands = [schema_root / (stem + ".json"), schema_root / (stem + ".csv")]
    return [p for p in cands if p.exists()]


def _read_rows(path: Path) -> tuple[list[str], list[dict]]:
    """Return (columns, rows) from a JSON array-of-objects or a CSV."""
    if path.suffix == ".json":
        data = json.loads(path.read_text())
        if isinstance(data, dict):  # tolerate {"rows": [...]} or {table: [...]}
            data = next((v for v in data.values() if isinstance(v, list)), [])
        cols: list[str] = []
        for row in data:
            for k in row:
                if k not in cols:
                    cols.append(k)
        return cols, list(data)
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        cols = list(reader.fieldnames or [])
        return cols, [dict(r) for r in reader]


def _allowed(spec: dict) -> set[str]:
    out = {spec["primary_key"]}
    for key in ("required", "optional", "conditional", "derived"):
        out.update(spec.get(key, []))
    return out


def _is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False


def _fk_values(value) -> list[str]:
    """Normalise an FK cell to a list of string keys (handles list + CSV-serialised)."""
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = json.loads(text.replace("'", '"'))
            return [str(v).strip() for v in parsed if str(v).strip()]
        except json.JSONDecodeError:
            text = text[1:-1]
    return [t.strip().strip("'\"") for t in text.split(",") if t.strip()]


def validate_structure(schema_root: str | Path, *, strict: bool = False) -> Report:
    schema_root = Path(schema_root)
    manifest = _load_manifest(schema_root)
    tables: dict[str, dict] = manifest["tables"]
    rep = Report()
    # content issues (empty required, unresolved FK) are fatal only under --strict.
    content = rep.error if strict else rep.warn

    # Which (table, column) value-sets do we need to index? Any FK target column.
    def _targets(fk) -> list[str]:
        return fk["targets"] if isinstance(fk, dict) else [fk]

    wanted_cols: set[tuple[str, str]] = set()
    for spec in tables.values():
        for fk in spec.get("fk", {}).values():
            for t in _targets(fk):
                tt, tc = t.split(".")
                wanted_cols.add((tt, tc))

    # Pass 1: column + required-value checks; collect value-sets for every FK-target column.
    col_sets: dict[tuple[str, str], set[str]] = {wc: set() for wc in wanted_cols}
    seen_tables: set[str] = set()
    loaded: dict[str, list[dict]] = {}
    for tname, spec in tables.items():
        files = _find_files(schema_root, spec["location"])
        if not files:
            rep.warn(
                tname, f"no data file found at {spec['location']} (content pending)"
            )
            continue
        seen_tables.add(tname)
        allowed = _allowed(spec)
        required = set(spec.get("required", []))
        enum_values: dict[str, list[str]] = spec.get("enum_values", {})
        loaded.setdefault(tname, [])
        for path in files:
            cols, rows = _read_rows(path)
            colset = set(cols)
            for missing in sorted(required - colset):
                rep.error(tname, f"{path.name}: missing required column '{missing}'")
            for unknown in sorted(colset - allowed):
                rep.error(
                    tname, f"{path.name}: unknown column '{unknown}' (not in manifest)"
                )
            for i, row in enumerate(rows):
                for col in required & colset:
                    if _is_empty(row.get(col)):
                        content(
                            tname, f"{path.name} row {i}: required '{col}' is empty"
                        )
                for col, valid_vals in enum_values.items():
                    if col in colset:
                        for v in _fk_values(row.get(col)):
                            if v not in valid_vals:
                                content(
                                    tname,
                                    f"{path.name} row {i}: {col}='{v}' not a valid "
                                    f"enum value",
                                )
                for tt, tc in wanted_cols:
                    if tt == tname:
                        for v in _fk_values(row.get(tc)):
                            col_sets[(tt, tc)].add(v)
            loaded[tname].extend(rows)

    # Pass 2: foreign-key resolution (multi-target + literal-allow supported).
    for tname, spec in tables.items():
        for col, fk in spec.get("fk", {}).items():
            targets = _targets(fk)
            literals = set(fk.get("literals", [])) if isinstance(fk, dict) else set()
            tgt_tables = {t.split(".")[0] for t in targets}
            if not (tgt_tables & seen_tables):
                rep.warn(
                    tname, f"FK '{col}' -> {targets}: no target table loaded; skipped"
                )
                continue
            valid = set(literals)
            for t in targets:
                tt, tc = t.split(".")
                valid |= col_sets.get((tt, tc), set())
            for i, row in enumerate(loaded.get(tname, [])):
                for v in _fk_values(row.get(col)):
                    if v not in valid:
                        content(tname, f"row {i}: {col}='{v}' not in {targets}")
    return rep


def _format(rep: Report) -> str:
    lines = [f"{f.level:5} [{f.table}] {f.message}" for f in rep.findings]
    lines.append("")
    lines.append(f"{rep.n_errors} error(s), {rep.n_warnings} warning(s).")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    strict = "--strict" in argv
    positional = [a for a in argv if not a.startswith("-")]
    root = (
        Path(positional[0])
        if positional
        else Path(__file__).resolve().parents[2] / "schema"
    )
    rep = validate_structure(root, strict=strict)
    print(_format(rep))
    return 1 if rep.n_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
