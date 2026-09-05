"""Frozen finite interface calibration; no native Adva semantic authority.

Search monotone Boolean observations backwards from an order-embedding demand.
Keep execution traces and exhaustive finite comparison evidence separately.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from time import perf_counter


NODES = ("a", "b", "c", "d")
COMPLETED = (frozenset(), frozenset("B"), frozenset("C"), frozenset("BC"))
COARSE_MASKS = (14, 8)  # Some operation completed; both operations completed.
SCHEMA = "adva.research.knowledge-interface-calibration.v1"
FIXTURE = Path(__file__).resolve().parents[2] / "examples/verified_witness/knowledge-interface-diamond.json"


def precedes(left: int, right: int) -> bool:
    return COMPLETED[left] <= COMPLETED[right]


def bit(mask: int, node: int) -> int:
    return (mask >> node) & 1


def coordinates(masks: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(bit(mask, node) for mask in masks) for node in range(4))


def coordinate_leq(left: tuple[int, ...], right: tuple[int, ...]) -> bool:
    return all(a <= b for a, b in zip(left, right, strict=True))


def monotone(mask: int) -> bool:
    return all(
        not precedes(i, j) or bit(mask, i) <= bit(mask, j)
        for i in range(4) for j in range(4)
    )


def mismatches(masks: tuple[int, ...]) -> list[dict[str, object]]:
    values = coordinates(masks)
    return [
        {"left": NODES[i], "right": NODES[j],
         "declared_order": precedes(i, j),
         "coordinate_order": coordinate_leq(values[i], values[j])}
        for i in range(4) for j in range(4)
        if precedes(i, j) != coordinate_leq(values[i], values[j])
    ]


def search_refinement(max_candidates: int = 4) -> dict[str, object]:
    """Fuel counts complete candidate-family checks, not elapsed time."""
    if type(max_candidates) is not int or max_candidates < 0:
        raise ValueError("max_candidates must be a nonnegative integer")
    admitted = tuple(mask for mask in range(16) if monotone(mask))
    available = tuple(mask for mask in admitted if mask not in (0, 15, *COARSE_MASKS))
    families = tuple(
        family for width in range(len(available) + 1)
        for family in itertools.combinations(available, width)
    )
    audit: list[dict[str, object]] = []
    for family in families:
        if len(audit) >= max_candidates:
            return {"status": "Unknown", "checked": audit,
                    "remaining_families": len(families) - len(audit),
                    "next_family": list(family)}
        errors = mismatches(COARSE_MASKS + family)
        audit.append({"added_masks": list(family), "mismatches": errors})
        if not errors:
            return {
                "status": "Found", "boolean_predicates_examined": 16,
                "monotone_masks": list(admitted), "available_masks": list(available),
                "candidate_family_count": len(families), "checked": audit,
                "added_masks": list(family), "minimum_added_coordinates": len(family),
                "minimality_scope": "all monotone Boolean coordinates on these four states",
            }
    return {"status": "Unknown", "checked": audit, "remaining_families": 0,
            "reason": "declared candidate family exhausted"}


def apply_operation(values: tuple[int, ...], operation: str) -> tuple[int, ...]:
    if len(values) != 4 or any(type(v) is not int or v not in (0, 1) for v in values):
        raise ValueError("the calibration domain is exactly four Boolean inputs")
    if operation not in ("B", "C"):
        raise ValueError("unknown comparator")
    left, right = (0, 1) if operation == "B" else (2, 3)
    result = list(values)
    result[left], result[right] = min(values[left], values[right]), max(values[left], values[right])
    return tuple(result)


def trace(values: tuple[int, ...], operations: str) -> list[list[int]]:
    result = [list(values)]
    for operation in operations:
        values = apply_operation(values, operation)
        result.append(list(values))
    return result


def paths() -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for i, source in enumerate(COMPLETED):
        for j, target in enumerate(COMPLETED):
            if source <= target:
                for operations in itertools.permutations(sorted(target - source)):
                    state = source
                    nodes = [NODES[i]]
                    for operation in operations:
                        state = state | {operation}
                        nodes.append(NODES[COMPLETED.index(state)])
                    result.append({"nodes": nodes, "operations": list(operations),
                                   "source": NODES[i], "target": NODES[j],
                                   "cost_in_operations": len(operations)})
    return result


def build_report() -> dict[str, object]:
    search = search_refinement()
    if search["status"] != "Found":
        raise ValueError("frozen search did not find a witness")
    masks = COARSE_MASKS + tuple(search["added_masks"])
    forward = coordinates(masks)
    opposite = tuple(tuple(1 - v for v in row) for row in forward)
    pasts = [{k for k in range(4) if precedes(k, node)} for node in range(4)]
    relation_checks = []
    for i in range(4):
        for j in range(4):
            entailment = all(k not in pasts[i] or k in pasts[j] for k in range(4))
            dual = coordinate_leq(opposite[j], opposite[i])
            if not (precedes(i, j) == coordinate_leq(forward[i], forward[j]) == entailment == dual):
                raise ValueError("relation transport failed")
            relation_checks.append({"left": NODES[i], "right": NODES[j],
                                    "order": precedes(i, j), "past_entailment": entailment,
                                    "opposite_coordinate_order": dual})
    commutation = []
    for values in itertools.product((0, 1), repeat=4):
        bc, cb = trace(values, "BC"), trace(values, "CB")
        if bc[-1] != cb[-1]:
            raise ValueError("disjoint comparator commutation failed")
        commutation.append({"input": list(values), "B_then_C": bc, "C_then_B": cb})
    collision_inputs = ((0, 1, 0, 0), (1, 0, 0, 0))
    collision_outputs = [apply_operation(v, "B") for v in collision_inputs]
    if collision_outputs[0] != collision_outputs[1]:
        raise ValueError("inverse obstruction missing")
    all_paths = paths()
    budget_one = {(p["source"], p["target"]) for p in all_paths if p["cost_in_operations"] <= 1}
    budget_two = {(p["source"], p["target"]) for p in all_paths if p["cost_in_operations"] <= 2}
    counterexample = ["a", "b", "d"]
    if not (("a", "b") in budget_one and ("b", "d") in budget_one and ("a", "d") not in budget_one):
        raise ValueError("bounded composition counterexample missing")
    return {
        "schema": SCHEMA,
        "scope": "Four completion states of two disjoint four-channel Boolean comparators; research-local replay only",
        "model": {"nodes": list(NODES), "completed_operations": [sorted(s) for s in COMPLETED],
                  "comparators": {"B": [0, 1], "C": [2, 3]},
                  "coarse_masks": list(COARSE_MASKS)},
        "search": search,
        "views": {
            "coarse": dict(zip(NODES, coordinates(COARSE_MASKS), strict=True)),
            "refined": dict(zip(NODES, forward, strict=True)),
            "opposite": dict(zip(NODES, opposite, strict=True)),
            "past_sets": {NODES[i]: [NODES[k] for k in sorted(pasts[i])] for i in range(4)},
            "relation_checks": relation_checks,
        },
        "execution": {
            "paths": all_paths, "path_count": len(all_paths),
            "endpoint_pair_count": len({(p["source"], p["target"]) for p in all_paths}),
            "commutation_domain_size": len(commutation), "commutation": commutation,
            "single_valued_inverse_obstruction": {
                "operation": "B", "distinct_inputs": [list(v) for v in collision_inputs],
                "equal_output": list(collision_outputs[0]),
            },
            "whole_network_sorting_counterexample": {
                "input": [1, 1, 0, 0], "output": trace((1, 1, 0, 0), "BC")[-1],
            },
        },
        "budget": {
            "unit": "one comparator operation; excludes host and verification overhead",
            "reachable_pairs_at_one": [list(p) for p in sorted(budget_one)],
            "reachable_pairs_at_two": [list(p) for p in sorted(budget_two)],
            "nontransitivity_at_one": counterexample,
        },
        "open_obligations": [
            "Native Adva identities and interface-transport certificates",
            "Physical interpretation, scales, measurement protocols and embodiment",
            "Definition and evidence for the three physical worlds conjecture",
            "Coherent dynamics and the proposed spectrum-to-vocabulary correspondence",
            "Meaning of the proposed Buddhist three-roots correspondence",
            "Subjective experience and the philosophical awakening conjecture",
        ],
    }


def encoded_report() -> str:
    return json.dumps(build_report(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def check_fixture(path: Path) -> None:
    """Recheck this one frozen problem, including its retained open obligations."""
    if path.read_bytes() != encoded_report().encode("utf-8"):
        raise ValueError("fixture differs from the complete deterministic replay")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write the deterministic research fixture")
    parser.add_argument("--check", type=Path, help="rederive and byte-compare a frozen fixture")
    arguments = parser.parse_args()
    start = perf_counter()
    encoded = encoded_report()
    if arguments.check is not None and arguments.check.read_bytes() != encoded.encode("utf-8"):
        parser.exit(1, "fixture differs from the complete deterministic replay\n")
    if arguments.output is not None:
        arguments.output.write_text(encoded, encoding="utf-8")
    elif arguments.check is None:
        print(encoded, end="")
    print(json.dumps({"replay_seconds": perf_counter() - start,
                      "scope": "report derivation and requested file I/O; excludes startup"}), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
