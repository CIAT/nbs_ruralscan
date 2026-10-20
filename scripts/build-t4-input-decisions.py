#!/usr/bin/env python3
"""Render proposed input decisions; never modify analytical schema or approvals."""
import csv
import html
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'pipeline/t4_audit/agroforestry/final_audit/executable_categories/input_decision_cards.csv'
VERSION = '2026-10-20-v1'


def rows(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def esc(value):
    return html.escape(str(value), quote=True)


def main():
    cards = rows(DATA)
    evidence = {r['evidence_id']: r for r in rows(ROOT / 'schema/registers/EV_evidence_register.csv')}
    sources = {r['source_id']: r for r in rows(ROOT / 'schema/registers/SRC_source_register.csv')}
    sections = []
    for card in cards:
        cid = card['decision_id']
        parts = [f'<section id="{esc(cid)}"><h2>{esc(cid)} · {esc(card["title"])}</h2>',
                 f'<p class="meta">{esc(card["family"])} · {esc(card["mask"])}</p>']
        for key, label in [('current_behaviour', 'Current behaviour'), ('definition', 'What this input means')]:
            parts.append(f'<h3>{label}</h3><p>{esc(card[key])}</p>')
        parts.append('<details><summary>Source evidence and limits</summary>')
        for eid in json.loads(card['evidence_ids']):
            ev = evidence[eid]
            src = sources[ev['source_id']]
            url = src['url']
            if src['library_path']:
                url = 'https://cgiar.sharepoint.com/sites/Alliance-ClimateActionNetZero/Shared%20Documents/ClimateActionNetZero/1_Projects/' + '/'.join(quote(p) for p in src['library_path'].split('/'))
                if ev['page']:
                    url += '#page=' + quote(ev['page'])
            citation = esc(src['citation'])
            if url:
                citation = f'<a href="{esc(url)}" target="_blank" rel="noopener">{citation}</a>'
            parts.append(f'<p>{citation} · page {esc(ev["page"])}<br><code>{esc(eid)}</code></p><blockquote>{esc(ev["quote"])}</blockquote>')
        parts.append(f'<p class="notice">Evidence limit: {esc(card["evidence_limit"])}</p></details><h3>Dataset options</h3><ul>')
        for label, url, note in json.loads(card['datasets']):
            name = f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(label)}</a>' if url else esc(label)
            parts.append(f'<li><strong>{name}</strong> — {esc(note)}</li>')
        parts.append('</ul>')
        for key, label in [('recommended_action', 'Recommendation — not applied'), ('proposed_rule', 'Proposed rule'), ('fallback', 'Missing-data fallback'), ('implementation_owner', 'Who does the work'), ('user_information', 'Information needed from you')]:
            parts.append(f'<h3>{label}</h3><p>{esc(card[key])}</p>')
        options = ''.join(f'<option value="{esc(a)}">{esc(a)}</option>' for a in json.loads(card['answer_options']))
        parts.append(f'<div class="decision"><h3>Decision</h3><p>{esc(card["exact_question"])}</p><label for="answer-{cid}">Your choice</label><select id="answer-{cid}" data-id="{cid}"><option value="">Not answered</option>{options}</select><label for="notes-{cid}">Notes / alternative / dataset details</label><textarea id="notes-{cid}" rows="3"></textarea></div></section>')
        sections.append(''.join(parts))
    nav = ' · '.join(f'<a href="#{esc(c["decision_id"])}">{esc(c["decision_id"])}</a>' for c in cards)
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>T4 input decisions</title><style>
body{font:16px/1.55 system-ui;background:#f3f6f4;color:#193b33;max-width:1000px;margin:auto;padding:24px}h1{line-height:1.2}h2{font-size:24px}h3{font-size:16px;margin-bottom:4px}p{margin-top:4px}section{background:white;border:1px solid #c9d8d0;border-radius:10px;padding:26px;margin:24px 0;scroll-margin-top:15px}.meta{color:#536b62}a{color:#006953}blockquote{white-space:pre-wrap;border-left:3px solid #93b6a5;padding-left:16px;margin-left:0}code{overflow-wrap:anywhere;font-size:12px}.notice{background:#fff0d7;padding:14px}.decision{background:#eaf3ee;padding:18px;margin-top:18px}label{display:block;font-weight:600;margin-top:12px}input,select,textarea,button{font:inherit;padding:10px;box-sizing:border-box}select,textarea{width:100%}button{cursor:pointer;margin:12px 8px 0 0}summary{cursor:pointer;font-weight:600}li{margin:10px 0}.toolbar{border:1px solid #b6cfc1;padding:18px;background:white}#status{font-weight:600}@media(max-width:600px){body{padding:12px}section{padding:16px}}
</style></head><body><h1>Agroforestry T4: input decision cards</h1><p>Seven cards · proposal version 2026-10-20-v1</p><p class="notice"><strong>Proposals only.</strong> No live rules changed. Crop-host fallback already approved; C1 only asks about optional refinement. Choices stay in this browser. Export CSV and return it for application; export itself does not apply decisions.</p><p><a href="t4-categorical-tables.html">Current categorical tables</a></p>'''
    page += f'<nav>{nav}</nav><div class="toolbar"><label for="reviewer">Reviewer</label><input id="reviewer" placeholder="Your name"><br><button id="export">Export decisions CSV</button><button id="clear">Clear saved draft</button><p id="status" aria-live="polite"></p></div>' + ''.join(sections)
    page += '<script>const version=' + json.dumps(VERSION) + ';const ids=' + json.dumps([c['decision_id'] for c in cards]) + ';'
    page += '''
const key='t4-input-decisions-'+version;const byId=id=>document.getElementById(id);let storageOK=true;
function state(){return {reviewer:byId('reviewer').value,answers:Object.fromEntries(ids.map(id=>[id,{answer:byId('answer-'+id).value,notes:byId('notes-'+id).value}]))};}
function status(){const n=ids.filter(id=>byId('answer-'+id).value).length;byId('status').textContent=n+' / '+ids.length+' answered. '+(storageOK?'Draft saved locally.':'Local storage unavailable; export before closing.');}
function save(){try{localStorage.setItem(key,JSON.stringify(state()));}catch(e){storageOK=false;}status();}
try{const old=JSON.parse(localStorage.getItem(key)||'null');if(old){byId('reviewer').value=old.reviewer||'';for(const id of ids){byId('answer-'+id).value=old.answers?.[id]?.answer||'';byId('notes-'+id).value=old.answers?.[id]?.notes||'';}}}catch(e){storageOK=false;}
document.querySelectorAll('input,select,textarea').forEach(el=>el.addEventListener('input',save));status();
function csvCell(value){return '"'+String(value).replaceAll('"','""')+'"';}
function exportText(s,date){const rows=[['decision_id','answer','notes','reviewer','date','proposal_version'],...ids.map(id=>[id,s.answers[id].answer,s.answers[id].notes,s.reviewer,date,version])];return rows.map(row=>row.map(csvCell).join(',')).join('\\r\\n')+'\\r\\n';}
byId('export').onclick=()=>{const s=state();if(!s.reviewer.trim()){byId('status').textContent='Enter reviewer name before export.';byId('reviewer').focus();return;}const date=new Date().toLocaleDateString('en-CA');const blob=new Blob([exportText(s,date)],{type:'text/csv;charset=utf-8'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='review_agroforestry-t4-input-decisions-oct20_'+s.reviewer.replace(/[^a-z0-9_-]/gi,'_')+'_'+date+'.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
byId('clear').onclick=()=>{if(!confirm('Clear this browser draft? Export first if you want to keep it.'))return;byId('reviewer').value='';for(const id of ids){byId('answer-'+id).value='';byId('notes-'+id).value='';}save();};
</script></body></html>'''
    dest = ROOT / 'docs/review/t4-input-decisions.html'
    dest.write_text(page, encoding='utf-8')
    print(f'Rendered {len(cards)} cards: {dest}')


if __name__ == '__main__':
    main()
