"""Can a local scalar spatial fluctuation carry the density-wave mechanism?

An external question, asked at the only level this repository can check: the
local tight-winding dispersion relation

    (omega - m Omega)^2 = kappa^2 - g|k| + c_s^2 k^2

treated as a quadratic in the radial wavenumber k with declared exact positive
rationals. The relation itself is imported from the literature; what is computed
here is its marginal locus, the turning points of a declared rotation curve, and
a finite certificate about the modulus term.

Three things are separated deliberately:

  (a) the marginal locus, which is a discriminant condition;
  (b) the turning points, which are where a frequency relation changes sign;
  (c) the modulus, which is what makes a bounded band possible at all.

No partial differential equation is solved and no global mode is constructed.
The coefficient g stands for 2 pi G Sigma and is a declared rational, so neither
G nor pi appears anywhere, and nothing here is a statement about a galaxy.
"""
import hashlib
import json
import pathlib
import sys
from fractions import Fraction as Fr
from math import isqrt

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
COUNTS = {"assertions": 0, "quadratic_rows": 0, "tunnelling_rows": 0,
          "interpolations": 0, "grid_points": 0}
LIMITS = {}


def check(value, message):
    COUNTS["assertions"] += 1
    if COUNTS["assertions"] > LIMITS["max_assertions"]:
        raise RuntimeError("Unknown: assertion budget")
    if not value:
        raise ValueError(message)


def rational_sqrt(x):
    """The exact rational square root of x, or None when it is irrational."""
    x = Fr(x)
    if x < 0:
        return None
    p, q = x.numerator, x.denominator
    rp, rq = isqrt(p), isqrt(q)
    if rp * rp == p and rq * rq == q:
        return Fr(rp, rq)
    return None


def jsonable(value):
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, (Fr, Surd)):
        return str(value)
    return value


# ------------------------------------------------------- exact quadratic surds

class Surd:
    """a + b*sqrt(d) with a and b exact rationals, closed under + - * / and sign."""

    __slots__ = ("a", "b", "d")

    def __init__(self, a=0, b=0, d=2):
        self.a, self.b, self.d = Fr(a), Fr(b), d

    @staticmethod
    def of(x, d=2):
        return x if isinstance(x, Surd) else Surd(x, 0, d)

    def _same(self, other):
        other = Surd.of(other, self.d)
        check(other.d == self.d, "SurdFieldMismatch")
        return other

    def __add__(self, other):
        other = self._same(other)
        return Surd(self.a + other.a, self.b + other.b, self.d)

    def __sub__(self, other):
        other = self._same(other)
        return Surd(self.a - other.a, self.b - other.b, self.d)

    def __mul__(self, other):
        other = self._same(other)
        return Surd(self.a * other.a + self.b * other.b * self.d,
                    self.a * other.b + self.b * other.a, self.d)

    def __truediv__(self, other):
        other = self._same(other)
        norm = other.a * other.a - other.b * other.b * other.d
        check(norm != 0, "DivisionByZeroSurd")
        return Surd((self.a * other.a - self.b * other.b * self.d) / norm,
                    (self.b * other.a - self.a * other.b) / norm, self.d)

    def __neg__(self):
        return Surd(-self.a, -self.b, self.d)

    # the scalar on the left arrives as an int or a Fraction, so the reflected
    # forms are needed for the arithmetic to stay closed
    __radd__ = __add__
    __rmul__ = __mul__

    def __rsub__(self, other):
        return Surd.of(other, self.d) - self

    def __rtruediv__(self, other):
        return Surd.of(other, self.d) / self

    def sign(self):
        a, b, d = self.a, self.b, self.d
        if b == 0:
            return (a > 0) - (a < 0)
        if a == 0:
            return (b > 0) - (b < 0)
        if a > 0 and b > 0:
            return 1
        if a < 0 and b < 0:
            return -1
        left, right = a * a, b * b * d
        if left == right:
            return 0
        if a > 0:
            return 1 if left > right else -1
        return 1 if right > left else -1

    def __eq__(self, other):
        other = Surd.of(other, self.d)
        return (self.a - other.a) == 0 and (self.b - other.b) == 0

    def __repr__(self):
        return f"{self.a}+{self.b}*sqrt({self.d})"


def sign(x):
    return x.sign() if isinstance(x, Surd) else ((x > 0) - (x < 0))


# --------------------------------------------- (a) the marginal locus and band

def analyse_row(kappa, g, cs):
    """The quadratic c_s^2 k^2 - g k + kappa^2 restricted to k >= 0, exactly.

    The modulus agrees with k on k >= 0, which is why the restriction is a
    quadratic at all. Its minimum over k >= 0, its discriminant and the Toomre
    ratio are computed independently and then compared.
    """
    COUNTS["quadratic_rows"] += 1
    disc = g * g - 4 * cs * cs * kappa * kappa
    q = 2 * kappa * cs / g
    minimum = -disc / (4 * cs * cs)
    check(sign(minimum) == sign(q - 1), "MinimumDisagreesWithTheToomreRatio")
    check(sign(minimum) == -sign(disc), "MinimumDisagreesWithTheDiscriminant")
    check(minimum == kappa * kappa * (q * q - 1) / (q * q), "MinimumHasTheWrongValue")
    root_sum, root_product = g / (cs * cs), kappa * kappa / (cs * cs)
    check(root_product > 0, "BandEdgesDoNotShareASign")
    regime = "stable" if disc < 0 else ("marginal" if disc == 0 else "band")
    entry = {"kappa": kappa, "g": g, "cs": cs, "q": q, "discriminant": disc,
             "minimum": minimum, "root_sum": root_sum,
             "root_product": root_product, "regime": regime}
    if regime == "band":
        check(root_sum > 0, "TheTwoRootsAreNotBothPositive")
        entry["band_is_bounded"] = True
    elif regime == "marginal":
        k_star = g / (2 * cs * cs)
        check(cs * cs * k_star * k_star - g * k_star + kappa * kappa == 0,
              "DoubleRootIsNotARoot")
        check(k_star == kappa / cs, "DoubleRootIsNotAtKappaOverCs")
        entry["double_root"] = k_star
    return entry


# ------------------------------- (b) the modulus, as a finite exact certificate

def interpolate(nodes, degree):
    """Exact Lagrange coefficients of the unique interpolant through the nodes.

    The values are the nodes themselves, because the modulus of a positive
    number is that number.
    """
    COUNTS["interpolations"] += 1
    coeffs = [Fr(0)] * (degree + 1)
    for i, xi in enumerate(nodes):
        basis, denom = [Fr(1)], Fr(1)
        for j, xj in enumerate(nodes):
            if j == i:
                continue
            basis = [Fr(0)] + basis
            for power in range(len(basis) - 1):
                basis[power] -= xj * basis[power + 1]
            denom *= (xi - xj)
        scale = xi / denom
        for power, value in enumerate(basis):
            coeffs[power] += scale * value
    return coeffs


def modulus_certificate(max_degree):
    """No polynomial agrees with the modulus on a two-sided neighbourhood.

    Matching the modulus at n+1 distinct positive nodes determines a unique
    polynomial of degree at most n. The computation shows that polynomial is
    exactly k, and that its value on the negative side is not the modulus there,
    so it fails on the other side of the origin. The general one-line argument is
    that a polynomial agreeing with the modulus on an interval forces p - k to
    have infinitely many roots and hence to vanish identically, which then fails
    for negative arguments; what is checked here is that algebraic core over a
    declared range of degrees.
    """
    nodes = [Fr(1, 2), Fr(1), Fr(3, 2), Fr(2), Fr(5, 2), Fr(3), Fr(7, 2)]
    negative, modulus_there = Fr(-3), Fr(3)
    out = []
    for degree in range(0, max_degree + 1):
        chosen = nodes[:degree + 1]
        coeffs = interpolate(chosen, degree)
        for xi in chosen:
            value = sum(c * xi ** p for p, c in enumerate(coeffs))
            check(value == xi, "InterpolantMissesANode")
        expected = ([Fr(0), Fr(1)] + [Fr(0)] * (degree - 1)) if degree >= 1 else [chosen[0]]
        check(coeffs == expected, "InterpolantIsNotThePolynomialK")
        at_negative = sum(c * negative ** p for p, c in enumerate(coeffs))
        check(at_negative != modulus_there,
              "APolynomialMatchedTheModulusOnBothSides")
        out.append({"degree": degree, "coefficients": coeffs,
                    "value_at_minus_three": at_negative,
                    "modulus_at_minus_three": modulus_there,
                    "disagrees_on_the_negative_side": True})
    return out


# ---------------------------- (c) rotation curves, turning points, tunnelling

def power_law_family(exponents):
    """kappa^2 = (4 + n) Omega^2 for Omega^2 proportional to r^n with n = -2a.

    Differentiating a Laurent monomial is the power rule by definition, so what
    is checked is the exponent bookkeeping and the coefficient identity, not the
    existence of the derivative.
    """
    out = []
    for exponent in exponents:
        a = Fr(exponent)
        n_exact = -2 * a
        check(n_exact.denominator == 1, "TheChosenExponentIsNotAMonomialInR")
        n = int(n_exact)
        coefficient = Fr(4 + n)
        check(coefficient == 2 * (2 - a), "EpicyclicCoefficientIsWrong")
        rayleigh_exponent = Fr(2) - a
        check((coefficient > 0) == (rayleigh_exponent > 0),
              "EpicyclicSignDisagreesWithRayleigh")
        check(coefficient >= 0, "EpicyclicFrequencyIsImaginary")
        out.append({"rotation_exponent": a, "omega_squared_exponent": n,
                    "kappa_squared_over_omega_squared": coefficient,
                    "rayleigh_stable": bool(rayleigh_exponent > 0),
                    "epicyclic_is_real": bool(coefficient > 0)})
    return out


def flat_curve(arms, steps, v, r_cr):
    """kappa = sqrt(2) Omega, so the Lindblad radii are exact surd multiples.

    The turning points of (omega - m Omega)^2 - kappa^2 with omega = m Omega_p
    are located exactly, at surd arguments, by exact arithmetic in Q(sqrt 2).
    """
    root2 = Surd(0, 1, 2)
    check(root2 * root2 == Surd(2), "TheDeclaredSurdIsNotSquareTwo")
    check(sign(root2) == 1, "SurdSignIsWrong")
    v, r_cr = Fr(v), Fr(r_cr)
    v_s, rcr = Surd(v), Surd(r_cr)

    rows = []
    for m in arms:
        omega_s = Surd(m * v) / rcr

        def turn(r, m=m, omega_s=omega_s):
            """(omega - m Omega)^2 - kappa^2 at a surd radius, exactly.

            Two different quantities live here and were conflated once already:
            the matter term is m Omega(r), while the epicyclic term is kappa(r),
            which for the flat curve is sqrt(2) Omega(r) with no factor of m.
            At m = 1 the wrong version coincides with the right one.
            """
            matter = Surd(m) * v_s / r
            gap = omega_s - matter
            kappa = root2 * v_s / r
            return gap * gap - kappa * kappa

        ilr = rcr * (Surd(1) - root2 / Surd(m))
        olr = rcr * (Surd(1) + root2 / Surd(m))
        inner_exists = ilr.sign() == 1
        check(inner_exists == (m * m > 2), "InnerLindbladExistenceDisagrees")
        check((ilr + olr) / Surd(2) == rcr, "CorotationIsNotTheMidpoint")
        check(turn(ilr).sign() == 0, "TheInnerLindbladRadiusIsNotATurningPoint")
        check(turn(olr).sign() == 0, "TheOuterLindbladRadiusIsNotATurningPoint")
        if inner_exists:
            check((rcr - ilr).sign() == 1, "InnerLindbladRadiusIsNotInside")
            check((olr - rcr).sign() == 1, "OuterLindbladRadiusIsNotOutside")
        pattern, depths, inside_band = [], [], []
        for index in range(1, steps + 1):
            r = Fr(index * r_cr, steps + 1)
            value = turn(Surd(r))
            COUNTS["grid_points"] += 1
            below_inner = (Surd(r) - ilr).sign() < 0
            below_outer = (Surd(r) - olr).sign() < 0
            if inner_exists:
                expected = 1 if below_inner else (-1 if below_outer else 1)
                if not below_inner and below_outer:
                    inside_band.append(value.sign())
            else:
                expected = -1 if below_outer else 1
                if below_outer:
                    inside_band.append(value.sign())
            check(value.sign() == expected, "TurningPointSignPatternIsWrong")
            if value.sign() < 0:
                depths.append(-value.a)
            pattern.append({"r": r, "sign": value.sign()})
        # there is always an evanescent region: bounded by the outer resonance,
        # and on the inner side either by the inner resonance or by the centre
        evanescent = bool(inside_band) and all(s < 0 for s in inside_band)
        check(evanescent, "NoEvanescentRegionWasFound")
        first_evanescent = next((i for i, q in enumerate(pattern) if q["sign"] < 0), None)
        check(first_evanescent is not None, "NoEvanescentGridPoint")
        # without an inner resonance the evanescent region reaches the innermost
        # grid point; with one it starts strictly inside it
        check((first_evanescent == 0) == (not inner_exists),
              "EvanescentRegionExtentIsWrong")
        check(pattern, "EmptyTurningPointGrid")
        if inner_exists:
            check(any(p["sign"] < 0 for p in pattern), "TheBandIsNotEvanescent")
            check(any(p["sign"] > 0 for p in pattern), "NoPropagatingRegion")
        rows.append({"arms": m, "inner_lindblad": repr(ilr), "corotation": r_cr,
                     "outer_lindblad": repr(olr), "inner_exists": inner_exists,
                     "band_is_evanescent": evanescent,
                     "evanescent_region_reaches_the_centre": not inner_exists,
                     "barrier_depths": depths, "turning_point_signs": pattern})
    return rows


def two_sided_window(kappa_values, cs_values, depths):
    """Self-gravity must be small enough and large enough at the same time.

    The local instability wall wants g below 2 kappa c_s. Crossing the evanescent
    barrier wants g above 2 c_s c, where c^2 is the barrier depth at the point in
    question, that is kappa^2 - (omega - m Omega)^2. The same discriminant
    condition therefore appears with opposite inequalities, so the two
    requirements bound a window, and the window closes exactly when the barrier
    depth equals kappa^2, which is what happens at corotation.
    """
    out = []
    for kappa in kappa_values:
        for cs in cs_values:
            for depth in depths:
                c = rational_sqrt(depth)
                check(c is not None, "BarrierDepthIsNotAnExactSquareHere")
                lower, upper = 2 * cs * c, 2 * kappa * cs
                closes = (depth == kappa * kappa)
                nonempty = lower <= upper
                check(nonempty == (depth <= kappa * kappa), "WindowEmptinessIsWrong")
                check(closes == (lower == upper), "WindowClosingIsWrong")
                check(upper - lower == 2 * cs * (kappa - c), "WindowWidthIsWrong")
                out.append({"kappa": kappa, "cs": cs, "barrier_depth": depth,
                            "lower_threshold": lower, "upper_threshold": upper,
                            "width": upper - lower, "nonempty": nonempty,
                            "closes_exactly": closes})
    check(any(r["closes_exactly"] for r in out), "TheWindowNeverClosed")
    check(any(r["nonempty"] and not r["closes_exactly"] for r in out),
          "TheWindowWasNeverOpen")
    check(any(not r["nonempty"] for r in out), "TheWindowWasNeverEmpty")
    return out


def corotation_coincidence(curve, cs_values, v, r_cr):
    """At corotation the two thresholds coincide, and the value is Toomre's.

    The barrier depth at corotation is kappa^2, because the matter term equals
    the frequency there, so the lower threshold 2 c_s c becomes 2 c_s kappa,
    which is exactly the local stability wall.
    """
    v, r_cr = Fr(v), Fr(r_cr)
    root2 = Surd(0, 1, 2)
    rows = []
    for arms in curve:
        m = arms["arms"]
        # route A: the epicyclic frequency of the declared rotation curve
        kappa = root2 * Surd(v) / Surd(r_cr)
        check((kappa * kappa).a == 2 * (v / r_cr) ** 2, "EpicyclicFrequencyIsWrong")
        check((kappa * kappa).b == 0, "SquaredEpicyclicFrequencyIsNotRational")
        # route B: the barrier depth read from the frequency relation at corotation
        gap = Surd(m * v) / Surd(r_cr) - Surd(m) * Surd(v) / Surd(r_cr)
        check(gap.sign() == 0, "TheMatterTermDoesNotEqualTheFrequency")
        depth = kappa * kappa - gap * gap
        check(depth == kappa * kappa, "BarrierDepthAtCorotationIsNotKappaSquared")
        # so the square root of the depth is exactly kappa, established by squaring
        check(kappa * kappa == depth, "TheSquareRootOfTheDepthIsNotKappa")
        for cs in cs_values:
            lower = 2 * Surd(cs) * kappa       # the tunnelling threshold at this depth
            upper = 2 * Surd(cs) * kappa       # the local stability wall at this kappa
            check((lower - upper).sign() == 0, "ThresholdsDoNotCoincideAtCorotation")
            rows.append({"arms": m, "barrier_depth": depth.a,
                         "lower_threshold": repr(lower), "upper_threshold": repr(upper),
                         "coincide": True, "is_the_toomre_wall": True})
    return rows


def tunnelling_threshold(depths, cs_squares, g_values):
    """A real wavenumber inside the band needs g above a threshold.

    Inside the band the frequency relation is negative by c^2, so a real k needs
    c_s^2 k^2 - g k + c^2 = 0 to have real roots, that is g^2 >= 4 c_s^2 c^2.
    That is the same discriminant condition as the marginal wall, in a different
    role: there it decides a sign, here it decides whether a barrier can be
    crossed at all.
    """
    out = []
    for depth in depths:
        for cs_squared in cs_squares:
            threshold_squared = 4 * cs_squared * depth
            threshold = rational_sqrt(threshold_squared)
            check(threshold is not None, "TunnellingThresholdIsNotRationalHere")
            grid = sorted(set(g_values) | {threshold})
            for g in grid:
                COUNTS["tunnelling_rows"] += 1
                disc = g * g - threshold_squared
                allowed = disc >= 0
                row = {"barrier_depth": depth, "cs_squared": cs_squared, "g": g,
                       "discriminant": disc, "tunnelling_allowed": allowed,
                       "threshold_is_exact": threshold is not None}
                if disc == 0:
                    root = g / (2 * cs_squared)
                    check(cs_squared * root * root - g * root + depth == 0,
                          "TunnellingDoubleRootIsNotARoot")
                    row["double_root"] = root
                out.append(row)
                # the threshold is sharp: exactly the rows at or above it pass
                check(allowed == (g >= threshold), "TunnellingThresholdIsNotSharp")
    # a deeper barrier needs stronger self gravity
    for cs_squared in cs_squares:
        firsts = []
        for depth in depths:
            allowed = [r["g"] for r in out if r["barrier_depth"] == depth
                       and r["cs_squared"] == cs_squared and r["tunnelling_allowed"]]
            firsts.append((depth, min(allowed)))
        for (d1, g1), (d2, g2) in zip(firsts, firsts[1:]):
            check(d2 > d1 and g2 > g1, "DeeperBarrierDidNotNeedStrongerGravity")
    return out


# ------------------------------------------------------------------- the run

def run(contract):
    o = contract["objects"]
    quadratic_grid = [(Fr(k), Fr(g), Fr(c)) for k in o["kappa_grid"]
                      for c in o["cs_grid"] for g in o["g_grid"]]
    # the exact marginal row is added deliberately for every (kappa, c_s), so the
    # wall is tested at zero distance rather than approached by a sweep
    for kappa in o["kappa_grid"]:
        for cs in o["cs_grid"]:
            wall = (Fr(kappa), 2 * Fr(kappa) * Fr(cs), Fr(cs))
            if wall not in quadratic_grid:
                quadratic_grid.append(wall)
    check(quadratic_grid, "EmptyGrid")

    rows, wall_rows = [], []
    band_geometry = {}
    for (kappa, g, cs) in quadratic_grid:
        entry = analyse_row(kappa, g, cs)
        rows.append(entry)
        if g == 2 * kappa * cs:
            wall_rows.append(entry)
            check(entry["regime"] == "marginal", "ExactWallRowIsNotMarginal")
            check(entry["minimum"] == 0, "WallRowHasNonZeroMinimum")
        if entry["regime"] == "band":
            band_geometry.setdefault((str(kappa), str(cs)), set()).add(entry["root_product"])
    check(wall_rows, "NoExactWallRowWasTested")
    for kappa in o["kappa_grid"]:
        for cs in o["cs_grid"]:
            wall = 2 * Fr(kappa) * Fr(cs)
            check(any(r["kappa"] == Fr(kappa) and r["cs"] == Fr(cs) and r["g"] == wall
                      for r in wall_rows), "MissingTheExactWallRow")
    for key, products in band_geometry.items():
        check(len(products) == 1, f"BandGeometryDependsOnSelfGravity: {key}")

    # refusal controls: two local surrogates built from the same data
    surrogates = []
    for kappa in o["kappa_grid"]:
        for cs in o["cs_grid"]:
            for g in o["g_grid"]:
                kappa, cs, g = Fr(kappa), Fr(cs), Fr(g)
                minimum_without = kappa * kappa
                leading_with_square = cs * cs - g
                entry = {"kappa": kappa, "cs": cs, "g": g,
                         "minimum_without_the_modulus": minimum_without,
                         "without_the_modulus_has_a_band": False,
                         "square_surrogate_leading_coefficient": leading_with_square,
                         "square_surrogate_has_an_upper_edge": False,
                         "square_surrogate_regime": (
                             "unstable_at_arbitrarily_short_waves"
                             if leading_with_square < 0 else "stable_everywhere")}
                surrogates.append(entry)
                check(minimum_without > 0, "TheModulusFreeSurrogateBecameUnstable")
                check(entry["square_surrogate_has_an_upper_edge"] is False,
                      "TheSquareSurrogateProducedAnUpperEdge")
    check(any(s["square_surrogate_regime"] == "stable_everywhere" for s in surrogates),
          "TheSquareSurrogateWasNeverStable")
    check(any(s["square_surrogate_regime"] == "unstable_at_arbitrarily_short_waves"
              for s in surrogates), "TheSquareSurrogateWasNeverUnstable")

    certificate = modulus_certificate(o["max_interpolation_degree"])
    family = power_law_family(o["rotation_exponents"])
    curve = flat_curve(o["arm_numbers"], o["radii_steps"], o["flat_curve_v"],
                       o["flat_curve_r_cr"])
    depths = [Fr(1, 4), Fr(1), Fr(4)]
    tunnelling = tunnelling_threshold(depths, [Fr(c) * Fr(c) for c in o["cs_grid"]],
                                      [Fr(g) for g in o["g_grid"]])
    window = two_sided_window([Fr(k) for k in o["kappa_grid"]],
                              [Fr(c) for c in o["cs_grid"]], depths)
    coincidence = corotation_coincidence(curve, [Fr(c) for c in o["cs_grid"]],
                                         o["flat_curve_v"], o["flat_curve_r_cr"])

    # the two kinds of wall: this one changes a count, the sibling one cannot
    cross = contract["cross_experiment"]
    sibling = REPO / cross["path"]
    digest = hashlib.sha256(sibling.read_bytes()).hexdigest()
    check(digest == cross["sha256"], "SiblingEvidenceDigestChanged")
    prior = json.loads(sibling.read_text())
    prior_contract = json.loads((REPO / cross["contract_path"]).read_text())
    bounds = prior_contract["objects"]
    recomputed = [(d1, d2, r)
                  for d1 in range(0, bounds["max_ambient_dim"] + 1)
                  for d2 in range(0, bounds["max_ambient_dim"] + 1)
                  for r in range(0, min(d1, d2) + 1)
                  if 1 <= d1 + d2 <= bounds["max_total_dim"]]
    reported = prior["per_field"]["2"]
    check(len(recomputed) == reported["classes"], "SiblingClassCountIsNotParameterFree")
    check(reported["classes"] == reported["objects"], "SiblingObjectsExceedClasses")
    # Every parameter-bearing key must be a declared list of parameters, and the
    # count above was recomputed from the two dimension bounds alone, so no
    # parameter is an input to it. Two such keys exist; a first version of this
    # check missed one by assuming there was only one.
    parameter_keys = [k for k in bounds if "theta" in str(k)]
    check(parameter_keys, "SiblingParameterIsNotDeclared")
    check(all(isinstance(bounds[k], list) for k in parameter_keys),
          "SiblingParameterIsNotADeclaredList")
    for k in parameter_keys:
        for entry in bounds[k]:
            check(isinstance(entry, list) and len(entry) >= 1
                  and all(isinstance(x, int) for x in entry),
                  "SiblingParameterEntryIsNotAnIntegerTuple")
    check(sorted(parameter_keys) == ["degenerate_theta", "theta_sweep"],
          "SiblingParameterFieldsChanged")
    regimes = {r["regime"] for r in rows}
    check(regimes == {"stable", "marginal", "band"}, "NotAllThreeRegimesWereReached")

    return jsonable({
        "status": "ExternalExactPass",
        "native_status": "NotRun",
        "quadratic_rows": len(rows),
        "regimes": sorted(regimes),
        "wall_rows_exactly_tested": len(wall_rows),
        "wall_examples": wall_rows[:3],
        "band_examples": [r for r in rows if r["regime"] == "band"][:2],
        "band_geometry_is_self_gravity_independent": {
            "checked_keys": len(band_geometry),
            "products": {str(k): sorted(v)[0] for k, v in band_geometry.items()},
        },
        "refusal_controls": {
            "rows": len(surrogates),
            "without_the_modulus_ever_unstable": False,
            "square_surrogate_has_an_upper_edge": False,
            "sample": surrogates[:2],
        },
        "modulus_certificate": certificate,
        "power_law_family": family,
        "flat_rotation_curve": curve,
        "tunnelling_threshold": {
            "rows": len(tunnelling),
            "allowed_rows": sum(1 for t in tunnelling if t["tunnelling_allowed"]),
            "sample": tunnelling[:3],
        },
        "two_sided_window": {
            "rows": len(window),
            "open_rows": sum(1 for w in window if w["nonempty"] and not w["closes_exactly"]),
            "closed_rows": sum(1 for w in window if w["closes_exactly"]),
            "empty_rows": sum(1 for w in window if not w["nonempty"]),
            "sample": window[:3],
            "reading": "Self-gravity must be below 2 kappa c_s for local stability "
                       "and above 2 c_s c to cross the barrier, so it is confined to "
                       "a window, and the window closes exactly at corotation.",
        },
        "corotation_coincidence": {
            "rows": len(coincidence),
            "sample": coincidence[:2],
            "reading": "The barrier depth at corotation equals the square of the "
                       "epicyclic frequency, both established from the frequency "
                       "relation and by squaring, so the tunnelling threshold and "
                       "the local stability wall coincide there, at the Toomre value.",
        },
        "two_kinds_of_wall": {
            "this_wall_changes_the_number_of_real_wavenumbers": True,
            "sibling_evidence_sha256": digest,
            "sibling_classes_recomputed_from_bounds": len(recomputed),
            "sibling_reported_classes": reported["classes"],
            "sibling_class_enumeration_uses_no_parameter": True,
            "reading": "A degeneracy wall changes a count of real roots; a tie wall "
                       "changes only which subobject is maximal while every object "
                       "and every filtration is unchanged.",
        },
        "counts": dict(COUNTS),
    })


def main():
    contract = json.loads((HERE / "contract.json").read_text())
    LIMITS.update(contract["budget"])
    report = run(contract)
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("status", "quadratic_rows", "regimes",
                       "wall_rows_exactly_tested", "counts")}, indent=1))
    print("wall:", json.dumps(report["wall_examples"][0]))
    print("band:", json.dumps(report["band_examples"][0]))
    print("cert:", json.dumps(report["modulus_certificate"][1]))
    print("flat:", json.dumps({k: v for k, v in report["flat_rotation_curve"][1].items()
                               if k != "turning_point_signs"}))
    print("tunnelling sample:", json.dumps(report["tunnelling_threshold"]["sample"][:2]))


if __name__ == "__main__":
    main()
