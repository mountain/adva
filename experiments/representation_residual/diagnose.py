#!/usr/bin/env python3
"""Read the retained k28 mismatch; no native execution or semantic allocation."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import time


def pair(q):
    assert max(q.numerator.bit_length(), q.denominator.bit_length()) <= 256
    return [str(q.numerator), str(q.denominator)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter_ns()
    paths = [args.evidence / "report.json", args.evidence / "product-k28.native-result.adva"]
    raw = []
    for path in paths:
        assert path.stat().st_size < 1024 * 1024
        raw.append(path.read_bytes())
    report, native = [json.loads(x) for x in raw]
    lexical = json.loads(raw[1], parse_float=str)
    case = next(x for x in report["cases"] if x["id"] == "product-k28")
    assert case["native"]["state"] == "Unknown"
    assert native["state"] == "Completed"
    submitted = (args.evidence / "product-k28.program.adva").read_text()
    assert native["program_json"] == submitted
    previous = sum(report["actual"][key] for key in
                   ["exact_ast_visits", "float_ast_visits", "trace_ast_visits"])
    # The original suite reserved at most 128 visits and used 112. This
    # diagnostic evaluates one multiplication (three tree visits), no search.
    assert previous + 3 <= 128
    q = {name: Fraction(*map(int, x["intended"]))
         for name, x in case["input_observation"].items()}
    p = {name: Fraction.from_float(float.fromhex(x["binary64_hex"]))
         for name, x in case["input_observation"].items()}
    r = {name: Fraction.from_float(value) for name, value in native["program"]["inputs"].items()}
    v_intended = Fraction(*map(int, case["exact_intention"]))
    v_python_inputs = Fraction(*map(int, case["exact_after_input_rounding"]))
    v_reported_inputs = r["x"] * r["y"]
    observed = Fraction.from_float(native["evaluation"]["values"][0])
    residuals = {"input": v_python_inputs - v_intended,
                 "transport": v_reported_inputs - v_python_inputs,
                 "operation": observed - v_reported_inputs,
                 "total": observed - v_intended}
    assert sum(residuals[x] for x in ["input", "transport", "operation"]) == residuals["total"]
    result = {
        "schema": "adva.representation-transport-diagnostic.research", "version": 0,
        "state": "ObservedTransportMismatch", "original_suite_state": report["state"],
        "original_case_native_state": case["native"]["state"],
        "qualification": "Native bit patterns are inferred by decoding its serialized input/output values; no direct Rust to_bits trace was recorded. This does not isolate parser versus serialization behavior.",
        "source_sha256": {path.name: hashlib.sha256(data).hexdigest() for path, data in zip(paths, raw)},
        "native_input_lexemes": lexical["program"]["inputs"],
        "native_input_hex_inferred": {name: value.hex() for name, value in native["program"]["inputs"].items()},
        "input_differences_from_python": {name: pair(r[name] - p[name]) for name in r},
        "input_differences_from_exact_intention": {name: pair(r[name] - q[name]) for name in r},
        "exact_product_of_reported_inputs": pair(v_reported_inputs),
        "native_output_lexeme": lexical["evaluation"]["values"][0],
        "native_output_hex_inferred": native["evaluation"]["values"][0].hex(),
        "residuals": {name: pair(value) for name, value in residuals.items()},
        "nonzero_inputs_preserved": all(value != 0 for value in r.values()),
        "native_calls": 0, "additional_ast_visits": 3, "combined_math_ast_visits": previous + 3,
        "remaining_math_ast_budget": 128 - previous - 3,
        "elapsed_ns_before_serialization": time.perf_counter_ns() - started,
        "serialization_ns": None, "peak_memory_bytes": None,
        "next_obligation": "Record exact IEEE-754 input/output bit patterns at the native JSON boundary before changing arithmetic or accepting the cross-language adapter."
    }
    assert time.perf_counter_ns() - started < 5_000_000_000
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"state": result["state"], "residuals": result["residuals"],
                      "combined_math_ast_visits": result["combined_math_ast_visits"]}))


if __name__ == "__main__":
    main()
