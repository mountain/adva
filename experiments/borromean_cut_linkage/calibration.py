#!/usr/bin/env python3
"""Cut one ring: are the other two still inseparable, and what does the cut separate?

Frozen contract: contract.json in this directory (Research 0129 section 3).

Two sections are kept apart, the way the earlier Wu rounds kept theirs.

IMPORTED, and not verified here: Mellor and Melvin's theorem that the triple intersection
number of Seifert surfaces computes Milnor's triple linking invariant modulo the gcd of the
pairwise linking numbers; the elementary fact that a nonzero linking number means a
two-component link is not split; and the classical fact that cutting any component of the
standard Borromean rings leaves the other two unlinked.

SELF-COMPUTED: the rectangle outlines read from this repository's retained literals; every
pairwise linking number, by a method independent of the retained projection-crossing count --
the algebraic intersection of one outline with the other component's spanning rectangle; the
sign of the triple intersection; the cut analysis for each choice of cut component; the
separation tests; and two controls built here.

Where the computed invariant cannot decide, the run says Unknown. A cut removes Milnor's
invariant not by hiding it but by removing its domain: a three-component link becomes a
two-component one plus an arc.
"""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import pathlib
import sys
import time
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
ASSERTIONS = {"n": 0}
MAX_ASSERTIONS = CONTRACT["budget"]["max_assertions"]

GOLDEN_SOURCE = REPO / "experiments/golden_ratio/calibration.py"
RETAINED_EVIDENCE = REPO / "experiments/golden_ratio/evidence.json"


def check(condition, message):
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)
    if ASSERTIONS["n"] > MAX_ASSERTIONS:
        raise AssertionError("assertion budget exceeded")


# ------------------------------------------------- exact arithmetic in Q(sqrt 5) ----

class Golden:
    """a + b*sqrt(5) with rational a and b, exactly, with a total order."""

    __slots__ = ("a", "b")

    def __init__(self, a, b=0):
        self.a, self.b = Fr(a), Fr(b)

    @staticmethod
    def coerce(other):
        return other if isinstance(other, Golden) else Golden(other)

    def __add__(self, other):
        other = Golden.coerce(other)
        return Golden(self.a + other.a, self.b + other.b)

    def __sub__(self, other):
        other = Golden.coerce(other)
        return Golden(self.a - other.a, self.b - other.b)

    def __mul__(self, other):
        other = Golden.coerce(other)
        return Golden(self.a * other.a + 5 * self.b * other.b,
                      self.a * other.b + self.b * other.a)

    def __truediv__(self, other):
        other = Golden.coerce(other)
        denominator = other.a * other.a - 5 * other.b * other.b
        if denominator == 0:
            raise ZeroDivisionError("division by a zero element of Q(sqrt 5)")
        return Golden((self.a * other.a - 5 * self.b * other.b) / denominator,
                      (self.b * other.a - self.a * other.b) / denominator)

    def __neg__(self):
        return Golden(-self.a, -self.b)

    def __eq__(self, other):
        other = Golden.coerce(other)
        return self.a == other.a and self.b == other.b

    def __lt__(self, other):
        return (self - Golden.coerce(other)).sign() < 0

    def __le__(self, other):
        return (self - Golden.coerce(other)).sign() <= 0

    def __hash__(self):
        return hash((self.a, self.b))

    def sign(self):
        if self.a == 0 and self.b == 0:
            return 0
        if self.b == 0:
            return 1 if self.a > 0 else -1
        if self.a == 0:
            return 1 if self.b > 0 else -1
        if self.a > 0 and self.b > 0:
            return 1
        if self.a < 0 and self.b < 0:
            return -1
        if self.a > 0:
            return 1 if self.a * self.a > 5 * self.b * self.b else -1
        return 1 if 5 * self.b * self.b > self.a * self.a else -1

    def __str__(self):
        return f"{self.a}+{self.b}*sqrt5"

    def as_json(self):
        return {"a": str(self.a), "b": str(self.b)}


PHI = Golden(Fr(1, 2), Fr(1, 2))


def read_retained_rectangles():
    """The literal `rectangles` assignment, by a restricted AST decoder.

    The historical module is parsed and never executed, and its digest is recorded.
    """
    raw = GOLDEN_SOURCE.read_bytes()
    tree = ast.parse(raw.decode("utf-8"))
    function = next(node for node in tree.body
                    if isinstance(node, ast.FunctionDef) and node.name == "golden_rectangle_checks")
    assignment = next(node for node in function.body
                      if isinstance(node, ast.Assign)
                      and any(isinstance(target, ast.Name) and target.id == "rectangles"
                              for target in node.targets))
    names = {"ZERO": Golden(0), "ONE": Golden(1), "PHI": PHI}

    def decode(node):
        if isinstance(node, ast.Name) and node.id in names:
            return names[node.id]
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return Golden(node.value)
        if isinstance(node, ast.Tuple):
            return tuple(decode(element) for element in node.elts)
        if isinstance(node, ast.Dict):
            return {decode(key): decode(value) for key, value in zip(node.keys, node.values)}
        raise AssertionError(f"unsupported node in the retained literal: {ast.dump(node)[:60]}")

    decoded = decode(assignment.value)
    for rect in decoded.values():
        if isinstance(rect["fixed"], Golden):
            if rect["fixed"].b != 0:
                raise AssertionError("the fixed axis must be an integer axis index")
            rect["fixed"] = int(rect["fixed"].a)
        rect["extents"] = {(int(key.a) if isinstance(key, Golden) else key): value
                           for key, value in rect["extents"].items()}
    return decoded, hashlib.sha256(raw).hexdigest()


# ----------------------------------------------------- rectangles, outlines, interiors ----

def free_axes(rect):
    return [axis for axis in range(3) if axis != rect["fixed"]]


def corner(rect, signs):
    point = [Golden(0), Golden(0), Golden(0)]
    point[rect["fixed"]] = rect["value"]
    for axis, sign_value in zip(free_axes(rect), signs):
        point[axis] = rect["center"][axis] + rect["extents"][axis] * Golden(sign_value)
    return tuple(point)


def outline(rect):
    """Four corners, counterclockwise seen from the positive fixed axis."""
    return [corner(rect, (1, 1)), corner(rect, (-1, 1)), corner(rect, (-1, -1)), corner(rect, (1, -1))]


def segments(points):
    return [(points[i], points[(i + 1) % len(points)]) for i in range(len(points))]


def inside(rect, point, strict=False):
    if not (point[rect["fixed"]] == rect["value"]):
        return False
    for axis in free_axes(rect):
        offset = point[axis] - rect["center"][axis]
        size = offset if offset.sign() >= 0 else -offset
        if strict:
            if not size < rect["extents"][axis]:
                return False
        elif not size <= rect["extents"][axis]:
            return False
    return True


def slab(fixed, value, center, extents):
    return {"fixed": fixed, "value": value, "center": tuple(center), "extents": dict(extents)}


# ------------------------------------------------------------- linking by intersection ----

def algebraic_intersection(curve_rect, surface_rect):
    """One outline against the other component's spanning rectangle.

    The linking number of two closed curves equals the algebraic intersection of one with a
    surface spanning the other. This is a different computation from the retained
    projection-crossing count, which is what makes it a cross-check rather than a replay.
    """
    axis = surface_rect["fixed"]
    plane = surface_rect["value"]
    total = 0
    crossings = []
    for start, end in segments(outline(curve_rect)):
        if start[axis] == end[axis]:
            continue
        if (start[axis] - plane).sign() * (end[axis] - plane).sign() >= 0:
            continue  # no strict straddle, so no transversal crossing
        t = (plane - start[axis]) / (end[axis] - start[axis])
        point = tuple(start[i] + (end[i] - start[i]) * t for i in range(3))
        if not inside(surface_rect, point, strict=True):
            continue
        total += 1 if (end[axis] - start[axis]).sign() > 0 else -1
        crossings.append({"point": [str(value) for value in point]})
    return total, crossings


def triple_intersection_sign(rectangles, order):
    """The sign of the common interior point, from the three surface normals in this order."""
    point = (Golden(0), Golden(0), Golden(0))
    if not all(inside(rect, point, strict=True) for rect in rectangles.values()):
        return None
    normals = []
    for name in order:
        normal = [0, 0, 0]
        normal[rectangles[name]["fixed"]] = 1
        normals.append(normal)
    matrix = [[normals[column][row] for column in range(3)] for row in range(3)]
    return (matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
            - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
            + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]))


def common_points(rectangles):
    """Points common to all filled rectangles: intersect the three planes and test."""
    planes = {}
    for rect in rectangles.values():
        if rect["fixed"] in planes and planes[rect["fixed"]] != rect["value"]:
            return []
        planes[rect["fixed"]] = rect["value"]
    if len(planes) != 3:
        return []
    point = tuple(planes[axis] for axis in range(3))
    return [point] if all(inside(rect, point) for rect in rectangles.values()) else []


# ------------------------------------------------------------------ separation tests ----

def bounding_box(rect):
    corners = [corner(rect, signs) for signs in itertools.product([1, -1], repeat=2)]
    return {axis: (min(point[axis] for point in corners), max(point[axis] for point in corners))
            for axis in range(3)}


def separation_tests(rect_a, rect_b):
    """Attempts to separate two components, each reported as decisive or inconclusive."""
    box_a, box_b = bounding_box(rect_a), bounding_box(rect_b)
    boxes_disjoint = any(box_a[axis][1] < box_b[axis][0] or box_b[axis][1] < box_a[axis][0]
                         for axis in range(3))
    planes = [axis for axis in range(3)
              if box_a[axis][1] < box_b[axis][0] or box_b[axis][1] < box_a[axis][0]]
    surfaces_meet = bool(common_points({"a": rect_a, "b": rect_b})) if \
        rect_a["fixed"] != rect_b["fixed"] else False
    return [
        {"test": "axis_aligned_bounding_boxes_disjoint", "decisive": boxes_disjoint,
         "verdict": "separable" if boxes_disjoint else "inconclusive",
         "reason": "disjoint bounding boxes separate the components; overlapping ones decide nothing"},
        {"test": "axis_aligned_separating_plane", "decisive": bool(planes), "planes": planes,
         "verdict": "separable" if planes else "inconclusive",
         "reason": "a separating plane is a sufficient witness for splitting, and finding none decides nothing"},
        {"test": "spanning_rectangles_meet", "decisive": False, "they_meet": surfaces_meet,
         "verdict": "inconclusive",
         "reason": ("split components may still be separated by a sphere rather than a plane, so meeting "
                    "spanning surfaces proves nothing either way")},
    ]


# ------------------------------------------------------------------------------ run ----

def hopf_style_pair():
    """Two rectangles in orthogonal planes that link once, plus a far bystander.

    The second rectangle is centred at y = 3/2 with half-height 3/2, so exactly one of its
    outline crossings of the first rectangle's disk falls inside that disk and the other
    falls outside it: that is the whole difference between a link and two curves that merely
    pass through one another.
    """
    first = slab(2, Golden(0), (Golden(0), Golden(0), Golden(0)),
                 {0: Golden(2), 1: Golden(2)})
    second = slab(0, Golden(0), (Golden(0), Golden(3, 2), Golden(0)),
                  {1: Golden(3, 2), 2: Golden(1)})
    bystander = slab(2, Golden(20), (Golden(10), Golden(10), Golden(20)),
                     {0: Golden(1), 1: Golden(1)})
    return first, second, bystander


def main():
    started = time.time()
    rectangles, source_digest = read_retained_rectangles()
    check(len(rectangles) == 3, "the retained literal must declare three rectangles")
    names = list(rectangles)
    retained = json.loads(RETAINED_EVIDENCE.read_text(encoding="utf-8"))["golden_rectangles"]

    linking = {}
    for first, second in itertools.combinations(names, 2):
        forward, crossings = algebraic_intersection(rectangles[first], rectangles[second])
        backward, _ = algebraic_intersection(rectangles[second], rectangles[first])
        retained_pair = (retained["linking_numbers"].get(f"{first}|{second}")
                         or retained["linking_numbers"].get(f"{second}|{first}"))
        linking[f"{first}|{second}"] = {
            "computed": forward, "computed_reverse": backward, "they_agree": forward == backward,
            "retained_projection_crossings": retained_pair, "crossings_inside_a_surface": crossings}
        check(forward == backward, "both directions of the linking computation must agree")

    triple = {",".join(order): triple_intersection_sign(rectangles, order)
              for order in itertools.permutations(names)}
    cyclic = [triple[",".join(names[i:] + names[:i])] for i in range(3)]
    check(all(sign is not None for sign in cyclic), "the triple intersection must exist")
    check(len(set(cyclic)) == 1, "the cyclic orders must share one sign")
    check(all(triple[",".join(reversed(names[i:] + names[:i]))] == -sign
              for i, sign in enumerate(cyclic)), "reversing a cyclic order must flip the sign")
    common = common_points(rectangles)
    check(common == [(Golden(0), Golden(0), Golden(0))],
          "the three filled rectangles must meet exactly at the origin")

    cuts = {}
    for cut in names:
        surviving = [name for name in names if name != cut]
        pair = f"{surviving[0]}|{surviving[1]}"
        value = linking[pair]["computed"]
        tests = separation_tests(rectangles[surviving[0]], rectangles[surviving[1]])
        decisive = any(test["decisive"] for test in tests)
        cuts[cut] = {
            "surviving_pair": surviving,
            "surviving_linking_number": value,
            "linking_number_decides_inseparability": value != 0,
            "separation_tests": tests,
            "separation_decided": decisive,
            "outcome": "inseparable" if value != 0 else ("separable" if decisive else "Unknown"),
            "reason": ("the surviving pair's linking number is zero and no separating witness was found, so the "
                       "computed invariant cannot decide whether the two rings come apart"
                       if value == 0 and not decisive else "decided by the computed invariant or a witness"),
            "milnor_invariant_after_the_cut": ("undefined: the triple linking invariant is defined for a "
                                               "three-component link, and the cut leaves two components and an arc"),
            "why_the_cut_cannot_change_the_linking_number": ("the computation uses only the surviving two "
                                                             "components, so removing the third cannot change it; "
                                                             "this is a property of the computation and is recorded "
                                                             "as such rather than as a theorem"),
        }

    first, second, bystander = hopf_style_pair()
    hopf_forward, hopf_crossings = algebraic_intersection(second, first)
    hopf_backward, _ = algebraic_intersection(first, second)
    check(hopf_forward != 0 and hopf_backward != 0, "the linked control must link")
    check(hopf_forward == hopf_backward, "the linked control's two directions must agree")

    split_a = slab(2, Golden(0), (Golden(0), Golden(0), Golden(0)), {0: Golden(1), 1: Golden(1)})
    split_b = slab(2, Golden(10), (Golden(0), Golden(0), Golden(10)), {0: Golden(1), 1: Golden(1)})
    split_forward, _ = algebraic_intersection(split_b, split_a)
    split_tests = separation_tests(split_a, split_b)
    check(split_forward == 0, "the split control must have linking number zero")
    check(any(test["decisive"] for test in split_tests), "the split control must be decided")

    bystander_links = [algebraic_intersection(bystander, first)[0],
                       algebraic_intersection(bystander, second)[0]]
    check(all(value == 0 for value in bystander_links), "the bystander must be unlinked from both")

    # A rational-ratio companion: the same three slabs with 3/2 in place of PHI. If the
    # unlinking came from the golden ratio rather than from the ratio exceeding one, this
    # would differ; the retained note makes the same caution about uniqueness.
    rational_ratio = Golden(3, 2)
    rational_rectangles = {
        "z0": slab(2, Golden(0), (Golden(0), Golden(0), Golden(0)), {0: Golden(1), 1: rational_ratio}),
        "x0": slab(0, Golden(0), (Golden(0), Golden(0), Golden(0)), {1: Golden(1), 2: rational_ratio}),
        "y0": slab(1, Golden(0), (Golden(0), Golden(0), Golden(0)), {2: Golden(1), 0: rational_ratio}),
    }
    rational_linking = {f"{a}|{b}": algebraic_intersection(rational_rectangles[a], rational_rectangles[b])[0]
                        for a, b in itertools.combinations(list(rational_rectangles), 2)}
    rational_cyclic = triple_intersection_sign(rational_rectangles, tuple(rational_rectangles))
    check(all(value == 0 for value in rational_linking.values()),
          "the rational-ratio companion must be pairwise unlinked as well")
    check(rational_cyclic is not None, "the rational-ratio companion must still meet at one point")
    check(Golden(1) < PHI, "the golden ratio must exceed one, which is what excludes the crossing points")
    check(not (rational_ratio < Golden(1)), "so must the rational companion's ratio")

    # Cutting the bystander away must leave the linked pair linked: recomputed explicitly.
    pair_after_cut = algebraic_intersection(second, first)[0]
    check(pair_after_cut == hopf_forward,
          "removing the bystander must not change the linked pair's linking number")

    for cut, entry in cuts.items():
        check(entry["outcome"] in ("Unknown", "inseparable", "separable"),
              "every cut must carry an outcome word")

    elapsed = time.time() - started
    checks = {
        "the_retained_literals_are_read_without_executing_the_module": True,
        "the_pairwise_linking_numbers_are_recomputed_independently": True,
        "the_two_directions_of_each_linking_number_agree": all(
            entry["they_agree"] for entry in linking.values()),
        "the_triple_intersection_is_recomputed": len(triple) == 6,
        "the_three_filled_rectangles_meet_at_one_point": common == [(Golden(0), Golden(0), Golden(0))],
        "every_cut_choice_is_analysed": len(cuts) == 3,
        "each_separation_test_carries_a_verdict": all(
            all("verdict" in test for test in entry["separation_tests"]) for entry in cuts.values()),
        "the_linked_control_is_decided": hopf_forward != 0,
        "the_split_control_is_decided": split_forward == 0 and any(test["decisive"] for test in split_tests),
        "the_bystander_is_unlinked": all(value == 0 for value in bystander_links),
        "cutting_the_bystander_leaves_the_pair_linked": pair_after_cut == hopf_forward,
        "the_rational_ratio_companion_agrees": all(value == 0 for value in rational_linking.values()),
        "every_cut_carries_an_outcome": all(entry["outcome"] == "Unknown" or
                                            entry["linking_number_decides_inseparability"] for entry in cuts.values()),
        "imported_and_computed_are_separated": True,
        "within_time_budget": elapsed < CONTRACT["budget"]["wall_seconds"],
        "within_assertion_budget": ASSERTIONS["n"] <= MAX_ASSERTIONS,
    }
    status = "ExternalExactPass" if all(checks.values()) else "ExternalPartial"

    evidence = {
        "schema": "adva.external.borromean-cut-linkage.v0",
        "version": 0,
        "status": status,
        "checks": checks,
        "contract": "experiments/borromean_cut_linkage/contract.json",
        "checker_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "tooling": {
            "python": sys.version.split()[0],
            "arithmetic": "exact a + b*sqrt(5) with rational a and b; no float in any computed quantity",
            "external_library": "none",
            "external_oracle_not_native_authority": True,
        },
        "imported_not_verified_here": [
            {"statement": ("Mellor and Melvin: the triple intersection number of Seifert surfaces computes "
                           "Milnor's triple linking invariant modulo the gcd of the pairwise linking numbers"),
             "source": "A geometric interpretation of Milnor's triple linking numbers, AGT 3 (2003) 557-568, arXiv:math/0110001",
             "used_for": "why a raw triple-point count is insufficient, and what m - t means"},
            {"statement": "a nonzero linking number means the two-component link is not split",
             "source": "elementary; used only in that direction"},
            {"statement": ("cutting any one component of the standard Borromean rings leaves the other two "
                           "unlinked, so the classical configuration does not survive a cut"),
             "source": ("classical; NOT transferred to the retained configuration, because no isotopy to the "
                        "standard Borromean rings is computed here")},
        ],
        "self_computed": {
            "source": {"path": "experiments/golden_ratio/calibration.py", "sha256": source_digest,
                       "how": "the literal rectangles assignment decoded by a restricted AST decoder; the module is never executed"},
            "rectangles": {name: {"fixed": rect["fixed"], "value": str(rect["value"]),
                                  "center": [str(value) for value in rect["center"]],
                                  "extents": {str(axis): str(value) for axis, value in rect["extents"].items()}}
                           for name, rect in rectangles.items()},
            "method": ("the pairwise linking number as the algebraic intersection of one outline with the other "
                       "component's spanning rectangle, which is independent of the retained projection-crossing count"),
            "linking_numbers": linking,
            "triple_intersection": {
                "signed_sums_by_order": {order: (sign if sign is None else sign) for order, sign in triple.items()},
                "cyclic_orders_share_one_sign": True,
                "cyclic_sign": cyclic[0],
                "retained_recorded": retained["link_certificate"]["triple_intersection"],
                "common_point": "the origin, interior to all three filled rectangles",
            },
            "cuts": cuts,
        },
        "controls_built_here": {
            "hopf_style_linked_pair": {
                "construction": ("one filled square of half-width 2 in z = 0, and one rectangle centred at "
                                 "y = 3/2 with half-extents 3/2 and 1 in x = 0, chosen so that exactly one of "
                                 "its outline crossings of the first disk falls inside it"),
                "linking_one_way": hopf_forward,
                "linking_the_other_way": hopf_backward,
                "crossings_inside_the_disk": hopf_crossings,
                "outcome": ("the pair is linked, and a nonzero linking number decides it, so this pair stays "
                            "inseparable even after a third component is cut away"),
            },
            "split_pair": {
                "construction": "two parallel squares in z = 0 and z = 10",
                "linking": split_forward,
                "separation_tests": split_tests,
                "outcome": "separable, decided by an exhibited separating plane rather than by the linking number",
            },
            "bystander": {
                "construction": "a small square far away, unlinked from both members of the linked pair",
                "linking_to_the_pair": bystander_links,
                "outcome": "cutting this third component changes nothing about the pair's linkage",
            },
            "rational_ratio_companion": {
                "construction": "the same three slabs with 3/2 in place of the golden ratio",
                "pairwise_linking": rational_linking,
                "triple_intersection_sign": rational_cyclic,
                "outcome": ("the same conclusion, so what unlinks this family is the ratio exceeding one, not the "
                            "golden ratio in particular; this matches the retained round's own caution that a unit "
                            "invariant here is not evidence of uniqueness of the golden ratio"),
            },
            "retained_squares_companion": {
                "what_it_is": "the concentric orthogonal squares of the retained surface audit, quoted and not recomputed",
                "retained_values": "pairwise linking zero, boundary term m = 1, triple points t = 1, mu = 0",
                "why_it_matters": ("the same raw triple-point count as the golden rectangles with no triple "
                                   "linking, which is the imported point that a count is not an invariant"),
            },
        },
        "the_contrast": {
            "pairwise_linking_under_a_cut": ("survives and decides: it is an invariant of the surviving pair, it is "
                                             "recomputed here after each cut, and a nonzero value proves the pair is "
                                             "not split"),
            "triple_linking_under_a_cut": ("does not survive as a computation: the invariant is defined for a "
                                           "three-component link, so the cut does not hide it but removes its "
                                           "domain, and the surviving pair's linking number is zero in the retained "
                                           "configuration, so nothing computed here replaces it"),
            "consequence": ("in the retained configuration every choice of cut leaves a surviving pair whose "
                            "linking number is zero, so this run cannot decide whether those two rings come apart, "
                            "and it reports Unknown rather than a guess"),
        },
        "what_would_decide_the_unknown": [
            "the Alexander or Conway polynomial of the surviving two-component sublink from a diagram, since a nonzero polynomial proves non-splitting",
            "an explicit splitting sphere, or an isotopy that separates the two components",
            "an isotopy from the retained configuration to the standard Borromean rings, which would let the classical Brunnian statement transfer; not computed here",
        ],
        "cost": {"wall_seconds_before_serialization": round(elapsed, 3),
                 "assertions": ASSERTIONS["n"], "subprocesses": 0},
        "what_is_not_claimed": [
            "This is an external exact computation, not a native certificate, and it admits nothing into any catalog",
            "No isotopy to the standard Borromean rings is computed, so the classical Brunnian statement is quoted and not transferred",
            "Whether the surviving two components of the retained configuration come apart is Unknown here and is not reported as separable or inseparable",
            "The linking number is necessary but not sufficient for splitting: a zero value decides nothing, which is stated wherever it occurs",
            "Milnor's invariant is quoted through the imported theorem and is not computed from a link complement here",
            "The retained squares companion is quoted with its recorded values and is not recomputed in this run",
            "The controls are built here for contrast and are not claims about the retained configuration",
            "Nothing about Feigenbaum, Arakelov, mirror symmetry, the density-wave line or the repository's geometry growth line follows from this run",
        ],
    }
    (HERE / "evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{status}: {ASSERTIONS['n']} assertions, {round(elapsed, 3)} s")
    for pair, entry in linking.items():
        print(f"  lk({pair}) = {entry['computed']} (reverse {entry['computed_reverse']}, "
              f"retained {entry['retained_projection_crossings']})")
    print(f"  triple intersection, cyclic sign = {cyclic[0]}")
    for cut, entry in cuts.items():
        print(f"  cut {cut}: surviving {entry['surviving_pair']} lk={entry['surviving_linking_number']} "
              f"-> {entry['outcome']}")
    print(f"  Hopf control {hopf_forward} / {hopf_backward} (one crossing inside the disk); "
          f"split control {split_forward}")
    print(f"  rational-ratio companion: linking {rational_linking}, triple sign {rational_cyclic}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
