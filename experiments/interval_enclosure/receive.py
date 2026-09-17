#!/usr/bin/env python3
"""Original bounded rational interval receiver, Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy; account use
is not his review or correctness guarantee. Enclosure is a finite research
contract, without native authority or a claim of exact dependency recovery.
"""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import resource
import signal
import time

PROFILE = "adva.research.interval-enclosure.v0"
WORK = 0
ZERO = Fraction(0)
ONE = Fraction(1)


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


def bounded_integer(value):
    if abs(value).bit_length() > 512:
        raise Refusal("UnknownBudget", "arithmetic-intermediate-bit-limit")
    return value


def bounded(value):
    bounded_integer(value.numerator)
    bounded_integer(value.denominator)
    return value


def add(left, right):
    tick()
    a = bounded_integer(left.numerator * right.denominator)
    b = bounded_integer(right.numerator * left.denominator)
    d = bounded_integer(left.denominator * right.denominator)
    return bounded(Fraction(bounded_integer(a + b), d))


def subtract(left, right):
    return add(left, -right)


def multiply(left, right):
    tick()
    n = bounded_integer(left.numerator * right.numerator)
    d = bounded_integer(left.denominator * right.denominator)
    return bounded(Fraction(n, d))


def inverse(value):
    tick()
    demand(value != 0, "reciprocal:zero")
    return bounded(Fraction(value.denominator, value.numerator))


def interval_product(left, right):
    """Sign cases independently derived from monotonicity on each orthant."""
    a, b = left
    c, d = right
    tick(2)
    if a >= 0:
        if c >= 0:
            return multiply(a, c), multiply(b, d)
        if d <= 0:
            return multiply(b, c), multiply(a, d)
        return multiply(b, c), multiply(b, d)
    if b <= 0:
        if c >= 0:
            return multiply(a, d), multiply(b, c)
        if d <= 0:
            return multiply(b, d), multiply(a, c)
        return multiply(a, d), multiply(a, c)
    if c >= 0:
        return multiply(a, d), multiply(b, d)
    if d <= 0:
        return multiply(b, c), multiply(a, c)
    return (min(multiply(a, d), multiply(b, c)),
            max(multiply(a, c), multiply(b, d)))


def round_outward(interval, grid):
    if grid is None:
        return interval
    lo, hi = interval
    tick(2)
    low_scaled = bounded_integer(lo.numerator * grid)
    high_scaled = bounded_integer(hi.numerator * grid)
    lower, _ = divmod(low_scaled, lo.denominator)
    upper, remainder = divmod(high_scaled, hi.denominator)
    if remainder:
        upper = bounded_integer(upper + 1)
    return bounded(Fraction(lower, grid)), bounded(Fraction(upper, grid))


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
        bounded_integer(a)
        bounded_integer(b)
    result = Fraction(a, b)
    demand(result.numerator == a and result.denominator == b, "rational:canonical")
    return bounded(result)


def interval(value, cap=None):
    demand(type(value) is list and len(value) == 2, "interval:shape")
    result = rational(value[0], cap), rational(value[1], cap)
    demand(result[0] <= result[1], "interval:reversed")
    return result


def pair(value):
    return [value.numerator, value.denominator]


def wire_interval(value):
    return [pair(value[0]), pair(value[1])]


def request(value):
    keys(value, ("question", "variables", "nodes", "mode", "grid", "epsilon", "history", "scope"),
         "request")
    label(value["question"], "question")
    variables = value["variables"]
    demand(type(variables) is list and len(variables) <= 2, "variables:length")
    declarations = {}
    for variable in variables:
        keys(variable, ("name", "interval"), "variable")
        label(variable["name"], "variable:name")
        demand(variable["name"] not in declarations, "variables:duplicate")
        declarations[variable["name"]] = interval(variable["interval"], 64)
    if value["mode"] == "exact-rational":
        demand(value["grid"] is None, "grid:exact-mode")
    elif value["mode"] == "outward-grid":
        demand(type(value["grid"]) is int and value["grid"] in (1, 2, 4, 8, 16, 32, 64),
               "grid:unsupported")
    else:
        raise ValueError("mode:unsupported")
    epsilon = rational(value["epsilon"], 64)
    demand(epsilon > 0, "epsilon:positive")
    history = value["history"]
    demand(type(history) is list and 1 <= len(history) <= 4, "history:length")
    for item in history:
        label(item, "history")
    demand(value["scope"] == "all-rational-valuations-in-box", "scope:unsupported")
    nodes = value["nodes"]
    demand(type(nodes) is list and 1 <= len(nodes) <= 7, "nodes:length")
    depths, used = [], set()
    for index, node in enumerate(nodes):
        demand(type(node) is dict and "op" in node, "node:shape")
        op = node["op"]
        if op == "var":
            keys(node, ("op", "name"), "var")
            label(node["name"], "var:name")
            demand(node["name"] in declarations, "var:undeclared")
            used.add(node["name"])
            depths.append(1)
        elif op == "const":
            keys(node, ("op", "value"), "const")
            rational(node["value"], 64)
            depths.append(1)
        elif op in ("add", "sub", "mul", "div"):
            keys(node, ("op", "left", "right"), "binary")
            for field in ("left", "right"):
                demand(type(node[field]) is int and 0 <= node[field] < index, "reference:not-earlier")
            depths.append(1 + max(depths[node["left"]], depths[node["right"]]))
        else:
            raise ValueError("node:unsupported-op")
        tick()
        demand(depths[-1] <= 4, "nodes:depth-limit")
    demand(used == set(declarations), "variables:unused")
    reachable, stack = set(), [len(nodes) - 1]
    while stack:
        index = stack.pop()
        if index in reachable:
            continue
        reachable.add(index)
        node = nodes[index]
        tick()
        if node["op"] in ("add", "sub", "mul", "div"):
            stack.extend((node["left"], node["right"]))
    demand(len(reachable) == len(nodes), "nodes:unreachable")
    return declarations, epsilon


def result_for(enclosure, epsilon):
    lo, hi = enclosure
    tick(4)
    if lo == hi == 0:
        zero = "ExactZero"
    elif lo > 0:
        zero = "StrictPositive"
    elif hi < 0:
        zero = "StrictNegative"
    else:
        zero = "ZeroUndetermined"
    if lo == hi == 1:
        one = "ExactOne"
    elif hi < 1 or lo > 1:
        one = "ExcludesOne"
    else:
        one = "OneUndetermined"
    return {"kind": "enclosure", "interval": wire_interval(enclosure),
            "zero_class": zero, "one_class": one, "within_epsilon": -epsilon <= lo and hi <= epsilon}


def verify(expected, candidate, prepared, diagnostics):
    keys(candidate, ("profile", "request", "trace", "result"), "candidate")
    demand(candidate["profile"] == PROFILE, "profile:unsupported")
    tick()
    demand(canonical(candidate["request"]) == canonical(expected), "request:binding")
    trace = candidate["trace"]
    demand(type(trace) is list and len(trace) <= len(expected["nodes"]), "trace:length")
    declarations, epsilon = prepared
    propagated = []
    for index, node in enumerate(expected["nodes"]):
        op = node["op"]
        if op == "var":
            tight = declarations[node["name"]]
        elif op == "const":
            point = rational(node["value"], 64)
            tight = point, point
        else:
            left, right = propagated[node["left"]], propagated[node["right"]]
            if op == "add":
                tight = add(left[0], right[0]), add(left[1], right[1])
            elif op == "sub":
                tight = subtract(left[0], right[1]), subtract(left[1], right[0])
            elif op == "mul":
                tight = interval_product(left, right)
            else:
                if right[0] <= 0 <= right[1]:
                    diagnostics["obstruction"] = {"node": index, "denominator": wire_interval(right),
                                                  "reason": "zero-not-excluded"}
                    demand(len(trace) == index, "trace:blocked-prefix-length")
                    wanted = {"kind": "unknown-domain", "node": index, "denominator": wire_interval(right)}
                    result = candidate["result"]
                    keys(result, ("kind", "node", "denominator"), "result")
                    demand(type(result["node"]) is int, "result:node-type")
                    interval(result["denominator"])
                    demand(canonical(result) == canonical(wanted), "result:domain-obstruction")
                    return "UnknownDomain", "propagated-denominator-does-not-exclude-zero", None
                reciprocal = inverse(right[1]), inverse(right[0])
                tight = interval_product(left, reciprocal)
        enclosed = round_outward(tight, expected["grid"])
        demand(index < len(trace), "trace:missing-entry")
        entry = trace[index]
        keys(entry, ("index", "tight", "enclosure"), "trace-entry")
        demand(type(entry["index"]) is int and entry["index"] == index, "trace-entry:index")
        supplied_tight, supplied_enclosure = interval(entry["tight"]), interval(entry["enclosure"])
        demand(supplied_tight == tight, "trace-entry:tight-mismatch")
        demand(supplied_enclosure == enclosed, "trace-entry:enclosure-mismatch")
        diagnostics["verified_prefix"].append(entry)
        propagated.append(enclosed)
        tick(2)
    demand(len(trace) == len(expected["nodes"]), "trace:complete-length")
    wanted = result_for(propagated[-1], epsilon)
    result = candidate["result"]
    keys(result, ("kind", "interval", "zero_class", "one_class", "within_epsilon"), "result")
    interval(result["interval"])
    demand(type(result["within_epsilon"]) is bool, "result:epsilon-boolean")
    demand(canonical(result) == canonical(wanted), "result:enclosure-classification")
    return "VerifiedEnclosure", "all-declared-node-enclosures-and-classifications-checked", result


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
    diagnostics = {"verified_prefix": [], "obstruction": None}
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
            outcome, reason, accepted_result = verify(expected, candidate, prepared, diagnostics)
        except (ValueError, TypeError, KeyError, RecursionError) as error:
            raise Refusal("InvalidEvidence", str(error)) from error
        if outcome == "VerifiedEnclosure":
            delta = ["complete finite expression and ordered dependency graph bound",
                     "exact rational propagation and declared outward rounding checked",
                     "zero, one, and epsilon classifications checked without implicit equality",
                     "verified node history retained without native authority"]
    except Refusal as error:
        outcome, reason = error.outcome, error.reason
    except Exception as error:
        outcome, reason = "ImplementationFailure", type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    if outcome != "VerifiedEnclosure":
        accepted_result, delta = None, []
    print(json.dumps({"profile": PROFILE, "outcome": outcome, "reason": reason,
                      "expected_request": expected, "verified_prefix": diagnostics["verified_prefix"],
                      "accepted_result": accepted_result, "obstruction": diagnostics["obstruction"],
                      "semantic_delta": delta, "native_authority": False,
                      "close_authorized": False, "free_authorized": False,
                      "work_units": WORK, "wall_seconds": time.perf_counter() - started},
                     sort_keys=True, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
