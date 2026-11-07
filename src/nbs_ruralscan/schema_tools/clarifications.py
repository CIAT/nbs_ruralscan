"""Questions and answers attached to the normal evidence review workflow."""

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock

from nbs_ruralscan.ingest.source_publication import SourceSnapshot
from .review_inputs import ReviewInputs
from .review_local import InvalidRequest, _install, read_decisions

LOCK = RLock()


@dataclass(frozen=True)
class ClarificationPaths:
    evidence: Path
    review_log: Path
    decisions: Path
    followups: Path
    history: Path
    pending: Path

    def __post_init__(self):
        for name, path in vars(self).items():
            object.__setattr__(self, name, Path(os.path.abspath(path)))
        if len({str(path.resolve()).casefold() for path in vars(self).values()}) != len(
            vars(self)
        ):
            raise ValueError("Clarification paths must be distinct")

    @classmethod
    def from_root(cls, root):
        root = Path(root).resolve()
        return cls(
            root / "schema/registers/EV_evidence_register.csv",
            root / "pipeline/metrics/review_log.csv",
            root / "pipeline/review/decisions.json",
            root / "pipeline/t4_audit/agroforestry/review_followups.json",
            root / "pipeline/metrics/clarification_log.json",
            root / "pipeline/review/clarifications.json",
        )


def _paths(root):
    return (
        root
        if isinstance(root, ClarificationPaths)
        else ClarificationPaths.from_root(root)
    )


def _validate_events(events):
    # Older history can lack review-specific fields. Keep its original keys and
    # values so digest-based acknowledgement works across versions.
    if not isinstance(events, list):
        raise ValueError("Clarification events must be a list")
    for event in events:
        if not isinstance(event, dict) or any(
            not isinstance(event.get(key), str) or not event[key].strip()
            for key in ("issue_id", "date")
        ):
            raise ValueError("Clarification event requires a dated issue ID")
        if any(
            key in event and not isinstance(event[key], str)
            for key in ("action", "fingerprint", "reviewer", "note")
        ) or (
            "evidence_ids" in event
            and (
                not isinstance(event["evidence_ids"], list)
                or not all(isinstance(eid, str) for eid in event["evidence_ids"])
            )
        ):
            raise ValueError("Malformed clarification event fields")
    return events


def read_events(path):
    return _validate_events(read_json(Path(path), []))


def serialize_events(events):
    return (json.dumps(_validate_events(events), indent=2) + "\n").encode("utf-8")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def read_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def event_key(event):
    return digest(event)


def shared_events(root):
    return read_events(_paths(root).history)


def pending_events(root):
    paths = _paths(root)
    known = {event_key(e) for e in read_events(paths.history)}
    return [e for e in read_events(paths.pending) if event_key(e) not in known]


def all_events(root):
    paths = _paths(root)
    events = {
        event_key(e): e for e in read_events(paths.history) + read_events(paths.pending)
    }
    return sorted(events.values(), key=lambda e: (e["date"], event_key(e)))


def merge_history(shared, local):
    """Return ordered history and the legacy count of newly seen local entries."""
    shared, local = _validate_events(shared), _validate_events(local)
    known = {event_key(e) for e in shared}
    pending = [e for e in local if event_key(e) not in known]
    if not pending:
        return shared, 0
    unique = {event_key(e): e for e in shared + pending}
    return sorted(unique.values(), key=lambda e: (e["date"], event_key(e))), len(
        pending
    )


def publish(root, *, local_events=None):
    """Replay local events onto shared history. Keep the local store for retry."""
    paths = _paths(root)
    with LOCK:
        history = SourceSnapshot.capture([paths.history])
        inputs = ReviewInputs([] if local_events is not None else [paths.pending])
        local = read_events(paths.pending) if local_events is None else local_events
        events, count = merge_history(read_events(paths.history), local)
        history.assert_unchanged()
        inputs.verify()
        if count:
            _install(history, {paths.history: serialize_events(events)}, inputs.verify)
        return count


def build(root):
    paths = _paths(root)
    with paths.evidence.open() as f:
        evidence = {r["evidence_id"]: r for r in csv.DictReader(f)}
    with paths.review_log.open() as f:
        log = list(csv.DictReader(f))
    latest = {}
    for r in log:
        who = latest.setdefault(r["evidence_id"], {})
        if r["decision"].lower() == "reopen":
            who.pop(r["reviewer"], None)
        elif r["decision"]:
            who[r["reviewer"]] = r
    for eid, reviewers in read_decisions(paths.decisions)[0].items():
        for reviewer, r in reviewers.items():
            if r.get("decision"):
                latest.setdefault(eid, {})[reviewer] = dict(r, reviewer=reviewer)
    followups = list(read_json(paths.followups, {}).values())
    groups = {}
    for eid, ev in evidence.items():
        if ev["use_role"] not in {
            "structural_suitability",
            "operational_risk",
        }:
            continue
        reviews = list(latest.get(eid, {}).values())
        # A completed scope correction is not an unanswered clarification.
        # Keep incomplete reclassifications visible until the register reflects them.
        concerns = [
            r
            for r in reviews
            if r["decision"].lower() not in {"ok", "keep"}
            and not (
                r["decision"].lower() == "reclassify"
                and ev["claim_scope"] in {"species_specific", "crop_specific"}
            )
        ]
        if (
            not concerns
            and any(r["decision"].lower() in {"ok", "keep"} for r in reviews)
            and ev["reviewer_ok"].lower() != "true"
        ):
            concerns = [
                dict(
                    reviewer="Status reconciliation",
                    note="Recorded keep decision is not reflected in the approval flag.",
                    reason="status_mismatch",
                    decision="query",
                )
            ]
        # Retain answered questions after a record decision; acceptance is history,
        # never a substitute for reviewing the evidence. Only recover actual queries.
        for old in log:
            if old["evidence_id"] != eid or old["decision"].lower() not in {
                "query",
                "flag",
            }:
                continue
            if any(
                a["evidence_id"] == eid
                and a.get("reviewer") == old["reviewer"]
                and a.get("note", "").strip() == old.get("note", "").strip()
                for a in followups
            ):
                if not any(
                    c["reviewer"] == old["reviewer"]
                    and c.get("note", "").strip() == old.get("note", "").strip()
                    for c in concerns
                ):
                    concerns.append(old)
        for r in concerns:
            question = r.get("note", "").strip() or (
                "Review reason: "
                + (r.get("reason") or r["decision"])
                + ". No written question recorded; investigate history before requesting another review."
            )
            # Exact shared question, same source and reviewer only. Never group merely by variable.
            key = digest(
                [ev["source_id"], r["reviewer"], question, r.get("reason", "")]
            )[:20]
            g = groups.setdefault(
                key,
                dict(
                    id=key,
                    source=ev["source_id"],
                    reviewer=r["reviewer"],
                    question=question,
                    records=[],
                    answers=[],
                ),
            )
            g["records"].append(
                dict(
                    evidence_id=eid,
                    variable=ev["variable"],
                    page=ev["page"],
                    quote=ev["quote"],
                    claim_scope=ev["claim_scope"],
                    relationship=ev["relationship"],
                )
            )
            for answer in followups:
                if (
                    answer["evidence_id"] != eid
                    or answer.get("note", "").strip() != r.get("note", "").strip()
                    or answer.get("reviewer") != r["reviewer"]
                ):
                    continue
                valid = bool(answer.get("resolution_checks"))
                for check in answer.get("resolution_checks", []):
                    value = evidence.get(check["evidence_id"], {}).get(
                        check["field"], ""
                    )
                    if hashlib.sha256(value.encode()).hexdigest() != check["sha256"]:
                        valid = False
                if answer.get("status") in {"resolved", "needs_judgement"} and valid:
                    g["answers"].append(
                        dict(
                            evidence_id=eid,
                            response=answer["resolution"],
                            needs_judgement=answer.get("status") == "needs_judgement",
                            source_check=answer.get("source_check", {}),
                        )
                    )
    events = all_events(paths)
    result = []
    for g in groups.values():
        g["records"].sort(key=lambda r: r["evidence_id"])
        g["fingerprint"] = digest(g)
        covered = {a["evidence_id"] for a in g["answers"]}
        g["status"] = (
            "answer_ready"
            if all(r["evidence_id"] in covered for r in g["records"])
            else "needs_investigation"
        )
        if any(a.get("needs_judgement") for a in g["answers"]):
            g["status"] = "needs_judgement"
        g["history"] = [e for e in events if e["issue_id"] == g["id"]]
        # A decision closes only this reviewer's question on this record.
        # Shared answers remain open on other records. Legacy accept events do not close.
        for item in g["records"]:
            decision = latest.get(item["evidence_id"], {}).get(g["reviewer"], {})
            closed = decision.get("decision", "").lower() in {"ok", "keep", "drop"}
            superseded = decision.get("decision", "").lower() in {"query", "flag"} and (
                decision.get("note", "").strip() != g["question"].strip()
                and bool(decision.get("note", "").strip())
            )
            followup = any(
                e.get("fingerprint") == g["fingerprint"]
                and e.get("action") in {"reply", "reopen"}
                and item["evidence_id"] in e.get("evidence_ids", [])
                for e in g["history"]
            )
            item["review_status"] = (
                "resolved"
                if closed or superseded
                else "needs_investigation"
                if followup
                else g["status"]
            )
        if all(r["review_status"] == "needs_investigation" for r in g["records"]):
            g["status"] = "needs_investigation"
        if all(r["review_status"] == "resolved" for r in g["records"]):
            g["status"] = "resolved"
        result.append(g)
    return sorted(result, key=lambda g: (g["status"], g["source"], g["id"]))


def prepare_event(issues, payload):
    """Check a response against the issue snapshot and construct its event."""
    if not isinstance(payload, dict):
        raise InvalidRequest("Clarification response must be an object")
    for key in ("issue_id", "fingerprint", "action", "reviewer", "note", "evidence_id"):
        value = payload.get(key)
        if value is not None and not isinstance(value, str):
            raise InvalidRequest(f"{key} must be text")
    issue = issues.get(payload.get("issue_id"))
    if not issue or payload.get("fingerprint") != issue["fingerprint"]:
        raise InvalidRequest("Issue changed. Reload before responding.")
    action = payload.get("action")
    if action not in {"accept", "reply", "reopen"}:
        raise InvalidRequest("Unknown action")
    reviewer = (payload.get("reviewer") or "").strip()
    note = (payload.get("note") or "").strip()
    if not reviewer or (action == "reply" and not note):
        raise InvalidRequest("Reviewer and a written reply are required.")
    if action == "accept" and issue["status"] != "answer_ready":
        raise InvalidRequest(
            "Only a complete answer awaiting confirmation can be accepted."
        )
    ids = [r["evidence_id"] for r in issue["records"]]
    if payload.get("evidence_id"):
        if payload["evidence_id"] not in ids:
            raise InvalidRequest("Record does not belong to this question")
        ids = [payload["evidence_id"]]
    event = dict(
        issue_id=issue["id"],
        fingerprint=issue["fingerprint"],
        action=action,
        reviewer=reviewer,
        note=note,
        date=datetime.now(timezone.utc).isoformat(),
        evidence_ids=ids,
    )
    return event


def record_many(root, payloads):
    """Validate all replies against the same review state, then append them once."""
    paths = _paths(root)
    with LOCK:
        selected = SourceSnapshot.capture([paths.pending])
        inputs = ReviewInputs(
            [
                paths.evidence,
                paths.review_log,
                paths.decisions,
                paths.followups,
                paths.history,
            ]
        )
        issues = {g["id"]: g for g in build(paths)}
        new = [prepare_event(issues, payload) for payload in payloads]
        pending = read_events(paths.pending)
        selected.assert_unchanged()
        inputs.verify()
        if new:
            _install(
                selected,
                {paths.pending: serialize_events(pending + new)},
                inputs.verify,
            )
        return new


def record(root, payload):
    return record_many(root, [payload])[0]
