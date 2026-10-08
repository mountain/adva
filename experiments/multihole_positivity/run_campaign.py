"""Run the single frozen external campaign; this is not a native Adva executor."""
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


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(destination):
    contract = json.loads((HERE / "contract.json").read_text())
    budget = contract["budget"]
    destination.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    initial_cpu = resource.getrusage(resource.RUSAGE_CHILDREN)
    initial_self = resource.getrusage(resource.RUSAGE_SELF)
    resource.setrlimit(resource.RLIMIT_AS, (budget["address_space_bytes"], budget["address_space_bytes"]))
    cpu_ceiling = math.ceil(initial_self.ru_utime + initial_self.ru_stime) + budget["campaign_cpu_seconds"]
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_ceiling, cpu_ceiling))
    report = {
        "schema": "adva.external-multihole-positivity-campaign.v0",
        "status": "Unknown",
        "native_status": "Unavailable",
        "source_bindings": {},
        "launches": [],
        "automatic_retries": 0,
    }
    test = HERE.parent.parent / "tests/python/test_multihole_positivity.py"
    sources = [HERE / n for n in ("contract.json", "checker.py", "verifier.py", "run_campaign.py")] + [test]
    report["source_bindings"] = {p.name: digest(p) for p in sources}

    def child(args, expected=0, environment=None):
        if len(report["launches"]) >= budget["maximum_child_launches"]:
            raise RuntimeError("launch budget exhausted")
        remaining = budget["campaign_wall_seconds"] - (time.monotonic() - started)
        used = resource.getrusage(resource.RUSAGE_CHILDREN)
        own = resource.getrusage(resource.RUSAGE_SELF)
        used_cpu = (used.ru_utime + used.ru_stime - initial_cpu.ru_utime - initial_cpu.ru_stime
                    + own.ru_utime + own.ru_stime - initial_self.ru_utime - initial_self.ru_stime)
        remaining_cpu = int(budget["campaign_cpu_seconds"] - used_cpu - 1)
        if remaining <= 0 or remaining_cpu <= 0:
            raise RuntimeError("campaign resource budget exhausted")

        def limits():
            resource.setrlimit(resource.RLIMIT_AS, (budget["address_space_bytes"], budget["address_space_bytes"]))
            resource.setrlimit(resource.RLIMIT_CPU, (remaining_cpu, remaining_cpu))
            resource.setrlimit(resource.RLIMIT_FSIZE, (budget["output_bytes"], budget["output_bytes"]))

        begin = time.monotonic()
        launch = {"argv": [Path(a).name if "/" in a else a for a in args], "expected_exit": expected}
        report["launches"].append(launch)
        try:
            out_path = destination / ("child-%d.stdout" % len(report["launches"]))
            err_path = destination / ("child-%d.stderr" % len(report["launches"]))
            with out_path.open("xb") as out, err_path.open("xb") as err:
                result = subprocess.run(args, cwd=HERE, env=environment, stdout=out, stderr=err,
                                        timeout=min(budget["each_child_wall_seconds"], remaining), preexec_fn=limits)
        except subprocess.TimeoutExpired:
            launch.update(outcome="Unknown", reason="child wall limit")
            raise RuntimeError("child wall limit")
        if any(p.stat().st_size > budget["output_bytes"] for p in destination.iterdir()):
            raise RuntimeError("per-file output limit")
        if sum(p.stat().st_size for p in destination.iterdir()) > budget["total_retained_bytes"]:
            raise RuntimeError("aggregate retained output limit")
        stdout, stderr = out_path.read_text(), err_path.read_text()
        launch.update(exit=result.returncode, elapsed_seconds=round(time.monotonic()-begin, 6),
                      stdout=stdout, stderr=stderr)
        if result.returncode != expected:
            launch["outcome"] = "Failed"
            raise RuntimeError("child exited outside declared outcome")
        launch["outcome"] = "AsDeclared"
        return stdout

    first, second = destination / "ordinary.json", destination / "optimized.json"
    try:
        child([sys.executable, str(HERE / "checker.py"), "--output", str(first)])
        child([sys.executable, "-O", str(HERE / "checker.py"), "--output", str(second)])
        if first.read_bytes() != second.read_bytes():
            raise RuntimeError("ordinary and optimized evidence differ")
        receiver = child([sys.executable, str(HERE / "verifier.py"), str(first)])
        report["independent_receiver"] = json.loads(receiver)
        if report["independent_receiver"].get("status") != "Verified":
            raise RuntimeError("independent receiver did not verify")
        env = dict(os.environ, MULTIHOLE_EVIDENCE=str(first), PYTHONDONTWRITEBYTECODE="1")
        child([sys.executable, str(test)], environment=env)
        child([sys.executable, str(HERE / "checker.py"), "--output", str(first)], expected=2)
        for p in sources:
            if digest(p) != report["source_bindings"][p.name]:
                raise RuntimeError("source changed during campaign")
        report.update(status="Passed", evidence_sha256=digest(first), optimized_sha256=digest(second),
                      byte_identical=True, total_launches=len(report["launches"]))
    except (RuntimeError, OSError, ValueError) as error:
        report["reason"] = str(error)
    report["elapsed_seconds"] = round(time.monotonic()-started, 6)
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    report["child_cpu_seconds"] = round(usage.ru_utime + usage.ru_stime - initial_cpu.ru_utime - initial_cpu.ru_stime, 6)
    own = resource.getrusage(resource.RUSAGE_SELF)
    report["parent_cpu_seconds"] = round(own.ru_utime + own.ru_stime - initial_self.ru_utime - initial_self.ru_stime, 6)
    if report["elapsed_seconds"] > budget["campaign_wall_seconds"] or report["child_cpu_seconds"] + report["parent_cpu_seconds"] > budget["campaign_cpu_seconds"]:
        report.update(status="Unknown", reason="aggregate campaign resource limit")
    encoded = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
    if len(encoded) > budget["output_bytes"]:
        raise RuntimeError("campaign report output limit")
    if sum(p.stat().st_size for p in destination.iterdir()) + len(encoded) > budget["total_retained_bytes"]:
        raise RuntimeError("aggregate report output limit")
    with (destination / "campaign.json").open("xb") as stream:
        stream.write(encoded)
    print(json.dumps({"status": report["status"], "launches": len(report["launches"]),
                      "elapsed_seconds": report["elapsed_seconds"], "report": str(destination / "campaign.json")}))
    return 0 if report["status"] == "Passed" else 3


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: run_campaign.py NEW_DIRECTORY")
    raise SystemExit(run(Path(sys.argv[1]).resolve()))
