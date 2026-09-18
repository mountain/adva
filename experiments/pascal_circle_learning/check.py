"""Independent exact checker for one external rational Pascal-circle profile.

Authored by ChatGPT (OpenAI), through Mingli Yuan's account as proxy.
Original contribution under Unknown v0.3. No native Adva admission or Seal.
This module imports no producer, search code, numerical optimizer or SymPy.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import re

SCHEMA = "adva.external.pascal-circle-candidate.v0"
MAX_BYTES = 1048576
MAX_BITS = 4096
VERTICES = {"red": [1, 3, 5, 7, 9], "blue": [2, 4, 8, 12]}
TARGETS = {"red": [11, 13], "blue": [0, 6, 10]}


def rational(value):
    """Only canonical, bounded exact strings; bool/float coercion is forbidden."""
    if (type(value) is not str or len(value) > 2500
            or re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?", value) is None):
        raise ValueError("canonical rational string required")
    result = Fraction(value)
    if str(result) != value:
        raise ValueError("noncanonical rational string")
    if max(abs(result.numerator).bit_length(), result.denominator.bit_length()) > MAX_BITS:
        raise ValueError("rational coordinate bit limit")
    return result


def _point(value):
    if type(value) is not list or len(value) != 2:
        raise ValueError("two affine coordinates required")
    return tuple(rational(v) for v in value)


def _keys(obj, keys, name):
    if type(obj) is not dict or set(obj) != set(keys):
        raise ValueError(name + " fields differ from the fixed profile")


def _indices(value, count):
    if (type(value) is not list or len(value) != count
            or any(type(i) is not int or not 0 <= i < 14 for i in value)):
        raise ValueError("invalid vertex indices")
    return value


def _on_circle(point, center, radius_squared):
    return sum((p - c) ** 2 for p, c in zip(point, center)) == radius_squared


def _line(p, q, center=None):
    """Affine line coefficients; coincident endpoints require a true tangent."""
    if p == q:
        if center is None:
            raise ValueError("coincident endpoints without a circle tangent")
        a, b = p[0] - center[0], p[1] - center[1]
        line = (a, b, -(a * p[0] + b * p[1]))
    else:
        line = (p[1] - q[1], q[0] - p[0], p[0] * q[1] - q[0] * p[1])
    if line[0] == line[1] == 0:
        raise ValueError("zero or invalid line")
    return line


def _normalize(point):
    nonzero = next((v for v in point if v != 0), None)
    if nonzero is None:
        raise ValueError("zero projective point")
    return tuple(v / nonzero for v in point)


def _intersection(first, second):
    """Solve two affine linear equations, explicitly handling parallel lines."""
    a, b, c = first
    d, e, f = second
    denominator = a * e - d * b
    if denominator:
        return ((b * f - e * c) / denominator,
                (c * d - f * a) / denominator, Fraction(1))
    if a * f == d * c and b * f == e * c:
        raise ValueError("coincident opposite sides have no unique intersection")
    return _normalize((b, -a, Fraction(0)))


def _collinear(points):
    (a, b, c), (d, e, f), (g, h, i) = points
    return a * e * i + b * f * g + c * d * h - c * e * g - b * d * i - a * f * h == 0


def _orientation(p, q, r):
    return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])


def _between(p, q, r):
    return (min(p[0], q[0]) <= r[0] <= max(p[0], q[0])
            and min(p[1], q[1]) <= r[1] <= max(p[1], q[1]))


def _segments_meet(a, b, c, d):
    ab_c, ab_d = _orientation(a, b, c), _orientation(a, b, d)
    cd_a, cd_b = _orientation(c, d, a), _orientation(c, d, b)
    if ab_c * ab_d < 0 and cd_a * cd_b < 0:
        return True
    return ((ab_c == 0 and _between(a, b, c))
            or (ab_d == 0 and _between(a, b, d))
            or (cd_a == 0 and _between(c, d, a))
            or (cd_b == 0 and _between(c, d, b)))


def _simple_polygon(points):
    """Allow straight vertices, but no crossing, touching, overlap or reversal."""
    n = len(points)
    if len(set(points)) != n:
        return False
    for i in range(n):
        p, q, r = points[i - 1], points[i], points[(i + 1) % n]
        if _orientation(p, q, r) == 0:
            if sum((p[k] - q[k]) * (r[k] - q[k]) for k in range(2)) >= 0:
                return False
        for j in range(i + 1, n):
            if j == i + 1 or (i == 0 and j == n - 1):
                continue
            if _segments_meet(q, r, points[j], points[(j + 1) % n]):
                return False
    return sum(points[i][0] * points[(i + 1) % n][1]
               - points[(i + 1) % n][0] * points[i][1] for i in range(n)) != 0


def check_candidate(obj):
    """Return a fresh exact verdict; supplied success flags are not admitted."""
    checks, failures, intersections, diagnostics = {}, [], {}, []

    def record(name, condition):
        checks[name] = bool(condition)
        if not condition:
            failures.append(name)

    try:
        _keys(obj, ("schema", "points", "circles", "bindings"), "candidate")
        if obj["schema"] != SCHEMA:
            raise ValueError("unsupported candidate schema")
        if len(json.dumps(obj, allow_nan=False).encode()) > MAX_BYTES:
            raise ValueError("candidate byte limit")
        if type(obj["points"]) is not list or len(obj["points"]) != 14:
            raise ValueError("exactly fourteen ordered affine points required")
        points = [_point(p) for p in obj["points"]]
        _keys(obj["circles"], ("red", "blue"), "circles")
        _keys(obj["bindings"], ("red", "blue"), "bindings")
        circles = {}
        for name in VERTICES:
            circle, binding = obj["circles"][name], obj["bindings"][name]
            _keys(circle, ("center", "radius_squared", "vertices"), name + " circle")
            _keys(binding, ("sequence", "intersections"), name + " binding")
            vertices = _indices(circle["vertices"], len(VERTICES[name]))
            if vertices != VERTICES[name]:
                raise ValueError(name + " circle vertex membership changed")
            center, radius_squared = _point(circle["center"]), rational(circle["radius_squared"])
            sequence = _indices(binding["sequence"], 6)
            if set(sequence) != set(vertices):
                raise ValueError(name + " sequence is not the declared circle vertices")
            repeats = sum(sequence[i] == sequence[(i + 1) % 6] for i in range(6))
            counts = sorted(sequence.count(i) for i in vertices)
            expected_counts = [1, 1, 1, 1, 2] if name == "red" else [1, 1, 2, 2]
            if repeats != 6 - len(vertices) or counts != expected_counts:
                raise ValueError(name + " repetition pattern must represent adjacent tangencies")
            targets = binding["intersections"]
            if type(targets) is not list or len(targets) != 3:
                raise ValueError("three intersection bindings required")
            finite_targets = [i for i in targets if i is not None]
            if (any(type(i) is not int for i in finite_targets)
                    or sorted(finite_targets) != TARGETS[name]
                    or targets.count(None) != (1 if name == "red" else 0)):
                raise ValueError(name + " intersection identities changed")
            circles[name] = (center, radius_squared, sequence, targets)
        record("circle_center_incidence", sum(
            (circles["blue"][0][k] - circles["red"][0][k]) ** 2
            for k in range(2)) == circles["red"][1])
        record("schema_and_rational_coordinates", True)
        record("fourteen_distinct_points", len(set(points)) == 14)
        record("simple_polygon", _simple_polygon(points))
        for name, (center, radius_squared, sequence, targets) in circles.items():
            record(name + ".positive_radius_squared", radius_squared > 0)
            record(name + ".circle_membership", all(_on_circle(points[i], center, radius_squared)
                                                    for i in VERTICES[name]))
            record(name + ".exact_circle_cardinality", all(
                not _on_circle(points[i], center, radius_squared)
                for i in range(14) if i not in VERTICES[name]))
            record(name + ".targets_off_circle", all(not _on_circle(points[i], center, radius_squared)
                                                     for i in TARGETS[name]))
            try:
                lines = [_line(points[sequence[i]], points[sequence[(i + 1) % 6]], center)
                         for i in range(6)]
                if len({_normalize(line) for line in lines}) != 6:
                    raise ValueError("coincident polygon sides")
                crosspoints = [_intersection(lines[i], lines[i + 3]) for i in range(3)]
                record(name + ".nonzero_lines_and_intersections", True)
            except ValueError as exc:
                record(name + ".nonzero_lines_and_intersections", False)
                diagnostics.append(name + ": " + str(exc))
                continue
            record(name + ".distinct_intersections", len({_normalize(p) for p in crosspoints}) == 3)
            record(name + ".pascal_collinearity", _collinear(crosspoints))
            record(name + ".infinity_count", sum(p[2] == 0 for p in crosspoints)
                   == (1 if name == "red" else 0))
            for i, (point, target) in enumerate(zip(crosspoints, targets)):
                matches = point[2] == 0 if target is None else (
                    point[2] != 0 and point[:2] == points[target])
                record(name + ".binding." + str(i), matches)
            intersections[name] = [[str(v) for v in point] for point in crosspoints]
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError) as exc:
        record("schema_and_rational_coordinates", False)
        diagnostics.append(str(exc))
    return {"status": "Refuted" if failures else "Verified", "checks": checks,
            "failures": failures, "intersections": intersections, "diagnostics": diagnostics}


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def load_candidate(path):
    with Path(path).open("rb") as source:
        raw = source.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("candidate byte limit")
    return json.loads(raw, object_pairs_hook=_unique_keys)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    try:
        report = check_candidate(load_candidate(args.candidate))
    except (OSError, ValueError, RecursionError) as exc:
        report = {"status": "Refuted", "checks": {}, "failures": [str(exc)]}
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if report["status"] == "Verified" else 2


if __name__ == "__main__":
    raise SystemExit(main())
