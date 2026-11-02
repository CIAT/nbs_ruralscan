"""Validate the bounded handbook audit against hydrated local source artifacts."""

import hashlib
import json
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[3]
AUDIT = Path(__file__).resolve().parent
receipt = json.loads((AUDIT / "acquisition.json").read_text())
pdf = ROOT / receipt["cache"]
data = pdf.read_bytes()
assert hashlib.sha256(data).hexdigest() == receipt["sha256"]
assert (
    hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    == receipt["git_blob_sha1"]
)
doc = fitz.open(pdf)
claims = json.loads((AUDIT / "claims.json").read_text())
assert len(doc) == 18 and len(claims) == 12
for claim in claims:
    assert claim["quote"] in doc[claim["page"] - 1].get_text(), claim["id"]
bands = next(c["quote"] for c in claims if c["id"] == "species_bands")
for label in ["400-800 min/d:", "100-400 min/d:", "10-100 min/d:", "<10 min/d:"]:
    assert label in bands
code = (ROOT / ".cache/corpus/tool_mangrove_mini_buoy.txt").read_text()
for expression in ["ana1[7,2]<0.15", "ana1[1,2]<=(15)", "ana1[5,2]<100||ana1[5,2]>800"]:
    assert expression in code
probes = json.loads((AUDIT / "boundary_checks.json").read_text())
assert probes[0]["code"] == ("low" if probes[0]["value"] < 0.15 else "high")
assert probes[1]["code_warning"] == (probes[1]["value"] <= 15)
for probe in probes[2:]:
    assert probe["code_unsuitable"] == (probe["value"] < 100 or probe["value"] > 800)
print(
    "PASS: PDF identity; 12 native anchors; 4 species bands; code expressions and boundary probes."
)
