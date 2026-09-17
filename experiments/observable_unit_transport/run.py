#!/usr/bin/env python3
"""Original exact unit-transport producer and bounded supervisor, Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy; not his review.
This producer imports the old probability producer, never the new receiver.
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

ROOT = Path(__file__).resolve().parent
PROFILE = "adva.research.observable-unit-transport.v0"
spec = importlib.util.spec_from_file_location("observable_probability_producer", ROOT.parent / "probability_receipt/run.py")
producer = importlib.util.module_from_spec(spec); spec.loader.exec_module(producer)
put, rat = producer.put, producer.rat
SCALE = {"m":F(1), "cm":F(1,100), "s":F(1), "ms":F(1,1000)}


def fixture(reuse=False):
    source = {"question":"observable-unit-time-reuse" if reuse else "observable-unit-length",
              "carrier":["case:0","case:1","case:2","case:3"],
              "reference":[rat(F(1,4))]*4,
              "probability":list(map(rat,[F(1,4),F(1,4),F(1,2),0] if reuse else [F(1,2),F(1,4),F(1,4),0])),
              "observation":["a","a","b","void"] if reuse else ["a","a","b","b"],
              "observable":{"name":"elapsed-coordinate" if reuse else "position-coordinate",
                            "unit":"s" if reuse else "m",
                            "values":list(map(rat,[0,F(1,4),F(1,2),1] if reuse else [0,1,2,3]))},
              "history":["receiver-declared-original-question"],
              "scope":"complete-declared-finite-carrier"}
    dimension, first, second = ("Time","s","ms") if reuse else ("Length","m","cm")
    return {"source":source, "source_quantity":{"dimension":dimension,"unit":first,"origin":[0,1]},
            "target_quantity":{"dimension":dimension,"unit":second,"origin":[0,1]},
            "step":first+"-to-"+second}


def produce(expected):
    first, second = expected["source_quantity"]["unit"], expected["target_quantity"]["unit"]
    a = SCALE[first]/SCALE[second]
    target = copy.deepcopy(expected["source"])
    target["observable"]["values"] = [rat(F(*v)*a) for v in target["observable"]["values"]]
    target["observable"]["unit"] = second
    target["history"].append(expected["step"])
    return {"profile":PROFILE,"request":copy.deepcopy(expected),
            "source_receipt":producer.produce(expected["source"]),
            "target_receipt":producer.produce(target),
            "transport":{"factor":rat(a),"expectation_unit":{"unit":second,"power":1},
                         "variance_unit":{"unit":second,"power":2}}}


def mutations(expected, good):
    rows = []
    a = F(*good["transport"]["factor"])
    def save(name, value, checked): rows.append((name,value,checked))
    x = copy.deepcopy(good); x["transport"]["factor"] = rat(a+1); save("wrong-factor",x,2)
    x = copy.deepcopy(good); x["target_receipt"]["claims"]["variance"] = rat(a*F(*good["source_receipt"]["claims"]["variance"])); save("linear-variance",x,1)
    x = copy.deepcopy(good); x["transport"]["variance_unit"]["power"] = 1; save("unsquared-unit",x,2)
    x = copy.deepcopy(good); x["target_receipt"]["claims"]["density_energy"] = rat(a*a*F(*good["source_receipt"]["claims"]["density_energy"])); save("scaled-density-energy",x,1)
    for mode in ("probability","observation","observable","history"):
        target = copy.deepcopy(good["target_receipt"]["context"])
        if mode == "probability": target[mode] = [rat(F(1,4))]*4
        elif mode == "observation": target[mode] = ["all"]*4
        elif mode == "observable":
            # The zero-probability coordinate changes: all reported moments agree,
            # but the full carrier map is not the receiver's requested map.
            target[mode]["values"][-1] = rat(F(*target[mode]["values"][-1])+1)
        else: target[mode][0] = "substituted-history"
        x = copy.deepcopy(good); x["target_receipt"] = producer.produce(target)
        save("recomputed-"+mode,x,2)
    x = copy.deepcopy(good); x["request"]["step"] = "other-task"; save("changed-request",x,0)
    x = copy.deepcopy(good); x["native_authority"] = True; save("native-authority",x,0)
    x = copy.deepcopy(good); x["target_receipt"]["claims"]["density"].pop(); save("missing-atom",x,1)
    return rows


def unsupported(primary):
    rows=[]
    for name in ("dimension-mismatch","forged-dimension","unknown-unit","nonzero-origin","noncanonical-zero",
                 "boolean-origin","source-unit-mismatch","target-overflow","history-full"):
        x=copy.deepcopy(primary)
        if name == "dimension-mismatch": x["target_quantity"].update(dimension="Time",unit="s")
        elif name == "forged-dimension": x["source_quantity"]["dimension"]="Time"
        elif name == "unknown-unit": x["target_quantity"]["unit"]="km"
        elif name == "nonzero-origin": x["target_quantity"]["origin"]=[1,1]
        elif name == "noncanonical-zero": x["target_quantity"]["origin"]=[0,2]
        elif name == "boolean-origin": x["target_quantity"]["origin"]=[False,1]
        elif name == "source-unit-mismatch": x["source"]["observable"]["unit"]="cm"
        elif name == "target-overflow": x["source"]["observable"]["values"][-1]=[12,1]
        else: x["source"]["history"]=["original","one","two","three"]
        rows.append((name,x))
    return rows


class Campaign:
    def __init__(self, output):
        self.output=output; self.started=time.perf_counter(); self.assertions=0; self.work=0; self.rows=[]
        self.phases={"construction_seconds":0.,"serialization_seconds":0.,"receiving_seconds":0.,"independent_observation_seconds":0.}

    def check(self, truth, detail):
        self.assertions+=1
        if not truth: raise AssertionError(detail)

    def save(self,path,value):
        t=time.perf_counter(); put(path,value); self.phases["serialization_seconds"]+=time.perf_counter()-t

    def build(self,expected):
        t=time.perf_counter(); value=produce(expected); self.phases["construction_seconds"]+=time.perf_counter()-t
        return value

    def call(self,name,expected,candidate,wanted,checked):
        self.check(len(self.rows)<40,"process-bound")
        folder=self.output/name; folder.mkdir(parents=True)
        self.save(folder/"expected.json",expected); self.save(folder/"candidate.json",candidate)
        self.check((folder/"expected.json").stat().st_size<=32768 and (folder/"candidate.json").stat().st_size<=32768,"wire-bound")
        args=[sys.executable,"-B","-S",str(ROOT/"receive.py"),"--expected",str(folder/"expected.json"),"--candidate",str(folder/"candidate.json")]
        self.save(folder/"command.json",{"argv":args})
        row={"case":name}; self.rows.append(row)
        remain=30-(time.perf_counter()-self.started)
        if remain<=0: raise TimeoutError("campaign-wall-limit")
        t=time.perf_counter()
        with (folder/"stdout.json").open("wb") as out,(folder/"stderr.txt").open("wb") as err:
            p=subprocess.Popen(args,stdout=out,stderr=err,preexec_fn=producer.limits)
            try: p.wait(timeout=min(3,remain))
            finally:
                if p.poll() is None: p.kill(); p.wait(timeout=.2)
        elapsed=time.perf_counter()-t; self.phases["receiving_seconds"]+=elapsed
        row.update(returncode=p.returncode,wall_seconds=elapsed)
        self.check(p.returncode==0,(name,p.returncode,(folder/"stderr.txt").read_text()))
        r=json.loads((folder/"stdout.json").read_text())
        row.update(outcome=r["outcome"],reason=r["reason"],work_units=r["work_units"],endpoint_arithmetic_checked=r["endpoint_arithmetic_checked"])
        self.work+=r["work_units"]
        self.check(r["outcome"]==wanted,(name,r))
        self.check(r["expected_request"]==expected,name+":expected-kept")
        self.check(len(r["endpoint_arithmetic_checked"])==checked,name+":arithmetic-stage")
        self.check(all(r[k] is False for k in ("native_authority","close_authorized","free_authorized")),name+":no-native-authority")
        self.check(0<=r["work_units"]<=10000,name+":work-bound")
        if wanted=="AcceptedObservableUnitTransport":
            self.check(r["accepted_target"]==candidate["target_receipt"]["context"],name+":returned-target")
            self.check(r["transport"]==candidate["transport"] and bool(r["semantic_delta"]),name+":accepted-relation")
            self.observe(name,expected,candidate)
        else:
            self.check(r["accepted_target"] is None and r["transport"] is None and r["semantic_delta"]==[],name+":refusal-has-no-transport")
        return r

    def observe(self,name,expected,candidate):
        t=time.perf_counter()
        p=[F(*x) for x in expected["source"]["probability"]]
        values=[F(*v) for v in expected["source"]["observable"]["values"]]
        a=SCALE[expected["source_quantity"]["unit"]]/SCALE[expected["target_quantity"]["unit"]]
        # Raw second moment provides an independent variance expression.
        mean=sum(x*y for x,y in zip(p,values)); var=sum(x*y*y for x,y in zip(p,values))-mean*mean
        old,new=candidate["source_receipt"]["claims"],candidate["target_receipt"]["claims"]
        self.check(F(*old["variance"])==var and F(*new["variance"])==a*a*var,name+":second-moment-variance")
        self.check(F(*old["expectation"])==mean and F(*new["expectation"])==a*mean,name+":mean")
        for key in ("density","density_mean","density_energy","density_variance","observed_energy","hidden_residual"):
            self.check(old[key]==new[key],name+":dimensionless-"+key)
        for atom1,atom2 in zip(old["atoms"],new["atoms"]):
            self.check(atom1["conditional"]==atom2["conditional"],name+":conditional-law")
            if atom1["conditional"] is None:
                self.check(atom2["conditional_mean"] is None and atom2["conditional_variance"] is None,name+":null-preserved")
        self.phases["independent_observation_seconds"]+=time.perf_counter()-t
        self.save(self.output/name/"independent-observation.json",{"factor":rat(a),"source_mean":rat(mean),"target_mean":rat(a*mean),
                  "source_variance":rat(var),"target_variance":rat(a*a*var),"density_energy":old["density_energy"],"hidden_residual":old["hidden_residual"]})


def main(output):
    output.mkdir(parents=True,exist_ok=False); c=Campaign(output); failure=None
    def deadline(*_): raise TimeoutError("campaign-wall-limit")
    signal.signal(signal.SIGALRM,deadline); signal.setitimer(signal.ITIMER_REAL,30)
    try:
        c.save(output/"contract.json",json.loads((ROOT/"contract.json").read_text()))
        t=time.perf_counter(); primary,reuse=fixture(),fixture(True)
        c.phases["construction_seconds"]+=time.perf_counter()-t
        good=c.build(primary)
        r=c.call("primary/forward",primary,good,"AcceptedObservableUnitTransport",2)
        inverse=copy.deepcopy(primary); inverse["source"]=r["accepted_target"]
        inverse["source_quantity"],inverse["target_quantity"]=copy.deepcopy(primary["target_quantity"]),copy.deepcopy(primary["source_quantity"])
        inverse["step"]="cm-to-m-retained-inverse"
        inv=c.build(inverse); reverse=c.call("primary/inverse",inverse,inv,"AcceptedObservableUnitTransport",2)
        returned=reverse["accepted_target"]
        c.check(returned["observable"]==primary["source"]["observable"],"inverse-numerical-return")
        c.check(returned["history"]==primary["source"]["history"]+[primary["step"],inverse["step"]],"inverse-two-history-entries")
        rg=c.build(reuse); c.call("reuse/forward",reuse,rg,"AcceptedObservableUnitTransport",2)
        constant=copy.deepcopy(primary); constant["source"]["observable"]["values"]=[[2,1]]*4
        cg=c.build(constant); c.call("constant/forward",constant,cg,"AcceptedObservableUnitTransport",2)
        c.check(cg["source_receipt"]["claims"]["variance"]==[0,1] and cg["target_receipt"]["claims"]["variance"]==[0,1],"zero-variance-retained")
        identity=copy.deepcopy(primary); identity["target_quantity"]=copy.deepcopy(identity["source_quantity"]); identity["step"]="identity-still-keeps-history"
        c.call("identity/forward",identity,c.build(identity),"AcceptedObservableUnitTransport",2)
        for name,expected,candidate in (("primary",primary,good),("reuse",reuse,rg)):
            t=time.perf_counter(); controls=mutations(expected,candidate); c.phases["construction_seconds"]+=time.perf_counter()-t
            for suffix,x,checked in controls:
                if suffix == "recomputed-observable":
                    c.check(x["target_receipt"]["claims"] == candidate["target_receipt"]["claims"],"zero-mass-change-keeps-all-statistics")
                c.call(name+"/"+suffix,expected,x,"InvalidEvidence",checked)
        x=copy.deepcopy(rg); atom=x["target_receipt"]["claims"]["atoms"][-1]
        c.check(atom["label"]=="void" and atom["conditional"] is None,"actual-zero-event-control")
        atom.update(conditional=[[1,1],[0,1],[0,1],[0,1]],conditional_mean=[0,1],conditional_variance=[0,1])
        c.call("reuse/invented-zero-conditional",reuse,x,"InvalidEvidence",1)
        t=time.perf_counter(); contexts=unsupported(primary); c.phases["construction_seconds"]+=time.perf_counter()-t
        for name,expected in contexts: c.call("context/"+name,expected,good,"InvalidContext",0)
        c.check(len(c.rows)==37,"declared-37-case-coverage")
    except Exception as exc:
        failure={"type":type(exc).__name__,"message":str(exc)}
    finally: signal.setitimer(signal.ITIMER_REAL,0)
    hashes={str(path.relative_to(ROOT.parent)):hashlib.sha256(path.read_bytes()).hexdigest()
            for folder in (ROOT,ROOT.parent/"probability_receipt") for path in (folder/"receive.py",folder/"run.py") if path.exists()}
    result={"profile":PROFILE,"status":"Passed" if failure is None else "Failed","failure":failure,
            "calls":len(c.rows),"assertions":c.assertions,"work_units":c.work,"search_candidates":0,
            "wall_seconds":time.perf_counter()-c.started,"phases":c.phases,"runs":c.rows,"source_sha256":hashes,
            "child_peak_rss_kib":resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            "supervisor_peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "python_version":sys.version,"native_authority":False,"new_native_vocabulary":[],
            "cost_scope":"Instrumented construction, serialization, fresh receiving and independent checks; per-case reuse timings retained. Final report encoding, uninstrumented bookkeeping, archival, research, review and network costs not isolated."}
    put(output/"execution.json",result)
    print(json.dumps({k:v for k,v in result.items() if k not in ("runs","source_sha256")},sort_keys=True))
    return 0 if failure is None else 1


if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True)
    raise SystemExit(main(p.parse_args().output.resolve()))
