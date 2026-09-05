"""Exact research oracle for typed (p, q) periods and three-dimensional lifts.

This pure-Python fixture creates no Adva semantic authority.  In particular,
equal integer pairs do not identify phase periods, orbifold orders, torus
slopes, ProgramSlice histories, or knots.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd, lcm

Int2 = tuple[int, int]
Matrix2 = tuple[Int2, Int2]


def det2(matrix: Matrix2) -> int:
    (a, b), (c, d) = matrix
    return a * d - b * c


def multiply2(left: Matrix2, right: Matrix2) -> Matrix2:
    (a, b), (c, d) = left
    (e, f), (g, h) = right
    return ((a * e + b * g, a * f + b * h), (c * e + d * g, c * f + d * h))


def power2(matrix: Matrix2, exponent: int) -> Matrix2:
    if exponent < 0:
        raise ValueError("this finite oracle accepts non-negative powers only")
    result: Matrix2 = ((1, 0), (0, 1))
    factor = matrix
    remaining = exponent
    while remaining:
        if remaining % 2:
            result = multiply2(result, factor)
        factor = multiply2(factor, factor)
        remaining //= 2
    return result


def apply2(matrix: Matrix2, vector: Int2) -> Int2:
    (a, b), (c, d) = matrix
    x, y = vector
    return a * x + b * y, c * x + d * y


@dataclass(frozen=True, slots=True)
class PhasePeriods:
    """Two visible clock periods; not orbifold orders or a torus slope."""

    positive: int
    negative: int

    def __post_init__(self) -> None:
        if self.positive < 1 or self.negative < 1:
            raise ValueError("phase periods must be positive")

    @property
    def joint_return(self) -> int:
        return lcm(self.positive, self.negative)

    @property
    def component_count(self) -> int:
        return gcd(self.positive, self.negative)

    @property
    def primitive_winding(self) -> Int2:
        joint = self.joint_return
        return joint // self.positive, joint // self.negative

    def successor(self, state: Int2) -> Int2:
        return (
            (state[0] + 1) % self.positive,
            (state[1] + 1) % self.negative,
        )

    def orbits(self) -> tuple[tuple[Int2, ...], ...]:
        unseen = {
            (left, right)
            for left in range(self.positive)
            for right in range(self.negative)
        }
        result: list[tuple[Int2, ...]] = []
        while unseen:
            start = min(unseen)
            orbit: list[Int2] = []
            current = start
            while current not in orbit:
                orbit.append(current)
                unseen.remove(current)
                current = self.successor(current)
            assert current == start
            result.append(tuple(orbit))
        return tuple(result)


@dataclass(frozen=True, slots=True)
class OrbifoldOrders:
    """Orders of the two finite points of a hyperbolic (p, q, infinity) orbifold."""

    p: int
    q: int

    def __post_init__(self) -> None:
        if self.p < 2 or self.q < 2:
            raise ValueError("orbifold orders must be at least two")
        if self.p * self.q <= self.p + self.q:
            raise ValueError("(p, q, infinity) must be hyperbolic")

    @property
    def meridians(self) -> tuple[Int2, Int2]:
        return (self.p - 1, -1), (-1, self.q - 1)

    @property
    def gluing_matrix(self) -> Matrix2:
        first, second = self.meridians
        return ((first[0], second[0]), (first[1], second[1]))

    @property
    def filling_homology_order(self) -> int:
        return abs(det2(self.gluing_matrix))

    @property
    def central_lift_torsion(self) -> int | None:
        torsion = gcd(self.p, self.q)
        return torsion if torsion > 1 else None


@dataclass(frozen=True, slots=True)
class TorusSlope:
    """A declared homology class in H_1(T^2); not either kind of period."""

    meridian: int
    longitude: int


def dehn_twist(power: int = 1) -> Matrix2:
    return ((1, power), (0, 1))


def torus_link_pairwise_linking(p: int, q: int) -> int:
    components = gcd(p, q)
    if components < 2:
        raise ValueError("a knot has no pair of distinct components")
    return abs(p * q) // components**2


def test_double_period_torus_splits_into_gcd_many_primitive_orbits() -> None:
    for periods in (
        PhasePeriods(2, 3),
        PhasePeriods(2, 4),
        PhasePeriods(3, 4),
        PhasePeriods(3, 6),
    ):
        orbits = periods.orbits()
        winding = periods.primitive_winding

        assert len(orbits) == periods.component_count
        assert {len(orbit) for orbit in orbits} == {periods.joint_return}
        assert sum(len(orbit) for orbit in orbits) == (
            periods.positive * periods.negative
        )
        assert gcd(*winding) == 1
        assert winding == (
            periods.negative // periods.component_count,
            periods.positive // periods.component_count,
        )


def test_orbifold_orders_control_the_lens_filling_homology_order() -> None:
    for orders in (OrbifoldOrders(2, 3), OrbifoldOrders(2, 4), OrbifoldOrders(3, 4)):
        assert orders.filling_homology_order == (
            orders.p * orders.q - orders.p - orders.q
        )

    assert OrbifoldOrders(2, 3).filling_homology_order == 1
    assert OrbifoldOrders(2, 4).filling_homology_order == 2
    assert OrbifoldOrders(3, 4).filling_homology_order == 5


def test_q4_parity_cover_resolves_the_two_component_cusp_link_data() -> None:
    orders = OrbifoldOrders(2, 4)
    cusp_fibre = (1, 1)
    first_meridian, second_meridian = orders.meridians

    def cover_coordinates(vector: Int2) -> Int2:
        x, y = vector
        if (x + y) % 2:
            raise ValueError("the vector is outside the index-two parity lattice")
        return (x + y) // 2, (x - y) // 2

    assert abs(det2(((1, 1), (1, -1)))) == 2
    assert cover_coordinates(cusp_fibre) == (1, 0)
    assert cover_coordinates(first_meridian) == (0, 1)
    assert cover_coordinates(second_meridian) == (1, -2)
    assert apply2(((1, 0), (0, 1)), (1, 0)) == (1, 0)
    assert (1, 0) == (
        cover_coordinates(second_meridian)[0]
        + 2 * cover_coordinates(first_meridian)[0],
        cover_coordinates(second_meridian)[1]
        + 2 * cover_coordinates(first_meridian)[1],
    )

    periods = PhasePeriods(2, 4)
    assert periods.component_count == 2
    assert torus_link_pairwise_linking(2, 4) == 2


def test_central_lift_abelianization_blocks_a_naive_q4_link_complement() -> None:
    modular = OrbifoldOrders(2, 3)
    q4 = OrbifoldOrders(2, 4)

    # Abelianizing <x,y | x^p = y^q> gives Z plus Z/gcd(p,q).
    assert modular.central_lift_torsion is None
    assert q4.central_lift_torsion == 2

    # A two-component link complement in S^3 has free H_1 of rank two.
    central_lift_h1 = (1, q4.central_lift_torsion)
    two_component_link_h1 = (2, None)
    assert central_lift_h1 != two_component_link_h1


def test_two_visible_periods_close_while_the_dehn_twist_lift_does_not() -> None:
    identity: Matrix2 = ((1, 0), (0, 1))
    transverse = (0, 1)

    for periods in (PhasePeriods(2, 3), PhasePeriods(2, 4), PhasePeriods(3, 4)):
        joint = periods.joint_return
        lifted = power2(dehn_twist(), joint)

        assert lifted == dehn_twist(joint)
        assert lifted != identity
        assert apply2(lifted, transverse) == (joint, 1)
        for visible_modulus in (periods.positive, periods.negative):
            assert tuple(
                tuple(entry % visible_modulus for entry in row) for row in lifted
            ) == identity


def test_equal_numerals_do_not_identify_the_three_pq_roles() -> None:
    periods = PhasePeriods(3, 4)
    orders = OrbifoldOrders(3, 4)
    slope = TorusSlope(3, 4)

    assert periods != orders
    assert orders != slope
    assert slope != periods

    # One pair of numerals yields three different, independently computed features.
    assert periods.component_count == 1
    assert periods.joint_return == 12
    assert orders.filling_homology_order == 5
