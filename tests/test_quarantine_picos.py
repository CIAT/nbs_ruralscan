"""Tests for the PICOS wrong-practice check + auto-quarantine guard (2026-06-23)."""

import csv
import json
import os
from dataclasses import replace
from pathlib import Path

import pytest

from nbs_ruralscan.schema_tools import check_picos, check_scope, quarantine


def test_check_scope_allocation_result_signal():
    # AHP land-use allocation OUTPUT is off-scope (a result, not a suitability rule)...
    alloc = (
        "the compatible land use allocation on land map unit 2 produced the ratio "
        "of 6.87%, 46.29%, 46.42% and 0.41% for settlement, conservation agriculture, "
        "agroforestry and forest respectively."
    )
    assert any(p.search(alloc) for p in check_scope._SIGNALS.values())
    # ...but a genuine slope-threshold suitability quote must stay CLEAN (no false positive).
    legit = (
        "Agroforestry is suitable on slopes up to 20% for agroforestry establishment."
    )
    assert not any(p.search(legit) for p in check_scope._SIGNALS.values())


_FIELDS = [
    "evidence_id",
    "nbs_id",
    "use_role",
    "quote",
    "reviewer_ok",
    "review_state",
    "attribution",
]


def _write_ev(tmp_path, rows):
    reg = tmp_path / "registers"
    reg.mkdir(parents=True, exist_ok=True)
    with (reg / "EV_evidence_register.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        w = csv.DictWriter(f, fieldnames=_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in _FIELDS})
    return reg / "EV_evidence_register.csv"


def test_picos_flags_reforestation_but_not_agroforestry(tmp_path):
    ev = _write_ev(
        tmp_path,
        [
            {
                "evidence_id": "e1",
                "nbs_id": "agroforestry",
                "use_role": "structural_suitability",
                "quote": "Reforestation on steep slopes above 30% was prioritised.",
            },
            {
                "evidence_id": "e2",  # mentions reforestation BUT also agroforestry -> not flagged
                "nbs_id": "agroforestry",
                "use_role": "structural_suitability",
                "quote": "Unlike reforestation, agroforestry suits slopes up to 30%.",
            },
            {
                "evidence_id": "e3",  # genuine AF claim -> not flagged
                "nbs_id": "agroforestry",
                "use_role": "structural_suitability",
                "quote": "Alley cropping is suitable where slope is below 15%.",
            },
        ],
    )
    flags = {f["evidence_id"] for f in check_picos.check(ev)}
    assert flags == {"e1"}


def test_picos_skips_reviewed_and_non_structural(tmp_path):
    ev = _write_ev(
        tmp_path,
        [
            {
                "evidence_id": "ok1",
                "nbs_id": "agroforestry",
                "use_role": "structural_suitability",
                "quote": "Afforestation programme details.",
                "reviewer_ok": "true",
            },
            {
                "evidence_id": "t6",
                "nbs_id": "agroforestry",
                "use_role": "nbs_effect",
                "quote": "Afforestation programme details.",
            },
        ],
    )
    assert check_picos.check(ev) == []


def test_quarantine_excludes_human_touched(tmp_path):
    schema = tmp_path / "schema"
    _write_ev(
        schema,
        [
            {
                "evidence_id": "junk1",
                "nbs_id": "agroforestry",
                "use_role": "structural_suitability",
                "quote": "The study site is located in northern Kenya.",  # off_scope
            },
            {
                "evidence_id": "human1",
                "nbs_id": "agroforestry",
                "use_role": "structural_suitability",
                "quote": "Reforestation across the catchment.",  # wrong_practice
            },
        ],
    )
    # human already decided on human1 -> must be excluded from auto-quarantine
    (tmp_path / "pipeline" / "review").mkdir(parents=True)
    (tmp_path / "pipeline" / "review" / "decisions.json").write_text(
        json.dumps({"human1": {"peetmate": {"decision": "ok"}}})
    )
    cands = {c["evidence_id"] for c in quarantine.candidates(schema)}
    assert "junk1" in cands
    assert "human1" not in cands

    applied = quarantine.apply(schema)
    assert [a["evidence_id"] for a in applied] == ["junk1"]
    rows = list(
        csv.DictReader((schema / "registers" / "EV_evidence_register.csv").open())
    )
    by = {r["evidence_id"]: r for r in rows}
    assert by["junk1"]["review_state"] == "dropped"
    assert "[AUTO-QUARANTINE" in by["junk1"]["attribution"]
    assert by["human1"]["review_state"] == ""
    # idempotent: a second apply changes nothing more
    assert quarantine.apply(schema) == []


@pytest.fixture
def detached(tmp_path):
    paths = quarantine.QuarantinePaths(
        tmp_path / "records/evidence.csv",
        tmp_path / "catalogue/sources.csv",
        tmp_path / "method/policy.csv",
        tmp_path / "history/applied.csv",
        tmp_path / "local/pending.json",
    )
    for p in vars(paths).values():
        p.parent.mkdir()
    paths.sources.write_text(
        "source_id,source_category\nsoftware,tool\npaper,updated_lit\n"
    )
    paths.policy.write_text(
        "variable,decision,reason\nlocal_rule,exclude,selected policy\ntriage,flag,needs review\n"
    )
    paths.review_log.write_text("evidence_id,decision\nreopened,reopen\n")
    # An older review store is a read-only input, including its original encoding.
    paths.decisions.write_bytes(
        '{"draft":{"alice":{"decision":"query","note":"café"}}}'.encode("cp1252")
    )
    default = dict(
        evidence_id="",
        source_id="paper",
        nbs_id="agroforestry",
        use_role="structural_suitability",
        variable="slope",
        reviewer_ok="",
        review_state="",
        quote="Reforestation across the catchment.",
        attribution="Prior note",
        extra="Untouched, including\na line break.",
    )
    rows = [
        dict(default, evidence_id="wrong"),
        dict(
            default,
            evidence_id="off",
            quote="The study area was located in Kenya.",
            review_state="pending",
        ),
        dict(
            default,
            evidence_id="policy",
            use_role="operational_risk",
            variable="local_rule",
        ),
        dict(
            default,
            evidence_id="advisory",
            use_role="operational_risk",
            variable="triage",
        ),
        dict(default, evidence_id="tool", source_id="software"),
        dict(default, evidence_id="draft"),
        dict(default, evidence_id="reopened"),
        dict(default, evidence_id="approved", reviewer_ok="TRUE"),
        dict(default, evidence_id="removed", review_state="dropped"),
    ]
    with paths.evidence.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(default), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return paths


def test_detached_screening_order_and_soft_drop_preserve_provenance(detached):
    paths = detached
    before = {p: p.read_bytes() for p in vars(paths).values()}
    proposed = quarantine.candidates(paths)
    assert [r["evidence_id"] for r in proposed] == ["off", "policy", "wrong"]
    assert {p: p.read_bytes() for p in before} == before
    applied = quarantine.apply(paths)
    assert [r["evidence_id"] for r in applied] == ["wrong", "off", "policy"]
    old_rows = list(
        csv.DictReader(before[paths.evidence].decode().splitlines(keepends=True))
    )
    with paths.evidence.open(newline="", encoding="utf-8") as stream:
        current = list(csv.DictReader(stream))
    by_id = {row["evidence_id"]: row for row in proposed}
    for old, row in zip(old_rows, current, strict=True):
        expected = old.copy()
        flag = by_id.get(row["evidence_id"])
        if flag:
            expected["review_state"] = "dropped"
            expected["attribution"] += (
                f" [AUTO-QUARANTINE {flag['kind']}:{flag['signal']}]"
            )
        assert row == expected
    assert all(p.read_bytes() == b for p, b in before.items() if p != paths.evidence)
    after = paths.evidence.read_bytes()
    assert quarantine.apply(paths) == [] and paths.evidence.read_bytes() == after


@pytest.mark.parametrize(
    ("field", "damaged"),
    [
        ("decisions", b'{"draft":'),
        ("decisions", b'{"draft":{"alice":"keep"}}'),
        ("review_log", b"decision,note\nkeep,checked\n"),
        ("review_log", b'evidence_id,decision\nreopened,"truncated'),
        ("review_log", b"evidence_id,decision\nreopened\n"),
    ],
)
def test_unreadable_human_state_refuses_classification_and_publication(
    detached, field, damaged
):
    path = getattr(detached, field)
    path.write_bytes(damaged)
    before = detached.evidence.read_bytes()
    for operation in (quarantine.candidates, quarantine.apply):
        with pytest.raises((ValueError, csv.Error)):
            operation(detached)
        assert detached.evidence.read_bytes() == before
        assert path.read_bytes() == damaged


@pytest.mark.parametrize(
    "dependency", ["evidence", "sources", "policy", "review_log", "decisions"]
)
def test_changed_dependency_prevents_install_and_preserves_other_writer(
    detached, monkeypatch, dependency
):
    changed = getattr(detached, dependency)
    original = changed.read_bytes()
    before = detached.evidence.read_bytes()
    check = check_picos.check

    def edit_during_check(staged):
        assert staged != detached.evidence
        flags = check(staged)
        changed.write_bytes(original + b"\n")
        return flags

    monkeypatch.setattr(check_picos, "check", edit_during_check)
    with pytest.raises(ValueError, match="changed"):
        quarantine.apply(detached)
    assert changed.read_bytes() == original + b"\n"
    if changed != detached.evidence:
        assert detached.evidence.read_bytes() == before


def test_failed_install_recovers_the_exact_original_evidence(detached, monkeypatch):
    before = detached.evidence.read_bytes()
    replace_file = os.replace
    failed = []

    def interrupt(source, destination):
        replace_file(source, destination)
        if Path(destination) == detached.evidence and not failed:
            failed.append(destination)
            raise OSError("interrupt after evidence replacement")

    monkeypatch.setattr(os, "replace", interrupt)
    with pytest.raises(OSError, match="interrupt"):
        quarantine.apply(detached)
    assert failed and detached.evidence.read_bytes() == before


def test_quarantine_rejects_aliases_and_ambiguous_evidence_ids(detached):
    with pytest.raises(ValueError, match="distinct"):
        replace(detached, decisions=detached.evidence)
    raw = detached.evidence.read_text().replace("approved,paper", "wrong,paper")
    detached.evidence.write_text(raw)
    with pytest.raises(ValueError, match="Duplicate evidence_id"):
        quarantine.apply(detached)
    assert detached.evidence.read_text() == raw


def test_redirected_pending_store_cannot_discard_a_human_exemption(detached, tmp_path):
    directory = tmp_path / "real" / "child"
    directory.mkdir(parents=True)
    selected = directory.parent / "decisions.json"
    selected.write_text('{"wrong":{"alice":{"decision":"keep"}}}')
    redirect = tmp_path / "redirect"
    redirect.symlink_to(directory, target_is_directory=True)
    other = tmp_path / "decisions.json"
    other.write_text("{}")
    paths = replace(detached, decisions=redirect / ".." / "decisions.json")
    before = paths.evidence.read_bytes()
    for action in (quarantine.candidates, quarantine.apply):
        with pytest.raises(ValueError, match="symlink"):
            action(paths)
        assert paths.evidence.read_bytes() == before
        assert selected.read_text() == '{"wrong":{"alice":{"decision":"keep"}}}'
        assert other.read_text() == "{}"


@pytest.mark.parametrize(
    ("field", "bad"),
    [
        ("sources", "source_id,category\nsoftware,tool\n"),
        ("sources", "source_id,source_category\nsoftware,tool\nsoftware,grey\n"),
        ("policy", "variable,decision,reason\nlocal_rule,exlcude,typo\n"),
        (
            "policy",
            "variable,decision,reason\nlocal_rule,flag,triage\nlocal_rule,exclude,conflict\n",
        ),
        ("policy", "variable,decision\nlocal_rule,exclude\n"),
    ],
)
def test_incomplete_or_ambiguous_exemptions_stop_quarantine(detached, field, bad):
    getattr(detached, field).write_text(bad, encoding="utf-8")
    original = {p: p.read_bytes() for p in vars(detached).values()}
    for action in (quarantine.candidates, quarantine.apply):
        with pytest.raises(ValueError):
            action(detached)
        assert original == {p: p.read_bytes() for p in original}


@pytest.mark.parametrize("field", ["reviewer_ok", "review_state", "source_id"])
def test_missing_review_and_source_columns_never_lose_an_exemption(detached, field):
    with detached.evidence.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames
        columns = [name for name in reader.fieldnames if name != field]
        rows = list(reader)
    with detached.evidence.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    original = detached.evidence.read_bytes()
    for action in (quarantine.candidates, quarantine.apply):
        with pytest.raises(ValueError, match="Invalid columns"):
            action(detached)
        assert detached.evidence.read_bytes() == original


def test_late_human_decision_survives_and_prevents_soft_drop(detached, monkeypatch):
    original = detached.evidence.read_bytes()
    pending = {
        "wrong": {"bob": {"decision": "keep", "note": "Reviewed during the build"}}
    }
    replace_file = os.replace
    installed = []

    def review_while_installing(source, destination):
        replace_file(source, destination)
        if Path(destination) == detached.evidence and not installed:
            installed.append(destination)
            detached.decisions.write_text(json.dumps(pending), encoding="utf-8")

    monkeypatch.setattr(os, "replace", review_while_installing)
    with pytest.raises(ValueError, match="changed"):
        quarantine.apply(detached)
    assert installed and detached.evidence.read_bytes() == original
    assert json.loads(detached.decisions.read_text()) == pending


def test_cli_and_callable_defaults_resolve_the_selected_working_tree(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.chdir(tmp_path)
    assert quarantine.candidates() == quarantine.apply() == []
    assert list(tmp_path.iterdir()) == []
    schema = tmp_path / "schema"
    _write_ev(
        schema,
        [
            dict(
                evidence_id="wrong",
                nbs_id="agroforestry",
                use_role="structural_suitability",
                quote="Reforestation across the catchment.",
            )
        ],
    )
    path = schema / "registers/EV_evidence_register.csv"
    original = path.read_bytes()
    assert quarantine.main(["--dry-run"]) == 0
    assert "dry-run" in capsys.readouterr().out and path.read_bytes() == original
    assert quarantine.main(["--apply", str(schema)]) == 0
    assert "dropped 1" in capsys.readouterr().out
    assert quarantine.apply() == []
