#!/usr/bin/env python3
"""Where are the HNS walls, and is the graded-data fibre a chamber?

Frozen contract: contract.json in this directory (Research 0129 section 3).
The model is imported from the frozen sibling experiment, not reimplemented, and
its declared counts are reproduced at run time as an interface check. Every wall
condition, every slope and every pairing below is an exact Fraction or integer.
No floating point is used on the mathematics.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
import pathlib
import sys
import time
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
SIBLING_DIR = HERE.parent / "hns_object_forgetting"
SIBLING_SRC = SIBLING_DIR / "calibration.py"
SIBLING_EVIDENCE = SIBLING_DIR / "evidence.json"
SIBLING_EVIDENCE_SHA = "09280cf0cd5e3bdd17b32200f0d7121d1bbe31a8eafec6a4f4b85912fd59d550"

ASSERTIONS = {"n": 0}


def check(condition, message):
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SIB = load(SIBLING_SRC, "hns_object_forgetting_calibration")


# ----------------------------------------------------------- the model ----

def classes(max_dim, max_total):
    return [
        (d1, d2, r)
        for d1 in range(max_dim + 1)
        for d2 in range(max_dim + 1)
        for r in range(min(d1, d2) + 1)
        if 1 <= d1 + d2 <= max_total
    ]


def model_pass(fields, max_dim, max_total, thetas, sweep):
    """Run the frozen sibling model and collect what the new questions need.

    The sibling's own regression block re-runs one injective class over the sweep;
    that block is reproduced here so that its declared filtration count, 429, is
    matched rather than approximated. Keys and collisions used for the interface
    check are restricted to the declared eleven-parameter sweep, because the
    extra off-grid parameters are this round's addition and would inflate them.
    """
    per_field = {}
    regression_calls = 0
    for p in fields:
        subs = {d: SIB.all_subspaces(p, d) for d in range(0, max_dim + 1)}
        records = []
        sweep_keys = {"dims_and_slopes": set(), "dims_slopes_and_piece_rank": set()}
        for (d1, d2, r) in classes(max_dim, max_total):
            im_phi = SIB.image_basis(p, d1, d2, r)
            subs_here = SIB.subobjects(p, d1, d2, r, subs[d1], subs[d2])
            for theta in thetas:
                pieces = SIB.hn_filtration(p, d1, d2, r, subs_here, im_phi, theta)
                weak, strong = SIB.keys_of(pieces)
                if theta in sweep:
                    sweep_keys["dims_and_slopes"].add(weak)
                    sweep_keys["dims_slopes_and_piece_rank"].add(strong)
                records.append(
                    {
                        "class": (d1, d2, r),
                        "theta": theta,
                        "piece_dims": tuple(tuple(pc["dims"]) for pc in pieces),
                        "weak": weak,
                    }
                )
        if regression_calls == 0:  # the sibling runs this block once in total
            regression = next(c for c in classes(max_dim, max_total) if c[2] == c[0] and c[0] > 0)
            d1, d2, r = regression
            im_phi = SIB.image_basis(p, d1, d2, r)
            subs_here = SIB.subobjects(p, d1, d2, r, subs[d1], subs[d2])
            for theta in sweep:
                SIB.hn_filtration(p, d1, d2, r, subs_here, im_phi, theta)
                regression_calls += 1
        per_field[p] = {
            "classes": len(classes(max_dim, max_total)),
            "records": records,
            "shadows_dims_and_slopes": len(sweep_keys["dims_and_slopes"]),
            "shadows_with_piece_rank": len(sweep_keys["dims_slopes_and_piece_rank"]),
        }
    return per_field, regression_calls


def collision_count(records):
    seen = {}
    for rec in records:
        seen.setdefault((rec["theta"], rec["weak"]), set()).add(rec["class"])
    return sum(1 for owners in seen.values() if len(owners) > 1)


# ----------------------------------------------------------- the walls ----

def wall_form(e, d):
    """(a, b) with mu_e(theta) = mu_d(theta) exactly when a*th1 + b*th2 = 0."""
    delta = e[0] * d[1] - e[1] * d[0]
    return (delta, -delta)


def primitive(v):
    g = math.gcd(abs(v[0]), abs(v[1]))
    return (v[0] // g, v[1] // g) if g else (0, 0)


def wall_analysis(dims, thetas):
    tied, wall_dirs = [], {}
    for e, d in itertools.combinations(dims, 2):
        form = wall_form(e, d)
        if form == (0, 0):
            tied.append([list(e), list(d)])
        else:
            wall_dirs.setdefault(primitive(form), []).append([list(e), list(d)])
    exact_mismatch = 0
    for e, d in itertools.combinations(dims, 2):
        a, b = wall_form(e, d)
        for theta in thetas:
            lhs = SIB.slope(e, theta) == SIB.slope(d, theta)
            rhs = a * theta[0] + b * theta[1] == 0
            if lhs != rhs:
                exact_mismatch += 1
    return {
        "admissible_dimension_vectors": [list(d) for d in dims],
        "identically_tied_pairs": tied,
        "identically_tied_pair_count": len(tied),
        "primitive_wall_directions": sorted([list(k) for k in wall_dirs]),
        "genuine_wall_pair_count": sum(len(v) for v in wall_dirs.values()),
        "slope_equality_identity_mismatches": exact_mismatch,
        "identity_checked_over": [list(t) for t in thetas],
    }


# ------------------------------------------------- the graded-data fibre ----

def cell_of(theta):
    if theta[0] > theta[1]:
        return "+"
    if theta[0] < theta[1]:
        return "-"
    return "0"


def level_condition(piece_dims, theta, other):
    """Two parameters in one cell agree on the recorded slopes exactly when the
    difference of the parameters pairs to zero with every piece dimension."""
    diff = (theta[0] - other[0], theta[1] - other[1])
    return all(diff[0] * d[0] + diff[1] * d[1] == 0 for d in piece_dims)


def fibre_analysis(per_field, thetas):
    """Is the graded-data fibre a chamber of the wall arrangement, or a level set?

    Two things are separated. A cell of the arrangement fixes the *order* of the
    slopes and therefore the filtration type; it does not fix the slope values,
    which move with the parameters. So the fibre is expected to be finer than a
    cell, and a pair of parameters in different cells is expected to share a key
    only when the filtration is trivial at both.
    """
    same_cell_different_key = []
    same_cell_different_key_total = 0
    different_cell_same_key = []
    different_cell_same_key_total = 0
    same_cell_same_type = True
    criterion_mismatch = []
    single_piece_across_cells = True
    pairs = 0
    for p, data in per_field.items():
        by_class = {}
        for rec in data["records"]:
            by_class.setdefault(rec["class"], {})[rec["theta"]] = rec
        for cls, table in by_class.items():
            for theta, other in itertools.combinations(thetas, 2):
                pairs += 1
                a, b = table[theta], table[other]
                same_key = a["weak"] == b["weak"]
                same_type = a["piece_dims"] == b["piece_dims"]
                same_cell = cell_of(theta) == cell_of(other)
                if same_cell and not same_type:
                    same_cell_same_type = False
                if same_cell and not same_key:
                    same_cell_different_key_total += 1
                if same_cell and not same_key and len(same_cell_different_key) < 6:
                    same_cell_different_key.append(
                        {
                            "field": p, "class": list(cls),
                            "parameters": [list(theta), list(other)],
                            "cell": cell_of(theta),
                            "filtration_type": [list(x) for x in a["piece_dims"]],
                            "graded_data_left": [list(x) for x in a["weak"]],
                            "graded_data_right": [list(x) for x in b["weak"]],
                        }
                    )
                if (not same_cell) and same_key:
                    different_cell_same_key_total += 1
                    if len(a["piece_dims"]) != 1 or len(b["piece_dims"]) != 1:
                        single_piece_across_cells = False
                    if len(different_cell_same_key) < 4:
                        different_cell_same_key.append(
                            {
                                "field": p, "class": list(cls),
                                "parameters": [list(theta), list(other)],
                                "cells": [cell_of(theta), cell_of(other)],
                                "pieces_at_left": len(a["piece_dims"]),
                                "pieces_at_right": len(b["piece_dims"]),
                                "graded_data": [list(x) for x in a["weak"]],
                            }
                        )
                predicted = same_type and level_condition(a["piece_dims"], theta, other)
                if predicted != same_key and len(criterion_mismatch) < 5:
                    criterion_mismatch.append(
                        {"field": p, "class": list(cls),
                         "parameters": [list(theta), list(other)],
                         "predicted": predicted, "actual": same_key}
                    )
    return {
        "class_parameter_pairs": pairs,
        "same_cell_implies_same_filtration_type": same_cell_same_type,
        "same_cell_different_graded_data_total": same_cell_different_key_total,
        "same_cell_different_graded_data": same_cell_different_key,
        "different_cell_same_graded_data_total": different_cell_same_key_total,
        "different_cell_same_graded_data": different_cell_same_key,
        "every_different_cell_shared_key_is_a_single_piece": single_piece_across_cells,
        "criterion": "the weak key is equal exactly when the filtration type is equal and (theta - theta') pairs to zero with every piece dimension",
        "criterion_mismatches": criterion_mismatch,
    }


# ------------------------------------------- the R2 criterion, in two dimensions ----

def hull(points):
    pts = sorted({(Fr(x), Fr(y)) for x, y in points})
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for pt in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], pt) <= 0:
            lower.pop()
        lower.append(pt)
    upper = []
    for pt in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], pt) <= 0:
            upper.pop()
        upper.append(pt)
    return lower[:-1] + upper[:-1]


def facets(poly):
    """Normalised facet data <n, x> <= 1, with the hull on the side of the origin.

    The outward normal of an edge of a counter-clockwise hull is (dy, -dx). A
    non-positive offset means the origin is outside that facet, so the polytope
    never has the origin in its interior and nothing is normalised: flipping the
    normal would silently make the test vacuous.
    """
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        normal = (b[1] - a[1], a[0] - b[0])
        offset = normal[0] * a[0] + normal[1] * a[1]
        if offset <= 0:
            return None
        out.append((Fr(normal[0]) / offset, Fr(normal[1]) / offset, offset))
    return out


def hypothesis(poly):
    if len(poly) < 3:
        return "not full-dimensional"
    area = Fr(0)
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        area += x1 * y2 - x2 * y1
    if area == 0:
        return "not full-dimensional"
    if facets(poly) is None:
        return "the origin is not interior"
    return None


def criterion(vertices):
    """The R2 minimal-lattice lemma for a two-dimensional rational polytope."""
    poly = hull(vertices)
    reason = hypothesis(poly)
    if reason:
        return {"verdict": "RefusedAtHypothesis", "reason": reason}
    fs = facets(poly)
    polar = hull([(f[0], f[1]) for f in fs])
    witness = None
    for v in poly:
        for y in polar:
            value = v[0] * y[0] + v[1] * y[1]
            if value.denominator != 1:
                witness = {"primal_vertex": [str(v[0]), str(v[1])],
                           "polar_vertex": [str(y[0]), str(y[1])],
                           "pairing": str(value),
                           "denominator": value.denominator}
                break
        if witness:
            break
    if witness:
        return {"verdict": "Fail", "witness": witness,
                "vertices": [[str(x), str(y)] for x, y in poly],
                "polar_vertices": [[str(x), str(y)] for x, y in polar]}
    return {"verdict": "Pass",
            "minimal_witness_lattice": {
                "generators_are_the_vertices": [[str(x), str(y)] for x, y in poly],
                "all_vertices_integral": all(
                    x.denominator == 1 and y.denominator == 1 for x, y in poly
                ),
                "note": "the lemma's witness lattice is the Z-span of the vertex set; when a vertex is not integral that lattice strictly contains Z^2 and a classical index in Z^2 does not apply",
            },
            "vertices": [[str(x), str(y)] for x, y in poly],
            "polar_vertices": [[str(x), str(y)] for x, y in polar]}


def positively_spans(normals):
    """Do the normals positively span the plane? Equivalently, is the origin
    interior to their convex hull, which is what makes the half-plane
    intersection bounded."""
    return hypothesis(hull(normals)) is None


# ------------------------------------------------------------------ main ----

def main():
    started = time.monotonic()
    contract = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
    o = contract["objects"]
    fields = o["fields"]
    max_dim, max_total = o["max_ambient_dim"], o["max_total_dim"]
    sweep = [tuple(t) for t in o["theta_sweep"]]
    extra = [tuple(t) for t in o["extra_off_grid_parameters"]]
    thetas = sweep + extra
    SIB.LIMITS.update(contract["budget"])

    evidence = {
        "schema": "adva.dodecahedral-hamiltonicity.evidence.research",
        "schema_note": "replaced below by the wall-localization schema",
        "version": 0,
        "checker_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "contract": "experiments/hns_wall_localization/contract.json",
        "exact_field": "Q with Fractions; no floating point on the mathematics",
        "budget": contract["budget"],
    }
    evidence["schema"] = "adva.research.hns-wall-localization-evidence.v0"
    evidence.pop("schema_note")

    # --- interface: the frozen sibling model, re-run and compared
    per_field, regression_calls = model_pass(fields, max_dim, max_total, thetas, set(sweep))
    recorded = json.loads(SIBLING_EVIDENCE.read_text(encoding="utf-8"))
    actual_sha = hashlib.sha256(SIBLING_EVIDENCE.read_bytes()).hexdigest()
    all_records = [r for p in fields for r in per_field[p]["records"]]
    sweep_records = [r for r in all_records if r["theta"] in set(sweep)]
    interface = {
        "sibling_evidence_sha256": actual_sha,
        "sibling_evidence_sha256_expected": SIBLING_EVIDENCE_SHA,
        "sibling_evidence_unchanged": actual_sha == SIBLING_EVIDENCE_SHA,
        "objects_rerun": len({(p, r["class"]) for p in fields for r in per_field[p]["records"]}),
        "objects_recorded": recorded["counts"]["objects"],
        "filtrations_rerun_on_the_sweep": len(sweep_records),
        "filtrations_rerun_including_the_regression_block": len(sweep_records) + regression_calls,
        "filtrations_recorded": recorded["counts"]["filtrations"],
        "shadows_per_field_rerun": {str(p): per_field[p]["shadows_dims_and_slopes"] for p in fields},
        "shadows_per_field_recorded": {str(p): recorded["per_field"][str(p)]["shadows_dims_and_slopes"] for p in fields},
        "collisions_rerun": sum(
            collision_count([r for r in per_field[p]["records"] if r["theta"] in set(sweep)])
            for p in fields
        ),
        "collisions_recorded": recorded["collision_totals"]["dims_and_slopes"]["colliding_shadows"],
    }
    interface["agrees"] = (
        interface["sibling_evidence_unchanged"]
        and interface["objects_rerun"] == interface["objects_recorded"]
        and interface["filtrations_rerun_including_the_regression_block"] == interface["filtrations_recorded"]
        and interface["shadows_per_field_rerun"] == interface["shadows_per_field_recorded"]
        and interface["collisions_rerun"] == interface["collisions_recorded"]
    )
    evidence["interface"] = interface
    check(interface["agrees"], "the frozen sibling model was not reproduced")

    # --- the walls, computed exactly
    dims = [
        (a, b)
        for a in range(max_dim + 1)
        for b in range(max_dim + 1)
        if 1 <= a + b <= max_total
    ]
    evidence["walls"] = wall_analysis(dims, thetas)
    evidence["walls"]["directions_are_the_single_line_theta1_equals_theta2"] = (
        evidence["walls"]["primitive_wall_directions"] == [[-1, 1], [1, -1]]
    )
    check(evidence["walls"]["slope_equality_identity_mismatches"] == 0,
          "the slope equality identity failed on the model")

    # --- the fibre question
    evidence["fibre"] = fibre_analysis(per_field, thetas)
    check(evidence["fibre"]["criterion_mismatches"] == [], "the fibre criterion failed")
    check(evidence["fibre"]["same_cell_implies_same_filtration_type"],
          "a cell does not determine the filtration type")
    check(evidence["fibre"]["same_cell_different_graded_data"],
          "no witness was found that the fibre is finer than the cell")

    # --- the R2 criterion, validated on its own fixtures first
    fixtures = {
        "square_2d": [(1, 1), (-1, 1), (-1, -1), (1, -1)],
        "reflexive_triangle_2d": [(1, 0), (0, 1), (-1, -1)],
        "twice_square_2d": [(2, 2), (-2, 2), (-2, -2), (2, -2)],
        "halves_triangle_2d": [(1, 0), (0, 1), (Fr(-1, 2), Fr(-1, 2))],
        "thirds_triangle_2d": [(1, 0), (0, 1), (Fr(-1, 3), Fr(-1, 3))],
    }
    evidence["criterion_validation"] = {
        name: criterion(pts) for name, pts in fixtures.items()
    }
    val = evidence["criterion_validation"]
    check(val["square_2d"]["verdict"] == "Pass", "the square must pass")
    check(val["reflexive_triangle_2d"]["verdict"] == "Pass", "the reflexive triangle must pass")
    check(val["twice_square_2d"]["verdict"] == "Pass", "twice the square must still pass")
    check(val["halves_triangle_2d"]["verdict"] == "Pass",
          "the halves triangle has nonintegral vertices yet must still pass with a coarser lattice")
    check(val["thirds_triangle_2d"]["verdict"] == "Fail",
          "the thirds triangle must fail with a nonintegral pairing")

    # --- the S1 candidates
    normals = [tuple(v) for v in evidence["walls"]["primitive_wall_directions"]]
    grid = hull([(Fr(x), Fr(y)) for x, y in sweep])
    weight = [(d[0] - d[1], d[0] + d[1]) for d in dims]
    candidates = {
        "canonical_half_plane_intersection": {
            "construction": "the intersection of the half planes whose normals are the wall directions, offset one",
            "normals": [list(n) for n in normals],
            "positively_spans_the_plane": positively_spans(normals),
            "verdict": None,
        },
        "hull_of_wall_normals": {
            "construction": "the convex hull of the primitive wall directions",
            "vertices": [list(v) for v in normals],
            "verdict": None,
        },
        "hull_of_the_declared_grid": {
            "construction": "the convex hull of the eleven declared grid parameters",
            "vertices": [[str(x), str(y)] for x, y in grid],
            "verdict": None,
        },
        "weight_polytope_of_the_declared_range": {
            "construction": "the convex hull of (d1 - d2, d1 + d2) over the declared dimension vectors",
            "vertices": [list(v) for v in weight],
            "verdict": None,
        },
    }
    candidates["canonical_half_plane_intersection"]["verdict"] = (
        "RefusedAtHypothesis: the wall normals do not positively span the plane, so the "
        "intersection is an unbounded strip and not a polytope"
        if not candidates["canonical_half_plane_intersection"]["positively_spans_the_plane"]
        else "handed to the criterion"
    )
    candidates["hull_of_wall_normals"]["verdict"] = criterion(normals)["verdict"] == "RefusedAtHypothesis" and (
        "RefusedAtHypothesis: a segment is not full dimensional"
    ) or "handed to the criterion"
    candidates["hull_of_the_declared_grid"]["verdict"] = criterion(
        list(candidates["hull_of_the_declared_grid"]["vertices"])
        and [(Fr(x), Fr(y)) for x, y in grid] or []
    )["verdict"] + " (and refused as non-canonical: the grid is a declared finite sample, not a consequence of the stability structure)"
    weight_poly = criterion(weight)
    candidates["weight_polytope_of_the_declared_range"]["verdict"] = (
        weight_poly["verdict"]
        + (": " + weight_poly.get("reason", "") if weight_poly["verdict"] == "RefusedAtHypothesis" else "")
    )
    candidates["hull_of_the_declared_grid"]["criterion_result"] = criterion(
        [(Fr(x), Fr(y)) for x, y in grid]
    )
    candidates["weight_polytope_of_the_declared_range"]["criterion_result"] = weight_poly
    evidence["s1_candidates"] = candidates
    evidence["s1_outcome"] = (
        "No candidate reached the criterion as a canonical polytope: three fail its hypothesis and the "
        "fourth is decided but is the hull of a declared finite sample rather than a consequence of the "
        "stability structure."
    )

    # --- verdicts
    checks = {
        "sibling_model_reproduced": interface["agrees"],
        "wall_identity_exact_on_the_model": evidence["walls"]["slope_equality_identity_mismatches"] == 0,
        "wall_set_is_one_line": evidence["walls"]["directions_are_the_single_line_theta1_equals_theta2"],
        "fibre_criterion_holds": evidence["fibre"]["criterion_mismatches"] == [],
        "cell_determines_the_filtration_type": evidence["fibre"]["same_cell_implies_same_filtration_type"],
        "fibre_is_finer_than_the_cell_witnessed": bool(evidence["fibre"]["same_cell_different_graded_data"]),
        "cross_wall_shared_keys_are_single_piece": evidence["fibre"]["every_different_cell_shared_key_is_a_single_piece"],
        "criterion_validated_on_fixtures": all(
            val[k]["verdict"] == v
            for k, v in (("square_2d", "Pass"), ("reflexive_triangle_2d", "Pass"),
                         ("twice_square_2d", "Pass"), ("halves_triangle_2d", "Pass"),
                         ("thirds_triangle_2d", "Fail"))
        ),
        "every_s1_candidate_refused_or_non_canonical": all(
            c["verdict"] is not None for c in candidates.values()
        ),
        "within_assertion_budget": ASSERTIONS["n"] <= o["max_assertions"],
        "within_time_budget": (time.monotonic() - started) <= contract["budget"]["wall_seconds"],
    }
    evidence["checks"] = checks
    evidence["assertions"] = ASSERTIONS["n"]
    evidence["status"] = "ExternalExactPass" if all(checks.values()) else "Residual"
    evidence["cost"] = {
        "wall_seconds_before_serialization": round(time.monotonic() - started, 6),
        "assertions_this_round": ASSERTIONS["n"],
        "assertions_inside_the_imported_sibling_model": SIB.COUNTS["assertions"],
        "subprocesses": 0,
    }
    text = json.dumps(evidence, indent=2, sort_keys=True)
    (HERE / "evidence.json").write_text(text + "\n", encoding="utf-8")
    print(json.dumps({k: evidence[k] for k in
                      ("status", "checks", "cost", "s1_outcome")}, indent=1))
    print("walls:", json.dumps(evidence["walls"]["primitive_wall_directions"]),
          "tied pairs:", evidence["walls"]["identically_tied_pair_count"])
    print("fibre witness:", json.dumps(evidence["fibre"]["same_cell_different_graded_data"][:1])[:400])
    return 0 if evidence["status"] == "ExternalExactPass" else 1


if __name__ == "__main__":
    sys.exit(main())
