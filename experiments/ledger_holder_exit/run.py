#!/usr/bin/env python3
"""Original bounded holder-exit witness, Unknown v0.3.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
not his review or guarantee. No receiver code or arithmetic rule is changed.
"""
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
import sys
import time

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "holder_exit_ancestor", ROOT.parent / "decision_ledger_contention/run.py")
ancestor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ancestor)


class Campaign(ancestor.Campaign):
    def launch(self, *args, **kwargs):
        self.check(len(self.jobs) < 16, "frozen-child-count")
        self.check(self.work < 100000, "frozen-total-receiver-work")
        return super().launch(*args, **kwargs)

    def episode_exit(self, name, expected, mode):
        started = time.perf_counter()
        folder = self.output / name
        folder.mkdir(parents=True)
        db = folder / "ledger.sqlite3"
        t = time.perf_counter()
        good = ancestor.producer.envelope(expected)
        good["profile"] = ancestor.PROFILE
        self.phases["construction_seconds"] += time.perf_counter() - t
        self.finish(self.launch(name + "/init", "init", db, expected), "InitializedLedger")
        before = self.observe(db, folder, "before-overlap")
        ready_r, ready_w = os.pipe()
        release_r, release_w = os.pipe()
        fds = {ready_r, ready_w, release_r, release_w}
        held = None
        try:
            held = self.launch(name + "/holder", "submit", db, expected, good,
                               gate=(ready_w, release_r))
            os.close(ready_w); fds.remove(ready_w)
            os.close(release_r); fds.remove(release_r)
            readable, _, _ = select.select([ready_r], [], [], 1.5)
            self.check(bool(readable), "readiness-deadline")
            wire = os.read(ready_r, 4096)
            self.check(wire.endswith(b"\n") and len(wire) < 4096, "readiness-wire")
            ready = json.loads(wire)
            self.check(ready["event"] == "begin-immediate-acquired" and
                       ready["pid"] == held["process"].pid, "actual-held-transaction")
            self.check(held["process"].poll() is None, "holder-live-before-contender")
            self.event(name, "holder-ready", readiness=ready)
            busy = self.finish(self.launch(name + "/contender", "submit", db, expected, good),
                               "LedgerBusy")
            self.check(busy["parent_checked"] is False and busy["stored_result"] is None and
                       busy["allowance"] is None, "busy-is-not-a-semantic-judgment")
            self.check(busy["sqlite_diagnostic"]["primary_code"] == 5 and
                       busy["sqlite_diagnostic"]["in_transaction"] is False,
                       "busy-before-transaction")
            self.check(held["process"].poll() is None, "holder-live-until-injection")
            self.event(name, "sigkill-owned-holder", pid=held["process"].pid)
            held["process"].kill()
            remaining = min(3 - (time.perf_counter() - held["started"]),
                            30 - (time.perf_counter() - self.started))
            self.check(remaining > 0, "holder-exit-budget")
            held["process"].wait(timeout=remaining)
            held["done"] = True
            held["wall_seconds"] = time.perf_counter() - held["started"]
            self.phases["child_lifetime_seconds_sum"] += held["wall_seconds"]
            self.check(held["process"].returncode == -signal.SIGKILL, "actual-sigkill")
            self.check((held["folder"] / "stdout.json").read_bytes() == b"", "no-holder-reply")
            self.check(type(ready["work_units"]) is int and 0 <= ready["work_units"] <= 10000,
                       "partial-holder-work")
            held["partial_work_units"] = ready["work_units"]
            self.work += ready["work_units"]
            self.event(name, "holder-reaped", returncode=held["process"].returncode)
        finally:
            for fd in fds:
                try:
                    os.close(fd)
                except OSError:
                    pass
            if held is not None and held["process"].poll() is None:
                held["process"].kill()
                held["process"].wait(timeout=.5)
        after_exit = self.observe(db, folder, "after-exit")
        self.check(after_exit == before, "full-logical-state-preserved-after-exit")
        retry_expected, retry_candidate = copy.deepcopy(expected), copy.deepcopy(good)
        wanted = "CommittedContinuation"
        if mode == "false-arithmetic":
            retry_candidate["checkpoint_receipt"]["next_receipt"]["target_receipt"]["claims"]["net_value"] = [7, 1]
            wanted = "InvalidEvidence"
        elif mode == "changed-context":
            retry_expected["prefix_request"]["source"]["history"][0] = "substituted-origin"
            wanted = "InvalidContext"
        reply = self.finish(self.launch(name + "/retry", "submit", db,
                                        retry_expected, retry_candidate), wanted)
        final = self.observe(db, folder, "after-retry")
        if mode == "valid":
            self.check(reply["parent_checked"] is True, "fresh-arithmetic-check-required")
            self.check(len(final["transitions"]) == 1, "one-accepted-slot")
            slot, key, payload, stored = final["transitions"][0]
            self.check(slot == 1 and key == good["transition_key"] and
                       json.loads(payload) == good, "entire-accepted-payload")
            self.check(json.loads(stored) == reply["stored_result"], "entire-stored-result")
            self.check(final["schema"] == before["schema"] and
                       final["meta"][0][:-1] == before["meta"][0][:-1], "unchanged-binding")
            self.check(json.loads(final["meta"][0][-1]) ==
                       {"grant": 3, "spent": 3, "remaining": 0}, "one-real-ledger-debit")
        else:
            self.check(final == before, "refused-retry-preserves-whole-ledger")
            self.check(reply["stored_result"] is None, "refusal-has-no-accepted-result")
            self.check(reply["parent_checked"] is (mode == "false-arithmetic"),
                       "context-gate-before-arithmetic")
        self.check(db.stat().st_size <= 1048576, "database-bound")
        self.check(self.work <= 100000, "total-receiver-work-bound")
        return {"case": name, "retry_outcome": reply["outcome"],
                "exit_preserved_full_state": after_exit == before,
                "final_slot_count": len(final["transitions"]),
                "wall_seconds": time.perf_counter() - started}


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    c = Campaign(output)
    failure, episodes = None, []
    def deadline(*_):
        raise TimeoutError("campaign-wall-limit")
    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 30)
    try:
        c.save(output / "contract.json", json.loads((ROOT / "contract.json").read_text()))
        t = time.perf_counter()
        families = list(ancestor.producer.families())
        c.phases["construction_seconds"] += time.perf_counter() - t
        for family, mode in [(0, "valid"), (1, "valid"), (0, "false-arithmetic"), (1, "changed-context")]:
            name, expected = families[family]
            episodes.append(c.episode_exit(name + "/" + mode, expected, mode))
        c.check(len(c.jobs) == 16 and len(episodes) == 4, "complete-frozen-schedules")
    except Exception as exc:
        failure = type(exc).__name__ + ": " + str(exc)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        c.cleanup()
    hashes = {}
    for name in ("ledger_holder_exit", "decision_ledger_contention", "decision_ledger",
                 "decision_checkpoint", "decision_scale_composition", "decision_scale",
                 "finite_decision", "probability_receipt"):
        for filename in ("run.py", "receive.py", "gate_worker.py", "contract.json"):
            p = ROOT.parent / name / filename
            if p.exists():
                hashes[str(p.relative_to(ROOT.parent.parent))] = hashlib.sha256(p.read_bytes()).hexdigest()
    rows = [{"case": j["case"], "pid": j["process"].pid,
             "returncode": j["process"].returncode, "wall_seconds": j.get("wall_seconds"),
             "outcome": j.get("report", {}).get("outcome"),
             "work_units": j.get("report", {}).get("work_units", j.get("partial_work_units"))}
            for j in c.jobs]
    result = {"profile": "adva.research.ledger-holder-exit.v0",
              "status": "Passed" if failure is None else "Failed", "failure": failure,
              "assertions": c.assertions, "processes": len(rows), "search_candidates": 0,
              "work_units": c.work, "wall_seconds": time.perf_counter() - c.started,
              "phases": c.phases, "episodes": episodes, "runs": rows, "events": c.events,
              "source_sha256": hashes, "python_version": sys.version,
              "sqlite_version": sqlite3.sqlite_version,
              "child_peak_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
              "supervisor_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "new_vocabulary": [], "native_authority": False,
              "measurement_limits": "Receiver work includes gate-reported partial holder work, not OS/supervisor operations. Child lifetimes overlap. RSS is highest process, not aggregate concurrent memory. Final result serialization and publication are outside campaign timing."}
    ancestor.put(output / "execution.json", result)
    print(json.dumps({k: v for k, v in result.items() if k not in ("source_sha256", "events", "runs")}, sort_keys=True))
    return 0 if failure is None else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    raise SystemExit(main(parser.parse_args().output.resolve()))
