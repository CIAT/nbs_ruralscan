/* Shared display classification for C.5 and Stage 03. Synthetic fixture only. */
(function () {
  'use strict';
  var variables = [
    {key:'poverty',label:'Rural poverty'}, {key:'food',label:'Food insecurity'},
    {key:'soil',label:'Soil degradation'}, {key:'biod',label:'Biodiversity loss'},
    {key:'carbon',label:'Carbon loss'}, {key:'water',label:'Water stress'},
    {key:'drought',label:'Drought hazard',hazard:true}, {key:'flood',label:'Flood hazard',hazard:true},
    {key:'erosion',label:'Soil erosion',hazard:true}, {key:'heat',label:'Heat stress',hazard:true}
  ];
  var storageKey = 'v2-variable-classification', settings = {};
  function valid(key, config) {
    return variables.some(function(v){return v.key === key;}) && config && [2,3,5].includes(config.count) &&
      ['quantile','threshold'].includes(config.method) && Array.isArray(config.cuts) &&
      (config.method === 'quantile' || (config.cuts.length === config.count-1 && config.cuts.every(function(x,i){
        return Number.isFinite(x) && x > 0 && x < 100 && (!i || x > config.cuts[i-1]);
      })));
  }
  function copy(x) {return JSON.parse(JSON.stringify(x));}
  function save() {try {localStorage.setItem(storageKey,JSON.stringify(settings));} catch(e) { /* session-only if storage unavailable */ }}
  function restore(input) {
    if(!input || typeof input!=='object' || Array.isArray(input) || Object.keys(input).some(function(key){return !valid(key,input[key]);}))return false;
    settings=copy(input);save();return true;
  }
  function refresh() {try {var stored=JSON.parse(localStorage.getItem(storageKey)||'{}'), next={};variables.forEach(function(v){if(stored && valid(v.key,stored[v.key]))next[v.key]=copy(stored[v.key]);});settings=next;} catch(e) { /* preserve session settings if storage unavailable */ }}
  refresh();
  function get(key) {return copy(settings[key] || {count:3,method:'quantile',cuts:[33.33,66.67]});}
  function set(key,config) {if(!valid(key,config))return false;refresh();settings[key]=copy(config);save();return true;}
  function build(key,state,override) {
    var config=override || get(key);
    if(!valid(key,config))return {error:'Enter ' + ((config && config.count || 3)-1) + ' strictly increasing cut points between 0 and 100.'};
    var meta=variables.find(function(v){return v.key===key;}), F=window.FIXTURE;
    var eligible=F.cells.filter(function(c){return !c.excluded && !c.unknown && Number.isFinite(c.ind[key]);});
    var raw=eligible.map(function(c){return c.ind[key];}), lo=Math.min.apply(null,raw), hi=Math.max.apply(null,raw);
    function value(c,period) {var x=meta.hazard && period==='ssp' ? c[key+'2050'] : c.ind[key];return 100*(x-lo)/(hi-lo || 1);}
    var selected=F.rollup(state).sel, sample=eligible.filter(selected);
    if(!sample.length)return {error:'No eligible cells in the selected opportunity space.'};
    var reference=eligible.filter(F.rollup(Object.assign({},state,{climate:'base'})).sel);
    if(!reference.length)return {error:'No baseline reference cells in the selected opportunity classes.'};
    var base=reference.map(function(c){return value(c,'base');}).sort(function(a,b){return a-b;});
    var cuts=config.method==='threshold' ? config.cuts.slice() : Array.from({length:config.count-1},function(_,i){return base[Math.min(base.length-1,Math.floor(base.length*(i+1)/config.count))];});
    var names=config.count===2 ? ['Low','High'] : config.count===3 ? ['Low','Medium','High'] : ['Very low','Low','Medium','High','Very high'];
    function classify(c,period) {var v=value(c,period),i=0;while(i<cuts.length && v>=cuts[i])i++;return i;}
    var values=sample.map(function(c){return value(c,state.climate);}), counts=Array(config.count).fill(0);
    sample.forEach(function(c){counts[classify(c,state.climate)]++;});
    var palette=['#e6eedc','#bbd3ac','#80ae81','#48835d','#205b41'];
    function rampIndex(i){return Math.round(i*4/(config.count-1));}
    return {error:'',names:names,cuts:cuts,count:config.count,method:config.method,sample:sample,counts:counts,values:values,
      colors:names.map(function(_,i){return palette[rampIndex(i)];}),value:value,classify:classify,
      high:function(c,period){return classify(c,period)>=(config.count===5 ? 3 : config.count-1);},
      mapKey:function(c,period){return 'lhq'+rampIndex(classify(c,period));},
      range:function(i){return i===0 ? '< '+cuts[0].toFixed(1) : i===cuts.length ? '≥ '+cuts[i-1].toFixed(1) : cuts[i-1].toFixed(1)+' to < '+cuts[i].toFixed(1);}
    };
  }
  window.V1BClassification={refresh:refresh,variables:variables,get:get,set:set,snapshot:function(){return copy(settings);},restore:restore,build:build};
})();
