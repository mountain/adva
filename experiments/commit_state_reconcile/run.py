#!/usr/bin/env python3
"""Construct and check nine finite reconciliation cases."""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import sqlite3
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("reconcile_producer",ROOT.parent/"decision_ledger_contention/run.py")
ancestor=importlib.util.module_from_spec(spec); spec.loader.exec_module(ancestor)
put=ancestor.put


class Campaign:
    def __init__(self,out):
        self.out=out; self.started=time.perf_counter(); self.assertions=0; self.work=0; self.runs=[]
        self.phases={"construction_seconds":0.0,"serialization_seconds":0.0,"child_lifetime_seconds_sum":0.0}
    def check(self,x,label):
        self.assertions+=1
        if not x: raise AssertionError(label)
    def save(self,path,value):
        t=time.perf_counter(); put(path,value); self.phases["serialization_seconds"]+=time.perf_counter()-t
    def invoke(self,name,script,args,wanted,ledger=None):
        self.check(len(self.runs)<15,"child-count-limit"); folder=self.out/name; folder.mkdir(parents=True)
        command=[sys.executable,"-B","-S",str(script),*args]; self.save(folder/"command.json",{"argv":command})
        before=hashlib.sha256(ledger.read_bytes()).hexdigest() if ledger is not None and ledger.is_file() else None
        started=time.perf_counter(); p=subprocess.run(command,capture_output=True,timeout=3,preexec_fn=ancestor.producer.limits)
        elapsed=time.perf_counter()-started; self.phases["child_lifetime_seconds_sum"]+=elapsed
        (folder/"stdout.json").write_bytes(p.stdout); (folder/"stderr.txt").write_bytes(p.stderr)
        self.check(p.returncode==0,(name,p.returncode,p.stderr.decode(errors="replace")))
        report=json.loads(p.stdout); self.check(report["outcome"]==wanted,(name,report))
        self.check(type(report.get("work_units")) is int and 0<=report["work_units"]<=10000,"work-per-call")
        self.work+=report["work_units"]; self.check(self.work<=100000,"total-work")
        after=hashlib.sha256(ledger.read_bytes()).hexdigest() if ledger is not None and ledger.is_file() else None
        if script==ROOT/"receive.py":
            self.check(before==after,"read-only-byte-preservation")
            self.check(report["parent_checked"] is False and report["debit_delta"]==0 and
                       report["retry_authorized"] is False,"no-check-debit-or-retry")
        self.runs.append({"case":name,"outcome":report["outcome"],"wall_seconds":elapsed,
                          "work_units":report["work_units"],"ledger_sha256_before":before,
                          "ledger_sha256_after":after})
        return report
    def init(self,name,expected,db):
        f=self.out/name; f.mkdir(parents=True); ep=f/"expected.json"; self.save(ep,expected)
        return self.invoke(name+"/init",ROOT.parent/"decision_ledger_contention/receive.py",
                           ["init","--expected",str(ep),"--ledger",str(db)],"InitializedLedger",db)
    def submit(self,name,expected,candidate,db):
        f=self.out/name; f.mkdir(parents=True,exist_ok=True); ep=f/"expected.json"; cp=f/"candidate.json"
        self.save(ep,expected); self.save(cp,candidate)
        return self.invoke(name+"/submit",ROOT.parent/"decision_ledger_contention/receive.py",
                           ["submit","--expected",str(ep),"--ledger",str(db),"--candidate",str(cp)],
                           "CommittedContinuation",db)
    def reconcile(self,name,expected,candidate,db,wanted):
        f=self.out/name; f.mkdir(parents=True,exist_ok=True); request={"profile":"adva.research.commit-state-reconcile.v0","expected_request":expected,"candidate":candidate}
        rp=f/"request.json"; self.save(rp,request); self.check(rp.stat().st_size<=196608,"request-size")
        return self.invoke(name+"/reconcile",ROOT/"receive.py",["--request",str(rp),"--ledger",str(db)],wanted,db)


def main(output):
    output.mkdir(parents=True,exist_ok=False); c=Campaign(output); failure=None
    signal.signal(signal.SIGALRM,lambda *_:(_ for _ in()).throw(TimeoutError("campaign-wall-limit")))
    signal.setitimer(signal.ITIMER_REAL,30)
    try:
        c.save(output/"contract.json",json.loads((ROOT/"contract.json").read_text()))
        t=time.perf_counter(); families=list(ancestor.producer.families()); c.phases["construction_seconds"]+=time.perf_counter()-t
        fixtures={}
        for index,label in ((0,"symmetric"),(1,"asymmetric")):
            _,expected=families[index]; candidate=ancestor.producer.envelope(expected); candidate["profile"]=ancestor.PROFILE
            empty=output/(label+"-empty.sqlite3"); committed=output/(label+"-committed.sqlite3")
            c.init(label+"-empty-build",expected,empty); c.init(label+"-committed-build",expected,committed)
            committed_reply=c.submit(label+"-committed-build",expected,candidate,committed)
            fixtures[label]=(expected,candidate,empty,committed,committed_reply)
            u=c.reconcile(label+"-empty",expected,candidate,empty,"ProvenUncommittedLedger")
            c.check(u["allowance"]=={"grant":3,"spent":2,"remaining":1} and u["stored_result"] is None,"empty-witness")
            s=c.reconcile(label+"-committed",expected,candidate,committed,"StoredCommitted")
            c.check(s["stored_result"]==committed_reply["stored_result"] and s["allowance"]=={"grant":3,"spent":3,"remaining":0},"stored-witness")
        expected,candidate,_,committed,_=fixtures["symmetric"]
        changed=copy.deepcopy(candidate); changed["checkpoint_receipt"]["checkpoint"]["pending_step"]["step"]="different-query"
        c.reconcile("changed-candidate",expected,changed,committed,"UnknownCommitState")
        changed_expected=copy.deepcopy(expected); changed_expected["prefix_request"]["source"]["history"][0]="different-origin"
        c.reconcile("changed-expected",changed_expected,candidate,committed,"UnknownCommitState")
        tampered=output/"tampered-checker.sqlite3"; shutil.copy2(committed,tampered)
        db=sqlite3.connect(tampered); db.execute("UPDATE meta SET checker_json='{}' WHERE singleton=1"); db.commit(); db.close()
        c.reconcile("tampered-checker",expected,candidate,tampered,"UnknownCommitState")
        corrupt=output/"corrupt.sqlite3"; corrupt.write_bytes(b"original synthetic invalid sqlite bytes\n")
        c.reconcile("corrupt-ledger",expected,candidate,corrupt,"UnknownCommitState")
        c.reconcile("missing-ledger",expected,candidate,output/"missing.sqlite3","UnknownCommitState")
        c.check(len(c.runs)==15,"complete-frozen-processes")
    except Exception as error:
        failure=type(error).__name__+": "+str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
    hashes={}
    for name in ("commit_state_reconcile","ledger_postwrite_exit","ledger_holder_exit","decision_ledger_contention","decision_ledger","decision_checkpoint","decision_scale_composition","decision_scale","finite_decision","probability_receipt"):
        for filename in ("receive.py","run.py","gate_worker.py","contract.json"):
            p=ROOT.parent/name/filename
            if p.exists(): hashes[str(p.relative_to(ROOT.parent.parent))]=hashlib.sha256(p.read_bytes()).hexdigest()
    result={"profile":"adva.research.commit-state-reconcile.v0","status":"Passed" if failure is None else "Failed","failure":failure,
            "assertions":c.assertions,"processes":len(c.runs),"work_units":c.work,"search_candidates":0,
            "wall_seconds":time.perf_counter()-c.started,"phases":c.phases,"runs":c.runs,"source_sha256":hashes,
            "python_version":sys.version,"sqlite_version":sqlite3.sqlite_version,
            "child_peak_rss_kib":resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            "supervisor_peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "proposed_vocabulary":["commit-state-reconcile","UnknownCommitState"],"native_authority":False,
            "measurement_limits":"RSS values are category maxima, not aggregate memory. Child lifetimes include process setup and overlap no children. Research and publication are unmeasured."}
    put(output/"execution.json",result)
    print(json.dumps({k:v for k,v in result.items() if k not in ("runs","source_sha256")},sort_keys=True))
    return 0 if failure is None else 1


if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True)
    raise SystemExit(main(p.parse_args().output.resolve()))
