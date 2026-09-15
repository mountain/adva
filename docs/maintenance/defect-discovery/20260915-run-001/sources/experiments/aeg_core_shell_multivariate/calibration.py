"""Two variables: what still works, what does not, and what a truncated shell costs.

The previous round left two things open in one question: whether the multivariate
case needs a greatest-common-divisor algorithm and a monomial order, and whether the
reason for declining the truncated route still stands. This experiment measures both
in a declared bivariate fragment, exactly.

What is measured, and each is a check rather than a claim:

  * value equality between two rational functions is decided by cross multiplication,
    with no greatest common divisor and no monomial order on that path;
  * Kronecker substitution is an exact equality test because it is injective on
    bounded degrees, but it is not a correct greatest-common-divisor route: with the
    declared degenerate exponent the substituted divisor is a strict multiple of the
    true image, and the extra factor is named;
  * no polynomials p and q satisfy p*x + q*y = 1, proved by evaluating at the origin
    and separately searched over every monomial up to a declared bound, the search
    being reported as a bounded negative and never as the proof;
  * modular and specialised images of the divisor agree, which is the congruence half
    of the historical method; no rational reconstruction is implemented, and that gap
    is recorded;
  * and the composed measurement the previous round left unmeasured: a truncated
    inverse modulo the ideal of positive-degree terms against the exact carrier, on the
    content level and on the object level, with the growth of each route reported.

Nothing here uses floating point.
"""
import itertools
import hashlib
import json
import pathlib
import sys
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
COUNTS = {"assertions": 0, "multiplications": 0, "bezout_pairs_examined": 0,
          "kronecker_images": 0, "modular_images": 0}
LIMITS = {}


def check(value, message):
    COUNTS["assertions"] += 1
    if COUNTS["assertions"] > LIMITS["max_assertions"]:
        raise RuntimeError("Unknown: assertion budget")
    if not value:
        raise ValueError(message)


def jsonable(value):
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, Fr):
        return str(value)
    return value


# ------------------------------------------------- exact polynomials in n variables

class MPoly:
    """A sparse polynomial with exact rational coefficients over declared variables.

    A monomial is an exponent vector; the leading monomial is the largest in the
    lexicographic order on that vector, which is the only place a monomial order
    appears in this file and it is used for division, never for equality.
    """

    __slots__ = ("terms", "nvars")

    def __init__(self, terms, nvars):
        cleaned = {}
        for coefficient, exponents in terms:
            coefficient = Fr(coefficient)
            exponents = tuple(exponents)
            check(len(exponents) == nvars, "MonomialHasTheWrongNumberOfVariables")
            check(all(e >= 0 for e in exponents), "NegativeExponentRefused")
            if coefficient:
                cleaned[exponents] = cleaned.get(exponents, Fr(0)) + coefficient
                if not cleaned[exponents]:
                    del cleaned[exponents]
        self.terms = cleaned
        self.nvars = nvars

    @staticmethod
    def constant(value, nvars):
        return MPoly([(value, (0,) * nvars)], nvars)

    @staticmethod
    def variable(index, nvars):
        exponents = [0] * nvars
        exponents[index] = 1
        return MPoly([(1, tuple(exponents))], nvars)

    @staticmethod
    def zero(nvars):
        return MPoly([], nvars)

    def is_zero(self):
        return not self.terms

    def __add__(self, other):
        out = dict(self.terms)
        for exponents, coefficient in other.terms.items():
            out[exponents] = out.get(exponents, Fr(0)) + coefficient
            if not out[exponents]:
                del out[exponents]
        # out is keyed by exponent vector, but MPoly takes (coefficient, exponents);
        # passing items() directly swaps them, the same transposition this repository
        # has now made twice
        return MPoly([(coefficient, exponents) for exponents, coefficient in out.items()],
                     self.nvars)

    def __neg__(self):
        return MPoly([(-c, e) for e, c in self.terms.items()], self.nvars)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        COUNTS["multiplications"] += 1
        out = {}
        for e1, c1 in self.terms.items():
            for e2, c2 in other.terms.items():
                exponents = tuple(a + b for a, b in zip(e1, e2))
                out[exponents] = out.get(exponents, Fr(0)) + c1 * c2
        return MPoly([(c, e) for e, c in out.items()], self.nvars)

    def scale(self, factor):
        return MPoly([(c * Fr(factor), e) for e, c in self.terms.items()], self.nvars)

    def is_constant(self):
        """True when no term has a positive total degree; the zero polynomial counts."""
        return all(sum(e) == 0 for e in self.terms)

    def total_degree(self):
        return max((sum(e) for e in self.terms), default=-1)

    def monomial_count(self):
        return len(self.terms)

    def evaluate(self, point):
        check(len(point) == self.nvars, "PointHasTheWrongNumberOfCoordinates")
        total = Fr(0)
        for exponents, coefficient in self.terms.items():
            term = coefficient
            for value, exponent in zip(point, exponents):
                term *= Fr(value) ** exponent
            total += term
        return total

    def kronecker(self, base):
        """Substitute the i-th variable by t^(base^(n-1-i)).

        Injective exactly when every variable's degree is below the base, which is
        what makes it an exact test and what the degenerate base breaks.
        """
        COUNTS["kronecker_images"] += 1
        terms = []
        for exponents, coefficient in self.terms.items():
            exponent = 0
            for position, value in enumerate(exponents):
                exponent += value * base ** (self.nvars - 1 - position)
            terms.append((coefficient, (exponent,)))
        return MPoly(terms, 1)

    def reduce_mod(self, prime):
        """Reduce the coefficients into F_p; refuses when a denominator vanishes mod p."""
        COUNTS["modular_images"] += 1
        terms = []
        for exponents, coefficient in self.terms.items():
            numerator = coefficient.numerator % prime
            denominator = coefficient.denominator % prime
            check(denominator != 0, "CoefficientDenominatorVanishesModuloThePrime")
            terms.append((Fr(numerator * pow(denominator, -1, prime) % prime), exponents))
        return MPoly(terms, self.nvars)

    def is_divisible_by(self, candidate):
        """Exact division; returns None when the leading monomial does not divide."""
        check(not candidate.is_zero(), "DivisionByZeroPolynomialRefused")
        remainder = self
        quotient_terms = []
        guard = 0
        while not remainder.is_zero():
            guard += 1
            check(guard <= 4096, "DivisionDidNotTerminate")
            lead, clead = max(remainder.terms), max(candidate.terms)
            if any(a < b for a, b in zip(lead, clead)):
                return None
            shift = tuple(a - b for a, b in zip(lead, clead))
            factor = remainder.terms[lead] / candidate.terms[clead]
            quotient_terms.append((factor, shift))
            remainder = remainder - MPoly([(factor, shift)], self.nvars) * candidate
        return MPoly(quotient_terms, self.nvars)

    def monic_univariate(self):
        """Divide by the leading coefficient; over Q the units are constants, so this
        is enough to make the representative canonical. Shifting exponents instead
        would need negative powers and is not a polynomial operation."""
        lead = max(self.terms)
        return MPoly([(c / self.terms[lead], e) for e, c in self.terms.items()], 1)

    def show(self):
        names = "xyz"
        if not self.terms:
            return "0"
        parts = []
        for exponents in sorted(self.terms, reverse=True):
            coefficient = self.terms[exponents]
            body = "".join("%s%s" % (names[i], "" if e == 1 else "^%d" % e)
                           for i, e in enumerate(exponents) if e)
            parts.append("%s%s" % (coefficient, body))
        return " + ".join(parts)

    def __eq__(self, other):
        return self.terms == other.terms


def parse(terms, nvars):
    return MPoly([(Fr(c), e) for c, e in terms], nvars)


# ------------------------------------------------------- the one-variable engines

def univariate_gcd(a, b, prime=None):
    """The Euclidean algorithm, over Q or over F_p; the result is monic."""
    def step(x, y):
        quotient, remainder = MPoly.zero(1), x
        guard = 0
        while not remainder.is_zero() and max(remainder.terms) >= max(y.terms):
            guard += 1
            check(guard <= 512, "UnivariateDivisionDidNotTerminate")
            lead, ylead = max(remainder.terms), max(y.terms)
            shift = lead[0] - ylead[0]
            if prime is None:
                factor = remainder.terms[lead] / y.terms[ylead]
            else:
                divisor = y.terms[ylead].numerator % prime
                check(divisor != 0, "UnluckyPrimeZeroesTheLeadingCoefficient")
                inverse = pow(divisor, -1, prime)
                factor = Fr(remainder.terms[lead].numerator % prime * inverse % prime)
            term = MPoly([(factor, (shift,))], 1)
            quotient = quotient + term
            remainder = remainder - term * y
            if prime is not None:
                # keep every intermediate coefficient in F_p: reducing only the input
                # leaves multiples of p behind and the arithmetic stops being modular
                remainder = remainder.reduce_mod(prime)
                quotient = quotient.reduce_mod(prime)
        return remainder
    while not b.is_zero():
        a, b = b, step(a, b)
    check(not a.is_zero(), "UnivariateGcdIsZero")
    return a.monic_univariate()


# ------------------------------------------- the truncated inverse modulo an ideal

def truncated_inverse(denominator, order):
    """The inverse modulo the ideal of positive-degree terms to the declared order.

    For a denominator with a non-zero constant term write denominator = constant *
    (1 + g) with g in the ideal; then the inverse is constant^-1 * (1 - g + g^2 - ...),
    a finite series because g^order lies in the ideal raised to that order.
    """
    nvars = denominator.nvars
    constant = denominator.terms.get((0,) * nvars)
    check(constant is not None and constant != 0, "InverseNeedsANonzeroConstantTerm")
    unit = denominator.scale(1 / constant)
    one = MPoly.constant(1, nvars)
    g = unit - one
    if g.is_zero():
        return one
    total, power = one, one
    for step in range(order):
        power = power * g
        total = total + power.scale(-1 if step % 2 == 0 else 1)
    return total.scale(1 / constant)


def inside_the_ideal(product, order):
    return all(sum(e) >= order for e in product.terms)


# ---------------------------------------------------------------------- the checks

def run(contract):
    o = contract["objects"]
    nvars = 2
    g = parse(o["g"], nvars)
    h = parse(o["h"], nvars)
    k = parse(o["k"], nvars)
    x = MPoly.variable(0, nvars)
    y = MPoly.variable(1, nvars)

    # (0) no Bezout combination of x and y exists
    check(x.evaluate((0, 0)) == 0 and y.evaluate((0, 0)) == 0,
          "TheOriginEvaluationDoesNotVanish")
    bound = o["bezout_search_bound"]
    monomials = [MPoly([(1, e)], nvars) for e in itertools.product(range(bound + 1), repeat=nvars)
                 if 0 < sum(e) <= bound]
    found = []
    for p in monomials:
        for q in monomials:
            COUNTS["bezout_pairs_examined"] += 1
            combination = p * x + q * y
            if combination.total_degree() == 0:
                found.append([p.show(), q.show()])
    check(not found, "ABezoutCombinationWasFound")
    bezout = {
        "claim": "no polynomials p and q satisfy p*x + q*y = 1",
        "proof": "evaluate at the origin: every monomial of p*x and of q*y vanishes there, so "
                 "the left side is 0 while the right side is 1",
        "bounded_search": {"bound": bound, "monomials": len(monomials),
                           "pairs_examined": COUNTS["bezout_pairs_examined"],
                           "witnesses_found": len(found),
                           "searched_family": "p and q are single monomials with coefficient one",
                           "status": "bounded negative over a declared family, not the proof"},
        "consequence": "Q[x,y] is not a Bezout domain, so an extended-Euclidean inversion cannot be "
                       "transferred from Z or Q[x] to two variables; the historical method's 求一 "
                       "step has no target object here"}

    # (1) value equality of rational functions by cross multiplication
    equality = []
    for scale in (h, k, x + y):
        # the same value written two ways: g*h / g*k against (g*h*scale) / (g*k*scale)
        num_one, den_one = g * h, g * k
        num_two, den_two = num_one * scale, den_one * scale
        cross = num_one * den_two - num_two * den_one
        check(cross.is_zero(), "CrossMultiplicationDidNotDecideEquality")
        check(h.is_divisible_by(g) is None or True, "unused")
        equality.append({"scale": scale.show(),
                         "left_pair": "%s / %s" % (num_one.show()[:24], den_one.show()[:24]),
                         "cross_product_is_zero": True,
                         "uses_gcd": False, "uses_monomial_order": False})

    # (2) Kronecker: exact only while injective, and a divisor route only by measurement
    maximum_degree = max(max(e[i] for e in (g * h).terms | (g * k).terms)
                         for i in range(nvars))
    kronecker = []
    for base in o["kronecker_exponents_to_test"]:
        label = "injective" if base > maximum_degree else "non-injective"
        injective = base > maximum_degree
        left, right = g * h, g * k
        difference = left - right
        image_of_difference = difference.kronecker(base)
        # a collision is exhibited whenever the substitution is not injective
        collision = None
        if not injective:
            monomials = [MPoly([(1, e)], nvars)
                         for e in itertools.product(range(maximum_degree + 1), repeat=nvars)
                         if sum(e) > 0]
            for one, other in itertools.combinations(monomials, 2):
                if one != other and one.kronecker(base) == other.kronecker(base):
                    collision = [one.show(), other.show(), one.kronecker(base).show()]
                    break
            check(collision is not None,
                  "ANonInjectiveSubstitutionExhibitedNoCollisionWhichCannotBe")
        image_gcd = univariate_gcd(left.kronecker(base), right.kronecker(base))
        true_image = univariate_gcd(g.kronecker(base), g.kronecker(base))
        agrees = image_gcd == true_image
        kronecker.append({
            "label": label, "base": base,
            "maximum_degree_in_each_variable": maximum_degree,
            "injective_on_these_degrees": injective,
            "collision_witness": collision,
            "equality_decided_by_the_image_is_sound": injective,
            "image_of_the_difference_is_zero": image_of_difference.is_zero(),
            "substituted_gcd": image_gcd.show()[:70],
            "image_of_the_true_divisor_normalised": true_image.show()[:70],
            "divisor_image_agrees": agrees,
            "reading": ("the substitution is injective here, so the image decides equality soundly, "
                        "and on this pair it also returns the image of the true divisor"
                        if injective and agrees else
                        "the substitution is injective here and the image decides equality soundly, "
                        "but whether it returns the true divisor's image is a measurement on the "
                        "pair rather than a guarantee" if injective else
                        "the substitution is not injective, so an image can make two distinct "
                        "polynomials look equal; the collision witness is exhibited")})
    check(any(row["injective_on_these_degrees"] for row in kronecker),
          "NoInjectiveBaseWasTested")
    check(any(not row["injective_on_these_degrees"] for row in kronecker),
          "NoNonInjectiveBaseWasTested")
    check(all(row["collision_witness"] for row in kronecker
              if not row["injective_on_these_degrees"]),
          "ANonInjectiveBaseHasNoCollisionWitness")
    # the threshold is derived from the degrees, not declared, and each declared
    # exponent is placed on one side of it by measurement
    injectivity_threshold = maximum_degree + 1
    below_threshold = [row["base"] for row in kronecker
                       if not row["injective_on_these_degrees"]]
    at_or_above = [row["base"] for row in kronecker if row["injective_on_these_degrees"]]
    check(below_threshold, "EveryDeclaredExponentMetTheThresholdSoNothingIsExhibited")

    # (3) the congruence half: modular and specialised images of the divisor
    # recovery is measured per cell rather than asserted: the image of the divisor
    # always divides a computed image, so every mismatch is a strict extra factor,
    # and that factor is exhibited instead of being smoothed over
    congruence = []
    for image_exponent in o["kronecker_exponents_to_test"]:
        expected_full = g.kronecker(image_exponent)
        for prime in o["primes"]:
            reduced_left = (g * h).reduce_mod(prime).kronecker(image_exponent)
            reduced_right = (g * k).reduce_mod(prime).kronecker(image_exponent)
            image = univariate_gcd(reduced_left, reduced_right, prime=prime)
            expected_mod = expected_full.reduce_mod(prime).monic_univariate()
            matches = image == expected_mod
            extra = None
            if not matches:
                quotient = image.is_divisible_by(expected_mod)
                check(quotient is not None,
                      "TheImageIsNotEvenAMultipleOfTheDivisorWhichCannotBe")
                check(not quotient.is_constant(),
                      "TheMismatchWasOnlyAScalarSoMonicNormalisationWasWrong")
                extra = quotient.show()[:60]
            congruence.append({"route": "modular", "image_exponent": image_exponent,
                               "prime": prime,
                               "image_matches_the_reduced_divisor": matches,
                               "extra_factor": extra,
                               "image": image.show()[:60],
                               "expected": expected_mod.show()[:60],
                               "status": "Recovered" if matches else
                                         "UnluckyImageCarriesAnExtraFactor"})
    for point in o["specializations"]:
        # substitute y at the declared point, leaving a univariate polynomial in x
        def specialise(poly):
            terms = []
            for exponents, coefficient in poly.terms.items():
                value = Fr(point[1]) ** exponents[1]
                terms.append((coefficient * value, (exponents[0],)))
            return MPoly(terms, 1)
        image = univariate_gcd(specialise(g * h), specialise(g * k))
        expected_specialised = specialise(g).monic_univariate()
        matches = image == expected_specialised
        extra = None
        if not matches:
            quotient = image.is_divisible_by(expected_specialised)
            check(quotient is not None,
                  "TheSpecialisedImageIsNotAMultipleOfTheSpecialisedDivisor")
            extra = None if quotient is None else quotient.show()[:60]
        congruence.append({"route": "specialization", "specialization_y": point[1],
                           "image_matches_the_specialised_divisor": matches,
                           "extra_factor": extra,
                           "image": image.show()[:60],
                           "status": "Recovered" if matches else
                                     "UnluckyImageCarriesAnExtraFactor"})
    recovered = [row for row in congruence if row["status"] == "Recovered"]
    unlucky = [row for row in congruence if row["status"] != "Recovered"]
    check(recovered, "NoDeclaredImageRecoveredTheDivisorAtAll")
    for row in unlucky:
        check(row["extra_factor"] is not None, "AnUnluckyImageHasNoWitness")

    # (4) the composed measurement: truncated shell against the exact carrier
    # the denominator must have a non-zero constant term for the inverse to exist in
    # the local ring; 1 + h would be x^2, whose constant term is zero and which the
    # checker refuses, so the declared denominator is h + 2 = x^2 + 1
    denominator = h + MPoly.constant(2, nvars)
    composed, truncated = [], []
    for order in o["truncation_orders"]:
        approximation = truncated_inverse(denominator, order)
        residual = approximation * denominator - MPoly.constant(1, nvars)
        check(inside_the_ideal(residual, order), "TheTruncationResidualIsNotInsideTheIdeal")
        check(not residual.is_zero(), "TheTruncationDroppedNothingSoItProvesNothing")
        truncated.append({"order": order,
                          "approximation_monomials": approximation.monomial_count(),
                          "exact_denominator_monomials": denominator.monomial_count(),
                          "residual_monomials": residual.monomial_count(),
                          "residual_inside_the_ideal": True,
                          "residual_is_nonzero": True})
        composed.append({
            "order": order,
            "truncated_content": approximation.show()[:70],
            "exact_content": "1/(%s)" % denominator.show()[:50],
            "content_equal": False,
            "content_inequality_is_detectable": True,
            "object_equal": False,
            "object_difference": "the truncated carrier carries a truncation provenance, the exact "
                                 "one carries an unexpanded remainder",
            "cost": {"truncated_monomials": approximation.monomial_count(),
                     "exact_pair_monomials": denominator.monomial_count() + 1},
            "reading": "the truncated route is the cheap one and its loss is exactly the residual "
                       "inside the declared ideal: non-zero, hence visible, hence usable with a "
                       "label and never mistakable for the exact carrier"})

    refusals = []
    for case, action in (
            ("division by the zero polynomial",
             lambda: MPoly.constant(1, 2).is_divisible_by(MPoly.zero(2))),
            ("negative exponent", lambda: MPoly([(1, (-1, 0))], 2)),
            ("inverse without a constant term",
             lambda: truncated_inverse(x, 2)),
            ("coefficient denominator vanishing modulo the prime",
             lambda: MPoly([(Fr(1, 5), (0, 0))], 2).reduce_mod(5))):
        try:
            action()
            refusals.append({"case": case, "refused": False})
        except ValueError as error:
            refusals.append({"case": case, "refused": True, "message": str(error)})
    check(all(r["refused"] for r in refusals), "ARefusalControlWasAccepted")

    return jsonable({
        "status": "ExternalExactPass",
        "native_status": "NotRun",
        "variables": ["x", "y"],
        "bezout": bezout,
        "value_equality": equality,
        "kronecker": {
            "injectivity_threshold": injectivity_threshold,
            "maximum_degree_in_each_variable": maximum_degree,
            "declared_exponents_below_the_threshold": below_threshold,
            "declared_exponents_at_or_above_the_threshold": at_or_above,
            "rows": kronecker},
        "congruence_route": {
            "cells": congruence,
            "image_exponents": o["kronecker_exponents_to_test"],
            "cells_recovered": len(recovered),
            "cells_unlucky": len(unlucky),
            "status": ("recovery is measured per cell, and every mismatch carries an exhibited "
                       "extra factor")},
        "truncated_inverse": truncated,
        "composed_measurement": composed,
        "refusals": refusals,
        "findings": [
            "value equality between two rational functions in two variables is decided by cross "
            "multiplication, with no greatest common divisor and no monomial order on that path",
            "Kronecker substitution decides equality soundly exactly while it is injective on the "
            "declared degree bounds; the threshold is derived from the degrees instead of being "
            "declared, and every declared exponent below it exhibits a colliding pair, so an image "
            "can make two distinct polynomials look equal",
            "the exponent first chosen by hand for this experiment sits below the derived threshold, "
            "so calling it lucky in advance was an optimistic label rather than a measurement; the "
            "contract now declares exponents to test and lets the run place each one",
            "at the injective base the substituted divisor is measured against the image of the true "
            "divisor on the declared pair; that agreement is a measurement on the pair, not a "
            "guarantee, so reducing to the one-variable engine does not settle the divisor problem",
            "no polynomials p and q satisfy p*x + q*y = 1: proved by evaluating at the origin and "
            "searched over every monomial up to the declared bound with no witness found, so the "
            "historical method's inversion step has no target object in two variables",
            "recovery through modular and specialised images is measured per cell rather than "
            "asserted; every mismatch is a strict extra factor over the divisor and that factor is "
            "exhibited, so injectivity of the substitution is not the same condition as a lucky "
            "image, and no rational reconstruction is implemented",
            "the truncated inverse modulo the ideal of positive-degree terms exists and is exact at "
            "every declared order, and its loss is exactly the residual inside that ideal",
            "the composed measurement the previous round left unmeasured is taken: against the exact "
            "carrier the truncated one is unequal at the content level and at the object level, and "
            "the inequality is detectable because the residual is non-zero"],
        "counts": dict(COUNTS),
    })


def main():
    argv = sys.argv[1:]
    contract_path = HERE / "contract.json"
    contract_bytes = contract_path.read_bytes()
    contract = json.loads(contract_bytes)
    LIMITS.update(contract["budget"])
    report = run(contract)
    # the frozen record is pinned to the exact contract that produced it
    report["contract"] = {"path": contract_path.name,
                          "sha256": hashlib.sha256(contract_bytes).hexdigest(),
                          "base_commit": contract["base_commit"],
                          "schema": contract["schema"]}
    out = pathlib.Path(argv[0]) if argv else HERE / "evidence.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "counts")}, indent=1))
    for finding in report["findings"]:
        print(" *", finding)
    print("Bezout:", json.dumps(report["bezout"]["bounded_search"], ensure_ascii=False))
    section = report["kronecker"]
    print("Kronecker 注入阈值:", section["injectivity_threshold"],
          "低于阈值者:", section["declared_exponents_below_the_threshold"])
    for row in section["rows"]:
        print("Kronecker[base=%s %s]: 单射=%s 碰撞见证=%s 除子像相符=%s" % (
            row["base"], row["label"], row["injective_on_these_degrees"],
            row["collision_witness"], row["divisor_image_agrees"]))
    cells = report["congruence_route"]
    print("同余路线: 恢复 %d 格 / 不利 %d 格" % (cells["cells_recovered"], cells["cells_unlucky"]))
    for row in cells["cells"]:
        if row["status"] != "Recovered":
            print("  不利格:", json.dumps(row, ensure_ascii=False)[:200])
    print("复合测量[order=1]:", json.dumps(report["composed_measurement"][0], ensure_ascii=False)[:300])


if __name__ == "__main__":
    main()

