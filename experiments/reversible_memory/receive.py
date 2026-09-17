#!/usr/bin/env python3
"""Independent finite receiver for reversible-memory v0.

Project-original contribution by ChatGPT (OpenAI), through Mingli Yuan's
account proxy, under Unknown v0.3. No producer or external oracle imports.
The complete supplied joint law is an assumption, not inferred evidence.
"""
from __future__ import annotations

import argparse
import json
import math
import resource
import signal
import sys
import time
from fractions import Fraction

PROFILE = "adva.research.reversible-memory.v0"
EXPECTED_FIELDS = {"question", "system_states", "environment", "horizon", "schedule",
                   "initial_joint", "flip_rate", "history", "scope"}
CANDIDATE_FIELDS = {"profile", "request", "micro", "trace", "claim"}
TRACE_FIELDS = {"step", "law", "predicted_law", "marginal_match", "adjacent_match",
                "history_match", "positive_histories", "null_histories", "witness"}
LIMIT_WORK = 6000
LIMIT_INPUT = 65536
LIMIT_OUTPUT = 262144
LIMIT_BITS = 512
START = time.monotonic()
WORK = 0


class Rejection(Exception):
    pass


class Exhausted(Exception):
    pass


def require(ok, reason):
    if not ok:
        raise Rejection(reason)


def tick(amount=1):
    global WORK
    if WORK + amount > LIMIT_WORK:
        raise Exhausted("work-limit")
    WORK += amount
    if time.monotonic() - START > 3:
        raise Exhausted("wall-limit")


def alarm_handler(_signum, _frame):
    raise Exhausted("process-time-limit")


def integer_bound(value):
    if abs(value).bit_length() > LIMIT_BITS:
        raise Exhausted("arithmetic-bit-limit")
    return value


def bounded(value):
    integer_bound(value.numerator)
    integer_bound(value.denominator)
    return value


def add(a, b):
    x = integer_bound(a.numerator * b.denominator)
    y = integer_bound(b.numerator * a.denominator)
    d = integer_bound(a.denominator * b.denominator)
    return bounded(Fraction(integer_bound(x + y), d))


def mul(a, b):
    n = integer_bound(a.numerator * b.numerator)
    d = integer_bound(a.denominator * b.denominator)
    return bounded(Fraction(n, d))


def wire(value):
    return [value.numerator, value.denominator]


def fraction(value):
    require(type(value) is list and len(value) == 2, "rational-shape")
    n, d = value
    require(type(n) is int and type(d) is int, "rational-integer-type")
    require(0 <= n <= 4096 and 1 <= d <= 4096, "rational-input-bound")
    require(math.gcd(n, d) == 1, "rational-not-canonical")
    return Fraction(n, d)


def exact_keys(value, fields, label):
    require(type(value) is dict and set(value) == fields, label + "-fields")


def strict_equal(a, b):
    """JSON comparison that never identifies True with 1 or 1.0 with 1."""
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return set(a) == set(b) and all(strict_equal(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(strict_equal(x, y) for x, y in zip(a, b))
    return a == b


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate-json-key")
        result[key] = value
    return result


def reject_constant(value):
    raise Rejection("nonfinite-json-number:" + value)


def read_json(path):
    with open(path, "rb") as stream:
        raw = stream.read(LIMIT_INPUT + 1)
    require(len(raw) <= LIMIT_INPUT, "input-byte-limit")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise Rejection("invalid-json:" + type(exc).__name__) from exc


def label(value):
    require(type(value) is str and 1 <= len(value) <= 64, "bounded-label")


def labels(value, low, high, unique=False):
    require(type(value) is list and low <= len(value) <= high, "label-list-bound")
    for item in value:
        label(item)
    if unique:
        require(len(set(value)) == len(value), "duplicate-label")


def context(value):
    exact_keys(value, EXPECTED_FIELDS, "expected")
    label(value["question"])
    labels(value["system_states"], 2, 2, unique=True)
    labels(value["environment"], 1, 6, unique=True)
    labels(value["history"], 1, 4)
    m = len(value["environment"])
    horizon = value["horizon"]
    require(type(horizon) is int and 0 <= horizon <= 6, "horizon-bound")
    schedule = value["schedule"]
    require(type(schedule) is list and len(schedule) == horizon, "schedule-coverage")
    require(all(type(j) is int and 0 <= j < m for j in schedule), "schedule-index")
    require(value["scope"] == "finite-reversible-bit-environment", "scope")
    dense = value["initial_joint"]
    require(type(dense) is list and len(dense) == 2 ** (m + 1), "dense-joint-coverage")
    masses = []
    total = Fraction(0)
    for raw in dense:
        tick()
        probability = fraction(raw)
        masses.append(probability)
        total = add(total, probability)
    require(total == 1, "joint-not-normalized")
    q = fraction(value["flip_rate"])
    require(q <= 1, "flip-rate-range")
    return m, horizon, schedule, masses, q


def gate(state, index, m):
    """Apply U_index using the independently specified dense bit encoding."""
    width = 1 << m
    env = state % width
    flip = (env >> (m - 1 - index)) & 1
    return state ^ (flip << m)


def check_micro(m, schedule):
    states = 1 << (m + 1)
    visits = 0
    for index in schedule:
        seen = set()
        for state in range(states):
            tick()
            seen.add(gate(state, index, m))
            visits += 1
        require(seen == set(range(states)), "internal-gate-not-bijective")
    for state in range(states):
        tick()
        moved = state
        for index in schedule:
            tick()
            moved = gate(moved, index, m)
        for index in reversed(schedule):
            tick()
            moved = gate(moved, index, m)
        require(moved == state, "internal-roundtrip-failure")
    return {"states": states, "gate_bijections": visits, "roundtrip_states": states}


def initial_law(m, masses):
    result = [Fraction(0), Fraction(0)]
    for state, probability in enumerate(masses):
        tick()
        system = state >> m
        result[system] = add(result[system], probability)
    return result


def row_truth(step, index, m, masses, packed_paths, current, previous_law, q):
    """Enumerate exact path masses; packed history integers give lex order."""
    histories = [Fraction(0) for _ in range(1 << step)]
    flipped = [Fraction(0) for _ in range(1 << step)]
    law = [Fraction(0), Fraction(0)]
    adjacent = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(0)]]
    for state, probability in enumerate(masses):
        tick()
        previous = current[state] >> m
        history = packed_paths[state]
        next_state = gate(current[state], index, m)
        following = next_state >> m
        histories[history] = add(histories[history], probability)
        if previous != following:
            flipped[history] = add(flipped[history], probability)
        law[following] = add(law[following], probability)
        adjacent[previous][following] = add(adjacent[previous][following], probability)
        packed_paths[state] = (history << 1) | following
        current[state] = next_state
    stay = add(Fraction(1), -q)
    predicted = [add(mul(previous_law[0], stay), mul(previous_law[1], q)),
                 add(mul(previous_law[0], q), mul(previous_law[1], stay))]
    adjacent_match = True
    for before in range(2):
        for after in range(2):
            tick()
            expected = mul(previous_law[before], stay if before == after else q)
            if adjacent[before][after] != expected:
                adjacent_match = False
    positive = 0
    witness = None
    for history in range(1 << step):
        tick()
        mass = histories[history]
        if mass == 0:
            continue
        positive += 1
        wanted = mul(q, mass)
        if flipped[history] != wanted and witness is None:
            bits = [(history >> (step - 1 - j)) & 1 for j in range(step)]
            witness = {"history": bits, "history_mass": wire(mass),
                       "flip_mass": wire(flipped[history]),
                       "required_flip_mass": wire(wanted)}
    return {"step": step, "law": list(map(wire, law)),
            "predicted_law": list(map(wire, predicted)),
            "marginal_match": law == predicted, "adjacent_match": adjacent_match,
            "history_match": witness is None, "positive_histories": positive,
            "null_histories": (1 << step) - positive, "witness": witness}, law


def empty_result():
    return {"profile": PROFILE, "outcome": "ImplementationFailure", "reason": "not-started",
            "expected_request": None, "verified_prefix": [], "accepted_result": None,
            "obstruction": None, "verified_counterexample": None,
            "native_authority": False, "close_authorized": False, "free_authorized": False,
            "work_units": 0, "wall_seconds": 0.0}


def receive(expected_path, candidate_path, result):
    try:
        expected = read_json(expected_path)
        m, horizon, schedule, masses, q = context(expected)
    except Rejection as exc:
        result.update(outcome="InvalidContext", reason=str(exc))
        return
    result["expected_request"] = expected
    try:
        candidate = read_json(candidate_path)
        exact_keys(candidate, CANDIDATE_FIELDS, "candidate")
        require(type(candidate["profile"]) is str and candidate["profile"] == PROFILE,
                "profile-mismatch")
        require(strict_equal(candidate["request"], expected), "request-mismatch")
        exact_keys(candidate["micro"], {"states", "gate_bijections", "roundtrip_states"}, "micro")
        require(strict_equal(candidate["micro"], check_micro(m, schedule)), "micro-mismatch")
        trace = candidate["trace"]
        require(type(trace) is list and len(trace) <= horizon, "trace-coverage-bound")
        exact_keys(candidate["claim"], {"kind", "first_failure"}, "claim")
        claim = candidate["claim"]
        require(type(claim["kind"]) is str and claim["kind"] in
                {"VerifiedMarkovHorizon", "Counterexample", "UnknownCoverage"}, "claim-kind")
        first = claim["first_failure"]
        require(first is None or (type(first) is int and 1 <= first <= horizon), "claim-first-failure")
        states = 1 << (m + 1)
        current = list(range(states))
        packed_paths = [state >> m for state in range(states)]
        previous_law = initial_law(m, masses)
        for row_index, supplied in enumerate(trace):
            step = row_index + 1
            exact_keys(supplied, TRACE_FIELDS, "trace-row")
            truth, next_law = row_truth(step, schedule[row_index], m, masses,
                                        packed_paths, current, previous_law, q)
            require(strict_equal(supplied, truth), "trace-row-mismatch:" + str(step))
            result["verified_prefix"].append(truth)
            if truth["witness"] is not None and result["verified_counterexample"] is None:
                result["verified_counterexample"] = {"step": step, **truth["witness"]}
            previous_law = next_law
        if len(trace) < horizon:
            first = (result["verified_counterexample"]["step"]
                     if result["verified_counterexample"] is not None else None)
            require(strict_equal(claim, {"kind": "UnknownCoverage", "first_failure": first}),
                    "partial-claim-mismatch")
            result.update(outcome="UnknownCoverage", reason="missing-complete-steps",
                          obstruction={"missing_steps": list(range(len(trace) + 1, horizon + 1))})
            return
        first = (result["verified_counterexample"]["step"]
                 if result["verified_counterexample"] is not None else None)
        kind = "Counterexample" if first is not None else "VerifiedMarkovHorizon"
        wanted_claim = {"kind": kind, "first_failure": first}
        require(strict_equal(claim, wanted_claim), "claim-mismatch")
        result.update(outcome=kind, reason="complete-finite-check", accepted_result=wanted_claim)
    except Rejection as exc:
        result.update(outcome="InvalidEvidence", reason=str(exc))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    result = empty_result()
    try:
        resource.setrlimit(resource.RLIMIT_AS, (134217728, 134217728))
        # Exit before the hard ceiling so UnknownBudget can retain the prefix.
        resource.setrlimit(resource.RLIMIT_CPU, (2, 3))
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.signal(signal.SIGXCPU, alarm_handler)
        signal.setitimer(signal.ITIMER_REAL, 2.8)
        receive(args.expected, args.candidate, result)
    except (Exhausted, MemoryError) as exc:
        result.update(outcome="UnknownBudget", reason=str(exc) or "memory-limit")
    except Exception as exc:
        result.update(outcome="ImplementationFailure", reason=type(exc).__name__)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    result["work_units"] = WORK
    result["wall_seconds"] = time.monotonic() - START
    encoded = json.dumps(result, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
    if len(encoded.encode("utf-8")) > LIMIT_OUTPUT:
        result.update(outcome="UnknownBudget", reason="output-byte-limit", accepted_result=None,
                      obstruction=None)
        encoded = json.dumps(result, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
        if len(encoded.encode("utf-8")) > LIMIT_OUTPUT:
            # The validated profile bounds make this unreachable; never silently
            # trim verified history to disguise a serialization budget breach.
            raise Exhausted("retained-result-output-byte-limit")
    sys.stdout.write(encoded)


if __name__ == "__main__":
    main()
