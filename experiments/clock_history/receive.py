#!/usr/bin/env python3
"""Original independent clock/history receiver, contributed under Unknown v0.3.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
account use is not Mingli's authorship, review, or a correctness guarantee.
The embedded receiver is imported only after checking its frozen SHA-256.
No producer or external paper content is incorporated.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import signal
import sys
import tempfile
import time

PROFILE = "adva.research.clock-history.v0"
DEPENDENCY_SHA256 = "6a8cfe9f48b2485b1a4a2ca17199168b10005617e6dae19509d4597da0e15d7d"
EXPECTED_FIELDS = {"question", "history", "scope", "clocks", "edges", "events", "micro_request"}
CANDIDATE_FIELDS = {"profile", "request", "calibration", "events", "micro"}
START = time.monotonic()
OLD = None


class BudgetExceeded(Exception):
    pass


def stop_at_limit(_signum, _frame):
    raise BudgetExceeded("process-time-limit")


def dependency():
    path = Path(__file__).resolve().parent.parent / "reversible_memory" / "receive.py"
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != DEPENDENCY_SHA256:
        raise RuntimeError("frozen-dependency-sha256-mismatch")
    spec = importlib.util.spec_from_file_location("clock_history_frozen_receiver", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("frozen-dependency-load-failure")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Do not reset START, WORK, or any receiving function in the imported module.
    return module


def rational(value):
    OLD.require(type(value) is list and len(value) == 2, "signed-rational-shape")
    n, d = value
    OLD.require(type(n) is int and type(d) is int, "signed-rational-integer-type")
    OLD.require(abs(n) <= 4096 and 1 <= d <= 4096, "signed-rational-input-bound")
    result = Fraction(n, d)
    OLD.require(result.numerator == n and result.denominator == d, "signed-rational-not-canonical")
    return result


def context(expected):
    OLD.exact_keys(expected, EXPECTED_FIELDS, "expected")
    OLD.label(expected["question"])
    OLD.labels(expected["history"], 1, 4)
    OLD.require(expected["scope"] == "finite-clock-calibration-and-observed-history", "scope")
    OLD.labels(expected["clocks"], 3, 3, unique=True)
    micro = OLD.context(expected["micro_request"])
    m, horizon = micro[:2]
    OLD.require(1 <= m <= 3 and 1 <= horizon <= 3, "clock-profile-micro-bound")
    edges = expected["edges"]
    OLD.require(type(edges) is list and len(edges) == 3, "three-oriented-edges")
    matrices = []
    for edge in edges:
        OLD.tick()
        OLD.exact_keys(edge, {"rate", "offset"}, "edge")
        rate, offset = rational(edge["rate"]), rational(edge["offset"])
        OLD.require(rate > 0, "clock-rate-not-positive")
        matrices.append(((rate, offset), (Fraction(0), Fraction(1))))
    events = expected["events"]
    OLD.require(type(events) is list and len(events) == horizon + 1, "event-context-coverage")
    ids = []
    instants = []
    for event in events:
        OLD.tick()
        OLD.exact_keys(event, {"id", "time"}, "event-context")
        OLD.label(event["id"])
        ids.append(event["id"])
        instant = rational(event["time"])
        OLD.require(not instants or instant > instants[-1], "event-times-not-increasing")
        instants.append(instant)
    OLD.require(len(set(ids)) == len(ids), "duplicate-event-id")
    return matrices, instants, horizon


def matrix_product(left, right):
    rows = []
    for i in range(2):
        row = []
        for j in range(2):
            entry = Fraction(0)
            for k in range(2):
                OLD.tick()
                entry = OLD.add(entry, OLD.mul(left[i][k], right[k][j]))
            row.append(entry)
        rows.append(tuple(row))
    return tuple(rows)


def apply(matrix, instant):
    # Homogeneous two-coordinate multiplication, not the producer's scalar loop.
    vector = (instant, Fraction(1))
    output = []
    for i in range(2):
        value = Fraction(0)
        for j in range(2):
            OLD.tick()
            value = OLD.add(value, OLD.mul(matrix[i][j], vector[j]))
        output.append(value)
    OLD.require(output[1] == 1, "internal-non-affine-result")
    return output[0]


def calibration(matrices):
    product = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))
    for matrix in matrices:
        product = matrix_product(matrix, product)
    rate, offset = product[0]
    OLD.require(product[1] == (Fraction(0), Fraction(1)), "internal-affine-product")
    kind = "ClockInconsistent" if rate != 1 else "RateConsistent" if offset != 0 else "ClockConsistent"
    return {"rate": OLD.wire(rate), "offset": OLD.wire(offset), "kind": kind}


def event_truth(event_id, instant, matrices):
    readings = [instant]
    for matrix in matrices[:2]:
        readings.append(apply(matrix, readings[-1]))
    roundtrip = apply(matrices[2], readings[-1])
    return {"id": event_id, "readings": [OLD.wire(x) for x in readings],
            "roundtrip": OLD.wire(roundtrip)}


def empty_result():
    return {"profile": PROFILE, "outcome": "ImplementationFailure", "reason": "not-started",
            "expected_request": None, "verified_calibration": None, "verified_events": [],
            "micro_result": None, "dynamics_outcome": None, "verified_counterexample": None,
            "obstruction": None, "work_units": 0, "wall_seconds": 0.0,
            "native_authority": False, "close_authorized": False, "free_authorized": False}


def receive_micro(expected, candidate, result):
    inner = OLD.empty_result()
    result["micro_result"] = inner
    work_before = OLD.WORK
    start = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix="adva-clock-history-") as temp:
            expected_path = Path(temp) / "expected.json"
            candidate_path = Path(temp) / "candidate.json"
            for path, value in ((expected_path, expected), (candidate_path, candidate)):
                encoded = json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False)
                OLD.require(len(encoded.encode("utf-8")) <= OLD.LIMIT_INPUT, "embedded-input-byte-limit")
                path.write_text(encoded, encoding="utf-8")
            # Invoke the frozen public file-based receiving API unchanged.
            OLD.receive(str(expected_path), str(candidate_path), inner)
    except (OLD.Exhausted, BudgetExceeded, MemoryError) as exc:
        inner.update(outcome="UnknownBudget", reason=str(exc) or "memory-limit")
        raise
    except Exception as exc:
        inner.update(outcome="ImplementationFailure", reason=type(exc).__name__)
        raise
    finally:
        inner["work_units"] = OLD.WORK - work_before
        inner["wall_seconds"] = time.monotonic() - start
        result["dynamics_outcome"] = inner["outcome"]
        result["verified_counterexample"] = inner["verified_counterexample"]


def receive(expected_path, candidate_path, result):
    try:
        expected = OLD.read_json(expected_path)
        matrices, instants, horizon = context(expected)
    except OLD.Rejection as exc:
        result.update(outcome="InvalidContext", reason=str(exc))
        return
    result["expected_request"] = expected
    try:
        candidate = OLD.read_json(candidate_path)
        OLD.exact_keys(candidate, CANDIDATE_FIELDS, "candidate")
        OLD.require(type(candidate["profile"]) is str and candidate["profile"] == PROFILE,
                    "profile-mismatch")
        OLD.require(OLD.strict_equal(candidate["request"], expected), "request-mismatch")
        OLD.exact_keys(candidate["calibration"], {"rate", "offset", "kind"}, "calibration")
        checked_calibration = calibration(matrices)
        OLD.require(OLD.strict_equal(candidate["calibration"], checked_calibration), "calibration-mismatch")
        result["verified_calibration"] = checked_calibration
        events = candidate["events"]
        OLD.require(type(events) is list and len(events) <= horizon + 1, "event-evidence-coverage")
        for index, event in enumerate(events):
            OLD.exact_keys(event, {"id", "readings", "roundtrip"}, "event-evidence")
            truth = event_truth(expected["events"][index]["id"], instants[index], matrices)
            OLD.require(OLD.strict_equal(event, truth), "event-mismatch:" + str(index))
            result["verified_events"].append(truth)
        receive_micro(expected["micro_request"], candidate["micro"], result)
        dynamics = result["dynamics_outcome"]
        if dynamics not in {"VerifiedMarkovHorizon", "Counterexample", "UnknownCoverage"}:
            result.update(outcome=dynamics, reason="micro:" + result["micro_result"]["reason"])
            return
        missing = [event["id"] for event in expected["events"][len(events):]]
        if missing or dynamics == "UnknownCoverage":
            result.update(outcome="UnknownCoverage", reason="incomplete-event-or-dynamics-coverage",
                          obstruction={"missing_events": missing,
                                       "micro": result["micro_result"]["obstruction"]})
            return
        if checked_calibration["kind"] != "ClockConsistent":
            result.update(outcome="CalibrationObstruction", reason="clock-loop-not-identity",
                          obstruction=checked_calibration)
            return
        result.update(outcome="VerifiedTransport", reason="complete-clock-and-history-transport")
    except OLD.Rejection as exc:
        result.update(outcome="InvalidEvidence", reason=str(exc))


def main():
    global OLD
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    result = empty_result()
    try:
        resource.setrlimit(resource.RLIMIT_AS, (134217728, 134217728))
        resource.setrlimit(resource.RLIMIT_CPU, (2, 3))
        signal.signal(signal.SIGALRM, stop_at_limit)
        signal.signal(signal.SIGXCPU, stop_at_limit)
        signal.setitimer(signal.ITIMER_REAL, 2.8)
        OLD = dependency()
        receive(args.expected, args.candidate, result)
    except (BudgetExceeded, MemoryError) as exc:
        result.update(outcome="UnknownBudget", reason=str(exc) or "memory-limit")
    except Exception as exc:
        if OLD is not None and isinstance(exc, OLD.Exhausted):
            result.update(outcome="UnknownBudget", reason=str(exc))
        else:
            result.update(outcome="ImplementationFailure", reason=type(exc).__name__ + ":" + str(exc))
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    result["work_units"] = OLD.WORK if OLD is not None else 0
    result["wall_seconds"] = time.monotonic() - START
    encoded = json.dumps(result, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(",", ":")) + "\n"
    if len(encoded.encode("utf-8")) > 262144:
        # Validated bounds make this unreachable; preserve every checked component.
        raise BudgetExceeded("retained-result-output-byte-limit")
    sys.stdout.write(encoded)


if __name__ == "__main__":
    main()
