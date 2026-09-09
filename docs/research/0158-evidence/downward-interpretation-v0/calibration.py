#!/usr/bin/env python3
"""External finite calibration. No imports or calls into Adva's native kernel."""
import argparse
import copy
import hashlib
import itertools
import json
import resource
import signal
import sys
import time
from pathlib import Path


class Limit(Exception):
    pass


class Invalid(Exception):
    pass


class Budget:
    def __init__(self, maximum):
        self.maximum = maximum
        self.used = 0
        self.by_phase = {}

    def spend(self, phase, n=1):
        if self.used + n > self.maximum:
            raise Limit("logical_work_units")
        self.used += n
        self.by_phase[phase] = self.by_phase.get(phase, 0) + n


def require(condition, message):
    if not condition:
        raise Invalid(message)


def canonical_int(x, lo=0, hi=6):
    return type(x) is int and lo <= x <= hi


def subsets(n):
    return [frozenset(i for i in range(n) if mask & (1 << i))
            for mask in range(1 << n)]


def relational_calibration(budget):
    counts = {"relations": 0, "subset_pairs": 0, "closure_checks": 0,
              "transpose_round_trips": 0}
    for m in range(4):
        for n in range(4):
            X, Q = frozenset(range(m)), frozenset(range(n))
            AS, BS = subsets(m), subsets(n)
            cells = list(itertools.product(range(m), range(n)))
            for mask in range(1 << len(cells)):
                budget.spend("relation")
                R = {pair for i, pair in enumerate(cells) if mask & (1 << i)}
                # Implement derivation by intersections of row/column sets.
                rows = {x: frozenset(q for xx, q in R if xx == x) for x in X}
                cols = {q: frozenset(x for x, qq in R if qq == q) for q in Q}

                def intent(A):
                    out = Q
                    for x in A:
                        out = out & rows[x]
                    return out

                def extent(B):
                    out = X
                    for q in B:
                        out = out & cols[q]
                    return out

                assert extent(frozenset()) == X
                assert intent(frozenset()) == Q
                transposed = {(q, x) for x, q in R}
                assert {(x, q) for q, x in transposed} == R
                counts["transpose_round_trips"] += 1
                for A in AS:
                    closure = extent(intent(A))
                    assert A <= closure
                    assert extent(intent(closure)) == closure
                    counts["closure_checks"] += 1
                    budget.spend("closure")
                    for B in BS:
                        budget.spend("relational_pair")
                        # Independent oracle: inspect every incidence in A x B.
                        oracle = all((x, q) in R for x in A for q in B)
                        assert (B <= intent(A)) == oracle
                        assert (A <= extent(B)) == oracle
                        counts["subset_pairs"] += 1
                for B in BS:
                    closure = intent(extent(B))
                    assert B <= closure
                    assert intent(extent(closure)) == closure
                    counts["closure_checks"] += 1
                    budget.spend("closure")
                counts["relations"] += 1
    return counts


def propose_arithmetic():
    """Supplied feature, not discovered: y=x^2; solve the affine equation."""
    cases = []
    for target in range(7):
        y = (4 * (target - 6)) % 7  # 4 is the inverse of 2 in F7.
        roots = [x for x in range(7) if (x * x) % 7 == y]
        cases.append({"target": target, "abstract_witness": y,
                      "roots": roots, "selected": roots[0] if roots else None,
                      "other_roots": roots[1:],
                      "status": "Lifted" if roots else "NoLiftFiniteScope"})
    return cases


def check_arithmetic(cases, budget):
    require(len(cases) == 7, "target coverage")
    for target, case in enumerate(cases):
        budget.spend("arithmetic_header")
        require(type(case["target"]) is int and case["target"] == target, "target")
        y = case["abstract_witness"]
        require(canonical_int(y), "abstract scalar type")
        require((y + y + 6) % 7 == target, "abstract equation")
        # Reconstruct the square by repeated addition, and check the original
        # equation independently of the producer's affine inversion.
        roots, direct = [], []
        for x in range(7):
            budget.spend("arithmetic_row")
            sq = sum(x for _ in range(x)) % 7
            if sq == y:
                roots.append(x)
            if (sq + sq + 6) % 7 == target:
                direct.append(x)
        require(roots == direct, "downward soundness and complete coverage")
        require(all(canonical_int(x) for x in case["roots"]), "root scalar type")
        require(case["roots"] == roots, "root coverage")
        require(case["selected"] == (roots[0] if roots else None), "selection")
        require(case["other_roots"] == roots[1:], "unselected alternatives")
        require(case["status"] == ("Lifted" if roots else "NoLiftFiniteScope"), "status")


FRAME = "external:F7-square-return:v0"


def propose_return(target, fuel):
    y = (4 * (target - 6)) % 7
    rows = []
    for x in range(min(7, fuel)):
        sq = (x * x) % 7
        rows.append({"x": x, "square": sq, "value": ((2 * x) * x + 6) % 7})
        if sq == y:
            break
    matches = [r["x"] for r in rows if r["square"] == y]
    status = "VerifiedExists" if matches else (
        "RefutedExistsFiniteScope" if len(rows) == 7 else "Unknown")
    return {"frame": FRAME, "target": target, "goal": "exists", "fuel": fuel,
            "abstract_witness": y, "rows": rows,
            "witness": matches[0] if matches else None, "status": status,
            "unvisited": list(range(len(rows), 7))}


def check_return(receipt, target, fuel, budget):
    budget.spend("return_header")
    require(receipt["frame"] == FRAME, "stale frame")
    require(receipt["goal"] == "exists", "goal changed")
    require(canonical_int(receipt["target"]) and receipt["target"] == target, "stale target")
    require(type(receipt["fuel"]) is int and receipt["fuel"] == fuel, "fuel binding")
    y = receipt["abstract_witness"]
    require(canonical_int(y) and (y + y + 6) % 7 == target, "abstract witness")
    rows = receipt["rows"]
    require(len(rows) <= min(fuel, 7), "fuel exceeded")
    found = None
    for i, row in enumerate(rows):
        budget.spend("return_row")
        require(found is None, "continued past declared first-witness stop")
        require(canonical_int(row["x"]) and row["x"] == i, "schedule coverage")
        require(canonical_int(row["square"]) and canonical_int(row["value"]), "scalar type")
        square = sum(i for _ in range(i)) % 7
        value = (square + square + 6) % 7
        require(row["square"] == square and row["value"] == value, "false row")
        if value == target:
            require(square == y, "downward link")
            found = i
    expected = "VerifiedExists" if found is not None else (
        "RefutedExistsFiniteScope" if len(rows) == 7 else "Unknown")
    require(receipt["status"] == expected, "unsupported verdict")
    require(receipt["witness"] is None or canonical_int(receipt["witness"]), "witness type")
    require(receipt["witness"] == found, "unwitnessed selection")
    require(receipt["unvisited"] == list(range(len(rows), 7)), "unvisited residual")
    # Successful semantic acceptance is a prerequisite for local cancellation.
    return {"status": expected, "pending_exists_obligations": 0 if expected != "Unknown" else 1,
            "accepted_response": expected != "Unknown", "history_rows": len(rows)}


def tamper_controls(main, negative, budget):
    mutations = []
    r = copy.deepcopy(main); r["rows"][1]["value"] = 2
    mutations.append(("wrong_value", r, 1, 7))
    r = copy.deepcopy(main); r["target"] = 5
    mutations.append(("stale_target", r, 1, 7))
    r = copy.deepcopy(main); r["frame"] = "external:other-frame:v0"
    mutations.append(("stale_frame", r, 1, 7))
    r = copy.deepcopy(main); r["goal"] = "unique"
    mutations.append(("changed_goal", r, 1, 7))
    r = copy.deepcopy(negative); r["rows"].pop(); r["unvisited"] = [6]
    mutations.append(("missing_coverage", r, 5, 7))
    r = copy.deepcopy(main); r["fuel"] = 0
    mutations.append(("forged_zero_fuel", r, 1, 0))
    r = copy.deepcopy(main); r["rows"][1]["x"] = 0
    mutations.append(("duplicate_position", r, 1, 7))
    r = copy.deepcopy(main); r["rows"][1]["x"] = True
    mutations.append(("boolean_position", r, 1, 7))
    results = []
    for name, r, target, fuel in mutations:
        try:
            check_return(r, target, fuel, budget)
        except Invalid as exc:
            results.append({"control": name, "status": "Rejected", "reason": str(exc)})
        else:
            raise AssertionError("tamper accepted: " + name)
    return results


def structural_countermodels(budget):
    out = {}
    budget.spend("countermodel", 7)
    fibres = {y: [x for x in range(7) if x*x % 7 == y] for y in range(7)}
    assert fibres[1] == [1, 6] and fibres[3] == []
    out["noninjective"] = {"same_feature": 1, "distinct_inputs": [1, 6],
                           "left_inverse": "Impossible for the square map"}
    out["vacuity"] = {"abstract_point": 3, "fibre": [],
                      "all_fibre_members_satisfy_false": all(False for _ in fibres[3]),
                      "existential_witness": any(True for _ in fibres[3])}
    assert out["vacuity"]["all_fibre_members_satisfy_false"]
    assert not out["vacuity"]["existential_witness"]
    vectors = [1, -1]
    assert sum(vectors) == 0 and any(v != 0 for v in vectors)
    out["scalar_zero"] = {"per_obligation_residual": vectors, "scalar_sum": 0,
                          "all_obligations_satisfied": False}
    out["balanced_forgery"] = {"requested_tokens": 1, "claimed_response_tokens": 1,
                              "raw_balance": 0, "payload": {"y": 1, "x": 2},
                              "link_valid": 2*2 % 7 == 1}
    assert not out["balanced_forgery"]["link_valid"]
    R01 = {(0, 0), (1, 1)}
    R12 = {(0, 0), (1, 1)}
    R20 = {(0, 1), (1, 0)}
    solutions = []
    for x, y, z in itertools.product(range(2), repeat=3):
        budget.spend("global_compatibility")
        if (x, y) in R01 and (y, z) in R12 and (z, x) in R20:
            solutions.append([x, y, z])
    assert not solutions
    out["three_way_obstruction"] = {"pair_relations": [sorted(R01), sorted(R12), sorted(R20)],
                                    "each_pair_nonempty": True, "global_solutions": solutions,
                                    "covered_global_assignments": 8}
    restored = [(x*x % 7, fibres[x*x % 7].index(x)) for x in range(7)]
    assert len(set(restored)) == 7
    assert [fibres[y][branch] for y, branch in restored] == list(range(7))
    out["retained_branch"] = {"encoding": restored, "decodes_all_seven": True,
                              "max_fibre_size": 2, "max_branch_bits": 1}
    out["round_trip"] = {"initial_frame": "A", "final_frame": "A",
                         "history": ["A-to-B", "B-to-A"], "spent": 2,
                         "grant": 2, "remaining": 0}
    return out


def run(contract, budget):
    result = {"schema": "external.downward-interpretation.evidence.v0"}
    result["relations"] = relational_calibration(budget)
    cases = propose_arithmetic()
    budget.spend("arithmetic_proposal", 7 * 8)
    check_arithmetic(cases, budget)
    result["arithmetic"] = cases
    receipts = []
    for target, fuel in contract["frozen_families"]["return_runs"]:
        r = propose_return(target, fuel)
        budget.spend("return_proposal", 1 + len(r["rows"]))
        judgment = check_return(r, target, fuel, budget)
        receipts.append({"receipt": r, "judgment": judgment})
    result["return_runs"] = receipts
    result["tamper_controls"] = tamper_controls(receipts[0]["receipt"], receipts[1]["receipt"], budget)
    result["countermodels"] = structural_countermodels(budget)
    # Independent enumeration confirms all 49 original-equation/link rows,
    # then the very same evidence bytes are serialized and replayed.
    encoded = json.dumps(result, sort_keys=True)
    budget.spend("serialization", len(encoded))
    parsed = json.loads(encoded)
    check_arithmetic(parsed["arithmetic"], budget)
    for item, (target, fuel) in zip(parsed["return_runs"], contract["frozen_families"]["return_runs"]):
        replay = check_return(item["receipt"], target, fuel, budget)
        assert replay == item["judgment"]
    result["serialized_arithmetic_replay"] = "Passed"
    result["status"] = "PassedFiniteCalibration"
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=Path(__file__).with_name("contract.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("Refusing overwrite; choose a new output path")
    raw_contract = args.contract.read_bytes()
    if len(raw_contract) > 65536:
        raise SystemExit("Contract too large")
    contract = json.loads(raw_contract)
    limits = contract["limits"]
    resource.setrlimit(resource.RLIMIT_AS, (limits["address_space_mib"]*1024**2,)*2)
    resource.setrlimit(resource.RLIMIT_CPU, (limits["cpu_seconds"],)*2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (limits["file_bytes"],)*2)
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(Limit("wall_seconds")))
    signal.alarm(limits["wall_seconds"])
    start = time.monotonic()
    budget = Budget(limits["logical_work_units"])
    try:
        result = run(contract, budget)
    except Limit as exc:
        result = {"status": "Unknown", "reason": str(exc), "partial_evidence_promoted": False}
    except (AssertionError, Invalid) as exc:
        result = {"status": "ImplementationFailure", "reason": str(exc), "partial_evidence_promoted": False}
    result["contract_sha256"] = hashlib.sha256(raw_contract).hexdigest()
    result["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result["costs"] = {"logical_work_units": budget.used, "by_phase": budget.by_phase,
                       "elapsed_before_final_checkpoint_seconds": time.monotonic()-start,
                       "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                       "final_checkpoint_budget": "one exclusive write, at most 1 MiB; OS resource limits remain active"}
    data = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    if len(data) > limits["file_bytes"]:
        raise SystemExit("Unknown: checkpoint exceeds byte limit")
    with args.output.open("xb") as handle:
        handle.write(data)
    signal.alarm(0)
    print(json.dumps({"status": result["status"], "relations": result.get("relations"),
                      "arithmetic_targets": len(result.get("arithmetic", [])),
                      "tamper_rejections": len(result.get("tamper_controls", [])),
                      "costs": result["costs"], "elapsed_including_checkpoint_seconds": time.monotonic()-start,
                      "output_bytes": len(data)}))
    return 0 if result["status"] == "PassedFiniteCalibration" else 1


if __name__ == "__main__":
    sys.exit(main())
