#!/usr/bin/env python3
"""Supervise the frozen Node.js receipt campaign over archived bytes."""
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
ARCHIVE = ROOT.parent / "commit_snapshot_crosscheck" / "evidence" / "attempt-1.tar.gz"
ARCHIVE_SHA = "f453b565f232dcac480afc8ab156e32e7683f4dff30667079c949d95b01d900e"
VALID = (
    ("symmetric-empty", "ProvenUncommittedLedger"),
    ("symmetric-committed", "StoredCommitted"),
    ("asymmetric-empty", "ProvenUncommittedLedger"),
    ("asymmetric-committed", "StoredCommitted"),
)
CONTROLS = (
    "projection-disagreement",
    "same-builder-provenance",
    "changed-candidate",
    "changed-expected",
    "wrong-right-pin",
    "missing-right",
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.write_bytes((canonical(value) + "\n").encode())


class Campaign:
    def __init__(self, output):
        self.output = output
        self.started = time.perf_counter()
        self.assertions = 0
        self.work = 0
        self.runs = []
        self.selected_bytes = 0
        self.phases = {"archive_read_seconds": 0.0, "node_seconds": 0.0,
                       "serialization_seconds": 0.0}

    def check(self, condition, label):
        self.assertions += 1
        if not condition:
            raise AssertionError(label)

    def save(self, path, value):
        started = time.perf_counter()
        path.parent.mkdir(parents=True, exist_ok=True)
        write_json(path, value)
        self.phases["serialization_seconds"] += time.perf_counter() - started

    def read_member(self, archive, name, destination):
        started = time.perf_counter()
        member = archive.getmember(name)
        self.check(member.isfile() and not member.issym() and not member.islnk(), "archive-regular-file")
        self.check(0 <= member.size <= 262144, "archive-member-size")
        body = archive.extractfile(member).read()
        self.check(len(body) == member.size, "archive-member-length")
        self.selected_bytes += len(body)
        self.check(self.selected_bytes <= 3145728, "selected-archive-byte-limit")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(body)
        self.phases["archive_read_seconds"] += time.perf_counter() - started
        return destination

    def invoke(self, label, request, left, right, wanted):
        self.check(len(self.runs) < 14, "child-process-limit")
        folder = self.output / "runs" / label
        folder.mkdir(parents=True, exist_ok=True)
        command = ["node", "--max-old-space-size=32", str(ROOT / "receive_pair.mjs"),
                   "--request", str(request), "--left", str(left), "--right", str(right)]
        self.save(folder / "command.json", {"argv": command})
        started = time.perf_counter()
        process = subprocess.run(command, capture_output=True, timeout=3)
        elapsed = time.perf_counter() - started
        self.phases["node_seconds"] += elapsed
        (folder / "stdout.json").write_bytes(process.stdout)
        (folder / "stderr.txt").write_bytes(process.stderr)
        self.check(process.returncode == 0,
                   (label, process.returncode, process.stderr.decode(errors="replace")))
        report = json.loads(process.stdout)
        self.check(report["outcome"] == wanted, (label, report["outcome"], report["reason"]))
        units = report["work_units"]
        self.check(type(units) is int and 0 <= units <= 10000, "work-per-call")
        self.work += units
        self.check(self.work <= 100000, "total-work")
        self.check(report["sqlite_opened"] is False and report["ledger_path_accepted"] is False,
                   "node-no-ledger")
        self.check(report["parent_checked"] is False and report["debit_delta"] == 0 and
                   report["retry_authorized"] is False, "no-parent-debit-retry")
        self.check(report["native_authority"] is False and report["close_authorized"] is False and
                   report["free_authorized"] is False, "no-native-authority")
        self.runs.append({"case": label, "outcome": report["outcome"],
                          "wall_seconds": elapsed,
                          "receiver_wall_nanoseconds": report["wall_nanoseconds"],
                          "work_units": units, "process_peak_rss_kib": report["process_peak_rss_kib"],
                          "reason": report["reason"]})
        return report


def semantic_view(report):
    return {key: report.get(key) for key in (
        "outcome", "stored_result", "allowance", "snapshot_state", "projection_sha256",
        "left_builder_source_sha256", "right_builder_source_sha256", "parent_checked",
        "debit_delta", "retry_authorized", "sqlite_opened", "native_authority",
        "close_authorized", "free_authorized")}


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    campaign = Campaign(output)
    failure = None
    correction_replays = 1
    signal.signal(signal.SIGALRM,
                  lambda *_: (_ for _ in ()).throw(TimeoutError("campaign-wall-limit")))
    signal.setitimer(signal.ITIMER_REAL, 30)
    try:
        contract = json.loads((ROOT / "contract.json").read_text())
        campaign.save(output / "contract.json", contract)
        campaign.check(digest(ARCHIVE.read_bytes()) == ARCHIVE_SHA, "ancestor-archive-pin")
        source = (ROOT / "receive_pair.mjs").read_text()
        campaign.check("node:sqlite" not in source and "child_process" not in source and
                       "python" not in " ".join(line for line in source.splitlines()
                                                if line.lstrip().startswith("import ")).lower(),
                       "node-source-import-boundary")
        campaign.check(set(line.split("from ")[-1].strip().rstrip(";").strip('"')
                           for line in source.splitlines() if line.startswith("import ")) ==
                       {"node:crypto", "node:fs", "node:perf_hooks"}, "node-standard-library-only")

        inputs = output / "inputs"
        with tarfile.open(ARCHIVE, "r:gz") as archive:
            extracted = {}

            def member(name):
                if name not in extracted:
                    target = inputs / name
                    extracted[name] = campaign.read_member(archive, name, target)
                return extracted[name]

            for label, wanted in VALID:
                request = member(f"{label}-pair/pair-request.json")
                left = member(f"{label}.inherited.snapshot.json")
                right = member(f"{label}.independent.snapshot.json")
                python_report_path = member(f"{label}-pair/receive/stdout.json")
                node_report = campaign.invoke(label, request, left, right, wanted)
                python_report = json.loads(python_report_path.read_text())
                campaign.check(semantic_view(node_report) == semantic_view(python_report),
                               f"{label}:cross-language-semantic-match")

            symmetric_left = member("symmetric-committed.inherited.snapshot.json")
            symmetric_right = member("symmetric-committed.independent.snapshot.json")
            paths = {
                "projection-disagreement": (symmetric_left,
                    member("projection-disagreement.snapshot.json")),
                "same-builder-provenance": (symmetric_left, symmetric_left),
                "changed-candidate": (symmetric_left, symmetric_right),
                "changed-expected": (symmetric_left, symmetric_right),
                "wrong-right-pin": (symmetric_left, symmetric_right),
                "missing-right": (symmetric_left, output / "inputs" / "intentionally-missing.json"),
            }
            for label in CONTROLS:
                request = member(f"{label}/pair-request.json")
                python_report_path = member(f"{label}/receive/stdout.json")
                report = campaign.invoke(label, request, *paths[label], "UnknownCommitState")
                python_report = json.loads(python_report_path.read_text())
                campaign.check(python_report["outcome"] == report["outcome"],
                               f"{label}:cross-language-refusal-match")

            base_request = member("symmetric-committed-pair/pair-request.json")
            raw = base_request.read_text()
            marker = '"profile":"adva.research.commit-snapshot-pair-receive.v0"'
            campaign.check(raw.count(marker) == 1, "unique-outer-profile-marker")
            duplicate = output / "generated" / "duplicate-key.json"
            duplicate.parent.mkdir(parents=True, exist_ok=True)
            duplicate.write_text(raw.replace(marker, marker + "," + marker, 1))
            campaign.invoke("duplicate-key", duplicate, symmetric_left, symmetric_right,
                            "UnknownCommitState")

            campaign.check('"grant":3' in raw, "integer-control-marker")
            fractional = output / "generated" / "fractional-number.json"
            fractional.write_text(raw.replace('"grant":3', '"grant":3.0', 1))
            campaign.invoke("fractional-number", fractional, symmetric_left, symmetric_right,
                            "UnknownCommitState")

            unsafe = output / "generated" / "unsafe-integer.json"
            unsafe.write_text(raw.replace('"grant":3', '"grant":9007199254740992', 1))
            campaign.invoke("unsafe-integer", unsafe, symmetric_left, symmetric_right,
                            "UnknownCommitState")

            noncanonical_snapshot = output / "generated" / "noncanonical.snapshot.json"
            noncanonical_snapshot.write_bytes(b" " + symmetric_left.read_bytes())
            repinned = json.loads(base_request.read_text())
            repinned["left_snapshot_sha256"] = digest(noncanonical_snapshot.read_bytes())
            repinned_request = output / "generated" / "repinned-noncanonical-request.json"
            write_json(repinned_request, repinned)
            campaign.invoke("repinned-noncanonical-snapshot", repinned_request,
                            noncanonical_snapshot, symmetric_right, "UnknownCommitState")

        campaign.check(len(campaign.runs) == 14, "complete-frozen-campaign")
        campaign.check(not any(path.suffix == ".sqlite3" for path in inputs.rglob("*")),
                       "no-sqlite-extracted")
        campaign.check(sum(path.stat().st_size for path in output.rglob("*") if path.is_file())
                       <= 5242880, "output-byte-limit")
    except Exception as error:
        failure = type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)

    sources = {}
    for name in ("contract.json", "receive_pair.mjs", "run.py", "pack.py"):
        path = ROOT / name
        if path.exists():
            sources[str(path.relative_to(ROOT.parent.parent))] = digest(path.read_bytes())
    result = {
        "profile": "adva.research.commit-snapshot-node-receiver.v0",
        "status": "Passed" if failure is None else "Failed",
        "failure": failure,
        "assertions": campaign.assertions,
        "processes": len(campaign.runs),
        "work_units": campaign.work,
        "search_candidates": 0,
        "correction_replays": correction_replays,
        "wall_seconds": time.perf_counter() - campaign.started,
        "phases": campaign.phases,
        "selected_archive_bytes": campaign.selected_bytes,
        "runs": campaign.runs,
        "source_sha256": sources,
        "python_supervisor_version": sys.version,
        "node_version": subprocess.run(["node", "--version"], capture_output=True,
                                       text=True, timeout=3).stdout.strip(),
        "child_peak_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        "supervisor_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "revised_vocabulary": ["commit-state-reconcile"],
        "native_authority": False,
        "measurement_limits": "RSS values are process-category maxima, not aggregate memory. The Node old-space flag is not a total process-memory limit. Research, coding and publication time are unmeasured.",
    }
    write_json(output / "execution.json", result)
    print(canonical({key: value for key, value in result.items()
                     if key not in ("runs", "source_sha256")}))
    return 0 if failure is None else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    raise SystemExit(main(parser.parse_args().output.resolve()))
