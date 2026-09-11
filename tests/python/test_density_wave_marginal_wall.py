"""The density-wave mechanism is not a local scalar, and its wall is a degeneracy.

Research 0170 answers an external question at the only level this repository can
check. This test holds the answer in place: the marginal locus must stay a
discriminant, the band must stay bounded and its edge product independent of
self-gravity, the local surrogates must keep failing, the modulus must stay
certifiably non-polynomial, and the two-sided window must stay open, closing and
empty in the declared regimes. It also holds the boundary: the density-wave wall
must not be presented as the Harder-Narasimhan wall.
"""

import json
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/density_wave_marginal_wall"
CHECKER = HERE / "calibration.py"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0170-density-wave-marginal-wall-and-the-nonlocality-of-self-gravity.md"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_the_marginal_locus_is_a_discriminant_condition():
    report = load(EVIDENCE)
    assert report["status"] == "ExternalExactPass"
    assert report["native_status"] == "NotRun"
    assert sorted(report["regimes"]) == ["band", "marginal", "stable"]
    assert report["wall_rows_exactly_tested"] >= 9
    wall = report["wall_examples"][0]
    assert wall["regime"] == "marginal"
    assert wall["discriminant"] == "0"
    assert wall["minimum"] == "0"
    assert wall["q"] == "1"
    assert "double_root" in wall


def test_the_band_is_bounded_and_its_edges_come_from_other_data():
    report = load(EVIDENCE)
    assert report["band_examples"], "the unstable band must be retained"
    band = report["band_examples"][0]
    assert band["band_is_bounded"] is True
    geometry = report["band_geometry_is_self_gravity_independent"]
    assert geometry["checked_keys"] >= 9
    for key, product in geometry["products"].items():
        kappa, cs = key.strip("()").replace("'", "").split(", ")
        from fractions import Fraction
        assert Fraction(product) == Fraction(kappa) ** 2 / Fraction(cs) ** 2, key


def test_the_local_surrogates_cannot_produce_a_bounded_band():
    controls = load(EVIDENCE)["refusal_controls"]
    assert controls["rows"] > 0
    assert controls["without_the_modulus_ever_unstable"] is False
    assert controls["square_surrogate_has_an_upper_edge"] is False


def test_the_modulus_is_certifiably_not_a_polynomial_symbol():
    certificate = load(EVIDENCE)["modulus_certificate"]
    assert len(certificate) >= 7
    for entry in certificate:
        assert entry["disagrees_on_the_negative_side"] is True
        assert entry["value_at_minus_three"] != entry["modulus_at_minus_three"]
    by_degree = {e["degree"]: e for e in certificate}
    assert by_degree[1]["coefficients"] == ["0", "1"]
    assert by_degree[6]["coefficients"] == ["0", "1", "0", "0", "0", "0", "0"]


def test_the_turning_points_are_exact_and_corotation_is_the_midpoint():
    curve = load(EVIDENCE)["flat_rotation_curve"]
    by_arms = {row["arms"]: row for row in curve}
    assert by_arms[1]["inner_exists"] is False, "m = 1 has no inner Lindblad resonance"
    assert "1+-1*sqrt(2)" in by_arms[1]["inner_lindblad"]
    for m in (2, 3, 4):
        assert by_arms[m]["inner_exists"] is True
        assert by_arms[m]["band_is_evanescent"] is True
    assert any(p["sign"] < 0 for p in by_arms[2]["turning_point_signs"])


def test_the_window_is_two_sided_and_closes_at_corotation():
    report = load(EVIDENCE)
    window = report["two_sided_window"]
    assert window["open_rows"] > 0 and window["closed_rows"] > 0 and window["empty_rows"] > 0
    coincidence = report["corotation_coincidence"]
    assert coincidence["rows"] > 0
    for row in coincidence["sample"]:
        assert row["coincide"] is True
        assert row["is_the_toomre_wall"] is True
        assert row["lower_threshold"] == row["upper_threshold"]


def test_the_two_kinds_of_wall_are_not_conflated():
    report = load(EVIDENCE)
    contrast = report["two_kinds_of_wall"]
    assert contrast["this_wall_changes_the_number_of_real_wavenumbers"] is True
    assert contrast["sibling_class_enumeration_uses_no_parameter"] is True
    assert contrast["sibling_classes_recomputed_from_bounds"] == contrast["sibling_reported_classes"]
    note = NOTE.read_text(encoding="utf-8")
    assert "The shape of a wall is shared; the wall is not." in note
    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.density-wave-marginal-wall.v0"]
    assert len(match) == 1
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "A scalar density fluctuation with the mechanism of the density wave" in forbidden
    assert ("The Toomre marginal wall with a stability wall of the Harder-Narasimhan type"
            in forbidden)


def test_the_boundary_is_registered_as_imported_terminology():
    terms = load(ROOT / "docs/terminology/density-wave-boundaries-v0.json")
    assert terms["status"] == "Proposed"
    assert terms["authority"]["native_admission"] == "NotGranted"
    names = [t["name"] for t in terms["terms"]]
    assert names == ["density-wave"]
    does_not_imply = " | ".join(terms["terms"][0]["does_not_imply"])
    assert "A rotational restoring tendency with an inward contraction" in does_not_imply
    assert "A local approximation with the global mode problem" in does_not_imply
    assert terms["terms"][0]["refusal"], "the global problem must be refused explicitly"


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    output = tmp_path / "fresh.json"
    completed = subprocess.run(
        [sys.executable, str(CHECKER), str(output)],
        capture_output=True, text=True, timeout=300, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert load(output) == load(EVIDENCE)
