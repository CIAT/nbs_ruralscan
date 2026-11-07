"""Local review edits, captured before preparation and published with rollback."""

from contextlib import closing, contextmanager
import csv
from datetime import date, datetime, timezone
import io
import json
from pathlib import Path
import re
import sqlite3

from nbs_ruralscan.ingest.source_publication import SourceSnapshot


@contextmanager
def review_pair_lock():
    """Keep a submission process out of the interval between the two replacements.

    A short SQLite write reservation is cross-platform and released by the OS on
    process exit. The per-user lock contains no review data. Never hold it during
    network operations, rendering, or review on another person's machine.
    """
    directory = Path.home() / ".cache" / "ruralscan"
    directory.mkdir(parents=True, exist_ok=True)
    try:
        connection = sqlite3.connect(directory / "review-snapshot.lock", timeout=10)
    except sqlite3.Error as exc:
        raise OSError(f"Cannot open the review snapshot lock: {exc}") from exc
    with closing(connection):
        try:
            connection.execute("BEGIN IMMEDIATE")
        except sqlite3.Error as exc:
            raise OSError(
                "Could not reserve the review snapshot. Retry the operation."
            ) from exc
        yield


class InvalidRequest(ValueError):
    """A review action needs different input from its caller."""


_TEXT_FIELDS = ("decision", "reason", "note", "claim_scope", "taxon")


def validate_text_fields(payload, fields):
    for key in fields:
        if key in payload and not isinstance(payload[key], str):
            raise InvalidRequest(f"{key} must be text")


def read_decisions(path: Path) -> tuple[dict, bytes | None]:
    """Read historical and current stores. Return UTF-8 repair bytes only if needed."""
    if not path.exists():
        return {}, None
    raw = path.read_bytes()
    try:
        repair = None
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("cp1252")
            repair = text.encode("utf-8")
        store = json.loads(text)
        if not isinstance(store, dict) or any(
            not isinstance(reviewers, dict)
            or any(
                not isinstance(entry, dict)
                or any(
                    key in entry and not isinstance(entry[key], str)
                    for key in _TEXT_FIELDS
                )
                for entry in reviewers.values()
            )
            for reviewers in store.values()
        ):
            raise ValueError("Expected decisions grouped by evidence ID and reviewer")
    except ValueError as exc:
        raise ValueError(f"Unreadable decision store {path.name}: {exc}") from exc
    return store, repair


def _store_bytes(store: dict) -> bytes:
    return json.dumps(store, indent=2).encode("utf-8")


def _install(snapshot, contents, verify=None):
    """Some captured files can remain absent. Guard them even when publishing a subset."""

    def validate(stage):
        snapshot.assert_unchanged()
        if verify is not None:
            verify()
        for path, body in contents.items():
            if (stage / path.name).read_bytes() != body:
                raise ValueError(f"Staged review record differs: {path.name}")

    targets = (
        snapshot
        if set(snapshot.paths) == set(contents)
        else SourceSnapshot.capture(contents)
    )
    targets.publish(contents, validate)


def load_store(path: Path) -> dict:
    snapshot = SourceSnapshot.capture([path])
    store, repair = read_decisions(path)
    snapshot.assert_unchanged()
    if repair is not None:
        _install(snapshot, {path: repair})
    return store


def save_decision(paths, payload):
    from . import clarifications
    from .review_inputs import ReviewInputs

    eid = payload.get("evidence_id")
    decision = payload.get("decision")
    if not isinstance(eid, str) or not eid.strip():
        raise InvalidRequest("evidence_id required")
    validate_text_fields(
        payload, ("reason", "note", "reviewer", "claim_scope", "taxon")
    )
    if decision is not None:
        validate_text_fields(payload, ("decision",))
    reviewer = _field(payload, "reviewer") or "reviewer"
    answers = payload.get("answered_issue_ids") if decision in {"query", "flag"} else []
    if answers and (
        not isinstance(answers, list) or not all(isinstance(a, str) for a in answers)
    ):
        raise InvalidRequest("answered_issue_ids must contain issue IDs")
    targets = [paths.pending, paths.decisions] if answers else [paths.decisions]
    snapshot = SourceSnapshot.capture(targets)
    store, _ = read_decisions(paths.decisions)
    writes = {}
    verify = None
    if answers:
        inputs = ReviewInputs(
            [paths.evidence, paths.review_log, paths.followups, paths.history]
        )
        verify = inputs.verify
        issues = {issue["id"]: issue for issue in clarifications.build(paths)}
        events = clarifications.read_events(paths.pending)
        replies = []
        for issue_id in dict.fromkeys(answers):
            issue = issues.get(issue_id)
            if issue and any(
                record["evidence_id"] == eid for record in issue["records"]
            ):
                replies.append(
                    clarifications.prepare_event(
                        issues,
                        {
                            "issue_id": issue_id,
                            "fingerprint": issue["fingerprint"],
                            "evidence_id": eid,
                            "reviewer": reviewer,
                            "action": "reply",
                            "note": payload.get("note", ""),
                        },
                    )
                )
        if replies:
            writes[paths.pending] = clarifications.serialize_events(events + replies)
    reviewers = store.setdefault(eid, {})
    if decision:
        entry = {
            "decision": decision,
            "reason": payload.get("reason", ""),
            "note": payload.get("note", ""),
        }
        for key in ("taxon", "claim_scope"):
            if payload.get(key):
                entry[key] = str(payload[key]).strip()
        if payload.get("reviewed_conflict"):
            entry["reviewed_conflict_at"] = datetime.now(timezone.utc).isoformat()
        reviewers[reviewer] = entry
    else:
        reviewers.pop(reviewer, None)
    if not reviewers:
        store.pop(eid)
    writes[paths.decisions] = _store_bytes(store)
    if paths.pending in writes:
        with review_pair_lock():
            _install(snapshot, writes, verify)
    else:
        _install(snapshot, writes, verify)
    return {
        "ok": True,
        "decided": sum(
            1
            for byrev in store.values()
            for entry in byrev.values()
            if entry.get("decision")
        ),
    }


def _field(payload, key):
    value = payload.get(key) or ""
    if not isinstance(value, str):
        raise InvalidRequest(f"{key} must be text")
    return value.strip()


def clear_decisions(path: Path, payload):
    reviewer = _field(payload, "reviewer")
    if not reviewer:
        raise InvalidRequest("reviewer required (use '*' to clear all)")
    backup = path.with_name("decisions.bak.json")
    snapshot = SourceSnapshot.capture([backup, path])
    store, repair = read_decisions(path)
    writes = {}
    if path.exists():
        writes[backup] = repair if repair is not None else path.read_bytes()
    if reviewer == "*":
        store.clear()
        result = {"ok": True, "cleared_for": "ALL"}
    else:
        cleared = 0
        for eid, reviewers in list(store.items()):
            entry = reviewers.get(reviewer)
            if entry is not None and entry.get("applied") not in (True, "true"):
                del reviewers[reviewer]
                cleared += 1
            if not reviewers:
                del store[eid]
        result = {"ok": True, "cleared_for": reviewer, "cleared": cleared}
    writes[path] = _store_bytes(store)
    _install(snapshot, writes)
    return result


_GAP_FIELDS = (
    "gap_id",
    "date",
    "reporter",
    "nbs_id",
    "suitability_family_id",
    "table",
    "source_id",
    "location",
    "variable",
    "note",
    "status",
)


def report_gap(path: Path, payload):
    row = {key: _field(payload, key) for key in _GAP_FIELDS[2:-1]}
    if not (row["variable"] or row["note"]):
        raise InvalidRequest("a gap needs at least a variable or a note")
    snapshot = SourceSnapshot.capture([path])
    raw = path.read_bytes() if path.exists() else b""
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""), strict=True)
    if raw and tuple(reader.fieldnames or ()) != _GAP_FIELDS:
        raise ValueError("Unexpected gap register header")
    numbers = [
        int(match[1])
        for record in reader
        if (match := re.fullmatch(r"gap_(\d+)", record["gap_id"]))
    ]
    gap_id = f"gap_{max(numbers, default=0) + 1:04d}"
    row.update(gap_id=gap_id, date=date.today().isoformat(), status="open")
    row["reporter"] = row["reporter"] or "reviewer"
    addition = io.StringIO(newline="")
    writer = csv.DictWriter(addition, fieldnames=_GAP_FIELDS)
    if not raw:
        writer.writeheader()
    elif not raw.endswith((b"\n", b"\r")):
        addition.write("\n")
    writer.writerow(row)
    _install(snapshot, {path: raw + addition.getvalue().encode("utf-8")})
    return {"ok": True, "gap_id": gap_id}
