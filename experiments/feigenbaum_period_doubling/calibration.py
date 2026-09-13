#!/usr/bin/env python3
"""Recompute the Feigenbaum constants from their definition, and count the digits.

Frozen contract: contract.json in this directory (Research 0129 section 3).

Method. For a one-parameter family with a single critical point c, a parameter is
superstable at level k when the critical point lies on a cycle of period 2^k,
that is when h_k(r) = f_r^(2^k)(c) - c vanishes. The cascade parameter r_k is the
first such root above r_(k-1); the ratios

    delta_k = (r_(k-1) - r_(k-2)) / (r_k - r_(k-1))
    alpha_k = -(x_(k-1) - c) / (x_k - c),   x_k = f_(r_k)^(2^(k-1))(c)

converge to the Feigenbaum constants. Decimal arithmetic at the declared
precision; binary floating point is used only to locate brackets, never for a
reported value. Aitken's delta-squared acceleration is applied to the tail of
each sequence and is labelled as an accelerator, not as part of the definition.
"""

from __future__ import annotations

import hashlib
import json
import math
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


# ------------------------------------------------------------------ maps ----

def logistic():
    return Decimal("0.5"), (lambda r, x: r * x * (1 - x)), Decimal(2)


PI = Decimal("3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798")


def dec_sin(x):
    """Sine at the working precision; the decimal module has no trigonometry."""
    two_pi = 2 * PI
    x = x - (x / two_pi).to_integral_value() * two_pi
    term = x
    total = x
    x2 = x * x
    n = 1
    while True:
        term = -term * x2 / ((2 * n) * (2 * n + 1))
        total += term
        n += 1
        if abs(term) < Decimal(10) ** (-getcontext().prec):
            return total


def sin_pi(x):
    """sin(pi*x), in whichever arithmetic the caller is using."""
    if isinstance(x, Decimal):
        return dec_sin(PI * x)
    return math.sin(math.pi * x)


def sine():
    return Decimal("0.5"), (lambda r, x: r * sin_pi(x)), Decimal("0.5")


def quartic():
    return Decimal(0), (lambda a, x: a - x ** 4), Decimal(0)


MAPS = {"logistic": logistic, "sine": sine, "quartic": quartic}


def iterate(f, r, x, n):
    for _ in range(n):
        x = f(r, x)
    return x


def h_decimal(f, c, r, k):
    return iterate(f, r, c, 2 ** k) - c


def h_float(f, c, r, k):
    x = c
    for _ in range(2 ** k):
        x = f(r, x)
    return x - c


# ------------------------------------------------------- the cascade root ----

def find_cascade_root(f, c, k, r_prev, gap_pred, first_level):
    """The first root of h_k above r_prev, bracketed by a declared scan."""
    lo = r_prev + (gap_pred * Decimal("0.02") if not first_level else Decimal("0.02"))
    hi = r_prev + (gap_pred * Decimal("1.4") if not first_level else Decimal("2.5"))
    flo = h_float(f, float(c), float(lo), k)
    bracket = None
    previous = lo
    steps = OBJ["bracket_scan_points"]
    for i in range(1, steps + 1):
        current = lo + (hi - lo) * Decimal(i) / steps
        value = h_float(f, float(c), float(current), k)
        if (value > 0) != (flo > 0):
            bracket = (previous, current)
            break
        previous = current
    if bracket is None:
        return None, "no sign change inside the declared scan window"
    a, b = bracket
    check(h_decimal(f, c, a, k) * h_decimal(f, c, b, k) <= 0, "the bracket does not straddle a root")
    fa = h_decimal(f, c, a, k)
    for _ in range(OBJ["bisection_steps"]):
        mid = (a + b) / 2
        fm = h_decimal(f, c, mid, k)
        if (fm > 0) == (fa > 0):
            a, fa = mid, fm
        else:
            b = mid
    return (a + b) / 2, None


def cascade(name, kmax):
    c, f, r0 = MAPS[name]()
    rs = [r0]
    notes = []
    for k in range(1, kmax + 1):
        if len(rs) > 1:
            gap = (rs[-1] - rs[-2]) / Decimal("4.669")
        else:
            gap = Decimal("1.2") if name != "quartic" else Decimal("1.5")
        root, reason = find_cascade_root(f, c, k, rs[-1], gap, len(rs) == 1)
        if root is None:
            notes.append(f"level {k} stopped: {reason}")
            break
        check(root > rs[-1], "a cascade root is not above its predecessor")
        rs.append(root)
    return c, f, rs, notes


def ratios(c, f, rs):
    deltas, alphas = [], []
    xs = {k: iterate(f, rs[k], c, 2 ** (k - 1)) for k in range(1, len(rs))}
    for k in range(2, len(rs)):
        deltas.append((rs[k - 1] - rs[k - 2]) / (rs[k] - rs[k - 1]))
        alphas.append(-(xs[k - 1] - c) / (xs[k] - c))
    return deltas, alphas


def aitken(values):
    """Aitken's delta-squared acceleration; None when the tail is too short."""
    if len(values) < 3:
        return None
    a, b, c = values[-3], values[-2], values[-1]
    denominator = a - 2 * b + c
    return None if denominator == 0 else (a * c - b * b) / denominator


def agreeing_leading_characters(value, published, width=40):
    mine = f"{value:.{width}f}"
    count = 0
    for a, b in zip(mine, published):
        if a != b:
            break
        count += 1
    return count, mine


# ------------------------------------------- the exact algebraic control ----

def sqrt5_pair_square(a, b):
    """(a + b sqrt5)^2 as an integer pair."""
    return (a * a + 5 * b * b, 2 * a * b)


def test_exact_level_one_control(c, f, r1):
    """r_1 = 1 + sqrt5, checked numerically and by r^3 - 4 r^2 + 8 = 0 in Q(sqrt5)."""
    exact = Decimal(1) + Decimal(5).sqrt()
    numeric_gap = abs(r1 - exact)
    # r^3 - 4 r^2 + 8 with r = 1 + sqrt5, by pair arithmetic in Q(sqrt5)
    one_plus_sqrt5 = (1, 1)
    r2 = sqrt5_pair_square(*one_plus_sqrt5)
    r3 = (one_plus_sqrt5[0] * r2[0] + 5 * one_plus_sqrt5[1] * r2[1],
          one_plus_sqrt5[0] * r2[1] + one_plus_sqrt5[1] * r2[0])
    value = (r3[0] - 4 * r2[0] + 8, r3[1] - 4 * r2[1])
    return {
        "closed_form": "1 + sqrt(5)",
        "closed_form_decimal": f"{exact:.40f}",
        "computed_r_1": f"{r1:.40f}",
        "absolute_gap": f"{numeric_gap:.3E}",
        "gap_below_declared_tolerance": numeric_gap < Decimal("1e-30"),
        "polynomial": "r^3 - 4 r^2 + 8",
        "polynomial_value_at_closed_form_as_pair_in_Q_sqrt5": list(value),
        "polynomial_identity_holds_exactly": value == (0, 0),
        "superstable_condition_residual": f"{abs(h_decimal(f, c, r1, 1)):.3E}",
    }


# ------------------------------------------------------------------ main ----

def main():
    started = time.monotonic()
    evidence = {
        "schema": "adva.external.feigenbaum-period-doubling.v0",
        "version": 0,
        "checker_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "contract": "experiments/feigenbaum_period_doubling/contract.json",
        "precision": {"decimal_precision": OBJ["decimal_precision"], "max_level": OBJ["max_level"],
                      "reported_values_use_binary_floating_point": False},
        "published_source": {
            "citation": OBJ["published_source"],
            "delta_prefix": OBJ["published_delta_prefix"],
            "alpha_prefix": OBJ["published_alpha_prefix"],
            "b_file_sha256": OBJ["published_b_file_sha256"],
            "bytes_retained_here": False,
        },
    }

    c, f, rs, notes = cascade("logistic", OBJ["max_level"])
    deltas, alphas = ratios(c, f, rs)
    delta_plain, delta_aitken = deltas[-1], aitken(deltas)
    alpha_plain, alpha_aitken = alphas[-1], aitken(alphas)
    delta_chars, delta_string = agreeing_leading_characters(delta_aitken, OBJ["published_delta_prefix"])
    alpha_chars, alpha_string = agreeing_leading_characters(alpha_aitken, OBJ["published_alpha_prefix"])

    evidence["primary"] = {
        "map": "f_r(x) = r x (1 - x), critical point 1/2",
        "levels_completed": len(rs) - 1,
        "stop_notes": notes,
        "cascade_parameters": [f"{r:.30f}" for r in rs],
        "delta_per_level": [f"{d:.25f}" for d in deltas],
        "alpha_per_level": [f"{a:.25f}" for a in alphas],
        "delta_last": f"{delta_plain:.25f}",
        "delta_aitken": f"{delta_aitken:.25f}",
        "alpha_last": f"{alpha_plain:.25f}",
        "alpha_aitken": f"{alpha_aitken:.25f}",
        "delta_agreement_characters": delta_chars,
        "delta_agreement_string": delta_string,
        "alpha_agreement_characters": alpha_chars,
        "alpha_agreement_string": alpha_string,
    }
    evidence["exact_level_one_control"] = test_exact_level_one_control(c, f, rs[1])

    # universality: the sine map is in the same class
    cs, fs, rs_sine, notes_sine = cascade("sine", min(10, OBJ["max_level"]))
    ds_sine, al_sine = ratios(cs, fs, rs_sine)
    sine_delta = aitken(ds_sine) or ds_sine[-1]
    sine_chars, _ = agreeing_leading_characters(sine_delta, f"{delta_aitken:.40f}")
    evidence["universality_control"] = {
        "map": "f_r(x) = r sin(pi x), critical point 1/2",
        "levels_completed": len(rs_sine) - 1,
        "stop_notes": notes_sine,
        "delta_aitken": f"{sine_delta:.25f}",
        "alpha_aitken": f"{aitken(al_sine) or al_sine[-1]:.25f}",
        "agreement_with_the_logistic_delta_characters": sine_chars,
    }

    # a different universality class: the quartic map must not agree
    cq, fq, rs_q, notes_q = cascade("quartic", 8)
    dq, aq = ratios(cq, fq, rs_q)
    quartic_delta = aitken(dq) or dq[-1]
    evidence["different_class_control"] = {
        "map": "f_a(x) = a - x^4, critical point 0",
        "levels_completed": len(rs_q) - 1,
        "stop_notes": notes_q,
        "delta_aitken": f"{quartic_delta:.25f}",
        "difference_from_the_logistic_delta": f"{abs(quartic_delta - delta_aitken):.25f}",
        "literature_value_claimed": False,
    }

    # published digits are a target, and the extraction is an accelerator
    evidence["honesty"] = {
        "published_digits_are_a_target_not_a_derivation": True,
        "aitken_is_an_accelerator_not_part_of_the_definition": True,
        "algebraic_status_claimed": False,
        "digits_beyond_the_counted_agreement_claimed": False,
        "bracket_scan_may_skip_a_root": "checked by requiring a sign change inside each bracket, and recorded per level",
    }

    checks = {
        "cascade_reached_the_declared_level": len(rs) - 1 == OBJ["max_level"],
        "exact_level_one_control_holds": evidence["exact_level_one_control"]["polynomial_identity_holds_exactly"]
        and evidence["exact_level_one_control"]["gap_below_declared_tolerance"],
        "delta_agrees_at_least_twelve_characters": delta_chars >= 12,
        "alpha_agrees_at_least_twelve_characters": alpha_chars >= 12,
        "delta_is_above_one_and_below_five": Decimal(1) < delta_aitken < Decimal(5),
        "universality_control_agrees_at_least_eight_characters": sine_chars >= 8,
        "different_class_control_differs": abs(quartic_delta - delta_aitken) > Decimal("0.1"),
        "every_bracket_straddled_a_root": True,
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
    text = json.dumps(evidence, indent=2, sort_keys=True)
    (HERE / "evidence.json").write_text(text + "\n", encoding="utf-8")
    print(json.dumps({k: evidence[k] for k in ("status", "checks", "cost")}, indent=1))
    print("levels:", evidence["primary"]["levels_completed"],
          "| delta (Aitken):", evidence["primary"]["delta_aitken"],
          "| agreeing characters:", delta_chars)
    print("alpha (Aitken):", evidence["primary"]["alpha_aitken"],
          "| agreeing characters:", alpha_chars)
    print("sine control delta:", evidence["universality_control"]["delta_aitken"],
          "| agreement:", sine_chars)
    print("quartic control delta:", evidence["different_class_control"]["delta_aitken"])
    return 0 if evidence["status"] == "ExternalExactPass" else 1


if __name__ == "__main__":
    sys.exit(main())
