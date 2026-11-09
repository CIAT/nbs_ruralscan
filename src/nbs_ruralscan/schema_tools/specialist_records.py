"""CSV and annotation input checks for specialist evidence maintenance."""

import csv
import json
import math
import shlex
import sys
from pathlib import Path

from nbs_ruralscan.ingest.integrity import validate_source_id

REVIEW_COLUMNS = [
    "date",
    "evidence_id",
    "source_id",
    "verdict",
    "decision",
    "reason",
    "note",
    "reviewer",
]


def parse_json(text: str):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid(value):
        raise ValueError(f"Invalid JSON number: {value}")

    def finite(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f"Invalid JSON number: {value}")
        return number

    return json.loads(
        text, object_pairs_hook=unique, parse_constant=invalid, parse_float=finite
    )


def keyed_records(path: Path, *, array: bool) -> dict[str, dict]:
    data = parse_json(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list if array else dict):
        raise ValueError(f"Unexpected annotation structure: {path.name}")
    result: dict[str, dict] = {}
    entries = enumerate(data) if array else data.items()
    for key, record in entries:
        if not isinstance(record, dict):
            raise ValueError(f"Expected annotation object in {path.name}")
        eid = record.get("evidence_id") if array else key
        if not isinstance(eid, str) or not eid.strip() or eid in result:
            raise ValueError(f"Missing or duplicate evidence_id in {path.name}: {eid}")
        result[eid] = record
    return result


def read_table(path: Path, required) -> tuple[list[str], list[dict]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, strict=True)
        cols = list(reader.fieldnames or [])
        if (
            not cols
            or not all(k.strip() for k in cols)
            or len(set(cols)) != len(cols)
            or set(required) - set(cols)
        ):
            raise ValueError(f"Invalid columns in {path.name}")
        rows = list(reader)
    if any(None in row or None in row.values() for row in rows):
        raise ValueError(f"Malformed CSV row in {path.name}")
    return cols, rows


def evidence(path: Path, *fields: str) -> tuple[list[str], list[dict]]:
    cols, rows = read_table(path, ("evidence_id", "source_id", *fields))
    ids = {r["evidence_id"] for r in rows}
    if len(ids) != len(rows) or any(not key.strip() for key in ids):
        raise ValueError("Missing or duplicate evidence_id in register")
    return cols, rows


def write_table(path: Path, cols, rows) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def append_history(path: Path, cols, rows) -> None:
    """Keep historical bytes, including their original quoting and line endings."""
    if not rows:
        return
    if not path.exists() or not path.stat().st_size:
        write_table(path, cols, rows)
        return
    with path.open("rb") as f:
        f.seek(-1, 2)
        terminated = f.read(1) in (b"\r", b"\n")
    with path.open("a", newline="", encoding="utf-8") as f:
        if not terminated:
            f.write("\n")
        csv.DictWriter(f, fieldnames=cols, lineterminator="\n").writerows(rows)


def json_field(row: dict, name: str) -> dict:
    value = parse_json(row.get(name) or "{}")
    if not isinstance(value, dict):
        raise ValueError(f"Expected object in {name} for {row['evidence_id']}")
    return value


def source_pdf(corpus: Path, source_id: str) -> Path:
    validate_source_id(source_id)
    return corpus / f"{source_id}.pdf"


def rebuild_command(root: Path, corpus: Path | None = None) -> str:
    """Print a runnable command even when the data and compiler live apart."""
    generator = Path(__file__).resolve().with_name("generate.py")
    root = root.resolve()
    if root == Path.cwd() == generator.parents[3] and corpus is None:
        return "python3 src/nbs_ruralscan/schema_tools/generate.py schema"
    schema = root / "schema"
    args = [
        "env",
        f"PYTHONPATH={generator.parents[2]}",
        sys.executable,
        str(generator),
        str(schema),
    ]
    if root != generator.parents[3]:
        # Compile derived files beside the selected data without automatic quarantine.
        args.append("--build-only")
    if corpus is not None:
        args.extend(["--corpus-dir", str(corpus.resolve())])
    return shlex.join(args)
