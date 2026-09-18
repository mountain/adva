#!/usr/bin/env python3
"""Bounded exact local curved-patch experiment, not a plane-tiling solver.

Original work by ChatGPT (OpenAI), through Mingli Yuan's account proxy,
contributed under Unknown v0.3. Exact polygon primitives were independently
developed by the concurrent geometry audit in this project. No paper source,
figure, or third-party implementation is incorporated.
"""

from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import signal
import time

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_CANDIDATE_SHA256 = "5d805463d69e0d5e2b248f09077e8a8bbaa09021938961c819383dae0960190c"
ORDER = (10, 13, 8, 9)
AMPLITUDES = tuple(F(1, d) for d in (10, 1000, 100000, 10000000, 1000000000))
LIMITS = {"copies": 4, "transform_proposals": 196,
          "exact_geometry_checks": 50000, "wall_seconds": 120,
          "cpu_seconds": 120, "memory_bytes": 2 * 1024 ** 3,
          "input_bytes": 1024 ** 2, "output_bytes": 8 * 1024 ** 2,
          "automatic_continuations": 0}


class Budget:
    def __init__(self):
        self.start = time.monotonic()
        self.cpu_start = time.process_time()
        self.checks = 0
        self.proposals = 0

    def check(self):
        self.checks += 1
        if self.checks > LIMITS["exact_geometry_checks"]:
            raise TimeoutError("exact geometry check limit")
        if time.monotonic() - self.start > LIMITS["wall_seconds"] - 2:
            raise TimeoutError("wall time limit; checkpoint reserve")

    def propose(self):
        self.proposals += 1
        if self.proposals > LIMITS["transform_proposals"]:
            raise TimeoutError("transform proposal limit")
        self.check()

    def ledger(self):
        return {"exact_geometry_checks": self.checks,
                "transform_proposals": self.proposals,
                "wall_seconds": time.monotonic() - self.start,
                "cpu_seconds": time.process_time() - self.cpu_start,
                "maximum_resident_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                "automatic_continuations": 0}


def point_json(point):
    return [str(x) for x in point]


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def area2(poly):
    return sum((poly[i][0] * poly[(i + 1) % len(poly)][1]
                - poly[(i + 1) % len(poly)][0] * poly[i][1]
                for i in range(len(poly))), F(0))


def triangulate(poly):
    ids = list(range(len(poly)))
    if area2(poly) < 0:
        ids.reverse()
    triangles = []
    while len(ids) > 3:
        for k, b in enumerate(ids):
            a, c = ids[k - 1], ids[(k + 1) % len(ids)]
            tri = (poly[a], poly[b], poly[c])
            if cross(*tri) <= 0:
                continue
            if any(all(cross(tri[z], tri[(z + 1) % 3], poly[j]) >= 0
                       for z in range(3)) for j in ids if j not in (a, b, c)):
                continue
            triangles.append((a, b, c))
            ids.pop(k)
            break
        else:
            raise ValueError("exact triangulation failed")
    triangles.append(tuple(ids))
    assert sum(area2([poly[j] for j in t]) for t in triangles) == abs(area2(poly))
    return triangles


def convex_clip(subject, clipper):
    """Closed convex intersection, retaining even point/segment contacts."""
    poly = list(subject)
    for i, a in enumerate(clipper):
        b = clipper[(i + 1) % len(clipper)]
        if not poly:
            break
        result = []
        for k, q in enumerate(poly):
            r = poly[k - 1]
            cq, cr = cross(a, b, q), cross(a, b, r)
            if (cq >= 0) != (cr >= 0):
                alpha = cr / (cr - cq)
                result.append(tuple(r[j] + alpha * (q[j] - r[j]) for j in range(2)))
            if cq >= 0:
                result.append(q)
        poly = list(dict.fromkeys(result))
    return poly


def hull(points):
    ordered = sorted(set(points))
    halves = []
    for seq in (ordered, list(reversed(ordered))):
        side = []
        for p in seq:
            while len(side) >= 2 and cross(side[-2], side[-1], p) <= 0:
                side.pop()
            side.append(p)
        halves.append(side)
    return halves[0][:-1] + halves[1][:-1]


def box(poly):
    return tuple((min(p[k] for p in poly), max(p[k] for p in poly)) for k in (0, 1))


def boxes_disjoint(a, b):
    return any(a[k][1] < b[k][0] or b[k][1] < a[k][0] for k in (0, 1))


def apply(transform, point):
    sign, dx, dy = transform
    return (sign * point[0] + dx, sign * point[1] + dy)


def attach(transform, edge, points):
    sign, dx, dy = transform
    a, b = points[edge], points[(edge + 1) % len(points)]
    return (-sign, sign * (a[0] + b[0]) + dx,
            sign * (a[1] + b[1]) + dy)


def interior_overlap(poly, other, triangles, budget):
    for i, ids in enumerate(triangles):
        tri = [poly[j] for j in ids]
        bb = box(tri)
        for j, jds in enumerate(triangles):
            budget.check()
            another = [other[k] for k in jds]
            if boxes_disjoint(bb, box(another)):
                continue
            intersection = convex_clip(tri, another)
            twice_area = abs(area2(intersection))
            if twice_area:
                return {"triangles": [i, j], "area": str(twice_area / 2),
                        "intersection": [point_json(q) for q in intersection]}
    return None


def controls(a, b, epsilon):
    d = (b[0] - a[0], b[1] - a[1])
    normal = (-d[1], d[0])
    return [tuple(a[k] + F(i, 5) * d[k]
                  + ({2: -1, 3: 1}.get(i, 0)) * epsilon * normal[k] / 10
                  for k in (0, 1)) for i in range(6)]


def curve(a, b, epsilon, t):
    d = (b[0] - a[0], b[1] - a[1])
    normal = (-d[1], d[0])
    f = epsilon * t ** 2 * (1 - t) ** 2 * (2 * t - 1)
    return tuple(a[k] + t * d[k] + f * normal[k] for k in (0, 1))


def unique_edges(polygons):
    edges = {}
    for tile, poly in enumerate(polygons):
        for i, a in enumerate(poly):
            b = poly[(i + 1) % len(poly)]
            key = tuple(sorted((a, b)))
            if key not in edges:
                edges[key] = {"a": a, "b": b, "incidences": []}
            edges[key]["incidences"].append([tile, i])
    return list(edges.values())


def certify_hulls(edges, epsilon, budget):
    hulls = [hull(controls(e["a"], e["b"], epsilon)) for e in edges]
    boxes = [box(poly) for poly in hulls]
    checked = 0
    for i, h in enumerate(hulls):
        for j in range(i):
            budget.check()
            checked += 1
            if boxes_disjoint(boxes[i], boxes[j]):
                continue
            allowed = {edges[i]["a"], edges[i]["b"]} & {edges[j]["a"], edges[j]["b"]}
            intersection = convex_clip(h, hulls[j])
            if any(point not in allowed for point in intersection):
                return {"status": "RefutedSufficientCondition", "epsilon": str(epsilon),
                        "hull_pairs_checked": checked, "edge_pair": [j, i],
                        "incidences": [edges[j]["incidences"], edges[i]["incidences"]],
                        "intersection": [point_json(p) for p in intersection]}
    return {"status": "Verified", "epsilon": str(epsilon),
            "hull_pairs_checked": checked}


def stereo(p):
    x, y = p
    q = x * x + y * y
    return (2 * x / (q + 1), 2 * y / (q + 1), (q - 1) / (q + 1))


def sphere_check(p, budget):
    budget.check()
    q = stereo(p)
    assert sum(c * c for c in q) == 1
    assert (q[0] / (1 - q[2]), q[1] / (1 - q[2])) == p
    return q


def sphere_evidence(polygons, epsilon, budget):
    records = []
    for tile, poly in enumerate(polygons):
        vertices = [sphere_check(p, budget) for p in poly]
        samples = []
        for edge, a in enumerate(poly):
            b = poly[(edge + 1) % len(poly)]
            samples.append([point_json(sphere_check(curve(a, b, epsilon, t), budget))
                            for t in (F(0), F(1, 4), F(1, 2), F(3, 4), F(1))])
        records.append({"tile": tile, "vertices": [point_json(p) for p in vertices],
                        "edge_sample_parameters": ["0", "1/4", "1/2", "3/4", "1"],
                        "edge_samples": samples})
    chord_squares = []
    for poly in polygons:
        a, b = stereo(poly[0]), stereo(poly[1])
        chord_squares.append(sum((a[k] - b[k]) ** 2 for k in range(3)))
    all_chords = []
    for poly in polygons:
        xyz = [stereo(p) for p in poly]
        all_chords.append(sorted(sum((xyz[i][k] - xyz[(i + 1) % len(poly)][k]) ** 2
                                     for k in range(3)) for i in range(len(poly))))
    return {"status": "Verified", "tile_samples": records,
            "edge_0_chord_squared_by_tile": [str(c) for c in chord_squares],
            "edge_0_chord_squared_equal": len(set(chord_squares)) == 1,
            "sorted_all_edge_chord_squares_by_tile": [[str(c) for c in row] for row in all_chords],
            "spherical_tile_edge_length_multisets_equal": all(row == all_chords[0] for row in all_chords),
            "scope": "Rational points on the unit sphere with exact inverse. The changed chord-length multiset certifies that spherical copies are not mutually congruent, even allowing vertex relabelling."}


def run(candidate_path, report, budget):
    if candidate_path.stat().st_size > LIMITS["input_bytes"]:
        raise ValueError("input byte limit")
    with candidate_path.open("rb") as source:
        raw = source.read(LIMITS["input_bytes"] + 1)
    if len(raw) > LIMITS["input_bytes"]:
        raise ValueError("input byte limit")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_CANDIDATE_SHA256:
        raise ValueError("this finite experiment pins one exact rational candidate")
    spec = importlib.util.spec_from_file_location("pascal_external_check", ROOT / "experiments/pascal_circle_learning/check.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    # Parse the digest-pinned bytes already read: a concurrent file change must
    # not make the checked geometry differ from the input recorded above.
    candidate = json.loads(raw)
    checked = checker.check_candidate(candidate)
    budget.check()
    if checked["status"] != "Verified":
        raise ValueError("input Pascal candidate Refuted")
    report["input"] = {"sha256": digest, "verification": checked["status"],
                       "check_count": len(checked["checks"])}
    points = [tuple(F(x) for x in p) for p in candidate["points"]]
    triangles = triangulate(points)
    report["triangulation"] = [list(t) for t in triangles]
    transforms = [(1, F(0), F(0))]
    polygons = [points]
    trials = report.setdefault("attachment_trials", [])
    for base in range(LIMITS["copies"]):
        if base >= len(transforms) or len(transforms) == LIMITS["copies"]:
            break
        for edge in ORDER:
            if len(transforms) == LIMITS["copies"]:
                break
            budget.propose()
            proposal = attach(transforms[base], edge, points)
            trial = {"parent": base, "edge": edge, "transform": point_json(proposal)}
            trials.append(trial)
            if proposal in transforms:
                trial["status"] = "Duplicate"
                continue
            poly = [apply(proposal, p) for p in points]
            for index, retained in enumerate(polygons):
                overlap = interior_overlap(retained, poly, triangles, budget)
                if overlap:
                    trial.update({"status": "Refuted", "overlaps_tile": index, "witness": overlap})
                    break
            else:
                trial.update({"status": "Verified", "tile": len(transforms)})
                transforms.append(proposal)
                polygons.append(poly)
    report["planar_patch"] = {"status": "Verified", "tile_count": len(polygons),
                              "transforms": [point_json(t) for t in transforms],
                              "vertices": [[point_json(p) for p in poly] for poly in polygons],
                              "all_pair_interiors_disjoint": True}
    edges = unique_edges(polygons)
    report["planar_patch"]["unique_edge_count"] = len(edges)
    report["planar_patch"]["shared_seams"] = [e["incidences"] for e in edges if len(e["incidences"]) > 1]
    curvature = report.setdefault("curvature_trials", [])
    for epsilon in AMPLITUDES:
        result = certify_hulls(edges, epsilon, budget)
        curvature.append(result)
        if result["status"] == "Verified":
            report["curved_patch"] = {"status": "Verified", "epsilon": str(epsilon),
                                      "curve": "A+t*d+epsilon*t^2*(1-t)^2*(2*t-1)*J*d",
                                      "proof": "Each simple curve is monotone along its chord and contained in its Bernstein control hull. Distinct hulls meet only at shared endpoints after seam deduplication. Shrinking epsilon to zero gives an embedded graph isotopy to the independently checked disjoint straight patch. Shared seams agree identically by central symmetry."}
            report["sphere"] = sphere_evidence(polygons, epsilon, budget)
            report["status"] = "VerifiedLocalPatch"
            break
    else:
        report["curved_patch"] = {"status": "Unknown", "reason": "finite amplitude schedule did not certify control-hull separation"}
        report["status"] = "UnknownCurvature"
    report["residual"] = "A finite patch does not establish an infinite tiling, a monotile, aperiodicity, a cut-and-project construction, or unchanged spherical congruence. Endpoint tangent angles remain fixed."


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=ROOT / "experiments/pascal_circle_learning/evidence/candidate.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    budget = Budget()
    report = {"schema": "adva.external.pascal-spectre-patch.v0", "limits": LIMITS,
              "arithmetic": "Exact Fraction for every acceptance decision"}
    resource.setrlimit(resource.RLIMIT_CPU, (LIMITS["cpu_seconds"] - 1, LIMITS["cpu_seconds"]))
    resource.setrlimit(resource.RLIMIT_AS, (LIMITS["memory_bytes"], LIMITS["memory_bytes"]))
    resource.setrlimit(resource.RLIMIT_FSIZE, (LIMITS["output_bytes"], LIMITS["output_bytes"]))
    def timed_out(signum, frame):
        raise TimeoutError("supervised wall-clock limit")
    signal.signal(signal.SIGALRM, timed_out)
    signal.alarm(LIMITS["wall_seconds"] - 1)
    try:
        run(args.candidate, report, budget)
    except (TimeoutError, MemoryError) as error:
        report.update({"status": "Unknown", "stop_reason": str(error)})
    except (ValueError, ArithmeticError, AssertionError) as error:
        report.update({"status": "Invalidated", "stop_reason": str(error)})
    except OSError as error:
        report.update({"status": "Unavailable", "stop_reason": str(error)})
    finally:
        signal.alarm(0)
    report["resource_ledger"] = budget.ledger()
    encoded = json.dumps(report, indent=2) + "\n"
    if len(encoded.encode()) > LIMITS["output_bytes"]:
        raise ValueError("output byte limit; result not retained")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded)
    print(json.dumps({"status": report["status"], "tile_count": report.get("planar_patch", {}).get("tile_count"),
                      "curved_patch": report.get("curved_patch"), "resource_ledger": report["resource_ledger"]}, indent=2))
    return 0 if report["status"] == "VerifiedLocalPatch" else 1


if __name__ == "__main__":
    raise SystemExit(main())
