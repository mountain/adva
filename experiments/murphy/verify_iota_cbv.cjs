"use strict";
// Independent direct call-by-value Iota evaluator; authored by ChatGPT (OpenAI).
// Usage: node verify_iota_cbv.cjs FILE.iota
const fs=require('fs');
const code=fs.readFileSync(process.argv[2],'utf8').trim();
let calls=0,pos=0,prints=0;
const tick=()=>{if(++calls>100000)throw Error('fuel exhausted');};
const I=x=>{tick();return x;};
const K=x=>{tick();return y=>{tick();return x;};};
const S=x=>{tick();return y=>{tick();return z=>{tick();return x(z)(y(z));};};};
const iota=f=>{tick();return f(S)(K);};
function read(){
  if(pos>=code.length)throw Error('truncated');
  const c=code[pos++];
  if(c==='i')return iota;
  if(c==='*'){const f=read(),x=read();return f(x);}
  throw Error('syntax');
}
const value=read(),constructionFunctionCalls=calls;
if(pos!==code.length)throw Error('unread suffix');
let stop=I;for(let i=0;i<6;i++)stop=K(stop);
const before=calls;
const result=value(stop)(()=>{prints++;return I;});
const wrapperFunctionCalls=calls-before;
const token=Object.freeze({token:'probe'});
let test=result;for(let i=0;i<4;i++)test=test(token);
const K4IProbe=test(token)===token;
if(prints!==0||!K4IProbe)throw Error('behavior mismatch');
console.log(JSON.stringify({interpreter:'independent direct call-by-value Iota evaluator',consumed:pos,constructionFunctionCalls,wrapperFunctionCalls,printerInvocations:prints,K4IProbe},null,2));
