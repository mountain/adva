#!/usr/bin/env python3
"""Original bounded two-process campaign, Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy; not his review.
Independent supervisor: imports only the existing producer, not the new receiver.
"""
import argparse
import copy
from fractions import Fraction as F
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
PROFILE = "adva.research.decision-ledger-contention.v0"
spec = importlib.util.spec_from_file_location("contention_producer", ROOT.parent / "decision_ledger/run.py")
producer = importlib.util.module_from_spec(spec); spec.loader.exec_module(producer)
put = producer.put


def snapshot(path):
    """All schema and application rows; never called during the overlap."""
    db = sqlite3.connect(path.as_uri() + "?mode=rw", uri=True, isolation_level=None)
    try:
        schema = db.execute("SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name").fetchall()
        meta = db.execute("SELECT * FROM meta ORDER BY singleton").fetchall()
        rows = db.execute("SELECT * FROM transitions ORDER BY slot").fetchall()
    finally:
        db.close()
    return {"schema": schema, "meta": meta, "transitions": rows}


class Campaign:
    def __init__(self, output):
        self.output = output; self.started = time.perf_counter()
        self.jobs = []; self.events = []; self.assertions = 0; self.work = 0
        self.phases = dict(construction_seconds=0.0, serialization_seconds=0.0,
                           observation_seconds=0.0, child_lifetime_seconds_sum=0.0)

    def check(self, condition, detail):
        self.assertions += 1
        if not condition: raise AssertionError(detail)

    def event(self, case, event, **values):
        self.events.append(dict(case=case, event=event, at_seconds=time.perf_counter()-self.started, **values))

    def save(self, path, value):
        t = time.perf_counter(); put(path, value)
        self.phases["serialization_seconds"] += time.perf_counter()-t

    def observe(self, path, folder, name):
        t = time.perf_counter(); state = snapshot(path)
        self.phases["observation_seconds"] += time.perf_counter()-t
        self.save(folder / (name + ".json"), state)
        return state

    def launch(self, case, command, db, expected, candidate=None, engine="new", gate=None, reverse_json=False):
        self.check(len(self.jobs) < 40, "process-count-limit")
        self.check(sum(j["process"].poll() is None for j in self.jobs) < 2, "overlap-limit")
        folder = self.output / case; folder.mkdir(parents=True, exist_ok=False)
        self.save(folder / "expected.json", expected)
        argv = [command, "--expected", str(folder / "expected.json"), "--ledger", str(db)]
        if candidate is not None:
            if reverse_json:
                t = time.perf_counter()
                wire = json.dumps(dict(reversed(list(candidate.items()))), ensure_ascii=False)
                (folder / "candidate.json").write_text(wire + "\n")
                self.phases["serialization_seconds"] += time.perf_counter()-t
            else: self.save(folder / "candidate.json", candidate)
            self.check((folder / "candidate.json").stat().st_size <= 196608, "candidate-wire-limit")
            argv += ["--candidate", str(folder / "candidate.json")]
        script = ROOT / "receive.py" if engine == "new" else ROOT.parent / "decision_ledger/receive.py"
        passed = ()
        if gate is not None:
            script = ROOT / "gate_worker.py"
            argv = ["--engine", engine, "--ready-fd", str(gate[0]), "--release-fd", str(gate[1]), "--"] + argv
            passed = tuple(gate)
        args = [sys.executable, "-B", "-S", str(script)] + argv
        self.save(folder / "command.json", {"argv": args, "test_gate": gate is not None})
        out = (folder / "stdout.json").open("wb"); err = (folder / "stderr.txt").open("wb")
        started = time.perf_counter()
        try:
            p = subprocess.Popen(args, stdout=out, stderr=err, pass_fds=passed, preexec_fn=producer.limits)
        finally:
            out.close(); err.close()
        job = dict(case=case, process=p, started=started, folder=folder, expected=expected, done=False)
        self.jobs.append(job); self.event(case, "launched", pid=p.pid)
        return job

    def finish(self, job, wanted):
        timeout = min(3-(time.perf_counter()-job["started"]), 30-(time.perf_counter()-self.started))
        if timeout <= 0: raise TimeoutError("child-or-campaign-wall-limit")
        p = job["process"]; p.wait(timeout=timeout)
        elapsed = time.perf_counter()-job["started"]
        job["wall_seconds"] = elapsed
        self.phases["child_lifetime_seconds_sum"] += elapsed
        job["done"] = True
        self.event(job["case"], "exited", pid=p.pid, returncode=p.returncode)
        self.check(p.returncode == 0, (job["case"], p.returncode, (job["folder"] / "stderr.txt").read_text()))
        r = json.loads((job["folder"] / "stdout.json").read_text())
        job["report"] = r; job["wall_seconds"] = elapsed
        if type(r.get("work_units")) is int: self.work += r["work_units"]
        self.check(r["outcome"] == wanted, (job["case"], r))
        self.check(r["expected_request"] == job["expected"], "expected-request-retained")
        self.check(all(r[k] is False for k in ("native_authority", "close_authorized", "free_authorized")), "no-native-authority")
        self.check(r["debit_delta"] == (1 if wanted == "CommittedContinuation" else 0), "reported-debit")
        self.check(type(r["work_units"]) is int and 0 <= r["work_units"] <= 10000, "work-bound")
        return r

    def episode(self, name, expected, kind, engine="new"):
        folder = self.output / name; folder.mkdir(parents=True)
        db = folder / "ledger.sqlite3"
        t = time.perf_counter(); good = producer.envelope(expected)
        good["profile"] = PROFILE if engine == "new" else producer.PROFILE
        holder = copy.deepcopy(good); contender = copy.deepcopy(good)
        holder["transition_key"] = "alpha"; contender["transition_key"] = "alpha"
        if kind == "conflict":
            contender["checkpoint_receipt"]["checkpoint"]["pending_step"]["step"] = "changed-pending-task"
        elif kind in ("keys", "reversed-keys"):
            contender["transition_key"] = "beta"
            if kind == "reversed-keys": holder["transition_key"], contender["transition_key"] = "beta", "alpha"
        elif kind == "invalid-holder":
            holder["checkpoint_receipt"]["next_receipt"]["target_receipt"]["claims"]["net_value"] = [7, 1]
        self.phases["construction_seconds"] += time.perf_counter()-t
        self.finish(self.launch(name+"/init", "init", db, expected, engine=engine), "InitializedLedger")
        before = self.observe(db, folder, "before-overlap")
        self.check(len(before["meta"]) == 1 and before["transitions"] == [], "empty-ledger")
        ready_r, ready_w = os.pipe(); release_r, release_w = os.pipe()
        fds = {ready_r, ready_w, release_r, release_w}; held = None
        try:
            held = self.launch(name+"/holder", "submit", db, expected, holder, engine, (ready_w, release_r))
            os.close(ready_w); fds.remove(ready_w); os.close(release_r); fds.remove(release_r)
            readable, _, _ = select.select([ready_r], [], [], 1.5)
            self.check(bool(readable), "gate-ready-deadline")
            wire = os.read(ready_r, 4096)
            self.check(wire.endswith(b"\n") and len(wire) < 4096, "gate-wire-bound")
            gate = json.loads(wire)
            self.check(gate["event"] == "begin-immediate-acquired" and gate["pid"] == held["process"].pid, "actual-holder-ready")
            self.check(held["process"].poll() is None, "holder-alive-before-contender")
            self.event(name, "holder-ready", readiness=gate)
            contender_job = self.launch(name+"/contender", "submit", db, expected, contender, engine)
            busy = self.finish(contender_job, "LedgerBusy" if engine == "new" else "InvalidLedger")
            self.check(held["process"].poll() is None, "holder-alive-after-contender")
            self.check(busy["stored_result"] is None and busy["allowance"] is None and busy["parent_checked"] is False, "no-authoritative-state-on-busy")
            if engine == "new":
                d = busy["sqlite_diagnostic"]
                self.check(d["primary_code"] == 5 and d["in_transaction"] is False, "numeric-pretransaction-busy")
            self.event(name, "release-holder", pid=held["process"].pid)
            os.write(release_w, b"R")
            result = self.finish(held, "InvalidEvidence" if kind == "invalid-holder" else "CommittedContinuation")
        finally:
            for fd in fds:
                try: os.close(fd)
                except OSError: pass
            if held is not None and held["process"].poll() is None:
                held["process"].terminate()
                try: held["process"].wait(timeout=.2)
                except subprocess.TimeoutExpired: held["process"].kill(); held["process"].wait(timeout=.2)
        middle = self.observe(db, folder, "after-holder")
        wanted = {"same":"ReplayedContinuation", "conflict":"Conflict", "keys":"PausedLedgerCapacity",
                  "reversed-keys":"PausedLedgerCapacity", "invalid-holder":"CommittedContinuation"}[kind]
        retry = self.finish(self.launch(name+"/retry", "submit", db, expected, contender, engine, reverse_json=kind=="same"), wanted)
        after = self.observe(db, folder, "after-retry")
        committed = contender if kind == "invalid-holder" else holder
        self.check(len(after["transitions"]) == 1, "one-final-slot")
        slot, key, payload, stored_result = after["transitions"][0]
        self.check(slot == 1 and key == committed["transition_key"] and json.loads(payload) == committed, "entire-stored-candidate")
        self.check(json.loads(stored_result) == (retry if kind == "invalid-holder" else result)["stored_result"], "entire-stored-result")
        self.check(after["schema"] == before["schema"] and after["meta"][0][:-1] == before["meta"][0][:-1], "fixed-schema-context-profile-checkers-initial-balance")
        self.check(json.loads(after["meta"][0][-1]) == committed["checkpoint_receipt"]["allowance_after"], "exact-final-allowance")
        self.check(json.loads(after["meta"][0][-1]) == {"grant":3,"spent":3,"remaining":0}, "one-debit-in-db")
        if kind == "invalid-holder":
            self.check(middle == before and result["parent_checked"] is True and retry["parent_checked"] is True, "invalid-holder-no-mutation-then-valid-recheck")
        else:
            self.check(after == middle, "retry-full-state-unchanged")
            self.check(retry["parent_checked"] is False, "occupied-slot-no-new-parent-check")
        if kind == "same": self.check(retry["stored_result"] == result["stored_result"], "same-stored-result-on-replay")
        self.check(db.stat().st_size <= 1048576, "database-byte-bound")
        return db, good

    def cleanup(self):
        for job in self.jobs:
            p = job["process"]
            if p.poll() is None:
                p.terminate()
                try: p.wait(timeout=.2)
                except subprocess.TimeoutExpired: p.kill(); p.wait(timeout=.2)


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    c = Campaign(output); failure = None
    def timeout(*_): raise TimeoutError("campaign-wall-limit")
    signal.signal(signal.SIGALRM, timeout); signal.setitimer(signal.ITIMER_REAL, 30)
    try:
        c.save(output / "contract.json", json.loads((ROOT / "contract.json").read_text()))
        t = time.perf_counter(); families = list(producer.families())
        # Fresh asymmetric instance, distinct from the sequential-ledger fixture.
        f = producer.producer.producer.producer.producer.fixture
        fresh = f("contention-asymmetric", prior=(F(1,4),F(3,4)),
                  kernel=((F(3,4),F(1,4)),(F(1,3),F(2,3))), loss=((0,2),(3,0)), cost=F(1,8))
        fresh["history"] = fresh["history"][:1]
        primary, reuse = copy.deepcopy(families[0][1]), copy.deepcopy(families[1][1])
        reuse["prefix_request"]["source"] = fresh
        c.phases["construction_seconds"] += time.perf_counter()-t
        new_db = new_good = None
        for name, expected, kinds in [("primary",primary,["same","conflict","keys","reversed-keys","invalid-holder"]),
                                      ("reuse",reuse,["same","conflict","reversed-keys"])]:
            for kind in kinds:
                db, good = c.episode(name+"/"+kind, expected, kind)
                if new_db is None: new_db, new_good = db, good
        old_db, old_good = c.episode("legacy", primary, "same", engine="legacy")
        raw = b"original synthetic non-SQLite ledger bytes\n"
        invalid = output / "not-a-database.sqlite3"; invalid.write_bytes(raw)
        r = c.finish(c.launch("non-sqlite", "submit", invalid, primary, new_good), "InvalidLedger")
        c.check(r["sqlite_diagnostic"]["primary_code"] in (11,26) and invalid.read_bytes() == raw, "non-sqlite-separate-numeric-refusal")
        for name, db, engine, good in [("new-opens-old",old_db,"new",new_good),("old-opens-new",new_db,"legacy",old_good)]:
            before = snapshot(db)
            c.finish(c.launch(name,"submit",db,primary,good,engine), "InvalidLedger")
            c.check(snapshot(db) == before, "profile-refusal-preserves-full-ledger")
        c.check(len(c.jobs) == 39, "declared-process-coverage")
    except Exception as exc:
        failure = type(exc).__name__ + ": " + str(exc)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0); c.cleanup()
    names = ["decision_ledger_contention", "decision_ledger", "decision_checkpoint", "decision_scale_composition", "decision_scale", "finite_decision", "probability_receipt"]
    hashes = {}
    for name in names:
        for filename in ("receive.py", "run.py", "gate_worker.py"):
            path = ROOT.parent / name / filename
            if path.exists(): hashes[str(path.relative_to(ROOT.parent))] = hashlib.sha256(path.read_bytes()).hexdigest()
    rows = [{"case":j["case"],"pid":j["process"].pid,"returncode":j["process"].returncode,
             "wall_seconds":j.get("wall_seconds"),"outcome":j.get("report",{}).get("outcome"),
             "work_units":j.get("report",{}).get("work_units")} for j in c.jobs]
    result = {"profile":PROFILE,"status":"Passed" if failure is None else "Failed","failure":failure,
              "assertions":c.assertions,"processes":len(rows),"work_units":c.work,"search_candidates":0,
              "wall_seconds":time.perf_counter()-c.started,"phases":c.phases,"runs":rows,"events":c.events,
              "child_peak_rss_kib":resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
              "supervisor_peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "python_version":sys.version,"sqlite_version":sqlite3.sqlite_version,"source_sha256":hashes,
              "memory_scope":"Linux ru_maxrss; largest child RSS, not simultaneous aggregate peak",
              "native_authority":False,"new_vocabulary":[]}
    put(output / "execution.json", result)
    print(json.dumps({k:v for k,v in result.items() if k not in ("runs","events","source_sha256")},sort_keys=True))
    return 0 if failure is None else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--output",type=Path,required=True)
    raise SystemExit(main(parser.parse_args().output.resolve()))
