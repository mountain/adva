"""Time existing frozen programs through the unchanged, checked Rust APIs.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy.
This is a finite measurement, not another bootstrap/specializer campaign.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import statistics
import subprocess
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments/bounded_self_compiler"))
from language import canonical, decode_target, seed_compile  # noqa: E402
from regression import bound_sources, read_archive  # noqa: E402
from checker import receive_compilation  # noqa: E402
from reference import Budget  # noqa: E402


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def observation(run):
    return {"status": run["status"], "value": run["state"]["phase"].get("value")}


def prepare():
    bound_sources()
    archived = read_archive("primary")
    read = lambda name: json.loads(archived[name])
    stages = [read(f"compiler.c{i}.adva") for i in (1, 2, 3)]
    assert canonical(stages[0]) == canonical(stages[1]) == canonical(stages[2])
    suite = []
    equalities = []
    budget = Budget()

    def add(name, version, program, data, expected, iterations=64, samples=9):
        suite.append(dict(name=name, version=version, program=program, input=data,
                          expected=expected, fuel=2048 if version == 0 else 200000,
                          iterations=iterations, samples=samples))

    for stage in (1, 2):
        run = read(f"self-c{stage}.run.adva")
        add(f"self-compile/c{stage}", 1, stages[stage-1], run["input"], observation(run), 1, 3)
    for row in read("summary.json")["fixtures"]:
        name = row["name"]
        source = read(f"{name}.source.adva")
        emitted = [decode_target(read(f"{name}-c{i}.run.adva")["state"]["phase"]["value"]) for i in (1, 2)]
        seed = seed_compile(source)
        assert canonical(seed) == canonical(emitted[0]) == canonical(emitted[1])
        receive_compilation(source, emitted[1], budget)
        equalities.append({"fixture": name, "seed_c1_c2_targets_equal": True,
                           "target_sha256": hashlib.sha256(canonical(seed)).hexdigest()})
        run = read(f"{name}-execute.run.adva")
        for stage in (1, 2):
            add(f"fixture/{name}/c{stage}", 1, emitted[stage-1], run["input"], observation(run))

    evidence = ROOT / "experiments/futamura_dynamic_residual/evidence/attempt-1"
    with tarfile.open(evidence / "attempt.tar.gz") as archive:
        members = archive.getmembers()
        assert len(members) <= 150 and sum(m.size for m in members) < 16 * 1024**2
        assert all(m.isfile() for m in members)
        files = {m.name: json.loads(archive.extractfile(m).read()) for m in members}
    for first in (0, 1):
        for second in (0, 1):
            for returned in (0, 1):
                label = f"p{first}{second}{returned}"
                run = files[f"runs/{label}.compiled.run.adva"]
                add(f"dynamic/{label}/compile", 0, run["program"], run["input"], observation(run), 32)
                for x in (7, 9):
                    for arm in ("interpreted", "residual"):
                        run = files[f"runs/{label}.{arm}.{x}.run.adva"]
                        add(f"dynamic/{label}/{x}/{arm}", 0, run["program"], run["input"], observation(run), 32 if arm == "interpreted" else 128)
                    residual_run = run
                    direct = {**run["program"], "name": "direct-source",
                              "code": [{"op":"input", "dst":first}, {"op":"input", "dst":second}, {"op":"return", "src":returned}]}
                    add(f"dynamic/{label}/{x}/direct", 0, direct, {"kind":"integer", "value":x}, observation(residual_run), 128)
    return suite, equalities


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    binary = args.binary.resolve()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    suite, equalities = prepare()
    (out / "suite.json").write_bytes(canonical(suite) + b"\n")
    affinity = sorted(os.sched_getaffinity(0))
    cpu = affinity[0]
    metadata = {
        "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "rustc": subprocess.check_output(["rustc", "--version"], text=True).strip(),
        "platform": platform.platform(), "cpu": cpu,
        "cpu_model": next((s.split(":", 1)[1].strip() for s in Path("/proc/cpuinfo").read_text().splitlines() if s.startswith("model name")), "unknown"),
        "binary_sha256": digest(binary), "suite_sha256": digest(out / "suite.json"),
        "harness_sha256": digest(ROOT / "crates/adva-witness/examples/execution_performance.rs"),
        "driver_sha256": digest(Path(__file__)), "build": "cargo build --locked --release -p adva-witness --example execution_performance",
        "limits": {"wall_seconds":600, "cpu_seconds":540, "address_space_bytes":1024**3, "output_file_bytes":16*1024**2},
        "scope": "Checked run API including admission, initialization, full trace/digests and internal report size serialization; excludes process startup, input parsing, file I/O and separate replay. One untimed run plus full replay per case. No VM changes.",
    }
    (out / "metadata.json").write_bytes(canonical(metadata) + b"\n")

    def limits():
        os.sched_setaffinity(0, {cpu})
        resource.setrlimit(resource.RLIMIT_CPU, (540, 540))
        resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
        resource.setrlimit(resource.RLIMIT_FSIZE, (16*1024**2, 16*1024**2))

    with (out / "samples.jsonl").open("x") as stdout, (out / "stderr.txt").open("x") as stderr:
        result = subprocess.run([str(binary), str(out / "suite.json")], stdout=stdout, stderr=stderr,
                                timeout=600, preexec_fn=limits)
    if result.returncode:
        raise RuntimeError(f"benchmark failed ({result.returncode}); output retained in {out}")
    records = [json.loads(line) for line in (out / "samples.jsonl").read_text().splitlines()]
    summary = []
    for case in suite:
        checks = [r["result"] for r in records if r["name"] == case["name"] and r["kind"] == "checked"]
        samples = [r["ns_per_run"] for r in records if r["name"] == case["name"] and r["kind"] == "sample"]
        assert len(checks) == 1 and len(samples) == case["samples"]
        assert checks[0]["observation"] == case["expected"]
        summary.append({"name":case["name"], "median_ns":statistics.median(samples),
                        "min_ns":min(samples), "max_ns":max(samples), "samples":len(samples),
                        "iterations":case["iterations"], "steps":checks[0]["steps"],
                        "status":checks[0]["observation"]["status"], "trace_blake3":checks[0]["trace_blake3"]})
    by_name = {r["name"]: r for r in summary}
    for row in equalities:
        a, b = [by_name[f"fixture/{row['fixture']}/c{i}"] for i in (1, 2)]
        assert a["trace_blake3"] == b["trace_blake3"] and a["steps"] == b["steps"]
    assert by_name["self-compile/c1"]["trace_blake3"] == by_name["self-compile/c2"]["trace_blake3"]
    result = {"status":"Passed", "wall_seconds_including_preparation":time.monotonic()-started,
              "checked_cases":len(suite), "target_equalities":equalities, "measurements":summary}
    (out / "results.json").write_bytes(canonical(result) + b"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ("measurements", "target_equalities")}))


if __name__ == "__main__":
    main()
