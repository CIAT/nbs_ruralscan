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
