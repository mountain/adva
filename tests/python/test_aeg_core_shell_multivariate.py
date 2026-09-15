"""The multivariate rung: what the historical method reaches, and what it does not.

Research 0190 records the second rung of the core-shell line. The row is bounded
and its conclusions are mostly negative, so the tempting repairs are the quiet
ones: call a hand-chosen exponent lucky without deriving the injectivity
threshold, keep a bounded search and let it read as a proof, or report a
recovered image while an unlucky cell quietly returned an extra factor. This
test recomputes the witnesses from the evidence instead of trusting the labels,
and it holds the frozen contract to its own record.
"""

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/aeg_core_shell_multivariate"
CHECKER = HERE / "calibration.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0190-the-multivariate-rung-of-the-historical-method.md"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run(output=None):
    argv = [sys.executable, str(CHECKER)]
    if output:
        argv += [str(output)]
    return subprocess.run(argv, capture_output=True, text=True, timeout=300,
                          check=False, cwd=ROOT)


def term_map(shown):
    """Read a shown polynomial back into {exponent vector: coefficient}.

    Reading a displayed form is where a coefficient and an exponent swap places,
    which this repository has already done twice, so each variable is located
    rather than consumed in order.
    """
    out = {}
    for token in shown.split(" + "):
        token = token.strip()
        match = re.match(r"^([+-]?)(\d*)", token)
        sign = -1 if match.group(1) == "-" else 1
        coefficient = int(match.group(2)) if match.group(2) else 1
        exponents = []
        for variable in ("x", "y"):
            if variable not in token:
                exponents.append(0)
                continue
            power = re.search(variable + r"\^(\d+)", token)
            exponents.append(int(power.group(1)) if power else 1)
        key = tuple(exponents)
        out[key] = out.get(key, 0) + sign * coefficient
    return {e: c for e, c in out.items() if c}


def kronecker(exponents, base):
    return exponents[0] * base + exponents[1]


def test_the_frozen_contract_reproduces_its_own_evidence(tmp_path):
    """A frozen record must stay reproducible, not merely retained."""
    fresh = tmp_path / "evidence.json"
    completed = run(output=fresh)
    assert completed.returncode == 0, completed.stderr
    assert load(fresh) == load(EVIDENCE), (
        "the frozen evidence no longer follows from its own contract")


def test_the_evidence_pins_the_contract_it_came_from():
    pinned = load(EVIDENCE)["contract"]
    assert pinned["sha256"] == hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
    assert pinned["base_commit"] == load(CONTRACT)["base_commit"]
    assert pinned["path"] == CONTRACT.name


def test_the_value_equality_route_uses_neither_a_gcd_nor_a_monomial_order():
    """The route that survives in two variables is the cheap one, and it says so."""
    rows = load(EVIDENCE)["value_equality"]
    assert rows, "no equality route was recorded"
    for row in rows:
        assert row["cross_product_is_zero"] is True
        assert row["uses_gcd"] is False
        assert row["uses_monomial_order"] is False


def test_the_bezout_negative_is_bounded_and_never_reads_as_a_proof():
    bezout = load(EVIDENCE)["bezout"]
    search = bezout["bounded_search"]
    assert search["witnesses_found"] == 0
    assert search["pairs_examined"] == search["monomials"] ** 2
    assert "not the proof" in search["status"]
    assert "single monomials" in search["searched_family"], (
        "the searched family is narrower than the claim and must be declared")
    assert "origin" in bezout["proof"], "the actual proof is missing"
    assert "not a Bezout domain" in bezout["consequence"]


def test_the_injectivity_threshold_is_derived_and_every_lower_exponent_witnesses_a_collision():
    """The threshold must come from the degrees, not from a chosen exponent."""
    section = load(EVIDENCE)["kronecker"]
    threshold = section["injectivity_threshold"]
    assert threshold == section["maximum_degree_in_each_variable"] + 1
    for row in section["rows"]:
        assert row["injective_on_these_degrees"] == (row["base"] >= threshold)
        assert row["equality_decided_by_the_image_is_sound"] is row["injective_on_these_degrees"]
        if row["base"] >= threshold:
            assert row["collision_witness"] is None
            continue
        assert row["base"] in section["declared_exponents_below_the_threshold"]
        one, other, common = row["collision_witness"]
        # the witness is recomputed here rather than trusted as a label
        assert one != other
        image_of_one = kronecker(next(iter(term_map(one))), row["base"])
        image_of_other = kronecker(next(iter(term_map(other))), row["base"])
        assert image_of_one == image_of_other, (
            "the recorded pair is not a colliding pair")
        assert next(iter(term_map(common))) == (image_of_one, 0), (
            "the recorded image is not the image of the recorded pair")


def test_no_hand_chosen_exponent_is_reported_as_injective_without_the_derivation():
    """The first exponent chosen for this row sat below the threshold."""
    section = load(EVIDENCE)["kronecker"]
    below = section["declared_exponents_below_the_threshold"]
    assert below, "nothing below the threshold was tested, so nothing is exhibited"
    assert max(section["declared_exponents_at_or_above_the_threshold"]) >= \
        section["injectivity_threshold"]
    assert min(below) < section["injectivity_threshold"]
    findings = " ".join(load(EVIDENCE)["findings"])
    assert "optimistic label" in findings, (
        "the corrected label must remain on the record")


def test_every_unlucky_image_carries_an_exhibited_extra_factor():
    """Recovery is per cell; a mismatch must come with the factor that caused it."""
    section = load(EVIDENCE)["congruence_route"]
    cells = section["cells"]
    assert len(cells) == section["cells_recovered"] + section["cells_unlucky"]
    assert section["cells_recovered"] > 0, "nothing was recovered at all"
    unlucky = [row for row in cells if row["status"] != "Recovered"]
    assert unlucky, (
        "no unlucky cell was encountered, so the load-bearing control is absent")
    for row in unlucky:
        image = term_map(row["image"])
        for exponents, coefficient in term_map(row["expected"]).items():
            for offset, other in term_map(row["extra_factor"]).items():
                combined = tuple(a + b for a, b in zip(exponents, offset))
                image[combined] = image.get(combined, 0) - coefficient * other
        # expected times the extra factor must reproduce the image exactly
        assert not {e: c for e, c in image.items() if c}, row
    assert any(row["route"] == "modular" for row in unlucky)


def test_the_composed_measurement_is_taken_and_its_loss_is_the_residual():
    """The measurement the previous round left open is taken here."""
    rows = load(EVIDENCE)["composed_measurement"]
    assert rows, "the composed measurement is missing"
    for row in rows:
        assert row["content_equal"] is False
        assert row["object_equal"] is False
        assert row["content_inequality_is_detectable"] is True
    residuals = load(EVIDENCE)["truncated_inverse"]
    assert residuals
    for row in residuals:
        assert row["residual_inside_the_ideal"] is True
        assert row["residual_is_nonzero"] is True


def test_the_refusal_controls_are_recorded():
    refusals = load(EVIDENCE)["refusals"]
    assert len(refusals) >= 3
    for row in refusals:
        assert row["refused"] is True
        assert row["message"], row


def test_the_note_records_the_rung_and_the_index_agrees():
    assert NOTE.exists(), "the note is missing"
    text = NOTE.read_text(encoding="utf-8")
    index = (ROOT / "docs/research/README.md").read_text(encoding="utf-8")
    assert NOTE.name in index, "the note is not indexed"
    assert "0190" in index
    assert "ézout" in text or "Bezout" in text, "the negative result is not stated"
    assert "NotRun" in text, "the native status must be stated"
    assert "0190" in text


# ------------------------------------------------------ the truncated inverse helper

def checker_module():
    """Import the checker to call a helper directly, as the discovery probes do."""
    spec = importlib.util.spec_from_file_location("multivariate_inverse", CHECKER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.LIMITS["max_assertions"] = 100000
    return module


def test_the_truncated_inverse_of_a_constant_scales_by_that_constant():
    """c times its truncated inverse must be exactly one for every nonzero c.

    A pure constant has no positive-degree terms, so nothing is truncated and the
    product is exactly one. The early exit taken when the normalized remainder is
    zero returned the unit monomial and dropped the normalization it had just
    applied, giving one instead of 1/c for every c other than one.
    """
    module = checker_module()
    one = module.MPoly.constant(1, 2)
    for c in (Fraction(1), Fraction(-1), Fraction(2), Fraction(3), Fraction(1, 2)):
        for order in (1, 2):
            constant = module.MPoly.constant(c, 2)
            approximation = module.truncated_inverse(constant, order)
            assert approximation * constant == one, (c, order)
            assert approximation.terms == {(0, 0): 1 / c}, (c, order)


def test_the_inverse_keeps_its_scaling_on_both_sides_of_the_early_exit():
    """The zero-remainder shortcut and the series must agree where both apply.

    `one + x^2` has a nonzero remainder, so it takes the loop; adding the
    remainder to the constant term moves the same denominator onto the early
    exit. Both routes describe the same normalization and must not disagree.
    """
    module = checker_module()
    one = module.MPoly.constant(1, 2)
    x = module.MPoly.variable(0, 2)
    series_route = module.truncated_inverse(one + x, 1)
    assert series_route.terms == {(0, 0): 1, (1, 0): -1}
    for c in (Fraction(-1), Fraction(2), Fraction(3), Fraction(1, 2)):
        shortcut = module.truncated_inverse(module.MPoly.constant(c, 2), 2)
        assert shortcut * module.MPoly.constant(c, 2) == one
    # the frozen experiment's denominator still resolves through the series
    frozen = module.truncated_inverse(x * x + module.MPoly.constant(1, 2), 3)
    assert frozen * (x * x + module.MPoly.constant(1, 2)) - one != module.MPoly.zero(2)
