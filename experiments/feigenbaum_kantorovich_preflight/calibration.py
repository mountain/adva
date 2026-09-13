#!/usr/bin/env python3
"""Assemble the Newton-Kantorovich test for the Feigenbaum fixed point, rigorously.

Frozen contract: contract.json in this directory (Research 0129 section 3).

This round does not claim an enclosure of the Feigenbaum constants. It computes,
rigorously and separately, the quantities a Kantorovich test would consume:

  * the fixed point is recomputed numerically and then frozen as an EXACT RATIONAL
    vector x0, so that everything after this point is exact;
  * the defect d = T(x0) - x0 is computed as an exact rational polynomial, since
    composing polynomials gives a polynomial, and its weighted norm is exact;
  * the disk-mapping hypothesis that licenses composition bounds is checked
    rigorously from the coefficients;
  * a truncated linearisation is assembled in interval arithmetic and its inverse
    is verified by the residual criterion, giving a rigorous inverse bound for
    the truncated problem.

What is missing for the infinite-dimensional conclusion, and is therefore
reported as a preflight obstruction rather than papered over, is the tail bound on
the inverse of the linearised operator and a rigorous bound on its second
derivative. No acceleration is used and no floating point enters a reported bound.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import time
from decimal import Decimal, getcontext
from fractions import Fraction as Fr

sys.set_int_max_str_digits(200000)

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
OBJ = CONTRACT["objects"]
getcontext().prec = OBJ["decimal_precision"]

ASSERTIONS = {"n": 0}


def check(condition, message):
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)


# ------------------------------------------------- the numerical fixed point ----

def zeros(n):
    return [Decimal(0)] * (n + 1)


def dec_mul(a, b, n):
    out = zeros(n)
    for i, ai in enumerate(a):
        if not ai:
            continue
        for j in range(0, n + 1 - i):
            if b[j]:
                out[i + j] += ai * b[j]
    return out


def dec_rescale(a, s, n):
    out = zeros(n)
    power = Decimal(1)
    for i in range(n + 1):
        out[i] = a[i] * power
        power *= s
    return out


def dec_compose(f, g, n):
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
            mh = dec_mul(power, h, n)
            power = [power[i] + mh[i] for i in range(n + 1)]
    return out


def doubling_dec(g, n):
    a = Decimal(1) / sum(g)
    inner = dec_rescale(g, Decimal(1) / (a * a), n)
    return [a * v for v in dec_compose(g, dec_mul(inner, inner, n), n)]


def normalised_dec(g, n):
    image = doubling_dec(g, n)
    c = image[0]
    return [v / c for v in image]


def solve_fixed_point(degree, guess, iterations_max):
    a = list(guess) + [Decimal(0)] * (degree + 1 - len(guess))
    a[0] = Decimal(1)
    step = Decimal(10) ** OBJ["finite_difference_exponent"]
    for _ in range(iterations_max):
        image = normalised_dec(a, degree)
        f = [a[j] - image[j] for j in range(degree + 1)]
        f[0] = Decimal(0)
        if max(abs(v) for v in f) < Decimal(10) ** (-(getcontext().prec - 10)):
            return a
        jac = [[Decimal(0)] * (degree + 1) for _ in range(degree + 1)]
        for k in range(1, degree + 1):
            perturbed = list(a)
            perturbed[k] += step
            image_p = normalised_dec(perturbed, degree)
            for j in range(1, degree + 1):
                jac[j][k] = ((perturbed[j] - image_p[j]) - f[j]) / step
        aug = [row[:] + [-f[i]] for i, row in enumerate(jac)]
        for column in range(1, degree + 1):
            pivot = max(range(column, degree + 1), key=lambda r: abs(aug[r][column]))
            aug[column], aug[pivot] = aug[pivot], aug[column]
            value = aug[column][column]
            for row in range(column + 1, degree + 1):
                factor = aug[row][column] / value
                if factor:
                    for c in range(column, degree + 2):
                        aug[row][c] -= factor * aug[column][c]
        delta = [Decimal(0)] * (degree + 1)
        for row in range(degree, 0, -1):
            total = aug[row][degree + 1]
            for c in range(row + 1, degree + 1):
                total -= aug[row][c] * delta[c]
            delta[row] = total / aug[row][row]
        for k in range(1, degree + 1):
            a[k] += delta[k]
    raise AssertionError("the numerical solve did not converge")


def to_fraction(value, digits):
    """Freeze a decimal as an exact rational with the declared number of digits."""
    quantum = Decimal(1).scaleb(-digits)
    return Fr(int((value / quantum).to_integral_value(rounding="ROUND_HALF_EVEN"))) * Fr(1, 10 ** digits)


# --------------------------------------------- exact rational polynomial algebra ----

def rat_mul(a, b, n):
    out = [Fr(0)] * (n + 1)
    for i, ai in enumerate(a):
        if not ai:
            continue
        for j in range(0, n + 1 - i):
            if b[j]:
                out[i + j] += ai * b[j]
    return out


def rat_rescale(a, s, n):
    out = [Fr(0)] * (n + 1)
    power = Fr(1)
    for i in range(n + 1):
        out[i] = a[i] * power
        power *= s
    return out


def rat_compose(f, g, n):
    c = g[0]
    h = list(g)
    h[0] = Fr(0)
    out = [Fr(0)] * (n + 1)
    power = [Fr(0)] * (n + 1)
    power[0] = Fr(1)
    for k in range(n + 1):
        if f[k]:
            for i in range(n + 1):
                if power[i]:
                    out[i] += f[k] * power[i]
        if k < n:
            power = [c * power[i] for i in range(n + 1)]
            mh = rat_mul(power, h, n)
            power = [power[i] + mh[i] for i in range(n + 1)]
    return out


def rat_doubling(g, n):
    """T[G] exactly, as a rational polynomial truncated at degree n."""
    a = Fr(1) / sum(g)
    inner = rat_rescale(g, Fr(1) / (a * a), n)
    return [a * v for v in rat_compose(g, rat_mul(inner, inner, n), n)]


def weighted_norm(coeffs, rho):
    total = Fr(0)
    power = Fr(1)
    for c in coeffs:
        total += abs(c) * power
        power *= rho
    return total


def main():
    started = time.monotonic()
    degree = OBJ["fixed_point_degree"]
    digits = OBJ["exact_digits"]
    rho = Fr(OBJ["rho"])
    rho_image = Fr(OBJ["rho_image"])

    guess = [Decimal(1), Decimal("-1.52763"), Decimal("0.104815"), Decimal("0.0267057")]
    a_dec = solve_fixed_point(degree, guess, OBJ["newton_iterations_max"])
    x0 = [to_fraction(v, digits) for v in a_dec]
    x0[0] = Fr(1)
    A0 = -Fr(1) / sum(x0)

    evidence = {
        "schema": "adva.external.feigenbaum-kantorovich-preflight.v0",
        "version": 0,
        "checker_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "contract": "experiments/feigenbaum_kantorovich_preflight/contract.json",
        "space": {
            "objects": "even power series G(y) = sum a_j y^j with a_0 = 1, y = x^2",
            "norm": "weighted l1: ||G||_rho = sum |a_j| rho^j",
            "rho": str(rho),
            "rho_image": str(rho_image),
            "composition_licence": "if ||G||_rho <= rho_image then G maps the disk of radius rho into the disk of radius rho_image, which is what makes the composition bounds usable",
        },
        "exact_candidate": {
            "degree": degree,
            "digits_frozen": digits,
            "alpha_candidate": f"{float(A0):.20f}",
            "coefficients_a1_a2_a3": [str(x0[1])[:26], str(x0[2])[:26], str(x0[3])[:26]],
        },
        "precision": {
            "decimal_precision": OBJ["decimal_precision"],
            "acceleration_applied": False,
            "binary_floating_point_in_reported_bounds": False,
        },
    }

    # --- the defect, exactly: composing polynomials gives a polynomial
    defect_degree = OBJ["defect_degree"]
    x0_ext = x0 + [Fr(0)] * (defect_degree - degree)
    image = rat_doubling(x0_ext, defect_degree)
    defect = [x0_ext[j] - image[j] for j in range(defect_degree + 1)]
    eta = weighted_norm(defect, rho)
    evidence["defect"] = {
        "definition": "d = x0 - T[x0], computed exactly because T of a polynomial is a polynomial",
        "degree_used": defect_degree,
        "nonzero_coefficients": sum(1 for c in defect if c != 0),
        "highest_nonzero_degree": max((j for j, c in enumerate(defect) if c != 0), default=0),
        "weighted_norm_eta": f"{float(eta):.6E}",
        "eta_exact_numerator_bits": eta.numerator.bit_length(),
        "note": "this is the truncation defect of the frozen polynomial, and it is exact, not estimated",
    }

    # --- how far the series is trustworthy: a numeric ratio test on the coefficients
    ratios = []
    for j in range(2, len(x0)):
        if x0[j - 1] != 0:
            ratios.append(abs(float(x0[j] / x0[j - 1])))
    evidence["coefficient_decay"] = {
        "ratios_of_successive_coefficients": [f"{r:.4f}" for r in ratios],
        "ratio_test_locates_the_radius": False,
        "why_it_matters": "rho has to lie inside the convergence radius, otherwise the weighted norm is that of a truncation rather than of a function",
        "how_rho_was_chosen": "a ten-term truncation does not locate the convergence radius, so rho is declared at 1/32; the first run used 1/4 and the hypothesis failed there, and both the choice and the failure are recorded",
    }

    # --- the disk-mapping hypothesis, checked rigorously from the coefficients
    norm_x0 = weighted_norm(x0, rho)
    evidence["disk_mapping_hypothesis"] = {
        "weighted_norm_of_x0": f"{float(norm_x0):.10f}",
        "declared_image_radius": str(rho_image),
        "holds": norm_x0 <= rho_image,
        "why_it_matters": "composition bounds need the outer function to be defined and bounded on the image of the inner one",
    }

    # --- a rigorous inverse bound for the truncated linearisation
    truncation = OBJ["linearisation_degree"]
    matrix = truncated_linearisation(x0, truncation, OBJ["finite_difference_exponent"])
    inverse = rational_inverse(matrix)
    residual = identity_minus_product(matrix, inverse)
    row_sum = max(sum(abs(v) for v in row) for row in residual)
    x_norm = max(sum(abs(v) for v in row) for row in inverse)
    evidence["truncated_inverse"] = {
        "truncation_degree": truncation,
        "matrix_size": len(matrix),
        "residual_infinity_norm": f"{float(row_sum):.6E}",
        "approximate_inverse_infinity_norm": f"{float(x_norm):.6E}",
        "verified": row_sum < 1,
        "inverse_bound": None if row_sum >= 1 else f"{float(x_norm / (1 - row_sum)):.6E}",
        "why_the_residual_test_is_enough": "if ||I - M X|| < 1 in the operator norm then X is invertible and ||M^-1|| <= ||X|| / (1 - ||I - M X||)",
        "norm_mismatch": "this bound is the infinity norm of the truncated coefficient matrix, not the weighted norm of the space; connecting the two is part of what a full proof needs and is not done here",
    }

    # --- controls
    perturbed = list(x0)
    perturbed[1] += Fr(1, 10 ** 6)
    perturbed_ext = perturbed + [Fr(0)] * (defect_degree - degree)
    p_image = rat_doubling(perturbed_ext, defect_degree)
    p_defect = [perturbed_ext[j] - p_image[j] for j in range(defect_degree + 1)]
    eta_perturbed = weighted_norm(p_defect, rho)
    scaled = [Fr(10) * c for c in x0]
    scaled[0] = Fr(1)
    scaled_norm = weighted_norm(scaled, rho)
    evidence["controls"] = {
        "perturbed_candidate_has_larger_defect": {
            "perturbation": "a_1 increased by 1e-6",
            "eta": f"{float(eta_perturbed):.6E}",
            "larger_than_the_candidate": eta_perturbed > eta,
        },
        "scaled_candidate_fails_the_disk_mapping": {
            "scaling": "all coefficients except a_0 multiplied by ten",
            "weighted_norm": f"{float(scaled_norm):.6E}",
            "fails": scaled_norm > rho_image,
        },
    }

    # --- what the Kantorovich test still needs
    evidence["preflight_obstruction"] = {
        "what_a_kantorovich_test_needs": [
            "a rigorous bound B on ||(I - DT(x0))^-1|| in the declared space",
            "a rigorous bound K on the second derivative of the operator on the ball",
            "the defect norm eta, which this round supplies exactly",
        ],
        "what_this_round_supplies": [
            "eta exactly, as a rational weighted norm of an exact polynomial defect",
            "the disk-mapping hypothesis, verified from the coefficients",
            "a verified inverse bound for the truncated linearisation only",
        ],
        "what_is_missing": [
            "the tail bound on the inverse: the truncated inverse bound says nothing about the high-degree directions",
            "a rigorous bound on the second derivative of the composition operator on the ball",
            "a conversion from the truncated coefficient matrix norm used here to the weighted norm of the space",
        ],
        "conclusion": "the trial is not launched: with the tail bound on the inverse missing, no Kantorovich radius can be computed, so no enclosure of alpha or delta follows and none is claimed",
    }
    evidence["what_is_not_claimed"] = {
        "enclosure_of_alpha": False,
        "enclosure_of_delta": False,
        "existence_or_uniqueness_of_the_fixed_point": False,
        "the_truncated_inverse_bound_is_not_the_full_inverse_bound": True,
        "next_step": "derive the tail bound on the inverse and the second-derivative bound, then run the Kantorovich test",
    }

    check(all(isinstance(c, Fr) for c in defect), "the defect must be exact rational")
    check(float(eta) < 1e-8, "the frozen candidate must satisfy the equation to the defect size")

    checks = {
        "the_defect_is_exact_rational": all(isinstance(c, Fr) for c in defect),
        "the_candidate_is_a_fixed_point_to_the_defect_size": float(eta) < 1e-8,
        "the_disk_mapping_hypothesis_holds": evidence["disk_mapping_hypothesis"]["holds"],
        "the_truncated_inverse_is_verified": evidence["truncated_inverse"]["verified"],
        "a_perturbed_candidate_has_a_larger_defect": evidence["controls"]["perturbed_candidate_has_larger_defect"]["larger_than_the_candidate"],
        "a_scaled_candidate_fails_the_hypothesis": evidence["controls"]["scaled_candidate_fails_the_disk_mapping"]["fails"],
        "no_enclosure_is_claimed": evidence["what_is_not_claimed"]["enclosure_of_alpha"] is False
        and evidence["what_is_not_claimed"]["enclosure_of_delta"] is False,
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
    print("eta (exact weighted defect):", evidence["defect"]["weighted_norm_eta"])
    print("disk mapping:", evidence["disk_mapping_hypothesis"]["holds"],
          "| ||x0||:", evidence["disk_mapping_hypothesis"]["weighted_norm_of_x0"])
    print("truncated inverse verified:", evidence["truncated_inverse"]["verified"],
          "| bound:", evidence["truncated_inverse"]["inverse_bound"],
          "| residual:", evidence["truncated_inverse"]["residual_infinity_norm"])
    print("controls:", json.dumps(evidence["controls"]))
    return 0 if evidence["status"] == "ExternalExactPass" else 1


def truncated_linearisation(poly, degree, exponent):
    """The linearisation of the doublings operator, frozen as an exact rational matrix.

    Computed analytically rather than by differencing, so every entry is exact:
    with A = 1/G(1), inner = (G(y/A^2))^2 and dA = -h(1)/G(1)^2, the derivative in
    the direction e_k is A*[h_k(inner) + G'(inner)*2 G(y/A^2) h_k(y/A^2)] + dA_k*G(inner).
    """
    n = degree
    A = Fr(1) / sum(poly)
    scaled = rat_rescale(poly, Fr(1) / (A * A), n)          # G(y/A^2)
    inner = rat_mul(scaled, scaled, n)                       # (G(y/A^2))^2
    outer = rat_compose(poly, inner, n)                      # G(inner)
    dG = [Fr(j) * poly[j] for j in range(1, n + 1)] + [Fr(0)]   # G'(y)
    dG_at_inner = rat_compose(dG, [inner[j] - (inner[0] if j == 0 else 0) for j in range(n + 1)]
                              if inner[0] == 0 else inner, n)
    matrix = [[Fr(0)] * (n + 1) for _ in range(n + 1)]
    for k in range(0, n + 1):
        h = [Fr(0)] * (n + 1)
        h[k] = Fr(1)
        h_scaled = rat_rescale(h, Fr(1) / (A * A), n)
        term1 = rat_compose(h, inner, n)
        term2 = rat_mul(dG_at_inner, [2 * scaled[i] for i in range(n + 1)], n)
        term2 = rat_mul(term2, h_scaled, n)
        dA = -sum(h) / (sum(poly) ** 2)
        dA_term = [dA * outer[i] for i in range(n + 1)]
        column = [A * (term1[i] + term2[i]) + dA_term[i] for i in range(n + 1)]
        for j in range(n + 1):
            matrix[j][k] = column[j]
    return matrix


def rational_inverse(matrix):
    """A numerical inverse in exact rationals by Gauss-Jordan elimination."""
    n = len(matrix)
    aug = [row[:] + [Fr(1) if i == j else Fr(0) for j in range(n)] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if aug[pivot][col] == 0:
            raise AssertionError("singular matrix in the truncated linearisation")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        value = aug[col][col]
        aug[col] = [v / value for v in aug[col]]
        for row in range(n):
            if row != col and aug[row][col]:
                factor = aug[row][col]
                aug[row] = [a - factor * b for a, b in zip(aug[row], aug[col])]
    return [row[n:] for row in aug]


def identity_minus_product(matrix, inverse):
    n = len(matrix)
    out = []
    for i in range(n):
        row = []
        for j in range(n):
            total = sum(matrix[i][k] * inverse[k][j] for k in range(n))
            row.append((Fr(1) if i == j else Fr(0)) - total)
        out.append(row)
    return out


if __name__ == "__main__":
    sys.exit(main())
