#!/usr/bin/env python3
import copy
import hashlib
import itertools
import json
import resource
import time
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
IDENTITY = (1, 2, 3, 4)
W0 = (4, 3, 2, 1)
RELATIONS = {
    ("1", "3"): ("3", "1"),
    ("3", "1"): ("1", "3"),
    ("1", "2", "1"): ("2", "1", "2"),
    ("2", "1", "2"): ("1", "2", "1"),
    ("2", "3", "2"): ("3", "2", "3"),
    ("3", "2", "3"): ("2", "3", "2"),
}


def canonical_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def step(permutation, generator):
    result = list(permutation)
    i = int(generator) - 1
    result[i], result[i + 1] = result[i + 1], result[i]
    return tuple(result)


def act(word, start=IDENTITY):
    p = start
    vertices = [p]
    for generator in word:
        p = step(p, generator)
        vertices.append(p)
    return p, vertices


def inversion_count(permutation):
    return sum(permutation[i] > permutation[j] for i in range(4) for j in range(i + 1, 4))


def edge_key(u, v):
    return (u, v) if u < v else (v, u)


def edge_chain(vertices):
    chain = Counter()
    for u, v in zip(vertices, vertices[1:]):
        key = edge_key(u, v)
        chain[key] += 1 if key == (u, v) else -1
    return chain


def subtract_chain(left, right):
    result = Counter(left)
    result.subtract(right)
    return Counter({key: value for key, value in result.items() if value})


def face_id(prefix_permutation, generators):
    pair = set(generators)
    if pair == {"1", "3"}:
        a, b = sorted(prefix_permutation[:2])
        return f"Q_{a}{b}", ("1", "3"), 2
    if pair == {"1", "2"}:
        return f"H_12({prefix_permutation[3]})", ("1", "2"), 3
    if pair == {"2", "3"}:
        return f"H_23({prefix_permutation[0]})", ("2", "3"), 3
    raise ValueError(f"not a rank-two face: {generators}")


def canonical_face_boundary(prefix_permutation, generators, braid_length):
    # Move to the lexicographically least vertex in this rank-two coset, then
    # traverse the alternating cycle beginning with the smaller generator.
    seen = {prefix_permutation}
    frontier = [prefix_permutation]
    while frontier:
        p = frontier.pop()
        for generator in generators:
            q = step(p, generator)
            if q not in seen:
                seen.add(q)
                frontier.append(q)
    start = min(seen)
    cycle_word = "".join(generators) * braid_length
    end, vertices = act(cycle_word, start)
    assert end == start and set(vertices[:-1]) == seen
    return edge_chain(vertices)


def find_local_rewrite(before, after):
    if len(before) != len(after):
        return None
    for offset in range(len(before)):
        for old, new in RELATIONS.items():
            width = len(old)
            if tuple(before[offset:offset + width]) != old:
                continue
            candidate = before[:offset] + "".join(new) + before[offset + width:]
            if candidate == after:
                return offset, old, new
    return None


def occurrence(side, ordinal, before, after):
    rewrite = find_local_rewrite(before, after)
    if rewrite is None:
        raise ValueError("NonLocalRewrite")
    offset, old, new = rewrite
    prefix = before[:offset]
    prefix_permutation, _ = act(prefix)
    identifier, generators, braid_length = face_id(prefix_permutation, old)
    before_end, before_vertices = act("".join(old), prefix_permutation)
    after_end, after_vertices = act("".join(new), prefix_permutation)
    if before_end != after_end:
        raise ValueError("RewriteEndpointMismatch")
    local_boundary = subtract_chain(edge_chain(after_vertices), edge_chain(before_vertices))
    canonical_boundary = canonical_face_boundary(prefix_permutation, generators, braid_length)
    if local_boundary == canonical_boundary:
        orientation = 1
    elif local_boundary == Counter({key: -value for key, value in canonical_boundary.items()}):
        orientation = -1
    else:
        raise ValueError("FaceBoundaryMismatch")
    return {
        "side": side,
        "ordinal": ordinal,
        "before": before,
        "after": after,
        "offset": offset,
        "relation": "".join(old) + "->" + "".join(new),
        "face_id": identifier,
        "orientation": orientation,
    }, canonical_boundary


def enumerate_reduced_graph():
    words = []
    for symbols in itertools.product("123", repeat=6):
        word = "".join(symbols)
        target, _ = act(word)
        if target == W0 and inversion_count(target) == len(word):
            words.append(word)
    word_set = set(words)
    edges = set()
    for word in words:
        for other in words:
            if word < other and find_local_rewrite(word, other) is not None:
                edges.add((word, other))
    return words, sorted(edges)


def build_receipt(left_path, right_path):
    if left_path[0] != right_path[0] or left_path[-1] != right_path[-1]:
        raise ValueError("PathEndpointMismatch")
    occurrences = []
    boundaries = {}
    for side, path in (("L", left_path), ("R", right_path)):
        for ordinal, (before, after) in enumerate(zip(path, path[1:])):
            item, boundary = occurrence(side, ordinal, before, after)
            occurrences.append(item)
            boundaries[item["face_id"]] = boundary
    coefficients = Counter()
    for item in occurrences:
        side_sign = 1 if item["side"] == "L" else -1
        coefficients[item["face_id"]] += side_sign * item["orientation"]
    edge_boundary = Counter()
    for identifier, coefficient in coefficients.items():
        for edge, value in boundaries[identifier].items():
            edge_boundary[edge] += coefficient * value
    edge_boundary = Counter({key: value for key, value in edge_boundary.items() if value})
    return {
        "schema": "adva.research.signed-face-sweep-receipt.v0",
        "start_word": left_path[0],
        "end_word": left_path[-1],
        "occurrences": occurrences,
        "face_coefficients": dict(sorted(coefficients.items())),
        "edge_boundary_nonzero": [
            {"edge": [list(edge[0]), list(edge[1])], "coefficient": value}
            for edge, value in sorted(edge_boundary.items())
        ],
        "typed_comparison": "NotConstructed",
        "m6_filler": "NotConstructed",
    }


def validate_receipt(receipt, left_path, right_path):
    try:
        expected = build_receipt(left_path, right_path)
    except ValueError as error:
        return f"Refused/{error.args[0]}"
    occurrences = receipt.get("occurrences")
    if not isinstance(occurrences, list) or len(occurrences) != 14:
        return "Refused/OccurrenceCountMismatch"
    if occurrences != expected["occurrences"]:
        for observed, wanted in itertools.zip_longest(occurrences, expected["occurrences"]):
            if observed is None or wanted is None:
                return "Refused/OccurrenceCountMismatch"
            if observed.get("side") != wanted.get("side") or observed.get("ordinal") != wanted.get("ordinal") or observed.get("before") != wanted.get("before") or observed.get("after") != wanted.get("after"):
                return "Refused/OccurrenceOrderMismatch"
            if observed.get("face_id") != wanted.get("face_id"):
                return "Refused/FaceLabelMismatch"
            if observed.get("orientation") != wanted.get("orientation"):
                return "Refused/FaceOrientationMismatch"
            return "Refused/OccurrencePayloadMismatch"
    if receipt.get("face_coefficients") != expected["face_coefficients"]:
        return "Refused/FaceCoefficientMismatch"
    if receipt.get("edge_boundary_nonzero") != []:
        return "Refused/NonzeroEdgeBoundary"
    if receipt.get("typed_comparison") != "NotConstructed" or receipt.get("m6_filler") != "NotConstructed":
        return "Refused/PrematureSemanticPromotion"
    face_ids = set(receipt["face_coefficients"])
    expected_faces = {f"Q_{a}{b}" for a, b in itertools.combinations(range(1, 5), 2)} | {f"H_12({d})" for d in range(1, 5)} | {f"H_23({d})" for d in range(1, 5)}
    if face_ids != expected_faces or set(abs(v) for v in receipt["face_coefficients"].values()) != {1}:
        return "Refused/FaceCoverageMismatch"
    return "VerifiedFundamentalBoundary/OccurrenceHistoryRetained"


def chain_only(receipt):
    return {
        "face_coefficients": receipt.get("face_coefficients"),
        "edge_boundary_nonzero": receipt.get("edge_boundary_nonzero"),
    }


def main():
    started = time.perf_counter_ns()
    input_record = json.loads((ROOT / "input.json").read_text())
    left = input_record["left_path"]
    right = input_record["right_path"]
    constructed = time.perf_counter_ns()

    words, edges = enumerate_reduced_graph()
    canonical = build_receipt(left, right)
    reversed_receipt = build_receipt(list(reversed(left)), list(reversed(right)))

    reordered = copy.deepcopy(canonical)
    reordered["occurrences"][0], reordered["occurrences"][1] = reordered["occurrences"][1], reordered["occurrences"][0]
    relabelled = copy.deepcopy(canonical)
    relabelled["occurrences"][0]["face_id"] = "Q_99"
    sign_tampered = copy.deepcopy(canonical)
    sign_tampered["occurrences"][0]["orientation"] *= -1
    omitted = copy.deepcopy(canonical)
    omitted["occurrences"].pop()
    coefficient_tampered = copy.deepcopy(canonical)
    first_face = sorted(coefficient_tampered["face_coefficients"])[0]
    coefficient_tampered["face_coefficients"][first_face] *= -1
    promoted = copy.deepcopy(canonical)
    promoted["m6_filler"] = "Constructed"
    bad_left = left[:3] + ["111111"] + left[4:]

    cases = [
        ("canonical", canonical, left, right),
        ("reordered-occurrences", reordered, left, right),
        ("relabelled-face", relabelled, left, right),
        ("sign-tampered", sign_tampered, left, right),
        ("omitted-occurrence", omitted, left, right),
        ("coefficient-tampered", coefficient_tampered, left, right),
        ("premature-filler", promoted, left, right),
        ("fresh-reversed-paths", reversed_receipt, list(reversed(left)), list(reversed(right))),
    ]
    rows = []
    canonical_projection = chain_only(canonical)
    for name, receipt, left_case, right_case in cases:
        projection = chain_only(receipt)
        rows.append({
            "name": name,
            "chain_only_equal_to_canonical": projection == canonical_projection,
            "receipt_result": validate_receipt(receipt, left_case, right_case),
        })
    bad_path_result = validate_receipt(canonical, bad_left, right)
    verified = time.perf_counter_ns()

    expected = {
        "canonical": "VerifiedFundamentalBoundary/OccurrenceHistoryRetained",
        "reordered-occurrences": "Refused/OccurrenceOrderMismatch",
        "relabelled-face": "Refused/FaceLabelMismatch",
        "sign-tampered": "Refused/FaceOrientationMismatch",
        "omitted-occurrence": "Refused/OccurrenceCountMismatch",
        "coefficient-tampered": "Refused/FaceCoefficientMismatch",
        "premature-filler": "Refused/PrematureSemanticPromotion",
        "fresh-reversed-paths": "VerifiedFundamentalBoundary/OccurrenceHistoryRetained",
    }
    actual = {row["name"]: row["receipt_result"] for row in rows}
    checks = {
        "all_expected": actual == expected,
        "enumerated_words": 3 ** 6,
        "reduced_expression_vertices": len(words),
        "reduced_expression_edges": len(edges),
        "q4_faces": sum(key.startswith("Q_") for key in canonical["face_coefficients"]),
        "m6_faces": sum(key.startswith("H_") for key in canonical["face_coefficients"]),
        "canonical_zero_edge_boundary": canonical["edge_boundary_nonzero"] == [],
        "reordered_history_invisible_to_chain_only": chain_only(reordered) == canonical_projection,
        "bad_path_result": bad_path_result,
        "no_semantic_promotion": canonical["typed_comparison"] == "NotConstructed" and canonical["m6_filler"] == "NotConstructed",
    }
    if not (
        checks["all_expected"]
        and checks["reduced_expression_vertices"] == 16
        and checks["reduced_expression_edges"] == 18
        and checks["q4_faces"] == 6
        and checks["m6_faces"] == 8
        and checks["canonical_zero_edge_boundary"]
        and checks["reordered_history_invisible_to_chain_only"]
        and checks["bad_path_result"] == "Refused/NonLocalRewrite"
        and checks["no_semantic_promotion"]
    ):
        raise AssertionError(checks)

    baseline_started = time.perf_counter_ns()
    baseline_bytes = canonical_bytes(canonical_projection)
    baseline_formation_ns = time.perf_counter_ns() - baseline_started
    explicit_started = time.perf_counter_ns()
    explicit_bytes = canonical_bytes(canonical)
    explicit_formation_ns = time.perf_counter_ns() - explicit_started

    outcome = {
        "schema": "adva.research.signed-face-sweep-receipt.outcome.v0",
        "status": "PassedBoundedSignedFaceSweepReceipt",
        "claim": "The two supplied A3 rewrite paths independently enumerate one signed fundamental boundary with six Q4 and eight M6 face occurrences while retaining each occurrence history.",
        "graph": {
            "words_examined": 3 ** 6,
            "reduced_expression_vertices": len(words),
            "rewrite_edges": len(edges),
        },
        "canonical_receipt": canonical,
        "instances": rows,
        "extra_bad_path_control": bad_path_result,
        "checks": checks,
        "comparison": {
            "baseline_chain_only_bytes": len(baseline_bytes),
            "baseline_formation_ns": baseline_formation_ns,
            "explicit_receipt_bytes": len(explicit_bytes),
            "explicit_formation_ns": explicit_formation_ns,
            "formation_byte_delta": len(explicit_bytes) - len(baseline_bytes),
            "finite_distinction": "the reordered occurrence history has the same chain-only projection but the full receipt refuses it",
            "claim_boundary": "No global expressivity or efficiency theorem is claimed."
        },
        "cost": {
            "routes": 1,
            "search_candidates": 3 ** 6,
            "receipt_cases": len(rows),
            "construction_ns": constructed - started,
            "enumeration_evaluation_verification_ns": verified - constructed,
            "serialization_ns": None,
            "serialized_bytes": None,
            "ru_maxrss_kib_before_serialization": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "implementation_correction_replays": 0,
        },
        "proposed_word": {
            "word": "signed face-sweep receipt",
            "state": "Proposed",
            "role": "bind a signed cellular face chain to the ordered local rewrite occurrences that produced it",
            "input": "two finite paths of reduced expressions with common endpoints and declared Q4/M6 local rewrite grammar",
            "output_relation": "VerifiedFundamentalBoundary/OccurrenceHistoryRetained or an occurrence-, face-, sign-, coverage- or promotion-specific refusal",
            "applicability": "every adjacent pair is one declared rank-two rewrite and both paths share endpoints in the finite A3 reduced-expression graph",
            "witness": "the 16-vertex, 18-edge graph; fourteen canonical occurrences; six fixed negative receipts; one nonlocal path control; and one reversed-path reuse",
            "refusal_conditions": [
                "nonlocal rewrite or unequal path endpoints",
                "missing or reordered occurrence",
                "face label, orientation or coefficient mismatch",
                "nonzero edge boundary or incomplete fourteen-face coverage",
                "typed comparison or M6 filler claimed by the receipt"
            ],
            "expansion": "replay each gallery, identify its rank-two coset face from the prefix permutation, orient the face from the local path difference, telescope both path sweeps, check all fourteen face coefficients and zero edge boundary, and retain every step occurrence",
            "counterexample": "swapping two stored occurrences leaves the chain-only projection byte-identical but breaks path order and is refused",
            "replay": "timeout 30s python3 run.py",
            "residual": "the receipt does not construct a common typed comparison in a target category, compose relation witnesses natively, prove arbitrary A_n coherence, or supply any Q4/M6 filler"
        },
        "claim_boundary": "This independently checks the finite A3 cellular calculation only. Additive-zero and multiplicative-unit domains are untouched; no arithmetic-universality or hypothesized-arithmetic-truth evidence follows."
    }
    before_serialization = time.perf_counter_ns()
    canonical_bytes(outcome)
    outcome["cost"]["serialization_ns"] = time.perf_counter_ns() - before_serialization
    previous = -1
    while previous != outcome["cost"]["serialized_bytes"]:
        previous = outcome["cost"]["serialized_bytes"]
        outcome["cost"]["serialized_bytes"] = len(canonical_bytes(outcome))
    data = canonical_bytes(outcome)
    (ROOT / "outcome.json").write_bytes(data)
    print(json.dumps({
        "status": outcome["status"],
        "checks": checks,
        "baseline_bytes": len(baseline_bytes),
        "explicit_bytes": len(explicit_bytes),
        "serialized_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "ru_maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
