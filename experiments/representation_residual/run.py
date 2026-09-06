#!/usr/bin/env python3
"""Bounded external representation oracle; Rust retains native semantic authority.

Only the finite question's add/mul trees and pointwise scalar predicates are
interpreted here. This is not an Adva interpreter or a Seal/M1 verifier.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
import tracemalloc


QUESTION_SCHEMA = "adva.representation-question.research"
MAX_CASES = 8
MAX_AST_NODES = 128
MAX_FRACTION_BITS = 256
MAX_SOURCE_BYTES = 4096
MAX_QUESTION_BYTES = 65536
MAX_NATIVE_FILE_BYTES = 1048576
TOTAL_SECONDS = 30.0
NATIVE_SECONDS = 5.0
FUEL = 16
NAME = re.compile(r"[a-z][a-z0-9_]{0,31}\Z")
CASE_ID = re.compile(r"[a-z][a-z0-9_-]{0,47}\Z")
INTEGER = re.compile(r"-?(0|[1-9][0-9]{0,77})\Z")


class Rejected(ValueError):
    pass


class Unknown(RuntimeError):
    pass


def clock() -> int:
    return time.perf_counter_ns()


def pairs_unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Rejected(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json(raw: bytes):
    def reject_constant(value):
        raise Rejected(f"nonfinite JSON constant: {value}")
    return json.loads(raw, object_pairs_hook=pairs_unique,
                      parse_constant=reject_constant)


def encode(value) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def create_file(path: Path, raw: bytes):
    with path.open("xb") as stream:
        stream.write(raw)


def fraction_pair(value: Fraction):
    return [str(value.numerator), str(value.denominator)]


def bounded(value: Fraction) -> Fraction:
    if max(value.numerator.bit_length(), value.denominator.bit_length()) > MAX_FRACTION_BITS:
        raise Unknown("exact oracle exceeded the 256-bit rational bound")
    return value


def read_fraction(pair) -> Fraction:
    if not isinstance(pair, list) or len(pair) != 2:
        raise Rejected("rational must be [numerator string, denominator string]")
    if any(not isinstance(x, str) or not INTEGER.fullmatch(x) for x in pair):
        raise Rejected("rational integer syntax or decimal length exceeded")
    n, d = map(int, pair)
    if d <= 0:
        raise Rejected("rational denominator must be positive")
    if max(n.bit_length(), d.bit_length()) > MAX_FRACTION_BITS:
        raise Rejected("input rational exceeded the 256-bit bound")
    return bounded(Fraction(n, d))


def classify(value) -> str:
    return "zero" if value == 0 else "one" if value == 1 else "other"


def finite_float(value) -> float:
    try:
        result = float(value)
    except (OverflowError, ValueError) as error:
        raise Unknown("binary64 conversion failed") from error
    if not math.isfinite(result):
        raise Unknown("nonfinite binary64 value is outside this experiment")
    return result


def scan_expression(expr, inputs, uses, depth=0):
    if depth > 16:
        raise Rejected("AST depth exceeds 16")
    if isinstance(expr, str):
        if expr not in inputs:
            raise Rejected("expression references an undeclared input")
        uses[expr] += 1
        return 1
    if not isinstance(expr, list) or len(expr) != 3 or expr[0] not in ("add", "mul"):
        raise Unknown("only binary add/mul and declared input names are supported")
    return 1 + sum(scan_expression(child, inputs, uses, depth + 1) for child in expr[1:])


def source_expression(expr):
    if isinstance(expr, str):
        return f"(use {expr})"
    return f"({expr[0]} {source_expression(expr[1])} {source_expression(expr[2])})"


def render_program(case, exact_inputs):
    parameters = " ".join(f"({name} Real)" for name in exact_inputs)
    source = ("(module representation (export main) "
              f"(def main (fn ({parameters}) Real {source_expression(case['expression'])})))")
    if len(source.encode()) > MAX_SOURCE_BYTES:
        raise Rejected("source exceeds 4096 bytes")
    # Keep exact integers in JSON. Conversion belongs to the native reader.
    # Nonintegers here are dyadic; retain their intended rationals in question.
    native_inputs = {}
    for name, value in exact_inputs.items():
        if value.denominator == 1:
            native_inputs[name] = value.numerator
        else:
            if value.denominator & (value.denominator - 1):
                raise Rejected("native adapter only admits dyadic noninteger inputs")
            native_inputs[name] = finite_float(value)
    return {"schema": "adva.run.program.research", "version": 0,
            "source": source, "module": "representation", "entry": "main",
            "inputs": native_inputs, "fuel": FUEL}


def exact_eval(expr, values, metrics, deadline):
    if clock() >= deadline:
        raise Unknown("total wall budget exhausted during exact evaluation")
    metrics["exact_ast_visits"] += 1
    enforce_steps(metrics)
    if isinstance(expr, str):
        return values[expr]
    left = exact_eval(expr[1], values, metrics, deadline)
    right = exact_eval(expr[2], values, metrics, deadline)
    return bounded(left + right if expr[0] == "add" else left * right)


def enforce_steps(metrics):
    if (metrics["exact_ast_visits"] + metrics["float_ast_visits"]
            + metrics["trace_ast_visits"] > MAX_AST_NODES):
        raise Unknown("global mathematical AST steps exceeded 128")


def raw_float_eval(expr, values, metrics, deadline):
    if clock() >= deadline:
        raise Unknown("total wall budget exhausted during raw float evaluation")
    metrics["float_ast_visits"] += 1
    enforce_steps(metrics)
    if isinstance(expr, str):
        return values[expr]
    left = raw_float_eval(expr[1], values, metrics, deadline)
    right = raw_float_eval(expr[2], values, metrics, deadline)
    return finite_float(left + right if expr[0] == "add" else left * right)


def float_eval(expr, values, trace, metrics, deadline, path="root"):
    if clock() >= deadline:
        raise Unknown("total wall budget exhausted during float evaluation")
    metrics["trace_ast_visits"] += 1
    enforce_steps(metrics)
    if isinstance(expr, str):
        return values[expr]
    left = float_eval(expr[1], values, trace, metrics, deadline, path + ".left")
    right = float_eval(expr[2], values, trace, metrics, deadline, path + ".right")
    local_exact = bounded(Fraction.from_float(left) + Fraction.from_float(right)
                          if expr[0] == "add" else
                          Fraction.from_float(left) * Fraction.from_float(right))
    rounded = finite_float(left + right if expr[0] == "add" else left * right)
    local_residual = bounded(Fraction.from_float(rounded) - local_exact)
    trace.append({"path": path, "operation": expr[0], "left_hex": left.hex(),
                  "right_hex": right.hex(), "output_hex": rounded.hex(),
                  "exact_of_rounded_operands": fraction_pair(local_exact),
                  "local_rounding_residual": fraction_pair(local_residual)})
    return rounded


def inspect_case(case, metrics):
    if not isinstance(case, dict) or not CASE_ID.fullmatch(case.get("id", "")):
        raise Rejected("case id must be a short safe identifier")
    inputs = case.get("inputs")
    if not isinstance(inputs, dict) or not 1 <= len(inputs) <= 8:
        raise Rejected("each case requires one to eight inputs")
    if any(not NAME.fullmatch(name) for name in inputs):
        raise Rejected("input name is not a safe identifier")
    values = {name: read_fraction(pair) for name, pair in inputs.items()}
    uses = Counter()
    nodes = scan_expression(case.get("expression"), values, uses)
    if uses != Counter({name: 1 for name in values}):
        raise Rejected("native linear scope requires each declared input exactly once")
    if nodes > FUEL:
        raise Rejected("case AST admission exceeds native fuel 16")
    metrics["admitted_ast_nodes"] += nodes
    if metrics["admitted_ast_nodes"] * 4 > MAX_AST_NODES:
        raise Rejected("four fixed mathematical passes would exceed 128 AST steps")
    required = case.get("guard", {}).get("required_nonzero_inputs", [])
    if not isinstance(required, list) or any(name not in values for name in required):
        raise Rejected("nonzero guard references undeclared inputs")
    return values, nodes


def native_limits():
    import resource
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_NATIVE_FILE_BYTES, MAX_NATIVE_FILE_BYTES))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_AS, (536870912, 536870912))


def run_native(backend, program_path, result_path, deadline, metrics):
    left = (deadline - clock()) / 1e9
    if left <= 0:
        raise Unknown("total wall budget exhausted before native launch")
    timeout = min(NATIVE_SECONDS, left)
    stdout_path = result_path.with_suffix(".stdout.txt")
    stderr_path = result_path.with_suffix(".stderr.txt")
    started = clock()
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        kwargs = {"stdout": stdout, "stderr": stderr, "stdin": subprocess.DEVNULL,
                  "start_new_session": True}
        if os.name == "posix":
            kwargs["preexec_fn"] = native_limits
        proc = subprocess.Popen([str(backend), "run", str(program_path), "--output", str(result_path)], **kwargs)
        metrics["native_launches"] += 1
        try:
            try:
                returncode = proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired as error:
                raise Unknown("native execution reached its wall-time bound") from error
        finally:
            if os.name == "posix":
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            elif proc.poll() is None:
                proc.kill()
            proc.wait()
            metrics["native_wall_ns"] += clock() - started
    if returncode != 0:
        raise Unknown(f"native backend exited with code {returncode}; raw files retained")
    if not result_path.is_file() or result_path.stat().st_size > MAX_NATIVE_FILE_BYTES:
        raise Unknown("native report missing or oversized")
    report_raw = result_path.read_bytes()
    return parse_json(report_raw), hashlib.sha256(report_raw).hexdigest()


def observe(case, exact_inputs, metrics, deadline):
    raw_start = clock()
    float_inputs = {name: finite_float(value) for name, value in exact_inputs.items()}
    raw_vf = raw_float_eval(case["expression"], float_inputs, metrics, deadline)
    raw_ns = clock() - raw_start
    metrics["raw_float_ns"] += raw_ns
    start = clock()
    rounded_inputs = {name: bounded(Fraction.from_float(value)) for name, value in float_inputs.items()}
    v = exact_eval(case["expression"], exact_inputs, metrics, deadline)
    vq = exact_eval(case["expression"], rounded_inputs, metrics, deadline)
    trace = []
    vf = float_eval(case["expression"], float_inputs, trace, metrics, deadline)
    if vf.hex() != raw_vf.hex():
        raise RuntimeError("traced and plain binary64 evaluation disagreed")
    lifted_vf = bounded(Fraction.from_float(vf))
    input_delta = bounded(vq - v)
    operation_delta = bounded(lifted_vf - vq)
    total_delta = bounded(lifted_vf - v)
    if bounded(input_delta + operation_delta) != total_delta:
        raise RuntimeError("residual decomposition invariant failed")
    intended_class, observed_class = classify(v), classify(vf)
    guard_names = case.get("guard", {}).get("required_nonzero_inputs", [])
    guard_exact = all(exact_inputs[name] != 0 for name in guard_names)
    guard_rounded = all(float_inputs[name] != 0 for name in guard_names)
    predicate_matches = intended_class == observed_class
    gate = ("exact-oracle-confirmed" if predicate_matches and guard_exact and guard_rounded
            else "refuted" if not predicate_matches else "guard-refused")
    expected = case.get("expected", {})
    checks = {}
    if "exact" in expected:
        checks["exact"] = v == read_fraction(expected["exact"])
    if "float_hex" in expected:
        checks["float_hex"] = vf.hex() == expected["float_hex"]
    if "classifier" in expected:
        checks["classifier"] = observed_class == expected["classifier"]
    if "exactclass" in expected:
        checks["exactclass"] = intended_class == expected["exactclass"]
    if not all(checks.values()):
        raise Rejected(f"frozen expectation mismatch: {checks}")
    result = {
        "id": case["id"], "role": case.get("role"), "state": "Completed",
        "exact_intention": fraction_pair(v), "exact_after_input_rounding": fraction_pair(vq),
        "float_output_hex": vf.hex(), "float_output_exact": fraction_pair(lifted_vf),
        "correctly_rounded_intention_hex": finite_float(v).hex(),
        "commuting_at_this_point": finite_float(v).hex() == vf.hex(),
        "full_exact_value_preserved": v == lifted_vf,
        "residuals": {"input": fraction_pair(input_delta), "operations": fraction_pair(operation_delta),
                      "total": fraction_pair(total_delta), "sum_checked": True},
        "input_observation": {name: {"intended": fraction_pair(exact_inputs[name]),
                                     "binary64_hex": value.hex(),
                                     "rounded_exact": fraction_pair(rounded_inputs[name])}
                              for name, value in float_inputs.items()},
        "ordered_trace": trace,
        "guard": {"required_nonzero_inputs": guard_names, "exact_passed": guard_exact,
                  "rounded_passed": guard_rounded, "scope": "declared point only"},
        "scalar_predicate": {"intended": intended_class, "observed": observed_class,
                             "matches": predicate_matches, "gate": gate,
                             "scope": "only zero/one/other at this finite point; no Seal/M1"},
        "expectation_checks": checks,
        "raw_float_ns": raw_ns,
    }
    result["oracle_validation_ns"] = clock() - start
    metrics["oracle_validation_ns"] += result["oracle_validation_ns"]
    return result, float_inputs


def match_native(report, program, program_raw, float_inputs, observed):
    if (report.get("schema") != "adva.run.report.research" or type(report.get("version")) is not int
            or report["version"] != 0 or report.get("state") != "Completed"):
        raise Unknown("native report is not a completed known-schema run")
    native_program = report.get("program", {})
    if report.get("program_json") != program_raw.decode():
        raise Unknown("native report did not preserve the submitted exact program bytes")
    if any(native_program.get(key) != program[key] for key in ("schema", "version", "source", "module", "entry", "fuel")):
        raise Unknown("native report does not bind the submitted program")
    actual_inputs = native_program.get("inputs", {})
    input_matches = set(actual_inputs) == set(float_inputs) and all(
        type(actual_inputs[name]) in (float, int)
        and finite_float(actual_inputs[name]).hex() == float_inputs[name].hex() for name in float_inputs)
    values = report.get("evaluation", {}).get("values", [])
    if not isinstance(values, list) or len(values) != 1 or type(values[0]) not in (float, int):
        raise Unknown("native report must contain one scalar output")
    native_hex = finite_float(values[0]).hex()
    output_matches = native_hex == observed["float_output_hex"]
    if not input_matches or not output_matches:
        raise Unknown("native/Python input rounding or ordered output differed; raw reports retained")
    return {"state": "Completed", "input_rounding_matches": input_matches,
            "output_matches": output_matches, "output_hex": native_hex,
            "native_actual": report.get("actual"), "native_phase_seconds": report.get("phase_seconds")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--backend", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    started = clock()
    deadline = started + int(TOTAL_SECONDS * 1e9)
    tracemalloc.start()
    metrics = {"admitted_ast_nodes": 0, "exact_ast_visits": 0, "float_ast_visits": 0,
               "trace_ast_visits": 0, "raw_float_ns": 0,
               "native_launches": 0, "native_wall_ns": 0, "construction_ns": 0,
               "oracle_validation_ns": 0, "serialization_ns": 0}
    report = {"schema": "adva.representation-report.research", "version": 0,
              "state": "Unknown", "native_state": "NativeNotRun" if args.backend is None else "Pending",
              "execution_mode": "external_only" if args.backend is None else "external_oracle_plus_native",
              "authority": "Python exact finite oracle; no native exact-arithmetic theorem or universal syntax claim",
              "cases": [], "actual": metrics,
              "limits": {"cases": MAX_CASES, "mathematical_ast_steps": MAX_AST_NODES,
                         "admitted_ast_nodes_for_four_passes": MAX_AST_NODES // 4,
                         "fraction_bits": MAX_FRACTION_BITS, "source_bytes_per_case": MAX_SOURCE_BYTES,
                         "native_fuel_per_case": FUEL, "native_seconds_per_call": NATIVE_SECONDS,
                         "wall_seconds_total": TOTAL_SECONDS, "search_candidates": 0, "retries": 0}}
    failed = False
    try:
        if not (sys.float_info.radix == 2 and sys.float_info.mant_dig == 53
                and sys.float_info.max_exp == 1024 and sys.float_info.min_exp == -1021
                and sys.float_info.rounds == 1):
            raise Rejected("Python host is outside binary64 round-to-nearest assumptions")
        if args.question.stat().st_size > MAX_QUESTION_BYTES:
            raise Rejected("question exceeds 65536 bytes")
        raw = args.question.read_bytes()
        question = parse_json(raw)
        report["question_sha256"] = hashlib.sha256(raw).hexdigest()
        if (not isinstance(question, dict) or question.get("schema") != QUESTION_SCHEMA
                or type(question.get("version")) is not int or question["version"] != 0):
            raise Rejected("unknown question schema/version")
        required_budget = {"max_cases": MAX_CASES, "max_ast_steps": MAX_AST_NODES,
                           "fraction_bits": MAX_FRACTION_BITS, "total_seconds": TOTAL_SECONDS,
                           "native_call_seconds": NATIVE_SECONDS, "native_virtual_memory_kib": 524288,
                           "native_fuel": FUEL, "search_candidates": 0}
        if any(question.get("budget", {}).get(key) != value for key, value in required_budget.items()):
            raise Rejected("question budget differs from this frozen runner's supported budget")
        cases = question.get("cases")
        if not isinstance(cases, list) or not 1 <= len(cases) <= MAX_CASES:
            raise Rejected("question requires one to eight cases")
        if len({case.get("id") for case in cases if isinstance(case, dict)}) != len(cases):
            raise Rejected("case IDs must be distinct")
        prepared = [(case, *inspect_case(case, metrics)) for case in cases]
        backend = args.backend.resolve() if args.backend else None
        if backend and (not backend.is_file() or not os.access(backend, os.X_OK)):
            raise Rejected("requested native backend is not an executable file")
        if backend:
            if backend.stat().st_size > 67108864:
                raise Rejected("backend exceeds 64 MiB provenance hashing bound")
            digest = hashlib.sha256()
            with backend.open("rb") as stream:
                while chunk := stream.read(1048576):
                    digest.update(chunk)
            report["native_backend_sha256"] = digest.hexdigest()
        create_file(args.output_dir / "question.adva", raw)
        native_stopped = False
        for case, exact_inputs, nodes in prepared:
            result = {"id": case["id"], "state": "Unknown", "native": {"state": "NativeNotRun"}}
            try:
                if clock() >= deadline:
                    raise Unknown("total wall budget exhausted")
                construction_start = clock()
                program = render_program(case, exact_inputs)
                program_raw = encode(program)
                program_path = args.output_dir / f"{case['id']}.program.adva"
                create_file(program_path, program_raw)
                metrics["construction_ns"] += clock() - construction_start
                result, float_inputs = observe(case, exact_inputs, metrics, deadline)
                result["admitted_ast_nodes"] = nodes
                result["program_sha256"] = hashlib.sha256(program_raw).hexdigest()
                result["native"] = {"state": "NativeNotRun", "reason": "backend absent" if not backend else "prior native failure"}
                if backend and not native_stopped:
                    result_path = args.output_dir / f"{case['id']}.native-result.adva"
                    try:
                        native_report, native_hash = run_native(backend, program_path, result_path, deadline, metrics)
                        result["native"] = match_native(native_report, program, program_raw, float_inputs, result)
                        result["native"]["report_sha256"] = native_hash
                    except (Unknown, Rejected, OSError, ValueError, KeyError, TypeError) as error:
                        result["native"] = {"state": "Unknown", "reason": str(error)}
                        native_stopped = True
                        failed = True
            except (Rejected, Unknown, OSError, ValueError, KeyError, TypeError) as error:
                result.update(state="Rejected" if isinstance(error, Rejected) else "Unknown", reason=str(error))
                failed = True
            report["cases"].append(result)
        completed = [case for case in report["cases"] if case["state"] == "Completed"]
        false_zero = [case for case in completed if case["scalar_predicate"]["observed"] == "zero"
                      and case["scalar_predicate"]["intended"] != "zero"]
        false_one = [case for case in completed if case["scalar_predicate"]["observed"] == "one"
                     and case["scalar_predicate"]["intended"] != "one"]
        false_cases = false_zero + false_one
        report["comparison"] = {"same_finite_cases": len(completed),
                                "raw_false_zero": [case["id"] for case in false_zero],
                                "raw_false_one": [case["id"] for case in false_one],
                                "accepted_false_with_exact_oracle_gate": sum(
                                    case["scalar_predicate"]["gate"] == "exact-oracle-confirmed" for case in false_cases),
                                "incremental_oracle_validation_ns": metrics["oracle_validation_ns"],
                                "raw_binary64_baseline_ns": metrics["raw_float_ns"],
                                "claim": "pointwise oracle checks only; no acceleration or scope-coverage claim"}
        report["native_state"] = ("NativeNotRun" if not backend else
                                  "Completed" if all(case.get("native", {}).get("state") == "Completed"
                                                     for case in report["cases"]) else "Incomplete")
        report["state"] = "Incomplete" if failed else "Completed"
    except (Rejected, Unknown, OSError, ValueError, KeyError, TypeError) as error:
        report.update(state="Rejected" if isinstance(error, Rejected) else "Unknown", reason=str(error))
        failed = True
    metrics["elapsed_ns_before_final_serialization"] = clock() - started
    metrics["python_tracemalloc_peak_bytes_before_final_serialization"] = tracemalloc.get_traced_memory()[1]
    metrics["process_peak_rss_bytes"] = None
    metrics["native_peak_rss_bytes"] = None
    metrics["memory_note"] = "tracemalloc covers this Python process's traced allocations only; RSS and native peaks unmeasured"
    serialization_start = clock()
    encode(report)
    metrics["serialization_ns"] = clock() - serialization_start
    metrics["serialization_note"] = "one complete report encoding measured; final encoding and disk persistence excluded"
    create_file(args.output_dir / "report.json", encode(report))
    tracemalloc.stop()
    print(json.dumps({"state": report["state"], "native_state": report["native_state"],
                      "cases": len(report["cases"]), "report": str(args.output_dir / "report.json")}))
    return int(failed)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OSError as error:
        print(f"report persistence failed: {error}", file=sys.stderr)
        raise SystemExit(2)
