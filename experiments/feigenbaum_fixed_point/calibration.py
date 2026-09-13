#!/usr/bin/env python3
"""Solve the Feigenbaum-Cvitanovic fixed point and read both constants off it.

Frozen contract: contract.json in this directory (Research 0129 section 3).

Method. Work with even functions g(x) = G(x^2), G(0) = 1, and the doubling
operator T[G](y) = A G((G(y/A^2))^2) with A = 1/G(1). This is
g(x) = -alpha g(g(x/alpha)) with alpha = -1/g(1). Truncate G at a declared degree,
solve G = T[G] by Newton with a finite-difference Jacobian, and read alpha = -1/g(1).
The linearisation of T restricted to the normalised subspace g(0) = 1 has delta as
its dominant eigenvalue, obtained by power iteration. Every reported number comes
from decimal arithmetic at the declared precision; binary floating point is never
used for a reported value, and no acceleration of any kind is applied.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import time
from decimal import Decimal, getcontext

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
OBJ = CONTRACT["objects"]
getcontext().prec = OBJ["decimal_precision"]

ASSERTIONS = {"n": 0}


def check(condition, message):
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)


# ------------------------------------------------- truncated series algebra ----

def zeros(n):
    return [Decimal(0)] * (n + 1)


def multiply(a, b, n):
    out = zeros(n)
    for i, ai in enumerate(a):
        if not ai:
            continue
        for j in range(0, n + 1 - i):
            if b[j]:
                out[i + j] += ai * b[j]
    return out


def rescale(a, s, n):
    out = zeros(n)
    power = Decimal(1)
    for i in range(n + 1):
        out[i] = a[i] * power
        power *= s
    return out


def compose(f, g, n):
    """f(g(y)) for an arbitrary constant term: f(c + H) with H = g - c."""
    c = g[0]
    h = list(g)
    h[0] = Decimal(0)
    out = zeros(n)
    power = zeros(n)
    power[0] = Decimal(1)
    for k in range(n + 1):
        if f[k]:
            for i in range(n + 1):
                if power[i]:
                    out[i] += f[k] * power[i]
        if k < n:
            power = [c * power[i] for i in range(n + 1)]
            mh = multiply(power, h, n)
            power = [power[i] + mh[i] for i in range(n + 1)]
    return out


def doubling(g, n):
    """T[G](y) = A G((G(y/A^2))^2) with A = 1/G(1)."""
    a = Decimal(1) / sum(g)
    inner = rescale(g, Decimal(1) / (a * a), n)
    return [a * v for v in compose(g, multiply(inner, inner, n), n)]


def normalised(g, n):
    """T followed by division by its constant term, so the image has g(0) = 1."""
    image = doubling(g, n)
    c = image[0]
    return [v / c for v in image]


# ------------------------------------------------------------- the solver ----

def newton(degree, guess, iterations_max):
    a = list(guess) + [Decimal(0)] * (degree + 1 - len(guess))
    a[0] = Decimal(1)
    step = Decimal(10) ** OBJ["finite_difference_exponent"]
    achieved = None
    used = 0
    for used in range(1, iterations_max + 1):
        image = normalised(a, degree)
        f = [a[j] - image[j] for j in range(degree + 1)]
        f[0] = Decimal(0)
        achieved = max(abs(v) for v in f)
        if achieved < Decimal(10) ** (-(getcontext().prec - 10)):
            return a, used, achieved
        jacobian = [[Decimal(0)] * (degree + 1) for _ in range(degree + 1)]
        for k in range(1, degree + 1):
            perturbed = list(a)
            perturbed[k] += step
            image_p = normalised(perturbed, degree)
            for j in range(1, degree + 1):
                jacobian[j][k] = ((perturbed[j] - image_p[j]) - f[j]) / step
        augmented = [row[:] + [-f[i]] for i, row in enumerate(jacobian)]
        for column in range(1, degree + 1):
            pivot = max(range(column, degree + 1), key=lambda r: abs(augmented[r][column]))
            augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
            value = augmented[column][column]
            for row in range(column + 1, degree + 1):
                factor = augmented[row][column] / value
                if factor:
                    for c in range(column, degree + 2):
                        augmented[row][c] -= factor * augmented[column][c]
        delta = [Decimal(0)] * (degree + 1)
        for row in range(degree, 0, -1):
            total = augmented[row][degree + 1]
            for c in range(row + 1, degree + 1):
                total -= augmented[row][c] * delta[c]
            delta[row] = total / augmented[row][row]
        for k in range(1, degree + 1):
            a[k] += delta[k]
    return a, used, achieved


def truncation_residual(g, degree, extra=8):
    """Largest coefficient of the fixed-point equation beyond the truncation."""
    m = degree + extra
    extended = g + [Decimal(0)] * (m - degree)
    a = Decimal(1) / sum(extended)
    image = doubling(extended, m)
    del a
    return max(abs(extended[j] - image[j]) for j in range(degree + 1, m + 1))


def jacobian_normalised(g, degree):
    step = Decimal(10) ** OBJ["finite_difference_exponent"]
    base = normalised(g, degree)
    out = [[Decimal(0)] * (degree + 1) for _ in range(degree + 1)]
    for k in range(1, degree + 1):
        perturbed = list(g)
        perturbed[k] += step
        image_p = normalised(perturbed, degree)
        for j in range(1, degree + 1):
            out[j][k] = (image_p[j] - base[j]) / step
    return out


def jacobian_of_unnormalised_operator(g, degree):
    """The control: the operator before normalisation does not preserve g(0) = 1,
    so its linearisation has an extra direction with a different eigenvalue."""
    step = Decimal(10) ** OBJ["finite_difference_exponent"]
    base = doubling(g, degree)
    out = [[Decimal(0)] * (degree + 1) for _ in range(degree + 1)]
    for k in range(0, degree + 1):
        perturbed = list(g)
        perturbed[k] += step
        image_p = doubling(perturbed, degree)
        for j in range(0, degree + 1):
            out[j][k] = (image_p[j] - base[j]) / step
    return out


def dominant_eigenvalue(matrix, degree, iterations_max):
    v = [Decimal(1) if i % 2 else Decimal("-1") for i in range(degree + 1)]
    previous = None
    for _ in range(iterations_max):
        w = [sum(matrix[i][j] * v[j] for j in range(degree + 1)) for i in range(degree + 1)]
        norm = max(abs(x) for x in w)
        if norm == 0:
            return None
        v = [x / norm for x in w]
        if previous is not None and abs(norm - previous) < Decimal(10) ** (-(getcontext().prec - 25)):
            return norm
        previous = norm
    return previous


def agreeing(value, published, width=45):
    mine = f"{value:.{width}f}"
    count = 0
    for a, b in zip(mine, published):
        if a != b:
            break
        count += 1
    return count, mine


# ------------------------------------------------------------------ main ----

def main():
    started = time.monotonic()
    guess = [Decimal(1), Decimal("-1.52763"), Decimal("0.104815"), Decimal("0.0267057")]
    table = []
    for degree in OBJ["truncation_degrees"]:
        a, used, achieved = newton(degree, guess, OBJ["newton_iterations_max"])
        check(achieved is not None and achieved < Decimal("1e-40"), f"newton did not converge at degree {degree}")
        alpha = -Decimal(1) / sum(a)
        residual = truncation_residual(a, degree)
        delta = abs(dominant_eigenvalue(jacobian_normalised(a, degree), degree,
                                        OBJ["power_iterations_max"]))
        alpha_chars, alpha_string = agreeing(alpha, OBJ["published_alpha_prefix"])
        delta_chars, delta_string = agreeing(delta, OBJ["published_delta_prefix"])
        reciprocal_chars, reciprocal_string = agreeing(
            Decimal(1) / alpha, OBJ["published_reciprocal_alpha_prefix"])
        table.append({
            "degree": degree,
            "newton_iterations": used,
            "newton_residual": f"{achieved:.2E}",
            "truncation_residual_beyond_the_degree": f"{residual:.2E}",
            "alpha": f"{alpha:.35f}",
            "delta": f"{delta:.35f}",
            "g_1": f"{sum(a):.35f}",
            "g_1_times_alpha": f"{sum(a) * alpha:.30f}",
            "alpha_agreement_characters": alpha_chars,
            "delta_agreement_characters": delta_chars,
            "reciprocal_agreement_characters": reciprocal_chars,
            "alpha_agreement_string": alpha_string,
            "delta_agreement_string": delta_string,
            "reciprocal_agreement_string": reciprocal_string,
            "coefficients_a1_a2_a3": [f"{a[1]:.30f}", f"{a[2]:.30f}", f"{a[3]:.30f}"],
        })

    last = table[-1]
    # the control: the unrestricted linearisation has a different dominant eigenvalue
    a_last, _, _ = newton(OBJ["truncation_degrees"][-1], guess, OBJ["newton_iterations_max"])
    unrestricted = abs(dominant_eigenvalue(
        jacobian_of_unnormalised_operator(a_last, OBJ["truncation_degrees"][-1]),
        OBJ["truncation_degrees"][-1], OBJ["power_iterations_max"]))

    evidence = {
        "schema": "adva.external.feigenbaum-fixed-point.v0",
        "version": 0,
        "checker_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "contract": "experiments/feigenbaum_fixed_point/contract.json",
        "equation": {
            "implemented": "G(y) = A G((G(y/A^2))^2) with A = 1/G(1)",
            "in_the_x_variable": "g(x) = -alpha g(g(x/alpha)) with alpha = -1/g(1)",
            "normalisation": "g(0) = 1, g even; alpha is then fixed by g(1)",
            "delta": "dominant eigenvalue of the linearised operator, restricted to the normalised subspace g(0) = 1",
        },
        "precision": {"decimal_precision": OBJ["decimal_precision"],
                      "acceleration_applied": False,
                      "binary_floating_point_in_reported_values": False},
        "published_source": {
            "citation": OBJ["published_source"],
            "delta_prefix": OBJ["published_delta_prefix"],
            "alpha_prefix": OBJ["published_alpha_prefix"],
            "reciprocal_alpha_prefix": OBJ["published_reciprocal_alpha_prefix"],
            "bytes_retained_here": False,
        },
        "table": table,
        "unnormalised_operator_control": {
            "dominant_eigenvalue": f"{unrestricted:.25f}",
            "differs_from_delta": abs(unrestricted - Decimal(last["delta"])) > Decimal("0.5"),
            "why": "the operator before normalisation does not preserve g(0) = 1, so its linearisation carries an extra direction whose eigenvalue is not delta; this is the mistake that the first version of this round made, and it is kept as a control",
        },
        "honesty": {
            "no_acceleration_used": True,
            "verified_error_bound_claimed": False,
            "truncation_residual_is_a_numerical_indicator": True,
            "published_digits_are_a_target_not_a_derivation": True,
            "algebraic_status_claimed": False,
            "digits_beyond_the_counted_agreement_claimed": False,
        },
        "sibling": {
            "contract": OBJ["sibling_contract"],
            "note": "the earlier cascade round reached 14 agreeing characters with an accelerator; this round reaches more without one",
        },
    }

    # the two recorded targets must agree with each other: this is the check that
    # catches a mis-transcribed published prefix before it is used
    reciprocal_of_alpha_prefix = Decimal(1) / Decimal(OBJ["published_alpha_prefix"])
    prefix_consistency, _ = agreeing(reciprocal_of_alpha_prefix,
                                     OBJ["published_reciprocal_alpha_prefix"], width=45)
    evidence["published_target_consistency"] = {
        "reciprocal_of_the_alpha_prefix": f"{reciprocal_of_alpha_prefix:.45f}",
        "recorded_reciprocal_prefix": OBJ["published_reciprocal_alpha_prefix"],
        "agreement_characters": prefix_consistency,
        "note": "the alpha and reciprocal targets are checked against each other, so a mis-transcribed digit in either is caught here rather than compared against the computation",
    }

    checks = {
        "published_targets_are_mutually_consistent": prefix_consistency >= 30,
        "newton_converged_at_every_degree": all(
            Decimal(row["newton_residual"]) < Decimal("1e-40") for row in table),
        "truncation_residual_decreases_with_the_degree": all(
            Decimal(table[i + 1]["truncation_residual_beyond_the_degree"])
            < Decimal(table[i]["truncation_residual_beyond_the_degree"])
            for i in range(len(table) - 1)),
        "agreement_grows_with_the_degree": all(
            table[i + 1]["delta_agreement_characters"] >= table[i]["delta_agreement_characters"]
            for i in range(len(table) - 1)),
        "delta_agrees_at_least_twenty_five_characters": last["delta_agreement_characters"] >= 25,
        "alpha_agrees_at_least_twenty_five_characters": last["alpha_agreement_characters"] >= 25,
        "reciprocal_relation_holds": abs(Decimal(last["g_1_times_alpha"]) + Decimal(1)) < Decimal("1e-25"),
        "unnormalised_operator_control_differs": evidence["unnormalised_operator_control"]["differs_from_delta"],
        "within_assertion_budget": ASSERTIONS["n"] <= OBJ["max_assertions"],
        "within_time_budget": (time.monotonic() - started) <= CONTRACT["budget"]["wall_seconds"],
    }
    evidence["checks"] = checks
    evidence["status"] = "ExternalExactPass" if all(checks.values()) else "Residual"
    evidence["cost"] = {
        "wall_seconds_before_serialization": round(time.monotonic() - started, 3),
        "assertions": ASSERTIONS["n"],
        "subprocesses": 0,
    }
    (HERE / "evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n",
                                        encoding="utf-8")
    print(json.dumps({k: evidence[k] for k in ("status", "checks", "cost")}, indent=1))
    for row in table:
        print(f"  N={row['degree']:2d} residual={row['truncation_residual_beyond_the_degree']}"
              f"  alpha agree={row['alpha_agreement_characters']:2d}"
              f"  delta agree={row['delta_agreement_characters']:2d}")
    print("delta:", last["delta"], "| alpha:", last["alpha"])
    print("unnormalised-operator control:", evidence["unnormalised_operator_control"]["dominant_eigenvalue"])
    return 0 if evidence["status"] == "ExternalExactPass" else 1


if __name__ == "__main__":
    sys.exit(main())
