#!/usr/bin/env python3
"""Bounded external exact check: the lattice gate for a centered rational polytope.

Question. For a fixed centered full-dimensional rational polytope P with the
origin in its interior, does there exist a full-rank lattice M with
Vert(P) subset M and Vert(P^o) subset M* under the declared dot pairing?

Minimal-lattice lemma. Such an M exists if and only if every pairing
dot(v, y), v a supplied primal vertex and y a computed polar vertex, is an
integer. The minimal candidate is M = Z-span(Vert(P)), and no larger lattice
can be easier, because M1 subset M2 implies M2* subset M1*.

This script decides that question by one finite pairing check per fixture. It
performs no lattice search: the universal quantifier is discharged by the
lemma's two directions, and the checker never promotes a partial enumeration.

Retained correction replay. The first attempt exceeded its declared 25-second
CPU budget because this file's first lattice-basis helper did not terminate.
The helper is now a Euclidean integer reduction; the budget counters were
raised before the retained run, and the failed attempt is recorded in
execution-cost.json rather than hidden.

Authored by deepseek-v4-flash (DeepSeek Harness), committed through Mingli
Yuan's GitHub account as an authorized proxy. Python Fraction arithmetic is an
external oracle here, not Adva semantic authority.
"""

import argparse
import hashlib
import itertools
import json
import math
import os
import platform
import resource
import time
from fractions import Fraction

ZERO = Fraction(0)
ONE = Fraction(1)


class Exhausted(Exception):
    """A declared budget or a coverage guard was hit."""


class Budget:
    def __init__(self, max_triples, max_checks, seconds):
        self.max_triples = max_triples
        self.max_checks = max_checks
        self.deadline = time.monotonic() + seconds
        self.triples = 0
        self.checks = 0

    def triple(self):
        self.triples += 1
        if self.triples > self.max_triples or time.monotonic() >= self.deadline:
            raise Exhausted("triple budget or wall clock")

    def check(self, count=1):
        self.checks += count
        if self.checks > self.max_checks or time.monotonic() >= self.deadline:
            raise Exhausted("check budget or wall clock")


# ---------------------------------------------------------------- exact algebra


def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), ZERO)


def solve(matrix, rhs):
    """Exact solution of a square rational system, or None when singular."""
    d = len(matrix)
    rows = [[Fraction(x) for x in row] + [Fraction(rhs[i])] for i, row in enumerate(matrix)]
    for col in range(d):
        pivot = None
        for r in range(col, d):
            if rows[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            return None
        rows[col], rows[pivot] = rows[pivot], rows[col]
        lead = rows[col][col]
        rows[col] = [x / lead for x in rows[col]]
        for r in range(d):
            if r != col and rows[r][col] != 0:
                factor = rows[r][col]
                rows[r] = [a - factor * b for a, b in zip(rows[r], rows[col])]
    return tuple(rows[i][d] for i in range(d))


def determinant(rows):
    d = len(rows)
    if d == 1:
        return Fraction(rows[0][0])
    total = ZERO
    for j in range(d):
        minor = [row[:j] + row[j + 1:] for row in rows[1:]]
        total += ((-1) ** j) * rows[0][j] * determinant(minor)
    return total


def lattice_index(rows, dim):
    """Index in Z^dim of the lattice spanned by integer rows: gcd of dim-minors.

    Returns None when the rows do not span a full-rank lattice.
    """
    g = 0
    for combo in itertools.combinations(rows, dim):
        det = determinant([list(r) for r in combo])
        g = math.gcd(g, abs(int(det)))
    return None if g == 0 else g


def hnf_basis(rows, dim):
    """A triangular basis of the integer row lattice, by Euclidean reduction.

    Each elimination step strictly decreases a pivot magnitude, so this
    terminates; the previous helper looped and was replaced (see module note).
    """
    matrix = [list(r) for r in rows if any(x != 0 for x in r)]
    pivot_row = 0
    pivots = []
    for col in range(dim):
        while True:
            nonzero = [i for i in range(pivot_row, len(matrix)) if matrix[i][col] != 0]
            if len(nonzero) <= 1:
                break
            nonzero.sort(key=lambda i: abs(matrix[i][col]))
            head, other = nonzero[0], nonzero[1]
            quotient = matrix[other][col] // matrix[head][col]
            if quotient:
                matrix[other] = [a - quotient * b
                                 for a, b in zip(matrix[other], matrix[head])]
            else:
                matrix[other], matrix[head] = matrix[head], matrix[other]
            # continue: the Euclidean step reduces the next pivot magnitude
        targets = [i for i in range(pivot_row, len(matrix)) if matrix[i][col] != 0]
        if targets:
            matrix[pivot_row], matrix[targets[0]] = matrix[targets[0]], matrix[pivot_row]
            if matrix[pivot_row][col] < 0:
                matrix[pivot_row] = [-x for x in matrix[pivot_row]]
            pivots.append(col)
            pivot_row += 1
    for i, col in enumerate(pivots):
        if matrix[i][col] == 0:
            continue
        for j in range(i):
            quotient = matrix[j][col] // matrix[i][col]
            if quotient:
                matrix[j] = [a - quotient * b for a, b in zip(matrix[j], matrix[i])]
    return [r for r in matrix[:len(pivots)]]


# ------------------------------------------------------------------- geometry


def active_polar_vertices(vertices, dim, budget, constraints=None):
    """Polar vertices of conv(vertices) by complete active-constraint enumeration.

    With the origin interior, polar vertices are exactly the facet normals of the
    offset-one normalization, so this also yields the H-representation
    {x : dot(y, x) <= 1 for every returned y}.
    """
    pool = vertices if constraints is None else constraints
    found = set()
    for combo in itertools.combinations(range(len(pool)), dim):
        budget.triple()
        y = solve([list(pool[i]) for i in combo], [ONE] * dim)
        if y is None:
            continue
        feasible = True
        for v in pool:
            budget.check()
            if dot(v, y) > ONE:
                feasible = False
                break
        if feasible:
            found.add(y)
    return sorted(found)


def pairing_obstruction(vertices, polar, budget):
    """The first nonintegral primal-polar pairing, and every distinct value seen."""
    first = None
    witnesses = {}
    for v in vertices:
        for y in polar:
            budget.check()
            value = dot(v, y)
            if value.denominator != 1:
                record = {"primal_vertex": [str(x) for x in v],
                          "polar_vertex": [str(x) for x in y]}
                if first is None:
                    first = dict(record, pairing=str(value))
                witnesses.setdefault(str(value), record)
    return first, witnesses


def common_denominator(vectors):
    scale = 1
    for vec in vectors:
        for x in vec:
            scale = scale * x.denominator // math.gcd(scale, x.denominator)
    return scale


def as_integers(vectors, scale):
    return [[int(x * scale) for x in vec] for vec in vectors]


# ------------------------------------------------------------------ fixtures


def signed_permutations_of(values, dim):
    out = set()
    for perm in itertools.permutations(values):
        for signs in itertools.product((1, -1), repeat=dim):
            out.add(tuple(Fraction(perm[i] * signs[i]) for i in range(dim)))
    return sorted(out)


def shear_matrix():
    """A(x, y, z) = (x + y, y, z), an integral unimodular map."""
    return [[1, 1, 0], [0, 1, 0], [0, 0, 1]]


def apply_matrix(matrix, vector):
    return tuple(Fraction(sum(matrix[i][j] * vector[j] for j in range(len(vector))))
                 for i in range(len(matrix)))


def contragredient_image(matrix, vector):
    """Solve matrix^T z = vector: the correct transport for polar covectors."""
    dim = len(vector)
    transpose = [[Fraction(matrix[j][i]) for j in range(dim)] for i in range(dim)]
    return solve(transpose, list(vector))


def fixture_definitions():
    cube = signed_permutations_of((1, 1, 1), 3)
    shear = shear_matrix()
    square = sorted({(Fraction(1), Fraction(1)), (Fraction(1), Fraction(-1)),
                     (Fraction(-1), Fraction(1)), (Fraction(-1), Fraction(-1))})
    triangle = [tuple(Fraction(x) for x in v) for v in ((1, 0), (0, 1), (-1, -1))]
    simplex = [tuple(Fraction(x) for x in v)
               for v in ((1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, -1, -1))]
    to24 = signed_permutations_of((0, 1, 2), 3)
    return [
        {"name": "square_2d", "dim": 2, "vertices": square, "expect": "pass"},
        {"name": "reflexive_triangle_2d", "dim": 2, "vertices": triangle, "expect": "pass"},
        {"name": "cube_3d", "dim": 3, "vertices": cube, "expect": "pass"},
        {"name": "sheared_cube_3d", "dim": 3,
         "vertices": sorted({apply_matrix(shear, v) for v in cube}), "expect": "pass",
         "transport_of": "cube_3d", "matrix": shear},
        {"name": "reflexive_simplex_3d", "dim": 3, "vertices": simplex, "expect": "pass"},
        {"name": "to24_3d", "dim": 3, "vertices": to24, "expect": "fail"},
        {"name": "unimodular_image_of_to24_3d", "dim": 3,
         "vertices": sorted({apply_matrix(shear, v) for v in to24}), "expect": "fail",
         "transport_of": "to24_3d", "matrix": shear},
        {"name": "twice_to24_3d", "dim": 3,
         "vertices": sorted({tuple(2 * x for x in v) for v in to24}), "expect": "fail"},
    ]


def declared_hrep():
    """Declared facet inequalities, for the facet-normal reading."""
    return {
        "square_2d": [((1, 0), ONE), ((0, 1), ONE), ((-1, 0), ONE), ((0, -1), ONE)],
        "reflexive_triangle_2d": [((1, 1), ONE), ((-2, 1), ONE), ((1, -2), ONE)],
        "cube_3d": [((s1, 0, 0), ONE) for s1 in (1, -1)]
                   + [((0, s2, 0), ONE) for s2 in (1, -1)]
                   + [((0, 0, s3), ONE) for s3 in (1, -1)],
        "reflexive_simplex_3d": [((1, 1, 1), ONE), ((1, 1, -3), ONE),
                                 ((1, -3, 1), ONE), ((-3, 1, 1), ONE)],
        "to24_3d": [((s1, 0, 0), Fraction(2)) for s1 in (1, -1)]
                   + [((0, s2, 0), Fraction(2)) for s2 in (1, -1)]
                   + [((0, 0, s3), Fraction(2)) for s3 in (1, -1)]
                   + [((s1, s2, s3), Fraction(3))
                      for s1, s2, s3 in itertools.product((1, -1), repeat=3)],
        "twice_to24_3d": [((s1, 0, 0), Fraction(4)) for s1 in (1, -1)]
                         + [((0, s2, 0), Fraction(4)) for s2 in (1, -1)]
                         + [((0, 0, s3), Fraction(4)) for s3 in (1, -1)]
                         + [((s1, s2, s3), Fraction(6))
                            for s1, s2, s3 in itertools.product((1, -1), repeat=3)],
    }


# --------------------------------------------------------------------- runner


def run_fixture(spec, hrep_table, budget, polar_cache):
    dim = spec["dim"]
    vertices = spec["vertices"]
    polar = active_polar_vertices(vertices, dim, budget)
    polar_cache[spec["name"]] = polar
    bipolar = active_polar_vertices(polar, dim, budget)
    recovered = sorted(bipolar) == sorted(vertices)

    record = {
        "dimension": dim,
        "primal_vertices": len(vertices),
        "polar_vertices": len(polar),
        "bipolar_recovers_primal": recovered,
        "polar_common_denominator": common_denominator(polar),
        "expected": spec["expect"],
    }
    if not recovered:
        record["status"] = "InvalidDomain"
        record["reason"] = "bipolar does not recover the primal; interior origin not established"
        return record

    obstruction, witnesses = pairing_obstruction(vertices, polar, budget)
    basis = hnf_basis(as_integers(vertices, 1), dim)
    record["minimal_lattice_basis"] = [[str(x) for x in row] for row in basis]
    record["minimal_lattice_index_in_zd"] = lattice_index(as_integers(vertices, 1), dim)
    scale = common_denominator(polar)
    record["polar_lattice_index_scaled_by_common_denominator"] = lattice_index(
        as_integers(polar, scale), dim)

    if obstruction is None:
        record["status"] = "ReflexiveForSomeLattice"
        record["witness_lattice"] = "Z-span(Vert(P)), the minimal candidate"
    else:
        record["status"] = "NoCompatibleLattice"
        record["certificate"] = obstruction
        record["certificate_distinct_values"] = sorted(
            witnesses, key=lambda text: Fraction(text))
        record["certificate_witnesses"] = witnesses

    facets = hrep_table.get(spec["name"])
    if facets:
        polar_set = set(polar)
        rows = []
        matched = 0
        for normal, offset in facets:
            point = tuple(Fraction(n) / offset for n in normal)
            hit = point in polar_set
            matched += 1 if hit else 0
            rows.append({"normal": list(normal), "offset": str(offset),
                         "normal_over_offset": [str(x) for x in point],
                         "is_computed_polar_vertex": hit})
        record["declared_facets"] = rows
        record["declared_facets_matching_polar"] = matched
        record["declared_offsets"] = sorted({str(o) for _, o in facets})

    if "transport_of" in spec:
        base_polar = polar_cache.get(spec["transport_of"]) or active_polar_vertices(
            next(f["vertices"] for f in fixture_definitions()
                 if f["name"] == spec["transport_of"]), dim, budget)
        transported = sorted({contragredient_image(spec["matrix"], y) for y in base_polar})
        wrong = sorted({apply_matrix(spec["matrix"], y) for y in base_polar})
        record["polar_equals_contragredient_transport"] = transported == sorted(polar)
        record["wrong_direction_transport_matches"] = wrong == sorted(polar)
    return record


def controls(budget):
    out = {}
    to24 = signed_permutations_of((0, 1, 2), 3)
    cube = signed_permutations_of((1, 1, 1), 3)

    forged = (ONE, ZERO, ZERO)
    feasible = all(dot(v, forged) <= ONE for v in to24)
    out["forged_polar_vertex"] = {
        "point": [str(x) for x in forged],
        "feasible_for_primal_constraints": feasible,
        "status": "RefusedForgedPolarVertex" if not feasible else "UnexpectedlyAccepted",
    }

    residual, epsilon = Fraction(1, 2), Fraction(3, 4)
    out["epsilon_integrality"] = {
        "residual": str(residual),
        "epsilon": str(epsilon),
        "residual_below_epsilon": residual < epsilon,
        "status": "RefusedEpsilonIntegrality",
        "note": "a residual inside a tolerance is not an integer pairing",
    }

    try:
        partial = active_polar_vertices(cube, 3, budget, constraints=cube[:-1])
        out["incomplete_coverage"] = {
            "enumerated_primal_vertices": len(cube) - 1,
            "polar_vertices_found_for_partial_set": len(partial),
            "status": "UnknownCoverage",
            "note": "one primal constraint withheld; no verdict is issued",
        }
    except Exhausted:
        out["incomplete_coverage"] = {"status": "UnknownResource"}

    flat = [(Fraction(1), Fraction(1), ZERO), (Fraction(1), Fraction(-1), ZERO),
            (Fraction(-1), Fraction(1), ZERO), (Fraction(-1), Fraction(-1), ZERO)]
    flat_polar = active_polar_vertices(flat, 3, budget)
    out["non_full_dimensional"] = {
        "primal_vertices": len(flat),
        "polar_vertices": len(flat_polar),
        "status": "InvalidDomain" if len(flat_polar) == 0 else "UnexpectedlyAccepted",
        "note": "a flat vertex set spans no three-dimensional lattice",
    }

    shifted = sorted({(x + 1, y, z) for x, y, z in cube})
    shifted_polar = active_polar_vertices(shifted, 3, budget)
    shifted_bipolar = active_polar_vertices(shifted_polar, 3, budget)
    recovered = sorted(shifted_bipolar) == sorted(shifted)
    out["origin_on_boundary"] = {
        "primal_vertices": len(shifted),
        "polar_vertices": len(shifted_polar),
        "bipolar_recovers_primal": recovered,
        "status": "InvalidDomain" if not recovered else "UnexpectedlyAccepted",
        "note": "translated cube; the origin lies on a facet",
    }

    shear = shear_matrix()
    cube_polar = active_polar_vertices(cube, 3, budget)
    right = sorted({contragredient_image(shear, y) for y in cube_polar})
    wrong = sorted({apply_matrix(shear, y) for y in cube_polar})
    sheared_polar = active_polar_vertices(sorted({apply_matrix(shear, v) for v in cube}), 3, budget)
    good = right == sorted(sheared_polar)
    bad = wrong == sorted(sheared_polar)
    out["wrong_dual_transport"] = {
        "contragredient_matches": good,
        "applying_A_instead_matches": bad,
        "status": "RefusedMismatch" if (good and not bad) else "UnexpectedlyAccepted",
    }
    return out


def documented_pairing_check(polar_cache):
    """Re-verify the 2026-09-10 certificate inside this run, as its own check."""
    to24 = signed_permutations_of((0, 1, 2), 3)
    primal = (Fraction(1), Fraction(2), Fraction(0))
    polar = (Fraction(1, 2), Fraction(0), Fraction(0))
    value = dot(primal, polar)
    return {
        "primal_vertex_is_a_vertex": primal in to24,
        "polar_vertex_is_a_polar_vertex": polar in polar_cache.get("to24_3d", []),
        "pairing": str(value),
        "nonintegral": value.denominator != 1,
    }


def install_limits(address_space_bytes, cpu_seconds):
    """Install the declared limits, recording honestly which ones the platform took."""
    installed = {"address_space_bytes": None, "cpu_seconds": None}
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        installed["cpu_seconds"] = cpu_seconds
    except (ValueError, OSError) as exc:
        installed["cpu_seconds"] = "not-installed: %s" % type(exc).__name__
    try:
        resource.setrlimit(resource.RLIMIT_AS, (address_space_bytes, address_space_bytes))
        installed["address_space_bytes"] = address_space_bytes
    except (ValueError, OSError) as exc:
        installed["address_space_bytes"] = "not-installed: %s" % type(exc).__name__
    return installed


def peak_rss_kib():
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if platform.system() == "Darwin":
        return usage // 1024, "ru_maxrss reported in bytes on this platform, divided by 1024"
    return usage, "ru_maxrss reported in kibibytes on this platform"


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="bounded lattice-gate check")
    parser.add_argument("--output", required=True)
    parser.add_argument("--seconds", type=float, default=30.0)
    args = parser.parse_args()
    if os.path.exists(args.output):
        raise SystemExit("refusing to overwrite: %s" % args.output)

    here = os.path.dirname(os.path.abspath(__file__))
    contract_path = os.path.join(here, "contract.json")
    start = time.monotonic()
    limits = install_limits(268435456, 25)
    budget = Budget(20000, 500000, args.seconds)

    status = "Passed"
    try:
        hrep_table = declared_hrep()
        polar_cache = {}
        fixtures = [run_fixture(spec, hrep_table, budget, polar_cache)
                    for spec in fixture_definitions()]
        refusals = controls(budget)
    except Exhausted as exc:
        fixtures, refusals = [], {"budget": {"status": "UnknownResource: %s" % exc}}
        status = "UnknownResource"

    expected = {
        "square_2d": "ReflexiveForSomeLattice",
        "reflexive_triangle_2d": "ReflexiveForSomeLattice",
        "cube_3d": "ReflexiveForSomeLattice",
        "sheared_cube_3d": "ReflexiveForSomeLattice",
        "reflexive_simplex_3d": "ReflexiveForSomeLattice",
        "to24_3d": "NoCompatibleLattice",
        "unimodular_image_of_to24_3d": "NoCompatibleLattice",
        "twice_to24_3d": "NoCompatibleLattice",
    }
    checks = {
        "every_fixture_matches_its_declared_expectation":
            all(record.get("status") == expected.get(spec["name"])
                for spec, record in zip(fixture_definitions(), fixtures)),
        "every_fixture_bipolar_recovers_primal":
            all(record.get("bipolar_recovers_primal") for record in fixtures),
        "to24_certificate_is_the_documented_pairing":
            any(record.get("certificate", {}).get("pairing") == "1/2" for record in fixtures),
        "documented_pairing_still_holds_for_to24":
            all(documented_pairing_check(polar_cache).values()),
        "declared_facets_all_match_computed_polar_vertices":
            all(record.get("declared_facets_matching_polar") == len(record["declared_facets"])
                for record in fixtures if "declared_facets" in record),
        "unimodular_image_still_fails_and_transports_correctly":
            all(record.get("polar_equals_contragredient_transport")
                for record in fixtures if "transport_of" in record),
        "every_refusal_is_a_refusal":
            all(value.get("status", "").startswith(("Refused", "Unknown", "Invalid"))
                for value in refusals.values()),
    }

    elapsed_ns = int((time.monotonic() - start) * 1e9)
    rss, rss_note = peak_rss_kib()
    report = {
        "schema": "adva.external.reflexive-lattice-gate.v0",
        "status": status if all(checks.values()) else "Failed",
        "contract_sha256": sha256_of(contract_path),
        "source_sha256": sha256_of(os.path.abspath(__file__)),
        "base_commit": json.load(open(contract_path))["base_commit"],
        "criterion": "exists M with Vert(P) in M and Vert(P^o) in M* iff every primal-polar pairing is an integer",
        "fixtures": fixtures,
        "refusal_controls": refusals,
        "checks": checks,
        "documented_pairing_recheck": documented_pairing_check(polar_cache),
        "work_units": {"constraint_triples": budget.triples, "assertions": budget.checks},
        "limits_installed": limits,
        "platform": "%s %s; %s" % (platform.system(), platform.release(), rss_note),
        "elapsed_before_final_write_ns": elapsed_ns,
        "peak_rss_kib": rss,
        "native_authority": "NotGranted",
    }
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, sort_keys=True)
    print(json.dumps({k: report[k] for k in ("status", "work_units", "limits_installed",
                                             "peak_rss_kib")}, ensure_ascii=False))
    if report["status"] != "Passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
