"""Merge drivers for register CSVs and id-keyed JSON (scripts/git-merge-*.py)."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYCSV = ROOT / "scripts" / "git-merge-keycsv.py"
JSONU = ROOT / "scripts" / "git-merge-jsonunion.py"


def _run(driver, tmp, base, ours, theirs, name="f"):
    paths = []
    for tag, text in (("O", base), ("A", ours), ("B", theirs)):
        p = tmp / f"{name}.{tag}"
        p.write_text(text, encoding="utf-8")
        paths.append(str(p))
    rc = subprocess.run([sys.executable, str(driver), *paths, name]).returncode
    return rc, Path(paths[1]).read_text(encoding="utf-8")


def test_keycsv_merges_disjoint_rows(tmp_path):
    base = "id,v\na,1\nb,1\n"
    ours = "id,v\na,2\nb,1\nc,1\n"  # edit a, add c
    theirs = "id,v\na,1\nb,3\nd,1\n"  # edit b, add d
    rc, out = _run(KEYCSV, tmp_path, base, ours, theirs)
    assert rc == 0
    assert out == "id,v\na,2\nb,3\nc,1\nd,1\n"


def test_keycsv_flags_same_row_edited_both_sides(tmp_path):
    rc, out = _run(KEYCSV, tmp_path, "id,v\na,1\n", "id,v\na,2\n", "id,v\na,3\n")
    assert rc == 1 and "a,2" in out


def test_keycsv_keeps_multiline_fields(tmp_path):
    base = 'id,q\na,"x\ny"\n'
    ours = 'id,q\na,"x\ny"\nb,z\n'
    rc, out = _run(KEYCSV, tmp_path, base, ours, base)
    assert rc == 0 and '"x\ny"' in out and "b,z" in out


def test_jsonunion_keeps_both_sides(tmp_path):
    base = json.dumps({"k1": {"s": "open"}})
    ours = json.dumps({"k1": {"s": "open"}, "k2": {"s": "open"}})
    theirs = json.dumps({"k1": {"s": "resolved"}, "k3": {"s": "open"}})
    rc, out = _run(JSONU, tmp_path, base, ours, theirs)
    d = json.loads(out)
    assert rc == 0 and d == {
        "k1": {"s": "resolved"},
        "k2": {"s": "open"},
        "k3": {"s": "open"},
    }


def test_keycsv_driver_in_a_real_merge(tmp_path):
    if not shutil.which("git"):
        return

    def g(*a):
        subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True)

    g("init", "-q", "-b", "main")
    g("config", "user.email", "t@t")
    g("config", "user.name", "t")
    g("config", "merge.keycsv.driver", f"{sys.executable} {KEYCSV} %O %A %B %P")
    (tmp_path / ".gitattributes").write_text("reg.csv merge=keycsv\n")
    (tmp_path / "reg.csv").write_text("id,v\na,1\n")
    g("add", ".")
    g("commit", "-qm", "base")
    g("checkout", "-qb", "feature")
    (tmp_path / "reg.csv").write_text("id,v\na,1\nb,1\n")
    g("commit", "-qam", "add b")
    g("checkout", "-q", "main")
    (tmp_path / "reg.csv").write_text("id,v\na,1\nc,1\n")
    g("commit", "-qam", "add c")
    g("checkout", "-q", "feature")
    g("merge", "-q", "--no-edit", "main")
    assert (tmp_path / "reg.csv").read_text() == "id,v\na,1\nb,1\nc,1\n"
