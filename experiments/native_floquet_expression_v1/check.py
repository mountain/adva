#!/usr/bin/env python3
"""Original exact-arithmetic calibration, NOT an Adva semantic checker.

Codex (OpenAI), contributed under Unknown v0.3 through Mingli Yuan's
authorized account proxy. Dependencies: Python standard library only.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import platform
import resource
import signal
import time


def add(p, q):
    return tuple((p[i] if i < len(p) else Q(0)) +
                 (q[i] if i < len(q) else Q(0))
                 for i in range(max(len(p), len(q))))


def mul(p, q):
    out = [Q(0)] * (len(p) + len(q) - 1)
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            out[i + j] += x * y
    return tuple(out)


def scale(a, p):
    return tuple(a * x for x in p)


def compose(p, q):
    out = (Q(0),)
    for c in reversed(p):
        out = add(mul(out, q), (c,))
    while len(out) > 1 and out[-1] == 0:
        out = out[:-1]
    return out


def evaluate(p, x):
    result = Q(0)
    for c in reversed(p):
        result = result * x + c
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("wall limit")))
    signal.alarm(20)
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_AS, (256 << 20, 256 << 20))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1 << 20, 1 << 20))
    started = time.monotonic()
    contract_path = Path(__file__).with_name("contract.json")
    contract = json.loads(contract_path.read_text())
    s = tuple(Q(x) for x in contract["fixture"]["reference_path"])
    a = tuple(Q(x) for x in contract["fixture"]["a"])
    q = tuple(Q(x) for x in contract["fixture"]["q"])
    assert len(s) == 13 and len(a) == len(q) == 12 and s[0] == s[12]
    checks = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    def step(m, x):
        h = x - s[m]
        return s[m + 1] + a[m] * h + q[m] * h * h

    check("reference_is_exact_periodic_orbit", all(step(m, s[m]) == s[m + 1] for m in range(12)))
    annual = (Q(0), Q(1))
    for m in range(12):
        annual = compose((Q(0), a[m], q[m]), annual)
    expected = (Q(0), Q(3, 8), Q(1, 8), Q(1, 64), Q(1, 512))
    check("full_annual_polynomial_equals_independent_expansion", annual == expected)
    product = Q(1)
    for value in a:
        product *= value
    check("first_degree_observation_composes", annual[1] == product == Q(3, 8))
    check("nonlinear_terms_are_retained", len(annual) == 5 and annual[2] != 0)
    reverse = compose((Q(0), a[0], q[0]), (Q(0), a[1], q[1]))
    check("same_multiplier_does_not_identify_order", reverse[1] == annual[1] and reverse != annual)
    check("reversed_quadratic_coefficient", reverse[2] == Q(17, 128))
    for u, v, du, dv in ((2, 3, 1, -1), (Q(1, 2), Q(3, 4), Q(1, 8), Q(1, 4))):
        exact = (u + du) * (v + dv) - u * v
        check("finite_product_identity_" + str(u), exact == u * dv + v * du + du * dv)
        check("dropped_cross_term_rejected_" + str(u), exact != u * dv + v * du)
    rows = []
    for h in (Q(-1, 2), Q(-1, 4), Q(0), Q(1, 4), Q(1, 2)):
        x = s[0] + h
        for m in range(12):
            x = step(m, x)
        exact = x - s[12]
        check("nested_evaluation_" + str(h), exact == evaluate(annual, h))
        rows.append({"h": str(h), "exact_return": str(exact), "first_degree": str(product*h),
                     "nonlinear_residual": str(exact-product*h)})
    # For |h|<=1/2, |R(h)| <= (1/8+1/128+1/2048)|h|^2.
    remainder_bound = Q(1, 8) + Q(1, 128) + Q(1, 2048)
    contraction_bound = product + remainder_bound * Q(1, 2)
    check("finite_amplitude_contraction_bound", contraction_bound == Q(1809, 4096) < 1)
    for row in rows:
        h, residual = Q(row["h"]), Q(row["nonlinear_residual"])
        check("remainder_bound_sample_" + str(h), abs(residual) <= remainder_bound*h*h)
    offset = Q(1, 8)
    defects = [step(m, s[m] + offset) - (s[m + 1] + offset) for m in range(12)]
    check("periodic_reference_not_necessarily_solution", defects == [Q(-31, 512), Q(-15, 512)] + [Q(0)]*10)
    check("zero_anomaly_has_nonzero_defect", step(0, s[0]+offset)-(s[1]+offset) != 0)
    payload = {
        "status": "PassedExternalArithmeticCalibration",
        "native_semantic_certificate": "NotConstructed",
        "native_source_occurrence_history_identity": "NotAssignedByThisChecker",
        "scope": "One fixed original scalar twelve-phase polynomial fixture; not meteorology or a general Floquet implementation",
        "python": platform.python_version(),
        "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "contract_sha256": hashlib.sha256(contract_path.read_bytes()).hexdigest(),
        "checks": checks,
        "check_count": len(checks),
        "annual_coefficients_ascending": [str(x) for x in annual],
        "reverse_coefficients_ascending": [str(x) for x in reverse],
        "annual_first_degree_multiplier": str(product),
        "nonlinear_remainder_bound_for_abs_h_le_half": str(remainder_bound),
        "absolute_return_bound_divided_by_abs_h": str(contraction_bound),
        "shifted_periodic_reference_defects": [str(x) for x in defects],
        "finite_perturbations": rows,
        "elapsed_seconds": time.monotonic()-started,
        "max_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    with args.output.open("x") as stream:
        json.dump(payload, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": payload["status"], "checks": len(checks), "annual_first_degree_multiplier": str(product)}))


if __name__ == "__main__":
    main()
