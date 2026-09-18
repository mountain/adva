"""Original constructive proposal family; external arithmetic, not native Adva.

Authored by ChatGPT (OpenAI), through Mingli Yuan's account proxy.
The Pascal arithmetic operations are reused from Adva's existing calibration.
The independent acceptance implementation is check.py, not this module.
"""
from __future__ import annotations

from fractions import Fraction

from experiments.knowledge_geometry.acceleration_direction import cross, det3

SCHEMA = "adva.external.pascal-circle-candidate.v0"
RED = (1, 3, 5, 7, 9)
BLUE = (2, 4, 8, 12)
RED_GROUP = (1, 3, 5, 7, 9, 11, 13)
BLUE_GROUP = (2, 4, 8, 12, 0, 6, 10)


def circle_point(t):
    denominator = 1 + t * t
    return ((1 - t * t) / denominator, 2 * t / denominator)


def line(p, q):
    return cross((*p, 1), (*q, 1))


def tangent(p):
    # Unit-circle tangent p.x*x+p.y*y=1.
    return (p[0], p[1], -1)


def affine_intersection(first, second):
    point = cross(first, second)
    if point[2] == 0:
        raise ValueError("required-finite-intersection-is-infinite-or-undefined")
    return (point[0] / point[2], point[1] / point[2])


def unit_groups(red_parameters, blue_parameters):
    """Two seven-point constructive charts; red middle intersection is infinity."""
    ta, tb, tc, td = red_parameters
    aa, bb = 1 - ta * tb, ta + tb
    denominator = aa + bb * td
    if denominator == 0:
        raise ValueError("red-chart-pole")
    te = (bb - aa * td) / denominator
    a, b, c, d, e = [circle_point(t) for t in (ta, tb, tc, td, te)]
    red = [a, b, c, d, e,
           affine_intersection(tangent(a), line(c, d)),
           affine_intersection(line(b, c), line(e, a))]
    a, b, c, d = [circle_point(t) for t in blue_parameters]
    blue = [a, b, c, d,
            affine_intersection(tangent(a), tangent(c)),
            affine_intersection(line(a, b), line(c, d)),
            affine_intersection(line(b, c), line(d, a))]
    return red, blue


def similarity(point, parameters):
    a, b, cx, cy = parameters
    x, y = point
    return (a * x - b * y + cx, b * x + a * y + cy)


def effective_transforms(parameters):
    """v1 couples centers exactly; legacy transforms are only for old witnesses."""
    red = parameters["red_similarity"]
    if "center_t" in parameters:
        if "blue_similarity" in parameters or len(parameters["center_t"]) != 1:
            raise ValueError("center-constrained family requires one direction and blue_linear only")
        k = circle_point(parameters["center_t"][0])
        cx, cy = similarity(k, red)
        a, b = parameters["blue_linear"]
        return red, [a, b, cx, cy]
    return red, parameters["blue_similarity"]


def construct(parameters):
    red, blue = unit_groups(parameters["red_t"], parameters["blue_t"])
    points = [None] * 14
    red_transform, blue_transform = effective_transforms(parameters)
    for indices, group, transform in (
        (RED_GROUP, red, red_transform),
        (BLUE_GROUP, blue, blue_transform),
    ):
        for index, point in zip(indices, group, strict=True):
            points[index] = similarity(point, transform)
    return points


def candidate(parameters):
    """Reconstruct AFTER rationalizing parameters, never round output coordinates."""
    parameters = {key: [Fraction(v) for v in values]
                  for key, values in parameters.items()}
    points = construct(parameters)
    circles = {}
    red_transform, blue_transform = effective_transforms(parameters)
    for name, indices, transform in (("red", RED, red_transform), ("blue", BLUE, blue_transform)):
        a, b, cx, cy = transform
        circles[name] = {"center": [str(cx), str(cy)],
                         "radius_squared": str(a * a + b * b),
                         "vertices": list(indices)}
    return {
        "schema": SCHEMA,
        "points": [[str(value) for value in point] for point in points],
        "circles": circles,
        "bindings": {
            "red": {"sequence": [1, 1, 3, 5, 7, 9],
                    "intersections": [11, None, 13]},
            "blue": {"sequence": [2, 2, 4, 8, 8, 12],
                     "intersections": [0, 6, 10]},
        },
    }


def proposal_collinearity(points):
    """Secondary producer diagnostic; never substitutes for independent checking."""
    return det3([(*points[index], 1) for index in (0, 6, 10)])
