"""Read-only inventory of frozen high-priority stocktake; no source promotion."""
import csv, json, re, unicodedata, subprocess
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
LIB=Path('/Users/pstewarda/Library/CloudStorage/OneDrive-CGIAR/ClimateActionNetZero/1_Projects/D591_Rural-Scan_NBS')
def norm(s):
    return re.sub(r'[^a-z0-9]+','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
def read(p):
    with (ROOT/p).open() as f:return list(csv.DictReader(f))
src={r['source_id']:r for r in read('schema/registers/SRC_source_register.csv')}
ev=read('schema/registers/EV_evidence_register.csv')
queue={r['source_id']:r for r in read('pipeline/acquisition_queue.csv')}
files={norm(p.name):p for p in LIB.rglob('*.pdf')}
known={'Brandt':'brandt_2015','Castle':'castle_2025','Mendonça et al. - 2022':'mendonca_2022','Mendonça et al. - 2023':'mendonca_2023','Palma':'palma_2007','Mucida':'mucida_2023','Sperandio':'sperandio_2024','Busch':'bukoski_2024_ncc_cost_effectiveness','Strassburg':'strassburg_2020_global_priority_restoration'}
rows=[]
for r in read('reference/stocktake/peer_reviewed_benchmarked.csv'):
    if r['Final_Benchmark']!='High':continue
    if not any(x in r['NbS_Practice'].lower() for x in ['forest','mangrove','silvopastoral']):continue
    name=r['File']; sid=next((v for k,v in known.items() if name.startswith(k)),'')
    es=[e for e in ev if sid and e['source_id']==sid and e['review_state']!='dropped']
    path=files.get(norm(name))
    disposition='priority_identity_and_coverage_gap'
    if sid in src:disposition='registered_evidence_present_not_completeness_proof'
    elif sid in queue:disposition='acquired_priority_method_not_reconciled'
    if name.startswith('Alevizos'):disposition='out_of_scope_macroalgae_stocktake_misclassification'
    elif name.startswith(('Ceccarelli','Sahana','Hu et')):disposition='species_lane_priority_separate_from_practice'
    elif name.startswith('Schroth'):disposition='crop_lane_scope_check'
    elif name.startswith('Wang et al. - 2017'):disposition='conservation_roi_method_scope_check'
    rows.append({'stocktake_file':name,'reported_priority':r['Final_Benchmark'],'original_nbs_label':r['NbS_Practice'],'source_id':sid,'canonical_status':src.get(sid,{}).get('extraction_status',queue.get(sid,{}).get('status','no reconciled identity found')),'active_ev':len(es),'active_t4_ev':sum(e['use_role']=='structural_suitability' for e in es),'library_file':str(path.relative_to(LIB)) if path else '', 'disposition':disposition})
with (OUT/'priority_stocktake.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
summary={'baseline_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'scope':'High-labelled peer-reviewed stocktake rows under forest/agroforestry/agrosilvopastoral labels, plus explicit misclassifications retained. Priority labels inherited, not independently re-rated. Name matching locates files, not verified bibliographic identity.','count':len(rows),'files_located_by_normalized_filename':sum(bool(r['library_file']) for r in rows),'dispositions':dict(Counter(r['disposition'] for r in rows))}
(OUT/'inventory_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
