"use strict";
// Independent oracle: instrument the pinned higher-order source, not machine.cjs.
// Both implementations still share the host JavaScript runtime.
function campaign(M,contract,reference) {
  const b=new M.Budget(contract.bounds), evidence={schema:"adva.external.zot-prefix-machine.evidence.v0",contract:contract.schema,attempt:contract.attempt,verdict:"Running",modes:{},checks:[],failures:[]};
  const check=(condition,label)=>{b.check();if(!condition)throw Error(label);evidence.checks.push(label);};
  const clone=x=>JSON.parse(JSON.stringify(x));
  let localEntries=0;
  const entry=()=>{b.entry();if(++localEntries>contract.bounds.oracleEntriesPerProgram)throw new M.Limit("oracle-local-fuel");};
  try {
    let body=reference.replace(/^import .*?;\s*$/m,"").split("const progFile =")[0];
    let instrumented=0;
    body=body.replace(/function\s+[A-Za-z0-9_]+\s*\([^)]*\)\s*\{/g,m=>{instrumented++;return m+" entry();";});
    body=body.replace("return output.join('');","return output;");
    const oracle=Function("entry",body+[
      "return function(word){",
      "try {",
      'const items=run(word).map(v=>typeof v==="string"?v:"<non-bit>");',
      'return {status:items.some(v=>v!=="0"&&v!=="1")?"RejectedNonBitOutput":"Accepted",items};',
      "} catch(e) {",
      'if(e instanceof TypeError) return {status:"RejectedTypeError",items:output.map(v=>typeof v==="string"?v:"<non-bit>")};',
      'return {status:"Unknown",reason:e.message};',
      "}};"
    ].join("\n"))(entry);
    check(instrumented===19,"pinned oracle has 19 function-entry fuel sites");
    const words=[];for(let n=0;n<=contract.bounds.maxPayloadLength;n++)for(let x=0;x<2**n;x++)words.push(n?x.toString(2).padStart(n,"0"):"");
    const referenceRows=words.map(word=>{b.check();localEntries=0;return {word,...oracle(word)};});
    evidence.referenceRows=referenceRows;
    check(referenceRows.every(r=>r.status!=="Unknown"),"all pinned-source oracle calls completed without resource ambiguity");
    const runners={};
    for(const mode of ["direct","prefix","state"]) {
      const runner=new M.Runner(b,mode);runners[mode]=runner;const steps=b.steps,start=Date.now();
      const rows=words.map(w=>{b.check();return runner.run(w);});
      evidence.modes[mode]={actualTransitions:b.steps-steps,elapsedMs:Date.now()-start,hits:runner.hits,misses:runner.misses,cacheEntries:runner.cache.size,arenaNodes:runner.a.nodes.length,rows};
    }
    const expected=evidence.modes.direct.rows;
    for(const mode of ["prefix","state"])check(JSON.stringify(evidence.modes[mode].rows)===JSON.stringify(expected),mode+" ledger, output and debited cost equal direct");
    function validate(rows) {
      if(rows.length!==words.length)throw Error("row coverage");
      for(let i=0;i<rows.length;i++) {
        b.check();const r=rows[i],o=referenceRows[i];
        if(r.word!==words[i]||M.unframe(r.code)!==r.word||r.weightExponent!==2*r.word.length+1)throw Error("frame or mass");
        if(r.status!==o.status||JSON.stringify(r.items)!==JSON.stringify(o.items))throw Error("oracle disagreement");
        if(r.cost!==expected[i].cost)throw Error("debited cost"); // Direct CEK comparator, not an independent cost semantics.
      }
      return true;
    }
    check(validate(expected),"every full-budget row agrees with independently instrumented Zot output/failure oracle");
    const codes=expected.map(r=>r.code).sort();
    check(codes.every((c,i)=>!i||!c.startsWith(codes[i-1])),"all finite framed codes form an antichain");
    const denominator=2**(2*contract.bounds.maxPayloadLength+1),tail=2**contract.bounds.maxPayloadLength;
    const mass=expected.reduce((s,r)=>s+2**(2*contract.bounds.maxPayloadLength+1-r.weightExponent),0);
    check(mass+tail===denominator,"exact Kraft mass plus unevaluated length tail equals one");
    evidence.probability={denominator,lengthTailNumerator:tail,cuts:[]};
    for(const t of contract.bounds.timeCuts) {
      const direct=words.map(w=>{b.check();return runners.direct.run(w,t);});
      for(const mode of ["prefix","state"]) {
        const rows=words.map(w=>{b.check();return runners[mode].run(w,t);});
        check(JSON.stringify(rows)===JSON.stringify(direct),mode+" warm-cache debit agrees at t="+t);
      }
      let lower=0,rejected=0,unknown=0;const counts={};
      for(const r of direct) {
        const weight=2**(2*contract.bounds.maxPayloadLength+1-r.weightExponent);
        counts[r.status]=(counts[r.status]||0)+1;
        if(r.status==="Accepted")lower+=weight;else if(r.status==="Unknown")unknown+=weight;else rejected+=weight;
      }
      check(lower+rejected+unknown+tail===denominator,"probability partition at t="+t);
      evidence.probability.cuts.push({t,counts,lowerNumerator:lower,upperNumerator:lower+unknown+tail,unknownNumerator:unknown,rejectedNumerator:rejected});
    }
    const row=w=>expected[words.indexOf(w)];
    check(row("0").status==="Accepted"&&row("00").status==="Accepted","raw Zot host-return prefix collision 0 / 00 retained");
    check(JSON.stringify(row("01000").items)==='["1"]'&&JSON.stringify(row("10000").items)==='[]',"adjacent-bit swap 01000 / 10000 changes output");
    evidence.counterexamples={rawPrefix:["0","00"],unsafeSwap:[row("01000"),row("10000")]};
    const a=runners.state.a,x=a.intern("K1",a.Bit0),y=a.intern("K1",a.Bit1);
    check(x!==y&&a.nodes[x][0]===a.nodes[y][0],"closure tag alone loses captured bit");
    const r0=M.advance(a,M.start(M.A(M.V(x),M.V(a.I))),64),r1=M.advance(a,M.start(M.A(M.V(y),M.V(a.I))),64);
    check(r0.value===a.Bit0&&r1.value===a.Bit1,"capture-erasing cache key would change result");
    const full=M.advance(a,M.start(M.A(M.V(a.Pr),M.V(a.K))),256);
    const partial=M.advance(a,M.start(M.A(M.V(a.Pr),M.V(a.K))),12);
    check(partial.status==="Running","checkpoint interrupts an active CEK stack");
    const checkpoint=clone({nodes:a.snapshot(),state:partial});
    const restored=M.Arena.restore(checkpoint.nodes,b);
    M.advance(restored,checkpoint.state,256-12);
    check(JSON.stringify(checkpoint.state)===JSON.stringify(full),"serialized continuation preserves output, residual and total steps");
    evidence.checkpoint={atStep:12,state:partial,nodes:checkpoint.nodes};
    function rejects(mut,label){const rows=clone(expected);mut(rows);let rejected=false;try{validate(rows);}catch(e){rejected=true;}check(rejected,label);}
    rejects(rows=>rows.pop(),"missing source-code mass rejected");
    rejects(rows=>{rows[1].weightExponent++;},"representative-only or altered weight rejected");
    rejects(rows=>{rows[0].items=["1"];},"changed output rejected");
    rejects(rows=>{rows[0].cost--;},"free cached step rejected");
    for(const code of ["","1","10","1000","0x"]) {
      let refused=false;try{M.unframe(code);}catch(e){refused=true;}check(refused,"invalid frame refused: "+JSON.stringify(code));
    }
    const known=row("01000"),below=runners.state.run("01000",known.cost-1);
    check(below.status==="Unknown"&&below.cost===known.cost-1,"warm cache cannot turn just-below-cost Unknown into halt");
    evidence.verdict="Completed";
  } catch(e) {
    evidence.verdict=e instanceof M.Limit?"Unknown":"InvalidEvidence";
    evidence.failures.push({name:e.name,message:e.message});
  }
  evidence.costs={transitions:b.steps,oracleEntries:b.oracle,elapsedMs:Date.now()-b.start};
  // All retained data are ASCII. This bounds the serialized checkpoint, not OS RSS.
  const text=JSON.stringify(evidence);
  if(text.length>contract.bounds.maxRetainedAsciiBytes){evidence.verdict="Unknown";evidence.failures.push({message:"retained-size"});delete evidence.referenceRows;for(const m of Object.values(evidence.modes))delete m.rows;}
  if(Date.now()-b.start>contract.bounds.maxElapsedMs){evidence.verdict="Unknown";evidence.failures.push({message:"elapsed-during-checkpoint"});}
  evidence.costs.throughCheckpointElapsedMs=Date.now()-b.start;
  return evidence;
}
if(typeof module!=="undefined") module.exports={campaign};
