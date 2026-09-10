"""Bounded chart calibration. Python never builds or authorizes a native IR."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import resource
import signal
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
NAMES = ("reference", "transported", "wrong-dual")


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def dot(x, y):
    return sum(a * b for a, b in zip(x, y, strict=True))


def matvec(a, x):
    return tuple(dot(row, x) for row in a)


def fixtures():
    vertices = sorted(set(
        tuple(s * x for s, x in zip(signs, perm, strict=True))
        for perm in itertools.permutations((0, 1, 2))
        for signs in itertools.product((-1, 1), repeat=3)
    ))
    axes = [tuple(sign if j == i else 0 for j in range(3))
            for i in range(3) for sign in (-1, 1)]
    signs = list(itertools.product((-1, 1), repeat=3))
    numerators = [tuple(3 * v for v in axis) for axis in axes]
    numerators += [tuple(2 * v for v in sign) for sign in signs]
    return [("to24", vertices, numerators, 6), ("cube-reuse", signs, axes, 1)]


def check_source(contract, source):
    require(digest(source) == contract["source_sha256"], "SourceDrift")


def exact_run(contract):
    start = time.perf_counter_ns()
    a, b = contract["A"], contract["B"]
    coefficient = [[sum(a[k][i] * b[k][j] for k in range(3))
                    for j in range(3)] for i in range(3)]
    require(coefficient == [[1, 0, 0], [0, 1, 0], [0, 0, 1]], "BadPairingLaw")
    rows, summaries = [], []
    for name, vertices, numerators, denominator in fixtures():
        require(denominator > 0, "InvalidDenominator")
        failures = 0
        for i, x in enumerate(vertices):
            for j, q in enumerate(numerators):
                require(len(rows) < contract["budget"]["max_pairs"], "PairBudget")
                ref = dot(x, q)
                right = dot(matvec(a, x), matvec(b, q))
                wrong = dot(matvec(a, x), matvec(a, q))
                require(ref == right, "PairingMismatch")
                require(all(abs(t) <= 3 for t in (*x, *q)), "InputRange")
                failures += wrong != ref
                reduced = Fraction(ref, denominator)
                rows.append({"fixture": name, "vertex": i, "dual": j,
                             "inputs": list(x + tuple(q)), "denominator": denominator,
                             "numerators": [ref, right, wrong],
                             "pairing": [reduced.numerator, reduced.denominator]})
        require(failures > 0, "NegativeControlUndetected")
        summaries.append({"fixture": name, "pairs": len(vertices) * len(numerators),
                          "wrong_dual_mismatches": failures})
    require(len(rows) == 384, "CoverageGap")
    return {"status": "ExternalExactPass", "coefficient_matrix": coefficient,
            "coefficient_checks": 9, "summaries": summaries, "rows": rows,
            "exact_ns": time.perf_counter_ns() - start}


def native_run(source, contract, rows):
    try:
        from adva import link_modules, load_program
    except ModuleNotFoundError as error:
        if error.name not in ("adva", "adva._native"):
            raise
        return {"status": "UnknownRuntime", "missing_module": error.name,
                "evaluations": 0, "compiled_programs": 0,
                "certificates": [], "native_ns": None}

    start = time.perf_counter_ns()
    workspace = link_modules([source.decode("utf-8")])
    functions, restored, records = [], [], []
    for name in NAMES:
        function = workspace.function("polar-pairing", name)
        require(list(function.signature.input_names) == contract["input_order"], "PortOrder")
        require(function.compilation_certificate is not None, "MissingCompilation")
        graft = function.graft_trace
        require(graft is not None, "MissingGraft")
        ir = function.ir
        require(len(ir["nodes"]) <= contract["budget"]["max_native_nodes_per_program"], "NodeBudget")
        copies = sum(node["operation"]["name"] == "copy" for node in ir["nodes"])
        require(copies == (0 if name == "reference" else 2), "ExplicitCopyBoundary")
        root = next(frame for frame in graft.result.frames if frame["id"] == graft.result.root)
        require([hole["hole"]["name"] for hole in root["holes"]] == contract["input_order"], "RootHoles")
        initial = function.causal_cut([])
        for hole in root["holes"]:
            require(hole["entry_wire"] in initial.frontier, "UnboundHole")
        binding = [{"coordinate_role": role, "hole": hole}
                   for role, hole in zip(contract["coordinate_roles"], root["holes"], strict=True)]
        entire = function.program_slice([], [node["id"] for node in ir["nodes"]])
        reloaded = load_program(json.dumps(ir))  # Rust import boundary, not serde-only.
        require(reloaded.ir == ir, "IRReplayMismatch")
        require(reloaded.history == function.history, "HistoryLost")
        require(reloaded.source_partition == function.source_partition, "SourceLost")
        require(reloaded.compilation_certificate is None and reloaded.graft_trace is None,
                "ImportedDiagramInventedCompilation")
        records.append({"name": name, "ir": ir, "graft": asdict(graft),
                        "binding": binding, "whole_slice": asdict(entire),
                        "compilation_certificate": function.compilation_certificate,
                        "validation_certificate": function.validation_certificate,
                        "reimport_certificate": reloaded.validation_certificate})
        functions.append(function)
        restored.append(reloaded)
    require(functions[0].history != functions[1].history, "HistoryCollapsed")

    compile_ns = time.perf_counter_ns() - start
    outputs = []
    eval_start = time.perf_counter_ns()
    evaluations = 0
    for row in rows:
        inputs = dict(zip(contract["input_order"], row["inputs"], strict=True))
        values = []
        for index, function in enumerate(functions):
            require(evaluations < contract["budget"]["max_native_evaluations"], "EvaluationBudget")
            result = function.evaluate_checked(inputs)
            evaluations += 1
            require(result.scalar == row["numerators"][index], "NativeValueMismatch")
            values.append({"value": result.scalar, "certificate": result.certificate})
        outputs.append(values)
    # New cube instance through the Rust import replay, retaining absent graft provenance.
    sample = next(row for row in rows if row["fixture"] == "cube-reuse")
    inputs = dict(zip(contract["input_order"], sample["inputs"], strict=True))
    for index, function in enumerate(restored):
        require(evaluations < contract["budget"]["max_native_evaluations"], "EvaluationBudget")
        require(function.evaluate(inputs) == sample["numerators"][index], "ReuseReplayMismatch")
        evaluations += 1
    return {"status": "FiniteNativePass", "compiled_programs": 3,
            "evaluations": evaluations, "compile_import_binding_ns": compile_ns,
            "evaluate_reuse_ns": time.perf_counter_ns() - eval_start,
            "native_ns": time.perf_counter_ns() - start,
            "records": records, "outputs": outputs}


def run():
    start = time.perf_counter_ns()
    contract_bytes = (HERE / "contract.json").read_bytes()
    contract = json.loads(contract_bytes)
    source = (ROOT / contract["source"]).read_bytes()
    check_source(contract, source)
    exact = exact_run(contract)
    try:
        check_source(contract, source + b"\n")
    except ValueError as error:
        require(str(error) == "SourceDrift", "WrongSourceRefusal")
    else:
        raise ValueError("SourceDriftAccepted")
    native = native_run(source, contract, exact["rows"])
    return {"schema": "adva.research.pairing-transport-evidence.v0",
            "contract_sha256": digest(contract_bytes), "source_sha256": digest(source),
            "adapter_sha256": digest(Path(__file__).read_bytes()),
            "exact": exact, "source_drift_control": "Rejected",
            "native": native, "total_before_serialization_ns": time.perf_counter_ns() - start,
            "rss_high_water_KiB_before_serialization": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "scope": "External exact chart check; native status is separate. No D*, free, Seal or mirror."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-native", action="store_true")
    args = parser.parse_args()
    budget = json.loads((HERE / "contract.json").read_text())["budget"]
    resource.setrlimit(resource.RLIMIT_CPU, (budget["cpu_seconds"], budget["cpu_seconds"]))
    resource.setrlimit(resource.RLIMIT_AS, (budget["address_space_bytes"], budget["address_space_bytes"]))
    resource.setrlimit(resource.RLIMIT_FSIZE, (budget["max_output_bytes"], budget["max_output_bytes"]))
    signal.alarm(budget["wall_seconds"])
    report = run()
    start = time.perf_counter_ns()
    encoded = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    require(json.loads(encoded) == report, "SerializationMismatch")
    codec_ns = time.perf_counter_ns() - start
    require(len(encoded.encode()) <= budget["max_output_bytes"], "OutputBudget")
    start = time.perf_counter_ns()
    with args.output.open("x") as stream:
        stream.write(encoded)
    write_ns = time.perf_counter_ns() - start
    print(json.dumps({"status": report["native"]["status"], "codec_ns": codec_ns,
                      "write_ns": write_ns, "output_bytes": len(encoded.encode()),
                      "rss_high_water_KiB_final": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))
    return 2 if args.require_native and report["native"]["status"] != "FiniteNativePass" else 0


if __name__ == "__main__":
    sys.exit(main())
