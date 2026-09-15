"""The (i - e)^(i - e) conjecture is refuted on its principal reading.

Research 0171 records a conjecture put to the repository and reports what can be
decided about it. This test holds the result in place: the principal branch must
stay refuted by the modulus being below one, the branch family must stay refuted
from minus six to six, the near misses must stay reported as distances, and the
undecided general case must stay undecided rather than being reported as false.
"""

import importlib.util
import json
import math
import subprocess
import sys
import tomllib
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/integer_power_absurdity"
CHECKER = HERE / "calibration.py"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0172-the-i-minus-e-integrality-conjecture.md"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def branch(report, index):
    match = [r for r in report["branches"] if r["branch_index"] == index]
    assert len(match) == 1, index
    return match[0]


def test_the_principal_branch_is_refuted_by_its_modulus():
    report = load(EVIDENCE)
    assert report["status"] == "ExternalExactPass"
    assert report["native_status"] == "NotRun"
    principal = report["principal_branch"]
    assert principal["verdict"] == "Refuted"
    modulus = principal["modulus"]
    assert Fraction(modulus["hi"]) < 1, "the modulus must be strictly below one"
    assert Fraction(modulus["hi"]) < Fraction(1, 10), "and below the certified bound"
    assert Fraction(modulus["lo"]) > 0, "and strictly above zero"
    exponent = principal["rational_exponent"]
    assert Fraction(exponent["hi"]) < 0, "the rational exponent must be negative"


def test_the_certified_bound_is_elementary_and_carries_no_approximation():
    bound = load(EVIDENCE)["elementary_bound"]
    assert bound["certified_upper_bound"] == "1/10"
    assert "ln 2" in bound["a_lower"] and "3/2" in bound["b_lower"]


def test_every_branch_from_minus_six_to_six_is_refuted():
    report = load(EVIDENCE)
    assert report["verdict_counts"]["unknown"] == 0
    assert report["verdict_counts"]["refuted"] == 13
    for row in report["branches"]:
        assert row["verdict"] == "Refuted", row["branch_index"]
    for index in range(0, 7):
        row = branch(report, index)
        assert Fraction(row["real_exponent"]["hi"]) < 0, index
        assert "between 0 and 1" in row["reason"], index
    for index in range(-6, 0):
        row = branch(report, index)
        assert Fraction(row["real_exponent"]["lo"]) > 0, index
        assert row["integers_inside_the_modulus_enclosure"] == [], index
        assert "contains no integer" in row["reason"], index


def test_the_near_misses_are_reported_as_distances():
    report = load(EVIDENCE)
    row = branch(report, -2)
    assert row["nearest_integer_to_the_modulus"] == 979
    distance = Fraction(row["distance_to_that_integer"])
    assert 0 < distance < Fraction(1, 10), "the near miss must stay a near miss"
    for index in range(-6, 0):
        entry = branch(report, index)
        assert Fraction(entry["distance_to_that_integer"]) > 0, index


def test_the_constants_are_derived_and_cross_checked():
    report = load(EVIDENCE)
    constants = report["constants"]
    assert constants["e_source"].startswith("the exponential series")
    assert "Machin" in constants["pi_source"]
    checks = report["consistency_checks"]
    assert sorted(checks["published_constants_cross_checked"]) == ["e", "ln2", "pi"]
    for key in ("e", "pi"):
        enclosure = constants[key]
        assert Fraction(enclosure["hi"]) > Fraction(enclosure["lo"])
    norm = checks["pythagorean_norm"]
    assert Fraction(norm["lo"]) <= 1 <= Fraction(norm["hi"])


def test_the_undecided_general_case_is_not_reported_as_false():
    note = NOTE.read_text(encoding="utf-8")
    assert "decided here" in note and "**not** decided here" in note
    assert "Unknown" in note
    contract = load(HERE / "contract.json")
    residual = contract["residual"]
    assert "not decided" in residual
    assert "Schanuel" in residual
    assert contract["protected"], "the protected list must survive"
    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims if c["claim_id"] == "adva.exact.i-minus-e-power-integrality.v0"]
    assert len(match) == 1
    assert match[0]["status"] == "exact"
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "A refuted branch with a refuted conjecture" in forbidden


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    output = tmp_path / "fresh.json"
    completed = subprocess.run(
        [sys.executable, str(CHECKER), str(output)],
        capture_output=True, text=True, timeout=300, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert load(output) == load(EVIDENCE)


# ------------------------------------------------- the exponential enclosure helper

GRID_STEP = Fraction(1, 10 ** 45)


def checker_module():
    """Import the checker to call a helper directly, as the discovery probes do."""
    spec = importlib.util.spec_from_file_location("absurdity_enclosure", CHECKER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.LIMITS["max_assertions"] = 100000
    return module


def exp_bounds(t, terms=60):
    """Rigorous L <= exp(t) <= U for rational t, by the direct series.

    This oracle is deliberately not the checker: it uses no argument halving and
    squaring, no outward rounding onto the precision grid, and no interval type.
    For t >= 0 the remainder after n terms is at most
    t^(n+1)/(n+1)! * 1/(1 - t/(n+2)); for t < 0 the reciprocal of exp(-t) is used
    and the two bounds exchange places.
    """
    if t < 0:
        low, high = exp_bounds(-t, terms)
        return 1 / high, 1 / low
    total = Fraction(0)
    for k in range(terms + 1):
        total += t ** k / math.factorial(k)
    tail = t ** (terms + 1) / math.factorial(terms + 1) / (1 - t / (terms + 2))
    return total, total + tail


def test_the_exponential_helper_encloses_an_interval_that_crosses_zero():
    """exp([-1,1]) is [exp(-1), exp(1)], and exp(-1) is strictly below one.

    The crossing-zero branch returned exp(0) = 1 as its lower bound, so the
    interval could not contain exp at any negative argument. Because exp is
    increasing the image of [lo, hi] is exactly [exp(lo), exp(hi)], so requiring
    lo <= exp(x.lo) and hi >= exp(x.hi) is both necessary and sufficient here.

    The comparison allows one step of the checker's own declared precision grid
    (10^45), since every endpoint is snapped outward onto it. The independent
    bounds are within 10^84 of the true values, so that allowance is the only
    slack and it is fourteen orders of magnitude tighter than the defect, which
    put the lower bound 0.63 too high.
    """
    module = checker_module()
    for lo, hi in ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(1)),
                   (Fraction(-1), Fraction(0)), (Fraction(-2), Fraction(-1)),
                   (Fraction(-1), Fraction(1)), (Fraction(-3, 2), Fraction(1, 2))):
        enclosure = module.exp_interval(module.Interval(lo, hi), 16)
        low, _ = exp_bounds(lo)
        _, high = exp_bounds(hi)
        assert enclosure.lo <= low + GRID_STEP, (
            "the lower bound is above exp(%s), so the interval is not an enclosure"
            % lo)
        assert enclosure.hi >= high - GRID_STEP, (
            "the upper bound is below exp(%s), so the interval is not an enclosure"
            % hi)
        assert enclosure.lo <= enclosure.hi


def test_the_crossing_zero_branch_agrees_with_the_two_one_sided_branches():
    """The three branches must not disagree about the same exponential.

    Splitting a crossing-zero interval at zero and taking the lower endpoint from
    the non-positive branch and the upper endpoint from the non-negative branch
    is a metamorphic reading of the same function. The defect showed up here as
    the crossing-zero branch reporting a lower bound of exactly one.
    """
    module = checker_module()
    zero = Fraction(0)
    for lo, hi in ((Fraction(-1), Fraction(1)), (Fraction(-3, 2), Fraction(1, 2)),
                   (Fraction(-1, 2), Fraction(2))):
        whole = module.exp_interval(module.Interval(lo, hi), 16)
        below = module.exp_interval(module.Interval(lo, zero), 16)
        above = module.exp_interval(module.Interval(zero, hi), 16)
        assert whole.lo <= below.lo, (lo, hi)
        assert whole.hi >= above.hi, (lo, hi)
        assert below.lo < 1, "exp of a strictly negative endpoint must be below one"
        assert below.hi == 1 and above.lo == 1
