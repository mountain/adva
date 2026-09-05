"""External exact Pascal calibration; no Adva semantic authority.

python experiments/knowledge_geometry/acceleration_direction.py witness
python experiments/knowledge_geometry/acceleration_direction.py benchmark
Both commands print JSON. Integer polynomial normalization is the trusted
computational basis, not a proof imported into the Rust or Metamath kernel.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import random
import statistics
import time
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class Poly:
    """Sparse Z-polynomials; monomials are sorted tuples of variable indices."""

    def __init__(self, terms):
        self.terms = {m: c for m, c in terms.items() if c}

    @staticmethod
    def coerce(value):
        return value if isinstance(value, Poly) else Poly({(): value})

    @staticmethod
    def var(index):
        return Poly({(index,): 1})

    def __add__(self, other):
        out = self.terms.copy()
        for m, c in self.coerce(other).terms.items():
            out[m] = out.get(m, 0) + c
        return Poly(out)

    __radd__ = __add__

    def __neg__(self):
        return Poly({m: -c for m, c in self.terms.items()})

    def __sub__(self, other):
        return self + -self.coerce(other)

    def __mul__(self, other):
        out = {}
        for a, c in self.terms.items():
            for b, d in self.coerce(other).terms.items():
                m = tuple(sorted(a + b))
                out[m] = out.get(m, 0) + c * d
        return Poly(out)

    __rmul__ = __mul__

    def record(self):
        return [[list(m), c] for m, c in sorted(self.terms.items())]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def det3(rows):
    a, b, c = rows
    u = cross(b, c)
    return a[0] * u[0] + a[1] * u[1] + a[2] * u[2]


def conic_rows(points):
    return [(x*x, y*y, z*z, x*y, x*z, y*z) for x, y, z in points]


def pascal_points(points):
    lines = [cross(points[i], points[(i + 1) % 6]) for i in range(6)]
    return [cross(lines[i], lines[i + 3]) for i in range(3)]


def incidence(points):
    return det3(pascal_points(points))


def permutation_det(rows):
    """Independent defining determinant; used for proof, never speed baseline."""
    n = len(rows)
    result = 0
    for p in itertools.permutations(range(n)):
        inversions = sum(p[i] > p[j] for i in range(n) for j in range(i+1, n))
        term = (-1) ** inversions
        for i in range(n):
            term = term * rows[i][p[i]]
        result = result + term
    return result


def bareiss(rows):
    """Exact fraction-free elimination with row pivoting and exact divisions."""
    a = [list(row) for row in rows]
    n = len(a)
    previous, sign = 1, 1
    for k in range(n - 1):
        pivot_row = next((i for i in range(k, n) if a[i][k]), None)
        if pivot_row is None:
            return 0
        if pivot_row != k:
            a[k], a[pivot_row] = a[pivot_row], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * pivot - a[i][k] * a[k][j]
                quotient, remainder = divmod(numerator, previous)
                if remainder:
                    raise ArithmeticError("nonexact Bareiss division")
                a[i][j] = quotient
            a[i][k] = 0
        previous = pivot
    return sign * a[-1][-1]


def validate_points(points):
    if not isinstance(points, (list, tuple)) or len(points) != 6:
        raise ValueError("six ordered homogeneous points required")
    for p in points:
        if (not isinstance(p, (list, tuple)) or len(p) != 3
                or any(type(v) is not int for v in p) or not any(p)):
            raise ValueError("nonzero integer triples required; clear rational denominators")


def evaluate(points, route):
    validate_points(points)
    if route == "bareiss":
        return bareiss(conic_rows(points))
    if route == "incidence":
        return incidence(points)
    raise ValueError("unknown route")


def geometric_status(points):
    validate_points(points)
    if any(det3(triple) == 0 for triple in itertools.combinations(points, 3)):
        return "outside-six-distinct-no-three-collinear-scope"
    return "pascal-collinear" if incidence(points) == 0 else "not-on-a-conic"


def lift(matrix):
    (a, b), (c, d) = matrix
    return ((a*a, 2*a*b, b*b), (a*c, a*d+b*c, b*d), (c*c, 2*c*d, d*d))


def matvec(matrix, vector):
    return tuple(sum(a*b for a, b in zip(row, vector)) for row in matrix)


def veronese(p):
    s, t = p
    return (s*s, s*t, t*t)


def polynomial_proof():
    points = [[Poly.var(3*i+j) for j in range(3)] for i in range(6)]
    f = permutation_det(conic_rows(points))
    g = incidence(points)
    if (f - g).terms:
        raise ArithmeticError("Pascal polynomial identity failed")
    # Separate six-variable exact proof of P1 -> conic equivariance and
    # invertibility of the induced plane map. No sampled substitution.
    a, b, c, d, s, t = [Poly.var(i) for i in range(6)]
    m = ((a, b), (c, d))
    left = veronese(matvec(m, (s, t)))
    right = matvec(lift(m), veronese((s, t)))
    residuals = [(x-y).record() for x, y in zip(left, right)]
    determinant_residual = (det3(lift(m)) - (a*d-b*c)*(a*d-b*c)*(a*d-b*c)).record()
    if any(residuals) or determinant_residual:
        raise ArithmeticError("projective lift identity failed")
    return {"variables": [f"{c}{i+1}" for i in range(6) for c in "xyz"],
            "coefficient_domain": "Z", "total_degree": 12,
            "f_terms": len(f.terms), "g_terms": len(g.terms),
            "residual_terms": 0, "common_normal_form": f.record(),
            "normal_form_sha256": digest(f.record()),
            "veronese_equivariance_residuals": residuals,
            "lift_determinant_residual": determinant_residual}


def robust_direction(setup_upper, baseline_lower, reuse_upper, count_lower):
    """Conditional arithmetic rule; caller must justify same-unit bounds."""
    values = [setup_upper, baseline_lower, reuse_upper, count_lower]
    if any(v is None for v in values):
        return {"status": "Unknown", "reason": "missing externally justified cost/workload bounds"}
    if any(type(v) is not int or v < 0 for v in values):
        raise ValueError("nonnegative integer cost ticks and workload count required")
    gap = baseline_lower - reuse_upper
    margin = count_lower * gap - setup_upper
    return {"status": "conditional-cost-improvement" if gap > 0 and margin > 0 else "not-certified",
            "guaranteed_margin_ticks": margin if gap >= 0 else None,
            "minimum_reuses_for_strict_improvement": setup_upper // gap + 1 if gap > 0 else None}


def witness():
    positive = [(i, i*i, 1) for i in range(6)]
    negative = positive[:-1] + [(5, 26, 1)]
    proof = polynomial_proof()
    return {"schema": "adva.external.acceleration-direction.research", "version": 0,
            "name": "acceleration-direction",
            "status": "exact-external-algebraic-witness",
            "native_adva_word": False,
            "question": "Can six-point conic evaluation be replaced by an equivalent incidence circuit, with an explicit amortization gate?",
            "problem_formation": {
                "origin": "user request; external literature-guided proposal",
                "observed_gap": "geometric relevance and numerical examples alone do not certify reusable computation or enterprise value",
                "retained_counterexample": {"points": negative, "F": 288, "G": 288,
                    "refutes": "unconditional collinearity of opposite-side intersections for arbitrary six points"},
                "candidate_directions": ["exact six-by-six Bareiss evaluation", "literature incidence circuit with one polynomial proof", "native proof transport: deferred dependencies"],
                "protected_invariants": ["same ordered input and exact scalar output", "explicit geometric side conditions", "replayable proof and counterexample", "setup and reuse costs retained"],
                "external_need": "Jiamin/customer supplied workload, acceptance criterion, integration cost, recurrence and price",
                "help_first_contribution": "publish exact identity, small checker, counterexample, reusable circuit and decision threshold",
                "falsifiers": ["any nonzero polynomial residual", "any baseline/circuit disagreement", "total admitted workload cost fails strict amortization inequality"],
                "finite_boundary": "18 variables, total degree 12, 720 determinant permutations; fixed six-point circuits"},
            "proof": proof,
            "pascal_example": {"points": positive, "intersection_points": pascal_points(positive),
                "F": evaluate(positive, "bareiss"), "G": evaluate(positive, "incidence"),
                "geometric_status": geometric_status(positive)},
            "decision": {"rule": "N_lower*(C_baseline_lower-C_reuse_upper)>C_setup_upper and C_baseline_lower>C_reuse_upper",
                "enterprise_result": robust_direction(None, None, None, None),
                "cost_scope": "same units; include certification, integration, validation, encoding/decoding, maintenance and recurrence; local timings are not guaranteed bounds"},
            "boundaries": ["classical identity, not a new Pascal theorem", "trusted Python integer/polynomial checker, not a Rust/Metamath proof", "scalar equality authorizes no Adva history or identity quotient", "PGL2 conic action is not arbitrary PGL3 action", "no universal ambient space or commercial optimum assumed"]}


def verify_witness(document):
    # Bind to this exact question and schema, not merely a claimant-supplied
    # residual or digest. Canonical bytes also distinguish bool from int.
    expected = witness()
    if canonical(document) != canonical(expected):
        raise ValueError("witness fails complete question-bound replay")
    return True


def workload():
    rng = random.Random(20260905)
    result = []
    for bits in (16, 64, 256):
        for _ in range(64):
            result.append([[rng.getrandbits(bits)+1 for _ in range(3)] for _ in range(6)])
    for n in range(1, 65):
        # Rational conic, a point at infinity, and nontrivial plane transform.
        p = [veronese((1, 0))] + [veronese((j+n, 1)) for j in range(5)]
        h = ((1, n, 0), (0, 1, n), (0, 0, 1))
        result.append([matvec(h, q) for q in p])
    for n in range(1, 65):
        result.append([(n, n+1, 1)] * 6)
    return result


def benchmark():
    started = time.perf_counter_ns()
    document = witness()
    encoded = canonical(document)
    verify_witness(json.loads(encoded))
    certificate_digest = hashlib.sha256(encoded.encode()).hexdigest()
    setup_ns = time.perf_counter_ns() - started
    tasks = workload()
    rounds, outputs = {"bareiss": [], "incidence": []}, {}
    for round_index in range(7):
        order = ("bareiss", "incidence") if round_index % 2 == 0 else ("incidence", "bareiss")
        for route in order:
            start = time.perf_counter_ns()
            values = [evaluate(p, route) for p in tasks]
            checksum = digest(values)
            rounds[route].append(time.perf_counter_ns() - start)
            outputs[route] = checksum
    if outputs["bareiss"] != outputs["incidence"]:
        raise ArithmeticError("benchmark routes disagree")
    baseline = math.floor(statistics.median(rounds["bareiss"]))
    reuse = math.floor(statistics.median(rounds["incidence"]))
    gap = baseline - reuse
    return {"schema": "adva.external.acceleration-direction.benchmark", "version": 0,
            "name": "acceleration-direction", "python": platform.python_version(),
            "platform": platform.platform(), "workload_sha256": digest(tasks),
            "tasks_per_batch": len(tasks),
            "composition": {"generic_integer_16_64_256_bits": 192, "transformed_conic_with_infinity": 64, "repeated_point_degenerate": 64},
            "input_json_bytes": len(canonical(tasks).encode()),
            "certificate_bytes": len(encoded.encode()), "certificate_sha256": certificate_digest,
            "setup_generate_serialize_replay_hash_ns": setup_ns,
            "batch_ns": rounds, "median_batch_ns": {"bareiss": baseline, "incidence": reuse},
            "median_ratio_baseline_over_incidence": baseline/reuse,
            "answers_sha256": outputs["bareiss"],
            "observed_break_even_batches": setup_ns // gap + 1 if gap > 0 else None,
            "cost_scope": "in-process: route includes input checks, exact evaluation, answer JSON and hash; one-off setup includes polynomial proof generation and replay, certificate JSON/hash. Excludes imports, input generation, disk IO, engineering, integration, customer validation and future maintenance",
            "interpretation": "single-process descriptive timing, neither guaranteed bounds nor global best algorithm comparison; baseline alone pays no new certificate setup",
            "enterprise_decision": "Unknown"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("witness", "benchmark", "verify"))
    parser.add_argument("path", nargs="?")
    args = parser.parse_args()
    if args.command == "verify":
        if not args.path:
            parser.error("verify requires a JSON path")
        verify_witness(json.loads(Path(args.path).read_text()))
        print(canonical({"name": "acceleration-direction", "verified": True}), end="")
    else:
        print(canonical(witness() if args.command == "witness" else benchmark()), end="")


if __name__ == "__main__":
    main()
