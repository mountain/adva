#!/usr/bin/env python3
"""Original finite research receiver under Unknown v0.3; no native authority.

ChatGPT (OpenAI), through Mingli Yuan's account proxy; no endorsement or
correctness guarantee. Work units count parsed rationals, checked scalar
equalities, and enumerated carrier/atom terms, not CPU instructions.
"""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import signal
import time

PROFILE = "adva.research.probability-receipt.v0"
CONTEXT = {"question", "carrier", "reference", "probability", "observation",
           "observable", "history", "scope"}
CLAIMS = {"density", "density_mean", "density_energy", "density_variance",
          "atoms", "observed_energy", "hidden_residual", "expectation",
          "variance", "tower_expectation", "within_variance", "between_variance"}
ATOM = {"label", "reference_mass", "probability_mass", "density", "conditional",
        "conditional_mean", "conditional_variance"}
WORK = 0


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


def rational(value, cap=1000000000):
    tick()
    demand(type(value) is list and len(value) == 2, "rational:shape")
    a, b = value
    demand(type(a) is int and type(b) is int, "rational:integer-type")
    demand(abs(a) <= cap and 0 < b <= cap, "rational:bound")
    result = Fraction(a, b)
    demand(result.numerator == a and result.denominator == b, "rational:canonical")
    return result


def vector(value, size, cap=1000000000):
    demand(type(value) is list and len(value) == size, "vector:length")
    return [rational(item, cap) for item in value]


def equal(value, expected, label):
    tick()
    demand(rational(value) == expected, label + ":mismatch")


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


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def context(value):
    keys(value, CONTEXT, "context")
    demand(type(value["question"]) is str, "question:type")
    carrier = value["carrier"]
    demand(type(carrier) is list and 1 <= len(carrier) <= 6, "carrier:length")
    demand(all(type(x) is str for x in carrier), "carrier:type")
    demand(len(set(carrier)) == len(carrier), "carrier:duplicate")
    n = len(carrier)
    reference = vector(value["reference"], n, 1024)
    probability = vector(value["probability"], n, 1024)
    demand(all(x > 0 for x in reference) and sum(reference) == 1, "reference:mass")
    demand(all(x >= 0 for x in probability) and sum(probability) == 1, "probability:mass")
    observation = value["observation"]
    demand(type(observation) is list and len(observation) == n, "observation:length")
    demand(all(type(x) is str and x for x in observation), "observation:type")
    obs = value["observable"]
    keys(obs, {"name", "unit", "values"}, "observable")
    demand(type(obs["name"]) is str and type(obs["unit"]) is str, "observable:labels")
    values = vector(obs["values"], n, 1024)
    history = value["history"]
    demand(type(history) is list and 1 <= len(history) <= 4, "history:length")
    demand(all(type(x) is str for x in history), "history:type")
    demand(value["scope"] == "complete-declared-finite-carrier", "scope:unsupported")
    return reference, probability, observation, values


def verify(expected, receipt, arrays):
    keys(receipt, {"profile", "context", "claims"}, "receipt")
    demand(receipt["profile"] == PROFILE, "profile:unsupported")
    demand(canonical(receipt["context"]) == canonical(expected), "context:binding")
    claim = receipt["claims"]
    keys(claim, CLAIMS, "claims")
    lam, prob, obs, values = arrays
    n = len(lam)
    density = vector(claim["density"], n)
    for i in range(n):
        tick()
        demand(density[i] * lam[i] == prob[i], "density:pointwise")
    mean = sum(lam[i] * density[i] for i in range(n))
    energy = sum(lam[i] * density[i] ** 2 for i in range(n))
    spread = sum(lam[i] * (density[i] - 1) ** 2 for i in range(n))
    equal(claim["density_mean"], mean, "density_mean")
    equal(claim["density_energy"], energy, "density_energy")
    equal(claim["density_variance"], spread, "density_variance")
    demand(mean == 1 and energy == 1 + spread, "density:identity")
    expectation = sum(prob[i] * values[i] for i in range(n))
    variance = sum(prob[i] * (values[i] - expectation) ** 2 for i in range(n))
    equal(claim["expectation"], expectation, "expectation")
    equal(claim["variance"], variance, "variance")
    labels = sorted(set(obs))
    atoms = claim["atoms"]
    demand(type(atoms) is list and len(atoms) == len(labels), "atoms:length")
    observed = hidden = tower = within = between = Fraction(0)
    for label, atom in zip(labels, atoms):
        tick(n + 1)
        keys(atom, ATOM, "atom")
        demand(atom["label"] == label, "atom:label-order")
        indexes = [i for i in range(n) if obs[i] == label]
        lmass = sum(lam[i] for i in indexes)
        pmass = sum(prob[i] for i in indexes)
        ratio = pmass / lmass
        equal(atom["reference_mass"], lmass, "atom:reference_mass")
        equal(atom["probability_mass"], pmass, "atom:probability_mass")
        equal(atom["density"], ratio, "atom:density")
        observed += lmass * ratio ** 2
        hidden += sum(lam[i] * (density[i] - ratio) ** 2 for i in indexes)
        if pmass == 0:
            demand(all(atom[k] is None for k in ("conditional", "conditional_mean",
                                                 "conditional_variance")), "atom:zero-event")
            continue
        conditional = vector(atom["conditional"], n)
        for i in range(n):
            tick()
            wanted = prob[i] if obs[i] == label else Fraction(0)
            demand(conditional[i] * pmass == wanted, "atom:conditional-law")
        demand(sum(conditional) == 1, "atom:conditional-mass")
        mu = sum(conditional[i] * values[i] for i in range(n))
        var = sum(conditional[i] * (values[i] - mu) ** 2 for i in range(n))
        equal(atom["conditional_mean"], mu, "atom:conditional_mean")
        equal(atom["conditional_variance"], var, "atom:conditional_variance")
        tower += pmass * mu
        within += pmass * var
        between += pmass * (mu - expectation) ** 2
    equal(claim["observed_energy"], observed, "observed_energy")
    equal(claim["hidden_residual"], hidden, "hidden_residual")
    equal(claim["tower_expectation"], tower, "tower_expectation")
    equal(claim["within_variance"], within, "within_variance")
    equal(claim["between_variance"], between, "between_variance")
    demand(energy == observed + hidden and hidden >= 0, "observation:identity")
    demand(expectation == tower and variance == within + between, "conditioning:identity")


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
        outcome, reason = "AcceptedFiniteReceipt", "all-declared-finite-checks-passed"
        delta = ["context-bound exact finite probability checks", "density and observation decomposition",
                 "conditional law, tower expectation and total variance on the declared carrier"]
    except Refusal as error:
        outcome, reason = error.outcome, error.reason
    except Exception as error:
        outcome, reason = "ImplementationFailure", type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    print(json.dumps({"profile": PROFILE, "outcome": outcome, "reason": reason,
                      "expected_context": expected, "semantic_delta": delta,
                      "native_authority": False, "close_authorized": False, "free_authorized": False,
                      "work_units": WORK, "wall_seconds": time.perf_counter() - started},
                     ensure_ascii=False, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
