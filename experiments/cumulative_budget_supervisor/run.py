"""Bounded synthetic trial. Trial allowance survives correction invocations.

Codex (OpenAI), project-original under Unknown v0.3, via Mingli Yuan's proxy.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

from supervisor import BoundaryError, Supervisor, strict, wire

ROOT = Path(__file__).resolve().parent


class Trial:
    def __init__(self, path):
        self.path = path
        if not path.exists():
            with path.open("xb") as stream:
                stream.write(wire({"profile": "cumulative-trial-v0", "charges": []}))

    def charge(self, units):
        data = strict(self.path.read_bytes())
        assert data["profile"] == "cumulative-trial-v0"
        assert type(units) is int and units > 0
        assert len(data["charges"]) < 20, "trial-call-reserve-exhausted"
        assert sum(data["charges"]) + units <= 400, "trial-work-exhausted"
        data["charges"].append(units)
        self.path.write_bytes(wire(data))


def main(output, trial_path):
    started = time.perf_counter()
    output.mkdir(exist_ok=False, parents=True)
    trial = Trial(trial_path)
    phases = {"construction_seconds": 0.0, "verification_seconds": 0.0,
              "serialization_seconds": 0.0, "fresh_process_seconds": 0.0}
    results, journals, checks = [], [], []
    fixture_attempts = 0
    failure = None

    def check(ok, label):
        checks.append(label)
        assert ok, label

    def new(name, work, calls):
        t = time.perf_counter()
        contract = {"task": name, "work_cap": work, "call_cap": calls, "correction_cap": 1}
        s = Supervisor(output / (name + ".json"), contract, initialize=True)
        journals.append((s.path, contract))
        phases["construction_seconds"] += time.perf_counter() - t
        return s

    def invoke(s, mode, units, command=None, timeout=0.5):
        nonlocal fixture_attempts
        fixture_attempts += 1
        r = s.run(command or [sys.executable, str(ROOT / "child.py"), mode],
                  units, mode, trial, timeout)
        results.append({"task": s.contract["task"], "mode": mode, **r})
        return r

    def refusal(s, action, reason, label):
        before = s.path.read_bytes()
        try:
            action()
            raise AssertionError(label + ": accepted")
        except (BoundaryError, FileExistsError) as exc:
            check(reason in str(exc), label + ": reason")
        check(before == s.path.read_bytes(), label + ": unchanged")

    def reload(s):
        q = Supervisor(s.path, s.contract)
        check(q.state() == s.state(), s.contract["task"] + ": reconstructed")
        return q

    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("outer-wall")))
    signal.setitimer(signal.ITIMER_REAL, 25)
    try:
        (output / "contract.json").write_bytes((ROOT / "contract.json").read_bytes())
        verify_started = time.perf_counter()
        a = new("correction", 9, 3)
        check(invoke(a, "success", 3)["outcome"] == "Observed", "A success")
        check(invoke(a, "exit", 3)["outcome"] == "ImplementationFailure", "A failure")
        refusal(a, lambda: a.reserve(1, "bypass-correction"), "AttemptBlocked", "A requires correction")
        a = reload(a)
        before = a.state()
        a.correct("replace exit fixture with reuse fixture")
        check(a.state()["reserved"] == before["reserved"] == 6, "A correction preserves debit")
        a = reload(a)
        check(invoke(a, "reuse", 3)["outcome"] == "Observed", "A reuse")
        refusal(a, lambda: a.reserve(1, "fourth"), "WorkExhausted", "A exhausted")
        check(a.state()["reserved"] == 9 and a.state()["reported_work"] == 3, "A conservative debit")

        b = new("failed-spawn", 5, 5)
        check(invoke(b, "missing", 4, [str(output / "no-such-executable")])["outcome"] ==
              "ImplementationFailure", "B failed spawn")
        b.correct("correct executable path")
        b = reload(b)
        refusal(b, lambda: b.reserve(2, "retry"), "WorkExhausted", "B no replenishment")
        check(b.state()["calls"] == 1 and b.state()["remaining_work"] == 1, "B charged before spawn")

        c = new("probe", 20, 1)
        check(invoke(c, "probe", 1)["outcome"] == "Observed", "C probe")
        refusal(c, lambda: c.reserve(1, "extra"), "CallsExhausted", "C probe uses call")

        d = new("bad-receipt", 20, 3)
        check(invoke(d, "malformed", 4)["outcome"] == "ImplementationFailure", "D malformed")
        d.correct("replace malformed receipt")
        check(invoke(d, "overreport", 4)["outcome"] == "BudgetViolation", "D overreport")
        refusal(d, lambda: d.reserve(1, "after-violation"), "AttemptBlocked", "D terminal")
        refusal(d, lambda: d.correct("again"), "CorrectionBlocked", "D cannot repair accounting away")

        e = new("unsettled", 6, 2)
        e.reserve(3, "reserved-before-controller-exit")
        e = reload(e)
        check(e.state()["stop"] == "UnknownAttemptState", "E pending")
        refusal(e, lambda: e.reserve(1, "unknown-retry"), "AttemptBlocked", "E blocks resume")

        f = new("binding", 9, 3)
        refusal(f, lambda: Supervisor(f.path, f.contract, initialize=True), "File exists", "F cannot reinitialize")
        changed = {**f.contract, "task": "different"}
        refusal(f, lambda: Supervisor(f.path, changed), "ContextChanged", "F cannot change task")
        refusal(f, lambda: f.reserve(True, "bool"), "ReservationType", "F bool")
        refusal(f, lambda: f.reserve(0, "zero"), "ReservationType", "F zero")
        refusal(f, lambda: f.reserve(-1, "negative"), "ReservationType", "F negative")
        refusal(f, lambda: f.append({"kind": "refund", "units": 1}), "EventKind", "F no refund event")

        g = new("timeout-reuse", 4, 2)
        check(invoke(g, "timeout", 2, timeout=0.1)["outcome"] == "ImplementationFailure", "G timeout")
        g = reload(g)
        g.correct("replace timeout with terminating fixture")
        check(invoke(g, "reuse", 2)["outcome"] == "Observed", "G reuse")
        check(g.state()["remaining_work"] == 0, "G no timeout refund")

        # Independent arithmetic audit does not call Supervisor.fold.
        audit = []
        for path, contract in journals:
            events = json.loads(path.read_text())["events"]
            reservations = [x["units"] for x in events if x["kind"] == "reserve"]
            cumulative = 0
            for i, n in enumerate(reservations, 1):
                cumulative += n
                check(cumulative <= contract["work_cap"] and i <= contract["call_cap"],
                      contract["task"] + ": independent prefix bound")
            state = Supervisor(path, contract).state()
            check(sum(reservations) == state["reserved"] and len(reservations) == state["calls"],
                  contract["task"] + ": independent total")
            audit.append({"task": contract["task"], "reservations": reservations, "state": state})
        # Counterfactual reset control: the old pattern has 6 spent before
        # correction; resetting allows 6 more against original cap 9.
        baseline = {"cap": 9, "before_reset": 6, "after_reset_admitted": 6}
        check(baseline["before_reset"] + baseline["after_reset_admitted"] > baseline["cap"],
              "reset baseline overspends same original cap")
        phases["verification_seconds"] += time.perf_counter() - verify_started

        # Fresh interpreter reconstruction, with its own separate charged start.
        before = a.path.read_bytes()
        expected_file = output / "inspect-context.json"
        expected_file.write_bytes(wire(a.contract))
        trial.charge(1)
        t = time.perf_counter()
        p = subprocess.run([sys.executable, str(ROOT / "supervisor.py"),
                            str(a.path), str(expected_file)], capture_output=True, timeout=0.5)
        phases["fresh_process_seconds"] += time.perf_counter() - t
        check(p.returncode == 0 and strict(p.stdout) == a.state(), "fresh process matches")
        check(a.path.read_bytes() == before, "inspection read-only")
        (output / "fresh-inspection.json").write_bytes(p.stdout)
        (output / "audit.json").write_bytes(wire({"independent": audit, "reset_control": baseline}))
        phases["serialization_seconds"] = sum(x.serialization_seconds for x in (a,b,c,d,e,f,g))
    except Exception as exc:
        failure = type(exc).__name__ + ": " + str(exc)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    trial_state = strict(trial_path.read_bytes())
    result = {"status": "Passed" if failure is None else "Failed", "failure": failure,
              "assertions": len(checks), "assertion_labels": checks, "fixture_spawn_attempts": fixture_attempts,
              "trial_account": trial_state, "trial_reserved_units": sum(trial_state["charges"]),
              "trial_charged_attempts": len(trial_state["charges"]),
              "results": results, "wall_seconds": time.perf_counter()-started, "phases": phases,
              "child_maxrss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
              "supervisor_maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "source_sha256": {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                                for name in ("contract.json","supervisor.py","child.py","run.py")},
              "search_candidates": 0, "new_vocabulary": [], "native_authority": False,
              "limitations": "Fixture work is self-reported; reservations bound entitlement, not physical CPU. RSS is per-category maximum. Verification phase includes construction and child wall times; serialization subtotal excludes reconstructed controller objects and is incomplete. No concurrent writers, journal rollback attack or power-loss guarantee."}
    (output / "execution.json").write_bytes(wire(result))
    assert sum(p.stat().st_size for p in output.rglob("*") if p.is_file()) <= 1048576
    print(json.dumps({k:v for k,v in result.items() if k not in ("results","source_sha256","assertion_labels")}))
    return 0 if failure is None else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--trial-account", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(main(args.output, args.trial_account))
