"""The (i - e)^(i - e) conjecture is refuted on its principal reading.

Research 0171 records a conjecture put to the repository and reports what can be
decided about it. This test holds the result in place: the principal branch must
stay refuted by the modulus being below one, the branch family must stay refuted
from minus six to six, the near misses must stay reported as distances, and the
undecided general case must stay undecided rather than being reported as false.
"""

import json
import subprocess
import sys
import tomllib
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/integer_power_absurdity"
CHECKER = HERE / "calibration.py"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0171-the-i-minus-e-integrality-conjecture.md"


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
