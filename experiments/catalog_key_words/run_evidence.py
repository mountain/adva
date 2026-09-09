"""Replay the bounded naming gate and its targeted regression suite."""

import hashlib
import importlib.util
import itertools
import json
import resource
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def main():
    started = time.perf_counter()
    spec = importlib.util.spec_from_file_location("catalog_measure", ROOT / "python/adva/math_catalog.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    t = time.perf_counter()
    seqs = [list(p) for n in range(1, 5)
            for p in itertools.permutations(("logic", "a", "b", "a1", "q4", "m6"), n)]
    construction = time.perf_counter() - t
    t = time.perf_counter()
    encoded = [module.link_words(p) for p in seqs]
    assert len(encoded) == len(set(encoded)) == 516
    assert all(module.unlink_key(k) == p for k, p in zip(encoded, seqs))
    codec_check = time.perf_counter() - t
    t = time.perf_counter()
    fresh = ["logic", "fresh", "word"]
    assert module.unlink_key(module.link_words(fresh)) == fresh
    reuse = time.perf_counter() - t
    runs = []
    for args in ([sys.executable, "-S", "python/adva/adva.py", "math-check"],
                 [sys.executable, "-S", "python/adva/adva.py", "math-check", "--key-words"],
                 [sys.executable, "-m", "pytest", "-q", "tests/python/test_math_catalog.py",
                  "tests/python/test_catalog_key_words.py"]):
        t = time.perf_counter()
        p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=30, check=False)
        run = {"command": args, "exit_code": p.returncode, "wall_seconds": time.perf_counter() - t,
               "stdout": p.stdout, "stderr": p.stderr}
        runs.append(run)
        if p.returncode:
            break
    t = time.perf_counter()
    compact = json.dumps({"sequences": seqs, "keys": encoded})
    serialization = time.perf_counter() - t
    t = time.perf_counter()
    recovered = json.loads(compact)
    assert recovered["sequences"] == [module.unlink_key(k) for k in recovered["keys"]]
    replay = time.perf_counter() - t
    files = ["python/adva/math_catalog.py", "python/adva/adva.py",
             "tests/python/test_math_catalog.py", "tests/python/test_catalog_key_words.py",
             "adva-library/names/catalog-key-words.json", "adva-library/names/catalog-key-words-v1.json",
             "adva-library/math/manifest.json", "experiments/catalog_key_words/contract.json"]
    report = {"status": "Passed" if all(r["exit_code"] == 0 for r in runs) else "Failed",
              "python": sys.version, "runs": runs, "finite_names": 516,
              "cost_seconds": {"construction": construction, "codec_verification": codec_check,
                               "fresh_codec_reuse": reuse, "serialization": serialization,
                               "codec_replay": replay, "before_report_write": time.perf_counter() - started},
              "process_peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "largest_child_peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
              "memory_scope": "separate process high-water marks, not simultaneous aggregate",
              "source_sha256": {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in files},
              "unmeasured": ["research and authoring", "network", "final report write"],
              "prior_validation": "645 tests passed before formatting and fixture import lint cleanup; no failing execution",
              "native_admission": "not-granted", "title_semantics_checked": False}
    (HERE / "evidence.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("runs", "source_sha256")}, indent=2))
    print(json.dumps([{k: v for k, v in r.items() if k not in ("stdout", "stderr")} for r in runs]))
    print(runs[-1]["stdout"][-100:])
    return 0 if report["status"] == "Passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
