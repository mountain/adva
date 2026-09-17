#!/usr/bin/env python3
"""Original bounded decision receiver under Unknown v0.3; no native authority.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
account use is not his review or a correctness guarantee. This research checker
compares declared finite losses; it does not infer anyone's preferences.
"""
import argparse
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import signal
import time

PROFILE = "adva.research.finite-decision.v0"
CONTEXT = {"question", "states", "observations", "actions", "prior", "kernel",
           "kernel_direction", "loss", "loss_unit", "observation_cost",
           "history", "scope"}
CLAIMS = {"observations", "prior_risks", "prior_minimizers",
          "risk_without_observation", "risk_with_observation", "gross_value",
          "net_value", "acquisition_minimizers"}
OBSERVATION = {"label", "mass", "posterior", "risks", "minimizers"}
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


def keys(value, expected, label):
    demand(type(value) is dict and set(value) == expected, label + ":fields")


def label(value, name):
    demand(type(value) is str and 1 <= len(value) <= 80, name + ":label")


def carrier(value, name):
    demand(type(value) is list and len(value) == 2, name + ":length")
    for item in value:
        label(item, name)
    demand(len(set(value)) == 2, name + ":duplicate")


def rational(value, cap=1000000000):
    tick()
    demand(type(value) is list and len(value) == 2, "rational:shape")
    a, b = value
    demand(type(a) is int and type(b) is int, "rational:integer-type")
    demand(abs(a) <= cap and 0 < b <= cap, "rational:bound")
    result = Fraction(a, b)
    demand(result.numerator == a and result.denominator == b,
           "rational:canonical")
    return result


def vector(value, size=2, cap=1000000000):
    demand(type(value) is list and len(value) == size, "vector:length")
    return [rational(item, cap) for item in value]


def matrix(value):
    demand(type(value) is list and len(value) == 2, "matrix:rows")
    return [vector(row, cap=64) for row in value]


def equal(value, expected, name):
    tick()
    demand(rational(value) == expected, name + ":mismatch")


def pair(value):
    return [value.numerator, value.denominator]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


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
    """Load the project checker itself, not a sender-supplied implementation."""
    global PARENT
    path = Path(__file__).resolve().parents[1] / "probability_receipt" / "receive.py"
    spec = importlib.util.spec_from_file_location("finite_probability_parent", path)
    demand(spec is not None and spec.loader is not None, "parent:loader")
    PARENT = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(PARENT)


def parent_call(function, *args):
    """The two sequential checkers spend one cumulative finite work budget."""
    global WORK
    PARENT.WORK = WORK
    try:
        return function(*args)
    except PARENT.Refusal as error:
        raise Refusal(error.outcome, "parent:" + error.reason) from error
    finally:
        WORK = PARENT.WORK


def context(value):
    keys(value, CONTEXT, "context")
    label(value["question"], "question")
    for name in ("states", "observations", "actions"):
        carrier(value[name], name)
    prior = vector(value["prior"], cap=64)
    demand(all(x >= 0 for x in prior) and sum(prior) == 1, "prior:mass")
    kernel = matrix(value["kernel"])
    demand(all(all(x >= 0 for x in row) and sum(row) == 1 for row in kernel),
           "kernel:mass")
    demand(value["kernel_direction"] == "observation-given-state", "kernel:direction")
    loss = matrix(value["loss"])
    demand(all(x >= 0 for row in loss for x in row), "loss:negative")
    label(value["loss_unit"], "loss_unit")
    cost = rational(value["observation_cost"], cap=64)
    demand(cost >= 0, "cost:negative")
    history = value["history"]
    demand(type(history) is list and 1 <= len(history) <= 4, "history:length")
    for item in history:
        label(item, "history")
    demand(value["scope"] == "complete-declared-finite-decision", "scope:unsupported")
    joint = [prior[s] * kernel[s][o] for s in range(2) for o in range(2)]
    tick(4)
    parent_expected = {
        "question": value["question"] + "/joint",
        "carrier": ["s0:o0", "s0:o1", "s1:o0", "s1:o1"],
        "reference": [[1, 4] for _ in range(4)],
        "probability": [pair(x) for x in joint],
        "observation": value["observations"] * 2,
        "observable": {"name": "state-index", "unit": "index",
                       "values": [[0, 1], [0, 1], [1, 1], [1, 1]]},
        "history": history,
        "scope": "complete-declared-finite-carrier",
    }
    # The inherited parent also bounds each canonical joint component by 1024.
    parent_arrays = parent_call(PARENT.context, parent_expected)
    return prior, kernel, loss, cost, parent_expected, parent_arrays


def minimizers(risks, actions):
    tick(len(risks))
    smallest = min(risks)
    return [action for action, risk in zip(actions, risks) if risk == smallest]


def verify(expected, receipt, arrays):
    keys(receipt, {"profile", "context", "probability_receipt", "claims"}, "receipt")
    demand(receipt["profile"] == PROFILE, "profile:unsupported")
    demand(canonical(receipt["context"]) == canonical(expected), "context:binding")
    prior, kernel, loss, cost, parent_expected, parent_arrays = arrays
    parent_call(PARENT.verify, parent_expected, receipt["probability_receipt"], parent_arrays)
    claim = receipt["claims"]
    keys(claim, CLAIMS, "claims")
    actions = expected["actions"]
    prior_risks = [sum(prior[s] * loss[s][a] for s in range(2)) for a in range(2)]
    tick(4)
    demand(vector(claim["prior_risks"]) == prior_risks, "prior_risks:mismatch")
    demand(claim["prior_minimizers"] == minimizers(prior_risks, actions),
           "prior_minimizers:mismatch")
    observations = claim["observations"]
    demand(type(observations) is list and len(observations) == 2, "observations:length")
    with_observation = Fraction(0)
    for o, atom in enumerate(observations):
        tick(2)
        keys(atom, OBSERVATION, "observation")
        demand(atom["label"] == expected["observations"][o], "observation:order")
        mass = sum(prior[s] * kernel[s][o] for s in range(2))
        equal(atom["mass"], mass, "observation:mass")
        if mass == 0:
            demand(all(atom[name] is None for name in ("posterior", "risks", "minimizers")),
                   "observation:zero-event")
            continue
        posterior = vector(atom["posterior"])
        for s in range(2):
            tick()
            demand(posterior[s] * mass == prior[s] * kernel[s][o], "posterior:law")
        demand(all(x >= 0 for x in posterior) and sum(posterior) == 1, "posterior:mass")
        risks = [sum(posterior[s] * loss[s][a] for s in range(2)) for a in range(2)]
        tick(4)
        demand(vector(atom["risks"]) == risks, "observation:risks")
        demand(atom["minimizers"] == minimizers(risks, actions), "observation:minimizers")
        with_observation += mass * min(risks)
    without_observation = min(prior_risks)
    gross = without_observation - with_observation
    net = gross - cost
    demand(gross >= 0, "information:negative-gross-value")
    for name, value in (("risk_without_observation", without_observation),
                        ("risk_with_observation", with_observation),
                        ("gross_value", gross), ("net_value", net)):
        equal(claim[name], value, name)
    acquisition = ["observe"] if net > 0 else ["skip"] if net < 0 else ["skip", "observe"]
    demand(claim["acquisition_minimizers"] == acquisition, "acquisition_minimizers:mismatch")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected", required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    expected = None
    outcome, reason, delta = "ImplementationFailure", "unstarted", []
    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 3)
    try:
        load_parent()
        try:
            expected = read(args.expected)
            arrays = context(expected)
        except (ValueError, TypeError, KeyError, RecursionError) as error:
            raise Refusal("InvalidContext", str(error)) from error
        try:
            receipt = read(args.candidate)
            verify(expected, receipt, arrays)
        except (ValueError, TypeError, KeyError, RecursionError) as error:
            raise Refusal("InvalidEvidence", str(error)) from error
        outcome, reason = "AcceptedFiniteDecision", "all-declared-finite-checks-passed"
        delta = ["context-bound finite joint probability receipt independently checked",
                 "conditional risks and complete action minimizer sets",
                 "gross and cost-adjusted value for the declared observe-or-skip choice"]
    except Refusal as error:
        outcome, reason = error.outcome, error.reason
    except Exception as error:
        outcome, reason = "ImplementationFailure", type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    print(json.dumps({"profile": PROFILE, "outcome": outcome, "reason": reason,
                      "expected_context": expected, "semantic_delta": delta,
                      "native_authority": False, "close_authorized": False,
                      "free_authorized": False, "work_units": WORK,
                      "wall_seconds": time.perf_counter() - started},
                     ensure_ascii=False, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
