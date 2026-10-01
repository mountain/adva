#!/usr/bin/env python3
"""Bind two real Node receives to the cumulative reservation prototype.

Project-original Codex (OpenAI), Unknown v0.3, through Mingli Yuan's
authorized account proxy. Account use is not review or a correctness claim.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parent.parent
SUPERVISOR_ROOT = REPOSITORY / "experiments" / "cumulative_budget_supervisor"
sys.path.insert(0, str(SUPERVISOR_ROOT))
from supervisor import BoundaryError, Supervisor, fields, strict, wire  # noqa: E402

ARCHIVE = REPOSITORY / "experiments" / "commit_snapshot_crosscheck" / "evidence" / "attempt-1.tar.gz"
RECEIVER = REPOSITORY / "experiments" / "commit_snapshot_node_receiver" / "calibrated" / "receive_pair.mjs"
CONTRACT = ROOT / "contract.json"
RESERVATION = 15361
TASK_CONTRACT = {
    "task": "receive-symmetric-empty-and-committed-v0",
    "work_cap": 30722,
    "call_cap": 2,
    "correction_cap": 0,
}
REPORT_FIELDS = (
    "profile", "outcome", "reason", "expected_request", "candidate",
    "stored_result", "allowance", "snapshot_state", "projection_sha256",
    "left_builder_source_sha256", "right_builder_source_sha256",
    "parent_checked", "debit_delta", "retry_authorized", "sqlite_opened",
    "ledger_path_accepted", "work_units", "meter", "wall_nanoseconds",
    "process_peak_rss_kib", "runtime", "native_authority",
    "close_authorized", "free_authorized",
)
SEMANTIC_FIELDS = (
    "outcome", "stored_result", "allowance", "snapshot_state",
    "projection_sha256", "left_builder_source_sha256",
    "right_builder_source_sha256", "parent_checked", "debit_delta",
    "retry_authorized", "sqlite_opened", "native_authority",
    "close_authorized", "free_authorized",
)
CASES = (
    ("symmetric-empty", "ProvenUncommittedLedger"),
    ("symmetric-committed", "StoredCommitted"),
)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


class TrialAccount:
    """Cumulative account importing the exact invalid-context attempt."""

    def __init__(self, path, prior_path, prior_pin, initialize=False):
        self.path = Path(path)
        self.prior_path = Path(prior_path)
        self.prior_pin = prior_pin
        if initialize:
            prior_raw = self.prior_path.read_bytes()
            if digest(prior_raw) != prior_pin:
                raise BoundaryError("PriorTrialPin")
            prior = strict(prior_raw)
            fields(prior, ("profile", "charges"))
            if prior != {"profile": "cumulative-node-trial-v0",
                          "charges": [RESERVATION, RESERVATION]}:
                raise BoundaryError("PriorTrialState")
            with self.path.open("xb") as stream:
                stream.write(wire({"profile": "cumulative-node-trial-v1",
                                   "prior_account_sha256": prior_pin,
                                   "prior_charges": prior["charges"],
                                   "replay_charges": []}))
        self.read()

    def read(self):
        raw = self.path.read_bytes()
        if len(raw) > 4096:
            raise BoundaryError("TrialSize")
        value = strict(raw)
        fields(value, ("profile", "prior_account_sha256", "prior_charges", "replay_charges"))
        if value["profile"] != "cumulative-node-trial-v1":
            raise BoundaryError("TrialProfile")
        if value["prior_account_sha256"] != self.prior_pin:
            raise BoundaryError("PriorTrialPin")
        if type(value["prior_charges"]) is not list or type(value["replay_charges"]) is not list:
            raise BoundaryError("TrialCharges")
        if value["prior_charges"] != [RESERVATION, RESERVATION]:
            raise BoundaryError("PriorTrialState")
        if any(type(n) is not int or n != RESERVATION for n in value["replay_charges"]):
            raise BoundaryError("TrialCharge")
        charges = value["prior_charges"] + value["replay_charges"]
        if len(charges) > 4 or sum(charges) > 61444:
            raise BoundaryError("TrialExhausted")
        if raw != wire(value):
            raise BoundaryError("TrialNoncanonical")
        return value

    def charge(self):
        value = self.read()
        charges = value["prior_charges"] + value["replay_charges"]
        if len(charges) + 1 > 4:
            raise BoundaryError("TrialCallsExhausted")
        if sum(charges) + RESERVATION > 61444:
            raise BoundaryError("TrialWorkExhausted")
        value["replay_charges"].append(RESERVATION)
        next_path = self.path.with_suffix(".next")
        with next_path.open("xb") as stream:
            stream.write(wire(value))
        next_path.replace(self.path)
        return self.read()


class Experiment:
    def __init__(self, output, trial_path, prior_trial_path, prior_attempt):
        self.output = output
        self.trial_path = trial_path
        self.prior_trial_path = prior_trial_path
        self.prior_attempt = prior_attempt
        self.started = time.perf_counter()
        self.assertions = []
        self.verifier_work = 0
        self.selected_bytes = 0
        self.node_seconds = 0.0
        self.serialization_seconds = 0.0
        self.runs = []
        self.failure = None

    def spend(self, units, label):
        if type(units) is not int or units < 0:
            raise AssertionError(label + ": verifier unit type")
        self.verifier_work += units
        if self.verifier_work > 100000:
            raise AssertionError(label + ": verifier-work-limit")

    def check(self, condition, label):
        self.spend(1, label)
        self.assertions.append(label)
        if not condition:
            raise AssertionError(label)

    def decoded(self, raw, label):
        value = strict(raw)
        nodes = 0
        stack = [value]
        while stack:
            item = stack.pop()
            nodes += 1
            if isinstance(item, dict):
                stack.extend(item.values())
            elif isinstance(item, list):
                stack.extend(item)
        self.spend(nodes, label + ":json-nodes")
        return value, nodes

    def save(self, path, value):
        started = time.perf_counter()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(wire(value))
        self.serialization_seconds += time.perf_counter() - started

    def read_member(self, archive, name, destination):
        member = archive.getmember(name)
        self.check(member.isfile() and not member.issym() and not member.islnk(), name + ":regular")
        self.check(0 <= member.size <= 262144, name + ":size")
        raw = archive.extractfile(member).read()
        self.check(len(raw) == member.size, name + ":length")
        self.selected_bytes += len(raw)
        self.check(self.selected_bytes <= 1048576, "selected-archive-byte-limit")
        self.spend((len(raw) + 63) // 64, name + ":read-blocks")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        return destination

    @staticmethod
    def semantic_view(report):
        return {key: report.get(key) for key in SEMANTIC_FIELDS}

    def invoke(self, label, wanted, request, left, right, python_report, supervisor, trial):
        # Trial charge and task reservation both precede process creation.
        trial.charge()
        reserved_state = supervisor.reserve(RESERVATION, label)
        attempt_id = reserved_state["calls"]
        folder = self.output / "runs" / label
        folder.mkdir(parents=True, exist_ok=True)
        command = ["node", "--max-old-space-size=32", str(RECEIVER),
                   "--request", str(request), "--left", str(left), "--right", str(right)]
        self.save(folder / "command.json", {"argv": command})
        started = time.perf_counter()
        raw = b""
        try:
            process = subprocess.run(command, capture_output=True, timeout=3)
            elapsed = time.perf_counter() - started
            self.node_seconds += elapsed
            raw = process.stdout
            (folder / "stdout.json").write_bytes(raw)
            (folder / "stderr.txt").write_bytes(process.stderr)
            if process.returncode != 0:
                raise BoundaryError("ChildExit")
            if len(raw) > 65536 or len(process.stderr) > 65536:
                raise BoundaryError("ChildOutput")
            report, report_nodes = self.decoded(raw, label + ":node-report")
            fields(report, REPORT_FIELDS)
            used = report["work_units"]
            if type(used) is not int or used < 0:
                raise BoundaryError("ReceiptWorkType")
            if used > RESERVATION:
                supervisor.append({"kind": "settle", "id": attempt_id,
                                   "outcome": "BudgetViolation", "reported_work": used})
                raise BoundaryError("BudgetViolation")
            # Observed means only that work accounting was readable. Semantic
            # acceptance remains a separate check below.
            settled = supervisor.append({"kind": "settle", "id": attempt_id,
                                         "outcome": "Observed", "reported_work": used})
        except (OSError, subprocess.TimeoutExpired, ValueError, BoundaryError) as error:
            if supervisor.state()["pending"] is not None:
                supervisor.append({"kind": "settle", "id": attempt_id,
                                   "outcome": "ImplementationFailure", "reported_work": None})
            raise BoundaryError(type(error).__name__ + ": " + str(error))

        self.check(report["profile"] == "adva.research.commit-snapshot-pair-receive-node.v1",
                   label + ":profile")
        self.check(report["outcome"] == wanted, label + ":outcome")
        self.check(report["reason"] == "distinct-builders-agree-on-pinned-ledger-projection",
                   label + ":reason")
        self.check(used == report["meter"]["value_nodes"] + report["meter"]["checks"],
                   label + ":meter-partition")
        self.check(used <= 15360 < RESERVATION, label + ":stopping-tick-reserved")
        self.check(report["meter"]["checks"] <= 1024, label + ":check-allowance")
        self.check(report["sqlite_opened"] is False and report["ledger_path_accepted"] is False,
                   label + ":no-ledger")
        self.check(report["parent_checked"] is False and report["debit_delta"] == 0 and
                   report["retry_authorized"] is False, label + ":no-parent-debit-retry")
        self.check(report["native_authority"] is False and report["close_authorized"] is False and
                   report["free_authorized"] is False, label + ":no-native-authority")

        for role, path in (("request", request), ("left", left), ("right", right)):
            _, nodes = self.decoded(path.read_bytes(), label + ":" + role)
            self.check(nodes == report["meter"]["decoded"][role]["value_nodes"],
                       label + ":" + role + ":value-node-match")
        expected, expected_nodes = self.decoded(python_report.read_bytes(), label + ":python-report")
        self.check(self.semantic_view(report) == self.semantic_view(expected),
                   label + ":cross-language-semantic-match")
        self.check(settled["reserved"] == attempt_id * RESERVATION and
                   settled["calls"] == attempt_id, label + ":cumulative-state")
        self.runs.append({
            "case": label,
            "outcome": report["outcome"],
            "reserved_units": RESERVATION,
            "reported_work": used,
            "unused_reserved_units": RESERVATION - used,
            "node_report_value_nodes": report_nodes,
            "python_report_value_nodes": expected_nodes,
            "wall_seconds": elapsed,
            "receiver_wall_nanoseconds": report["wall_nanoseconds"],
            "process_peak_rss_kib": report["process_peak_rss_kib"],
            "runtime": report["runtime"],
        })

    def run(self):
        self.output.mkdir(parents=True, exist_ok=False)
        contract_raw = CONTRACT.read_bytes()
        contract, _ = self.decoded(contract_raw, "contract")
        self.save(self.output / "contract.json", contract)
        self.check(digest(ARCHIVE.read_bytes()) == contract["pins"]["archive_sha256"], "archive-pin")
        self.check(digest(RECEIVER.read_bytes()) == contract["pins"]["node_receiver_sha256"], "receiver-pin")
        supervisor_source = SUPERVISOR_ROOT / "supervisor.py"
        self.check(digest(supervisor_source.read_bytes()) == contract["pins"]["supervisor_sha256"],
                   "supervisor-pin")
        source = RECEIVER.read_text()
        imports = {line.split("from ")[-1].strip().rstrip(";").strip('"')
                   for line in source.splitlines() if line.startswith("import ")}
        self.check(imports == {"node:crypto", "node:fs", "node:perf_hooks"},
                   "receiver-standard-library-only")
        self.check("node:sqlite" not in source and "child_process" not in source,
                   "receiver-no-sqlite-or-child")

        journal = self.output / "task-journal.json"
        supervisor = Supervisor(journal, TASK_CONTRACT, initialize=True)
        prior_execution = self.prior_attempt / "execution.json"
        prior_contract = self.prior_attempt / "executed-source" / "contract.json"
        prior_run = self.prior_attempt / "executed-source" / "run.py"
        self.check(digest(self.prior_trial_path.read_bytes()) ==
                   contract["pins"]["prior_trial_account_sha256"], "prior-trial-pin")
        self.check(digest(prior_execution.read_bytes()) ==
                   contract["pins"]["prior_execution_sha256"], "prior-execution-pin")
        self.check(digest(prior_contract.read_bytes()) ==
                   contract["pins"]["prior_contract_sha256"], "prior-contract-pin")
        self.check(digest(prior_run.read_bytes()) == contract["pins"]["prior_run_sha256"],
                   "prior-run-pin")
        prior_report, _ = self.decoded(prior_execution.read_bytes(), "prior-execution")
        prior_contract_value, _ = self.decoded(prior_contract.read_bytes(), "prior-contract")
        self.check(prior_report["status"] == "Passed" and prior_report["reserved_units"] == 30722 and
                   prior_report["node_processes"] == 2, "prior-observed-but-charged")
        self.check(prior_report["main_at_start"] == prior_contract_value["main_at_start"] and
                   prior_report["main_at_start"] != contract["main_at_start"],
                   "prior-invalid-context-coordinate")
        trial = TrialAccount(self.trial_path, self.prior_trial_path,
                             contract["pins"]["prior_trial_account_sha256"], initialize=True)
        inputs = self.output / "inputs"
        with tarfile.open(ARCHIVE, "r:gz") as archive:
            for label, wanted in CASES:
                request = self.read_member(archive, f"{label}-pair/pair-request.json",
                                           inputs / label / "request.json")
                left = self.read_member(archive, f"{label}.inherited.snapshot.json",
                                        inputs / label / "left.snapshot.json")
                right = self.read_member(archive, f"{label}.independent.snapshot.json",
                                         inputs / label / "right.snapshot.json")
                python_report = self.read_member(archive, f"{label}-pair/receive/stdout.json",
                                                 inputs / label / "python-report.json")
                self.invoke(label, wanted, request, left, right, python_report, supervisor, trial)

        final = supervisor.state()
        trial_final = trial.read()
        self.check(final["reserved"] == 30722 and final["calls"] == 2 and
                   final["remaining_work"] == 0 and final["remaining_calls"] == 0 and
                   final["stop"] is None, "final-task-account")
        self.check(final["reported_work"] == sum(run["reported_work"] for run in self.runs),
                   "reported-work-total")
        self.check(trial_final["prior_charges"] == [15361, 15361] and
                   trial_final["replay_charges"] == [15361, 15361], "final-trial-account")

        # Refusal controls operate after the two real calls. No trial charge or
        # process start is attempted, and both account files remain unchanged.
        before_journal = journal.read_bytes()
        before_trial = self.trial_path.read_bytes()
        try:
            supervisor.reserve(1, "third-launch")
            raise AssertionError("third-reservation-accepted")
        except BoundaryError as error:
            self.check("WorkExhausted" in str(error) or "CallsExhausted" in str(error),
                       "third-reservation-refused")
        self.check(journal.read_bytes() == before_journal and self.trial_path.read_bytes() == before_trial,
                   "refusal-preserves-accounts")
        try:
            trial.charge()
            raise AssertionError("fifth-trial-charge-accepted")
        except BoundaryError as error:
            self.check("TrialCallsExhausted" in str(error) or "TrialWorkExhausted" in str(error),
                       "fifth-trial-charge-refused")
        self.check(self.trial_path.read_bytes() == before_trial, "trial-refusal-preserves-account")
        changed = {**TASK_CONTRACT, "task": "changed-task"}
        try:
            Supervisor(journal, changed)
            raise AssertionError("changed-context-accepted")
        except BoundaryError as error:
            self.check("ContextChanged" in str(error), "changed-context-refused")
        self.check(journal.read_bytes() == before_journal, "changed-context-preserves-journal")

        events = strict(journal.read_bytes())["events"]
        reservations = [event["units"] for event in events if event["kind"] == "reserve"]
        self.check(reservations == [15361, 15361], "independent-reservation-sequence")
        self.check(sum(reservations) == 30722, "independent-reservation-total")
        self.save(self.output / "audit.json", {
            "task_contract": TASK_CONTRACT,
            "reservations": reservations,
            "task_state": final,
            "trial": trial_final,
            "semantic_cases": [{"case": run["case"], "outcome": run["outcome"]}
                               for run in self.runs],
        })

    def result(self):
        return {
            "profile": "adva.research.cumulative-node-receiver.v1",
            "status": "PassedAfterCorrectionReplay" if self.failure is None else "Failed",
            "failure": self.failure,
            "main_at_start": "19ac70e4886a3096bec00c3f4ba0008fbdc48c5d",
            "assertions": len(self.assertions),
            "assertion_labels": self.assertions,
            "node_processes": len(self.runs),
            "search_candidates": 0,
            "implementation_correction_replays": 1,
            "prior_invalid_context_reserved_units": 30722,
            "replay_reserved_units": sum(run["reserved_units"] for run in self.runs),
            "cumulative_reserved_units": 30722 + sum(run["reserved_units"] for run in self.runs),
            "reported_work_units": sum(run["reported_work"] for run in self.runs),
            "verifier_work_units": self.verifier_work,
            "selected_archive_bytes": self.selected_bytes,
            "wall_seconds": time.perf_counter() - self.started,
            "node_seconds": self.node_seconds,
            "serialization_seconds": self.serialization_seconds,
            "child_peak_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            "supervisor_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "runs": self.runs,
            "source_sha256": {
                str(path.relative_to(REPOSITORY)): digest(path.read_bytes())
                for path in (CONTRACT, Path(__file__), RECEIVER,
                             SUPERVISOR_ROOT / "supervisor.py")
            },
            "new_vocabulary": [],
            "native_authority": False,
            "limitations": "Reservations bound abstract receiver entitlement, not physical CPU or a hostile process. Python verification uses a separately bounded structural count. RSS values are per-category maxima, not concurrent total. Single local writer and intact files only; no authentication, power-loss or distributed guarantee. Research, coding and publication time are unmeasured.",
        }


def main(output, trial_path, prior_trial_path, prior_attempt):
    experiment = Experiment(output, trial_path, prior_trial_path, prior_attempt)
    signal.signal(signal.SIGALRM,
                  lambda *_: (_ for _ in ()).throw(TimeoutError("outer-wall-limit")))
    signal.setitimer(signal.ITIMER_REAL, 20)
    try:
        experiment.run()
        if sum(path.stat().st_size for path in output.rglob("*") if path.is_file()) > 2097152:
            raise AssertionError("retained-output-byte-limit")
    except Exception as error:
        experiment.failure = type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    result = experiment.result()
    if output.exists():
        (output / "execution.json").write_bytes(wire(result))
    print(canonical({key: value for key, value in result.items()
                     if key not in ("assertion_labels", "runs", "source_sha256")}))
    return 0 if experiment.failure is None else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--trial-account", required=True, type=Path)
    parser.add_argument("--prior-trial-account", required=True, type=Path)
    parser.add_argument("--prior-attempt", required=True, type=Path)
    args = parser.parse_args()
    raise SystemExit(main(args.output.resolve(), args.trial_account.resolve(),
                          args.prior_trial_account.resolve(), args.prior_attempt.resolve()))
