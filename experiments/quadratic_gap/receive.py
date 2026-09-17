#!/usr/bin/env python3
"""Original finite quadratic-gap receiver, contributed under Unknown v0.3.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy.
Account use is not his review, endorsement, or correctness guarantee. The
receiver checks rational witnesses without importing a producer or native API.
"""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import resource
import signal
import time

PROFILE = "adva.research.quadratic-gap.v0"
WORK = 0
ZERO = Fraction(0)
HALF = Fraction(1, 2)
SUCCESS = {"ExactOptimal", "EpsilonOptimal", "VerifiedGap"}


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
    p = integer_bound(left.numerator * right.denominator)
    q = integer_bound(right.numerator * left.denominator)
    denominator = integer_bound(left.denominator * right.denominator)
    return bounded(Fraction(integer_bound(p + q), denominator))


def subtract(left, right):
    return add(left, -right)


def multiply(left, right):
    tick()
    numerator = integer_bound(left.numerator * right.numerator)
    denominator = integer_bound(left.denominator * right.denominator)
    return bounded(Fraction(numerator, denominator))


def dot(left, right):
    demand(len(left) == len(right) and 1 <= len(left) <= 2, "dot:dimension")
    result = ZERO
    for a, b in zip(left, right):
        result = add(result, multiply(a, b))
    return result


def matvec(matrix, vector):
    return [dot(row, vector) for row in matrix]


def objective(matrix, linear, constant, point):
    return add(add(multiply(HALF, dot(point, matvec(matrix, point))),
                   dot(linear, point)), constant)


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


def vector(value, size, name, cap=None):
    demand(type(value) is list and len(value) == size, name + ":dimension")
    return [rational(item, cap) for item in value]


def pair(value):
    return [value.numerator, value.denominator]


def wire_vector(value):
    return [pair(item) for item in value]


def request(value):
    keys(value, ("question", "axes", "H", "c", "d", "box", "tolerance", "history", "scope"),
         "request")
    label(value["question"], "question")
    axes = value["axes"]
    demand(type(axes) is list and 1 <= len(axes) <= 2, "axes:dimension")
    for axis in axes:
        label(axis, "axis")
    demand(len(set(axes)) == len(axes), "axes:duplicate")
    size = len(axes)
    demand(type(value["H"]) is list and len(value["H"]) == size, "H:dimension")
    matrix = [vector(row, size, "H:row", 64) for row in value["H"]]
    linear = vector(value["c"], size, "c", 64)
    constant = rational(value["d"], 64)
    for i in range(size):
        for j in range(size):
            tick()
            demand(matrix[i][j] == matrix[j][i], "H:nonsymmetric")
    for i in range(size):
        tick()
        demand(matrix[i][i] >= 0, "H:negative-principal-minor")
    if size == 2:
        determinant = subtract(multiply(matrix[0][0], matrix[1][1]),
                               multiply(matrix[0][1], matrix[1][0]))
        demand(determinant >= 0, "H:negative-determinant")
    box = value["box"]
    demand(type(box) is list and len(box) == size, "box:dimension")
    bounds = [vector(item, 2, "box:interval", 64) for item in box]
    demand(all(lo <= hi for lo, hi in bounds), "box:reversed")
    tolerance = rational(value["tolerance"], 64)
    demand(tolerance >= 0, "tolerance:negative")
    history = value["history"]
    demand(type(history) is list and 1 <= len(history) <= 4, "history:length")
    for item in history:
        label(item, "history")
    demand(value["scope"] == "all-rational-points-in-box", "scope:unsupported")
    return matrix, linear, constant, bounds, tolerance


def verify(expected, candidate, prepared, retained):
    keys(candidate, ("profile", "request", "point", "upper", "lower", "claim"), "candidate")
    demand(candidate["profile"] == PROFILE, "profile:unsupported")
    tick()
    demand(canonical(candidate["request"]) == canonical(expected), "request:binding")
    matrix, linear, constant, box, tolerance = prepared
    size = len(linear)
    point = vector(candidate["point"], size, "point", 64)
    tick(size)
    demand(all(lo <= x <= hi for x, (lo, hi) in zip(point, box)), "point:outside-box")
    supplied_upper = rational(candidate["upper"])
    upper = objective(matrix, linear, constant, point)
    demand(supplied_upper == upper, "upper:objective-mismatch")
    retained["verified_feasible"] = {"point": wire_vector(point), "upper": pair(upper)}

    lower = candidate["lower"]
    if lower is None:
        claim = candidate["claim"]
        keys(claim, ("kind", "gap"), "claim")
        demand(claim["kind"] == "UnknownLowerBound" and claim["gap"] is None,
               "claim:missing-lower-classification")
        return "UnknownLowerBound", "feasible-point-checked-no-lower-certificate", None

    keys(lower, ("anchor", "gradient", "corner", "value"), "lower")
    anchor = vector(lower["anchor"], size, "anchor", 64)
    supplied_gradient = vector(lower["gradient"], size, "gradient")
    gradient = [add(item, coefficient) for item, coefficient in zip(matvec(matrix, anchor), linear)]
    demand(supplied_gradient == gradient, "lower:gradient-mismatch")
    supplied_corner = vector(lower["corner"], size, "corner")
    corner = [box[i][0] if gradient[i] >= 0 else box[i][1] for i in range(size)]
    tick(size)
    demand(supplied_corner == corner, "lower:corner-mismatch")
    offset = [subtract(corner[i], anchor[i]) for i in range(size)]
    lower_value = add(objective(matrix, linear, constant, anchor), dot(gradient, offset))
    demand(rational(lower["value"]) == lower_value, "lower:value-mismatch")
    retained["verified_lower"] = {"anchor": wire_vector(anchor), "gradient": wire_vector(gradient),
                                  "corner": wire_vector(corner), "value": pair(lower_value)}
    gap = subtract(upper, lower_value)
    demand(gap >= 0, "gap:negative")
    if gap == 0:
        kind = "ExactOptimal"
    elif gap <= tolerance:
        kind = "EpsilonOptimal"
    else:
        kind = "VerifiedGap"
    claim = candidate["claim"]
    keys(claim, ("kind", "gap"), "claim")
    demand(rational(claim["gap"]) == gap, "claim:gap-mismatch")
    demand(claim["kind"] == kind, "claim:kind-mismatch")
    accepted = {"kind": kind, "lower": pair(lower_value), "upper": pair(upper), "gap": pair(gap)}
    return kind, "feasible-upper-and-psd-affine-lower-gap-checked", accepted


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
    expected, accepted_result = None, None
    retained = {"verified_feasible": None, "verified_lower": None}
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
            outcome, reason, accepted_result = verify(expected, candidate, prepared, retained)
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
    print(json.dumps({"profile": PROFILE, "outcome": outcome, "reason": reason,
                      "expected_request": expected, **retained, "accepted_result": accepted_result,
                      "native_authority": False, "close_authorized": False, "free_authorized": False,
                      "work_units": WORK, "wall_seconds": time.perf_counter() - started},
                     sort_keys=True, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
