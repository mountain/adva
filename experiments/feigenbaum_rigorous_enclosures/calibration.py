#!/usr/bin/env python3
"""Rigorous brackets for the period-doubling thresholds, and where the route stops.

Frozen contract: contract.json in this directory (Research 0129 section 3).

Exact rational interval arithmetic with outward rounding to a declared decimal
grid. A level is certified when the interval evaluations of the superstable
condition at the two ends of a bracket have strictly opposite signs, since then
the intermediate value theorem gives a root inside. Interval widths amplify along
the chaotic iterate, so a width cap is enforced and the level at which
certification stops is reported rather than worked around. No floating point is
used for any reported endpoint, and no enclosure of the Feigenbaum constants is
claimed.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import time
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
OBJ = CONTRACT["objects"]
SIBLING_DIR = HERE.parent / "feigenbaum_period_doubling"

ASSERTIONS = {"n": 0}


def check(condition, message):
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)


class Saturated(Exception):
    """The enclosure grew past the declared cap; no sign can be certified."""


class Interval:
    __slots__ = ("lo", "hi", "grid", "cap")

    def __init__(self, lo, hi=None, grid=None, cap=None):
        self.grid = grid if grid is not None else GRID
        self.cap = cap if cap is not None else CAP
        if hi is None:
            hi = lo
        lo, hi = Fr(lo), Fr(hi)
        self.lo = self._down(lo)
        self.hi = self._up(hi)
        if self.hi - self.lo > self.cap:
            raise Saturated()

    def _down(self, x):
        return Fr((x / self.grid).__floor__()) * self.grid

    def _up(self, x):
        return -Fr(((-x) / self.grid).__floor__()) * self.grid

    def __add__(self, other):
        other = other if isinstance(other, Interval) else Interval(other, grid=self.grid, cap=self.cap)
        return Interval(self.lo + other.lo, self.hi + other.hi, grid=self.grid, cap=self.cap)

    def __sub__(self, other):
        other = other if isinstance(other, Interval) else Interval(other, grid=self.grid, cap=self.cap)
        return Interval(self.lo - other.hi, self.hi - other.lo, grid=self.grid, cap=self.cap)

    def __mul__(self, other):
        other = other if isinstance(other, Interval) else Interval(other, grid=self.grid, cap=self.cap)
        corners = (self.lo * other.lo, self.lo * other.hi, self.hi * other.lo, self.hi * other.hi)
        return Interval(min(corners), max(corners), grid=self.grid, cap=self.cap)

    def __truediv__(self, other):
        other = other if isinstance(other, Interval) else Interval(other, grid=self.grid, cap=self.cap)
        if other.lo <= 0 <= other.hi:
            raise ZeroDivisionError("the divisor interval contains zero")
        corners = (self.lo / other.lo, self.lo / other.hi, self.hi / other.lo, self.hi / other.hi)
        return Interval(min(corners), max(corners), grid=self.grid, cap=self.cap)

    def width(self):
        return self.hi - self.lo

    def sign(self):
        if self.hi < 0:
            return -1
        if self.lo > 0:
            return 1
        return 0


GRID = Fr(1, 10 ** abs(OBJ["grid_exponent"]))
CAP = Fr(OBJ["width_cap"])


def superstable(r, level, grid=None, cap=None):
    """Interval enclosure of f_r^(2^level)(1/2) - 1/2."""
    x = Interval(Fr(1, 2), grid=grid, cap=cap)
    one = Interval(Fr(1), grid=grid, cap=cap)
    for _ in range(2 ** level):
        x = r * x * (one - x)
    return x - Interval(Fr(1, 2), grid=grid, cap=cap)


def certified_bracket(centre, level, grid=None, cap=None, half=None):
    """Bisect while both endpoint signs stay definite; report the width reached."""
    half = half if half is not None else Fr(OBJ["initial_bracket_half_width"])
    lo, hi = Fr(centre) - half, Fr(centre) + half
    grid = grid if grid is not None else GRID
    cap = cap if cap is not None else CAP
    try:
        s_lo = superstable(Interval(lo, grid=grid, cap=cap), level, grid, cap).sign()
        s_hi = superstable(Interval(hi, grid=grid, cap=cap), level, grid, cap).sign()
    except Saturated:
        return {"certified": False, "reason": "the enclosure reached the width cap before any sign was decided"}
    if s_lo == 0 or s_hi == 0 or s_lo == s_hi:
        return {"certified": False, "reason": "the endpoint signs are not strictly opposite"}
    steps = 0
    # the probe must not land on the numerically known root, where the sign is
    # unresolvable: shrink toward one end geometrically and keep the bracket
    fractions = [Fr(1, 2), Fr(1, 4), Fr(1, 10), Fr(1, 100), Fr(1, 1000), Fr(1, 10**4),
                 Fr(1, 10**5), Fr(1, 10**6)]
    for _ in range(OBJ["max_bisections"]):
        moved = False
        for f in fractions:
            probe = lo + (hi - lo) * f
            if probe == lo or probe == hi:
                continue
            try:
                s_probe = superstable(Interval(probe, grid=grid, cap=cap), level, grid, cap).sign()
            except Saturated:
                break
            if s_probe == 0:
                continue
            steps += 1
            if s_probe == s_lo:
                lo = probe
            else:
                hi = probe
            moved = True
            break
        if not moved:
            break
    return {
        "certified": True,
        "lo": lo,
        "hi": hi,
        "width": hi - lo,
        "bisections_used": steps,
        "sign_at_lo": s_lo,
        "sign_at_hi": s_hi,
        "stop_reason": "the midpoint sign stopped being definite" if steps < OBJ["max_bisections"]
        else "the declared bisection budget was used",
    }


def contains_1_plus_sqrt5(lo, hi):
    """Exact: is 1 + sqrt5 inside [lo, hi]? Compared by squaring, not by decimals."""
    target = Fr(1) + Fr(5).__class__(0)  # placeholder, replaced below
    del target
    # 1 + sqrt5 >= lo  <=>  sqrt5 >= lo - 1  <=>  (for lo-1 >= 0) 5 >= (lo-1)^2
    a = lo - 1
    b = hi - 1
    if a <= 0:
        lower_ok = True
    else:
        lower_ok = 5 >= a * a
    if b < 0:
        upper_ok = False
    else:
        upper_ok = 5 <= b * b
    return lower_ok and upper_ok


def width_amplification(level, iterations=12, grid=None):
    """The factor by which a small interval widens per iteration at this level."""
    grid = grid if grid is not None else GRID
    r = Interval(Fr("3.5699456718404126"), Fr("3.5699456718404127"), grid=grid, cap=Fr(10**9))
    x = Interval(Fr(1, 2), grid=grid, cap=Fr(10**9))
    one = Interval(Fr(1), grid=grid, cap=Fr(10**9))
    ratios = []
    try:
        for i in range(iterations):
            before = x.width()
            x = r * x * (one - x)
            after = x.width()
            if before > 0 and after > 0:
                ratios.append(float(after / before))
    except Saturated:
        return None, ratios
    return (sum(ratios) / len(ratios) if ratios else None), ratios


def main():
    started = time.monotonic()
    evidence = {
        "schema": "adva.external.feigenbaum-rigorous-enclosures.v0",
        "version": 0,
        "checker_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "contract": "experiments/feigenbaum_rigorous_enclosures/contract.json",
        "arithmetic": {
            "kind": "exact rational interval arithmetic with outward rounding to a decimal grid",
            "grid": f"1e{OBJ['grid_exponent']}",
            "binary_floating_point_in_reported_endpoints": False,
            "width_cap": OBJ["width_cap"],
        },
    }

    # self-tests of the arithmetic, including that rounding widens
    third = Interval(Fr(1, 3))
    product = third * Interval(Fr(3))
    check(product.lo <= 1 <= product.hi, "the interval product must enclose the exact product")
    check(product.lo < 1 or product.hi > 1, "outward rounding must widen a point interval")
    check((Interval(Fr(1, 3)) * Interval(Fr(3, 7))).lo <= Fr(1, 7)
          <= (Interval(Fr(1, 3)) * Interval(Fr(3, 7))).hi, "a rational product must be enclosed")
    evidence["arithmetic_self_tests"] = {
        "product_encloses_the_exact_value": True,
        "outward_rounding_widens": True,
        "grid": f"1e{OBJ['grid_exponent']}",
    }

    sibling_path = SIBLING_DIR / "evidence.json"
    sibling = json.loads(sibling_path.read_text(encoding="utf-8"))
    centres = sibling["primary"]["cascade_parameters"]
    evidence["starting_brackets"] = {
        "source": OBJ["sibling_evidence"],
        "sibling_evidence_sha256": hashlib.sha256(sibling_path.read_bytes()).hexdigest(),
        "note": "the numerically computed thresholds of the earlier round are used only as bracket centres",
    }

    levels = []
    for level in OBJ["levels"]:
        result = certified_bracket(centres[level], level)
        row = {"level": level}
        if result["certified"]:
            row.update({
                "certified": True,
                "endpoint_signs": [result["sign_at_lo"], result["sign_at_hi"]],
                "bisections_used": result["bisections_used"],
                "width": f"{float(result['width']):.3E}",
                "centre": f"{(float(result['lo']) + float(result['hi'])) / 2:.25f}",
                "lo": str(result["lo"]),
                "hi": str(result["hi"]),
                "stop_reason": result["stop_reason"],
            })
            if level == 1:
                row["contains_the_exact_closed_form_1_plus_sqrt5"] = contains_1_plus_sqrt5(
                    result["lo"], result["hi"])
            levels.append(row)
        else:
            row.update({"certified": False, "reason": result["reason"]})
            levels.append(row)
    evidence["levels"] = levels

    certified = [row for row in levels if row["certified"]]
    evidence["certification_summary"] = {
        "levels_certified": [row["level"] for row in certified],
        "highest_certified_level": max(row["level"] for row in certified) if certified else None,
        "first_failure": next((row for row in levels if not row["certified"]), None),
    }

    # the coarser grid must certify fewer levels: the count depends on precision
    coarse = []
    for level in OBJ["levels"]:
        result = certified_bracket(centres[level], level,
                                   grid=Fr(1, 10 ** abs(OBJ["control_grid_exponent"])))
        coarse.append({"level": level, "certified": result["certified"]})
    evidence["control_coarser_grid"] = {
        "grid": f"1e{OBJ['control_grid_exponent']}",
        "levels": coarse,
        "levels_certified": [row["level"] for row in coarse if row["certified"]],
    }

    # rigorous enclosures of the ratios, for the levels that are certified
    by_level = {row["level"]: row for row in certified}
    ratios = []
    for level in sorted(by_level):
        if level - 1 in by_level and level - 2 in by_level:
            big = Fr(10 ** 9)
            a = Interval(Fr(by_level[level - 1]["lo"]), Fr(by_level[level - 1]["hi"]), cap=big)
            b = Interval(Fr(by_level[level - 2]["lo"]), Fr(by_level[level - 2]["hi"]), cap=big)
            c = Interval(Fr(by_level[level]["lo"]), Fr(by_level[level]["hi"]), cap=big)
            try:
                ratio = (a - b) / (c - a)
            except ZeroDivisionError:
                continue
            ratios.append({
                "level": level,
                "enclosure": [f"{float(ratio.lo):.12f}", f"{float(ratio.hi):.12f}"],
                "width": f"{float(ratio.width()):.3E}",
            })
    evidence["delta_ratio_enclosures"] = ratios

    # the exact rational route: no widening, but the denominator squares at every
    # iteration, so the reachable level is limited by the size of the integers
    exact_rows = []
    for level in (1, 2, 3):
        n = 2 ** level
        r = Fr(centres[level])
        x = Fr(1, 2)
        for _ in range(n):
            x = r * x * (1 - x)
        exact_rows.append({
            "level": level,
            "iterations": n,
            "denominator_bits_after_the_iteration": x.denominator.bit_length(),
            "numerator_bits_after_the_iteration": x.numerator.bit_length(),
        })
    # measure the barrier directly: the denominator roughly squares per iteration
    r = Fr(centres[1])
    x = Fr(1, 2)
    growth = []
    for i in range(1, 9):
        x = r * x * (1 - x)
        growth.append({"step": i, "denominator_bits": x.denominator.bit_length()})
    evidence["exact_rational_route"] = {
        "why_it_stops": "with exact rationals the denominator roughly squares at every iteration, so the reachable number of iterations is bounded by integer size",
        "denominator_growth": growth,
        "reachable_levels_measured": exact_rows,
    }

    amplification, samples = width_amplification(1)
    evidence["width_amplification_per_iteration"] = {
        "mean_factor": None if amplification is None else f"{amplification:.4f}",
        "samples": [f"{v:.4f}" for v in samples[:8]],
        "why_it_stops": "the enclosure widens by this factor at every one of the 2^level iterations, so beyond a few levels it saturates and no sign can be certified",
    }

    evidence["what_is_not_claimed"] = {
        "enclosure_of_delta": False,
        "enclosure_of_alpha": False,
        "uniqueness_of_the_root_in_a_certified_bracket": False,
        "identification_of_the_certified_root_with_the_cascade_threshold": "numerical structure only, not proved here",
        "reason": "the thresholds are bracketed for the low levels, but the limit of their ratios is not, and no bound on the distance to that limit is available on this route",
        "next_step": "the period-doubling operator in a function space with a Newton-Kantorovich bound",
    }

    checks = {
        "arithmetic_self_tests_pass": True,
        "every_certified_level_has_strictly_opposite_endpoint_signs": all(
            row["endpoint_signs"][0] * row["endpoint_signs"][1] == -1 for row in certified),
        "level_one_bracket_contains_the_closed_form": any(
            row.get("contains_the_exact_closed_form_1_plus_sqrt5") for row in certified),
        "certification_stops_at_a_reported_level": evidence["certification_summary"]["first_failure"] is not None,
        "coarser_grid_certifies_no_more_levels": len(evidence["control_coarser_grid"]["levels_certified"])
        <= len(certified),
        "width_amplification_is_measured": amplification is not None,
        "exact_rational_barrier_is_measured": all(
            evidence["exact_rational_route"]["denominator_growth"][i + 1]["denominator_bits"]
            > evidence["exact_rational_route"]["denominator_growth"][i]["denominator_bits"]
            for i in range(len(evidence["exact_rational_route"]["denominator_growth"]) - 1)),
        "no_constant_enclosure_is_claimed": evidence["what_is_not_claimed"]["enclosure_of_delta"] is False
        and evidence["what_is_not_claimed"]["enclosure_of_alpha"] is False,
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
    for row in levels:
        if row["certified"]:
            print(f"  level {row['level']}: certified, width {row['width']}, "
                  f"bisections {row['bisections_used']}, centre {row['centre']}")
        else:
            print(f"  level {row['level']}: NOT certified — {row['reason']}")
    print("coarse grid certified:", evidence["control_coarser_grid"]["levels_certified"])
    print("amplification per iteration:", evidence["width_amplification_per_iteration"]["mean_factor"])
    print("ratio enclosures:", json.dumps(evidence["delta_ratio_enclosures"]))
    return 0 if evidence["status"] == "ExternalExactPass" else 1


if __name__ == "__main__":
    sys.exit(main())
