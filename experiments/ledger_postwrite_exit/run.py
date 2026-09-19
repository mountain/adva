#!/usr/bin/env python3
"""Bounded post-write/pre-COMMIT contention-and-exit experiment."""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import select
import signal
import sqlite3
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("prior_holder", ROOT.parent / "ledger_holder_exit/run.py")
prior = importlib.util.module_from_spec(spec); spec.loader.exec_module(prior)
ancestor = prior.ancestor


class Campaign(prior.Campaign):
    def launch(self, case, command, db, expected, candidate=None, engine="new", gate=None, reverse_json=False):
        self.check(len(self.jobs) < 16, "frozen-child-count")
        self.check(self.work < 100000, "frozen-total-receiver-work")
        if gate is None:
            return ancestor.Campaign.launch(self, case, command, db, expected, candidate, engine, None, reverse_json)
        self.check(engine == "new" and not reverse_json, "postwrite-gate-scope")
        folder = self.output / case; folder.mkdir(parents=True, exist_ok=False)
        self.save(folder / "expected.json", expected)
        self.save(folder / "candidate.json", candidate)
        self.check((folder / "candidate.json").stat().st_size <= 196608, "candidate-wire-limit")
        argv = ["--ready-fd", str(gate[0]), "--release-fd", str(gate[1]), "--", command,
                "--expected", str(folder / "expected.json"), "--ledger", str(db),
                "--candidate", str(folder / "candidate.json")]
        args = [sys.executable, "-B", "-S", str(ROOT / "gate_worker.py"), *argv]
        self.save(folder / "command.json", {"argv": args, "test_gate": "before-commit"})
        out = (folder / "stdout.json").open("wb"); err = (folder / "stderr.txt").open("wb")
        started = time.perf_counter()
        try:
            process = subprocess.Popen(args, stdout=out, stderr=err, pass_fds=tuple(gate),
                                       preexec_fn=ancestor.producer.limits)
        finally:
            out.close(); err.close()
        job = {"case": case, "process": process, "started": started, "folder": folder,
               "expected": expected, "done": False}
        self.jobs.append(job); self.event(case, "launched", pid=process.pid)
        return job

    def episode(self, name, expected, mode):
        started = time.perf_counter(); folder = self.output / name; folder.mkdir(parents=True)
        db = folder / "ledger.sqlite3"; good = ancestor.producer.envelope(expected)
        good["profile"] = ancestor.PROFILE
        self.finish(self.launch(name+"/init", "init", db, expected), "InitializedLedger")
        before = self.observe(db, folder, "before-overlap")
        ready_r, ready_w = os.pipe(); release_r, release_w = os.pipe()
        fds = {ready_r, ready_w, release_r, release_w}; held = None
        try:
            held = self.launch(name+"/holder", "submit", db, expected, good, gate=(ready_w, release_r))
            os.close(ready_w); fds.remove(ready_w); os.close(release_r); fds.remove(release_r)
            readable, _, _ = select.select([ready_r], [], [], 1.5)
            self.check(bool(readable), "readiness-deadline")
            wire = os.read(ready_r, 4096); self.check(wire.endswith(b"\n") and len(wire)<4096, "ready-wire")
            ready = json.loads(wire)
            self.check(ready["event"] == "writes-complete-before-commit" and
                       ready["pid"] == held["process"].pid and ready["in_transaction"] is True,
                       "actual-postwrite-transaction")
            self.check(ready["tentative_rows"] == [[1, good["transition_key"]]] and
                       ready["tentative_allowance"] == {"grant":3,"spent":3,"remaining":0},
                       "holder-sees-both-tentative-writes")
            busy = self.finish(self.launch(name+"/contender", "submit", db, expected, good), "LedgerBusy")
            self.check(busy["parent_checked"] is False and busy["stored_result"] is None and
                       busy["allowance"] is None and busy["debit_delta"] == 0,
                       "contention-is-nonsemantic")
            self.check(busy["sqlite_diagnostic"]["primary_code"] == 5 and
                       busy["sqlite_diagnostic"]["in_transaction"] is False, "pretransaction-busy")
            held["process"].kill(); remaining = min(3-(time.perf_counter()-held["started"]),
                                                    30-(time.perf_counter()-self.started))
            self.check(remaining > 0, "holder-exit-budget"); held["process"].wait(timeout=remaining)
            held["done"] = True; held["wall_seconds"] = time.perf_counter()-held["started"]
            self.phases["child_lifetime_seconds_sum"] += held["wall_seconds"]
            self.check(held["process"].returncode == -signal.SIGKILL and
                       (held["folder"] / "stdout.json").read_bytes() == b"", "killed-before-reply")
            held["partial_work_units"] = ready["work_units"]; self.work += ready["work_units"]
        finally:
            for fd in fds:
                try: os.close(fd)
                except OSError: pass
            if held is not None and held["process"].poll() is None:
                held["process"].kill(); held["process"].wait(timeout=.5)
        after = self.observe(db, folder, "after-exit")
        self.check(after == before, "tentative-writes-rolled-back-to-entire-logical-prestate")
        retry_expected, retry_candidate = copy.deepcopy(expected), copy.deepcopy(good)
        wanted = "CommittedContinuation"
        if mode == "false-arithmetic":
            retry_candidate["checkpoint_receipt"]["next_receipt"]["target_receipt"]["claims"]["net_value"]=[7,1]
            wanted = "InvalidEvidence"
        elif mode == "changed-context":
            retry_expected["prefix_request"]["source"]["history"][0]="substituted-origin"
            wanted = "InvalidContext"
        reply = self.finish(self.launch(name+"/retry", "submit", db, retry_expected, retry_candidate), wanted)
        final = self.observe(db, folder, "after-retry")
        if mode == "valid":
            self.check(reply["parent_checked"] is True and reply["debit_delta"] == 1, "fresh-check-one-debit")
            self.check(len(final["transitions"]) == 1 and
                       json.loads(final["meta"][0][-1]) == {"grant":3,"spent":3,"remaining":0},
                       "one-committed-slot-and-debit")
        else:
            self.check(final == before and reply["stored_result"] is None and reply["debit_delta"] == 0,
                       "refusal-preserves-entire-ledger")
            self.check(reply["parent_checked"] is (mode == "false-arithmetic"),
                       "context-before-arithmetic")
        return {"case":name,"retry_outcome":reply["outcome"],"rollback_exact":after==before,
                "final_slots":len(final["transitions"]),"wall_seconds":time.perf_counter()-started}


def main(output):
    output.mkdir(parents=True, exist_ok=False); c=Campaign(output); failure=None; episodes=[]
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("campaign-wall-limit")))
    signal.setitimer(signal.ITIMER_REAL,30)
    try:
        c.save(output/"contract.json",json.loads((ROOT/"contract.json").read_text()))
        families=list(ancestor.producer.families())
        for family,mode in [(0,"valid"),(1,"valid"),(0,"false-arithmetic"),(1,"changed-context")]:
            label,expected=families[family]; episodes.append(c.episode(label+"/"+mode,expected,mode))
        c.check(len(c.jobs)==16 and len(episodes)==4,"complete-frozen-schedules")
    except Exception as error:
        failure=type(error).__name__+": "+str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL,0); c.cleanup()
    hashes={}
    for name in ("ledger_postwrite_exit","ledger_holder_exit","decision_ledger_contention","decision_ledger",
                 "decision_checkpoint","decision_scale_composition","decision_scale","finite_decision","probability_receipt"):
        for filename in ("run.py","receive.py","gate_worker.py","contract.json"):
            p=ROOT.parent/name/filename
            if p.exists(): hashes[str(p.relative_to(ROOT.parent.parent))]=hashlib.sha256(p.read_bytes()).hexdigest()
    rows=[{"case":j["case"],"returncode":j["process"].returncode,"wall_seconds":j.get("wall_seconds"),
           "outcome":j.get("report",{}).get("outcome"),"work_units":j.get("report",{}).get("work_units",j.get("partial_work_units"))} for j in c.jobs]
    result={"profile":"adva.research.ledger-postwrite-exit.v0","status":"Passed" if failure is None else "Failed",
            "failure":failure,"assertions":c.assertions,"processes":len(rows),"search_candidates":0,
            "work_units":c.work,"wall_seconds":time.perf_counter()-c.started,"phases":c.phases,
            "episodes":episodes,"runs":rows,"events":c.events,"source_sha256":hashes,
            "python_version":sys.version,"sqlite_version":sqlite3.sqlite_version,
            "child_peak_rss_kib":resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            "supervisor_peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "new_vocabulary":[],"native_authority":False,
            "measurement_limits":"Receiver work includes gate-reported partial holder work, not OS/supervisor operations. Child lifetimes overlap. RSS values are per-category maxima, not aggregate memory."}
    ancestor.put(output/"execution.json",result)
    print(json.dumps({k:v for k,v in result.items() if k not in ("runs","events","source_sha256")},sort_keys=True))
    return 0 if failure is None else 1


if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True)
    raise SystemExit(main(p.parse_args().output.resolve()))
