"""Bounded exact self-duality diagnosis of a fixed seven-point incidence set.

Original contribution by ChatGPT (OpenAI), through Mingli Yuan's account proxy,
under Unknown v0.3. This diagnoses the supplied candidate; it neither changes
the geometry nor searches for a new geometric solution. On the red side the
Pascal point at infinity is intentionally excluded from the seven finite points.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
from itertools import permutations
import json
from pathlib import Path
import resource
import signal
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from experiments.pascal_circle_learning import check as checker

MAX_PERMUTATIONS = 10080
MAX_SECONDS = 10
MAX_BYTES = 1048576
POINT_ORDERS = {"red": [1, 3, 5, 7, 9, 11, 13], "blue": [2, 4, 8, 12, 0, 6, 10]}


def line(first, second, center):
    if first == second:
        a, b = first[0] - center[0], first[1] - center[1]
        return (a, b, -a * first[0] - b * first[1])
    return (first[1] - second[1], second[0] - first[0],
            first[0] * second[1] - second[0] * first[1])


def normalize(coefficients):
    factor = next((value for value in coefficients if value), None)
    if factor is None:
        raise ValueError("undefined-line")
    return tuple(value / factor for value in coefficients)


def incident(point, coefficients):
    a, b, c = coefficients
    return a * point[0] + b * point[1] + c == 0


def diagnose(candidate, started=None):
    started = time.monotonic() if started is None else started
    result = {"schema": "adva.external.pascal-circle-duality.v0", "status": "Unknown",
              "permutations_evaluated": 0, "sides": {},
              "scope": "Each side has seven finite points, six tangent-limit hexagon sides, and its Pascal line. No claim about an expanded configuration or arbitrary projective polarity."}
    verified = checker.check_candidate(candidate)
    if verified["status"] != "Verified":
        result.update(reason="candidate-not-verified", candidate_failures=verified["failures"])
        return result
    points = [tuple(map(Fraction, pair)) for pair in candidate["points"]]
    for name, indices in POINT_ORDERS.items():
        center = tuple(map(Fraction, candidate["circles"][name]["center"]))
        sequence = candidate["bindings"][name]["sequence"]
        lines = [line(points[sequence[i]], points[sequence[(i + 1) % 6]], center)
                 for i in range(6)]
        lines.append(line(points[indices[-2]], points[indices[-1]], center))
        existing_lines = set(map(normalize, lines))
        if len(existing_lines) != 7:
            result["reason"] = "seven-distinct-lines-required"
            return result
        matrix = [[int(incident(points[i], coefficients)) for coefficients in lines]
                  for i in indices]
        row_sets = [frozenset(j for j, value in enumerate(row) if value) for row in matrix]
        column_sets = [frozenset(i for i in range(7) if matrix[i][j]) for j in range(7)]
        row_lookup = {neighbors: i for i, neighbors in enumerate(row_sets)}
        if len(row_lookup) != 7:
            result["reason"] = "distinct-point-neighborhoods-required-by-this-profile"
            return result
        row_degrees = list(map(sum, matrix))
        column_degrees = [sum(matrix[i][j] for i in range(7)) for j in range(7)]
        dualities, polarities = [], []
        for forward in permutations(range(7)):
            if time.monotonic() - started > MAX_SECONDS:
                result["reason"] = "wall-limit"
                return result
            if result["permutations_evaluated"] >= MAX_PERMUTATIONS:
                result["reason"] = "permutation-budget-exhausted"
                return result
            result["permutations_evaluated"] += 1
            if any(row_degrees[i] != column_degrees[forward[i]] for i in range(7)):
                continue
            # The image of a line's point-neighborhood must be a point's
            # line-neighborhood. Distinct neighborhoods make the reverse unique.
            reverse = [row_lookup.get(frozenset(forward[i] for i in column_sets[j]))
                       for j in range(7)]
            if all(value is not None for value in reverse) and len(set(reverse)) == 7:
                dualities.append({"points_to_lines": list(forward), "lines_to_points": reverse})
            # For an involution the reverse map is forward^{-1}; this symmetry
            # is the complete incidence test for that additional requirement.
            if all(matrix[i][forward[k]] == matrix[k][forward[i]]
                   for i in range(7) for k in range(i + 1, 7)):
                polarities.append(list(forward))
        missing = [i for i in candidate["circles"][name]["vertices"]
                   if normalize(line(points[i], points[i], center)) not in existing_lines]
        result["sides"][name] = {
            "point_order": indices, "line_order": ["l" + str(i) for i in range(7)],
            "matrix": matrix, "row_degrees": row_degrees, "column_degrees": column_degrees,
            "general_duality_count": len(dualities), "involutive_duality_count": len(polarities),
            "general_duality_witness": dualities[0] if dualities else None,
            "involutive_duality_witness": polarities[0] if polarities else None,
            "all_involutive_dualities": polarities,
            "circle_polarity_missing_tangents_at_points": missing,
            "exact_lines": [[str(value) for value in normalize(coefficients)] for coefficients in lines],
        }
    result.update(status="Diagnosed", reason="complete-fixed-incidence-enumeration")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    started = time.monotonic()

    def expired(_signal, _frame):
        raise TimeoutError("resource-limit")

    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 ** 3, 2 * 1024 ** 3))
    resource.setrlimit(resource.RLIMIT_CPU, (9, 10))
    signal.signal(signal.SIGXCPU, expired)
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, MAX_SECONDS)
    try:
        with args.candidate.open("rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("input-byte-limit")
        candidate = json.loads(raw, object_pairs_hook=checker._unique_keys)
        result = diagnose(candidate, started)
        result["source_sha256"] = hashlib.sha256(raw).hexdigest()
    except (OSError, ValueError, TimeoutError, MemoryError, RecursionError) as exc:
        result = {"schema": "adva.external.pascal-circle-duality.v0", "status": "Unknown",
                  "reason": str(exc), "partial_enumeration_is_not_nonexistence": True}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    result["wall_seconds"] = time.monotonic() - started
    result["cpu_seconds"] = resource.getrusage(resource.RUSAGE_SELF).ru_utime + resource.getrusage(resource.RUSAGE_SELF).ru_stime
    result["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "Diagnosed" else 3


if __name__ == "__main__":
    raise SystemExit(main())
