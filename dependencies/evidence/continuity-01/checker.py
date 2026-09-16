#!/usr/bin/env python3
"""Receive a pinned external machine without building the knowledge workspace.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy.
This finite engineering check neither imports documentary entries as knowledge
nor changes the authority of retained research evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "dependencies/adva-machine.lock.json"


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def git(root, *args):
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True,
        stderr=subprocess.PIPE, timeout=20,
    ).strip()


def checkout(root, revision):
    require(git(root, "rev-parse", "--show-toplevel") == str(root.resolve()),
            "dependency must be an independent checkout")
    require(git(root, "rev-parse", "HEAD") == revision, "dependency revision differs from lock")
    require(not git(root, "status", "--porcelain", "--untracked-files=all"),
            "dependency checkout contains changes")


def pins(root, files):
    for name, expected in files.items():
        require(sha(root / name) == expected, "pinned input differs: " + name)


def native_observer(report):
    # Preserve the complete program, compilation/history, certificates, values,
    # rejection and resource account. Only wall-clock measurements vary by host.
    require("phase_seconds" in report, "native report lacks separate timing")
    return {key: value for key, value in report.items() if key != "phase_seconds"}


class Commands:
    def __init__(self, evidence):
        self.evidence = evidence
        self.records = []

    def run(self, label, command, cwd, *, timeout=45, codes=(0,)):
        command = [str(part) for part in command]
        record = {"label": label, "argv": command, "cwd": str(cwd),
                  "timeout_seconds": timeout, "returncode": None}
        self.records.append(record)
        started = time.monotonic()
        logs = self.evidence / "logs"
        logs.mkdir(exist_ok=True)
        try:
            with (logs / (label + ".stdout")).open("xb") as out, \
                    (logs / (label + ".stderr")).open("xb") as err:
                result = subprocess.run(command, cwd=cwd, stdout=out, stderr=err,
                                        timeout=timeout, check=False)
                record["returncode"] = result.returncode
        finally:
            record["wall_seconds"] = time.monotonic() - started
        require(result.returncode in codes, f"{label} failed; see retained stderr")
        return result.returncode


def receive_dependencies(machine, lock, commands):
    checkout(machine, lock["machine"]["revision"])
    pins(machine, {"spec/catalog.json": lock["machine"]["spec_catalog_sha256"],
                   "toolchain/library.lock.json": lock["machine"]["library_lock_sha256"]})
    library = machine / "adva-library"
    checkout(library, lock["library"]["revision"])
    pins(library, {lock["library"]["subject"]: lock["library"]["subject_sha256"]})
    machine_lock = read(machine / "toolchain/library.lock.json")
    require(machine_lock["revision"] == lock["library"]["revision"],
            "machine and knowledge library locks disagree")
    # This is an integrity check, not loading the catalog as native knowledge.
    pins(library, machine_lock["files"])
    catalog = read(machine / "spec/catalog.json")
    pins(machine, catalog["files"])
    return library


def check(machine, output):
    output.mkdir(parents=True, exist_ok=False)
    evidence = output / "evidence"
    evidence.mkdir()
    commands = Commands(evidence)
    report = {"schema": "adva.knowledge.dependency-continuity.v0", "status": "Error",
              "scope": "two existing arithmetic fixtures; no general migration or new theorem",
              "commands": commands.records, "checks": []}
    try:
        lock = read(LOCK)
        require(lock["schema"] == "adva.knowledge.machine-dependency.v0", "unknown lock schema")
        shutil.copyfile(LOCK, evidence / "dependency.lock.json")
        shutil.copyfile(Path(__file__), evidence / "checker.py")
        pins(ROOT, lock["knowledge_inputs"])
        report["knowledge"] = {"base_commit": git(ROOT, "rev-parse", "HEAD"),
                               "checker_sha256": sha(Path(__file__)),
                               "lock_sha256": sha(LOCK)}
        if machine is None:
            machine = output / "dependencies/machine"
            machine.mkdir(parents=True)
            commands.run("git-init", ["git", "init", machine], output)
            commands.run("git-fetch", ["git", "fetch", "--depth=1",
                         lock["machine"]["repository"], lock["machine"]["revision"]], machine,
                         timeout=180)
            commands.run("git-checkout", ["git", "checkout", "--detach", "FETCH_HEAD"], machine)
            commands.run("library-fetch", ["git", "submodule", "update", "--init",
                         "--depth=1", "--", "adva-library"], machine, timeout=180)
        machine = machine.resolve()
        library = receive_dependencies(machine, lock, commands)
        report["dependencies"] = {"machine_revision": lock["machine"]["revision"],
                                  "library_revision": lock["library"]["revision"]}
        require(git(ROOT, "ls-tree", "HEAD", "adva-library").split()[2]
                == lock["library"]["revision"], "knowledge gitlink differs from library lock")
        # A new target directory prevents reuse of an unbound prebuilt binary.
        # No cargo command or package import is run in the knowledge workspace.
        commands.run("rust-version", ["rustc", "-Vv"], machine)
        commands.run("cargo-version", ["cargo", "-V"], machine)
        commands.run("python-version", [sys.executable, "--version"], machine)
        commands.run("build", ["cargo", "build", "--locked", "--release", "-p",
                     "adva-witness", "--bin", "adva", "--target-dir", output / "build"],
                     machine, timeout=lock["limits"]["build_seconds"])
        binary = output / "build/release/adva"
        report["build"] = {"binary_sha256": sha(binary),
                           "source_revision": lock["machine"]["revision"],
                           "cargo_lock_sha256": sha(machine / "Cargo.lock"),
                           "provenance": "locally built from checked checkout; not an authenticated build attestation"}
        commands.run("doctor", [sys.executable, machine / "adva-machine", "doctor",
                     "--binary", binary, "--library", library], machine)
        inputs = evidence / "inputs"
        inputs.mkdir()
        subject = inputs / "library-arithmetic.adva"
        shutil.copyfile(library / lock["library"]["subject"], subject)
        require(subject.read_bytes() == (ROOT / "programs/native-run/arithmetic.adva").read_bytes(),
                "library and knowledge subjects differ")
        baseline = inputs / "historical-arithmetic-result.adva"
        shutil.copyfile(ROOT / "docs/research/0140-native-run-evidence/arithmetic-result.adva", baseline)
        result = evidence / "library-arithmetic-result.adva"
        commands.run("library-arithmetic", [binary, "run", subject, "--output", result], machine)
        require(native_observer(read(result)) == native_observer(read(baseline)),
                "native execution differs from retained history/certificates/resource account")
        report["checks"].append({"name": "library-arithmetic-history", "status": "Passed",
                                 "observer": lock["observer"]["native_run"]})
        # The program comes from knowledge; the interpreter service comes from
        # the pinned machine. These profiles do not reinterpret PSC0 as exact i64.
        program = read(ROOT / "programs/bounded-interpreter/interpreter.adva")
        data = read(ROOT / "programs/bounded-interpreter/input.json")
        cases = [
            ("returned", data, 2048, {"kind": "Returned", "value": {"kind": "integer", "value": 14}}, 134),
            ("rejected", {"kind": "node", "tag": 99, "fields": []}, 2048,
             {"kind": "Rejected", "stage": "execution", "reason": "unsupported object tag"}, None),
            ("suspended", data, 17, {"kind": "Unknown", "reason": "Suspended"}, 17),
        ]
        require(len(cases) == lock["limits"]["case_count"], "case budget differs")
        for name, value, quantum, expected, spent in cases:
            request = inputs / (name + ".request.json")
            save(request, {"schema": "adva.machine.request.v0", "profile": "data-machine-v0",
                           "program": program, "input": value, "fuel": 2048, "quantum": quantum})
            destination = evidence / name
            code = commands.run(name, [sys.executable, machine / "adva-machine", "run", request,
                                "--engine", "rust", "--binary", binary, "--output", destination],
                                machine, timeout=lock["limits"]["command_seconds"],
                                codes=(2,) if name == "rejected" else (0,))
            received = read(destination / "report.json")
            require(received["outcome"] == expected, name + " outcome changed")
            require(received["binary_sha256"] == report["build"]["binary_sha256"], "binary binding differs")
            require(received["verification"]["status"] == "NativeReplayPassed", name + " not replayed")
            if spent is not None:
                require(received["execution"]["steps"] == spent, name + " instruction account differs")
            report["checks"].append({"name": name, "status": "Passed", "returncode": code,
                                     "outcome": expected, "verification": received["verification"]["status"],
                                     "steps": received["execution"]["steps"]})
        # Check dependencies and binary again before publishing a successful run.
        receive_dependencies(machine, lock, commands)
        pins(ROOT, lock["knowledge_inputs"])
        require(sha(binary) == report["build"]["binary_sha256"], "executable changed during run")
        report["status"] = "Passed"
    except Exception as error:
        report["error"] = {"type": type(error).__name__, "message": str(error)}
    save(evidence / "report.json", report)
    save(evidence / "manifest.json", {"schema": "adva.knowledge.continuity-files.v0",
         "files": {p.relative_to(evidence).as_posix(): sha(p)
                   for p in sorted(evidence.rglob("*")) if p.is_file()}})
    print(json.dumps({"status": report["status"], "evidence": str(evidence),
                      "checks": len(report["checks"]), "error": report.get("error")}, indent=2))
    return 0 if report["status"] == "Passed" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--machine", type=Path, help="existing clean checkout at the exact locked revision")
    parser.add_argument("--output", type=Path, required=True, help="new build/evidence directory")
    args = parser.parse_args()
    try:
        return check(args.machine, args.output.resolve())
    except FileExistsError:
        parser.exit(2, "output exists; choose a new directory\n")


if __name__ == "__main__":
    sys.exit(main())
