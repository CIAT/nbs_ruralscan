/* Read-only T3/T6 evidence companion. Exposure ranking never uses these ratings. */
(function () {
  'use strict';
  let data = null, failure = false;
  const mounts = Array.from(document.querySelectorAll('[data-infrastructure-evidence]'));
  if (!mounts.length) return;
  const escape = value => String(value || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const words = value => escape(value || 'Not reported').replace(/_/g, ' ');
  const hazardName = {flood:'River flood',landslide:'Landslide',fire:'Wildfire'};
  function hazard() {
    try {const saved=JSON.parse(localStorage.getItem('v2-2-infrastructure-exposure-priority'));if(saved && hazardName[saved.hazard])return saved.hazard;} catch (_) {}
    return 'flood';
  }
  function choose(practice, table, selectedHazard) {
    const candidates=data.records.filter(r=>r.nbs_id===practice.nbs && r.table===table && (table==='T6'||r.hazard_type===selectedHazard));
    return candidates.find(r=>r.suitability_family_id===practice.family) || candidates.find(r=>!r.suitability_family_id);
  }
  function prose(value, row) {
    return escape(value).replace(/\[(ev_[^\]]+)\]/g, (_, ids) => '['+ids.split(',').map(id=>{const index=row.evidence_ids.indexOf(id.trim());return index<0?'unmapped reference':index+1;}).join(', ')+']');
  }
  function provenance(row) {
    return '<details><summary>Sources, quoted evidence and review status ('+row.evidence_ids.length+(row.evidence_ids.length===1?' unit':' units')+')</summary><p>Record: '+escape(row.record_id)+' · '+escape(row.csv_path)+'</p><p>Evidence IDs identify units, not independent studies. Register review flags below do not establish approval of this synthesis or applicability to Haiti.</p><ul>'+row.evidence_ids.map(id=>{
      const ev=data.evidence[id];if(!ev)return '<li>'+escape(id)+' · Evidence unit missing from snapshot.</li>';
      const src=data.sources[ev.source_id]||{};
      const url=/^https?:\/\//.test(src.url||'')?src.url:'';
      return '<li><b>['+(row.evidence_ids.indexOf(id)+1)+'] '+escape(id)+'</b><p>'+(url?'<a href="'+escape(url)+'" target="_blank" rel="noopener">'+escape(src.citation||ev.source_id)+'</a>':escape(src.citation||ev.source_id))+'</p><p>Page / locator: '+escape(ev.page||ev.locator||'Not recorded')+' · Country: '+escape(src.study_country||'Not recorded')+' · Scale: '+escape(src.spatial_scale||'Not recorded')+'</p><p>Review state: '+escape(ev.review_state||'Not recorded')+'; reviewer OK: '+escape(ev.reviewer_ok||'Not recorded')+'</p><blockquote>'+escape(ev.quote)+'</blockquote></li>';
    }).join('')+'</ul></details>';
  }
  function record(row, practice, related) {
    if(!row)return '<p><b>No matching T3 mitigation row in this snapshot.</b> No mitigation conclusion can be drawn for this hazard. Absence of a row is not evidence of no effect.</p>';
    const wider=Boolean(practice.family && row.suitability_family_id!==practice.family);
    const scope=wider?'Wider NbS evidence only — not specific to this selected family.':practice.family?'Selected family evidence.':'NbS-level evidence across families.';
    const dropped=row.evidence_ids.some(id=>['dropped','quarantined'].includes((data.evidence[id]||{}).review_state));
    return '<section class="infra-record"><h4>'+ (related?'Related T6 evidence · Soil erosion':'T3 evidence · '+hazardName[row.hazard_type])+'</h4><p>'+scope+' Global synthesis; not a Haiti-specific or infrastructure-specific assessment.</p>'+
      '<p><b>'+ (related?'Effect direction: ':'Mitigation potential: ')+words(related?row.effect_direction:row.mitigation_potential)+'</b> · Confidence: '+words(related?row.effect_confidence:row.confidence)+'</p>'+
      (dropped?'<p><b>Review hold:</b> this row references dropped/quarantined evidence. Refresh synthesis before using its conclusion.</p>':'')+
      '<p><b>Mechanism and findings in existing synthesis</b></p><p>'+prose(related?row.effect_mechanism:row.mitigation_mechanism,row)+'</p>'+
      '<details><summary>Conditions, scale and limits</summary><p>'+prose(related?row.conditionality:row.caveats,row)+'</p><p>Timescale: '+words(row.timescale_of_effect)+' · Landscape-scale-only flag: '+words(row.landscape_scale_only)+'</p></details>'+
      provenance(row)+'</section>';
  }
  function render() {
    const selectedHazard=hazard();
    mounts.forEach(mount=>{
      if(!data){mount.innerHTML='<p>'+ (failure?'Evidence snapshot could not load. Mitigation evidence is unavailable; exposure scores alone do not imply protection.':'Loading existing T3/T6 evidence…')+'</p>';return;}
      const selected=V1BUI.state.practices||[];
      let cards=selected.map(id=>{
        const p=data.practices[id];if(!p)return '<p>No evidence mapping for '+escape(id)+'.</p>';
        const row=choose(p,'T3',selectedHazard), erosion=selectedHazard==='fire'?null:choose(p,'T6',selectedHazard);
        return '<article><h3>'+escape(p.label)+' · '+hazardName[selectedHazard]+'</h3>'+record(row,p,false)+
          (erosion?'<details><summary>Related soil-erosion mechanism — not proof of flood or landslide reduction</summary>'+record(erosion,p,true)+'</details>':'')+'</article>';
      }).join('');
      mount.innerHTML='<h3>Could this practice help—and how?</h3><p>Existing T3/T6 evidence for practices selected in the control bar. Unlike the fictional exposure figures, these are recorded synthesis findings with source evidence. Ratings describe their stated outcomes, not protection of roads or facilities.</p>'+
        cards+'<p><b>Connection to exposed assets remains unestablished.</b> Scoping can flag a candidate mechanism. Feasibility must establish the spatial pathway, event severity, design and scale before estimating protection, avoided damage or service continuity.</p>'+
        '<p><b>Ranking interpretation:</b> Section 5 weights exposed need only. Mitigation ratings are not multipliers and do not change those scores. A high exposure rank can coexist with missing, adverse or uncertain mitigation evidence.</p>'+
        (mount.dataset.infrastructureEvidence==='opportunity'?'<a href="05-hotspots.html?tab=2#service-priority">Compare exposure priority alongside this evidence in 5.2</a>':'<a href="03-opportunity.html?tab=5#infra-mechanism">Review hazard and evidence in 3.5</a>')+
        '<p class="sub"><a href="infrastructure-evidence.json">Download generated evidence snapshot</a> · CSV-derived review snapshot; not a live evidence service.</p>';
    });
  }
  V1BUI.onControls(render);
  window.addEventListener('infrastructure-exposure-change',render);
  window.addEventListener('storage',event=>{if(event.key==='v2-2-infrastructure-exposure-priority'||event.key===null)render();});
  window.addEventListener('pageshow',render);
  fetch('infrastructure-evidence.json').then(r=>{if(!r.ok)throw Error('Evidence unavailable');return r.json();}).then(value=>{data=value;render();}).catch(()=>{failure=true;render();});
})();
