/* Illustrative arithmetic only; not the spatial runtime or a scientific rule source. */
(function(){
  'use strict';
  function score(values,weights,mask){
    if(!Array.isArray(values)||!Array.isArray(weights)||!weights.length||values.length!==weights.length||weights.some(function(w){return !Number.isFinite(w)||w<0;}))return {status:'invalid',message:'Enter finite nonnegative weights.'};
    var total=weights.reduce(function(a,b){return a+b;},0);
    if(!Number.isFinite(total)||total<=0)return {status:'invalid',message:'All-zero or non-finite weight total: no priority score.'};
    if(mask==='excluded')return {status:'excluded',message:'Outside opportunity space: excluded, not zero priority.'};
    if(mask!=='included')return {status:'unknown',message:'Opportunity mask unknown: priority remains unknown.'};
    if(values.some(function(v,i){return weights[i]>0 && (![0,0.33,0.66,1].includes(v));}))return {status:'unknown',message:'Positive-weight concern missing or invalid: priority remains unknown.'};
    var contributions=weights.map(function(w,i){return w===0?0:w/total*values[i];});
    return {status:'scored',denominator:total,contributions:contributions,score:contributions.reduce(function(a,b){return a+b;},0)};
  }
  window.V1BPriorityPreview={score:score};
})();
