#!/usr/bin/env python3
"""Exercise the finite single-consumption state boundary.

Project-original Codex (OpenAI), Unknown v0.3, submitted through Mingli
Yuan's authorized account proxy. Account use is not review or correctness.
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


ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parent.parent
CONTRACT = ROOT / "contract.json"
TOOL = ROOT / "consume.py"
PARENT = REPOSITORY / "experiments" / "bound_charge_pair" / "evidence" / "attempt-1" / "cases"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def wire(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode()


def strict(raw):
    return json.loads(raw)


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(wire(value))


def pair_digest(account_raw, journal_raw):
    return digest(b"account\0" + account_raw + b"journal\0" + journal_raw)


def marker(pair, attempt):
    return digest(wire({"attempt_id": attempt, "kind": "no-target-test-marker",
                        "pair_digest": pair}))


def initial(pair):
    return {"profile": "single-consumption-ledger-v0", "pair_digest": pair,
            "state": "unconsumed", "attempt_id": None, "receipt_digest": None}


class Experiment:
    def __init__(self, output):
        self.output = output
        self.started = time.perf_counter()
        self.assertions = []
        self.records = []
        self.tool_seconds = 0.0
        self.tool_processes = 0
        self.work_units = 0
        self.failure = None

    def check(self, condition, label):
        if not condition:
            raise AssertionError(label)
        self.assertions.append(label)

    def make_case(self, name, pair):
        case = self.output / "cases" / name
        case.mkdir(parents=True, exist_ok=False)
        state = initial(pair)
        write_new(case / "initial.json", state)
        write_new(case / "ledger.json", state)
        return case

    def command(self, ledger, command, pair, attempt=None, receipt=None,
                crash=False):
        value = [sys.executable, str(TOOL), "--ledger", str(ledger),
                 "--command", command, "--pair-digest", pair]
        if attempt is not None:
            value += ["--attempt-id", attempt]
        if receipt is not None:
            value += ["--receipt-digest", receipt]
        if crash:
            value.append("--crash-after-reserve")
        return value

    def invoke(self, case, label, command, pair, expected, attempt=None,
               receipt=None, mutation=False):
        ledger = case / "ledger.json"
        before = ledger.read_bytes()
        started = time.perf_counter()
        process = subprocess.run(
            self.command(ledger, command, pair, attempt, receipt),
            capture_output=True, timeout=1,
        )
        elapsed = time.perf_counter() - started
        self.tool_seconds += elapsed
        self.tool_processes += 1
        self.check(process.returncode == 0, label + ":exit")
        self.check(len(process.stdout) <= 4096 and len(process.stderr) <= 4096,
                   label + ":output-bound")
        value = strict(process.stdout)
        write_new(case / (label + ".json"), value)
        after = ledger.read_bytes()
        self.check((after != before) == mutation, label + ":mutation")
        self.check(value["outcome"] == expected, label + ":outcome")
        self.check(value["effect_authorized"] is False and
                   value["retry_authorized"] is False and
                   value["refund_authorized"] is False, label + ":no-continuation")
        self.check(value["native_authority"] is False and
                   value["free_authorized"] is False, label + ":no-native")
        self.check(type(value["work_units"]) is int and
                   0 < value["work_units"] <= 4096, label + ":work-bound")
        self.work_units += value["work_units"]
        self.records.append({"case": case.name, "step": label,
                             "outcome": value["outcome"],
                             "reason": value["reason"],
                             "work_units": value["work_units"],
                             "seconds": elapsed})
        return value

    def injected_exit(self, case, pair, attempt):
        ledger = case / "ledger.json"
        before = ledger.read_bytes()
        started = time.perf_counter()
        process = subprocess.run(
            self.command(ledger, "reserve", pair, attempt=attempt, crash=True),
            capture_output=True, timeout=1,
        )
        elapsed = time.perf_counter() - started
        self.tool_seconds += elapsed
        self.tool_processes += 1
        self.check(process.returncode == 23, "crash:declared-exit")
        self.check(process.stdout == b"" and len(process.stderr) <= 4096,
                   "crash:no-receipt")
        after = ledger.read_bytes()
        self.check(after != before and strict(after)["state"] == "pending",
                   "crash:pending-retained")
        observation = {"exit_code": process.returncode,
                       "ledger_sha256_after": digest(after),
                       "receipt_present": False, "seconds": elapsed}
        write_new(case / "injected-exit.json", observation)
        self.records.append({"case": case.name, "step": "injected-exit",
                             "outcome": "ImplementationExitAfterPending",
                             "reason": "DeclaredCrashPoint", "work_units": None,
                             "seconds": elapsed})

    def contention(self, case, pair):
        ledger = case / "ledger.json"
        before = ledger.read_bytes()
        started = time.perf_counter()
        processes = [
            subprocess.Popen(self.command(ledger, "reserve", pair, attempt=attempt),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for attempt in ("contender-a", "contender-b")
        ]
        values = []
        for index, process in enumerate(processes):
            stdout, stderr = process.communicate(timeout=1)
            self.tool_processes += 1
            self.check(process.returncode == 0, "contention:exit-" + str(index))
            self.check(len(stdout) <= 4096 and len(stderr) <= 4096,
                       "contention:output-" + str(index))
            value = strict(stdout)
            values.append(value)
            write_new(case / ("contender-" + str(index) + ".json"), value)
            self.check(value["effect_authorized"] is False and
                       value["retry_authorized"] is False,
                       "contention:no-continuation-" + str(index))
            self.check(0 < value["work_units"] <= 4096,
                       "contention:work-" + str(index))
            self.work_units += value["work_units"]
            self.records.append({"case": case.name,
                                 "step": "contender-" + str(index),
                                 "outcome": value["outcome"],
                                 "reason": value["reason"],
                                 "work_units": value["work_units"],
                                 "seconds": None})
        elapsed = time.perf_counter() - started
        self.tool_seconds += elapsed
        self.check(sorted(value["outcome"] for value in values) ==
                   ["PendingRecorded", "UnknownConsumptionState"],
                   "contention:one-pending")
        self.check(before != ledger.read_bytes() and
                   strict(ledger.read_bytes())["state"] == "pending",
                   "contention:single-transition")

    def run(self):
        self.output.mkdir(parents=True, exist_ok=False)
        contract = strict(CONTRACT.read_bytes())
        write_new(self.output / "contract.json", contract)
        self.check(contract["status"] == "FrozenBeforeExecution", "contract-frozen")
        self.check(digest(TOOL.read_bytes()) == contract["pins"]["tool_sha256"],
                   "tool-pin")

        alpha_account = (PARENT / "exact-alpha" / "account.json").read_bytes()
        alpha_journal = (PARENT / "exact-alpha" / "journal.json").read_bytes()
        gamma_account = (PARENT / "exact-gamma" / "account.json").read_bytes()
        gamma_journal = (PARENT / "exact-gamma" / "journal.json").read_bytes()
        for label, raw in (("alpha_account", alpha_account),
                           ("alpha_journal", alpha_journal),
                           ("gamma_account", gamma_account),
                           ("gamma_journal", gamma_journal)):
            self.check(digest(raw) == contract["pins"][label + "_sha256"],
                       label + ":pin")
        alpha = pair_digest(alpha_account, alpha_journal)
        gamma = pair_digest(gamma_account, gamma_journal)
        self.check(alpha != gamma, "distinct-parent-pairs")

        normal = self.make_case("normal-alpha", alpha)
        self.invoke(normal, "00-reconcile", "reconcile", alpha,
                    "ProvenUnconsumed")
        self.invoke(normal, "01-reserve", "reserve", alpha, "PendingRecorded",
                    attempt="alpha-attempt", mutation=True)
        self.invoke(normal, "02-commit", "commit", alpha, "ConsumedRecorded",
                    attempt="alpha-attempt", receipt=marker(alpha, "alpha-attempt"),
                    mutation=True)
        first_recheck = self.invoke(normal, "03-reconcile", "reconcile", alpha,
                                    "StoredConsumed")
        second_reserve = self.invoke(normal, "04-second-reserve", "reserve", alpha,
                                     "StoredConsumed", attempt="alpha-second")
        self.check(first_recheck["receipt_digest"] == second_reserve["receipt_digest"],
                   "normal:receipt-stable")

        reuse = self.make_case("normal-gamma", gamma)
        self.invoke(reuse, "00-reserve", "reserve", gamma, "PendingRecorded",
                    attempt="gamma-attempt", mutation=True)
        self.invoke(reuse, "01-commit", "commit", gamma, "ConsumedRecorded",
                    attempt="gamma-attempt", receipt=marker(gamma, "gamma-attempt"),
                    mutation=True)
        self.invoke(reuse, "02-reconcile", "reconcile", gamma, "StoredConsumed")

        crashed = self.make_case("crash-after-pending", alpha)
        self.injected_exit(crashed, alpha, "crash-attempt")
        self.invoke(crashed, "01-reconcile", "reconcile", alpha,
                    "UnknownConsumptionState")
        self.invoke(crashed, "02-later-reserve", "reserve", alpha,
                    "UnknownConsumptionState", attempt="later-attempt")

        contended = self.make_case("contended-pending", gamma)
        self.contention(contended, gamma)
        self.invoke(contended, "02-reconcile", "reconcile", gamma,
                    "UnknownConsumptionState")

        wrong = self.make_case("wrong-pair", alpha)
        self.invoke(wrong, "00-wrong-reserve", "reserve", gamma,
                    "InvalidContext", attempt="wrong-attempt")
        self.invoke(wrong, "01-reconcile", "reconcile", alpha,
                    "ProvenUnconsumed")

        self.check(self.tool_processes == contract["limits"]["tool_processes"],
                   "process-count-exact")
        self.check(self.work_units <= contract["limits"]["work_units"],
                   "work-bound-total")
        retained = sum(path.stat().st_size for path in self.output.rglob("*")
                       if path.is_file())
        self.check(retained <= contract["limits"]["retained_output_bytes"],
                   "retained-output-bound")

    def result(self):
        return {
            "profile": "adva.research.single-consumption-receipt.v0",
            "status": "Passed" if self.failure is None else "Failed",
            "failure": self.failure,
            "main_at_start": "fec283277f3175be2a6ff69897d896526fc54fc9",
            "assertions": len(self.assertions),
            "assertion_labels": self.assertions,
            "tool_processes": self.tool_processes,
            "target_processes": 0,
            "expected_injected_exits": 1,
            "search_candidates": 0,
            "implementation_correction_replays": 0,
            "work_units_with_receipts": self.work_units,
            "tool_seconds": self.tool_seconds,
            "wall_seconds": time.perf_counter() - self.started,
            "child_peak_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            "supervisor_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "records": self.records,
            "source_sha256": {
                str(path.relative_to(REPOSITORY)): digest(path.read_bytes())
                for path in (CONTRACT, Path(__file__), TOOL)
            },
            "result": "One finite pair occupies one local consumption chain. Completed chains retain one marker and block later reservation; a process exit or contention after pending leaves UnknownConsumptionState and blocks retry.",
            "new_vocabulary": [],
            "native_authority": False,
            "limitations": "The marker is test data and no target effect runs. Atomic replacement, flock and fsync are exercised only on one trusted Linux host; power loss, filesystem failure, hostile code and distributed operation are not covered. The declared crash process emits no work receipt, so its structural work is unmeasured. UnknownConsumptionState is a local outcome, not a promoted word or native judgment.",
        }


def main(output):
    experiment = Experiment(output)
    signal.signal(signal.SIGALRM,
                  lambda *_: (_ for _ in ()).throw(TimeoutError("outer-wall-limit")))
    signal.setitimer(signal.ITIMER_REAL, 15)
    try:
        experiment.run()
    except Exception as error:
        experiment.failure = type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    result = experiment.result()
    if output.exists():
        (output / "execution.json").write_bytes(wire(result))
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ("assertion_labels", "records", "source_sha256")},
                     sort_keys=True))
    return 0 if experiment.failure is None else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    raise SystemExit(main(args.output.resolve()))
