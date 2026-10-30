/* v1 cartographic presentation only. Uses existing geometry and fixture summaries. */
window.WireframeMaps = (() => {
  const NS='http://www.w3.org/2000/svg';
  const palettes={opp:['#edf4ef','#1d6b50'],fire:['#fff3e7','#b64d20'],flood:['#eaf2f8','#25688e'],both:['#f1ecf6','#70468c'],hot:['#fceee7','#9d412e']};
  function node(tag,attrs={},text){const el=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,v));if(text!==undefined)el.textContent=text;return el;}
  function color(p,t){const rgb=h=>h.match(/\w\w/g).map(x=>parseInt(x,16));const a=rgb(p[0].slice(1)),b=rgb(p[1].slice(1));return `rgb(${a.map((v,i)=>Math.round(v+(b[i]-v)*t)).join(',')})`;}
  function init(keys){keys.forEach(k=>{
    const svg=document.getElementById('map-'+k);
    svg.querySelector(':scope > rect').setAttribute('fill','#f0f5f7');
    svg.querySelector('.sle-grat').remove();
    svg.querySelector('.sle-cities').remove();
    svg.querySelector('.sle-north').remove();
    const scale=svg.querySelector('.sle-scale');scale.setAttribute('transform','translate(445,370)');
    const geography=node('g',{class:'map-geography'});
    ['.sle-adm2-fill','#cells-'+k,'.sle-adm2-border','.sle-adm0','.sle-labels'].forEach(selector=>geography.append(svg.querySelector(selector)));
    svg.insertBefore(geography,scale);
    geography.querySelectorAll('.sle-adm2-fill path').forEach((p,i)=>p.dataset.district=SLE_GEO.adm2[i].name);
    geography.querySelectorAll('.sle-adm2-lbl').forEach(label=>{
      const name=label.textContent;label.dataset.district=name;
      if(name.startsWith('Western Area')){label.setAttribute('x','28');label.setAttribute('y',name.endsWith('Urban')?'249':'271');label.setAttribute('text-anchor','start');label.textContent=name.replace('Western Area','Western');}
      else label.setAttribute('text-anchor','middle');
    });
    geography.querySelectorAll('.sle-leader').forEach(line=>line.setAttribute('x2','92'));
    svg.append(node('text',{x:24,y:29,class:'map-country'},'SIERRA LEONE'));
    svg.append(node('text',{x:24,y:44,class:'map-status'},'Illustrative data · not pilot results'));
    svg.append(node('text',{x:35,y:335,class:'map-ocean'},'Atlantic Ocean'));
    svg.append(node('text',{x:560,y:33,class:'map-north'},'↑ N'));
    const note=document.createElement('p');note.className='map-reading';note.id='map-reading-'+k;
    svg.before(note);svg.setAttribute('aria-describedby',note.id);
  });}
  function paint(k,{districts,shares,palette,title,denominator,empty=false,detail="Cell detail"}){
    const svg=document.getElementById('map-'+k),p=palettes[palette];
    svg.dataset.display=districts?'districts':'cells';
    document.getElementById('cells-'+k).style.display=districts?'none':'';
    svg.querySelectorAll('.sle-adm2-fill path').forEach(path=>{
      const g=shares?.get(path.dataset.district),value=g?.den&&!empty?g.num/g.den:null;
      path.style.fill=districts?(value===null?'#e4e8e5':color(p,value)):'#e4e8e5';
      path.querySelector('title')?.remove();
      if(districts)path.append(node('title',{},`${path.dataset.district}: ${value===null?'no result':(value*100).toFixed(1)+'%'} · ${denominator}`));
    });
    svg.querySelectorAll('.sle-adm2-lbl').forEach(label=>{
      label.querySelector('tspan')?.remove();
      if(districts){
        const g=shares?.get(label.dataset.district),value=g?.den&&!empty?g.num/g.den:null;
        label.append(node('tspan',{x:label.getAttribute('x'),dy:9,class:'map-share'},value===null?'—':(value*100).toFixed(0)+'%'));
      }
    });
    const note=document.getElementById('map-reading-'+k);
    note.textContent=districts?`${title} · district summary. Denominator: ${denominator}. Colour summarises each district; it does not locate sites within it.`:`${title} · ${detail}. Coarse authored patterns; square edges are display cells, not surveyed boundaries.`;
    if(districts){
      const legend=document.getElementById('legend-'+k);legend.replaceChildren();
      [0,.25,.5,.75,1].forEach(t=>{const item=document.createElement('span'),swatch=document.createElement('i');swatch.className='swatch';swatch.style.background=color(p,t);item.append(swatch,document.createTextNode((t*100)+'%'));legend.append(item);});
      const item=document.createElement('span'),swatch=document.createElement('i');swatch.className='swatch';swatch.style.background='#e4e8e5';item.append(swatch,document.createTextNode('No result / no denominator'));legend.append(item);
    }
    svg.querySelector('title').textContent=title+' — Sierra Leone, illustrative '+(districts?'district summary':'cell detail');
  }
  function zoom(k,direction){const group=document.querySelector('#map-'+k+' .map-geography');const previous=Number(group.dataset.zoom||1);const z=direction==='reset'?1:Math.max(1,Math.min(4,previous*(direction==='in'?1.35:1/1.35)));group.dataset.zoom=z;group.setAttribute('transform',`translate(${300*(1-z)},${200*(1-z)}) scale(${z})`);const ticks=document.querySelectorAll('#map-'+k+' .sle-scale text');ticks[1].textContent=(50/z).toFixed(z===1?0:1);ticks[2].textContent=(100/z).toFixed(z===1?0:1)+' km';}
  return {init,paint,zoom};
})();
