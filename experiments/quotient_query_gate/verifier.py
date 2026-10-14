"""Independent brute-force receiver for quotient-query evidence."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path


def valid_family(bits, n):
    full = (1 << n) - 1
    family = {m for m in range(1 << n) if (bits >> m) & 1}
    for m in range(1 << n):
        if ((m in family) == ((full ^ m) in family)):
            return None
    for s in family:
        for t in range(1 << n):
            if s & ~t == 0 and t not in family:
                return None
    return tuple(sorted(family))


def brute_models(n):
    out = []
    candidates = 1 << (1 << n)
    for bits in range(candidates):
        model = valid_family(bits, n)
        if model is not None:
            out.append(model)
    return sorted(out), candidates


def realizers(model, n):
    return [i for i in range(n) if all((m >> i) & 1 for m in model)]


def lift(q, mask):
    return sum(1 << i for i, label in enumerate(q) if (mask >> label) & 1)


def gate(q, mask):
    for i in range(len(q)):
        for j in range(i + 1, len(q)):
            if q[i] == q[j] and ((mask >> i) & 1) != ((mask >> j) & 1):
                return {"status": "NonSaturated", "counterexample": [i, j]}
    result = 0
    for label in range(max(q) + 1):
        i = q.index(label)
        result |= ((mask >> i) & 1) << label
    return {"status": "Descends", "quotient_mask": result}


def classification(models, mask):
    values = [mask in m for m in models]
    return "ForcedPositive" if all(values) else "ForcedNegative" if not any(values) else "Underdetermined"


def expected_fixture(spec):
    n, q = spec["carrier_size"], spec["quotient"]
    if len(q) != n or not q or sorted(set(q)) != list(range(max(q) + 1)):
        raise ValueError("invalid quotient")
    k = max(q) + 1
    exact, exact_work = brute_models(n)
    quotient, quotient_work = brute_models(k)
    quotient_set = set(quotient)
    sat = {lift(q, m): m for m in range(1 << k)}
    restrictions, basic_mult, joint_mult = [], {}, {}
    for model in exact:
        restricted = tuple(sorted(sat[m] for m in model if m in sat))
        if restricted not in quotient_set:
            raise ValueError("bad restriction")
        key = ",".join(map(str, restricted))
        basic_mult[key] = basic_mult.get(key, 0) + 1
        rs = realizers(model, n)
        if rs:
            joint_mult[key] = joint_mult.get(key, 0) + 1
        restrictions.append({"exact_model": list(model), "quotient_model": list(restricted), "realizers": rs})
    exact_joint = [m for m in exact if realizers(m, n)]
    quotient_joint = [m for m in quotient if realizers(m, k)]
    qm = spec["named_query_quotient_mask"]
    em = lift(q, qm)
    return {
        "name": spec["name"], "carrier_size": n, "quotient_size": k, "quotient": q,
        "saturated_exact_masks": sorted(sat),
        "gates": {str(m): gate(q, m) for m in range(1 << n)},
        "basic": {"exact_models": [list(m) for m in exact], "quotient_models": [list(m) for m in quotient],
                  "lift_multiplicity": dict(sorted(basic_mult.items())),
                  "exact_query": classification(exact, em), "quotient_query": classification(quotient, qm)},
        "joint": {"exact_models": [list(m) for m in exact_joint], "quotient_models": [list(m) for m in quotient_joint],
                  "lift_multiplicity": dict(sorted(joint_mult.items())),
                  "exact_query": classification(exact_joint, em), "quotient_query": classification(quotient_joint, qm)},
        "restrictions": restrictions,
        "receiver_candidate_families": exact_work + quotient_work
    }


def verify(contract, result):
    if result.get("schema") != "adva.quotient-query-gate.result.v0" or result.get("base_commit") != contract.get("base_commit"):
        return {"status": "Rejected", "reason": "binding"}
    expected, work = [], 0
    try:
        for spec in contract["fixtures"]:
            item = expected_fixture(spec)
            work += item.pop("receiver_candidate_families")
            expected.append(item)
    except (KeyError, TypeError, ValueError) as error:
        return {"status": "Rejected", "reason": str(error)}
    if work > contract["budget"]["candidate_families"]:
        return {"status": "Rejected", "reason": "receiver candidate budget"}
    for actual, wanted in zip(result.get("fixtures", []), expected):
        comparable = copy.deepcopy(actual)
        comparable.pop("producer_candidate_families", None)
        comparable.pop("gate_checks", None)
        if comparable != wanted:
            return {"status": "Rejected", "reason": "semantic mismatch", "receiver_candidate_families": work}
    if len(result.get("fixtures", [])) != len(expected):
        return {"status": "Rejected", "reason": "fixture count", "receiver_candidate_families": work}
    return {"status": "Verified", "receiver_candidate_families": work}


def controls(contract, result):
    cases = []
    def mutate(label, edit):
        trial = copy.deepcopy(result); edit(trial)
        cases.append({"name": label, "outcome": verify(contract, trial)["status"]})
    mutate("wrong_lifted_region", lambda r: r["fixtures"][0]["restrictions"][0]["quotient_model"].append(3))
    mutate("wrong_lift_multiplicity", lambda r: r["fixtures"][0]["basic"]["lift_multiplicity"].update({"1,3": 99}))
    mutate("singleton_claimed_to_descend", lambda r: r["fixtures"][0]["gates"]["1"].update(status="Descends", quotient_mask=1))
    mutate("omitted_exact_model", lambda r: r["fixtures"][1]["basic"]["exact_models"].pop())
    mutate("changed_classification", lambda r: r["fixtures"][0]["joint"].update(exact_query="ForcedPositive"))
    bad = copy.deepcopy(contract); bad["fixtures"][0]["quotient"] = [0, 0, 2]
    cases.append({"name": "non_surjective_quotient", "outcome": verify(bad, result)["status"]})
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path); parser.add_argument("result", type=Path); parser.add_argument("output", type=Path)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text()); result = json.loads(args.result.read_text())
    receipt = verify(contract, result); receipt["controls"] = controls(contract, result)
    if any(x["outcome"] != "Rejected" for x in receipt["controls"]):
        receipt = {"status": "Rejected", "reason": "control accepted", "controls": receipt["controls"]}
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    raise SystemExit(0 if receipt["status"] == "Verified" else 2)


if __name__ == "__main__":
    main()
