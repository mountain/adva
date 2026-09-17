#!/usr/bin/env python3
"""Original bounded rational linear-system receiver, Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy. Account use
is not his review, endorsement, or correctness guarantee. This separate
research profile does not widen an invertible-operator or native contract.
"""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import resource
import signal
import time

PROFILE = "adva.research.linear-system.v0"
WORK = 0
ZERO = Fraction(0)
ONE = Fraction(1)
SUCCESS = {"UniqueSolution", "InconsistentSystem", "AffineSolutionFamily"}


class Refusal(Exception):
    def __init__(self, outcome, reason):
        self.outcome, self.reason = outcome, reason


def deadline(_signum, _frame):
    raise Refusal("UnknownBudget", "receiver-wall-limit")


def demand(ok, reason):
    if not ok:
        raise ValueError(reason)


def tick(count=1):
    global WORK
    if WORK + count > 10000:
        raise Refusal("UnknownBudget", "receiver-work-limit")
    WORK += count


def bounded(value):
    if abs(value.numerator).bit_length() > 512 or value.denominator.bit_length() > 512:
        raise Refusal("UnknownBudget", "arithmetic-intermediate-bit-limit")
    return value


def add(left, right):
    tick()
    return bounded(left + right)


def subtract(left, right):
    tick()
    return bounded(left - right)


def multiply(left, right):
    tick()
    return bounded(left * right)


def dot(left, right):
    demand(len(left) == 2 and len(right) == 2, "dot:dimension")
    return add(multiply(left[0], right[0]), multiply(left[1], right[1]))


def matvec(matrix, vector):
    return [dot(row, vector) for row in matrix]


def matmul(left, right):
    return [[dot(left[i], [right[0][j], right[1][j]]) for j in range(2)]
            for i in range(2)]


def determinant(matrix):
    return subtract(multiply(matrix[0][0], matrix[1][1]),
                    multiply(matrix[0][1], matrix[1][0]))


def residual(matrix, vector, rhs):
    return [subtract(a, b) for a, b in zip(matvec(matrix, vector), rhs)]


def rank(matrix):
    if determinant(matrix) != 0:
        return 2
    tick(4)
    return 1 if any(item != 0 for row in matrix for item in row) else 0


def pair(value):
    return [value.numerator, value.denominator]


def wire_vector(value):
    return [pair(item) for item in value]


def keys(value, names, name):
    demand(type(value) is dict and set(value) == set(names), name + ":fields")


def label(value, name):
    demand(type(value) is str and 1 <= len(value) <= 80, name + ":label")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def rational(value, cap):
    tick()
    demand(type(value) is list and len(value) == 2, "rational:shape")
    a, b = value
    demand(type(a) is int and type(b) is int, "rational:integer-type")
    demand(abs(a) <= cap and 0 < b <= cap, "rational:bound")
    result = Fraction(a, b)
    demand(result.numerator == a and result.denominator == b, "rational:canonical")
    return bounded(result)


def vector(value, cap, name):
    demand(type(value) is list and len(value) == 2, name + ":dimension")
    return [rational(item, cap) for item in value]


def matrix(value, cap, name):
    demand(type(value) is list and len(value) == 2, name + ":rows")
    return [vector(row, cap, name + ":row") for row in value]


def space(value, name):
    keys(value, ("id", "dimension", "basis"), name)
    label(value["id"], name + ":id")
    demand(type(value["dimension"]) is int and value["dimension"] == 2, name + ":dimension")
    # The outer list holds columns. Transposition leaves a 2x2 determinant unchanged.
    basis = matrix(value["basis"], 64, name + ":basis")
    demand(determinant(basis) != 0, name + ":dependent-basis")


def request(value):
    keys(value, ("question", "domain", "codomain", "operator", "rhs", "interpretation", "history"),
         "request")
    label(value["question"], "question")
    space(value["domain"], "domain")
    space(value["codomain"], "codomain")
    demand(value["domain"]["id"] != value["codomain"]["id"], "spaces:distinct-ids")
    operator = value["operator"]
    keys(operator, ("domain", "codomain", "action", "matrix"), "operator")
    demand(type(operator["domain"]) is str and operator["domain"] == value["domain"]["id"],
           "operator:domain-binding")
    demand(type(operator["codomain"]) is str and operator["codomain"] == value["codomain"]["id"],
           "operator:codomain-binding")
    demand(operator["action"] == "left-on-column", "operator:action")
    a = matrix(operator["matrix"], 64, "operator:matrix")
    rhs = value["rhs"]
    keys(rhs, ("space", "coordinates"), "rhs")
    demand(type(rhs["space"]) is str and rhs["space"] == value["codomain"]["id"], "rhs:space-binding")
    b = vector(rhs["coordinates"], 64, "rhs:coordinates")
    demand(value["interpretation"] == "all-solutions-over-Q", "interpretation:unsupported")
    history = value["history"]
    demand(type(history) is list and 1 <= len(history) <= 4, "history:length")
    for item in history:
        label(item, "history")
    return a, b


def verify(expected, candidate, prepared, diagnostics):
    keys(candidate, ("profile", "request", "claim"), "candidate")
    demand(candidate["profile"] == PROFILE, "profile:unsupported")
    tick()
    demand(canonical(candidate["request"]) == canonical(expected), "request:binding")
    claim = candidate["claim"]
    demand(type(claim) is dict and "kind" in claim, "claim:shape")
    kind = claim["kind"]
    demand(type(kind) is str, "claim:kind-type")
    a, b = prepared
    if kind == "unique":
        keys(claim, ("kind", "solution", "inverse"), "unique")
        x = vector(claim["solution"], 4096, "solution")
        inverse = matrix(claim["inverse"], 4096, "inverse")
        difference = residual(a, x, b)
        diagnostics["particular_residual"] = wire_vector(difference)
        demand(difference == [ZERO, ZERO], "solution:nonzero-residual")
        diagnostics["verified_particular"] = wire_vector(x)
        identity = [[ONE, ZERO], [ZERO, ONE]]
        demand(matmul(inverse, a) == identity, "inverse:left-product")
        demand(matmul(a, inverse) == identity, "inverse:right-product")
        return "UniqueSolution", "solution-and-two-sided-inverse-checked"
    if kind == "inconsistent":
        keys(claim, ("kind", "left_witness"), "inconsistent")
        y = vector(claim["left_witness"], 4096, "left-witness")
        annihilator = [dot(y, [a[0][j], a[1][j]]) for j in range(2)]
        contradiction = dot(y, b)
        diagnostics["annihilator"] = wire_vector(annihilator)
        diagnostics["contradiction"] = pair(contradiction)
        demand(annihilator == [ZERO, ZERO], "left-witness:not-annihilator")
        demand(contradiction == ONE, "left-witness:contradiction-not-one")
        return "InconsistentSystem", "left-annihilator-and-unit-contradiction-checked"
    if kind == "affine-family":
        keys(claim, ("kind", "particular", "kernel_basis"), "affine-family")
        x0 = vector(claim["particular"], 4096, "particular")
        difference = residual(a, x0, b)
        diagnostics["particular_residual"] = wire_vector(difference)
        demand(difference == [ZERO, ZERO], "particular:nonzero-residual")
        diagnostics["verified_particular"] = wire_vector(x0)
        supplied = claim["kernel_basis"]
        demand(type(supplied) is list and len(supplied) <= 2, "kernel-basis:length")
        basis = [vector(item, 4096, "kernel-vector") for item in supplied]
        for item in basis:
            image = matvec(a, item)
            diagnostics["kernel_residuals"].append(wire_vector(image))
            demand(item != [ZERO, ZERO], "kernel-vector:zero")
            demand(image == [ZERO, ZERO], "kernel-vector:nonzero-image")
        if len(basis) == 2:
            demand(determinant(basis) != 0, "kernel-basis:dependent")
        matrix_rank = rank(a)
        diagnostics["rank"] = matrix_rank
        nullity = 2 - matrix_rank
        demand(matrix_rank < 2, "affine-family:full-rank-use-unique")
        demand(len(basis) <= nullity, "kernel-basis:excess-directions")
        missing = nullity - len(basis)
        diagnostics["missing_kernel_directions"] = missing
        if missing:
            return "UnknownCoverage", "verified-particular-but-incomplete-kernel-basis"
        return "AffineSolutionFamily", "particular-and-complete-independent-kernel-basis-checked"
    raise ValueError("claim:unsupported-kind")


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
    expected, accepted_claim = None, None
    diagnostics = {"particular_residual": None, "verified_particular": None,
                   "annihilator": None, "contradiction": None,
                   "kernel_residuals": [], "rank": None, "missing_kernel_directions": None}
    delta = []
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
            outcome, reason = verify(expected, candidate, prepared, diagnostics)
        except (ValueError, TypeError, KeyError, RecursionError) as error:
            raise Refusal("InvalidEvidence", str(error)) from error
        if outcome in SUCCESS:
            accepted_claim = candidate["claim"]
            delta = ["complete typed rational coordinate problem bound",
                     "finite arithmetic witness independently checked",
                     "all-solutions claim justified by the declared witness kind",
                     "basis and ordered history preserved without native authority"]
    except Refusal as error:
        outcome, reason = error.outcome, error.reason
    except Exception as error:
        outcome, reason = "ImplementationFailure", type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    if outcome not in SUCCESS:
        accepted_claim, delta = None, []
    print(json.dumps({"profile": PROFILE, "outcome": outcome, "reason": reason,
                      "expected_request": expected, "accepted_claim": accepted_claim,
                      "diagnostics": diagnostics, "semantic_delta": delta,
                      "native_authority": False, "close_authorized": False, "free_authorized": False,
                      "work_units": WORK, "wall_seconds": time.perf_counter() - started},
                     sort_keys=True, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
