#!/usr/bin/env python3
"""Original bounded typed-kernel receiver under Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy; account use
is not his review or correctness guarantee. Markov extension is an explicit
formal assumption, not an observation of the world or native authority.
"""
import argparse
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import resource
import signal
import time

PROFILE = "adva.research.kernel-composition.v0"
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


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def same(left, right, name):
    tick()
    demand(canonical(left) == canonical(right), name + ":mismatch")


def rational(value, cap):
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


def distribution(value, cap, name):
    demand(type(value) is list and len(value) == 2, name + ":length")
    result = [rational(item, cap) for item in value]
    demand(all(item >= 0 for item in result) and sum(result) == 1, name + ":mass")
    return result


def space(value, name):
    keys(value, ("id", "labels"), name)
    label(value["id"], name + ":id")
    labels = value["labels"]
    demand(type(labels) is list and len(labels) == 2, name + ":labels-length")
    for item in labels:
        label(item, name + ":label")
    demand(len(set(labels)) == 2, name + ":duplicate-label")


def kernel(value, source, target, name):
    keys(value, ("source", "target", "direction", "rows"), name)
    same(value["source"], source, name + ":source")
    same(value["target"], target, name + ":target")
    demand(value["direction"] == "target-given-source", name + ":direction")
    rows = value["rows"]
    demand(type(rows) is list and len(rows) == 2, name + ":rows")
    return [distribution(row, 64, name + ":row") for row in rows]


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
    spec = importlib.util.spec_from_file_location("typed_kernel_probability_parent", path)
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


def joint_context(expected, left, right, mass, kind):
    carrier = [canonical([left["id"], left["labels"][i], right["id"], right["labels"][j]])
               for i in range(2) for j in range(2)]
    if kind == "BC":
        observation = [left["labels"][0]] * 2 + [left["labels"][1]] * 2
        name, values = "target-index", [0, 1, 0, 1]
    else:
        observation = right["labels"] * 2
        name, values = "source-index", [0, 0, 1, 1]
    tick(8)
    return {"question": expected["question"] + "/" + kind,
            "carrier": carrier, "reference": [[1, 4] for _ in range(4)],
            "probability": [pair(mass[i][j]) for i in range(2) for j in range(2)],
            "observation": observation,
            "observable": {"name": name, "unit": "index", "values": [[x, 1] for x in values]},
            "history": expected["history"] + expected["steps"][:1 if kind == "AB" else 2],
            "scope": "complete-declared-finite-carrier"}


def request(value):
    keys(value, ("question", "source", "middle", "target", "prior", "first_kernel",
                 "second_kernel", "second_prior", "assumption", "history", "steps"), "request")
    label(value["question"], "question")
    for name in ("source", "middle", "target"):
        space(value[name], name)
    demand(len({value[name]["id"] for name in ("source", "middle", "target")}) == 3,
           "spaces:distinct-ids")
    demand(value["assumption"] in ("markov-extension", "unspecified"), "assumption:unsupported")
    history, steps = value["history"], value["steps"]
    demand(type(history) is list and 1 <= len(history) <= 2, "history:length")
    demand(type(steps) is list and len(steps) == 2, "steps:length")
    for item in history + steps:
        label(item, "history-or-step")
    p = distribution(value["prior"], 64, "prior")
    k = kernel(value["first_kernel"], value["source"], value["middle"], "first-kernel")
    l = kernel(value["second_kernel"], value["middle"], value["target"], "second-kernel")
    second_prior = distribution(value["second_prior"], 1024, "second-prior")
    q = [sum(p[i] * k[i][j] for i in range(2)) for j in range(2)]
    m = [[sum(k[i][j] * l[j][h] for j in range(2)) for h in range(2)] for i in range(2)]
    r = [sum(q[j] * l[j][h] for j in range(2)) for h in range(2)]
    tick(16)
    demand(second_prior == q, "middle:prior-binding")
    for item in q + r + [x for row in m for x in row]:
        rational(pair(item), 1024)
    contexts = {
        "AB": joint_context(value, value["source"], value["middle"],
                            [[p[i] * k[i][j] for j in range(2)] for i in range(2)], "AB"),
        "BC": joint_context(value, value["middle"], value["target"],
                            [[q[j] * l[j][h] for h in range(2)] for j in range(2)], "BC"),
        "AC": joint_context(value, value["source"], value["target"],
                            [[p[i] * m[i][h] for h in range(2)] for i in range(2)], "AC"),
    }
    for context in contexts.values():
        parent_call(PARENT.context, context)
    return {"p": p, "q": q, "m": m, "r": r, "contexts": contexts,
            "unobserved_middle": [value["middle"]["labels"][j] for j in range(2) if q[j] == 0]}


def verify(expected, receipt, prepared, checked):
    keys(receipt, ("profile", "request", "interfaces", "claims"), "receipt")
    demand(receipt["profile"] == PROFILE, "profile:unsupported")
    same(receipt["request"], expected, "request:binding")
    interfaces = receipt["interfaces"]
    keys(interfaces, ("AB", "BC", "AC"), "interfaces")
    for name in ("AB", "BC", "AC"):
        item = interfaces[name]
        keys(item, ("profile", "context", "claims"), name + ":receipt")
        arrays = parent_call(PARENT.context, item["context"])
        parent_call(PARENT.verify, item["context"], item, arrays)
        checked.append(name)
    for name in ("AB", "BC"):
        same(interfaces[name]["context"], prepared["contexts"][name], name + ":requested-context")
    endpoint = interfaces["AC"]["context"]
    expected_endpoint = prepared["contexts"]["AC"]
    same({k: v for k, v in endpoint.items() if k != "probability"},
         {k: v for k, v in expected_endpoint.items() if k != "probability"},
         "AC:nonprobability-context")
    mass = [rational(item, 1024) for item in endpoint["probability"]]
    demand([mass[0] + mass[1], mass[2] + mass[3]] == prepared["p"], "AC:source-marginal")
    demand([mass[0] + mass[2], mass[1] + mass[3]] == prepared["r"], "AC:target-marginal")
    tick(4)
    claims = receipt["claims"]
    keys(claims, ("middle_prior", "composed_kernel", "target_prior"), "claims")
    same(claims["middle_prior"], [pair(item) for item in prepared["q"]], "claims:middle-prior")
    same(claims["composed_kernel"], [[pair(item) for item in row] for row in prepared["m"]],
         "claims:composed-kernel")
    same(claims["target_prior"], [pair(item) for item in prepared["r"]], "claims:target-prior")
    if expected["assumption"] == "unspecified":
        return False
    same(endpoint, expected_endpoint, "AC:markov-extension-context")
    return True


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
    expected, accepted_endpoint, composed_kernel = None, None, None
    checked, unobserved, delta = [], [], []
    outcome, reason = "ImplementationFailure", "unstarted"
    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 3)
    try:
        constrain_process()
        load_parent()
        try:
            expected = read(args.expected)
            prepared = request(expected)
            unobserved = prepared["unobserved_middle"]
        except (ValueError, TypeError, KeyError, RecursionError) as error:
            raise Refusal("InvalidContext", str(error)) from error
        try:
            receipt = read(args.candidate)
            accepted = verify(expected, receipt, prepared, checked)
        except (ValueError, TypeError, KeyError, RecursionError) as error:
            raise Refusal("InvalidEvidence", str(error)) from error
        if accepted:
            outcome, reason = "AcceptedMarkovKernelComposition", "all-declared-markov-composition-checks-passed"
            accepted_endpoint = prepared["contexts"]["AC"]
            composed_kernel = [[pair(item) for item in row] for row in prepared["m"]]
            delta = ["three finite interface receipts independently checked",
                     "typed adjacent spaces and complete middle prior bound",
                     "exact row-stochastic composition checked under declared Markov extension",
                     "zero-mass middle labels and full ordered history retained"]
        else:
            outcome, reason = "UnknownDependence", "dependence-premise-not-selected"
    except Refusal as error:
        outcome, reason = error.outcome, error.reason
    except Exception as error:
        outcome, reason = "ImplementationFailure", type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    if outcome != "AcceptedMarkovKernelComposition":
        accepted_endpoint, composed_kernel, delta = None, None, []
    print(json.dumps({"profile": PROFILE, "outcome": outcome, "reason": reason,
                      "expected_request": expected, "interface_arithmetic_checked": checked,
                      "accepted_endpoint": accepted_endpoint, "composed_kernel": composed_kernel,
                      "unobserved_middle": unobserved, "semantic_delta": delta,
                      "native_authority": False, "close_authorized": False, "free_authorized": False,
                      "work_units": WORK, "wall_seconds": time.perf_counter() - started},
                     sort_keys=True, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
