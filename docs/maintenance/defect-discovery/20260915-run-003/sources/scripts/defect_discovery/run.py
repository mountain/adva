#!/usr/bin/env python3
"""Bounded local discovery. Standard library only; never writes to a remote."""
import argparse
import hashlib
import json
import os
import pathlib
import platform
import signal
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

# -I deliberately removes script-directory imports, so add only this reviewed directory.
HERE = pathlib.Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from probes import SOURCES, run

CONTRACT = dict(schema="adva.defect-discovery.contract.v1", probes=list(SOURCES),
                repeats=2, max_cases_per_probe=32, worker_cpu_seconds=5,
                worker_wall_seconds=10, worker_address_bytes=512 * 1024 * 1024,
                worker_file_bytes=1024 * 1024, total_wall_seconds=75,
                max_source_bytes=1024 * 1024, retained_bytes=8 * 1024 * 1024)


def encode(obj):
    return (json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atomic(path, data):
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def worker(probe, root):
    if platform.system() != "Linux":
        raise RuntimeError("Unknown: enforced resource profile requires Linux")
    import resource
    for key, limit in ((resource.RLIMIT_CPU, CONTRACT["worker_cpu_seconds"]),
                       (resource.RLIMIT_AS, CONTRACT["worker_address_bytes"]),
                       (resource.RLIMIT_FSIZE, CONTRACT["worker_file_bytes"]),
                       (resource.RLIMIT_CORE, 0)):
        resource.setrlimit(key, (limit, limit))
    result = run(probe, root)
    if not 0 < len(result["cases"]) <= CONTRACT["max_cases_per_probe"]:
        raise RuntimeError("Unknown: case budget")
    sys.stdout.buffer.write(encode(result))


def replay(probe, root, remaining):
    started = time.monotonic()
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        p = subprocess.Popen([sys.executable, "-I", "-B", str(root / "scripts/defect_discovery/run.py"), "--worker", probe,
                              "--root", str(root)], stdout=out, stderr=err,
                             start_new_session=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        timeout = False
        try:
            p.wait(timeout=min(CONTRACT["worker_wall_seconds"], remaining))
        except subprocess.TimeoutExpired:
            timeout = True
            os.killpg(p.pid, signal.SIGKILL)
            p.wait()
        out.seek(0)
        err.seek(0)
        stdout = out.read(CONTRACT["worker_file_bytes"] + 1)
        stderr = err.read(CONTRACT["worker_file_bytes"] + 1)
    receipt = dict(process_id=p.pid, exit_code=p.returncode, timed_out=timeout,
                   elapsed_seconds=round(time.monotonic() - started, 6),
                   stderr=stderr.decode(errors="replace")[-8192:])
    try:
        if p.returncode or timeout or len(stdout) > CONTRACT["worker_file_bytes"]:
            raise ValueError("worker failed or exhausted budget")
        result = json.loads(stdout)
        if not 0 < len(result["cases"]) <= CONTRACT["max_cases_per_probe"]:
            raise ValueError("invalid worker evidence")
        receipt["result"] = result
        receipt["result_sha256"] = digest(encode(result))
    except (ValueError, KeyError, TypeError) as exc:
        receipt["unknown_reason"] = str(exc)
    return receipt


def classify(replays):
    if len(replays) != 2 or any("result" not in r for r in replays):
        return "Unknown"
    for receipt in replays:
        cases = receipt["result"].get("cases")
        if (not isinstance(cases, list) or not 0 < len(cases) <= CONTRACT["max_cases_per_probe"]
                or any(not isinstance(c, dict) or c.get("verdict") not in ("Pass", "Violation") for c in cases)):
            return "Unknown"
    if replays[0]["result_sha256"] != replays[1]["result_sha256"]:
        return "Unknown"
    return "NativeReproduced" if any(c["verdict"] == "Violation" for c in replays[0]["result"]["cases"]) else "BoundedPass"


def report_markdown(report):
    lines = ["# Bounded defect discovery report", "", f"Checked: {report['checked_at']}",
             f"Declared source: `{report['declared_source_commit']}` (not a deployed binary identity).", "",
             "| Probe | Evidence state | Violations | Upstream submission |",
             "| --- | --- | ---: | --- |"]
    for item in report["probes"]:
        result = item["replays"][0].get("result", {}) if item["replays"] else {}
        bad = [c for c in result.get("cases", []) if c["verdict"] == "Violation"]
        lines.append(f"| {item['id']} | {item['state']} | {len(bad)} | NotEligible: local adapter, no upstream attribution |")
    for item in report["probes"]:
        lines.extend(["", f"## {item['id']}", ""])
        result = item["replays"][0].get("result", {}) if item["replays"] else {}
        for field in ("invariant", "oracle", "scope", "common_mode"):
            lines.append(f"- {field}: {result.get(field, 'Unknown')}")
        for field in ("severity", "impact", "next_step", "open_obligations"):
            lines.append(f"- {field}: {item[field]}")
        for c in result.get("cases", []):
            if c["verdict"] == "Violation":
                lines.extend(["", f"Counterexample: `{c['name']}`", "```json", json.dumps(c, indent=2), "```"])
        lines.append("\nNext: validate intended helper domain, minimize, and add a regression before proposing a local fix.")
    lines.extend(["", "## Limits and attribution", "",
                  "NativeReproduced means the actual Python helper ran twice with identical evidence. It does not mean a native Rust certificate, an upstream defect, or deployed-product impact.",
                  "A bounded pass does not prove correctness. Clocks enforce a host resource limit; their presence alone is not a mathematical defect. Fraction/CPython and hardware remain shared assumptions.",
                  "No Rust/LLVM, kernel, BLAS, FFI, concurrent mutation, filesystem fault injection, or upstream reproducer was executed. Source content hashes and resource limits are in report.json.",
                  "Authored by ChatGPT (OpenAI), submitted through Mingli Yuan's GitHub account as an authorized proxy. Account use is not endorsement, review, or a correctness claim.", ""])
    return "\n".join(lines).encode()


def discover(root, out, source_commit):
    started = time.monotonic()
    out.mkdir(parents=True, exist_ok=False)
    paths = sorted({p for paths in SOURCES.values() for p in paths})
    paths += ["scripts/defect_discovery/probes.py", "scripts/defect_discovery/run.py"]
    hashes = {}
    total = 0
    for path in paths:
        with (root / path).open("rb") as f:
            data = f.read(CONTRACT["max_source_bytes"] + 1)
        if len(data) > CONTRACT["max_source_bytes"]:
            raise ValueError("source retention budget exceeded")
        total += len(data)
        dest = out / "sources" / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        atomic(dest, data)
        hashes[path] = digest(data)
    # Execute the retained snapshot, so witnesses cannot silently refer to later edits.
    snapshot = out / "sources"
    report = dict(schema="adva.defect-discovery.report.v1", checked_at=datetime.now(timezone.utc).isoformat(),
                  declared_source_commit=source_commit, source_identity="DeclaredCommitWithRetainedFileHashes",
                  contract=CONTRACT, environment=dict(python=sys.version, executable=sys.executable,
                  implementation=platform.python_implementation(), platform=platform.platform(),
                  machine=platform.machine(), libc=platform.libc_ver()), source_sha256=hashes, probes=[])
    for name in SOURCES:
        receipts = []
        for _ in range(CONTRACT["repeats"]):
            remaining = CONTRACT["total_wall_seconds"] - (time.monotonic() - started)
            if remaining <= 1:
                break
            receipts.append(replay(name, snapshot, remaining))
        state = classify(receipts)
        violation = state == "NativeReproduced"
        report["probes"].append(dict(id=name, state=state, upstream_state="NotEligible",
            owner="Adva research helper; upstream ownership not established", replays=receipts,
            severity="HighPotential_ExposureUnknown" if violation else "NoDemonstratedImpact",
            impact="Wrong bound or inverse could corrupt a consuming certificate; no affected accepted certificate demonstrated" if violation else "Only the declared finite relation and mutations were checked",
            next_step="Confirm intended helper domain, minimize, add regression, propose local fix" if violation else "Retain bounded coverage; extend only under a new finite contract",
            open_obligations="Retained experiment consumers, deployment, concurrent calls, independent interpreter/compiler/hardware, and upstream applicability remain unverified"))
    report["elapsed_seconds"] = round(time.monotonic() - started, 6)
    payloads = {"report.json": encode(report), "report.md": report_markdown(report)}
    if total + sum(map(len, payloads.values())) > CONTRACT["retained_bytes"]:
        raise ValueError("report retention budget exceeded")
    for name, data in payloads.items():
        atomic(out / name, data)
    # This completion marker is written last; consumers verify its hashes.
    atomic(out / "COMPLETE.json", encode({"schema": report["schema"],
                                         "sha256": {name: digest(data) for name, data in payloads.items()}}))
    states = {p["state"] for p in report["probes"]}
    print(json.dumps(dict(report=str(out / "report.md"), states=sorted(states))))
    return 2 if "Unknown" in states else 1 if "NativeReproduced" in states else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=HERE.parents[1])
    parser.add_argument("--out", type=pathlib.Path)
    parser.add_argument("--source-commit")
    parser.add_argument("--worker", choices=list(SOURCES), help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        if args.worker:
            sys.dont_write_bytecode = True
            worker(args.worker, args.root.resolve())
            return 0
        if not args.out or not args.source_commit or len(args.source_commit) != 40 or any(c not in "0123456789abcdef" for c in args.source_commit):
            parser.error("--out (new directory) and --source-commit (full lowercase SHA) required")
        return discover(args.root.resolve(), args.out.resolve(), args.source_commit)
    except Exception as exc:
        print(f"Unknown: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
