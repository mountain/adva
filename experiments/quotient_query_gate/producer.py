"""Finite quotient-query producer; project-original under Unknown v0.3."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def quotient_shape(q, n):
    require(len(q) == n, "quotient arity")
    require(all(isinstance(x, int) and x >= 0 for x in q), "quotient labels")
    k = max(q) + 1
    require(sorted(set(q)) == list(range(k)), "quotient must be onto consecutive labels")
    return k


def complement_pairs(n):
    full = (1 << n) - 1
    return [(m, full ^ m) for m in range(1 << n) if m < (full ^ m)]


def upward_closed(family, n):
    for s in family:
        for t in range(1 << n):
            if s & ~t == 0 and t not in family:
                return False
    return True


def models_fast(n):
    pairs = complement_pairs(n)
    models = []
    for choice in range(1 << len(pairs)):
        family = {pair[(choice >> i) & 1] for i, pair in enumerate(pairs)}
        if upward_closed(family, n):
            models.append(tuple(sorted(family)))
    return sorted(models), 1 << len(pairs)


def realizers(model, n):
    return [i for i in range(n) if all((mask >> i) & 1 for mask in model)]


def lift_mask(q, quotient_mask):
    return sum(1 << i for i, label in enumerate(q) if (quotient_mask >> label) & 1)


def gate(q, exact_mask):
    for i in range(len(q)):
        for j in range(i + 1, len(q)):
            if q[i] == q[j] and ((exact_mask >> i) & 1) != ((exact_mask >> j) & 1):
                return {"status": "NonSaturated", "counterexample": [i, j]}
    k = max(q) + 1
    quotient_mask = 0
    for label in range(k):
        members = [i for i, x in enumerate(q) if x == label]
        if (exact_mask >> members[0]) & 1:
            quotient_mask |= 1 << label
    return {"status": "Descends", "quotient_mask": quotient_mask}


def classify(models, mask):
    values = [mask in model for model in models]
    if all(values):
        return "ForcedPositive"
    if not any(values):
        return "ForcedNegative"
    return "Underdetermined"


def fixture_report(spec):
    n, q = spec["carrier_size"], spec["quotient"]
    k = quotient_shape(q, n)
    exact, exact_candidates = models_fast(n)
    quotient, quotient_candidates = models_fast(k)
    quotient_set = set(quotient)
    saturated = {lift_mask(q, m): m for m in range(1 << k)}

    restrictions = []
    basic_mult = {}
    joint_mult = {}
    for model in exact:
        restricted = tuple(sorted(saturated[m] for m in model if m in saturated))
        require(restricted in quotient_set, "restriction is not quotient A1/A2")
        key = ",".join(map(str, restricted))
        basic_mult[key] = basic_mult.get(key, 0) + 1
        restrictions.append({"exact_model": list(model), "quotient_model": list(restricted),
                             "realizers": realizers(model, n)})
        if realizers(model, n):
            joint_mult[key] = joint_mult.get(key, 0) + 1

    exact_joint = [m for m in exact if realizers(m, n)]
    quotient_joint = [m for m in quotient if realizers(m, k)]
    qmask = spec["named_query_quotient_mask"]
    emask = lift_mask(q, qmask)
    gates = {str(mask): gate(q, mask) for mask in range(1 << n)}
    for mask in spec["identity_sensitive_masks"]:
        require(gates[str(mask)]["status"] == "NonSaturated", "control mask unexpectedly descends")

    return {
        "name": spec["name"],
        "carrier_size": n,
        "quotient_size": k,
        "quotient": q,
        "saturated_exact_masks": sorted(saturated),
        "gates": gates,
        "basic": {
            "exact_models": [list(m) for m in exact],
            "quotient_models": [list(m) for m in quotient],
            "lift_multiplicity": dict(sorted(basic_mult.items())),
            "exact_query": classify(exact, emask),
            "quotient_query": classify(quotient, qmask)
        },
        "joint": {
            "exact_models": [list(m) for m in exact_joint],
            "quotient_models": [list(m) for m in quotient_joint],
            "lift_multiplicity": dict(sorted(joint_mult.items())),
            "exact_query": classify(exact_joint, emask),
            "quotient_query": classify(quotient_joint, qmask)
        },
        "restrictions": restrictions,
        "producer_candidate_families": exact_candidates + quotient_candidates,
        "gate_checks": 1 << n
    }


def produce(contract):
    reports = [fixture_report(x) for x in contract["fixtures"]]
    candidates = sum(x["producer_candidate_families"] for x in reports)
    require(candidates <= contract["budget"]["candidate_families"], "candidate budget")
    return {
        "schema": "adva.quotient-query-gate.result.v0",
        "status": "Passed",
        "base_commit": contract["base_commit"],
        "fixtures": reports,
        "producer_candidate_families": candidates,
        "search_candidates": 0,
        "conclusion": "Saturated queries descend, but quotient models need not have unique exact lifts; non-saturated queries are refused with a fibre counterexample."
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    report = produce(json.loads(args.contract.read_text()))
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
