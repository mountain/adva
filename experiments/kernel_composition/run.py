#!/usr/bin/env python3
"""Original finite kernel producer and independent supervisor, Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy; not his review.
Only the frozen probability producer is imported, never the new receiver.
"""
import argparse
import copy
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
PROFILE="adva.research.kernel-composition.v0"
spec=importlib.util.spec_from_file_location("kernel_probability_producer",ROOT.parent/"probability_receipt/run.py")
producer=importlib.util.module_from_spec(spec);spec.loader.exec_module(producer)
put,rat=producer.put,producer.rat


def wire_matrix(m): return [list(map(rat,row)) for row in m]
def values(m): return [[F(*v) for v in row] for row in m]
def multiply(k,l): return [[sum(k[i][j]*l[j][z] for j in range(2)) for z in range(2)] for i in range(2)]


def fixture(name="primary",reuse=False):
    spaces=[{"id":("复用" if reuse else name)+":"+s,"labels":[s+"0",s+"1"]} for s in ("A","B","C")]
    k=[[F(1,2),F(1,2)],[F(1,3),F(2,3)]] if reuse else [[F(3,4),F(1,4)],[F(1,2),F(1,2)]]
    l=[[F(3,4),F(1,4)],[F(1,4),F(3,4)]] if reuse else [[F(2,3),F(1,3)],[F(1,4),F(3,4)]]
    p=[F(2,5),F(3,5)] if reuse else [F(1,3),F(2,3)]
    e={"question":"kernel-"+name,"source":spaces[0],"middle":spaces[1],"target":spaces[2],
       "prior":list(map(rat,p)),
       "first_kernel":{"source":copy.deepcopy(spaces[0]),"target":copy.deepcopy(spaces[1]),"direction":"target-given-source","rows":wire_matrix(k)},
       "second_kernel":{"source":copy.deepcopy(spaces[1]),"target":copy.deepcopy(spaces[2]),"direction":"target-given-source","rows":wire_matrix(l)},
       "second_prior":[rat(sum(p[i]*k[i][j] for i in range(2))) for j in range(2)],
       "assumption":"markov-extension","history":[name+":declared"],"steps":[name+":first",name+":second"]}
    return e


def refresh_middle(e):
    p=list(map(lambda v:F(*v),e["prior"]));k=values(e["first_kernel"]["rows"])
    e["second_prior"]=[rat(sum(p[i]*k[i][j] for i in range(2))) for j in range(2)]


def interface(e,tag,probability):
    a,b=(e["source"],e["middle"]) if tag=="AB" else (e["middle"],e["target"]) if tag=="BC" else (e["source"],e["target"])
    carrier=[json.dumps([a["id"],a["labels"][i],b["id"],b["labels"][j]],sort_keys=True,separators=(",",":"),ensure_ascii=False) for i in range(2) for j in range(2)]
    bc=tag=="BC"
    return {"question":e["question"]+"/"+tag,"carrier":carrier,"reference":[[1,4]]*4,
            "probability":list(map(rat,probability)),
            "observation":[a["labels"][0]]*2+[a["labels"][1]]*2 if bc else b["labels"]*2,
            "observable":{"name":"target-index" if bc else "source-index","unit":"index","values":list(map(rat,[0,1,0,1] if bc else [0,0,1,1]))},
            "history":e["history"]+e["steps"][:1 if tag=="AB" else 2],"scope":"complete-declared-finite-carrier"}


def produce(e):
    p=[F(*v) for v in e["prior"]];k,l=values(e["first_kernel"]["rows"]),values(e["second_kernel"]["rows"])
    q=[sum(p[i]*k[i][j] for i in range(2)) for j in range(2)];m=multiply(k,l)
    r=[sum(q[j]*l[j][z] for j in range(2)) for z in range(2)]
    tables={"AB":[p[i]*k[i][j] for i in range(2) for j in range(2)],
            "BC":[q[j]*l[j][z] for j in range(2) for z in range(2)],
            "AC":[p[i]*m[i][z] for i in range(2) for z in range(2)]}
    return {"profile":PROFILE,"request":copy.deepcopy(e),
            "interfaces":{tag:producer.produce(interface(e,tag,tab)) for tag,tab in tables.items()},
            "claims":{"middle_prior":list(map(rat,q)),"composed_kernel":wire_matrix(m),"target_prior":list(map(rat,r))}}


def mutations(e,good):
    rows=[]
    def add(name,x,checked): rows.append((name,x,checked))
    x=copy.deepcopy(good);x["claims"]["middle_prior"].reverse();add("wrong-middle-claim",x,3)
    x=copy.deepcopy(good);x["claims"]["composed_kernel"][0][0]=rat(F(*x["claims"]["composed_kernel"][0][0])+1);add("wrong-product-claim",x,3)
    x=copy.deepcopy(good);x["claims"]["target_prior"]=copy.deepcopy(e["prior"]);add("wrong-target-claim",x,3)
    for tag,mode in (("AB","changed-first-law"),("BC","changed-middle-law"),("BC","renamed-middle"),("AC","reversed-product"),("BC","erased-history")):
        ctx=copy.deepcopy(good["interfaces"][tag]["context"])
        if mode=="changed-first-law":ctx["probability"]=[[1,4]]*4
        elif mode=="changed-middle-law":
            q=[F(*v) for v in reversed(good["claims"]["middle_prior"])];l=values(e["second_kernel"]["rows"])
            ctx["probability"]=[rat(q[j]*l[j][z]) for j in range(2) for z in range(2)]
        elif mode=="renamed-middle":ctx["observation"]=["other-B0"]*2+["other-B1"]*2
        elif mode=="reversed-product":
            rev=multiply(values(e["second_kernel"]["rows"]),values(e["first_kernel"]["rows"]));p=[F(*v) for v in e["prior"]]
            ctx["probability"]=[rat(p[i]*rev[i][z]) for i in range(2) for z in range(2)]
        else:ctx["history"]=ctx["history"][:-1]
        x=copy.deepcopy(good);x["interfaces"][tag]=producer.produce(ctx);add(mode,x,3)
    x=copy.deepcopy(good);x["request"]["steps"][1]="changed-task";add("changed-request",x,0)
    x=copy.deepcopy(good);x["interfaces"]["AB"]["claims"]["density"].pop();add("missing-first-atom",x,0)
    return rows


def bad_contexts(primary):
    rows=[]
    for name in ("middle-type-mismatch","middle-prior-mismatch","wrong-direction","negative-entry","nonstochastic-row","boolean-entry","history-capacity","joint-denominator","unsupported-assumption"):
        e=copy.deepcopy(primary)
        if name=="middle-type-mismatch":e["second_kernel"]["source"]["id"]="other-middle"
        elif name=="middle-prior-mismatch":e["second_prior"].reverse()
        elif name=="wrong-direction":e["second_kernel"]["direction"]="source-given-target"
        elif name=="negative-entry":e["first_kernel"]["rows"][0]=[[-1,1],[2,1]]
        elif name=="nonstochastic-row":e["first_kernel"]["rows"][0]=[[1,1],[1,1]]
        elif name=="boolean-entry":e["first_kernel"]["rows"][0][0]=[True,1]
        elif name=="history-capacity":e["history"]=["one","two","three"]
        elif name=="joint-denominator":
            e["prior"]=[[1,61],[60,61]];e["first_kernel"]["rows"]=[[[1,61],[60,61]],[[1,61],[60,61]]];refresh_middle(e)
        else:e["assumption"]="inferred-from-adjacent-laws"
        rows.append((name,e))
    return rows


class Campaign:
    def __init__(self,out):
        self.out=out;self.started=time.perf_counter();self.rows=[];self.assertions=0;self.work=0;self.scalar_terms=0
        self.phases={"construction_seconds":0.,"serialization_seconds":0.,"receiving_seconds":0.,"independent_observation_seconds":0.}
    def check(self,c,message):
        self.assertions+=1
        if not c:raise AssertionError(message)
    def save(self,path,v):
        t=time.perf_counter();put(path,v);self.phases["serialization_seconds"]+=time.perf_counter()-t
    def build(self,e):
        t=time.perf_counter();r=produce(e);self.phases["construction_seconds"]+=time.perf_counter()-t;return r
    def call(self,name,e,receipt,wanted,checked):
        self.check(len(self.rows)<40,"process-cap")
        folder=self.out/name;folder.mkdir(parents=True)
        self.save(folder/"expected.json",e);self.save(folder/"candidate.json",receipt)
        self.check(all((folder/f).stat().st_size<=32768 for f in ("expected.json","candidate.json")),"wire-limit")
        args=[sys.executable,"-B","-S",str(ROOT/"receive.py"),"--expected",str(folder/"expected.json"),"--candidate",str(folder/"candidate.json")]
        self.save(folder/"command.json",{"argv":args})
        row={"case":name};self.rows.append(row);remaining=30-(time.perf_counter()-self.started)
        if remaining<=0:raise TimeoutError("campaign-wall-limit")
        t=time.perf_counter()
        with (folder/"stdout.json").open("wb") as out,(folder/"stderr.txt").open("wb") as err:
            p=subprocess.Popen(args,stdout=out,stderr=err,preexec_fn=producer.limits)
            try:p.wait(timeout=min(3,remaining))
            finally:
                if p.poll() is None:p.kill();p.wait(timeout=.2)
        elapsed=time.perf_counter()-t;self.phases["receiving_seconds"]+=elapsed;row.update(returncode=p.returncode,wall_seconds=elapsed)
        self.check(p.returncode==0,(name,p.returncode,(folder/"stderr.txt").read_text()))
        r=json.loads((folder/"stdout.json").read_text());self.work+=r["work_units"]
        row.update(outcome=r["outcome"],reason=r["reason"],work_units=r["work_units"],interface_arithmetic_checked=r["interface_arithmetic_checked"])
        self.check(r["outcome"]==wanted,(name,r));self.check(r["expected_request"]==e,"expected-retained")
        self.check(len(r["interface_arithmetic_checked"])==checked,(name,"arithmetic-stage"))
        self.check(all(r[k] is False for k in ("native_authority","close_authorized","free_authorized")),"no-native-authority")
        self.check(0<=r["work_units"]<=10000,"work-limit")
        if wanted=="AcceptedMarkovKernelComposition":
            self.check(r["accepted_endpoint"]==receipt["interfaces"]["AC"]["context"] and r["composed_kernel"]==receipt["claims"]["composed_kernel"],"accepted-exact-result")
            self.check(bool(r["semantic_delta"]),"accepted-delta")
            self.observe(name,e,receipt)
        else:self.check(r["accepted_endpoint"] is None and r["composed_kernel"] is None and r["semantic_delta"]==[],"no-accepted-composition")
        return r
    def observe(self,name,e,receipt):
        t=time.perf_counter();p=[F(*v) for v in e["prior"]];k,l=values(e["first_kernel"]["rows"]),values(e["second_kernel"]["rows"])
        # Eight scalar path terms, never an eight-atom input to the parent.
        terms=[(i,j,z,p[i]*k[i][j]*l[j][z]) for i in range(2) for j in range(2) for z in range(2)];self.scalar_terms+=8
        observed={"AB":[sum(v for a,b,c,v in terms if a==i and b==j) for i in range(2) for j in range(2)],
                  "BC":[sum(v for a,b,c,v in terms if b==j and c==z) for j in range(2) for z in range(2)],
                  "AC":[sum(v for a,b,c,v in terms if a==i and c==z) for i in range(2) for z in range(2)]}
        self.check(sum(v for _,_,_,v in terms)==1,"scalar-path-mass")
        for tag,prob in observed.items():self.check(list(map(rat,prob))==receipt["interfaces"][tag]["context"]["probability"],"independent-path-projection:"+tag)
        self.phases["independent_observation_seconds"]+=time.perf_counter()-t
        self.save(self.out/name/"independent-paths.json",{"assumption":"declared-factorization-pKL","scalar_terms":[{"a":i,"b":j,"c":z,"mass":rat(v)} for i,j,z,v in terms],"projections":{tag:list(map(rat,v)) for tag,v in observed.items()}})


def main(out):
    out.mkdir(parents=True,exist_ok=False);c=Campaign(out);failure=None
    def deadline(*_):raise TimeoutError("campaign-wall-limit")
    signal.signal(signal.SIGALRM,deadline);signal.setitimer(signal.ITIMER_REAL,30)
    try:
        c.save(out/"contract.json",json.loads((ROOT/"contract.json").read_text()))
        primary,reuse=fixture(),fixture("reuse",True)
        good,rg=c.build(primary),c.build(reuse)
        c.call("primary/valid",primary,good,"AcceptedMarkovKernelComposition",3)
        c.call("reuse/valid",reuse,rg,"AcceptedMarkovKernelComposition",3)
        identity=fixture("identity");identity["first_kernel"]["rows"]=wire_matrix([[1,0],[0,1]]);refresh_middle(identity)
        ig=c.build(identity);c.call("identity/valid",identity,ig,"AcceptedMarkovKernelComposition",3)
        c.check(ig["claims"]["composed_kernel"]==identity["second_kernel"]["rows"],"identity-kernel-action")
        null=fixture("null-middle");null["prior"]=[[1,2],[1,2]];null["first_kernel"]["rows"]=wire_matrix([[1,0],[1,0]])
        null["second_kernel"]["rows"]=wire_matrix([[F(1,4),F(3,4)],[F(1,3),F(2,3)]]);refresh_middle(null)
        ng=c.build(null);nr=c.call("null-middle/valid",null,ng,"AcceptedMarkovKernelComposition",3)
        c.check(nr["unobserved_middle"]==[null["middle"]["labels"][1]],"unobserved-row-declared-not-learned")
        fair=fixture("fair");fair["prior"]=[[1,2],[1,2]]
        fair["first_kernel"]["rows"]=fair["second_kernel"]["rows"]=wire_matrix([[F(1,2),F(1,2)],[F(1,2),F(1,2)]]);refresh_middle(fair)
        fg=c.build(fair);c.call("fair/markov",fair,fg,"AcceptedMarkovKernelComposition",3)
        for name,e,r in (("primary",primary,good),("reuse",reuse,rg)):
            t=time.perf_counter();controls=mutations(e,r);c.phases["construction_seconds"]+=time.perf_counter()-t
            c.check(multiply(values(e["first_kernel"]["rows"]),values(e["second_kernel"]["rows"]))!=multiply(values(e["second_kernel"]["rows"]),values(e["first_kernel"]["rows"])),"genuine-noncommuting-example")
            for suffix,x,checked in controls:c.call(name+"/"+suffix,e,x,"InvalidEvidence",checked)
        x=copy.deepcopy(ng);atom=x["interfaces"]["BC"]["claims"]["atoms"][-1]
        c.check(atom["probability_mass"]==[0,1] and atom["conditional"] is None,"actual-null-conditional")
        atom.update(conditional=[[1,1],[0,1],[0,1],[0,1]],conditional_mean=[0,1],conditional_variance=[0,1])
        c.call("null-middle/invented-conditional",null,x,"InvalidEvidence",1)
        other=copy.deepcopy(null);other["second_kernel"]["rows"][1]=[[2,3],[1,3]];alt=c.build(other)
        c.check(alt["interfaces"]==ng["interfaces"] and alt["claims"]==ng["claims"],"unused-row-entire-observation-and-product-identical")
        c.call("null-middle/changed-unobserved-row",null,alt,"InvalidEvidence",0)
        models=[]
        for flip,name in ((0,"same"),(1,"opposite")):
            t=time.perf_counter();states=[{"a":a,"b":b,"c":a^flip,"mass":[1,4]} for a in range(2) for b in range(2)]
            tables={tag:[sum((F(*s["mass"]) for s in states if s[tag[0].lower()]==i and s[tag[1].lower()]==j),F(0)) for i in range(2) for j in range(2)] for tag in ("AB","BC","AC")}
            c.scalar_terms+=len(states)
            c.check(tables["AB"]==[F(1,4)]*4 and tables["BC"]==[F(1,4)]*4,"same-complete-adjacent-laws")
            c.check(tables["AC"]!=[F(1,4)]*4,"actual-nonmarkov-endpoint")
            models.append({"name":name,"states":states,"projections":{tag:list(map(rat,v)) for tag,v in tables.items()}})
            e=copy.deepcopy(fair);e["assumption"]="unspecified";candidate=produce(e)
            candidate["interfaces"]["AC"]=producer.produce(interface(e,"AC",tables["AC"]))
            c.phases["construction_seconds"]+=time.perf_counter()-t
            c.call("coupling/"+name+"-unspecified",e,candidate,"UnknownDependence",3)
            candidate["request"]=copy.deepcopy(fair)
            c.call("coupling/"+name+"-markov",fair,candidate,"InvalidEvidence",3)
        c.check(models[0]["projections"]["AC"]!=models[1]["projections"]["AC"],"two-distinct-compatible-endpoints")
        c.save(out/"coupling-models.json",{"complete_latent_carrier_size":4,"models":models,"scope":"Each model assigns C deterministically on four equiprobable (A,B) states. These adjacent marginals do not determine their endpoint coupling."})
        for name,e in bad_contexts(primary):c.call("context/"+name,e,good,"InvalidContext",0)
        c.check(len(c.rows)==40,"full-declared-case-coverage")
    except Exception as exc:failure={"type":type(exc).__name__,"message":str(exc)}
    finally:signal.setitimer(signal.ITIMER_REAL,0)
    hashes={str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in (ROOT,ROOT.parent/"probability_receipt") for p in (folder/"receive.py",folder/"run.py") if p.exists()}
    result={"profile":PROFILE,"status":"Passed" if failure is None else "Failed","failure":failure,"calls":len(c.rows),"assertions":c.assertions,
            "receiver_work_units":c.work,"supervisor_path_terms":c.scalar_terms,"search_candidates":0,"wall_seconds":time.perf_counter()-c.started,
            "phases":c.phases,"runs":c.rows,"source_sha256":hashes,"python_version":sys.version,
            "child_peak_rss_kib":resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,"supervisor_peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "cost_scope":"Instrumented phases exclude some bookkeeping but campaign wall includes it. Final report writing, archive, research/review/network not included; case reuse costs retained; no speedup claim.","native_authority":False,"new_native_vocabulary":[]}
    put(out/"execution.json",result);print(json.dumps({k:v for k,v in result.items() if k not in ("runs","source_sha256")},sort_keys=True))
    return 0 if failure is None else 1


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True)
    raise SystemExit(main(p.parse_args().output.resolve()))
