#!/usr/bin/env python3
"""Original bounded observable-unit receiver, Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy; account use
is not his review or correctness guarantee. The finite unit registry is a
declared formal convention, not physical calibration or native authority.
"""
import argparse
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import resource
import signal
import time

PROFILE = "adva.research.observable-unit-transport.v0"
REGISTRY = {"m": ("Length", Fraction(1)), "cm": ("Length", Fraction(1, 100)),
            "s": ("Time", Fraction(1)), "ms": ("Time", Fraction(1, 1000))}
WORK = 0
PARENT = None


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


def deadline(_signum, _frame):
    raise Refusal("UnknownBudget", "receiver-wall-limit")


def keys(value, names, name):
    demand(type(value) is dict and set(value) == set(names), name + ":fields")


def label(value, name):
    demand(type(value) is str and 1 <= len(value) <= 80, name + ":label")


def rational(value, cap=1000000000):
    tick()
    demand(type(value) is list and len(value) == 2, "rational:shape")
    a, b = value
    demand(type(a) is int and type(b) is int, "rational:integer-type")
    demand(abs(a) <= cap and 0 < b <= cap, "rational:bound")
    result = Fraction(a, b)
    demand(result.numerator == a and result.denominator == b, "rational:canonical")
    return result


def pair(value):
    return [value.numerator, value.denominator]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def same(left, right, name):
    tick()
    demand(canonical(left) == canonical(right), name + ":mismatch")


def scaled(before, after, factor, name):
    tick()
    demand(rational(after) == factor * rational(before), name + ":scale-mismatch")


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
    return json.loads(raw, object_pairs_hook=unique, parse_constant=constant,
                      parse_float=floating)


def load_parent():
    global PARENT
    path = Path(__file__).resolve().parents[1] / "probability_receipt" / "receive.py"
    spec = importlib.util.spec_from_file_location("observable_unit_probability_parent", path)
    demand(spec is not None and spec.loader is not None, "parent:loader")
    PARENT = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(PARENT)


def parent_call(function, *args):
    global WORK
    PARENT.WORK = WORK
    try:
        return function(*args)
    except PARENT.Refusal as error:
        raise Refusal(error.outcome, "parent:" + error.reason) from error
    finally:
        WORK = PARENT.WORK


def quantity(value, name):
    keys(value, ("dimension", "unit", "origin"), name)
    label(value["dimension"], name + ":dimension")
    label(value["unit"], name + ":unit")
    demand(value["unit"] in REGISTRY, name + ":unregistered-unit")
    dimension, scale = REGISTRY[value["unit"]]
    demand(value["dimension"] == dimension, name + ":registry-dimension")
    demand(rational(value["origin"], 1024) == 0, name + ":zero-origin-required")
    return dimension, scale


def request(value):
    keys(value, ("source", "source_quantity", "target_quantity", "step"), "request")
    source_dimension, source_scale = quantity(value["source_quantity"], "source-quantity")
    target_dimension, target_scale = quantity(value["target_quantity"], "target-quantity")
    demand(source_dimension == target_dimension, "quantity:dimension-mismatch")
    label(value["step"], "step")
    arrays = parent_call(PARENT.context, value["source"])
    demand(value["source"]["observable"]["unit"] == value["source_quantity"]["unit"],
           "source:quantity-unit-binding")
    factor = source_scale / target_scale
    target = json.loads(canonical(value["source"]))
    target["observable"]["values"] = [pair(factor * item) for item in arrays[3]]
    target["observable"]["unit"] = value["target_quantity"]["unit"]
    target["history"] = target["history"] + [value["step"]]
    tick(len(arrays[3]) + 3)
    parent_call(PARENT.context, target)
    return factor, arrays, target


def annotation(value, unit, power, name):
    keys(value, ("unit", "power"), name)
    demand(type(value["unit"]) is str and value["unit"] == unit, name + ":unit")
    demand(type(value["power"]) is int and value["power"] == power, name + ":power")
    tick(2)


def verify(expected, receipt, prepared, checked):
    keys(receipt, ("profile", "request", "source_receipt", "target_receipt", "transport"), "receipt")
    demand(receipt["profile"] == PROFILE, "profile:unsupported")
    same(receipt["request"], expected, "request:binding")
    factor, arrays, target_expected = prepared
    source, target = receipt["source_receipt"], receipt["target_receipt"]
    parent_call(PARENT.verify, expected["source"], source, arrays)
    checked.append("source")
    keys(target, ("profile", "context", "claims"), "target-receipt")
    target_arrays = parent_call(PARENT.context, target["context"])
    parent_call(PARENT.verify, target["context"], target, target_arrays)
    checked.append("target")
    same(target["context"], target_expected, "target:requested-context")

    transport = receipt["transport"]
    keys(transport, ("factor", "expectation_unit", "variance_unit"), "transport")
    demand(rational(transport["factor"]) == factor, "transport:registry-factor")
    unit = expected["target_quantity"]["unit"]
    annotation(transport["expectation_unit"], unit, 1, "expectation-unit")
    annotation(transport["variance_unit"], unit, 2, "variance-unit")

    before, after = source["claims"], target["claims"]
    for field in ("density", "density_mean", "density_energy", "density_variance",
                  "observed_energy", "hidden_residual"):
        same(before[field], after[field], field)
    for field in ("expectation", "tower_expectation"):
        scaled(before[field], after[field], factor, field)
    for field in ("variance", "within_variance", "between_variance"):
        scaled(before[field], after[field], factor * factor, field)
    demand(len(before["atoms"]) == len(after["atoms"]), "atoms:transport-length")
    for old, new in zip(before["atoms"], after["atoms"]):
        for field in ("label", "reference_mass", "probability_mass", "density", "conditional"):
            same(old[field], new[field], "atom:" + field)
        if old["conditional"] is None:
            demand(new["conditional_mean"] is None and new["conditional_variance"] is None,
                   "atom:null-transport")
            tick()
        else:
            scaled(old["conditional_mean"], new["conditional_mean"], factor, "atom:conditional-mean")
            scaled(old["conditional_variance"], new["conditional_variance"],
                   factor * factor, "atom:conditional-variance")
    return target_expected, transport


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
    expected, accepted_target, transport = None, None, None
    checked, delta = [], []
    outcome, reason = "ImplementationFailure", "unstarted"
    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 3)
    try:
        constrain_process()
        load_parent()
        try:
            expected = read(args.expected)
            prepared = request(expected)
        except (ValueError, TypeError, KeyError, RecursionError) as error:
            raise Refusal("InvalidContext", str(error)) from error
        try:
            receipt = read(args.candidate)
            target, annotations = verify(expected, receipt, prepared, checked)
        except (ValueError, TypeError, KeyError, RecursionError) as error:
            raise Refusal("InvalidEvidence", str(error)) from error
        outcome, reason = "AcceptedObservableUnitTransport", "all-declared-unit-transport-checks-passed"
        accepted_target, transport = target, annotations
        delta = ["both exact finite probability endpoint receipts checked",
                 "receiver registry and complete requested target bound",
                 "dimensionless density and conditional laws preserved",
                 "means scale by a and variances by a squared with checked unit powers",
                 "zero-probability nulls and appended history retained"]
    except Refusal as error:
        outcome, reason = error.outcome, error.reason
    except Exception as error:
        outcome, reason = "ImplementationFailure", type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    if outcome != "AcceptedObservableUnitTransport":
        accepted_target, transport, delta = None, None, []
    print(json.dumps({"profile": PROFILE, "outcome": outcome, "reason": reason,
                      "expected_request": expected, "endpoint_arithmetic_checked": checked,
                      "accepted_target": accepted_target, "transport": transport,
                      "semantic_delta": delta, "native_authority": False,
                      "close_authorized": False, "free_authorized": False,
                      "work_units": WORK, "wall_seconds": time.perf_counter() - started},
                     sort_keys=True, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
