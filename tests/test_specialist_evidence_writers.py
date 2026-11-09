"""Specialist CLI writes are isolated, reversible and bound to the selected evidence."""

import csv
import importlib.util
import json
import shlex
import sys
from pathlib import Path

import fitz
import pytest

from nbs_ruralscan.schema_tools import publication
from nbs_ruralscan.schema_tools.specialist_records import REVIEW_COLUMNS


ROOT = Path(__file__).resolve().parents[1]
EV = Path("schema/registers/EV_evidence_register.csv")
LOG = Path("pipeline/metrics/review_log.csv")
METRICS = Path("pipeline/metrics/direction_audit.csv")


def script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


correct = script("apply-unit-corrections")
bundle = script("apply-bundle-backfill")
severity = script("apply-severity-tags")
direction = script("direction-audit")


def write_csv(path, cols, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def read(path):
    with path.open(newline="", encoding="utf8") as stream:
        return list(csv.DictReader(stream))


def inventory(root):
    return {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def put(path, data):
    path.write_text(json.dumps(data), encoding="utf8")
    return str(path)


@pytest.fixture
def dataset(tmp_path):
    root = tmp_path / "selected"
    r = dict(
        evidence_id="ev1",
        source_id="paper",
        relationship='{"direction":"negative"}',
        context='{"hazard_type":"drought"}',
        quote="The drought was severe. Tree planting increased yield.",
        page="1",
        variable="yield",
        nbs_id="practice",
        use_role="nbs_effect",
        claim_basis="table",
        lineage_of="",
    )
    write_csv(
        root / EV, list(r), [r, dict(r, evidence_id="ev2"), dict(r, evidence_id="ev3")]
    )
    write_csv(
        root / LOG,
        REVIEW_COLUMNS,
        [dict(date="past", evidence_id="historical", note="a multi-line\nrecord")],
    )
    audit = tmp_path / "external audit"
    audit.mkdir()
    put(
        audit / "out_1.json",
        [
            dict(evidence_id="ev1", direction="positive", cue="increased yield"),
            dict(evidence_id="ev2", direction="none", cue="Tree planting"),
            dict(evidence_id="ev3", direction="ambiguous", cue="increased"),
        ],
    )
    put(
        audit / "adj_1.json",
        [
            dict(
                evidence_id="ev1",
                outcome="correct",
                direction="positive",
                framing="loss",
                why="Correct sign",
            ),
            dict(
                evidence_id="ev2",
                outcome="correct",
                direction="none",
                why="Not significant",
            ),
            dict(evidence_id="ev3", outcome="ambiguous", why="Unclear"),
        ],
    )
    corpus = tmp_path / "external corpus"
    corpus.mkdir()
    with fitz.open() as pdf:
        pdf.new_page().insert_text((50, 50), "Half the farmers planted trees.")
        pdf.save(corpus / "paper.pdf")
    return root, audit, corpus


def test_correction_refuses_mixed_request_and_records_each_real_change(
    dataset, tmp_path
):
    root, _, _ = dataset
    item: dict = dict(
        evidence_id="ev1",
        change={"context.note_append": "first pass"},
        why="source verified",
    )
    path = tmp_path / "corrections.json"
    args = [str(path), "--reviewer", "ai_fixture", "--root", str(root)]
    prior = inventory(root)
    put(path, [dict(item, change={**item["change"], "page": "3"})])
    with pytest.raises(ValueError, match="REFUSED"):
        correct.main(args)
    assert inventory(root) == prior
    put(path, [item])
    assert correct.main([*args, "--dry-run"]) == 0 and inventory(root) == prior
    assert correct.main(args) == 0
    after = inventory(root)
    assert json.loads(read(root / EV)[0]["context"])["note"] == "first pass"
    assert len(read(root / LOG)) == 2 and after[LOG].startswith(prior[LOG])
    assert correct.main(args) == 0 and inventory(root) == after
    put(path, [dict(item, change={"context.note_append": "second pass"})])
    assert correct.main(args) == 0 and len(read(root / LOG)) == 3


def test_bundle_needs_verbatim_basis_and_reads_only_selected_pdf(dataset, tmp_path):
    root, _, corpus = dataset
    path = tmp_path / "bundle.json"
    args = [str(path), "--root", str(root), "--corpus-dir", str(corpus)]
    partial = dict(attribution="bundled", component_share_pct=50)
    put(
        path,
        dict(
            ev1=partial,
            ev2=dict(partial, component_share_basis="missing", component_share_page=1),
        ),
    )
    old = inventory(root)
    assert bundle.main(args) == 0 and inventory(root) == old
    partial.update(
        component_share_basis="Half the farmers planted trees.", component_share_page=1
    )
    put(path, dict(ev1=partial))
    assert bundle.main([*args, "--dry-run"]) == 0 and inventory(root) == old
    assert bundle.main(args) == 0
    after = inventory(root)
    assert json.loads(read(root / EV)[0]["context"])["component_share_pct"] == 50
    assert bundle.main(args) == 0 and inventory(root) == after


def test_severity_refusals_and_retries(dataset, tmp_path):
    root, _, _ = dataset
    tags = tmp_path / "tags.json"
    put(
        tags,
        dict(
            ev1=dict(hazard_severity="severe", severity_cue="drought was severe"),
            ev2=dict(hazard_severity="severe", severity_cue="missing"),
            ev3=dict(hazard_severity="invalid"),
        ),
    )
    args = [str(tags), "--root", str(root)]
    old = inventory(root)
    assert severity.main([*args, "--dry-run"]) == 0 and inventory(root) == old
    assert severity.main(args) == 0
    rows = read(root / EV)
    assert json.loads(rows[0]["context"])["severity_cue"] == "drought was severe"
    assert all("hazard_severity" not in json.loads(r["context"]) for r in rows[1:])
    after = inventory(root)
    assert severity.main(args) == 0 and inventory(root) == after


def test_direction_modes_keep_claims_metrics_and_review_history(dataset):
    root, audit, _ = dataset
    args = ["--root", str(root), "--recode-dir", str(audit)]
    old = inventory(root)
    assert (
        direction.main(["compare", *args, "--dry-run"]) == 0
        and not (audit / "disagreements.json").exists()
    )
    assert (
        direction.main(["compare", *args]) == 0
        and len(json.loads((audit / "disagreements.json").read_bytes())) == 3
    )
    assert direction.main(["apply", *args, "--dry-run"]) == 0 and inventory(root) == old
    assert direction.main(["apply", *args]) == 0
    rel = [json.loads(row["relationship"]) for row in read(root / EV)]
    assert rel[0] == dict(
        direction="positive", framing="loss", direction_cue="increased yield"
    )
    assert rel[1] == dict(
        direction="negative", significance="ns", direction_cue="Tree planting"
    )
    assert rel[2] == dict(direction="negative")
    assert [r["decision"] for r in read(root / LOG)] == ["", "ok", "ok", "flag"]
    first = inventory(root)
    assert direction.main(["apply", *args]) == 0
    after = inventory(root)
    assert (
        first[EV] == after[EV]
        and first[LOG] == after[LOG]
        and after[METRICS].startswith(first[METRICS])
        and len(after[METRICS]) > len(first[METRICS])
    )


@pytest.mark.parametrize("operation", ["direction", "corrections"])
def test_late_failure_restores_register_and_all_history(
    dataset, tmp_path, monkeypatch, operation
):
    root, audit, _ = dataset
    if operation == "direction":
        command = direction.main
        args = ["apply", "--recode-dir", str(audit), "--root", str(root)]
        fail = root / METRICS
    else:
        payload = put(
            tmp_path / "changes.json",
            [dict(evidence_id="ev1", change={"claim_basis": "figure_read"})],
        )
        command = correct.main
        args = [payload, "--reviewer", "ai_pass", "--root", str(root)]
        fail = root / LOG
    old = inventory(root)
    installed = publication.os.replace
    failed = False

    def replace(src, dst):
        nonlocal failed
        installed(src, dst)
        if Path(dst) == fail and not failed:
            failed = True
            raise OSError("late test failure")

    with monkeypatch.context() as patch:
        patch.setattr(publication.os, "replace", replace)
        with pytest.raises(OSError, match="late test failure"):
            command(args)
    assert failed and inventory(root) == old
    assert command(args) == 0 and inventory(root) != old


@pytest.mark.parametrize(
    "raw",
    [
        '{"ev1":{},"ev1":{}}',
        '{"ev1":{"hazard_severity":"severe","severity_cue":123}}',
        '[{"evidence_id":"ev1"},{"evidence_id":"ev1"}]',
    ],
)
def test_malformed_annotation_cannot_change_register(dataset, tmp_path, raw):
    root, _, _ = dataset
    path = tmp_path / "bad.json"
    path.write_text(raw)
    before = inventory(root)
    with pytest.raises(ValueError):
        if raw.startswith("["):
            correct.main([str(path), "--root", str(root), "--reviewer", "ai_test"])
        else:
            severity.main([str(path), "--root", str(root)])
    assert inventory(root) == before


def test_direction_rejects_changed_annotation_file_set(dataset, monkeypatch):
    root, audit, _ = dataset
    before = inventory(root)
    compare = direction._compare

    def add_input(*args):
        result = compare(*args)
        put(audit / "out_2.json", [])
        return result

    monkeypatch.setattr(direction, "_compare", add_input)
    with pytest.raises(ValueError, match="file set changed"):
        direction.compare(root=root, directory=audit)
    assert not (audit / "disagreements.json").exists() and inventory(root) == before


def test_bundle_rejects_pdf_drift(dataset, tmp_path, monkeypatch):
    root, _, corpus = dataset
    payload = put(
        tmp_path / "shares.json",
        {
            "ev1": dict(
                component_share_pct=50,
                component_share_basis="Half the farmers planted trees.",
                component_share_page=1,
            )
        },
    )
    verify = bundle.verify_basis

    def change(*args, **kwargs):
        result = verify(*args, **kwargs)
        (corpus / "paper.pdf").write_bytes(b"external change")
        return result

    monkeypatch.setattr(bundle, "verify_basis", change)
    before = inventory(root)
    with pytest.raises(ValueError, match="input changed"):
        bundle.main([payload, "--root", str(root), "--corpus-dir", str(corpus)])
    assert (
        inventory(root) == before
        and (corpus / "paper.pdf").read_bytes() == b"external change"
    )


def test_direction_rejects_duplicate_coder_ids_and_malformed_history(dataset):
    root, audit, _ = dataset
    duplicate = audit / "out_other.json"
    put(duplicate, [dict(evidence_id="ev1", direction="none")])
    before = inventory(root)
    with pytest.raises(ValueError, match="Duplicate evidence_id"):
        direction.apply(False, root=root, directory=audit)
    assert inventory(root) == before
    duplicate.unlink()
    with (root / LOG).open("a", encoding="utf8") as f:
        f.write("unterminated,short\n")
    before = inventory(root)
    with pytest.raises(ValueError, match="Malformed CSV"):
        direction.apply(False, root=root, directory=audit)
    assert inventory(root) == before


def test_overflowing_numeric_correction_refused(dataset, tmp_path):
    root, _, _ = dataset
    p = tmp_path / "overflow.json"
    p.write_text('[{"evidence_id":"ev1","change":{"relationship.value":1e500}}]')
    before = inventory(root)
    with pytest.raises(ValueError, match="Invalid JSON number"):
        correct.main([str(p), "--reviewer", "ai_fixture", "--root", str(root)])
    assert inventory(root) == before


@pytest.mark.parametrize("command", ["correct", "bundle", "severity", "direction"])
def test_detached_rebuild_hint_selects_compiler_and_data(
    dataset, tmp_path, capsys, command
):
    root, audit, corpus = dataset
    selected = root.with_name("selected data's copy")
    root.rename(selected)
    payload = tmp_path / "empty.json"
    payload.write_text("[]" if command == "correct" else "{}")
    runner, args = {
        "correct": (correct.main, [str(payload), "--reviewer", "ai_fixture"]),
        "bundle": (bundle.main, [str(payload), "--corpus-dir", str(corpus)]),
        "severity": (severity.main, [str(payload)]),
        "direction": (direction.main, ["apply", "--recode-dir", str(audit)]),
    }[command]
    assert runner([*args, "--root", str(selected)]) == 0
    hint = capsys.readouterr().out.strip().splitlines()[-1].split("now: ", 1)[1]
    assert shlex.split(hint) == [
        "env",
        f"PYTHONPATH={ROOT / 'src'}",
        sys.executable,
        str(ROOT / "src/nbs_ruralscan/schema_tools/generate.py"),
        str(selected / "schema"),
        "--build-only",
        *(["--corpus-dir", str(corpus)] if command == "bundle" else []),
    ]


def test_explicit_directory_aliases_pin_targets_and_refuse_redirected_children(
    dataset, tmp_path
):
    root, audit, corpus = dataset
    alias = tmp_path / "selected aliases"
    alias.symlink_to(tmp_path, target_is_directory=True)
    selected = alias / root.name
    shares = put(
        tmp_path / "bundle.json",
        {
            "ev1": dict(
                component_share_pct=50,
                component_share_basis="Half the farmers planted trees.",
                component_share_page=1,
            )
        },
    )
    bundle_args = [
        shares,
        "--root",
        str(selected),
        "--corpus-dir",
        str(alias / corpus.name),
    ]
    assert bundle.main(bundle_args) == 0
    assert json.loads(read(root / EV)[0]["context"])["component_share_pct"] == 50
    assert (
        direction.main(
            [
                "compare",
                "--root",
                str(selected),
                "--recode-dir",
                str(alias / audit.name),
            ]
        )
        == 0
    )
    assert (audit / "disagreements.json").is_file()
    before = inventory(root)
    pdf = corpus / "paper.pdf"
    actual = tmp_path / "redirected.pdf"
    pdf.rename(actual)
    pdf.symlink_to(actual)
    with pytest.raises(ValueError, match="symlink"):
        bundle.main(bundle_args)
    with pytest.raises(ValueError, match=r"symlink: .*/bundle\.json"):
        bundle.main([str(alias / "bundle.json"), *bundle_args[1:]])
    assert inventory(root) == before
