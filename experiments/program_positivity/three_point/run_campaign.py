"""Independent three-point successor campaign; no native Adva execution."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(destination):
    contract = json.loads((HERE / "contract.json").read_text())
    budget = contract["campaign"]
    cases = json.loads((HERE / "cases.json").read_text())
    if set(cases) != set(contract["cases"]) or len(cases) != budget["batch_requests"]:
        raise ValueError("case set differs from the frozen contract")
    destination.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    initial_children = resource.getrusage(resource.RUSAGE_CHILDREN)
    initial_self = resource.getrusage(resource.RUSAGE_SELF)
    resource.setrlimit(resource.RLIMIT_AS, (budget["memory_bytes"], budget["memory_bytes"]))
    cpu_ceiling = math.ceil(initial_self.ru_utime + initial_self.ru_stime) + budget["cpu_seconds"]
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_ceiling, cpu_ceiling))
    report = {
        "schema": "adva.three-point-positivity-campaign.v0",
        "status": "Unknown", "native_status": "Unavailable",
        "source_bindings": {}, "launches": [], "automatic_retries": 0,
    }
    root = ENGINE.parent.parent
    test = root / "tests/python/test_program_positivity_three_point.py"
    sources = [HERE / name for name in ("contract.json", "cases.json", "run_campaign.py")]
    sources += [ENGINE / name for name in ("contract.json", "meta.py", "verifier.py")]
    sources += [test]
    report["source_bindings"] = {str(p.relative_to(root)): digest(p) for p in sources}

    def cpu_used():
        children = resource.getrusage(resource.RUSAGE_CHILDREN)
        own = resource.getrusage(resource.RUSAGE_SELF)
        return (children.ru_utime + children.ru_stime - initial_children.ru_utime - initial_children.ru_stime
                + own.ru_utime + own.ru_stime - initial_self.ru_utime - initial_self.ru_stime)

    def check_output(extra=0):
        files = [p for p in destination.iterdir() if p.is_file()]
        if any(p.stat().st_size > budget["output_bytes_per_file"] for p in files):
            raise RuntimeError("per-file output limit")
        if sum(p.stat().st_size for p in files) + extra > budget["total_output_bytes"]:
            raise RuntimeError("aggregate output limit")

    def child(args, expected=0, environment=None):
        if len(report["launches"]) >= budget["child_launches"]:
            raise RuntimeError("child launch budget exhausted")
        remaining_wall = budget["wall_seconds"] - (time.monotonic() - started)
        remaining_cpu = int(budget["cpu_seconds"] - cpu_used() - 1)
        if remaining_wall <= 0 or remaining_cpu <= 0:
            raise RuntimeError("campaign resource budget exhausted")

        def limits():
            resource.setrlimit(resource.RLIMIT_AS, (budget["memory_bytes"], budget["memory_bytes"]))
            resource.setrlimit(resource.RLIMIT_CPU, (remaining_cpu, remaining_cpu))
            resource.setrlimit(resource.RLIMIT_FSIZE,
                               (budget["output_bytes_per_file"], budget["output_bytes_per_file"]))

        begin = time.monotonic()
        launch = {"argv": [Path(a).name if "/" in a else a for a in args], "expected_exit": expected}
        report["launches"].append(launch)
        number = len(report["launches"])
        out_path = destination / ("child-%d.stdout" % number)
        err_path = destination / ("child-%d.stderr" % number)
        try:
            with out_path.open("xb") as out, err_path.open("xb") as err:
                process = subprocess.run(args, cwd=root, env=environment, stdout=out, stderr=err,
                                         timeout=min(budget["child_wall_seconds"], remaining_wall),
                                         preexec_fn=limits)
        except subprocess.TimeoutExpired:
            launch.update(outcome="Unknown", reason="child wall limit")
            raise RuntimeError("child wall limit")
        check_output()
        launch.update(exit=process.returncode, elapsed_seconds=round(time.monotonic() - begin, 6),
                      stdout=out_path.read_text(), stderr=err_path.read_text())
        if process.returncode != expected:
            launch["outcome"] = "Failed"
            raise RuntimeError("child exited outside declared outcome")
        launch["outcome"] = "AsDeclared"
        return launch["stdout"]

    first, second = destination / "ordinary.json", destination / "optimized.json"
    try:
        child([sys.executable, str(ENGINE / "meta.py"), "--batch", str(HERE / "cases.json"),
               "--output", str(first)])
        child([sys.executable, "-O", str(ENGINE / "meta.py"), "--batch", str(HERE / "cases.json"),
               "--output", str(second)])
        if first.read_bytes() != second.read_bytes():
            raise RuntimeError("ordinary and optimized evidence differ")
        received = child([sys.executable, str(ENGINE / "verifier.py"), str(HERE / "cases.json"), str(first)])
        report["independent_receiver"] = json.loads(received)
        if report["independent_receiver"].get("status") != "Verified":
            raise RuntimeError("independent receiver did not verify decisive claims")
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        child([sys.executable, str(test)], environment=env)
        child([sys.executable, str(ENGINE / "meta.py"), "--batch", str(HERE / "cases.json"),
               "--output", str(first)], expected=2)
        if any(digest(p) != report["source_bindings"][str(p.relative_to(root))] for p in sources):
            raise RuntimeError("source changed during campaign")
        report.update(status="Passed", evidence_sha256=digest(first), optimized_sha256=digest(second),
                      byte_identical=True, total_launches=len(report["launches"]),
                      batch_requests=len(cases))
    except (RuntimeError, OSError, ValueError) as error:
        report["reason"] = str(error)
    report["elapsed_seconds"] = round(time.monotonic() - started, 6)
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    report["child_cpu_seconds"] = round(usage.ru_utime + usage.ru_stime - initial_children.ru_utime - initial_children.ru_stime, 6)
    own = resource.getrusage(resource.RUSAGE_SELF)
    report["parent_cpu_seconds"] = round(own.ru_utime + own.ru_stime - initial_self.ru_utime - initial_self.ru_stime, 6)
    if report["elapsed_seconds"] > budget["wall_seconds"] or cpu_used() > budget["cpu_seconds"]:
        report.update(status="Unknown", reason="aggregate campaign resource limit")
    encoded = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
    if len(encoded) > budget["output_bytes_per_file"]:
        raise RuntimeError("campaign report output limit")
    check_output(len(encoded))
    with (destination / "campaign.json").open("xb") as stream:
        stream.write(encoded)
    print(json.dumps({"status": report["status"], "launches": len(report["launches"]),
                      "elapsed_seconds": report["elapsed_seconds"], "report": str(destination / "campaign.json")}))
    return 0 if report["status"] == "Passed" else 3


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: run_campaign.py NEW_DIRECTORY")
    raise SystemExit(run(Path(sys.argv[1]).resolve()))
