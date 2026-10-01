#!/usr/bin/env python3
"""Exercise one-charge--one-task binding under a frozen finite budget.

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
RECEIVER = ROOT / "reconcile.py"


def digest_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def wire(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode()


def digest_value(value):
    return digest_bytes(wire(value))


def strict(raw):
    return json.loads(raw)


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(wire(value))


def task(task_name, purpose, units):
    return {
        "task": task_name,
        "purpose": purpose,
        "work_cap": units,
        "call_cap": 1,
        "correction_cap": 0,
    }


def account(charge_id, contract, units, phase="charged"):
    return {
        "profile": "cumulative-trial-v1",
        "charges": [{
            "charge_id": charge_id,
            "task_contract_sha256": digest_value(contract),
            "units": units,
            "phase": phase,
        }],
    }


def journal(charge_id, contract, units, phase="reserved", event_digest=None):
    return {
        "profile": "task-reservation-v1",
        "contract": contract,
        "events": [{
            "kind": "reserve",
            "id": 1,
            "charge_id": charge_id,
            "task_contract_sha256": event_digest or digest_value(contract),
            "units": units,
            "phase": phase,
        }],
    }


def v0_account(units):
    return {"profile": "cumulative-trial-v0", "charges": [units]}


def v0_journal(contract, units):
    return {
        "contract": {
            "task": contract["task"],
            "work_cap": contract["work_cap"],
            "call_cap": contract["call_cap"],
            "correction_cap": contract["correction_cap"],
        },
        "events": [{"kind": "reserve", "id": 1, "units": units,
                    "purpose": contract["purpose"]}],
    }


class Experiment:
    def __init__(self, output):
        self.output = output
        self.started = time.perf_counter()
        self.assertions = []
        self.receipts = []
        self.receiver_seconds = 0.0
        self.failure = None
        self.representation_cost = None

    def check(self, condition, label):
        if not condition:
            raise AssertionError(label)
        self.assertions.append(label)

    def receive(self, name, account_value, journal_value, expected, reason=None):
        case = self.output / "cases" / name
        account_path = case / "account.json"
        journal_path = case / "journal.json"
        write_new(account_path, account_value)
        write_new(journal_path, journal_value)
        before = {"account": account_path.read_bytes(),
                  "journal": journal_path.read_bytes()}
        started = time.perf_counter()
        process = subprocess.run(
            [sys.executable, str(RECEIVER), "--account", str(account_path),
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
        self.check(account_path.read_bytes() == before["account"] and
                   journal_path.read_bytes() == before["journal"], name + ":read-only")
        self.check(receipt["outcome"] == expected, name + ":classification")
        if reason is not None:
            self.check(receipt["reason"] == reason, name + ":reason")
        self.check(receipt["launch_authorized"] is False and
                   receipt["retry_authorized"] is False and
                   receipt["account_mutation_authorized"] is False,
                   name + ":no-continuation")
        self.check(receipt["native_authority"] is False and
                   receipt["free_authorized"] is False, name + ":no-native-authority")
        self.check(type(receipt["work_units"]) is int and
                   0 <= receipt["work_units"] <= 2048, name + ":work-bound")
        self.receipts.append({
            "case": name,
            "outcome": receipt["outcome"],
            "reason": receipt["reason"],
            "work_units": receipt["work_units"],
            "receiver_seconds": elapsed,
        })
        return receipt

    def run(self):
        self.output.mkdir(parents=True, exist_ok=False)
        contract = strict(CONTRACT.read_bytes())
        write_new(self.output / "contract.json", contract)
        self.check(digest_bytes(RECEIVER.read_bytes()) == contract["pins"]["receiver_sha256"],
                   "receiver-pin")
        self.check(contract["status"] == "FrozenBeforeExecution", "contract-frozen")

        alpha = task("task-alpha", "launch-alpha", 7)
        beta_same_units = task("task-beta", "launch-beta", 7)
        gamma = task("task-gamma", "launch-gamma", 11)
        alpha_id = "charge-alpha-0001"
        gamma_id = "charge-gamma-0001"
        alpha_account = account(alpha_id, alpha, 7)
        alpha_journal = journal(alpha_id, alpha, 7)

        exact_alpha = self.receive(
            "exact-alpha", alpha_account, alpha_journal, "BindingVerified",
            "ExactChargeReservationPair")
        exact_gamma = self.receive(
            "exact-gamma", account(gamma_id, gamma, 11), journal(gamma_id, gamma, 11),
            "BindingVerified", "ExactChargeReservationPair")
        replay_alpha = self.receive(
            "replay-alpha", alpha_account, alpha_journal, "BindingVerified",
            "ExactChargeReservationPair")
        self.check(exact_alpha == replay_alpha, "replay-byte-semantic-equality")
        self.check(exact_alpha["charge_id"] != exact_gamma["charge_id"] and
                   exact_alpha["task_contract_sha256"] != exact_gamma["task_contract_sha256"],
                   "new-instance-reuse")

        # The second task has the same seven-unit total and reuses alpha's ID,
        # but its recomputed task coordinate differs from the retained charge.
        reused = self.receive(
            "reuse-alpha-id-by-beta", alpha_account,
            journal(alpha_id, beta_same_units, 7), "InvalidContext",
            "AccountTaskMismatch")
        forged = self.receive(
            "forged-beta-event-digest", alpha_account,
            journal(alpha_id, beta_same_units, 7,
                    event_digest=digest_value(alpha)), "InvalidContext",
            "AccountTaskMismatch")
        self.check(reused["launch_authorized"] is False and
                   forged["launch_authorized"] is False, "second-task-reuse-refused")

        self.receive("wrong-units", alpha_account, journal(alpha_id, alpha, 6),
                     "InvalidContext", "ChargeUnitsMismatch")
        self.receive("wrong-phase", account(alpha_id, alpha, 7, "reserved"),
                     alpha_journal, "InvalidEvidence", "InvalidEvidence: ChargePhase")

        duplicate_account = account(alpha_id, alpha, 7)
        duplicate_account["charges"].append(dict(duplicate_account["charges"][0]))
        self.receive("duplicate-charge-id", duplicate_account, alpha_journal,
                     "InvalidEvidence", "InvalidEvidence: DuplicateChargeId")

        duplicate_journal = journal(alpha_id, alpha, 7)
        second_event = dict(duplicate_journal["events"][0])
        second_event["id"] = 2
        duplicate_journal["events"].append(second_event)
        self.receive("duplicate-reservation-id", alpha_account, duplicate_journal,
                     "InvalidEvidence",
                     "InvalidEvidence: DuplicateReservationChargeId")

        # Same unit budget and task pair as Research 0245: amount equality alone
        # says yes twice, whereas the v1 relation distinguishes the two tasks.
        baseline_authorizations = sum(
            sum(item["charges"]) == sum(event["units"] for event in candidate["events"])
            for item, candidate in (
                (v0_account(7), v0_journal(alpha, 7)),
                (v0_account(7), v0_journal(beta_same_units, 7)),
            )
        )
        self.check(baseline_authorizations == 2, "v0-total-double-match")
        self.check(exact_alpha["outcome"] == "BindingVerified" and
                   reused["outcome"] == "InvalidContext", "v1-distinguishes-tasks")

        old_bytes = len(wire(v0_account(7))) + len(wire(v0_journal(alpha, 7)))
        new_bytes = len(wire(alpha_account)) + len(wire(alpha_journal))
        self.representation_cost = {
            "v0_pair_bytes": old_bytes,
            "v1_pair_bytes": new_bytes,
            "added_canonical_bytes": new_bytes - old_bytes,
            "new_relation_field_occurrences": 6,
            "new_vocabulary_words": 0,
            "verification_work_units_exact_pair": exact_alpha["work_units"],
            "baseline_totals_only_authorizations": baseline_authorizations,
            "v1_bound_matches_for_same_charge_id_across_two_tasks": 1,
        }
        self.check(new_bytes > old_bytes, "representation-overhead-recorded")

        total_work = sum(item["work_units"] for item in self.receipts)
        self.check(total_work <= contract["limits"]["receiver_work_units"],
                   "cumulative-work-bound")
        self.check(len(self.receipts) <= contract["limits"]["receiver_processes"],
                   "process-count-bound")
        retained = sum(path.stat().st_size for path in self.output.rglob("*")
                       if path.is_file())
        self.check(retained <= contract["limits"]["retained_output_bytes"],
                   "retained-output-bound")

    def result(self):
        return {
            "profile": "adva.research.bound-charge-pair.v0",
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
            "representation_cost": self.representation_cost,
            "source_sha256": {
                str(path.relative_to(REPOSITORY)): digest_bytes(path.read_bytes())
                for path in (CONTRACT, Path(__file__), RECEIVER)
            },
            "result": "A v1 charge that binds its identifier, exact task-contract digest, units and directed phase verifies with its one reservation and rejects the same identifier when a different task presents it; verification still grants no launch.",
            "new_vocabulary": [],
            "native_authority": False,
            "limitations": "Finite project-original fixtures only. BindingVerified is a local receipt outcome, not a promoted word or formal accept. A digest binds canonical bytes, not human intent or authorship. Read-only replay is not replay prevention or exactly-once execution. Files and code are trusted; no power-loss, authentication, hostile process, distributed transaction, native free, M6 closure or universality result is supplied.",
        }


def main(output):
    experiment = Experiment(output)
    signal.signal(signal.SIGALRM,
                  lambda *_: (_ for _ in ()).throw(TimeoutError("outer-wall-limit")))
    signal.setitimer(signal.ITIMER_REAL, 12)
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
