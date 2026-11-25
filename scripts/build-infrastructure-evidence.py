#!/usr/bin/env python3
"""Export existing T3/T6 prose and provenance for the scoping review panel.

No synthesis, ratings or analytical rules are created here. CSV remains authoritative.
Run from repository root; --source-root can point at a newer evidence checkout.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--source-root', type=Path, default=ROOT)
args = p.parse_args()
source = args.source_root
inputs = {}


def read(relative):
    path = source / relative
    inputs[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open(newline='', encoding='utf-8-sig') as handle:
        return list(csv.DictReader(handle))


practices = {
    'agro_f1': ('agroforestry', 'agroforestry__planted_silvoarable', 'Planted silvoarable agroforestry'),
    'riparian': ('riparian_buffer', '', 'Riparian buffers'),
    'anr': ('forest_restoration', 'forest_restoration__assisted_regeneration', 'Assisted natural regeneration'),
}
records = []
fields = ['record_id', 'nbs_id', 'suitability_family_id', 'hazard_type', 'variable_id',
          'risk_role', 'mitigation_potential', 'mitigation_mechanism', 'confidence',
          'effect_direction', 'effect_confidence', 'effect_mechanism', 'caveats',
          'conditionality', 'timescale_of_effect', 'landscape_scale_only', 'applicability']
for nbs, family, label in practices.values():
    for table in ['T3_nbs_hazard_farming', 'T6_nbs_scorecard']:
        relative = f'schema/recipes/{nbs}/{table}.csv'
        for row in read(relative):
            if row.get('scope_type') or row.get('farming_system', 'all') != 'all':
                continue
            if row.get('suitability_family_id', '') not in ['', family]:
                continue
            if table.startswith('T3'):
                if row['hazard_type'] not in ['flood', 'fire', 'landslide'] or row['risk_role'] not in ['livelihood_mitigation', 'both']:
                    continue
            elif row['variable_id'] != 'soil_erosion_risk':
                continue
            item = {k: row.get(k, '') for k in fields}
            item.update(table=table[:2], csv_path=relative, evidence_ids=json.loads(row.get('evidence_ids') or '[]'))
            records.append(item)
ids = {eid for row in records for eid in row['evidence_ids']}
ev = {r['evidence_id']: {k:r.get(k,'') for k in ['evidence_id','source_id','quote','page','locator','review_state','reviewer_ok']} for r in read('schema/registers/EV_evidence_register.csv') if r['evidence_id'] in ids}
sids = {r['source_id'] for r in ev.values()}
src = {r['source_id']: {k:r.get(k,'') for k in ['citation','url','doi','study_country','spatial_scale']} for r in read('schema/registers/SRC_source_register.csv') if r['source_id'] in sids}
output = {'description':'Generated existing-evidence snapshot; not a Haiti assessment or infrastructure-protection estimate.',
          'practices':{k:dict(nbs=n,family=f,label=l) for k,(n,f,l) in practices.items()},
          'records':records,'evidence':ev,'sources':src,'input_sha256':inputs}
path=ROOT/'docs/redesign/infrastructure-evidence.json'
path.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
print(f'{len(records)} synthesis rows, {len(ev)} evidence units, {len(src)} sources → {path}')
