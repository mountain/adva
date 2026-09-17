#!/usr/bin/env python3
"""Original finite ledger campaign under Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy; not his review.
The supervisor observes SQLite independently and never imports the new receiver.
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
import sqlite3
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
PROFILE = "adva.research.decision-ledger.v0"
spec = importlib.util.spec_from_file_location("ledger_checkpoint_producer", ROOT.parent / "decision_checkpoint/run.py")
producer = importlib.util.module_from_spec(spec); spec.loader.exec_module(producer)
put = producer.put


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def snapshot(path):
    if not path.exists(): return None
    db = sqlite3.connect(path.as_uri() + "?mode=rw", uri=True, isolation_level=None)
    try:
        m = db.execute("SELECT profile,expected_json,checker_json,initial_allowance_json,allowance_json FROM meta WHERE singleton=1").fetchone()
        rows = db.execute("SELECT transition_key,payload_json,result_json FROM transitions ORDER BY slot").fetchall()
    finally:
        db.close()
    return {"meta": {"profile": m[0], "expected": json.loads(m[1]), "checker": json.loads(m[2]),
                     "initial_allowance": json.loads(m[3]), "allowance": json.loads(m[4])},
            "transitions": [{"key": key, "payload": json.loads(payload), "result": json.loads(result)} for key, payload, result in rows]}


def families():
    f = producer.producer.producer.producer.fixture
    for name, source in [
        ("symmetric", f("ledger-symmetric")),
        ("asymmetric-reuse", f("ledger-asymmetric", prior=(F(3, 5), F(2, 5)),
          kernel=((F(2, 3), F(1, 3)), (F(1, 4), F(3, 4))), loss=((0, 3), (2, 0)), cost=F(1, 10))),
    ]:
        source["history"] = source["history"][:1]
        expected = {"prefix_request": {"source": source, "steps": [
            {"factor": [2, 1], "target_unit": "middle-unit", "step": name + ":first"},
            {"factor": [1, 2], "target_unit": source["loss_unit"], "step": name + ":second"}]},
            "pending_step": {"factor": [3, 2], "target_unit": "continued-unit", "step": name + ":third"},
            "allowance": {"grant": 3, "spent": 2, "remaining": 1}}
        yield name, expected


def envelope(expected):
    return {"profile": PROFILE, "transition_key": "chosen-transition",
            "checkpoint_receipt": producer.produce(expected)}


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (128 * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (3, 3))
    resource.setrlimit(resource.RLIMIT_FSIZE, (2 * 1024**2,) * 2)


class Campaign:
    def __init__(self, output):
        self.output = output; self.started = time.perf_counter(); self.metrics = []
        self.assertions = 0; self.work = 0
        self.phases = dict(construction_seconds=0.0, serialization_seconds=0.0,
                           receiving_seconds=0.0, observation_seconds=0.0)

    def check(self, condition, detail):
        self.assertions += 1
        if not condition: raise AssertionError(detail)

    def call(self, name, command, db, expected, candidate, wanted, fault=None, reverse_json=False):
        remaining = 30 - (time.perf_counter() - self.started)
        if len(self.metrics) >= 52 or remaining <= 0: raise RuntimeError("UnknownBudget")
        folder = self.output / name; folder.mkdir(parents=True)
        t = time.perf_counter(); before = snapshot(db); self.phases["observation_seconds"] += time.perf_counter() - t
        t = time.perf_counter()
        put(folder / "before.json", before); put(folder / "expected.json", expected)
        args = [sys.executable, "-B", "-S", str(ROOT / "receive.py"), command,
                "--expected", str(folder / "expected.json"), "--ledger", str(db)]
        if candidate is not None:
            if reverse_json:
                # Different byte order and whitespace, same parsed canonical payload.
                raw = json.dumps(dict(reversed(list(candidate.items()))), ensure_ascii=False)
                (folder / "candidate.json").write_text(raw + "\n")
                self.check(raw != json.dumps(candidate, sort_keys=True, indent=2), name + ":distinct-wire")
            else: put(folder / "candidate.json", candidate)
            args += ["--candidate", str(folder / "candidate.json")]
        if fault: args += ["--fault", fault]
        put(folder / "command.json", {"argv": args, "fault": fault})
        self.phases["serialization_seconds"] += time.perf_counter() - t
        remaining = 30 - (time.perf_counter() - self.started)
        if remaining <= 0: raise TimeoutError("campaign-wall-limit")
        t = time.perf_counter()
        with (folder / "stdout.json").open("wb") as out, (folder / "stderr.txt").open("wb") as err:
            p = subprocess.run(args, stdout=out, stderr=err, timeout=min(3, remaining), preexec_fn=limits)
        elapsed = time.perf_counter() - t; self.phases["receiving_seconds"] += elapsed
        row = {"case": name, "command": command, "returncode": p.returncode, "wall_seconds": elapsed}
        self.metrics.append(row)
        t = time.perf_counter(); after = snapshot(db); self.phases["observation_seconds"] += time.perf_counter() - t
        t = time.perf_counter(); put(folder / "after.json", after); self.phases["serialization_seconds"] += time.perf_counter() - t
        if fault:
            self.check(p.returncode == (17 if fault == "before_commit" else 19), row)
            self.check((folder / "stdout.json").read_bytes() == b"", name + ":no-reply")
            r = json.loads((folder / "stderr.txt").read_text())
            self.check(r["fault"] == fault and r["parent_checked"] is True, r)
            self.check(r["phase"] == ("writes-complete-before-commit" if fault == "before_commit" else "commit-succeeded-before-reply"), name + ":fault-position")
            row.update(outcome="InjectedExit", phase=r["phase"], work_units=r["work_units"])
            self.work += r["work_units"]
            if fault == "before_commit": self.check(after == before, name + ":rollback")
            else:
                self.check(len(after["transitions"]) == 1, name + ":committed-slot")
                self.check(after["meta"]["allowance"] == candidate["checkpoint_receipt"]["allowance_after"], name + ":committed-debit")
            return None, after
        self.check(p.returncode == 0, row)
        r = json.loads((folder / "stdout.json").read_text()); self.work += r["work_units"]
        row.update(outcome=r["outcome"], reason=r["reason"], work_units=r["work_units"],
                   debit_delta=r["debit_delta"], parent_checked=r["parent_checked"])
        self.check(r["outcome"] == wanted, (name, r))
        self.check(r["expected_request"] == expected, name + ":expected-retained")
        self.check(all(r[k] is False for k in ("native_authority", "close_authorized", "free_authorized")), name + ":no-native-authority")
        self.check(r["debit_delta"] == (1 if wanted == "CommittedContinuation" else 0), name + ":debit")
        if wanted == "InitializedLedger":
            self.check(after["transitions"] == [] and after["meta"]["allowance"] == expected["allowance"], name + ":initialized")
        elif wanted == "CommittedContinuation":
            self.check(len(before["transitions"]) == 0 and len(after["transitions"]) == 1, name + ":one-slot")
            self.check(after["meta"]["allowance"] == candidate["checkpoint_receipt"]["allowance_after"], name + ":after-balance")
            self.check(after["transitions"][0]["payload"] == candidate and after["transitions"][0]["result"] == r["stored_result"], name + ":stored-binding")
            self.check(r["parent_checked"] is True, name + ":new-verification")
        else:
            self.check(after == before, name + ":logical-state-unchanged")
        if wanted == "ReplayedContinuation":
            self.check(r["stored_result"] == before["transitions"][0]["result"], name + ":same-result")
            self.check(r["parent_checked"] is False, name + ":replay-not-reverification")
        return r, after

    def family(self, name, expected):
        t = time.perf_counter(); good = envelope(expected)
        cap = copy.deepcopy(expected); cap["prefix_request"]["source"]["history"].append("earlier-kept")
        zero = copy.deepcopy(expected); zero["allowance"] = {"grant": 3, "spent": 3, "remaining": 0}
        self.phases["construction_seconds"] += time.perf_counter() - t
        dbdir = self.output / "databases" / name; dbdir.mkdir(parents=True)
        def call(suffix, cmd, dbname, exp=expected, cand=good, wanted="CommittedContinuation", **kw):
            return self.call(name + "/" + suffix, cmd, dbdir / (dbname + ".sqlite3"), exp,
                             None if cmd == "init" else cand, wanted, **kw)
        call("normal-init", "init", "normal", wanted="InitializedLedger")
        first, _ = call("normal-commit", "submit", "normal")
        again, _ = call("normal-replay", "submit", "normal", wanted="ReplayedContinuation")
        self.check(first["stored_result"] == again["stored_result"], name + ":same-result-restart")
        call("canonical-replay", "submit", "normal", wanted="ReplayedContinuation", reverse_json=True)
        conflict = copy.deepcopy(good); conflict["checkpoint_receipt"]["checkpoint"]["pending_step"]["step"] = "conflicting-task"
        call("same-key-conflict", "submit", "normal", cand=conflict, wanted="Conflict")
        newkey = copy.deepcopy(good); newkey["transition_key"] = "another-key"
        call("new-key-capacity", "submit", "normal", cand=newkey, wanted="PausedLedgerCapacity")
        changed = copy.deepcopy(expected); changed["allowance"] = {"grant": 3, "spent": 1, "remaining": 2}
        call("changed-context", "submit", "normal", exp=changed, wanted="InvalidContext")
        call("reinit-existing", "init", "normal", wanted="LedgerExists")
        call("before-init", "init", "before", wanted="InitializedLedger")
        call("before-commit-exit", "submit", "before", fault="before_commit")
        call("before-retry", "submit", "before")
        call("before-replay", "submit", "before", wanted="ReplayedContinuation")
        call("after-init", "init", "after", wanted="InitializedLedger")
        _, saved = call("after-commit-exit", "submit", "after", fault="after_commit")
        recovered, _ = call("after-replay", "submit", "after", wanted="ReplayedContinuation")
        self.check(recovered["stored_result"] == saved["transitions"][0]["result"], name + ":lost-reply-recovered")
        call("invalid-init", "init", "invalid", wanted="InitializedLedger")
        invalid = copy.deepcopy(good)
        invalid["checkpoint_receipt"]["next_receipt"]["target_receipt"]["claims"]["net_value"] = [7, 1]
        call("invalid-parent", "submit", "invalid", cand=invalid, wanted="InvalidEvidence")
        call("valid-after-invalid", "submit", "invalid")
        call("pause-init", "init", "pause", exp=cap, wanted="InitializedLedger")
        cap_cand = envelope(cap)
        call("pause-history", "submit", "pause", exp=cap, cand=cap_cand, wanted="PausedHistoryCapacity")
        call("pause-repeat", "submit", "pause", exp=cap, cand=cap_cand, wanted="PausedHistoryCapacity")
        call("missing-database", "submit", "missing", wanted="MissingLedger")
        call("zero-init", "init", "zero", exp=zero, wanted="InitializedLedger")
        call("pause-allowance", "submit", "zero", exp=zero, cand=envelope(zero), wanted="PausedAllowance")


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    (output / "contract.json").write_bytes((ROOT / "contract.json").read_bytes())
    c = Campaign(output)
    report = {"profile": PROFILE, "search_candidates": 0, "new_vocabulary": 0,
              "python": sys.version, "sqlite": sqlite3.sqlite_version}
    def deadline(_signum, _frame):
        raise TimeoutError("campaign-wall-limit")
    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 30)
    try:
        t = time.perf_counter(); examples = list(families()); c.phases["construction_seconds"] += time.perf_counter() - t
        for name, expected in examples: c.family(name, expected)
        c.check(len(c.metrics) == 48, "fixed-process-count")
        c.check(time.perf_counter() - c.started < 30, "campaign-wall-bound")
        report["outcome"] = "PassedDecisionLedgerCampaign"
    except Exception as error:
        report.update(outcome="UnknownBudget" if isinstance(error, TimeoutError) else "Failure", failure={"type": type(error).__name__, "message": str(error)})
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    report.update(metrics=c.metrics, assertions=c.assertions, work_units=c.work, phases=c.phases,
                  campaign_wall_seconds=time.perf_counter() - c.started,
                  peak_children_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                  peak_supervisor_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  cost_scope="All input construction, serialization, fresh child startup/receiving, independent SQLite observations and recovery reads are included in total time. construction_seconds only times primary fixtures; some control copies and pause envelopes are included in total overhead instead. SQL statements and ancestor checks contribute counted receiver work; recovery internals have time but no instruction count. Reuse is included, not separately timed. Final report writing, archiving, research and publication excluded.")
    paths = [ROOT / f for f in ("contract.json", "run.py", "receive.py")]
    paths += [ROOT.parent / d / f for d in ("decision_checkpoint", "decision_scale_composition", "decision_scale", "finite_decision", "probability_receipt") for f in ("run.py", "receive.py")]
    report["source_sha256"] = {str(p.relative_to(ROOT.parent.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    put(output / "result.json", report)
    print(json.dumps({k: report[k] for k in ("outcome", "assertions", "work_units", "campaign_wall_seconds", "peak_children_rss_kib")}))
    return 0 if report["outcome"] == "PassedDecisionLedgerCampaign" else 1


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--output", required=True, type=Path)
    raise SystemExit(main(p.parse_args().output.resolve()))
