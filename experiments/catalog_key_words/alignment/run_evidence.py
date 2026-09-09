"""Bounded baseline/final replay of the fifteenth-key integration."""

import hashlib
import json
import resource
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CONTRACT = json.loads((HERE / "contract.json").read_text())


def child_limits():
    limit = CONTRACT["budget"]["child_address_space_bytes"]
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))


def main():
    phase = sys.argv[1]
    if phase not in {"baseline", "final"}:
        raise SystemExit("expected baseline or final")
    destination = HERE / (phase + ".json")
    if destination.exists():
        raise SystemExit("refusing to overwrite prior evidence")
    started = time.perf_counter()
    runs = []
    commands = [
        [sys.executable, "-S", "python/adva/adva.py", "math-check"],
        [sys.executable, "-S", "python/adva/adva.py", "math-check", "--key-words"],
    ]
    if phase == "final":
        commands.append([sys.executable, "-m", "pytest", "-q",
                         "tests/python/test_math_catalog.py",
                         "tests/python/test_catalog_key_words.py"])
    for i, command in enumerate(commands):
        remaining = CONTRACT["budget"]["total_driver_seconds"] - (time.perf_counter() - started)
        if remaining <= 0:
            runs.append({"status": "Unknown", "reason": "total deadline"})
            break
        t = time.perf_counter()
        try:
            run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                 timeout=min(30, remaining), preexec_fn=child_limits,
                                 check=False)
            expected = 2 if phase == "baseline" and i == 1 else 0
            record = {"command": command, "exit_code": run.returncode,
                      "expected_exit": expected, "stdout": run.stdout,
                      "stderr": run.stderr, "wall_seconds": time.perf_counter() - t}
            if i < 2:
                report = json.loads(run.stdout)
                expected_status = "InvalidCatalog" if expected == 2 else "CatalogConsistent"
                record["expected_status"] = expected_status
                record["matched"] = run.returncode == expected and report["status"] == expected_status
                if expected == 2:
                    record["matched"] &= "cover every declared catalog key" in str(report["reason"])
            else:
                record["matched"] = run.returncode == expected
            runs.append(record)
            if not record["matched"]:
                break
        except subprocess.TimeoutExpired:
            runs.append({"command": command, "status": "Unknown", "reason": "child timeout"})
            break
    paths = ["python/adva/adva.py", "python/adva/math_catalog.py",
             "tests/python/test_math_catalog.py", "tests/python/test_catalog_key_words.py",
             "adva-library/math/manifest.json", "adva-library/names/catalog-key-words.json",
             "adva-library/names/catalog-key-words-v1.json", "adva-library/pascal-task.adva",
             "adva-library/pascal-witness.adva",
             "adva-library/math/constraints/growth-obligation-v0000.json",
             "adva-library/math/constraints/growth-obligation-seal-v0000.json",
             "adva-library/meaning-yau-calabi-mapping-v0.md",
             "experiments/catalog_key_words/alignment/contract.json",
             "experiments/catalog_key_words/alignment/run_evidence.py"]
    result = {"phase": phase,
              "status": "ExpectedResults" if len(runs) == len(commands) and all(r.get("matched") for r in runs) else "UnknownOrFailure",
              "runs": runs, "python": sys.version,
              "wall_seconds_before_serialization": time.perf_counter() - started,
              "parent_peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "largest_child_peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
              "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths},
              "unmeasured": ["authoring", "network", "aggregate memory", "final file write"],
              "native_admission": "not-granted", "title_semantics_checked": False}
    t = time.perf_counter()
    payload = json.dumps(result, indent=2)
    result["serialization_seconds"] = time.perf_counter() - t
    t = time.perf_counter()
    assert json.loads(payload)["runs"] == runs
    result["report_replay_seconds"] = time.perf_counter() - t
    with destination.open("x") as f:
        f.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in {"runs", "source_sha256"}}, indent=2))
    print(json.dumps([{k: v for k, v in r.items() if k not in {"stdout", "stderr"}} for r in runs]))
    return 0 if result["status"] == "ExpectedResults" else 1


if __name__ == "__main__":
    raise SystemExit(main())
