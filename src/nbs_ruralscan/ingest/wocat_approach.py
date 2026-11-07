"""Acquire WOCAT Approach narratives, separately from Technology impact ratings.

The deterministic Markdown is the section-locator artifact. Raw questionnaire and
fetch metadata are sidecars; no values or evidence units are inferred here.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from .integrity import validate_source_id
from .source_publication import SourceSnapshot
from .wocat import _BLOCK

# Administrative/media fields are not questionnaire claims. Linked technologies are
# separate sources: never traverse them as if they belonged to this approach.
EXCLUDED = {
    "compiler",
    "compiler_id",
    "editors",
    "editor_ids",
    "reviewers",
    "reviewer_ids",
    "publishers",
    "publisher_ids",
    "header_image",
    "header_image_id",
    "images",
    "key_resource_persons",
    "technologies",
    "technology_ids",
    "accept_conditions",
    "funding_projects",
    "funding_institutions",
    "labels",
}


def approach_id(source_id: str) -> int:
    validate_source_id(source_id)
    match = re.fullmatch(r"wocat_[a-z0-9_]+_approach_(\d+)", source_id)
    if not match:
        raise ValueError(f"Not a WOCAT approach source ID: {source_id}")
    return int(match[1])


def parse(page: str, aid: int) -> dict:
    for url, block in _BLOCK.findall(page):
        if url != f"/api/database/approaches/{aid}/":
            continue
        outer = json.loads(html.unescape(block))
        body = outer.get("body")
        payload = json.loads(body) if isinstance(body, str) else body
        sv = payload.get("selected_version", {}) if isinstance(payload, dict) else {}
        if (
            not isinstance(payload, dict)
            or payload.get("id") != aid
            or sv.get("approach") != aid
            or not isinstance(sv.get("name"), dict)
            or not sv["name"].get("en")
            or not sv.get("description", {}).get("en")
            or sv.get("is_deleted")
            or sv.get("status") != 4
        ):
            raise ValueError(
                "Approach identity, publication status or English narrative missing"
            )
        return payload
    raise ValueError(
        f"Approach {aid} questionnaire not found; technology records are not interchangeable"
    )


def _leaves(value, path=""):
    if isinstance(value, dict):
        if "en" in value:
            yield path, " ".join(str(value["en"]).split())
        else:
            for key in sorted(value):
                yield from _leaves(value[key], f"{path}.{key}" if path else key)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from _leaves(item, f"{path}[{i}]")
    elif value is not None and value != "":
        yield path, str(value).lower() if isinstance(value, bool) else str(value)


def render(payload: dict, source_id: str) -> str:
    aid = approach_id(source_id)
    sv = payload["selected_version"]
    if payload["id"] != aid or sv["approach"] != aid:
        raise ValueError("Approach ID mismatch")
    lines = [
        f"# WOCAT approach {aid} — {sv['name']['en']}",
        "",
        f"source_id: {source_id}",
        f"selected_version_id: {sv['id']}",
        "",
    ]
    for key in sorted(set(sv) - EXCLUDED):
        leaves = list(_leaves(sv[key]))
        if leaves:
            lines += [f"## {key}", ""]
            lines += [f"{path}: {value}" if path else value for path, value in leaves]
            lines.append("")
    return "\n".join(lines)


def acquire(source_id: str, corpus: Path, *, expected_sha1: str = "") -> Path:
    aid = approach_id(source_id)
    corpus = Path(corpus)
    source, out, sidecar = (
        corpus / f"{source_id}{suffix}"
        for suffix in (".source.json", ".md", ".meta.json")
    )
    snapshot = SourceSnapshot.capture([source, out, sidecar])
    url = f"https://wocat.net/en/database/approaches/{aid}/"
    req = urllib.request.Request(
        url, headers={"User-Agent": "nbs-ruralscan/wocat-approach-adapter"}
    )
    with urllib.request.urlopen(req, timeout=40) as response:
        page = response.read().decode("utf-8")
    payload = parse(page, aid)
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=1)
    md = render(payload, source_id)
    digest = hashlib.sha1(md.encode()).hexdigest()
    if expected_sha1 and digest != expected_sha1:
        raise ValueError(
            "Approach transcript changed; restore archived artifact or re-review source version"
        )
    meta = dict(
        source_id=source_id,
        adapter="ingest/wocat_approach.py",
        url=url,
        fetched_at=datetime.now(timezone.utc).isoformat(),
        selected_version_id=payload["selected_version"]["id"],
        source_sha1=hashlib.sha1(raw.encode()).hexdigest(),
        render_sha1=digest,
    )

    def validate(staged: Path) -> None:
        raw_bytes = (staged / source.name).read_bytes()
        md_bytes = (staged / out.name).read_bytes()
        record = json.loads((staged / sidecar.name).read_text(encoding="utf-8"))
        questionnaire = json.loads(raw_bytes)
        if (
            render(questionnaire, source_id).encode("utf-8") != md_bytes
            or record != meta
            or hashlib.sha1(raw_bytes).hexdigest() != meta["source_sha1"]
            or hashlib.sha1(md_bytes).hexdigest() != meta["render_sha1"]
            or (expected_sha1 and meta["render_sha1"] != expected_sha1)
        ):
            raise ValueError("WOCAT approach artifact/provenance mismatch")

    snapshot.publish(
        {
            source: raw.encode("utf-8"),
            out: md.encode("utf-8"),
            sidecar: json.dumps(meta, indent=2).encode("utf-8"),
        },
        validate,
    )
    return out
