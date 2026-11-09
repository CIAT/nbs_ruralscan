# Replay of the shared runoff rainfall hold

The 9 November 2026 replay traced `water_harvesting__runoff_catchment__annual_precipitation` from the accepted decision to the six-practice release compiler. Both compilations used the same input tree and approved-only mode. [Original decision](../t4_water_block_20261109/rainfall_decision.md) · [Original run, source fingerprints and file checksums](../t4_water_block_20261109/rainfall_run.json)

| Compiler | SHA-256 of the complete rainfall mapping |
| --- | --- |
| Reviewed merge `624a23f03788b5e6adafb2fe0b564326ab527b28` | `e6a8e2d853eadbff1a7856691b7e49ef2a4b59b869bc2f97d73343adbfe2443a` |
| Release compiler `549940fd33f5bd2dcf5a79b48e1b08c1e2ee8b6d` | `4c5fff7527bdc392120e3b13840a45da137736a2d9c8f5f37559de28f54f8e89` |

The first hash matches both the recorded hash and the accepted row in the reviewed merge. Three CSV fields account for the entire difference in the second hash.

| Field | Reviewed merge | Release compiler |
| --- | --- | --- |
| `corpus_n` | `13` | Empty. Complete screened membership is unknown. |
| `paper_support_pct` | `34.0` | Empty. No verified denominator supports a percentage. |
| `justification` | Original decision text | Exact original text followed by one space and `Retained approved calibration hold; no new numeric synthesis or approval.` |

## Evidence and scope

All six file hashes in the original run matched the archived review tree. All four evidence fingerprints matched the original EV CSV records using `schema_tools.review_notes.evidence_fingerprint`. The source IDs, extraction rulesets and locators matched. The corresponding three cached PDFs and one HTML snapshot matched all four source hashes. The FAO snapshot was identified by its HTML content even though this cache used a `.pdf` filename. The retained profiles were checked at these locations.

| Profile | Source locator | Verified interpretation |
| --- | --- | --- |
| Kahinda et al. | PDF p. 3, §2.2.1.2 and Table 3, external-catchment column | For annual rainfall with 80% probability of exceedance, the printed 0–100, 100–200, 200–400, 400–600, 600–800, 800–1,000 and >1,000 mm bands have respective ranks 1, 2, 3, 4, 5, 3 and 1. Shared endpoint assignment is unspecified. |
| Ngugi et al. | PDF p. 9, Table 3, and p. 24, rainfall discussion | The ≥200 mm sand-dam guideline was tested. No dams were sampled in the 200–400 mm band. Two of 29 had water in the 400–600 mm band. |
| Critchley & Siegert | HTML chapter 5, §5.6.1–5.6.2, trapezoidal bund suitability | 250–500 mm in the described crop-production setting. |
| WOCAT | PDF p. 86, printed p. 73, “Water storage in soil” and bund diagram | 200–400 mm for large trapezoidal bunds. The layout cites Oweis et al., adapted from Critchley & Siegert. |

The bund ranges overlap at 250–400 mm. A site at 225 mm is covered only by WOCAT, a site at 300 mm by both, and a site at 450 mm only by Critchley & Siegert. The ranges are descriptive and independence of their estimates is unresolved. Both builds retain all four profiles with the numerical hold. The former 200 mm minimum, 600–800 mm optimum and 500 mm maximum remain archived in the hold.

## Reproduce both rows

In a CIAT checkout, activate the project Python environment. The pull request ref keeps the original compiler revision reachable from a fresh clone after a squash merge. Extract the two compiler revisions into separate directories. Supply the reviewed tree as the data source to both.

```sh
git fetch origin refs/pull/636/head
replay=$(mktemp -d)
mkdir "$replay/review" "$replay/release"
git archive 624a23f03788b5e6adafb2fe0b564326ab527b28 | tar -x -C "$replay/review"
git archive 549940fd33f5bd2dcf5a79b48e1b08c1e2ee8b6d | tar -x -C "$replay/release"
for compiler in review release; do
  PYTHONPATH="$replay/$compiler/src" python "$replay/$compiler/scripts/synthesise-recipe.py" \
    water_harvesting_conservation --source-root "$replay/review" --approved-only \
    --output-dir "$replay/output-$compiler"
done
python - "$replay" <<'PY'
import csv
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
run = json.loads((root / "review/methodology/audits/t4_water_block_20261109/rainfall_run.json").read_text())
for name, expected in run["replay"]["file_sha256"].items():
    assert hashlib.sha256((root / "review" / name).read_bytes()).hexdigest() == expected

def rainfall(directory):
    with (directory / "T4_suitability_mappings.csv").open(encoding="utf-8", newline="") as f:
        [row] = [r for r in csv.DictReader(f) if r["mapping_id"] == run["mapping_id"]]
    return row

old = rainfall(root / "output-review")
new = rainfall(root / "output-release")
assert old == rainfall(root / "review/schema/recipes/water_harvesting_conservation")
for row, expected in ((old, run["replay"]["accepted_mapping_sha256"]),
                      (new, "4c5fff7527bdc392120e3b13840a45da137736a2d9c8f5f37559de28f54f8e89")):
    encoded = json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    assert digest == expected
    print(digest)
for field in old:
    if old[field] != new[field]:
        print(field, repr(old[field]), "->", repr(new[field]))
PY
```
