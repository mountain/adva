"use strict";
// External research machine by ChatGPT (OpenAI). No native Adva identities.
// Closure tags mirror mountain/zot at the commit pinned in contract.json.
const V = x => ["v", x], A = (f,x) => ["a", f, x];
class Limit extends Error {}
class Budget {
  constructor(b) { this.b=b; this.start=Date.now(); this.steps=0; this.oracle=0; }
  check() { if(Date.now()-this.start>this.b.maxElapsedMs) throw new Limit("elapsed"); }
  tick() { this.check(); if(++this.steps>this.b.maxTransitions) throw new Limit("transitions"); }
  entry() { this.check(); if(++this.oracle>this.b.maxOracleEntries) throw new Limit("oracle-entries"); }
}
class Arena {
  constructor(budget) {
    this.budget=budget; this.nodes=[]; this.index=new Map();
    for(const t of ["I","K","S","Zero","One","Basis","Trivial","Pr","Bit0","Bit1"]) this[t]=this.intern(t);
    this.stop=this.I; for(let i=0;i<6;i++) this.stop=this.intern("K1",this.stop);
  }
  intern(tag,...env) {
    const key=JSON.stringify([tag,...env]);
    if(this.index.has(key)) return this.index.get(key);
    if(this.nodes.length>=this.budget.b.maxArenaNodes) throw new Limit("arena");
    const id=this.nodes.length; this.nodes.push(Object.freeze([tag,...env])); this.index.set(key,id); return id;
  }
  // Trusted local checkpoint only; this is NOT an untrusted import boundary.
  snapshot() { return this.nodes.map(n=>n.slice()); }
  static restore(nodes,budget) {
    if(nodes.length>budget.b.maxArenaNodes) throw new Limit("arena");
    const a=new Arena(budget);
    for(let i=0;i<nodes.length;i++) {
      const [tag,...env]=nodes[i];
      if(env.some(x=>!Number.isInteger(x)||x<0||x>=i)) throw Error("bad checkpoint edge");
      if(a.intern(tag,...env)!==i) throw Error("noncanonical checkpoint");
    }
    return a;
  }
}
function apply(a,f,x) {
  const [t,u,v]=a.nodes[f], val=(t,...e)=>V(a.intern(t,...e));
  switch(t) {
    case "I": return V(x);
    case "K": return val("K1",x);
    case "K1": return V(u);
    case "S": return val("S1",x);
    case "S1": return val("S2",u,x);
    case "S2": return A(A(V(u),V(x)),A(V(v),V(x)));
    case "Zero": return A(V(x),V(a.Basis));
    case "Basis": return A(A(V(x),V(a.S)),V(a.K));
    case "One": return val("BigLeft",x);
    case "BigLeft": return A(V(x),val("Left",u));
    case "Left": return val("BigRight",u,x);
    case "BigRight": return A(V(x),val("Right",u,v));
    case "Right": return A(V(u),A(V(v),V(x)));
    case "Trivial": return A(V(x),V(a.I));
    case "Pr": {
      let e=V(x); for(const z of [a.I,a.I,a.I,a.K,a.Bit0,a.Bit1]) e=A(e,V(z));
      return ["emit",e];
    }
    case "Bit0": case "Bit1": return null;
    default: throw Error("unknown closure tag: "+t);
  }
}
function start(term) { return {control:term,stack:[],output:[],steps:0,status:"Running"}; }
function step(a,s) {
  if(s.status!=="Running") return;
  a.budget.tick(); s.steps++;
  const c=s.control;
  if(c[0]==="a") { s.stack.push(["arg",c[2]]); s.control=c[1]; }
  else if(c[0]==="emit") { s.stack.push(["emit"]); s.control=c[1]; }
  else if(c[0]==="v") {
    if(s.stack.length===0) { s.status="Done"; s.value=c[1]; }
    else {
      const f=s.stack.pop();
      if(f[0]==="arg") { s.stack.push(["call",c[1]]); s.control=f[1]; }
      else if(f[0]==="call") {
        s.control=apply(a,f[1],c[1]);
        if(s.control===null) s.status="RejectedTypeError";
      } else {
        if(s.output.length>=a.budget.b.maxOutputItems) {s.status="Unknown";s.reason="output";return;}
        s.output.push(c[1]); s.control=V(a.Pr);
      }
    }
  } else throw Error("unknown term tag");
  if(s.stack.length>a.budget.b.maxStackFrames) {s.status="Unknown";s.reason="stack";}
}
function advance(a,s,fuel) {
  if(!Number.isInteger(fuel)||fuel<0) throw Error("invalid fuel");
  for(let i=0;i<fuel&&s.status==="Running";i++) step(a,s);
  return s;
}
function frame(w) { if(!/^[01]*$/.test(w)) throw Error("nonbinary"); return "1".repeat(w.length)+"0"+w; }
function unframe(code) {
  if(!/^[01]*$/.test(code)) throw Error("nonbinary");
  const n=code.indexOf("0");
  if(n<0||code.length!==2*n+1) throw Error("invalid frame");
  return code.slice(n+1);
}
function boundary(a,v,bit) {
  return bit==="finish"?A(A(V(v),V(a.stop)),V(a.Pr)):A(V(v),V(bit==="0"?a.Zero:a.One));
}
class Runner {
  constructor(budget,mode) {
    if(!["direct","prefix","state"].includes(mode)) throw Error("mode");
    this.a=new Arena(budget); this.mode=mode; this.cache=new Map(); this.hits=0; this.misses=0;
  }
  macro(v,bit,prefix,fuel) {
    const key=this.mode==="prefix"?JSON.stringify([prefix,bit]):JSON.stringify([v,bit]);
    const old=this.mode==="direct"?null:this.cache.get(key);
    if(old&&old.steps<=fuel) {this.hits++;return old;}
    this.misses++;
    const s=advance(this.a,start(boundary(this.a,v,bit)),fuel);
    if(s.status==="Running") {s.status="Unknown";s.reason="fuel";}
    if(this.mode!=="direct"&&s.status!=="Unknown") {
      if(!this.cache.has(key)&&this.cache.size>=this.a.budget.b.maxCacheEntries) throw new Limit("cache");
      this.cache.set(key,s);
    }
    return s;
  }
  run(w,fuel=this.a.budget.b.perProgramSteps) {
    if(w.length>this.a.budget.b.maxPayloadLength) throw Error("payload cap");
    const code=frame(w); let value=this.a.Trivial, cost=0, output=[],status="Running",reason;
    for(let i=0;i<=w.length;i++) {
      const s=this.macro(value,i<w.length?w[i]:"finish",w.slice(0,i),fuel-cost);
      cost+=s.steps; output.push(...s.output);
      if(s.status!=="Done") {status=s.status;reason=s.reason;break;}
      value=s.value;
      if(i===w.length) status="Returned";
    }
    const items=output.map(id=>this.a.nodes[id][0]==="Bit0"?"0":this.a.nodes[id][0]==="Bit1"?"1":"<non-bit>");
    if(status==="Returned") status=items.includes("<non-bit>")?"RejectedNonBitOutput":"Accepted";
    return {word:w,code,weightExponent:code.length,status,items,cost,...(reason?{reason}:{})};
  }
}
const ZotPrefixMachine={Limit,Budget,Arena,Runner,V,A,start,step,advance,boundary,frame,unframe};
if(typeof module!=="undefined") module.exports=ZotPrefixMachine;
