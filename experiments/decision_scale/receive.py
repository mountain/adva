#!/usr/bin/env python3
"""Original bounded decision-scale receiver under Unknown v0.3.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
account use is not his review or a correctness guarantee. Unit correspondence
is declared by the request, not inferred or physically established here.
"""
import argparse
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import signal
import time

PROFILE = "adva.research.decision-scale.v0"
REQUEST = {"source", "factor", "target_unit", "step"}
RECEIPT = {"profile", "request", "source_receipt", "target_receipt"}
DECISION_RECEIPT = {"profile", "context", "probability_receipt", "claims"}
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


def keys(value, expected, name):
    demand(type(value) is dict and set(value) == expected, name + ":fields")


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


def scaled(left, right, factor, name):
    tick()
    demand(rational(right) == factor * rational(left), name + ":scale-mismatch")


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            demand(key not in result, "json:duplicate-key")
            result[key] = value
        return result

    def constant(_value):
        raise ValueError("json:nonfinite")

    with Path(path).open("rb") as stream:
        raw = stream.read(32769)
    if len(raw) > 32768:
        raise Refusal("UnknownBudget", "wire-byte-limit")
    return json.loads(raw, object_pairs_hook=unique, parse_constant=constant)


def load_parent():
    """Load the pinned project decision checker and its probability checker."""
    global PARENT
    path = Path(__file__).resolve().parents[1] / "finite_decision" / "receive.py"
    spec = importlib.util.spec_from_file_location("decision_scale_parent", path)
    demand(spec is not None and spec.loader is not None, "parent:loader")
    PARENT = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(PARENT)
    PARENT.load_parent()


def parent_call(function, *args):
    """Both endpoint checks and their ancestors spend one cumulative budget."""
    global WORK
    PARENT.WORK = WORK
    try:
        return function(*args)
    except PARENT.Refusal as error:
        raise Refusal(error.outcome, "parent:" + error.reason) from error
    finally:
        WORK = PARENT.WORK


def request(value):
    keys(value, REQUEST, "request")
    factor = rational(value["factor"], cap=16)
    demand(factor > 0, "factor:positive-required")
    label(value["target_unit"], "target_unit")
    label(value["step"], "step")
    source_arrays = parent_call(PARENT.context, value["source"])
    # Copy the complete supplied context, preserving unrelated fields and roles.
    target = json.loads(canonical(value["source"]))
    target["loss"] = [[pair(factor * item) for item in row]
                      for row in source_arrays[2]]
    target["observation_cost"] = pair(factor * source_arrays[3])
    target["loss_unit"] = value["target_unit"]
    target["history"] = target["history"] + [value["step"]]
    tick(5)
    # Preflight the derived target, including ancestor joint-probability limits.
    parent_call(PARENT.context, target)
    return factor, source_arrays, target


def verify(expected, receipt, arrays, checked):
    keys(receipt, RECEIPT, "receipt")
    demand(receipt["profile"] == PROFILE, "profile:unsupported")
    same(receipt["request"], expected, "request:binding")
    factor, source_arrays, target_expected = arrays
    source = receipt["source_receipt"]
    parent_call(PARENT.verify, expected["source"], source, source_arrays)
    checked.append("source")

    target = receipt["target_receipt"]
    keys(target, DECISION_RECEIPT, "target-receipt")
    # Self-consistency is logged first, without granting the requested transport.
    target_arrays = parent_call(PARENT.context, target["context"])
    parent_call(PARENT.verify, target["context"], target, target_arrays)
    checked.append("target")
    same(target["context"], target_expected, "target:requested-context")

    before, after = source["claims"], target["claims"]
    for field in ("risk_without_observation", "risk_with_observation",
                  "gross_value", "net_value"):
        scaled(before[field], after[field], factor, field)
    for index in range(2):
        scaled(before["prior_risks"][index], after["prior_risks"][index],
               factor, "prior_risk")
    for field in ("prior_minimizers", "acquisition_minimizers"):
        same(before[field], after[field], field)
    for old, new in zip(before["observations"], after["observations"]):
        for field in ("label", "mass", "posterior", "minimizers"):
            same(old[field], new[field], "observation:" + field)
        if old["risks"] is None:
            demand(new["risks"] is None, "observation:null-risks")
        else:
            demand(new["risks"] is not None, "observation:missing-risks")
            for index in range(2):
                scaled(old["risks"][index], new["risks"][index], factor,
                       "observation:risk")
    # The inherited probability observable is state-index and is not a loss.
    same(source["probability_receipt"]["claims"],
         target["probability_receipt"]["claims"], "probability:unchanged-claims")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected", required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    expected = None
    checked = []
    outcome, reason, delta = "ImplementationFailure", "unstarted", []
    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 3)
    try:
        load_parent()
        try:
            expected = read(args.expected)
            arrays = request(expected)
        except ValueError as error:
            raise Refusal("InvalidContext", str(error)) from error
        try:
            receipt = read(args.candidate)
            verify(expected, receipt, arrays, checked)
        except ValueError as error:
            raise Refusal("InvalidEvidence", str(error)) from error
        outcome, reason = "AcceptedDecisionScale", "all-declared-transport-checks-passed"
        delta = ["both bounded decision and probability endpoint receipts checked",
                 "requested common positive loss and cost scale checked",
                 "all finite minimizer sets and null events preserved",
                 "complete requested target context and appended history bound"]
    except Refusal as error:
        outcome, reason = error.outcome, error.reason
    except Exception as error:
        # I/O and unexpected implementation errors are not mathematical refusals.
        outcome, reason = "ImplementationFailure", type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    print(json.dumps({"profile": PROFILE, "outcome": outcome, "reason": reason,
                      "expected_request": expected,
                      "endpoint_arithmetic_checked": checked,
                      "semantic_delta": delta, "native_authority": False,
                      "close_authorized": False, "free_authorized": False,
                      "work_units": WORK,
                      "wall_seconds": time.perf_counter() - started},
                     ensure_ascii=False, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
