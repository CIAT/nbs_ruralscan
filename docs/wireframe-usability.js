/* Presentation helpers only; no methodology or runtime data. */
window.WireframeUsability = (() => {
  'use strict';
  const esc = x => String(x).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function compactTable(headers, rows, label, id, expanded) {
    const table = subset => '<div class="table-scroll" tabindex="0" role="region" aria-label="'+esc(label)+'"><table><thead><tr>'+headers.map(x=>'<th scope="col">'+esc(x)+'</th>').join('')+'</tr></thead><tbody>'+subset.map(row=>'<tr>'+row.map(x=>'<td>'+esc(x)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';
    return '<p class="muted">'+esc(label)+'. Showing '+Math.min(5,rows.length)+' of '+rows.length+' units; full scope totals above are unchanged. On narrow screens, scroll the table sideways.</p>'+table(rows.slice(0,5))+(rows.length>5?'<details id="'+esc(id)+'"'+(expanded?' open':'')+'><summary>Show remaining '+(rows.length-5)+' units</summary>'+table(rows.slice(5))+'</details>':'');
  }
  function overlaps(scopes, names, nominalArea) {
    const keys=Object.keys(scopes), unique=new Map(), pairs=[];
    for(const cells of Object.values(scopes))for(const c of cells)unique.set(c.id,c);
    for(let i=0;i<keys.length;i++)for(let j=i+1;j<keys.length;j++){
      const a=keys[i],b=keys[j],ids=new Set(scopes[b].map(c=>c.id)),shared=scopes[a].filter(c=>ids.has(c.id));
      pairs.push([names[a]+' + '+names[b],shared.length*nominalArea,shared.reduce((sum,c)=>sum+c.people,0)]);
    }
    return {pairs,area:unique.size*nominalArea,residents:[...unique.values()].reduce((sum,c)=>sum+c.people,0)};
  }
  return Object.freeze({compactTable,overlaps});
})();
