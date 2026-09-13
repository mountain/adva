"use strict";
function keraiaBoundaryCampaign(contract) {
  const b=contract.bounds,start=Date.now();let operations=0;
  const e={schema:"adva.external.keraia-input-boundary.evidence.v0",verdict:"Running",checks:[],failures:[]};
  function tick(){if(++operations>b.maxOperations||Date.now()-start>b.maxElapsedMs)throw Error("Unknown: resource limit");}
  function check(c,s){tick();if(!c)throw Error(s);e.checks.push(s);}
  function linear(s){let slots=1;for(let i=0;i<s.length;i++){tick();slots+=s[i]==="1"?1:-1;if(slots===0)return i+1;}return null;}
  function recursive(s){
    let i=0;function tree(){tick();if(i===s.length)return false;const bit=s[i++];return bit==="0"||(tree()&&tree());}
    return tree()?i:null;
  }
  try {
    const exhaustive=[];let tested=0;
    for(let n=0;n<=b.maxExhaustiveLength;n++){
      let complete=0,incomplete=0,withData=0;
      for(let x=0;x<2**n;x++){
        const s=n?x.toString(2).padStart(n,"0"):"",p=linear(s),q=recursive(s);tested++;
        if(p!==q)throw Error("parser mismatch: "+s);
        if(p===null)incomplete++;else if(p===n)complete++;else withData++;
      }
      exhaustive.push({n,complete,incomplete,withData});
    }
    check(tested===2**(b.maxExhaustiveLength+1)-1,"all declared binary inputs independently parsed");
    e.exhaustive=exhaustive;e.testedInputs=tested;
    function choose(n,k){let v=1n;for(let j=1;j<=k;j++){tick();v=v*BigInt(n-k+j)/BigInt(j);}return v;}
    let live=new Map([[1,1n]]),states=1,totalCompleteScaled=0n;const tails=[];
    for(let n=1;n<=b.maxDPDepth;n++){
      const next=new Map();let terminal=0n;
      for(const [s,count] of live){
        tick();
        if(s===1)terminal+=count;else next.set(s-1,(next.get(s-1)||0n)+count);
        next.set(s+1,(next.get(s+1)||0n)+count);
      }
      if(next.size>b.maxLiveDPStates)throw Error("Unknown: DP state cap");
      totalCompleteScaled=totalCompleteScaled*2n+terminal;
      let residual=0n;for(const count of next.values())residual+=count;
      check(totalCompleteScaled+residual===2n**BigInt(n),"tree mass conservation at depth "+n);
      const catalan=n%2?choose(n-1,(n-1)/2)/BigInt((n+1)/2):0n;
      check(terminal===catalan,"DP agrees with independent Catalan formula at depth "+n);
      if(n<=b.maxExhaustiveLength)check(terminal===BigInt(exhaustive[n].complete)&&residual===BigInt(exhaustive[n].incomplete),"DP agrees with exhaustive syntax at depth "+n);
      if(n%2)tails.push({depth:n,completedTrees:terminal.toString(),unresolvedNumerator:residual.toString(),denominator:(2n**BigInt(n)).toString(),frontierStates:next.size});
      states+=next.size;live=next;
    }
    e.syntaxTails=tails;e.visitedDPStates=states;
    const example="111010010100110001",end=linear(example);
    check(end===17&&example.slice(end)==="1","paper prefix-Keraia example splits into 17 program bits and 1 data bit");
    e.paperSplit={code:example,program:example.slice(0,end),input:example.slice(end)};
    function reads(labels,input){
      let cursor=0;const outputs={};
      for(const label of labels){tick();if(cursor===input.length)return {status:"NeedInput",cursor,outputs};outputs[label]=input[cursor++];}
      return {status:cursor===input.length?"Halt":"Overflow",cursor,outputs};
    }
    const short=reads(["A","B"],"0"),extended=reads(["A","B"],"01"),swapped=reads(["B","A"],"01"),overflow=reads(["A","B"],"010");
    check(short.status==="NeedInput"&&extended.status==="Halt","underflow prefix is extendable; pruning its entire subtree loses halting inputs");
    check(extended.outputs.A==="0"&&swapped.outputs.A==="1","swapping labeled reads changes behavior on a fixed input");
    check(overflow.status==="Overflow"&&overflow.cursor===2,"unread suffix is checked at halt, not by tree parser");
    e.readControls={short,extended,swapped,overflow};
    e.verdict="Completed";
  }catch(err){e.verdict=err.message.startsWith("Unknown:")?"Unknown":"InvalidEvidence";e.failures.push(err.message);}
  e.costs={operations,elapsedMs:Date.now()-start};
  if(JSON.stringify(e).length>b.maxRetainedAsciiBytes||Date.now()-start>b.maxElapsedMs){e.verdict="Unknown";e.failures.push("checkpoint limit");}
  return e;
}
if(typeof module!=="undefined") module.exports={keraiaBoundaryCampaign};
