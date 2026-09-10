"""Independent Fraction and power-of-two oracles for the public native API."""

import math
import random
from fractions import Fraction

import pytest
from adva import compile_module, load_program


def function(body, signature="((x Real))"):
    return compile_module(
        f"(module audit (export f) (def f (fn {signature} Real {body})))"
    ).function("audit", "f")


def test_rational_literals_match_an_independent_exact_ratio_oracle():
    pairs = [(d + 1, d) for d in range(2**53 + 2, 2**53 + 258)]
    pairs += [(2**53, 2**53 + 1), (2**53 + 1, 2**53), (2**53 + 3, 2**53)]
    pairs += [(1, 2**63 - 1), (-(2**63), 1), (2**63 - 1, 1)]
    rng = random.Random(20260910)
    pairs += [(rng.randrange(-(2**63), 2**63), rng.randrange(1, 2**63)) for _ in range(256)]
    for n, d in pairs:
        compiled = function(f"{n}/{d}", "()")
        expected = float(Fraction(n, d))
        assert compiled.evaluate({}).hex() == expected.hex(), (n, d)
    compiled = function("9007199254740995/9007199254740994", "()")
    assert compiled.evaluate({}) == compiled.numpy_callable()() == 1.0
    assert load_program(compiled.ir).evaluate({}) == 1.0


@pytest.mark.parametrize("scale", [40, 50, 60])
@pytest.mark.parametrize("exponent", [-990, -1000, -1010])
def test_log_chain_returns_a_finite_exact_derivative(scale, exponent):
    compiled = function(f"(log (scale 1/{2**scale} (use x)))")
    value, gradient, certificate = compiled.value_and_gradient({"x": math.ldexp(1.0, exponent)})
    assert math.isfinite(value)
    assert gradient["x"] == math.ldexp(1.0, -exponent)
    assert "adva.builtin:log@2" in certificate["operation_rules"]


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_public_and_direct_native_entry_points_refuse_nonfinite_inputs(value):
    compiled = function("(log (use x))")
    for call in [
        compiled.evaluate_checked,
        compiled.value_and_gradient,
        compiled._native.evaluate,
        compiled._native.value_and_gradient,
    ]:
        with pytest.raises(ValueError, match="nonfinite input"):
            call({"x": value})


def test_output_and_jacobian_overflow_are_separate_refusals():
    compiled = function("(exp (use x))")
    for call in [compiled.evaluate, compiled.value_and_gradient]:
        with pytest.raises(ValueError, match="nonfinite output"):
            call({"x": 1000})
    compiled = function("(log (use x))")
    x = math.ldexp(1.0, -1074)
    assert math.isfinite(compiled.evaluate({"x": x}))
    with pytest.raises(ValueError, match="nonfinite derivative"):
        compiled.value_and_gradient({"x": x})
    objective = compiled.scipy_objective()
    with pytest.raises(ValueError, match="nonfinite derivative"):
        objective.jac([x])
