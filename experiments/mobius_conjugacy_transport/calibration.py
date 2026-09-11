"""Exact finite Möbius/conjugacy transport calibration.

Authored by ChatGPT (OpenAI). Submitted through Mingli Yuan's GitHub
account (mountain) as an authorized proxy. Neither attribution nor account
authorization is evidence of correctness.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import resource
import time


INF = "inf"


class LimitReached(RuntimeError):
    pass


class Fuel:
    def __init__(self, cap: int, deadline: float):
        self.cap = cap
        self.deadline = deadline
        self.used = 0

    def tick(self, amount: int = 1) -> None:
        if amount < 0 or self.used + amount > self.cap or time.monotonic() >= self.deadline:
            raise LimitReached
        self.used += amount


def det(m, p):
    a, b, c, d = m
    return (a * d - b * c) % p


def inv_scalar(x, p):
    if x % p == 0:
        raise ValueError("zero has no inverse")
    return pow(x, p - 2, p)


def canonical(m, p):
    m = tuple(x % p for x in m)
    first = next((x for x in m if x), None)
    if first is None:
        raise ValueError("zero matrix")
    scale = inv_scalar(first, p)
    return tuple((scale * x) % p for x in m)


def mmul(m, n, p):
    a, b, c, d = m
    e, f, g, h = n
    return canonical((a * e + b * g, a * f + b * h,
                      c * e + d * g, c * f + d * h), p)


def minv(m, p):
    a, b, c, d = m
    if det(m, p) == 0:
        raise ValueError("singular matrix")
    return canonical((d, -b, -c, a), p)


def square_nonzero(x, p):
    return x % p != 0 and pow(x % p, (p - 1) // 2, p) == 1


def enumerate_psl_by_square_determinant(p, fuel):
    classes = set()
    candidates = 0
    for m in product(range(p), repeat=4):
        fuel.tick()
        candidates += 1
        if square_nonzero(det(m, p), p):
            classes.add(canonical(m, p))
    return sorted(classes), candidates


def enumerate_psl_by_sl_quotient(p, fuel):
    classes = set()
    candidates = 0
    for m in product(range(p), repeat=4):
        fuel.tick()
        candidates += 1
        if det(m, p) == 1:
            classes.add(canonical(m, p))
    return sorted(classes), candidates


def act(m, x, p):
    a, b, c, d = m
    if x == INF:
        return INF if c % p == 0 else (a * inv_scalar(c, p)) % p
    denominator = (c * x + d) % p
    if denominator == 0:
        return INF
    return ((a * x + b) * inv_scalar(denominator, p)) % p


def points(p):
    return tuple(range(p)) + (INF,)


def perm(m, p):
    return tuple(act(m, x, p) for x in points(p))


def perm_compose(left, right, domain):
    lookup = dict(zip(domain, left))
    return tuple(lookup[y] for y in right)


def observer_key(m, probes, p):
    return tuple(act(m, x, p) for x in probes)


def poly_add(*terms):
    result = defaultdict(int)
    for term in terms:
        for monomial, coefficient in term.items():
            result[monomial] += coefficient
    return {m: c for m, c in result.items() if c}


def poly_scale(coefficient, term):
    return {m: coefficient * c for m, c in term.items() if coefficient * c}


def poly_mul(left, right):
    result = defaultdict(int)
    for (lu, lv), lc in left.items():
        for (ru, rv), rc in right.items():
            result[(lu + ru, lv + rv)] += lc * rc
    return {m: c for m, c in result.items() if c}


def critical_line_image():
    # w=u+iv, z=(2-w)/(w-1).  Re(z)=1/2 is equivalent to
    # 2 Re((2-w) conjugate(w-1)) - |w-1|^2 = 0.
    one = {(0, 0): 1}
    u = {(1, 0): 1}
    v = {(0, 1): 1}
    nr = poly_add(poly_scale(2, one), poly_scale(-1, u))
    ni = poly_scale(-1, v)
    dr = poly_add(u, poly_scale(-1, one))
    di = v
    numerator_real = poly_add(poly_mul(nr, dr), poly_mul(ni, di))
    denominator_norm = poly_add(poly_mul(dr, dr), poly_mul(di, di))
    raw = poly_add(poly_scale(2, numerator_real), poly_scale(-1, denominator_norm))
    normalized = poly_scale(-1, raw)

    circle = poly_add(
        poly_mul(poly_add(poly_scale(3, u), poly_scale(-4, one)),
                 poly_add(poly_scale(3, u), poly_scale(-4, one))),
        poly_mul(poly_scale(3, v), poly_scale(3, v)),
        poly_scale(-1, one),
    )
    expected = {(2, 0): 3, (1, 0): -8, (0, 0): 5, (0, 2): 3}
    if normalized != expected or circle != poly_scale(3, expected):
        raise AssertionError("critical-line polynomial transport")
    return {
        "source_predicate": "Re(z)=1/2",
        "inverse": "z=(2-w)/(w-1)",
        "cleared_equation": "3*u^2-8*u+5+3*v^2=0",
        "circle_equation": "(3*u-4)^2+(3*v)^2=1",
        "center": ["4/3", "0"],
        "radius": "1/3",
        "derived_coefficients": {
            f"u^{i}*v^{j}": coefficient
            for (i, j), coefficient in sorted(normalized.items())
        },
        "circle_multiple": 3,
        "status": "ExactAlgebraicTransport",
        "riemann_hypothesis_status": "NotTested",
    }


def first_separating_coordinate_size(group, p, fuel):
    domain = points(p)
    rows = []
    for size in range(len(domain) + 1):
        separated_at_size = False
        for probes in combinations(domain, size):
            fuel.tick()
            fibres = defaultdict(int)
            for g in group:
                fuel.tick()
                fibres[observer_key(g, probes, p)] += 1
            histogram = dict(sorted(Counter(fibres.values()).items()))
            separated = len(fibres) == len(group)
            rows.append({
                "probes": list(probes),
                "observations": len(fibres),
                "fibre_histogram": histogram,
                "separated": separated,
            })
            separated_at_size |= separated
        if separated_at_size:
            return size, rows
    raise AssertionError("finite full-coordinate observer did not separate")


def field_run(p, h_integer, fuel):
    group_a, candidates_a = enumerate_psl_by_square_determinant(p, fuel)
    group_b, candidates_b = enumerate_psl_by_sl_quotient(p, fuel)
    group_set = set(group_a)
    h = canonical(h_integer, p)
    h_inv = minv(h, p)
    identity = canonical((1, 0, 0, 1), p)
    projective_points = points(p)

    assertions = []

    def check(label, condition):
        fuel.tick()
        if not condition:
            raise AssertionError(f"F_{p}: {label}")
        assertions.append(label)

    expected_order = p * (p * p - 1) // 2
    check("independent PSL enumerations agree", group_a == group_b)
    check("PSL order", len(group_a) == expected_order)

    perms = {g: perm(g, p) for g in group_a}
    check("projective action is faithful", len(set(perms.values())) == len(group_a))
    check("each action is a permutation", all(set(q) == set(projective_points) for q in perms.values()))

    conjugated = {g: mmul(mmul(h, g, p), h_inv, p) for g in group_a}
    check("conjugation stays in PSL", set(conjugated.values()) <= group_set)
    check("conjugation fixes identity", conjugated[identity] == identity)
    check("conjugation is injective", len(set(conjugated.values())) == len(group_a))

    product_checks = 0
    left_homomorphism_matches = 0
    left_values = {g: mmul(h, g, p) for g in group_a}
    for g in group_a:
        for k in group_a:
            fuel.tick()
            gk = mmul(g, k, p)
            check_action = perm_compose(perms[g], perms[k], projective_points)
            if perms[gk] != check_action:
                raise AssertionError(f"F_{p}: action product law")
            if conjugated[gk] != mmul(conjugated[g], conjugated[k], p):
                raise AssertionError(f"F_{p}: conjugation product law")
            if mmul(h, gk, p) == mmul(left_values[g], left_values[k], p):
                left_homomorphism_matches += 1
            product_checks += 1
    check("all action and conjugation products", product_checks == len(group_a) ** 2)
    check("left multiplication preserves no ordered product pair", left_homomorphism_matches == 0)

    h_in_group = h in group_set
    left_in_carrier = sum(value in group_set for value in left_values.values())
    if h_in_group:
        check("left translate is set-valued but not identity-preserving",
              left_in_carrier == len(group_a) and left_values[identity] != identity)
        left_status = "NotRepresentation"
    else:
        check("left translate leaves the group carrier",
              left_in_carrier == 0 and left_values[identity] not in group_set)
        left_status = "InvalidCodomain"

    covariance_checks = 0
    untransported_probe_value_mismatches = 0
    probes = (0, 1, INF)
    transported_probes = tuple(act(h, x, p) for x in probes)
    receipt_matches = 0
    for g in group_a:
        old = observer_key(g, probes, p)
        new = observer_key(conjugated[g], transported_probes, p)
        decoded = tuple(act(h_inv, y, p) for y in new)
        if decoded == old:
            receipt_matches += 1
        if observer_key(conjugated[g], probes, p) != old:
            untransported_probe_value_mismatches += 1
        for x in projective_points:
            fuel.tick()
            if act(conjugated[g], act(h, x, p), p) != act(h, act(g, x, p), p):
                raise AssertionError(f"F_{p}: observer covariance")
            covariance_checks += 1
    check("all observer covariance squares", covariance_checks == len(group_a) * len(projective_points))
    check("transported observer receipts match", receipt_matches == len(group_a))
    check("unchanged probes and values do not generally match", untransported_probe_value_mismatches > 0)

    minimum, coordinate_rows = first_separating_coordinate_size(group_a, p, fuel)
    check("three projective point images are minimally separating", minimum == 3)

    affine_domain = tuple(range(p))
    defined_pairs = [(x, act(h, x, p)) for x in affine_domain if act(h, x, p) != INF]
    pole_inputs = [x for x in affine_domain if act(h, x, p) == INF]
    finite_outputs = [y for _, y in defined_pairs]
    missing_finite_outputs = sorted(set(range(p)) - set(finite_outputs))
    naive_local_injective = len(finite_outputs) == len(set(finite_outputs))
    affine_status = "UnknownCoverage"
    check("affine deletion looks locally injective", naive_local_injective)
    check("affine deletion loses pole and infinity coverage",
          pole_inputs == [p - 1] and missing_finite_outputs == [1] and
          len(defined_pairs) == p - 1 and affine_status == "UnknownCoverage")

    return {
        "field": p,
        "psl_order": len(group_a),
        "group": [list(g) for g in group_a],
        "candidate_matrices": candidates_a + candidates_b,
        "H": list(h),
        "H_inverse": list(h_inv),
        "H_determinant": det(h, p),
        "H_in_PSL": h_in_group,
        "left_transport": {
            "status": left_status,
            "identity_image": list(left_values[identity]),
            "outputs_in_carrier": left_in_carrier,
            "product_pairs_checked": product_checks,
            "homomorphism_matches": left_homomorphism_matches,
        },
        "conjugation": {
            "status": "Transported",
            "outputs_in_carrier": len(conjugated),
            "product_pairs_checked": product_checks,
            "observer_covariance_checks": covariance_checks,
        },
        "observer_receipt": {
            "probes": list(probes),
            "transported_probes": list(transported_probes),
            "decoded_matches": receipt_matches,
            "unchanged_probe_value_mismatches": untransported_probe_value_mismatches,
            "minimum_coordinate_count": minimum,
            "coordinate_search": coordinate_rows,
        },
        "affine_chart_control": {
            "status": affine_status,
            "defined_pairs": defined_pairs,
            "pole_inputs": pole_inputs,
            "missing_finite_outputs": missing_finite_outputs,
            "naive_local_injective": naive_local_injective,
        },
        "assertions": assertions,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", default=str(Path(__file__).with_name("contract.json")))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    start = time.perf_counter_ns()
    contract_bytes = Path(args.contract).read_bytes()
    contract = json.loads(contract_bytes)
    budget = contract["budgets"]
    resource.setrlimit(resource.RLIMIT_CPU, (budget["cpu_seconds"], budget["cpu_seconds"]))
    resource.setrlimit(resource.RLIMIT_AS, (budget["address_space_bytes"], budget["address_space_bytes"]))
    resource.setrlimit(resource.RLIMIT_FSIZE, (budget["output_bytes"], budget["output_bytes"]))
    fuel = Fuel(budget["work_units"], time.monotonic() + budget["wall_seconds"])
    report = {
        "schema": contract["schema"],
        "contract_sha256": hashlib.sha256(contract_bytes).hexdigest(),
        "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "native_authority": "NotGranted",
        "attempt": 1,
        "correction_replays": 1,
        "prior_attempt": {
            "path": "experiments/mobius_conjugacy_transport/evidence-initial-invalid.json",
            "status": "InvalidEvidence",
            "reason": "The critical-line coefficient check compared a literal with itself. Group and observer results were not contradicted, but the combined report was not admissible.",
            "checker_sha256": "7bd690e05a211ed210c9a488d02409a5fb152d274b071109ac8b58a71f0193d1"
        },
    }
    try:
        construction_start = time.perf_counter_ns()
        runs = [field_run(p, (1, 2, 1, 1), fuel) for p in contract["objects"]["fields"]]
        construction_and_check_ns = time.perf_counter_ns() - construction_start

        fuel.tick(2)
        critical_line_transport = critical_line_image()

        payload = {
            "runs": runs,
            "critical_line_transport": critical_line_transport,
            "summary": {
                "F5": "H is in PSL(2,F_5): left translation stays in the set but is not a representation",
                "F7": "H is outside PSL(2,F_7): left translation leaves the carrier; conjugation still normalizes it",
                "projective_boundary": "including infinity makes H total; affine deletion is UnknownCoverage",
            },
        }
        serialization_start = time.perf_counter_ns()
        compact = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        replayed = json.loads(compact)
        if json.dumps(replayed, sort_keys=True, separators=(",", ":")) != compact:
            raise AssertionError("serialization replay")
        serialization_ns = time.perf_counter_ns() - serialization_start
        report.update({
            "status": "Passed",
            "evidence": payload,
            "costs_ns": {
                "construction_search_verification": construction_and_check_ns,
                "serialization_replay": serialization_ns,
            },
        })
    except LimitReached:
        report["status"] = "UnknownResource"

    report.update({
        "work_units": fuel.used,
        "elapsed_before_final_write_ns": time.perf_counter_ns() - start,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "limits_installed": {
            "cpu_seconds": budget["cpu_seconds"],
            "address_space_bytes": budget["address_space_bytes"],
            "file_size_bytes": budget["output_bytes"],
        },
        "platform": "Linux; ru_maxrss is KiB",
    })
    encoded = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
    if len(encoded) > budget["output_bytes"]:
        raise LimitReached("serialized report exceeds output budget")
    with open(args.output, "xb") as handle:
        handle.write(encoded)
    print(json.dumps({k: v for k, v in report.items() if k != "evidence"}, sort_keys=True))


if __name__ == "__main__":
    main()
