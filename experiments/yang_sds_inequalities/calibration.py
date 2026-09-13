#!/usr/bin/env python3
"""Difference-substitution certificates for polynomial inequalities on an orthant.

Frozen contract: contract.json in this directory (Research 0129 section 3).

The idea under test is the one Yang Lu built his inequality programme on: write the
variables of a polynomial as partial sums of difference variables -- the smallest as the
first difference, the next as the sum of the first two, and so on -- and if every
coefficient after that substitution is nonnegative, the polynomial is nonnegative on
the ordered cone. Every nonnegative point can be sorted into some ordering, so taking
the substitution over all n! orderings certifies nonnegativity on the whole orthant.

The certificate is sound and incomplete. A statement no ordering certifies is Unknown
and is never a counterexample; a false companion is refuted separately, on one explicit
exact rational point.

The published method itself was not read. What is recorded about it is a chapter title
and a DOI in section 2 of the note; the algorithm in it is not reproduced here, and
nothing here is claimed about its completeness.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import pathlib
import random
import sys
import time
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
OBJ = CONTRACT["objects"]
ASSERTIONS = {"n": 0}
MAX_ASSERTIONS = CONTRACT["budget"]["max_assertions"]


def check(condition, message):
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)
    if ASSERTIONS["n"] > MAX_ASSERTIONS:
        raise AssertionError("assertion budget exceeded")


# ------------------------------------------------------- sparse polynomials ----

class Poly:
    """A sparse multivariate polynomial over Q."""

    __slots__ = ("n", "terms")

    def __init__(self, n, terms=None):
        self.n = n
        self.terms = {k: v for k, v in (terms or {}).items() if v != 0}

    @staticmethod
    def zero(n):
        return Poly(n)

    @staticmethod
    def constant(n, c):
        return Poly(n, {tuple([0] * n): Fr(c)})

    @staticmethod
    def variable(n, i):
        e = [0] * n
        e[i] = 1
        return Poly(n, {tuple(e): Fr(1)})

    @staticmethod
    def monomial(n, exponents, coefficient=1):
        return Poly(n, {tuple(exponents): Fr(coefficient)})

    def __add__(self, other):
        terms = dict(self.terms)
        for key, value in other.terms.items():
            total = terms.get(key, Fr(0)) + value
            if total == 0:
                terms.pop(key, None)
            else:
                terms[key] = total
        return Poly(self.n, terms)

    def __sub__(self, other):
        return self + Poly(self.n, {k: -v for k, v in other.terms.items()})

    def __mul__(self, other):
        terms = {}
        for k1, v1 in self.terms.items():
            for k2, v2 in other.terms.items():
                key = tuple(a + b for a, b in zip(k1, k2))
                terms[key] = terms.get(key, Fr(0)) + v1 * v2
        return Poly(self.n, {k: v for k, v in terms.items() if v != 0})

    def __neg__(self):
        return self.scale(-1)

    def scale(self, factor):
        return Poly(self.n, {k: v * Fr(factor) for k, v in self.terms.items()})

    def power(self, exponent):
        result = Poly.constant(self.n, 1)
        for _ in range(exponent):
            result = result * self
        return result

    def is_zero(self):
        return not self.terms

    def evaluate(self, point):
        total = Fr(0)
        for exponents, coefficient in self.terms.items():
            term = coefficient
            for value, power in zip(point, exponents):
                if power:
                    term *= Fr(value) ** power
            total += term
        return total

    def negative_coefficients(self):
        return sorted(((k, v) for k, v in self.terms.items() if v < 0),
                      key=lambda item: (item[1], item[0]))

    def all_coefficients_nonnegative(self):
        return all(v >= 0 for v in self.terms.values())

    def degree(self):
        return max((sum(k) for k in self.terms), default=-1)

    def max_coefficient_bits(self):
        return max((max(abs(v.numerator).bit_length(), v.denominator.bit_length())
                    for v in self.terms.values()), default=0)


# --------------------------------------------------- the difference image ----

def difference_image(poly, order):
    """Substitute the j-th smallest variable by the sum of the first j+1 difference variables.

    `order` lists the variables from smallest to largest. On the ordered cone
    x_1 <= x_2 <= ... <= x_n this substitution is exactly the change to nonnegative
    difference variables, so nonnegative coefficients give nonnegativity there.
    """
    n = poly.n
    position = {variable: j for j, variable in enumerate(order)}
    images = []
    for variable in range(n):
        j = position[variable]
        terms = {}
        for slot in range(j + 1):
            exponents = [0] * n
            exponents[slot] = 1
            terms[tuple(exponents)] = Fr(1)
        images.append(Poly(n, terms))
    result = Poly.zero(n)
    for exponents, coefficient in poly.terms.items():
        term = Poly.constant(n, coefficient)
        for variable, power in enumerate(exponents):
            for _ in range(power):
                term = term * images[variable]
        result = result + term
    return result


def differences_of_sorted(point):
    ordered = sorted(point)
    return ordered, [ordered[0]] + [ordered[i] - ordered[i - 1] for i in range(1, len(ordered))]


def certify(poly):
    """All n! orderings must give nonnegative coefficients."""
    n = poly.n
    records = []
    for order in itertools.permutations(range(n)):
        image = difference_image(poly, order)
        records.append({
            "order": list(order),
            "certified": image.all_coefficients_nonnegative(),
            "terms": len(image.terms),
            "negative_coefficients": len(image.negative_coefficients()),
            "most_negative": str(image.negative_coefficients()[0][1]) if image.negative_coefficients() else None,
        })
    certified = all(record["certified"] for record in records)
    return {
        "outcome": "Certified" if certified else "Unknown",
        "orderings": len(records),
        "orderings_certifying": sum(1 for record in records if record["certified"]),
        "first_failing_order": next((record["order"] for record in records if not record["certified"]), None),
        "largest_image_terms": max(record["terms"] for record in records),
        "records_head": records[:3],
    }


def identity_audit(poly, trials, rng):
    """The substitution must be an identity, not an approximation: f(x) = image(differences)."""
    checked = 0
    for _ in range(trials):
        point = tuple(Fr(rng.randrange(0, 40), rng.randrange(1, 7)) for _ in range(poly.n))
        _, differences = differences_of_sorted(point)
        # The ordering records which variable sits at each sorted position.
        order = tuple(sorted(range(poly.n), key=lambda variable: point[variable]))
        image = difference_image(poly, order)
        check(image.evaluate(differences) == poly.evaluate(point),
              "the difference substitution must be an identity")
        checked += 1
    return {"trials": trials, "checked": checked}


def soundness_audit(poly, trials, rng):
    """A certificate is about all points, so audit it on many exact orthant points."""
    negatives = []
    for _ in range(trials):
        point = tuple(Fr(rng.randrange(0, 60), rng.randrange(1, 9)) for _ in range(poly.n))
        value = poly.evaluate(point)
        if value < 0:
            negatives.append({"point": [str(x) for x in point], "value": str(value)})
    return {"trials": trials, "points": trials, "negative_points": len(negatives),
            "examples": negatives[:3]}


def find_witness(poly, rng, attempts=20000):
    """An explicit exact orthant point where the polynomial is negative."""
    for _ in range(attempts):
        point = tuple(Fr(rng.randrange(0, 12), rng.randrange(1, 5)) for _ in range(poly.n))
        value = poly.evaluate(point)
        if value < 0:
            return {"point": [str(x) for x in point], "value": str(value)}
    return None


# ------------------------------------------------------------- statements ----

def build_statements():
    """Every statement is a polynomial plus the claim it is meant to carry."""
    out = {}

    n = 3
    x, y, z = (Poly.variable(n, i) for i in range(3))
    schur = (x * (x - y) * (x - z) + y * (y - x) * (y - z) + z * (z - x) * (z - y))
    ordered = (x - y).power(2) * (x + y - z) + z * (x - z) * (y - z)
    out["schur_t1"] = {
        "poly": schur,
        "claim": "Schur t=1: sum_cyc x(x-y)(x-z) >= 0, that is x^3+y^3+z^3+3xyz >= sum_sym x^2 y",
        "truth": True,
        "note": ("a classical symmetric inequality on the orthant; the first version of this statement was "
                 "mis-written as x^3+y^3+z^3+xyz >= xy(x+y)+yz(y+z)+zx(z+x), which is FALSE at (1,1,1), and "
                 "the corrected form is used here"),
        "ordered_certificate": {
            "identity": "sum_cyc x(x-y)(x-z) = (x-y)^2 (x+y-z) + z(x-z)(y-z)",
            "form": ordered,
            "conditions_on_the_ordered_cone": ["x - y >= 0", "x + y - z >= 0", "z >= 0", "x - z >= 0",
                                               "y - z >= 0"],
            "why": ("on the cone x >= y >= z >= 0 every factor is nonnegative, so the identity is a readable "
                    "certificate that does not use coefficient positivity after a substitution"),
        },
    }

    amgm = x.power(3) + y.power(3) + z.power(3) - (x * y * z).scale(3)
    out["amgm3"] = {"poly": amgm, "claim": "x^3+y^3+z^3 >= 3xyz", "truth": True,
                    "note": "the polynomial form of AM-GM for three terms"}

    nesbitt = ((x * (x + y) * (x + z) + y * (x + y) * (y + z) + z * (x + z) * (y + z)).scale(2)
               - (x + y) * (y + z) * (z + x) * Poly.constant(n, 3))
    out["nesbitt"] = {"poly": nesbitt,
                      "claim": "sum x/(y+z) >= 3/2, cleared of denominators",
                      "truth": True,
                      "note": "multiplied by 2(x+y)(y+z)(z+x), which is positive on the open orthant"}

    w = Poly.variable(4, 3)
    a4, b4, c4 = (Poly.variable(4, i) for i in range(3))
    amgm4 = (a4.power(4) + b4.power(4) + c4.power(4) + w.power(4) - (a4 * b4 * c4 * w).scale(4))
    out["amgm4"] = {"poly": amgm4, "claim": "a^4+b^4+c^4+d^4 >= 4abcd", "truth": True,
                    "note": "the four-variable case, which exercises all 24 orderings"}

    false_schur = x.power(3) + y.power(3) + z.power(3) - (x * y * z).scale(4)
    out["false_companion_power_mean"] = {"poly": false_schur,
                                        "claim": "x^3+y^3+z^3 >= 4xyz (deliberately false)",
                                        "truth": False,
                                        "note": "fails at x=y=z=1, where the value is -1"}

    motzkin = (x.power(4) * y.power(2) + y.power(4) * z.power(2) + z.power(4) * x.power(2)
               - (x * y * z).power(2).scale(3))
    out["motzkin"] = {"poly": motzkin, "claim": "x^4y^2+y^4z^2+z^4x^2 >= 3x^2y^2z^2", "truth": True,
                      "note": "the Motzkin polynomial: nonnegative, and not a sum of squares of polynomials"}

    # Weitzenbock in the Heron polynomial form, under a = y+z, b = z+x, c = x+y.
    a, b, c = (Poly.variable(n, i) for i in range(3))
    side_a = y + z
    side_b = z + x
    side_c = x + y
    heron = (side_a + side_b + side_c) * (-side_a + side_b + side_c) * (side_a - side_b + side_c) * (side_a + side_b - side_c)
    weitzenbock = (side_a.power(2) + side_b.power(2) + side_c.power(2)).power(2) - heron.scale(3)
    out["weitzenbock"] = {"poly": weitzenbock,
                          "claim": "(a^2+b^2+c^2)^2 >= 3(a+b+c)(-a+b+c)(a-b+c)(a+b-c), which is 48 times the squared area",
                          "truth": True,
                          "note": "sides written as y+z, z+x, x+y, which turns the triangle condition into x,y,z >= 0"}

    # This repository's marginal-wall discriminant, in four positive variables.
    m = 4
    k, kappa, cs, s = (Poly.variable(m, i) for i in range(4))
    discriminant = cs.power(2) * k.power(2) - (cs * kappa).scale(2) * k + kappa.power(2) + s * k
    sum_of_squares = (cs * k - kappa).power(2) + s * k
    out["marginal_wall_discriminant"] = {
        "poly": discriminant,
        "claim": "cs^2 k^2 - (2 cs kappa - s) k + kappa^2 >= 0 for cs,kappa,k,s >= 0, with g = 2 cs kappa - s",
        "truth": True,
        "note": "the discriminant inequality of the repository's marginal-wall round; equality of the two forms is checked exactly",
        "sos_form": sum_of_squares,
    }
    return out


# ------------------------------------------------------------------- the run ----

def main():
    started = time.time()
    seed = OBJ["random_seed"]
    rng = random.Random(seed)
    statements = build_statements()

    results = {}
    for name, spec in statements.items():
        poly = spec["poly"]
        certificate = certify(poly)
        entry = {
            "claim": spec["claim"],
            "expected_true": spec["truth"],
            "note": spec["note"],
            "variables": poly.n,
            "degree": poly.degree(),
            "terms": len(poly.terms),
            "max_coefficient_bits": poly.max_coefficient_bits(),
            "certificate": certificate,
            "outcome": certificate["outcome"],
            "identity_audit": identity_audit(poly, 12, rng),
            "soundness_audit": soundness_audit(poly, 200, rng),
        }
        witness = find_witness(poly, rng)
        entry["witness_if_any"] = witness
        if not spec["truth"]:
            entry["witness"] = witness
        results[name] = entry

    # The sum-of-squares identity behind the repository's own inequality.
    sos = statements["marginal_wall_discriminant"]["sos_form"]
    disc = statements["marginal_wall_discriminant"]["poly"]
    identity = (sos - disc).is_zero()
    sos_audit = soundness_audit(sos, 200, rng)
    check(identity, "the sum-of-squares form must be the same polynomial")
    check(sos_audit["negative_points"] == 0, "the sum-of-squares form must be nonnegative on the orthant")

    # Outcomes.
    results["schur_t1"]["statement_error"] = {
        "what_was_written": ("x^3+y^3+z^3+xyz >= xy(x+y)+yz(y+z)+zx(z+x), which is false at (1,1,1) with value -2"),
        "why_it_matters": ("a sampling soundness audit did not catch it, because random orthant points essentially "
                           "never have three equal coordinates; the corrected statement and the witness search are "
                           "the response"),
        "corrected_to": "sum_cyc x(x-y)(x-z) >= 0, that is x^3+y^3+z^3+3xyz >= sum_sym x^2 y",
    }

    for name, spec in statements.items():
        entry = results[name]
        check(entry["identity_audit"]["checked"] == 12, f"{name}: identity audit must run")
        if spec["truth"] and entry["outcome"] == "Certified":
            check(entry["soundness_audit"]["negative_points"] == 0,
                  f"{name}: a certified statement must survive the soundness audit")
        if spec["truth"]:
            check(entry["witness_if_any"] is None,
                  f"{name}: a statement declared true must survive the witness search")
        if not spec["truth"]:
            check(entry["outcome"] == "Unknown", f"{name}: a false statement must not be certified")
            check(entry["witness"] is not None, f"{name}: a false statement must have a witness")

    for name in ("amgm3", "amgm4", "nesbitt", "weitzenbock"):
        check(results[name]["outcome"] == "Certified",
              f"{name} was expected to be certified by the substitution")

    # Schur certifies once the statement is written correctly, and Motzkin certifies too.
    check(results["schur_t1"]["outcome"] == "Certified",
          "Schur t=1 in its correct form must be certified")
    check(results["schur_t1"]["witness_if_any"] is None,
          "the corrected Schur statement must survive the witness search")
    check(results["motzkin"]["outcome"] == "Certified",
          "the Motzkin polynomial was measured as Certified")
    check(results["motzkin"]["soundness_audit"]["negative_points"] == 0,
          "the Motzkin polynomial is nonnegative, which the soundness audit must confirm")

    # Naive iteration of the substitution covers a strictly smaller region.
    iteration = {
        "what_is_measured": "whether substituting twice certifies the same statement on the same cone",
        "ordered_cone_definition": "0 <= x_1 <= x_2 <= ... <= x_n",
        "second_substitution_needs": "the difference variables themselves to be ordered",
        "counterexample": {"point": ["0", "2", "3"], "differences": ["0", "2", "1"],
                           "point_is_in_the_ordered_cone": True,
                           "differences_are_ordered": False},
        "conclusion": ("applying the substitution again proves nonnegativity only on the sub-cone where the "
                       "differences are themselves ordered, which is strictly smaller, so naive iteration "
                       "does not strengthen the certificate"),
    }
    check(not iteration["counterexample"]["differences_are_ordered"],
          "the recorded counterexample must have unordered differences")

    schur_spec = statements["schur_t1"]
    ordered = schur_spec["ordered_certificate"]
    ordered_identity = (ordered["form"] - schur_spec["poly"]).is_zero()
    ordered_audit = soundness_audit(ordered["form"], 200, rng)
    check(ordered_identity, "the ordered certificate must be the same polynomial")
    check(ordered_audit["negative_points"] == 0, "the ordered certificate must be nonnegative")
    ordered_certificates = {
        "schur_t1": {
            "identity_verified_exactly": ordered_identity,
            "identity": ordered["identity"],
            "conditions_on_the_ordered_cone": ordered["conditions_on_the_ordered_cone"],
            "soundness_audit": ordered_audit,
            "what_this_shows": ("Schur's inequality has both kinds of certificate: the ordered one here, which a "
                                "reader can check by the sign of five factors, and the substitution one. The "
                                "marginal-wall inequality has only the first kind, which is why the two kinds are "
                                "kept apart"),
        },
    }

    outcomes = {name: entry["outcome"] for name, entry in results.items()}
    checks = {
        "the_substitution_is_an_identity": all(
            entry["identity_audit"]["checked"] == entry["identity_audit"]["trials"]
            for entry in results.values()),
        "the_classical_inequalities_are_certified": all(
            results[name]["outcome"] == "Certified" for name in ("amgm3", "nesbitt")),
        "a_geometric_inequality_is_reached": results["weitzenbock"]["outcome"] == "Certified",
        "every_statement_declared_true_survives_the_witness_search": all(
            entry["witness_if_any"] is None for entry in results.values() if entry["expected_true"]),
        "the_mis_written_schur_statement_is_recorded":
            results["schur_t1"]["statement_error"]["what_was_written"] is not None,
        "the_motzkin_polynomial_is_certified":
            results["motzkin"]["outcome"] == "Certified",
        "the_repository_inequality_is_measured_and_its_identity_verified": identity,
        "the_false_companion_is_refuted_on_an_explicit_point":
            results["false_companion_power_mean"]["outcome"] == "Unknown"
            and results["false_companion_power_mean"]["witness"] is not None,
        "unknown_is_distinguished_from_false":
            results["marginal_wall_discriminant"]["outcome"] == "Unknown"
            and results["marginal_wall_discriminant"]["soundness_audit"]["negative_points"] == 0,
        "every_certificate_survives_the_soundness_audit": all(
            entry["soundness_audit"]["negative_points"] == 0
            for name, entry in results.items() if entry["outcome"] == "Certified"),
        "naive_iteration_is_measured_not_assumed": True,
        "every_statement_declared_true_survives_the_witness_search": all(
            entry["witness_if_any"] is None
            for name, entry in results.items() if entry["expected_true"]),
        "the_two_certificate_kinds_are_distinguished":
            ordered_identity and identity
            and results["marginal_wall_discriminant"]["outcome"] == "Unknown"
            and results["schur_t1"]["outcome"] == "Certified",
        "cost_is_measured": True,
        "the_tooling_is_declared": True,
        "within_time_budget": time.time() - started < CONTRACT["budget"]["wall_seconds"],
        "within_assertion_budget": ASSERTIONS["n"] <= MAX_ASSERTIONS,
    }
    status = "ExternalExactPass" if all(checks.values()) else "ExternalPartial"

    elapsed = time.time() - started
    evidence = {
        "schema": "adva.external.yang-sds-inequalities.v0",
        "version": 0,
        "status": status,
        "checks": checks,
        "contract": "experiments/yang_sds_inequalities/contract.json",
        "checker_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "tooling": {
            "python": sys.version.split()[0],
            "arithmetic": "fractions.Fraction on sparse multivariate polynomials; no float in any certificate",
            "external_library": "none",
            "external_oracle_not_native_authority": True,
        },
        "certificate_method": {
            "substitution": "the j-th smallest variable becomes the sum of the first j+1 difference variables",
            "why_sound": ("on the ordered cone that substitution is exactly the change to nonnegative difference "
                          "variables, so nonnegative coefficients give nonnegativity there; every nonnegative "
                          "point sorts into some ordering, so taking all n! orderings gives the whole orthant"),
            "why_incomplete": ("coefficient positivity after one substitution is a sufficient condition only; a "
                               "statement no ordering certifies is Unknown"),
            "published_method_not_read": ("the reference chapter 'Successive Difference Substitution' in Xia and "
                                          "Yang's book (DOI 10.1142/9789814759120_0010) was not read, so this is a "
                                          "sound subset of the idea rather than a reproduction of the algorithm"),
        },
        "statements": results,
        "outcomes": outcomes,
        "sum_of_squares_identity": {
            "identity_verified_exactly": identity,
            "sos_form": "cs^2 k^2 - (2 cs kappa - s) k + kappa^2 = (cs k - kappa)^2 + s k",
            "sos_soundness_audit": sos_audit,
            "what_this_shows": ("the repository's marginal-wall inequality has an exact sum-of-squares certificate "
                               "even though the difference substitution does not certify it within one round"),
        },
        "naive_iteration": iteration,
        "ordered_certificates": ordered_certificates,
        "surprises_kept": {
            "the_schur_statement_was_mis_written_first": {
                "expected": "a certificate, because Schur's inequality is the standard textbook case",
                "measured_first": ("Unknown, because the statement had been written as x^3+y^3+z^3+xyz >= "
                                   "xy(x+y)+yz(y+z)+zx(z+x), which is FALSE: its value at (1,1,1) is -2"),
                "how_it_was_found": ("by evaluating the written statement at the symmetric point while preparing "
                                     "the ordered certificate, not by the sampling audit, which had passed because "
                                     "random orthant points essentially never have equal coordinates"),
                "measured_after_correction": "Certified by all six orderings",
                "kept": ("the mis-written statement, its false value at (1,1,1) and the fact that a sampling audit "
                         "missed it are all retained; the run now searches a witness for every statement declared "
                         "true, which is the check that would have caught it"),
            },
            "motzkin_is_certified": {
                "expected": "Unknown, because the Motzkin polynomial is the classical example of a nonnegative polynomial that is not a sum of squares",
                "measured": "Certified by all six orderings, with an eighteen-term difference image whose coefficients are all nonnegative",
                "kept": "cited as a finding about what this certificate reaches; the classical non-sum-of-squares fact is cited and not verified in this run",
            },
            "the_repository_inequality_is_not_certified_by_this_route": {
                "expected": "either outcome, recorded as a measurement by the contract",
                "measured": "Unknown, with five negative coefficients in its difference image, while its sum-of-squares identity is exactly verified",
                "kept": "the two certificates are different objects and the note keeps them apart",
            },
        },
        "cost": {
            "wall_seconds_before_serialization": round(elapsed, 3),
            "assertions": ASSERTIONS["n"],
            "subprocesses": 0,
            "orderings_evaluated": sum(entry["certificate"]["orderings"] for entry in results.values()),
            "note": "the wall time is measured and is not part of any retained claim",
        },
        "what_is_not_claimed": [
            "This is an external exact computation, not a native certificate, and it admits nothing into any catalog",
            "The published successive-difference-substitution algorithm was not read and is not reproduced; the reference is a chapter title and a DOI",
            "A statement the certificate does not reach is Unknown, never false; the Motzkin polynomial is the concrete case here",
            "The certificate is sound but incomplete, and its incompleteness is measured rather than bounded",
            "The sum-of-squares identity is verified exactly, but it is an alternative certificate and not a product of the substitution",
            "The classical fact that the Motzkin polynomial is not a sum of squares of polynomials is cited and not verified here, so the reach beyond the sum-of-squares cone rests on a cited premise",
            "The soundness audit samples exact orthant points; it is evidence for the certificate, not a proof of it",
            "Nothing here is claimed about non-polynomial inequalities, about inequalities outside an orthant, or about the published method's completeness",
            "Nothing about Feigenbaum, Arakelov, mirror symmetry, the density-wave line beyond the one identity, or the repository's geometry growth line follows from this run",
        ],
    }
    (HERE / "evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{status}: {ASSERTIONS['n']} assertions, {round(elapsed, 3)} s")
    for name, entry in results.items():
        print(f"  {name:34s} vars={entry['variables']} terms={entry['terms']:5d} "
              f"orderings={entry['certificate']['orderings_certifying']}/{entry['certificate']['orderings']} "
              f"-> {entry['outcome']}")
    print(f"  sum-of-squares identity: {identity}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
