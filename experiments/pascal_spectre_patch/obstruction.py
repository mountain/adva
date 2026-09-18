"""Independent exact local-angle obstruction to monohedral plane tiling.

Authored by ChatGPT (OpenAI), through Mingli Yuan's account as proxy.
Project-original contribution under Unknown v0.3; no native Adva Seal.

If a reflex corner leaves a wedge narrower than every corner of the tile,
no congruent neighbor can fill it. Smooth edge points contribute angle pi.
The conclusion allows reflections and non-edge-to-edge contacts. It also
applies to simple regular curved boundaries preserving these endpoint
tangent angles. A negative result does not establish tileability.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

MAX_VERTICES = 64
MAX_BYTES = 1048576
MAX_BITS = 4096
DEFAULT_CANDIDATE = (Path(__file__).resolve().parents[1]
                     / "pascal_circle_learning/evidence/candidate.json")
DEFAULT_SHA256 = "5d805463d69e0d5e2b248f09077e8a8bbaa09021938961c819383dae0960190c"


def _cross(a, b, c):
    return ((b[0] - a[0]) * (c[1] - a[1])
            - (b[1] - a[1]) * (c[0] - a[0]))


def _on_segment(a, b, c):
    return (min(a[0], b[0]) <= c[0] <= max(a[0], b[0])
            and min(a[1], b[1]) <= c[1] <= max(a[1], b[1]))


def _segments_meet(a, b, c, d):
    ab_c, ab_d = _cross(a, b, c), _cross(a, b, d)
    cd_a, cd_b = _cross(c, d, a), _cross(c, d, b)
    if ab_c * ab_d < 0 and cd_a * cd_b < 0:
        return True
    return ((ab_c == 0 and _on_segment(a, b, c))
            or (ab_d == 0 and _on_segment(a, b, d))
            or (cd_a == 0 and _on_segment(c, d, a))
            or (cd_b == 0 and _on_segment(c, d, b)))


def _validate(points):
    if not isinstance(points, (list, tuple)) or not 3 <= len(points) <= MAX_VERTICES:
        raise ValueError("polygon must have 3 through 64 ordered vertices")
    result = []
    for p in points:
        if not isinstance(p, (list, tuple)) or len(p) != 2:
            raise ValueError("each vertex must have two coordinates")
        if any(type(x) not in (int, Fraction) for x in p):
            raise ValueError("exact integer or Fraction coordinates required")
        p = tuple(Fraction(x) for x in p)
        if any(max(abs(x.numerator).bit_length(), x.denominator.bit_length())
               > MAX_BITS for x in p):
            raise ValueError("coordinate bit limit exceeded")
        result.append(p)
    n = len(result)
    if len(set(result)) != n:
        raise ValueError("polygon vertices must be distinct")
    for i, b in enumerate(result):
        c = result[(i + 1) % n]
        if _cross(result[i - 1], b, c) == 0:
            raise ValueError("collinear consecutive edges are not admitted")
        for j in range(i + 1, n):
            if j == i + 1 or (i == 0 and j == n - 1):
                continue
            if _segments_meet(b, c, result[j], result[(j + 1) % n]):
                raise ValueError("polygon must be simple, without self-touching")
    area2 = sum(result[i][0] * result[(i + 1) % n][1]
                - result[(i + 1) % n][0] * result[i][1] for i in range(n))
    if not area2:
        raise ValueError("polygon has zero signed area")
    return result, area2


def check_polygon(points):
    """Return an exact sufficient obstruction; False is not a tiling proof.

    Both orientations are accepted and normalized in the angle calculation;
    indices always refer to the supplied order. For a corner let c be the
    orientation-normalized incoming/outgoing cross product and d their dot
    product. A convex angle has direction vector (-d,c) in the upper half
    plane. The complement of a reflex angle has direction (-d,-c). Their
    determinant compares these angles exactly, without arctan or tolerance.
    """
    points, area2 = _validate(points)
    n, orientation = len(points), (1 if area2 > 0 else -1)
    turns, angles = [], []
    lengths = []
    for i, p in enumerate(points):
        v = tuple(p[k] - points[i - 1][k] for k in range(2))
        w = tuple(points[(i + 1) % n][k] - p[k] for k in range(2))
        c = orientation * (v[0] * w[1] - v[1] * w[0])
        d = v[0] * w[0] + v[1] * w[1]
        turns.append((c, d))
        scale = max(abs(c), abs(d))
        # Display only. The normalized arguments cannot overflow float.
        angles.append(180 - math.degrees(math.atan2(float(c / scale), float(d / scale))))
        lengths.append(w[0] ** 2 + w[1] ** 2)
    classes = []
    for i, length in enumerate(lengths):
        if all(length != lengths[group[0]] for group in classes):
            classes.append([j for j in range(n) if lengths[j] == length])

    # Choose the largest reflex angle by exactly comparing complements.
    corner = None
    for i, (c, d) in enumerate(turns):
        if c >= 0:
            continue
        if corner is None:
            corner = i
        else:
            cc, dc = turns[corner]
            if dc * c - cc * d < 0:
                corner = i
    comparisons = []
    obstructed = False
    certificate = None
    if corner is not None:
        cc, dc = turns[corner]
        for i, (c, d) in enumerate(turns):
            determinant = None if c < 0 else -dc * c - cc * d
            greater = c < 0 or determinant > 0
            comparisons.append({
                "vertex": i,
                "case": "reflex_exceeds_pi" if c < 0 else "convex_angle_comparison",
                "normalized_cross": str(c), "dot": str(d),
                "comparison_determinant": None if determinant is None else str(determinant),
                "strictly_greater_than_complement": greater,
            })
        obstructed = all(item["strictly_greater_than_complement"] for item in comparisons)
        certificate = {
            "corner": corner,
            "complement_direction": [str(-dc), str(-cc)],
            "complement_is_between_zero_and_pi": cc < 0,
            "corner_degrees_approx": angles[corner],
            "complement_degrees_approx": 360 - angles[corner],
            "comparisons": comparisons,
        }
    return {
        "schema": "adva.external.pascal-spectre-obstruction.v0",
        "status": "Obstructed" if obstructed else "NoObstructionFound",
        "obstructed": obstructed,
        "vertex_count": n,
        "input_orientation": "counterclockwise" if area2 > 0 else "clockwise",
        "signed_area": str(area2 / 2),
        "squared_edge_lengths": [str(length) for length in lengths],
        "edge_length_classes": classes,
        "all_edge_lengths_distinct": len(classes) == n,
        "interior_angles_degrees_approx": angles,
        "certificate": certificate,
        "scope": ("Sufficient obstruction to plane tiling by congruent copies, including "
                  "reflections and non-edge-to-edge contacts. Curved boundaries must be "
                  "simple and regular and preserve these corner tangent angles. "
                  "NoObstructionFound does not establish tileability."),
    }


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def load_points(path):
    """Read bounded JSON with canonical rational strings in a points array."""
    with Path(path).open("rb") as source:
        raw = source.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("input byte limit exceeded")
    obj = json.loads(raw, object_pairs_hook=_unique_keys)
    if not isinstance(obj, dict) or not isinstance(obj.get("points"), list):
        raise ValueError("JSON object with a points array required")
    if not 3 <= len(obj["points"]) <= MAX_VERTICES:
        raise ValueError("vertex count exceeds profile")
    points = []
    for p in obj["points"]:
        if not isinstance(p, list) or len(p) != 2:
            raise ValueError("two coordinates required")
        row = []
        for value in p:
            if type(value) is not str or len(value) > 2500:
                raise ValueError("canonical rational string required")
            try:
                number = Fraction(value)
            except (ValueError, ZeroDivisionError) as exc:
                raise ValueError("valid canonical rational string required") from exc
            if str(number) != value:
                raise ValueError("noncanonical rational string")
            row.append(number)
        points.append(tuple(row))
    return points, hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", nargs="?", type=Path,
                        help="JSON points; omitted means the SHA-256-pinned Pascal candidate")
    args = parser.parse_args()
    try:
        points, digest = load_points(args.candidate or DEFAULT_CANDIDATE)
        if args.candidate is None and digest != DEFAULT_SHA256:
            raise ValueError("default candidate SHA-256 changed")
        report = check_polygon(points)
        report["candidate_sha256"] = digest
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError, RecursionError, OverflowError) as exc:
        print(json.dumps({"status": "Invalid", "obstructed": None, "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
