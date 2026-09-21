#!/usr/bin/env python3
"""Construct and check the frozen two-builder snapshot campaign."""
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
    "crosscheck_ancestor", ROOT.parent / "decision_ledger_contention" / "run.py")
ancestor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ancestor)
put = ancestor.put


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def projection(snapshot_path):
    value = json.loads(Path(snapshot_path).read_text())
    body = dict(value["body"])
    sources = body.pop("builder_source_sha256")
    raw = canonical(body).encode("utf-8")
    return raw, sources, hashlib.sha256(raw).hexdigest()


class Campaign:
    def __init__(self, output):
        self.output = output
        self.started = time.perf_counter()
        self.assertions = 0
        self.work = 0
        self.runs = []
        self.phases = {"construction_seconds": 0.0, "serialization_seconds": 0.0,
                       "inherited_builder_seconds": 0.0, "independent_builder_seconds": 0.0,
                       "pair_receiver_seconds": 0.0, "child_lifetime_seconds_sum": 0.0}

    def check(self, condition, label):
        self.assertions += 1
        if not condition:
            raise AssertionError(label)

    def save(self, path, value):
        started = time.perf_counter()
        put(path, value)
        self.phases["serialization_seconds"] += time.perf_counter() - started

    def invoke(self, name, script, args, wanted, ledger=None, phase=None):
        self.check(len(self.runs) < 24, "child-count-limit")
        folder = self.output / name
        folder.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, "-B", "-S", str(script), *args]
        self.save(folder / "command.json", {"argv": command})
        before = file_sha(ledger) if ledger is not None and ledger.is_file() else None
        started = time.perf_counter()
        process = subprocess.run(command, capture_output=True, timeout=3,
                                 preexec_fn=ancestor.producer.limits)
        elapsed = time.perf_counter() - started
        self.phases["child_lifetime_seconds_sum"] += elapsed
        if phase is not None:
            self.phases[phase] += elapsed
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
        after = file_sha(ledger) if ledger is not None and ledger.is_file() else None
        if ledger is not None and script in (ROOT / "snapshot_independent.py",
                                             ROOT.parent / "commit_snapshot_receipt" / "snapshot.py"):
            self.check(before == after, "builder-read-only")
        if script == ROOT / "receive_pair.py":
            self.check(report["sqlite_opened"] is False, "pair-no-sqlite")
            self.check(report["parent_checked"] is False and report["debit_delta"] == 0 and
                       report["retry_authorized"] is False, "no-check-debit-or-retry")
        self.runs.append({"case": name, "outcome": report["outcome"],
                          "wall_seconds": elapsed, "work_units": units,
                          "ledger_sha256_before": before, "ledger_sha256_after": after})
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

    def build(self, label, script, expected, candidate, ledger, snapshot, phase):
        folder = self.output / label
        folder.mkdir(parents=True, exist_ok=True)
        request = {"profile": "adva.research.commit-snapshot-builder.v0",
                   "expected_request": expected, "candidate": candidate}
        request_path = folder / "snapshot-request.json"
        self.save(request_path, request)
        return self.invoke(label + "/build", script,
                           ["--request", str(request_path), "--ledger", str(ledger),
                            "--output", str(snapshot)], "SnapshotCreated", ledger, phase)

    def receive(self, label, expected, candidate, left, right, left_pin, right_pin, wanted):
        folder = self.output / label
        folder.mkdir(parents=True, exist_ok=True)
        request = {"profile": "adva.research.commit-snapshot-pair-receive.v0",
                   "expected_request": expected, "candidate": candidate,
                   "left_snapshot_sha256": left_pin, "right_snapshot_sha256": right_pin}
        request_path = folder / "pair-request.json"
        self.save(request_path, request)
        return self.invoke(label + "/receive", ROOT / "receive_pair.py",
                           ["--request", str(request_path), "--left", str(left),
                            "--right", str(right)], wanted, None, "pair_receiver_seconds")


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
        pair_tree = ast.parse((ROOT / "receive_pair.py").read_text())
        imports = {node.names[0].name for node in ast.walk(pair_tree) if isinstance(node, ast.Import)}
        imports.update(node.module for node in ast.walk(pair_tree) if isinstance(node, ast.ImportFrom))
        campaign.check("sqlite3" not in imports, "pair-receiver-must-not-import-sqlite3")
        independent_tree = ast.parse((ROOT / "snapshot_independent.py").read_text())
        independent_imports = {node.names[0].name for node in ast.walk(independent_tree)
                               if isinstance(node, ast.Import)}
        independent_imports.update(node.module for node in ast.walk(independent_tree)
                                   if isinstance(node, ast.ImportFrom))
        campaign.check("importlib" not in independent_imports,
                       "independent-builder-no-ancestor-import")

        started = time.perf_counter()
        families = list(ancestor.producer.families())
        campaign.phases["construction_seconds"] += time.perf_counter() - started
        fixtures = {}
        for index, label in ((0, "symmetric"), (1, "asymmetric")):
            _, expected = families[index]
            candidate = ancestor.producer.envelope(expected)
            candidate["profile"] = ancestor.PROFILE
            fixtures[label] = {}
            for state in ("empty", "committed"):
                ledger = output / f"{label}-{state}.sqlite3"
                campaign.init(f"{label}-{state}-fixture", expected, ledger)
                submitted = None
                if state == "committed":
                    submitted = campaign.submit(f"{label}-{state}-fixture", expected, candidate, ledger)
                left = output / f"{label}-{state}.inherited.snapshot.json"
                right = output / f"{label}-{state}.independent.snapshot.json"
                left_report = campaign.build(f"{label}-{state}-inherited",
                                             ROOT.parent / "commit_snapshot_receipt" / "snapshot.py",
                                             expected, candidate, ledger, left, "inherited_builder_seconds")
                right_report = campaign.build(f"{label}-{state}-independent",
                                              ROOT / "snapshot_independent.py", expected, candidate,
                                              ledger, right, "independent_builder_seconds")
                left_projection, left_sources, left_projection_sha = projection(left)
                right_projection, right_sources, right_projection_sha = projection(right)
                campaign.check(left_projection == right_projection, "valid-projection-byte-agreement")
                campaign.check(left_projection_sha == right_projection_sha == right_report["projection_sha256"],
                               "valid-projection-digest-agreement")
                campaign.check(canonical(left_sources) != canonical(right_sources),
                               "valid-builder-provenance-distinct")
                wanted = "StoredCommitted" if state == "committed" else "ProvenUncommittedLedger"
                reply = campaign.receive(f"{label}-{state}-pair", expected, candidate, left, right,
                                         left_report["snapshot_file_sha256"],
                                         right_report["snapshot_file_sha256"], wanted)
                campaign.check(reply["projection_sha256"] == left_projection_sha,
                               "receiver-projection-digest")
                if state == "committed":
                    campaign.check(reply["stored_result"] == submitted["stored_result"],
                                   "stored-result-recovery")
                else:
                    campaign.check(reply["allowance"] == {"grant": 3, "spent": 2, "remaining": 1},
                                   "empty-allowance")
                fixtures[label][state] = (expected, candidate, left, right, left_report, right_report)

        expected, candidate, left, right, left_report, right_report = fixtures["symmetric"]["committed"]
        disagree = output / "projection-disagreement.snapshot.json"
        value = json.loads(right.read_text())
        value["body"]["source_ledger_sha256"] = "0" * 64
        value["body_sha256"] = hashlib.sha256(canonical(value["body"]).encode()).hexdigest()
        write_canonical(disagree, value)
        campaign.receive("projection-disagreement", expected, candidate, left, disagree,
                         left_report["snapshot_file_sha256"], file_sha(disagree), "UnknownCommitState")
        campaign.receive("same-builder-provenance", expected, candidate, left, left,
                         left_report["snapshot_file_sha256"], left_report["snapshot_file_sha256"],
                         "UnknownCommitState")
        changed_candidate = copy.deepcopy(candidate)
        changed_candidate["checkpoint_receipt"]["checkpoint"]["pending_step"]["step"] = "different-query"
        campaign.receive("changed-candidate", expected, changed_candidate, left, right,
                         left_report["snapshot_file_sha256"], right_report["snapshot_file_sha256"],
                         "UnknownCommitState")
        changed_expected = copy.deepcopy(expected)
        changed_expected["prefix_request"]["source"]["history"][0] = "different-origin"
        campaign.receive("changed-expected", changed_expected, candidate, left, right,
                         left_report["snapshot_file_sha256"], right_report["snapshot_file_sha256"],
                         "UnknownCommitState")
        campaign.receive("wrong-right-pin", expected, candidate, left, right,
                         left_report["snapshot_file_sha256"], "0" * 64, "UnknownCommitState")
        campaign.receive("missing-right", expected, candidate, left, output / "missing.snapshot.json",
                         left_report["snapshot_file_sha256"], right_report["snapshot_file_sha256"],
                         "UnknownCommitState")
        campaign.check(len(campaign.runs) == 24, "complete-frozen-processes")
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)

    sources = {}
    for directory in ("commit_snapshot_crosscheck", "commit_snapshot_receipt",
                      "commit_state_reconcile", "decision_ledger_contention", "decision_ledger"):
        for filename in ("receive_pair.py", "receive.py", "snapshot.py", "snapshot_independent.py",
                         "run.py", "contract.json"):
            path = ROOT.parent / directory / filename
            if path.exists():
                sources[str(path.relative_to(ROOT.parent.parent))] = file_sha(path)
    result = {"profile": "adva.research.commit-snapshot-crosscheck.v0",
              "status": "Passed" if failure is None else "Failed", "failure": failure,
              "assertions": campaign.assertions, "processes": len(campaign.runs),
              "work_units": campaign.work, "search_candidates": 0,
              "wall_seconds": time.perf_counter() - campaign.started,
              "phases": campaign.phases, "runs": campaign.runs,
              "source_sha256": sources, "python_version": sys.version,
              "child_peak_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
              "supervisor_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "revised_vocabulary": ["commit-state-reconcile"], "native_authority": False,
              "measurement_limits": "RSS values are category maxima, not aggregate memory. Research and publication time are unmeasured."}
    put(output / "execution.json", result)
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ("runs", "source_sha256")}, sort_keys=True))
    return 0 if failure is None else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    raise SystemExit(main(parser.parse_args().output.resolve()))
