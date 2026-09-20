#!/usr/bin/env python3
"""Construct and check the frozen commit-snapshot receipt campaign."""
import argparse
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "snapshot_ancestor", ROOT.parent / "decision_ledger_contention" / "run.py")
ancestor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ancestor)
put = ancestor.put


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Campaign:
    def __init__(self, output):
        self.output = output
        self.started = time.perf_counter()
        self.assertions = 0
        self.work = 0
        self.runs = []
        self.phases = {
            "construction_seconds": 0.0,
            "serialization_seconds": 0.0,
            "snapshot_seconds": 0.0,
            "verification_seconds": 0.0,
            "child_lifetime_seconds_sum": 0.0,
        }

    def check(self, condition, label):
        self.assertions += 1
        if not condition:
            raise AssertionError(label)

    def save(self, path, value):
        started = time.perf_counter()
        put(path, value)
        self.phases["serialization_seconds"] += time.perf_counter() - started

    def invoke(self, name, script, args, wanted, ledger=None, category=None):
        self.check(len(self.runs) < 20, "child-count-limit")
        folder = self.output / name
        folder.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, "-B", "-S", str(script), *args]
        self.save(folder / "command.json", {"argv": command})
        before = sha(ledger) if ledger is not None and ledger.is_file() else None
        started = time.perf_counter()
        process = subprocess.run(command, capture_output=True, timeout=3,
                                 preexec_fn=ancestor.producer.limits)
        elapsed = time.perf_counter() - started
        self.phases["child_lifetime_seconds_sum"] += elapsed
        if category is not None:
            self.phases[category] += elapsed
        (folder / "stdout.json").write_bytes(process.stdout)
        (folder / "stderr.txt").write_bytes(process.stderr)
        self.check(process.returncode == 0,
                   (name, process.returncode, process.stderr.decode(errors="replace")))
        report = json.loads(process.stdout)
        self.check(report["outcome"] == wanted, (name, report))
        units = report.get("work_units")
        self.check(type(units) is int and 0 <= units <= 10000, "work-per-call")
        self.work += units
        self.check(self.work <= 100000, "total-work")
        after = sha(ledger) if ledger is not None and ledger.is_file() else None
        if ledger is not None and script == ROOT / "snapshot.py":
            self.check(before == after, "snapshot-builder-read-only")
        if script == ROOT / "receive.py":
            self.check(report["sqlite_opened"] is False, "independent-no-sqlite")
            self.check(report["parent_checked"] is False and report["debit_delta"] == 0 and
                       report["retry_authorized"] is False, "no-check-debit-or-retry")
        self.runs.append({
            "case": name,
            "outcome": report["outcome"],
            "wall_seconds": elapsed,
            "work_units": units,
            "ledger_sha256_before": before,
            "ledger_sha256_after": after,
        })
        return report

    def init(self, label, expected, ledger):
        folder = self.output / label
        folder.mkdir(parents=True, exist_ok=True)
        expected_path = folder / "expected.json"
        self.save(expected_path, expected)
        return self.invoke(label + "/init", ROOT.parent / "decision_ledger_contention" / "receive.py",
                           ["init", "--expected", str(expected_path), "--ledger", str(ledger)],
                           "InitializedLedger", ledger)

    def submit(self, label, expected, candidate, ledger):
        folder = self.output / label
        folder.mkdir(parents=True, exist_ok=True)
        expected_path, candidate_path = folder / "expected.json", folder / "candidate.json"
        self.save(expected_path, expected)
        self.save(candidate_path, candidate)
        return self.invoke(label + "/submit", ROOT.parent / "decision_ledger_contention" / "receive.py",
                           ["submit", "--expected", str(expected_path), "--ledger", str(ledger),
                            "--candidate", str(candidate_path)], "CommittedContinuation", ledger)

    def snapshot(self, label, expected, candidate, ledger, snapshot):
        folder = self.output / label
        folder.mkdir(parents=True, exist_ok=True)
        request = {"profile": "adva.research.commit-snapshot-builder.v0",
                   "expected_request": expected, "candidate": candidate}
        request_path = folder / "snapshot-request.json"
        self.save(request_path, request)
        return self.invoke(label + "/snapshot", ROOT / "snapshot.py",
                           ["--request", str(request_path), "--ledger", str(ledger),
                            "--output", str(snapshot)], "SnapshotCreated", ledger, "snapshot_seconds")

    def receive(self, label, expected, candidate, snapshot, pin, wanted):
        folder = self.output / label
        folder.mkdir(parents=True, exist_ok=True)
        request = {"profile": "adva.research.commit-snapshot-receive.v0",
                   "expected_request": expected, "candidate": candidate,
                   "snapshot_file_sha256": pin}
        request_path = folder / "receive-request.json"
        self.save(request_path, request)
        return self.invoke(label + "/receive", ROOT / "receive.py",
                           ["--request", str(request_path), "--snapshot", str(snapshot)],
                           wanted, None, "verification_seconds")


def write_canonical(path, value):
    Path(path).write_bytes((canonical(value) + "\n").encode("utf-8"))


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    campaign = Campaign(output)
    failure = None
    signal.signal(signal.SIGALRM,
                  lambda *_: (_ for _ in ()).throw(TimeoutError("campaign-wall-limit")))
    signal.setitimer(signal.ITIMER_REAL, 30)
    try:
        campaign.save(output / "contract.json", json.loads((ROOT / "contract.json").read_text()))
        source_tree = ast.parse((ROOT / "receive.py").read_text())
        imports = {node.names[0].name for node in ast.walk(source_tree)
                   if isinstance(node, ast.Import)}
        imports.update(node.module for node in ast.walk(source_tree)
                       if isinstance(node, ast.ImportFrom))
        campaign.check("sqlite3" not in imports, "receiver-source-must-not-import-sqlite3")

        started = time.perf_counter()
        families = list(ancestor.producer.families())
        campaign.phases["construction_seconds"] += time.perf_counter() - started
        fixtures = {}
        for index, label in ((0, "symmetric"), (1, "asymmetric")):
            _, expected = families[index]
            candidate = ancestor.producer.envelope(expected)
            candidate["profile"] = ancestor.PROFILE
            empty = output / (label + "-empty.sqlite3")
            committed = output / (label + "-committed.sqlite3")
            campaign.init(label + "-empty-build", expected, empty)
            campaign.init(label + "-committed-build", expected, committed)
            committed_reply = campaign.submit(label + "-committed-build", expected, candidate, committed)
            empty_snapshot = output / (label + "-empty.snapshot.json")
            committed_snapshot = output / (label + "-committed.snapshot.json")
            empty_build = campaign.snapshot(label + "-empty", expected, candidate, empty, empty_snapshot)
            committed_build = campaign.snapshot(label + "-committed", expected, candidate,
                                                committed, committed_snapshot)
            fixtures[label] = (expected, candidate, empty_snapshot, committed_snapshot,
                               empty_build, committed_build, committed_reply)
            empty_reply = campaign.receive(label + "-empty", expected, candidate, empty_snapshot,
                                           empty_build["snapshot_file_sha256"],
                                           "ProvenUncommittedLedger")
            campaign.check(empty_reply["allowance"] == {"grant": 3, "spent": 2, "remaining": 1},
                           "empty-allowance")
            stored_reply = campaign.receive(label + "-committed", expected, candidate,
                                            committed_snapshot,
                                            committed_build["snapshot_file_sha256"],
                                            "StoredCommitted")
            campaign.check(stored_reply["stored_result"] == committed_reply["stored_result"],
                           "stored-result-recovery")

        expected, candidate, _, committed_snapshot, _, committed_build, _ = fixtures["symmetric"]
        changed_candidate = copy.deepcopy(candidate)
        changed_candidate["checkpoint_receipt"]["checkpoint"]["pending_step"]["step"] = "different-query"
        campaign.receive("changed-candidate", expected, changed_candidate, committed_snapshot,
                         committed_build["snapshot_file_sha256"], "UnknownCommitState")
        changed_expected = copy.deepcopy(expected)
        changed_expected["prefix_request"]["source"]["history"][0] = "different-origin"
        campaign.receive("changed-expected", changed_expected, candidate, committed_snapshot,
                         committed_build["snapshot_file_sha256"], "UnknownCommitState")

        tampered = output / "tampered.snapshot.json"
        value = json.loads(committed_snapshot.read_text())
        value["body"]["source_ledger_sha256"] = "0" * 64
        value["body_sha256"] = hashlib.sha256(canonical(value["body"]).encode()).hexdigest()
        write_canonical(tampered, value)
        campaign.receive("tampered-old-pin", expected, candidate, tampered,
                         committed_build["snapshot_file_sha256"], "UnknownCommitState")

        malformed = output / "malformed.snapshot.json"
        body = {}
        write_canonical(malformed, {"profile": "adva.research.commit-snapshot.v0", "version": 0,
                                    "body": body,
                                    "body_sha256": hashlib.sha256(canonical(body).encode()).hexdigest()})
        campaign.receive("malformed-own-pin", expected, candidate, malformed, sha(malformed),
                         "UnknownCommitState")

        wrong_profile = output / "wrong-profile.snapshot.json"
        value = json.loads(committed_snapshot.read_text())
        value["profile"] = "adva.research.commit-snapshot.wrong"
        write_canonical(wrong_profile, value)
        campaign.receive("wrong-profile-own-pin", expected, candidate, wrong_profile,
                         sha(wrong_profile), "UnknownCommitState")
        campaign.receive("missing-snapshot", expected, candidate, output / "missing.snapshot.json",
                         committed_build["snapshot_file_sha256"], "UnknownCommitState")
        campaign.check(len(campaign.runs) == 20, "complete-frozen-processes")
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)

    sources = {}
    for directory in ("commit_snapshot_receipt", "commit_state_reconcile", "decision_ledger_contention",
                      "decision_ledger", "decision_checkpoint", "decision_scale_composition",
                      "decision_scale", "finite_decision", "probability_receipt"):
        for filename in ("receive.py", "snapshot.py", "run.py", "contract.json"):
            path = ROOT.parent / directory / filename
            if path.exists():
                sources[str(path.relative_to(ROOT.parent.parent))] = sha(path)
    result = {
        "profile": "adva.research.commit-snapshot-receipt.v0",
        "status": "Passed" if failure is None else "Failed",
        "failure": failure,
        "assertions": campaign.assertions,
        "processes": len(campaign.runs),
        "work_units": campaign.work,
        "search_candidates": 0,
        "wall_seconds": time.perf_counter() - campaign.started,
        "phases": campaign.phases,
        "runs": campaign.runs,
        "source_sha256": sources,
        "python_version": sys.version,
        "child_peak_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        "supervisor_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "revised_vocabulary": ["commit-state-reconcile"],
        "native_authority": False,
        "measurement_limits": "RSS values are category maxima, not aggregate memory. Research and publication time are unmeasured.",
    }
    put(output / "execution.json", result)
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ("runs", "source_sha256")}, sort_keys=True))
    return 0 if failure is None else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    raise SystemExit(main(parser.parse_args().output.resolve()))
