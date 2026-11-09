"""Historical record operations must keep concurrent edits and caught failures recoverable."""

from pathlib import Path
import shutil

import pytest

from nbs_ruralscan.schema_tools import publication
from nbs_ruralscan.schema_tools.record_publication import edit_records
from nbs_ruralscan.schema_tools.review_inputs import ReviewInputs


def test_edit_records_rehearses_real_edit_and_keeps_optional_file_absent(tmp_path):
    source = tmp_path / "policy.csv"
    source.write_text("id\navailable\n")
    existing = tmp_path / "register.csv"
    before = b"id,decision\r\na,old\r\n"
    existing.write_bytes(before)
    log = tmp_path / "metrics/audit.csv"
    observations = []

    def mutate(files):
        assert files[existing].read_bytes() == before
        assert files[log].parent.is_dir() and not files[log].exists()
        observations.append(source.read_text())
        files[existing].write_bytes(b"id,decision\na,new\n")
        return {"changed": 1}

    for dry in (True, False):
        result = edit_records(
            [existing, log],
            mutate,
            optional=[log],
            inputs=ReviewInputs([source]),
            dry_run=dry,
        )
        assert result == {"changed": 1}
        assert not log.parent.exists()
        assert existing.read_bytes() == (before if dry else b"id,decision\na,new\n")
    assert len(observations) == 2


@pytest.mark.parametrize("interruption", ["replacement_prepared", "installed"])
def test_late_read_only_input_change_restores_outputs_and_keeps_new_input(
    tmp_path, monkeypatch, interruption
):
    review = tmp_path / "decisions.json"
    review.write_text("{}")
    ev = tmp_path / "records/ev.csv"
    ev.parent.mkdir()
    ev.write_bytes(b"evidence_id,state\r\ne,live\r\n")
    before = ev.read_bytes()
    log = tmp_path / "metrics/log.csv"
    extra = tmp_path / "policy.csv"
    extra.write_text("yes")
    inputs = ReviewInputs([review])
    newer_review = '{"e":{"someone":{"decision":"ok"}}}'

    def mutate(private):
        inputs.include([extra])
        private[ev].write_bytes(b"evidence_id,state\ne,dropped\n")
        private[log].write_bytes(b"event\ndropped\n")

    if interruption == "replacement_prepared":
        copy = publication._replacement

        def replace_input(source, target, mode):
            temporary = copy(source, target, mode)
            if target == log:
                review.write_text(newer_review)
            return temporary

        monkeypatch.setattr(publication, "_replacement", replace_input)
    else:
        replace = publication.os.replace

        def replace_input(source, target):
            replace(source, target)
            if Path(target) == log:
                review.write_text(newer_review)

        monkeypatch.setattr(publication.os, "replace", replace_input)

    with pytest.raises(ValueError, match="changed"):
        edit_records([ev, log], mutate, inputs=inputs)
    assert review.read_text() == newer_review
    assert ev.read_bytes() == before
    assert not log.exists() and not log.parent.exists()


def test_newly_discovered_input_must_remain_disjoint_from_outputs(tmp_path):
    target = tmp_path / "records.csv"
    target.write_text("id\nold\n")
    inputs = ReviewInputs()

    def prepare(private):
        private[target].write_text("id\nreplacement\n")
        inputs.include([target])

    with pytest.raises(ValueError, match="alias"):
        edit_records([target], prepare, inputs=inputs)
    assert target.read_text() == "id\nold\n"


def test_optional_output_validation_and_input_list_drift_in_dry_run(tmp_path):
    stage = tmp_path / "recodes"
    stage.mkdir()
    history = tmp_path / "audit.csv"
    listed = list(stage.glob("out_*.json"))

    def verify():
        if list(stage.glob("out_*.json")) != listed:
            raise ValueError("Input list changed")

    def mutate(private):
        assert not private[history].exists()
        (stage / "out_2.json").write_text("[]")

    with pytest.raises(ValueError, match="Input list changed"):
        edit_records([history], mutate, verify=verify, optional=[history], dry_run=True)
    assert not history.exists()


def test_parent_traversal_guards_the_file_read_by_operator(tmp_path):
    root = tmp_path / "selected"
    ordinary = root / "nested"
    ordinary.mkdir(parents=True)
    (root / "annotation.json").write_text("{}")
    other = tmp_path / "other/nested"
    other.mkdir(parents=True)
    (other.parent / "annotation.json").write_text('{"other":true}')
    selected = ordinary / "../annotation.json"
    inputs = ReviewInputs([selected])
    assert selected.read_text() == "{}"
    ordinary.rmdir()
    ordinary.symlink_to(other, target_is_directory=True)
    assert selected.read_text() == '{"other":true}'
    with pytest.raises(ValueError, match="symlink"):
        inputs.verify()
    with pytest.raises(ValueError, match="symlink"):
        ReviewInputs([selected])


@pytest.mark.parametrize("already_installed", [False, True])
def test_edit_during_final_install_is_retained_and_reported(
    tmp_path, monkeypatch, already_installed
):
    evidence = tmp_path / "evidence.csv"
    history = tmp_path / "history.csv"
    original = b"id,status\na,old\n"
    evidence.write_bytes(original)
    history.write_bytes(b"id,event\n")
    competing = b"id,status\na,reviewed\n"

    def mutate(private):
        if already_installed:
            private[evidence].write_bytes(b"id,status\na,corrected\n")
        private[history].write_bytes(b"id,event\na,checked\n")

    replace = publication.os.replace

    def add_review(src, dest):
        replace(src, dest)
        if Path(dest) == history and history.read_bytes().endswith(b"checked\n"):
            evidence.write_bytes(competing)

    monkeypatch.setattr(publication.os, "replace", add_review)
    if already_installed:
        with pytest.raises(
            publication.PublicationRecoveryError, match="not overwriting"
        ) as caught:
            edit_records([evidence, history], mutate)
        recovery = caught.value.recovery_dir
        assert (recovery / "before/evidence.csv").read_bytes() == original
        shutil.rmtree(recovery)
    else:
        with pytest.raises(ValueError, match="Output changed"):
            edit_records([evidence, history], mutate)
    assert evidence.read_bytes() == competing
    assert history.read_bytes() == b"id,event\n"


def test_ordinary_parent_traversal_selects_intended_destination(tmp_path):
    child = tmp_path / "child"
    child.mkdir()
    selected = child / "../audit.txt"

    def prepare(private):
        private[selected].write_text("verified\n")

    def validate(path):
        assert path.read_bytes() == b"verified\n"

    edit_records(
        [selected], prepare, validators={selected: validate}, optional=[selected]
    )
    assert (tmp_path / "audit.txt").read_bytes() == b"verified\n"
    child.rmdir()
    nested = tmp_path / "external/nested"
    nested.mkdir(parents=True)
    child.symlink_to(nested, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        edit_records([selected], prepare, validators={selected: validate})
    assert not (nested.parent / "audit.txt").exists()
