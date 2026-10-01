#!/usr/bin/env python3
"""Exercise the unbound charge window and a totals-only double claim.

Project-original ChatGPT (OpenAI), Unknown v0.3, submitted through Mingli
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
RECEIVER = ROOT / "reconcile.py"


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


def trial(charges):
    return {"profile": "cumulative-trial-v0", "charges": charges}


def journal(task, reservations):
    return {
        "contract": {"task": task, "work_cap": 20, "call_cap": 2,
                     "correction_cap": 0},
        "events": [
            {"kind": "reserve", "id": index, "units": units, "purpose": purpose}
            for index, (units, purpose) in enumerate(reservations, 1)
        ],
    }


class Experiment:
    def __init__(self, output):
        self.output = output
        self.started = time.perf_counter()
        self.assertions = []
        self.receipts = []
        self.receiver_seconds = 0.0
        self.failure = None

    def check(self, condition, label):
        if not condition:
            raise AssertionError(label)
        self.assertions.append(label)

    def receive(self, name, trial_value, journal_value):
        case = self.output / "cases" / name
        trial_path = case / "trial.json"
        journal_path = case / "journal.json"
        write_new(trial_path, trial_value)
        write_new(journal_path, journal_value)
        before = {"trial": trial_path.read_bytes(), "journal": journal_path.read_bytes()}
        started = time.perf_counter()
        process = subprocess.run(
            [sys.executable, str(RECEIVER), "--trial", str(trial_path),
             "--journal", str(journal_path)],
            capture_output=True, timeout=1,
        )
        elapsed = time.perf_counter() - started
        self.receiver_seconds += elapsed
        self.check(process.returncode == 0, name + ":receiver-exit")
        self.check(len(process.stdout) <= 4096 and len(process.stderr) <= 4096,
                   name + ":receiver-output-bound")
        receipt = strict(process.stdout)
        write_new(case / "receipt.json", receipt)
        self.check(trial_path.read_bytes() == before["trial"] and
                   journal_path.read_bytes() == before["journal"], name + ":read-only")
        self.check(receipt["outcome"] == "UnknownAttemptState", name + ":unknown")
        self.check(receipt["launch_authorized"] is False and
                   receipt["retry_authorized"] is False and
                   receipt["account_mutation_authorized"] is False,
                   name + ":no-continuation")
        self.check(receipt["native_authority"] is False and
                   receipt["free_authorized"] is False, name + ":no-native-authority")
        self.check(receipt["binding_fields_present"] is False, name + ":no-binding")
        self.check(type(receipt["work_units"]) is int and 0 < receipt["work_units"] <= 512,
                   name + ":work-bound")
        self.receipts.append({"case": name, "task": receipt["task"],
                              "outcome": receipt["outcome"],
                              "reason": receipt["reason"],
                              "amounts_equal": receipt["amounts_equal"],
                              "work_units": receipt["work_units"],
                              "receiver_seconds": elapsed})
        return receipt

    def run(self):
        self.output.mkdir(parents=True, exist_ok=False)
        contract = strict(CONTRACT.read_bytes())
        write_new(self.output / "contract.json", contract)
        self.check(digest(RECEIVER.read_bytes()) == contract["pins"]["receiver_sha256"],
                   "receiver-pin")
        self.check(contract["status"] == "FrozenBeforeExecution", "contract-frozen")

        # The actual interruption window: the cumulative account contains a
        # charge and the task journal is still empty. A second size is reuse.
        gap_alpha = self.receive("gap-alpha", trial([7]), journal("task-alpha", []))
        gap_beta = self.receive("gap-beta", trial([11]), journal("task-beta", []))
        self.check(gap_alpha["reason"] == "TrialChargeLacksTaskBinding" and
                   gap_alpha["task_reserved_units"] == 0, "gap-alpha-classification")
        self.check(gap_beta["reason"] == "TrialChargeLacksTaskBinding" and
                   gap_beta["task_reserved_units"] == 0, "gap-beta-reuse")

        # A tempting totals-only repair is unsafe: the same seven-unit charge
        # can appear to match two different task journals independently.
        shared_trial = trial([7])
        match_alpha = self.receive(
            "equal-alpha", shared_trial, journal("task-alpha", [(7, "launch-alpha")]))
        match_beta = self.receive(
            "equal-beta", shared_trial, journal("task-beta", [(7, "launch-beta")]))
        self.check(match_alpha["amounts_equal"] and match_beta["amounts_equal"],
                   "totals-only-double-match")
        self.check(match_alpha["task"] != match_beta["task"], "distinct-task-claims")
        unsafe_authorizations = sum(
            receipt["trial_charged_units"] == receipt["task_reserved_units"]
            for receipt in (match_alpha, match_beta)
        )
        self.check(unsafe_authorizations == 2, "unsafe-policy-double-authorizes")
        self.check(not match_alpha["launch_authorized"] and
                   not match_beta["launch_authorized"], "safe-policy-refuses-both")

        # Opposite mismatch: a task reservation without any trial charge also
        # cannot create permission.
        missing_charge = self.receive(
            "missing-charge", trial([]), journal("task-gamma", [(5, "launch-gamma")]))
        self.check(missing_charge["reason"] == "TaskReservationLacksTrialCharge" and
                   missing_charge["trial_charged_units"] == 0,
                   "missing-charge-classification")

        total_work = sum(item["work_units"] for item in self.receipts)
        self.check(total_work <= contract["limits"]["receiver_work_units"],
                   "cumulative-work-bound")
        self.check(len(self.receipts) <= contract["limits"]["receiver_processes"],
                   "process-count-bound")
        self.check(sum(path.stat().st_size for path in self.output.rglob("*") if path.is_file())
                   <= contract["limits"]["retained_output_bytes"], "retained-output-bound")

    def result(self):
        return {
            "profile": "adva.research.cumulative-charge-gap.v0",
            "status": "Passed" if self.failure is None else "Failed",
            "failure": self.failure,
            "main_at_start": "fec283277f3175be2a6ff69897d896526fc54fc9",
            "assertions": len(self.assertions),
            "assertion_labels": self.assertions,
            "receiver_processes": len(self.receipts),
            "target_processes": 0,
            "search_candidates": 0,
            "implementation_correction_replays": 0,
            "receiver_work_units": sum(item["work_units"] for item in self.receipts),
            "receiver_seconds": self.receiver_seconds,
            "wall_seconds": time.perf_counter() - self.started,
            "child_peak_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            "supervisor_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "receipts": self.receipts,
            "source_sha256": {
                str(path.relative_to(REPOSITORY)): digest(path.read_bytes())
                for path in (CONTRACT, Path(__file__), RECEIVER)
            },
            "result": "Current v0 charge bytes cannot bind one charge to one task; totals equality double-matches distinct tasks, so the receiver retains UnknownAttemptState and authorizes no launch.",
            "new_vocabulary": [],
            "native_authority": False,
            "limitations": "Finite project-original fixtures only. Abstract units are not CPU accounting. The receiver proves only that the v0 schema lacks a task binding; it does not model power loss, authenticate bytes, repair the gap, authorize retry, establish distributed atomicity, or grant native free.",
        }


def main(output):
    experiment = Experiment(output)
    signal.signal(signal.SIGALRM,
                  lambda *_: (_ for _ in ()).throw(TimeoutError("outer-wall-limit")))
    signal.setitimer(signal.ITIMER_REAL, 10)
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
                      if key not in ("assertion_labels", "receipts", "source_sha256")},
                     sort_keys=True))
    return 0 if experiment.failure is None else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    raise SystemExit(main(args.output.resolve()))
