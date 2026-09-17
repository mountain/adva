#!/usr/bin/env python3
"""Original finite decision checkpoint receiver under Unknown v0.3.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
account use is not his review or a correctness guarantee. This stateless checker
rechecks a saved prefix and a declared continuation. It performs no action,
durable transaction, exactly-once consumption, or native fuel renewal.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import signal
import time

PROFILE = "adva.research.decision-checkpoint.v0"
REQUEST = {"prefix_request", "pending_step", "allowance"}
RECEIPT = {"profile", "checkpoint", "next_receipt", "allowance_after"}
CHECKPOINT = {"prefix_receipt", "endpoint", "pending_step", "allowance"}
ALLOWANCE = {"grant", "spent", "remaining"}
STEP = {"factor", "target_unit", "step"}
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


def embedded_bound(value, maximum, name):
    tick()
    if len(canonical(value).encode("utf-8")) > maximum:
        raise Refusal("UnknownBudget", name + ":wire-byte-limit")


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
        raw = stream.read(131073)
    if len(raw) > 131072:
        raise Refusal("UnknownBudget", "wire-byte-limit")
    return json.loads(raw, object_pairs_hook=unique, parse_constant=constant)


def load_parent():
    """Load one unchanged composition receiver and all unchanged ancestors."""
    global PARENT
    path = Path(__file__).resolve().parents[1] / "decision_scale_composition" / "receive.py"
    spec = importlib.util.spec_from_file_location("decision_checkpoint_parent", path)
    demand(spec is not None and spec.loader is not None, "parent:loader")
    PARENT = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(PARENT)
    PARENT.load_parent()


def parent_call(function, *args):
    """Rechecking, preflights and continuation share one cumulative work cap."""
    global WORK
    PARENT.WORK = WORK
    try:
        return function(*args)
    except PARENT.Refusal as error:
        raise Refusal(error.outcome, "parent:" + error.reason) from error
    finally:
        WORK = PARENT.WORK


def scale_call(function, *args):
    # Do not skip composition.parent_call: it transfers work to/from scale.
    return parent_call(PARENT.parent_call, function, *args)


def allowance(value):
    keys(value, ALLOWANCE, "allowance")
    tick(3)
    demand(all(type(value[name]) is int for name in ALLOWANCE),
           "allowance:integer-type")
    grant, spent, remaining = value["grant"], value["spent"], value["remaining"]
    demand(1 <= grant <= 4 and 0 <= spent <= grant,
           "allowance:bound")
    demand(remaining == grant - spent, "allowance:balance")


def request(value):
    keys(value, REQUEST, "request")
    embedded_bound(value["prefix_request"], 65536, "prefix-request")
    prefix = parent_call(PARENT.request, value["prefix_request"])
    endpoint = prefix[2]
    pending = value["pending_step"]
    keys(pending, STEP, "pending-step")
    factor = scale_call(PARENT.PARENT.rational, pending["factor"], 16)
    demand(factor > 0, "pending-step:positive-factor-required")
    scale_call(PARENT.PARENT.label, pending["target_unit"], "pending-target-unit")
    scale_call(PARENT.PARENT.label, pending["step"], "pending-step")
    tick(2)
    allowance(value["allowance"])

    # Numeric bounds are checked even when the history is already full. A pause
    # must not conceal a malformed task or an out-of-profile arithmetic result.
    values = [item for row in endpoint["loss"] for item in row]
    values.append(endpoint["observation_cost"])
    for item in values:
        scaled = factor * scale_call(PARENT.PARENT.rational, item, 64)
        tick()
        demand(abs(scaled.numerator) <= 64 and scaled.denominator <= 64,
               "pending-step:arithmetic-bound")

    following = {"source": endpoint, **pending}
    embedded_bound(following, 32768, "next-request")
    next_arrays = None
    if len(endpoint["history"]) < 4:
        # This validates the real appended context under the unchanged parent.
        # For history length four no fifth-entry context is accepted or created.
        next_arrays = scale_call(PARENT.PARENT.request, following)
    return prefix, endpoint, following, next_arrays


def verify(expected, receipt, prepared, checked):
    keys(receipt, RECEIPT, "receipt")
    demand(receipt["profile"] == PROFILE, "profile:unsupported")
    checkpoint = receipt["checkpoint"]
    keys(checkpoint, CHECKPOINT, "checkpoint")
    prefix, endpoint, following, next_arrays = prepared
    saved_prefix = checkpoint["prefix_receipt"]
    embedded_bound(saved_prefix, 65536, "prefix-receipt")
    parent_call(PARENT.verify, expected["prefix_request"], saved_prefix, prefix, [])
    checked["prefix"] = True
    same(checkpoint["endpoint"], endpoint, "checkpoint:endpoint")
    same(checkpoint["pending_step"], expected["pending_step"], "checkpoint:pending-step")
    same(checkpoint["allowance"], expected["allowance"], "checkpoint:allowance")
    allowance(receipt["allowance_after"])

    before = expected["allowance"]
    if len(endpoint["history"]) == 4:
        demand(receipt["next_receipt"] is None, "pause:unexpected-next-receipt")
        same(receipt["allowance_after"], before, "pause:allowance-preserved")
        return "PausedHistoryCapacity", "unchanged-four-entry-history-capacity", checkpoint, before
    if before["remaining"] == 0:
        demand(receipt["next_receipt"] is None, "pause:unexpected-next-receipt")
        same(receipt["allowance_after"], before, "pause:allowance-preserved")
        return "PausedAllowance", "no-declared-attempt-allowance-remains", checkpoint, before

    following_receipt = receipt["next_receipt"]
    embedded_bound(following_receipt, 32768, "next-receipt")
    scale_call(PARENT.PARENT.verify, following, following_receipt, next_arrays, [])
    checked["next"] = True
    same(following_receipt["source_receipt"],
         saved_prefix["links"][1]["target_receipt"], "continuation:full-source-receipt")
    after = {"grant": before["grant"], "spent": before["spent"] + 1,
             "remaining": before["remaining"] - 1}
    same(receipt["allowance_after"], after, "continuation:one-attempt-debit")
    return ("AcceptedCheckpointContinuation", "prefix-and-declared-next-step-checked",
            checkpoint, after)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected", required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    expected = None
    checked = {"prefix": False, "next": False}
    retained, after = None, None
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
            result = verify(expected, receipt, prepared, checked)
        except ValueError as error:
            raise Refusal("InvalidEvidence", str(error)) from error
        outcome, reason, retained, after = result
        if outcome == "AcceptedCheckpointContinuation":
            delta = ["complete saved two-step prefix independently rechecked",
                     "pending third step checked at the same complete endpoint",
                     "all four history entries retained without capacity increase",
                     "one abstract attempt debit checked without external consumption"]
    except Refusal as error:
        outcome, reason = error.outcome, error.reason
    except Exception as error:
        outcome, reason = "ImplementationFailure", type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    print(json.dumps({"profile": PROFILE, "outcome": outcome, "reason": reason,
                      "expected_request": expected, "checkpoint_retained": retained,
                      "allowance_after": after, "prefix_checked": checked["prefix"],
                      "next_checked": checked["next"], "semantic_delta": delta,
                      "native_authority": False, "close_authorized": False,
                      "free_authorized": False, "work_units": WORK,
                      "wall_seconds": time.perf_counter() - started},
                     ensure_ascii=False, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
