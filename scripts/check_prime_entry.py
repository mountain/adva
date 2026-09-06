"""Execute only the five frozen Rust-through-Python receipt checks."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

CONTRACT_SHA = "e6d74973d1e6c1e2574c4c7d65d086d2639e97d4e894d10f3747a2648cab6827"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    contract_path = root / "docs/research/0148-finalize-python-entry-contract.json"
    contract_raw = contract_path.read_bytes()
    if len(contract_raw) > 16384 or hashlib.sha256(contract_raw).hexdigest() != CONTRACT_SHA:
        raise ValueError("frozen contract bytes changed")
    contract = json.loads(contract_raw)
    expected_cases = [("main", "FiniteExtensionVerified"), ("fresh", "FiniteExtensionVerified"),
                      ("composite-successor", "FiniteExtensionVerified"),
                      ("false-prime-successor", "Blocked"), ("zero-fuel", "Unknown")]
    if [(c["name"], c["expected"]) for c in contract["cases"]] != expected_cases:
        raise ValueError("fixed case list changed")
    args.output.mkdir(parents=True, exist_ok=False)
    cases = []
    total_fuel = 0
    started = time.perf_counter_ns()
    for name, expected in expected_cases:
        request = root / f"adva-library/prime-universe/requests/{name}.json"
        output = args.output / f"{name}.json"
        command = [sys.executable, str(root / "python/adva/adva.py"), "prime-check",
                   str(request), "--native", args.native, "--output", str(output)]
        before = time.perf_counter_ns()
        with (args.output / f"{name}.stdout").open("wb") as stdout, (args.output / f"{name}.stderr").open("wb") as stderr:
            completed = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=6, check=False)
        elapsed = time.perf_counter_ns() - before
        result = json.loads(output.read_bytes())
        native = result["native_result"]
        wanted_exit = {"FiniteExtensionVerified": 0, "Blocked": 2, "Unknown": 3}[expected]
        matched = (completed.returncode == wanted_exit and result["execution"] == "Completed"
                   and result["status"] == expected and native is not None
                   and native["status"] == expected and native["request"] == json.loads(request.read_bytes())
                   and result["cost"]["subprocess_invocations"] == 1
                   and native["native_free"] == "NotGranted"
                   and native["native_universe"] == "NotImplemented")
        if native is not None:
            total_fuel += native["fuel_spent"]
        cases.append({"name": name, "expected": expected, "matched": matched,
                      "exit_code": completed.returncode, "wall_ns_including_wrapper_save": elapsed,
                      "result": result})
    report = {"schema": "adva.prime-entry.five-case-report.research", "version": 0,
              "cases": cases, "all_matched": all(c["matched"] for c in cases),
              "native_calls": len(cases), "native_fuel_spent": total_fuel,
              "native_fuel_cap": 5120, "wall_ns": time.perf_counter_ns() - started,
              "child_peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
              "contract_sha256": hashlib.sha256(contract_raw).hexdigest(),
              "old_six_stage_protocol_calls": 0, "native_free": "NotGranted",
              "missing_costs": ["Research/coding/network", "Unit-test logical fuel; see separate host time log"]}
    if total_fuel > 5120:
        raise ValueError("fixed verification budget exceeded")
    encoded = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if len(encoded.encode()) > 262144:
        raise ValueError("report exceeds byte cap")
    (args.output / "report.json").write_text(encoded)
    print("PRIME_ENTRY_EVIDENCE_BEGIN")
    print(encoded, end="")
    print("PRIME_ENTRY_EVIDENCE_END")
    return 0 if report["all_matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
