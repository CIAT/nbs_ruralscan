"""Review continuity across browser origins and relocated technical input cards."""

from pathlib import Path
import shutil
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]


def test_browser_review_backup():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Browser backup tests require Node.js")
    subprocess.run([node, ROOT / "tests/js/browser_review_backup.test.cjs"], check=True)


def test_historic_input_cards_relocate_without_changing_draft_keys(tmp_path):
    cards = Path(
        "pipeline/t4_audit/agroforestry/final_audit/executable_categories/input_decision_cards.csv"
    )
    root = tmp_path / "source"
    output = tmp_path / "pages"
    for name in (
        cards,
        Path("schema/registers/EV_evidence_register.csv"),
        Path("schema/registers/SRC_source_register.csv"),
    ):
        dest = root / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
    result = subprocess.run(
        [
            sys.executable,
            ROOT / "scripts/build-t4-input-decisions.py",
            "--root",
            root,
            "--output-dir",
            output,
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Rendered 7 cards" in result.stdout
    page = output / "t4-input-decisions.html"
    assert "'t4-input-decisions-'+version" in page.read_text()
    assert list(output.iterdir()) == [page]
    assert not (root / "docs").exists()
