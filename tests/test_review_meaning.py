"""Exercise actual review-card JavaScript with recovered source metadata."""

from pathlib import Path
import shutil
import subprocess

import pytest


def test_review_card_meaning():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js needed for dashboard JavaScript test")
    subprocess.run(
        [node, "tests/js/review_meaning.test.cjs"],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
    )


def test_review_status_filters():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js needed for dashboard JavaScript test")
    subprocess.run(
        [node, "tests/js/review_status.test.cjs"],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
    )


def test_review_source_context():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js needed for dashboard JavaScript test")
    subprocess.run(
        [node, "tests/js/review_source_context.test.cjs"],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
    )


def test_review_table_continuations():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js needed for dashboard JavaScript test")
    subprocess.run(
        [node, "tests/js/review_table_continuations.test.cjs"],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
    )
