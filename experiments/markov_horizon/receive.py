#!/usr/bin/env python3
"""Original bounded Markov-horizon receiver, contributed under Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy; account use
is not his review, endorsement, or correctness guarantee. Scalar recurrences
are independent of the producer's row-matrix computation. No native authority.
"""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import resource
import signal
import time

PROFILE = "adva.research.markov-horizon.v0"
WORK = 0
ZERO = Fraction(0)
ONE = Fraction(1)
SUCCESS = {"CertifiedTolerance", "VerifiedHorizon"}


class Refusal(Exception):
    def __init__(self, outcome, reason):
        self.outcome, self.reason = outcome, reason


def demand(ok, reason):
    if not ok:
        raise ValueError(reason)


def tick(count=1):
    global WORK
    if WORK + count > 10000:
        raise Refusal("UnknownBudget", "receiver-work-limit")
    WORK += count


def integer_bound(value):
    if abs(value).bit_length() > 512:
        raise Refusal("UnknownBudget", "arithmetic-intermediate-bit-limit")
    return value


def bounded(value):
    integer_bound(value.numerator)
    integer_bound(value.denominator)
    return value


def add(left, right):
    tick()
    a = integer_bound(left.numerator * right.denominator)
    b = integer_bound(right.numerator * left.denominator)
    denominator = integer_bound(left.denominator * right.denominator)
    return bounded(Fraction(integer_bound(a + b), denominator))


def subtract(left, right):
    return add(left, -right)


def multiply(left, right):
    tick()
    numerator = integer_bound(left.numerator * right.numerator)
    denominator = integer_bound(left.denominator * right.denominator)
    return bounded(Fraction(numerator, denominator))


def scalar_step(point, intercept, slope):
    return add(intercept, multiply(slope, point))


def distance(left, right):
    return bounded(abs(subtract(left, right)))


def pair(value):
    return [value.numerator, value.denominator]


def keys(value, names, name):
    demand(type(value) is dict and set(value) == set(names), name + ":fields")


def label(value, name):
    demand(type(value) is str and 1 <= len(value) <= 80, name + ":label")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def rational(value, cap=None):
    tick()
    demand(type(value) is list and len(value) == 2, "rational:shape")
    a, b = value
    demand(type(a) is int and type(b) is int, "rational:integer-type")
    demand(b > 0, "rational:positive-denominator")
    if cap is not None:
        demand(abs(a) <= cap and b <= cap, "rational:bound")
    else:
        integer_bound(a)
        integer_bound(b)
    result = Fraction(a, b)
    demand(result.numerator == a and result.denominator == b, "rational:canonical")
    return bounded(result)


def probability(value, name, cap=None):
    demand(type(value) is list and len(value) == 2, name + ":dimension")
    result = [rational(item, cap) for item in value]
    demand(all(item >= 0 for item in result) and add(*result) == 1, name + ":mass")
    return result


def allowance(value, name):
    result = rational(value, 64)
    demand(0 <= result <= 1, name + ":outside-unit-interval")
    return result


def equal_rational(value, wanted, name):
    tick()
    demand(rational(value) == wanted, name + ":mismatch")


def request(value):
    keys(value, ("question", "states", "direction", "kernel", "initial", "stationary",
                 "horizon", "initial_error", "step_errors", "tolerance", "history", "scope"),
         "request")
    label(value["question"], "question")
    states = value["states"]
    demand(type(states) is list and len(states) == 2, "states:dimension")
    for state in states:
        label(state, "state")
    demand(states[0] != states[1], "states:duplicate")
    demand(value["direction"] == "row", "direction:unsupported")
    kernel = value["kernel"]
    demand(type(kernel) is list and len(kernel) == 2, "kernel:dimension")
    rows = [probability(row, "kernel:row", 64) for row in kernel]
    initial = probability(value["initial"], "initial", 64)
    stationary = probability(value["stationary"], "stationary", 64)
    intercept = rows[1][0]
    slope = subtract(rows[0][0], rows[1][0])
    q = bounded(abs(slope))
    demand(scalar_step(stationary[0], intercept, slope) == stationary[0],
           "stationary:not-fixed")
    horizon = value["horizon"]
    demand(type(horizon) is int and 0 <= horizon <= 6, "horizon:bound")
    initial_error = allowance(value["initial_error"], "initial-error")
    errors = value["step_errors"]
    demand(type(errors) is list and len(errors) == horizon, "step-errors:length")
    step_errors = [allowance(item, "step-error") for item in errors]
    tolerance = allowance(value["tolerance"], "tolerance")
    history = value["history"]
    demand(type(history) is list and 1 <= len(history) <= 4, "history:length")
    for item in history:
        label(item, "history")
    demand(value["scope"] == "two-state-time-homogeneous-probability-dynamics", "scope:unsupported")
    return {"intercept": intercept, "slope": slope, "q": q, "initial": initial[0],
            "stationary": stationary[0], "initial_error": initial_error,
            "step_errors": step_errors, "tolerance": tolerance, "horizon": horizon}


def verify(expected, candidate, prepared, verified_prefix):
    keys(candidate, ("profile", "request", "q", "trace", "claim"), "candidate")
    demand(candidate["profile"] == PROFILE, "profile:unsupported")
    tick()
    demand(canonical(candidate["request"]) == canonical(expected), "request:binding")
    equal_rational(candidate["q"], prepared["q"], "q")
    trace = candidate["trace"]
    horizon, q = prepared["horizon"], prepared["q"]
    demand(type(trace) is list and 1 <= len(trace) <= horizon + 1, "trace:length")
    exact = prepared["initial"]
    previous_approx = None
    bound = prepared["initial_error"]
    factor = ONE
    initial_distance = distance(prepared["initial"], prepared["stationary"])
    for index, row in enumerate(trace):
        keys(row, ("index", "exact", "approx", "error_to_exact", "step_residual",
                   "propagated_bound", "distance_to_stationary", "stationary_bound"), "trace-entry")
        demand(type(row["index"]) is int and row["index"] == index, "trace-entry:index")
        supplied_exact = probability(row["exact"], "trace-exact")
        approximate = probability(row["approx"], "trace-approx")
        if index > 0:
            exact = scalar_step(exact, prepared["intercept"], prepared["slope"])
            bound = add(multiply(q, bound), prepared["step_errors"][index - 1])
            factor = multiply(factor, q)
        wanted_exact = [exact, subtract(ONE, exact)]
        demand(supplied_exact == wanted_exact, "trace-exact:recurrence")
        error = distance(approximate[0], exact)
        equal_rational(row["error_to_exact"], error, "error-to-exact")
        if index == 0:
            demand(row["step_residual"] is None, "step-residual:initial-must-be-null")
            demand(error <= prepared["initial_error"], "initial-error:budget-exceeded")
        else:
            image = scalar_step(previous_approx, prepared["intercept"], prepared["slope"])
            residual = distance(approximate[0], image)
            equal_rational(row["step_residual"], residual, "step-residual")
            demand(residual <= prepared["step_errors"][index - 1], "step-error:budget-exceeded")
        equal_rational(row["propagated_bound"], bound, "propagated-bound")
        demand(error <= bound, "propagated-bound:violated")
        actual_distance = distance(approximate[0], prepared["stationary"])
        stationary_bound = add(multiply(factor, initial_distance), bound)
        equal_rational(row["distance_to_stationary"], actual_distance, "distance-to-stationary")
        equal_rational(row["stationary_bound"], stationary_bound, "stationary-bound")
        demand(actual_distance <= stationary_bound, "stationary-bound:violated")
        tick(4)
        verified_prefix.append(row)
        previous_approx = approximate[0]

    regime = "StrictContraction" if q < 1 else "Nonexpansive"
    complete = len(trace) == horizon + 1
    kind = ("UnknownCoverage" if not complete else
            "CertifiedTolerance" if stationary_bound <= prepared["tolerance"] else "VerifiedHorizon")
    claim = candidate["claim"]
    keys(claim, ("kind", "regime", "steps", "final_bound"), "claim")
    demand(claim["kind"] == kind, "claim:kind-mismatch")
    demand(claim["regime"] == regime, "claim:regime-mismatch")
    demand(type(claim["steps"]) is int and claim["steps"] == len(trace) - 1, "claim:steps-mismatch")
    equal_rational(claim["final_bound"], stationary_bound, "claim:final-bound")
    if not complete:
        return ("UnknownCoverage", "declared-future-indices-unverified", None,
                {"missing_indices": list(range(len(trace), horizon + 1))})
    result = {"kind": kind, "regime": regime, "steps": horizon, "final_bound": pair(stationary_bound),
              "actual_final_distance": pair(actual_distance)}
    return kind, "complete-declared-horizon-and-error-bounds-checked", result, None


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            demand(key not in result, "json:duplicate-key")
            result[key] = value
        return result

    def constant(_value):
        raise ValueError("json:nonfinite")

    def floating(_value):
        raise ValueError("json:noninteger-number")

    with Path(path).open("rb") as stream:
        raw = stream.read(32769)
    if len(raw) > 32768:
        raise Refusal("UnknownBudget", "wire-byte-limit")
    return json.loads(raw, object_pairs_hook=unique, parse_constant=constant, parse_float=floating)


def deadline(_signum, _frame):
    raise Refusal("UnknownBudget", "receiver-wall-limit")


def constrain_process():
    for kind, cap in ((resource.RLIMIT_AS, 134217728), (resource.RLIMIT_CPU, 3)):
        soft, hard = resource.getrlimit(kind)
        new_hard = cap if hard == resource.RLIM_INFINITY else min(cap, hard)
        new_soft = new_hard if soft == resource.RLIM_INFINITY else min(new_hard, soft)
        resource.setrlimit(kind, (new_soft, new_hard))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected", required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    expected, accepted_result, obstruction = None, None, None
    verified_prefix = []
    outcome, reason = "ImplementationFailure", "unstarted"
    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 3)
    try:
        constrain_process()
        try:
            expected = read(args.expected)
            prepared = request(expected)
        except (ValueError, TypeError, KeyError, RecursionError) as error:
            raise Refusal("InvalidContext", str(error)) from error
        try:
            candidate = read(args.candidate)
            outcome, reason, accepted_result, obstruction = verify(
                expected, candidate, prepared, verified_prefix)
        except (ValueError, TypeError, KeyError, RecursionError) as error:
            raise Refusal("InvalidEvidence", str(error)) from error
    except Refusal as error:
        outcome, reason = error.outcome, error.reason
    except Exception as error:
        outcome, reason = "ImplementationFailure", type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    if outcome not in SUCCESS:
        accepted_result = None
    if outcome != "UnknownCoverage":
        obstruction = None
    print(json.dumps({"profile": PROFILE, "outcome": outcome, "reason": reason,
                      "expected_request": expected, "verified_prefix": verified_prefix,
                      "accepted_result": accepted_result, "obstruction": obstruction,
                      "native_authority": False, "close_authorized": False, "free_authorized": False,
                      "work_units": WORK, "wall_seconds": time.perf_counter() - started},
                     sort_keys=True, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
