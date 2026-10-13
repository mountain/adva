"""Bounded state-DAG campaign; Codex (OpenAI), Unknown v0.3."""
import copy
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    out = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=False)
    contract = json.loads((HERE / "contract.json").read_text())
    started = time.perf_counter()
    logs, results = [], []
    account = {"launches": 0, "counted_units": 0, "serialization_seconds": 0.0}
    status = "ImplementationFailure"

    def write(name, value):
        tick = time.perf_counter()
        path = out / name
        path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
        account["serialization_seconds"] += time.perf_counter() - tick
        return path

    def launch(label, command, build=False):
        assert account["launches"] < contract["max_processes_including_build"]
        account["launches"] += 1
        tick = time.perf_counter()
        proc = subprocess.run(command, capture_output=True, text=True,
                              timeout=contract["build_timeout_seconds"] if build else contract["runtime_timeout_seconds"])
        (out / f"{label}.stdout").write_text(proc.stdout)
        (out / f"{label}.stderr").write_text(proc.stderr)
        logs.append({"label": label, "wall_seconds": time.perf_counter() - tick, "returncode": proc.returncode})
        assert proc.returncode == 0, (label, proc.stderr)
        if build:
            return None
        value = json.loads(proc.stdout)
        units = sum(value.get(key, {}).get("counted_units", 0) for key in ("cost", "verification_cost"))
        account["counted_units"] += units
        assert account["counted_units"] <= contract["total_counted_units"]
        return value

    try:
        cargo = str(Path.home() / ".cargo/bin/cargo")
        launch("build", [cargo, "build", "--manifest-path", str(HERE / "Cargo.toml")], True)
        target = Path(os.environ.get("CARGO_TARGET_DIR", str(HERE / "target")))
        binary = str(target / "debug/schedule-state-dag")
        prior_dir = ROOT / "experiments/schedule_prefix/evidence/attempt-1"
        prior = json.loads((prior_dir / "results.json").read_text())
        prior_cases = {entry["name"]: entry for entry in prior if "producer_cost" in entry}
        names = ["diamond", "three", "delayed", "two-chains"]
        produced = []
        for name in names:
            input_value = json.loads((prior_dir / f"{name}.input.json").read_text())
            input_path = write(f"{name}.input.json", input_value)
            dag = launch(f"{name}-produce", [binary, "produce", str(input_path)])
            dag_path = write(f"{name}.dag.json", dag)
            received = launch(f"{name}-verify", [binary, "verify", str(input_path), str(dag_path)])
            expected = prior_cases[name]["result"]
            assert received["outcome"] == "Verified"
            assert received["legal_words"] == expected["legal_words"]
            assert received["first_query"] == expected["first_query"]
            assert received["whole_query"] == expected["whole_query"]
            results.append({"name": name, "dag_producer_cost": dag["cost"],
                            "dag_receiver_cost": received["verification_cost"],
                            "prior_prefix_producer_cost": prior_cases[name]["producer_cost"],
                            "prior_prefix_receiver_cost": expected["verification_cost"],
                            "result": received})
            produced.append((input_path, dag))

        input_path, dag = produced[0]
        controls = []
        def mutate(name, fn, expected):
            candidate = copy.deepcopy(dag)
            fn(candidate)
            controls.append((name, candidate, expected))
        mutate("missing-edge", lambda d: d["states"][0]["edges"].pop(), "UnknownCoverage")
        mutate("missing-state", lambda d: d["states"].pop(), "UnknownCoverage")
        mutate("wrong-next", lambda d: d["states"][0]["edges"][0].update(next_cut=[]), "InvalidEvidence")
        mutate("forged-step", lambda d: d["states"][0]["edges"][0]["step"]["result"]["after"].update(completed=[]), "InvalidEvidence")
        mutate("duplicate-state", lambda d: d["states"].append(copy.deepcopy(d["states"][0])), "InvalidEvidence")
        mutate("wrong-binding", lambda d: d.update(diagram_hash="wrong"), "InvalidContext")
        mutate("unreachable-state", lambda d: d["states"].append({"cut": [999], "edges": []}), "InvalidEvidence")
        mutate("noncanonical-cut", lambda d: d["states"][3].update(cut=list(reversed(d["states"][3]["cut"]))), "InvalidEvidence")
        for name, candidate, expected in controls:
            candidate_path = write(f"{name}.dag.json", candidate)
            received = launch(name, [binary, "verify", str(input_path), str(candidate_path)])
            assert received["outcome"] == expected, (name, received)
            results.append({"name": name, "expected": expected, "result": received})
        status = "Passed"
    except Exception as error:
        write("failure.json", {"type": type(error).__name__, "message": str(error)})
        raise
    finally:
        write("results.json", results)
        write("execution.json", {"status": status, "account": account, "processes": logs,
              "wall_seconds": time.perf_counter() - started,
              "supervisor_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "all_children_peak_rss_kib_including_build": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
              "memory_scope": "Native VmHWM retained per output; child aggregate includes build; no hard memory cap"})
        sources = ["contract.json", "Cargo.toml", "Cargo.lock", "src/main.rs", "run.py"]
        write("sources.json", {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                               for name in sources if (HERE / name).exists()})
        manifest = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in sorted(out.iterdir()) if path.is_file()}
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
