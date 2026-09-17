#!/usr/bin/env python3
"""Original two-step decision-scale receiver under Unknown v0.3.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
account use is not his review or a correctness guarantee. This finite checker
binds ordered declared transports, without native composition or unit authority.
"""
import argparse
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import signal
import time

PROFILE = "adva.research.decision-scale-composition.v0"
REQUEST = {"source", "steps"}
STEP = {"factor", "target_unit", "step"}
RECEIPT = {"profile", "request", "links", "summary"}
SUMMARY = {"product_factor", "final_context", "single_step_factor_status"}
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


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def same(left, right, name):
    tick()
    demand(canonical(left) == canonical(right), name + ":mismatch")


def rational(value, cap=256):
    tick()
    demand(type(value) is list and len(value) == 2, "rational:shape")
    a, b = value
    demand(type(a) is int and type(b) is int, "rational:integer-type")
    demand(0 < a <= cap and 0 < b <= cap, "rational:positive-bound")
    result = Fraction(a, b)
    demand(result.numerator == a and result.denominator == b, "rational:canonical")
    return result


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
        raw = stream.read(65537)
    if len(raw) > 65536:
        raise Refusal("UnknownBudget", "wire-byte-limit")
    return json.loads(raw, object_pairs_hook=unique, parse_constant=constant)


def load_parent():
    """Load one unchanged scale checker and its unchanged ancestor checkers."""
    global PARENT
    path = Path(__file__).resolve().parents[1] / "decision_scale" / "receive.py"
    spec = importlib.util.spec_from_file_location("decision_scale_composition_parent", path)
    demand(spec is not None and spec.loader is not None, "parent:loader")
    PARENT = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(PARENT)
    PARENT.load_parent()


def parent_call(function, *args):
    """All links, preflights and nested checks spend one cumulative budget."""
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
    steps = value["steps"]
    demand(type(steps) is list and len(steps) == 2, "steps:length")
    requests, arrays = [], []
    current = value["source"]
    for index, step in enumerate(steps):
        keys(step, STEP, "step")
        tick()
        derived = {"source": current, "factor": step["factor"],
                   "target_unit": step["target_unit"], "step": step["step"]}
        # This also checks the full intermediate context and both history bounds.
        checked = parent_call(PARENT.request, derived)
        requests.append(derived)
        arrays.append(checked)
        current = checked[2]
    product = arrays[0][0] * arrays[1][0]
    tick()
    demand(0 < product.numerator <= 256 and product.denominator <= 256,
           "product:bound")
    return requests, arrays, current, product


def verify(expected, receipt, prepared, checked):
    keys(receipt, RECEIPT, "receipt")
    demand(receipt["profile"] == PROFILE, "profile:unsupported")
    same(receipt["request"], expected, "request:binding")
    links = receipt["links"]
    demand(type(links) is list and len(links) == 2, "links:length")
    derived, _arrays, final_context, product = prepared
    for index, link in enumerate(links):
        tick()
        if len(canonical(link).encode("utf-8")) > 32768:
            raise Refusal("UnknownBudget", "embedded-scale-wire-byte-limit")
        keys(link, PARENT.RECEIPT, "link")
        local_arrays = parent_call(PARENT.request, link["request"])
        parent_call(PARENT.verify, link["request"], link, local_arrays, [])
        # Diagnostic only: neither local success grants a composed transport.
        checked.append(index)

    for index in range(2):
        same(links[index]["request"], derived[index], "link:ordered-request")
    same(links[0]["target_receipt"]["context"],
         links[1]["source_receipt"]["context"], "middle:context")
    same(links[0]["target_receipt"], links[1]["source_receipt"], "middle:receipt")

    summary = receipt["summary"]
    keys(summary, SUMMARY, "summary")
    demand(rational(summary["product_factor"]) == product, "product:mismatch")
    status = ("WithinFactorBound" if product.numerator <= 16 and
              product.denominator <= 16 else "OutsideFactorBound")
    same(summary["single_step_factor_status"], status, "single-step-factor-status")
    same(summary["final_context"], final_context, "summary:final-context")
    same(links[1]["target_receipt"]["context"], final_context, "final:context")
    # Check the numerical product separately; history is never compressed.
    for state in range(2):
        for action in range(2):
            parent_call(PARENT.scaled, expected["source"]["loss"][state][action],
                        final_context["loss"][state][action], product, "final:loss")
    parent_call(PARENT.scaled, expected["source"]["observation_cost"],
                final_context["observation_cost"], product, "final:cost")


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
            prepared = request(expected)
        except ValueError as error:
            raise Refusal("InvalidContext", str(error)) from error
        try:
            receipt = read(args.candidate)
            verify(expected, receipt, prepared, checked)
        except ValueError as error:
            raise Refusal("InvalidEvidence", str(error)) from error
        outcome, reason = "AcceptedScaleComposition", "all-declared-composition-checks-passed"
        delta = ["two ordered finite scale transports and their ancestors checked",
                 "complete intermediate context and receipt bound",
                 "numerical product and final context checked with both history records",
                 "single-step factor bound reported without granting direct execution"]
    except Refusal as error:
        outcome, reason = error.outcome, error.reason
    except Exception as error:
        outcome, reason = "ImplementationFailure", type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    print(json.dumps({"profile": PROFILE, "outcome": outcome, "reason": reason,
                      "expected_request": expected, "locally_checked_steps": checked,
                      "semantic_delta": delta, "native_authority": False,
                      "close_authorized": False, "free_authorized": False,
                      "work_units": WORK,
                      "wall_seconds": time.perf_counter() - started},
                     ensure_ascii=False, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
