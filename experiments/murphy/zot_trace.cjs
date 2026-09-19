"use strict";
// Authored by ChatGPT (OpenAI). Read-only tracer; no source modifications.
// Usage: node zot_trace_0001011011.cjs MACHINE_CJS REFERENCE_ZOT_JS OUTPUT_JSON
const fs = require('fs'), crypto = require('crypto'), vm = require('vm');
const [machinePath, referencePath, outPath] = process.argv.slice(2);
if (!outPath) throw Error('Expected MACHINE_CJS REFERENCE_ZOT_JS OUTPUT_JSON');
function blob(path) {
  const raw = fs.readFileSync(path);
  return crypto.createHash('sha1').update('blob ' + raw.length + '\0').update(raw).digest('hex');
}
const machineBlob = blob(machinePath), referenceBlob = blob(referencePath);
if (machineBlob !== 'c496b066ca33554575cd86fa0dcfd57630f91c88' ||
    referenceBlob !== '43fcf74c885fd3abc90a2c8e5f88e177952ecbcf') throw Error('Source blob mismatch');
const M = require(require('path').resolve(machinePath));
const limits = {maxTransitions:10000,maxElapsedMs:5000,maxArenaNodes:10000,maxStackFrames:1000,maxOutputItems:64};
const a = new M.Arena(new M.Budget(limits)), word='0001011011';
let value=a.Trivial, total=0, trace=[], phases=[];
const valueTree=id=>{const [t,...env]=a.nodes[id];return [t,...env.map(valueTree)];};
const showValue=id=>{const [t,...env]=a.nodes[id];return t+(env.length?'('+env.map(showValue).join(', ')+')':'');};
const showTerm=e=>e[0]==='v'?showValue(e[1]):e[0]==='a'?'('+showTerm(e[1])+' '+showTerm(e[2])+')':'emit('+showTerm(e[1])+')';
const showFrame=f=>f[0]==='arg'?'arg '+showTerm(f[1]):f[0]==='call'?'call '+showValue(f[1]):'emit';
const snapshot=s=>({control:showTerm(s.control),stack:s.stack.map(showFrame),status:s.status,output:s.output.map(showValue)});
let programTree;
for(let i=0;i<=word.length;i++) {
  const bit=i<word.length?word[i]:'finish', s=M.start(M.boundary(a,value,bit));
  const beforeValue=showValue(value), start=total+1, events={}, calls=[];
  while(s.status==='Running') {
    const before=snapshot(s);let kind;
    if(s.control[0]==='a')kind='push_arg';
    else if(s.control[0]==='emit')kind='prepare_emit';
    else if(s.stack.length===0)kind='done';
    else {
      const f=s.stack[s.stack.length-1];
      kind=f[0]==='arg'?'focus_arg':f[0]==='call'?'apply':'emit';
      if(kind==='apply')calls.push({step:total+1,tag:a.nodes[f[1]][0],fn:showValue(f[1]),arg:showValue(s.control[1])});
    }
    M.step(a,s);total++;events[kind]=(events[kind]||0)+1;
    trace.push({step:total,phase:i+1,bit,kind,before,after:snapshot(s)});
  }
  if(s.status!=='Done')throw Error('Incomplete trace: '+s.status);
  phases.push({phase:i+1,prefix:word.slice(0,i+1),bit,start,end:total,cost:s.steps,events,beforeValue,afterValue:showValue(s.value),calls});
  value=s.value;
  if(i===word.length-1)programTree=valueTree(value);
}
// Independent higher-order source oracle: account for prebuilt K^6 I separately.
let body=fs.readFileSync(referencePath,'utf8').replace(/^import .*?;\s*$/m,'').split('const progFile =')[0];
body=body.replace(/function\s+([A-Za-z0-9_]+)\s*\([^)]*\)\s*\{/g,(m,name)=>m+' audit('+JSON.stringify(name)+');');
const entries=[];let entryFuel=10000;
const ctx=vm.createContext({audit:name=>{if(--entryFuel<0)throw Error('Oracle fuel');entries.push(name);}});
vm.runInContext(body,ctx,{timeout:1000});
vm.runInContext('var stopForAudit=K(K(K(K(K(K(I))))));',ctx,{timeout:1000});
entries.length=0;
vm.runInContext('output=[]; var programForAudit=zot("0001011011"); var returnedForAudit=programForAudit(stopForAudit)(pr);',ctx,{timeout:1000});
const names={Zero:'zero',One:'one',Basis:'basis',Trivial:'trivial',Pr:'pr',BigLeft:'bigleft',Left:'left',BigRight:'bigright',Right:'right'};
const expected=phases.flatMap(p=>p.calls).map(c=>names[c.tag]||c.tag);
const actual=entries.filter(n=>!['zot','process'].includes(n));
if(JSON.stringify(actual)!==JSON.stringify(expected))throw Error('Independent application sequence mismatch');
if(vm.runInContext('output.length',ctx)!==0)throw Error('Unexpected output');
const rawRun=vm.runInContext('run("0001011011")',ctx,{timeout:1000});
if(rawRun!=='')throw Error('Original run disagreement');
const counts={};for(const t of trace)counts[t.kind]=(counts[t.kind]||0)+1;
if(total!==125 || counts.apply!==38 || counts.done!==11)throw Error('Count mismatch');
const result={schema:'zot.trace.0001011011.v1',word,runtime:process.version,machineBlob,referenceBlob,limits,total,counts,programTree,returnedTree:valueTree(value),phases,trace,
  checks:{originalRunOutput:rawRun,independentApplicationSequence:actual,applicationSequenceMatches:true},
  countingScope:'CEK transitions only; excludes text parsing, arena construction, K^6 I preconstruction, host recursion and frame construction.'};
fs.writeFileSync(outPath,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({total,counts,programTree,returnedTree:valueTree(value),checks:result.checks}));
