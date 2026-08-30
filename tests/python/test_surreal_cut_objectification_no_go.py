from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from adva import link_modules


ORDERED_HOLE_PROGRAMS = r"""
(module surreal-cut-no-go
  (export left-right right-left)

  (def left-right
    (fn ((x Real) (y Real)) Real
      (add
        (frontier
          (use x)
          (use y)))))

  (def right-left
    (fn ((x Real) (y Real)) Real
      (add
        (frontier
          (use y)
          (use x)))))
)
"""


@dataclass(frozen=True, slots=True)
class FiniteSurrealCut:
    """A finite cut presentation, before quotienting to a surreal number."""

    left: tuple[Fraction, ...]
    right: tuple[Fraction, ...]

    def __post_init__(self) -> None:
        if not self.left or not self.right:
            raise ValueError("this bounded calibration requires two-sided cuts")
        if max(self.left) >= min(self.right):
            raise ValueError("every left option must be below every right option")

    def scale(self, factor: Fraction) -> FiniteSurrealCut:
        if factor <= 0:
            raise ValueError("positive scale is required to preserve cut orientation")
        return FiniteSurrealCut(
            tuple(factor * value for value in self.left),
            tuple(factor * value for value in self.right),
        )


def dyadic_birthday(value: Fraction) -> int:
    """Return the Conway birthday of a finite dyadic surreal."""

    denominator = value.denominator
    if denominator & (denominator - 1):
        raise ValueError("the candidate is not dyadic")
    if denominator == 1:
        return abs(value.numerator)
    exponent = denominator.bit_length() - 1
    return abs(value.numerator) // denominator + exponent + 1


def _ceil(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def objectify(cut: FiniteSurrealCut) -> Fraction:
    """Find the unique least-birthday dyadic strictly inside a finite cut."""

    lower = max(cut.left)
    upper = min(cut.right)
    candidates: set[Fraction] = set()
    for exponent in range(8):
        denominator = 1 << exponent
        first = (lower.numerator * denominator) // lower.denominator + 1
        last = _ceil(upper * denominator) - 1
        candidates.update(Fraction(numerator, denominator) for numerator in range(first, last + 1))

    least_birthday = min(dyadic_birthday(value) for value in candidates)
    simplest = sorted(
        value for value in candidates if dyadic_birthday(value) == least_birthday
    )
    if len(simplest) != 1:
        raise AssertionError(f"expected one simplest dyadic, got {simplest}")
    return simplest[0]


def test_surreal_objectification_is_not_natural_under_positive_scaling() -> None:
    cut = FiniteSurrealCut((Fraction(0),), (Fraction(1),))
    scaled = cut.scale(Fraction(3))

    assert objectify(cut) == Fraction(1, 2)
    assert objectify(scaled) == Fraction(1)
    assert Fraction(3) * objectify(cut) == Fraction(3, 2)
    assert objectify(scaled) != Fraction(3) * objectify(cut)


def test_objectification_collision_blocks_a_retraction_on_cut_presentations() -> None:
    narrow = FiniteSurrealCut((Fraction(0),), (Fraction(2),))
    wide = FiniteSurrealCut((Fraction(0),), (Fraction(3),))

    assert narrow != wide
    assert objectify(narrow) == objectify(wide) == Fraction(1)


def test_equal_arithmetic_value_does_not_forget_ordered_hole_binding() -> None:
    workspace = link_modules([ORDERED_HOLE_PROGRAMS])
    left_right = workspace.function("surreal-cut-no-go", "left-right")
    right_left = workspace.function("surreal-cut-no-go", "right-left")

    assert left_right.evaluate({"x": 2, "y": 3}) == 5
    assert right_left.evaluate({"x": 2, "y": 3}) == 5

    left_inputs = left_right.ir["nodes"][0]["inputs"]
    right_inputs = right_left.ir["nodes"][0]["inputs"]
    assert [wire["producer"]["index"] for wire in left_inputs] == [0, 1]
    assert [wire["producer"]["index"] for wire in right_inputs] == [1, 0]
    assert left_right.ir != right_left.ir
