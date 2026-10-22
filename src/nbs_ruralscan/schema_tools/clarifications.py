"""Clarification workflow, independent of extraction approval and consensus."""

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

LOCK = Lock()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def read_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def event_key(event):
    return digest(event)


def shared_events(root):
    return read_json(Path(root) / "pipeline/metrics/clarification_log.json", [])


def pending_events(root):
    known = {event_key(e) for e in shared_events(root)}
    return [
        e
        for e in read_json(Path(root) / "pipeline/review/clarifications.json", [])
        if event_key(e) not in known
    ]


def all_events(root):
    events = {event_key(e): e for e in shared_events(root) + pending_events(root)}
    return sorted(events.values(), key=lambda e: (e["date"], event_key(e)))


def publish(root):
    """Replay local events onto latest shared history, preserving others' events."""
    root = Path(root)
    with LOCK:
        pending = pending_events(root)
        if not pending:
            return 0
        path = root / "pipeline/metrics/clarification_log.json"
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(all_events(root), indent=2) + "\n", encoding="utf-8")
        tmp.replace(path)
        return len(pending)


def build(root):
    root = Path(root)
    with (root / "schema/registers/EV_evidence_register.csv").open() as f:
        evidence = {r["evidence_id"]: r for r in csv.DictReader(f)}
    with (root / "pipeline/metrics/review_log.csv").open() as f:
        log = list(csv.DictReader(f))
    latest = {}
    for r in log:
        who = latest.setdefault(r["evidence_id"], {})
        if r["decision"].lower() == "reopen":
            who.pop(r["reviewer"], None)
        elif r["decision"]:
            who[r["reviewer"]] = r
    for eid, reviewers in read_json(
        root / "pipeline/review/decisions.json", {}
    ).items():
        for reviewer, r in reviewers.items():
            if r.get("decision"):
                latest.setdefault(eid, {})[reviewer] = dict(r, reviewer=reviewer)
    followups = list(
        read_json(
            root / "pipeline/t4_audit/agroforestry/review_followups.json", {}
        ).values()
    )
    groups = {}
    for eid, ev in evidence.items():
        if (
            ev["nbs_id"] != "agroforestry"
            or ev["use_role"] not in {"structural_suitability", "operational_risk"}
            or ev["review_state"] == "dropped"
        ):
            continue
        reviews = list(latest.get(eid, {}).values())
        concerns = [r for r in reviews if r["decision"].lower() not in {"ok", "keep"}]
        if not concerns and reviews and ev["reviewer_ok"].lower() != "true":
            concerns = [
                dict(
                    reviewer="Status reconciliation",
                    note="Recorded keep decision is not reflected in the approval flag.",
                    reason="status_mismatch",
                    decision="query",
                )
            ]
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
    events = all_events(root)
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
        for e in g["history"]:
            if e["fingerprint"] != g["fingerprint"]:
                continue
            if e["action"] == "accept":
                g["status"] = "resolved"
            elif e["action"] in {"reply", "reopen"}:
                g["status"] = "needs_investigation"
        result.append(g)
    return sorted(result, key=lambda g: (g["status"], g["source"], g["id"]))


def record(root, payload):
    root = Path(root)
    with LOCK:
        issues = {g["id"]: g for g in build(root)}
        issue = issues.get(payload.get("issue_id"))
        if not issue or payload.get("fingerprint") != issue["fingerprint"]:
            raise ValueError("Issue changed. Reload before responding.")
        action = payload.get("action")
        if action not in {"accept", "reply", "reopen"}:
            raise ValueError("Unknown action")
        reviewer = str(payload.get("reviewer") or "").strip()
        note = str(payload.get("note") or "").strip()
        if not reviewer or (action == "reply" and not note):
            raise ValueError("Reviewer and a written reply are required.")
        if action == "accept" and issue["status"] != "answer_ready":
            raise ValueError(
                "Only a complete answer awaiting confirmation can be accepted."
            )
        event = dict(
            issue_id=issue["id"],
            fingerprint=issue["fingerprint"],
            action=action,
            reviewer=reviewer,
            note=note,
            date=datetime.now(timezone.utc).isoformat(),
            evidence_ids=[r["evidence_id"] for r in issue["records"]],
        )
        path = root / "pipeline/review/clarifications.json"
        events = read_json(path, [])
        events.append(event)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(events, indent=2) + "\n", encoding="utf-8")
        tmp.replace(path)
        return event
