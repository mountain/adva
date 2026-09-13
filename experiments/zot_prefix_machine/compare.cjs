"use strict";
function compareEvidence(left,right,contract) {
 const start=Date.now();let visited=0;
 function equal(a,b) {
  if(++visited>contract.bounds.maxVisitedValues||Date.now()-start>contract.bounds.maxElapsedMs)throw Error("comparison budget");
  if(a===b)return true;
  if(a===null||b===null||typeof a!=="object"||typeof b!=="object")return false;
  if(Array.isArray(a)!==Array.isArray(b))return false;
  const ka=Object.keys(a).sort(),kb=Object.keys(b).sort();
  if(ka.length!==kb.length||ka.some((k,i)=>k!==kb[i]))return false;
  return ka.every(k=>equal(a[k],b[k]));
 }
 function projection(e) {
  const modes={};
  for(const mode of ["direct","prefix","state"]){
   const m=e.modes[mode];modes[mode]={rows:m.rows,actualTransitions:m.actualTransitions,hits:m.hits,misses:m.misses,cacheEntries:m.cacheEntries,arenaNodes:m.arenaNodes};
  }
  return {modes,probability:e.probability};
 }
 const result={verdict:"Completed",checks:{}};
 try {
  result.checks.objectKeyOrderIgnored=equal({a:1,b:2},{b:2,a:1});
  result.checks.changedCostRefused=!equal({cost:1},{cost:2});
  result.checks.arrayOrderPreserved=!equal([{word:"0"},{word:"1"}],[{word:"1"},{word:"0"}]);
  result.checks.deterministicReplayEqual=equal(projection(left),projection(right));
  if(Object.values(result.checks).some(x=>!x))result.verdict="InvalidEvidence";
 }catch(e){result.verdict="Unknown";result.error=e.message;}
 result.costs={visitedValues:visited,elapsedMs:Date.now()-start};
 return result;
}
if(typeof module!=="undefined")module.exports={compareEvidence};
